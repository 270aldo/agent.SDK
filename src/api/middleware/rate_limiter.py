"""
Middleware de limitación de tasa para la API.

Este módulo proporciona un middleware para limitar la tasa de solicitudes a la API,
protegiendo contra abusos y ataques de denegación de servicio.
"""

import time
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, List, Tuple, Optional, Callable, Any
import logging

# Configurar el logger
logger = logging.getLogger("api.rate_limiter")

class RateLimiter(BaseHTTPMiddleware):
    """
    Middleware para limitar la tasa de solicitudes a la API.
    
    Utiliza una estrategia de ventana deslizante para rastrear las solicitudes
    y limitar el número de solicitudes por dirección IP y/o usuario.
    """
    
    def __init__(
        self, 
        app,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        admin_exempt: bool = True,
        whitelist_ips: Optional[List[str]] = None,
        whitelist_paths: Optional[List[str]] = None,
        get_user_id: Optional[Callable[[Request], str]] = None
    ):
        """
        Inicializa el middleware de limitación de tasa.
        
        Args:
            app: La aplicación FastAPI
            requests_per_minute: Número máximo de solicitudes permitidas por minuto
            requests_per_hour: Número máximo de solicitudes permitidas por hora
            admin_exempt: Si los usuarios administradores están exentos de la limitación
            whitelist_ips: Lista de IPs que están exentas de la limitación
            whitelist_paths: Lista de rutas que están exentas de la limitación
            get_user_id: Función para extraer el ID de usuario de la solicitud
        """
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.admin_exempt = admin_exempt
        self.whitelist_ips = whitelist_ips or []
        self.whitelist_paths = whitelist_paths or []
        self.get_user_id = get_user_id
        
        # Almacenamiento de solicitudes: {key: [(timestamp, count), ...]}
        self.request_store: Dict[str, List[Tuple[float, int]]] = {}
        
        # Intervalo de tiempo para limpiar el almacenamiento (1 hora en segundos)
        self.cleanup_interval = 3600
        self.last_cleanup = time.time()
    
    def _get_key(self, request: Request) -> str:
        """
        Obtiene la clave para identificar al solicitante.
        
        Utiliza el ID de usuario si está disponible, de lo contrario utiliza la IP.
        
        Args:
            request: La solicitud HTTP
            
        Returns:
            str: Clave para identificar al solicitante
        """
        if self.get_user_id:
            try:
                user_id = self.get_user_id(request)
                if user_id:
                    return f"user:{user_id}"
            except Exception as e:
                logger.warning(f"Error al obtener ID de usuario: {str(e)}")
        
        # Usar la IP del cliente como respaldo
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}"
    
    def _is_whitelisted(self, request: Request) -> bool:
        """
        Verifica si la solicitud está en la lista blanca.
        
        Args:
            request: La solicitud HTTP
            
        Returns:
            bool: True si la solicitud está en la lista blanca
        """
        # Verificar si la IP está en la lista blanca
        client_ip = request.client.host if request.client else None
        if client_ip and client_ip in self.whitelist_ips:
            return True
        
        # Verificar si la ruta está en la lista blanca
        path = request.url.path
        for whitelist_path in self.whitelist_paths:
            if path.startswith(whitelist_path):
                return True
        
        # Verificar si el usuario es administrador y están exentos
        if self.admin_exempt and self.get_user_id:
            try:
                user_id = self.get_user_id(request)
                # Aquí se podría verificar si el usuario es administrador
                # Por ahora, simplemente devolvemos False
                return False
            except Exception as e:
                logger.warning(f"Error checking admin status for rate limit exemption: {e}")
                return False
        
        return False
    
    def _cleanup_old_requests(self) -> None:
        """
        Limpia las solicitudes antiguas del almacenamiento.
        """
        current_time = time.time()
        
        # Realizar limpieza solo si ha pasado el intervalo de limpieza
        if current_time - self.last_cleanup < self.cleanup_interval:
            return
        
        self.last_cleanup = current_time
        
        # Tiempo límite para mantener registros (1 hora)
        cutoff_time = current_time - 3600
        
        for key in list(self.request_store.keys()):
            # Filtrar solo las solicitudes recientes
            recent_requests = [(ts, count) for ts, count in self.request_store[key] if ts > cutoff_time]
            
            if recent_requests:
                self.request_store[key] = recent_requests
            else:
                # Si no hay solicitudes recientes, eliminar la clave
                del self.request_store[key]
    
    def _check_rate_limit(self, key: str) -> Tuple[bool, Optional[int]]:
        """
        Verifica si se ha excedido el límite de tasa.
        
        Args:
            key: Clave para identificar al solicitante
            
        Returns:
            Tuple[bool, Optional[int]]: (excedido, segundos_para_reintentar)
        """
        current_time = time.time()
        
        # Si la clave no existe en el almacenamiento, crearla
        if key not in self.request_store:
            self.request_store[key] = [(current_time, 1)]
            return False, None
        
        # Filtrar solicitudes dentro de la ventana de tiempo
        minute_ago = current_time - 60
        hour_ago = current_time - 3600
        
        # Contar solicitudes en el último minuto y hora
        minute_requests = sum(count for ts, count in self.request_store[key] if ts > minute_ago)
        hour_requests = sum(count for ts, count in self.request_store[key] if ts > hour_ago)
        
        # Verificar límites
        if minute_requests >= self.requests_per_minute:
            # Calcular tiempo para reintentar (en segundos)
            oldest_in_minute = min(ts for ts, _ in self.request_store[key] if ts > minute_ago)
            retry_after = int(60 - (current_time - oldest_in_minute)) + 1
            return True, retry_after
        
        if hour_requests >= self.requests_per_hour:
            # Calcular tiempo para reintentar (en segundos)
            oldest_in_hour = min(ts for ts, _ in self.request_store[key] if ts > hour_ago)
            retry_after = int(3600 - (current_time - oldest_in_hour)) + 1
            return True, retry_after
        
        # Actualizar el contador de solicitudes
        self.request_store[key].append((current_time, 1))
        return False, None
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Procesa la solicitud y aplica la limitación de tasa.
        
        Args:
            request: La solicitud HTTP
            call_next: Función para continuar con la siguiente middleware
            
        Returns:
            Response: La respuesta HTTP
        """
        # Limpiar solicitudes antiguas periódicamente
        self._cleanup_old_requests()
        
        # Verificar si la solicitud está en la lista blanca
        if self._is_whitelisted(request):
            return await call_next(request)
        
        # Obtener clave para el solicitante
        key = self._get_key(request)
        
        # Verificar límite de tasa
        exceeded, retry_after = self._check_rate_limit(key)
        
        if exceeded:
            # Registrar el intento de exceso
            logger.warning(f"Límite de tasa excedido para {key}")
            
            # Devolver respuesta de error con encabezado Retry-After
            headers = {"Retry-After": str(retry_after)} if retry_after else {}
            
            raise HTTPException(
                status_code=429,
                detail="Demasiadas solicitudes. Por favor, inténtelo de nuevo más tarde.",
                headers=headers
            )
        
        # Continuar con la solicitud
        return await call_next(request)


def get_user_from_request(request: Request) -> Optional[str]:
    """
    Extrae el ID de usuario de la solicitud.
    
    Args:
        request: La solicitud HTTP
        
    Returns:
        Optional[str]: ID de usuario o None si no está autenticado
    """
    try:
        # Intentar obtener el token del encabezado de autorización
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        
        # En una implementación real, aquí se decodificaría el token JWT
        # y se extraería el ID de usuario
        # Por ahora, simplemente devolvemos None
        return None
    except Exception as e:
        logger.warning(f"Error al extraer usuario de la solicitud: {str(e)}")
        return None
