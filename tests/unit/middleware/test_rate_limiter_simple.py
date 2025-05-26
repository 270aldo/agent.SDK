"""
Pruebas unitarias simples para el middleware de limitación de tasa.

Este módulo contiene pruebas para verificar el correcto funcionamiento
del middleware de limitación de tasa sin depender del conftest.py.
"""

import pytest
import time
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI, Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from src.api.middleware.rate_limiter import RateLimiter

class TestRateLimiterSimple:
    """Pruebas simples para el middleware de limitación de tasa."""
    
    def setup_method(self):
        """Configuración para cada prueba."""
        # Crear una aplicación FastAPI simple para pruebas
        self.app = FastAPI()
    
    def test_init(self):
        """Prueba la inicialización del middleware."""
        # Inicializar el middleware con valores predeterminados
        rate_limiter = RateLimiter(self.app)
        
        # Verificar valores predeterminados
        assert rate_limiter.requests_per_minute == 60
        assert rate_limiter.requests_per_hour == 1000
        assert rate_limiter.admin_exempt is True
        assert rate_limiter.whitelist_ips == []
        assert rate_limiter.whitelist_paths == []
        assert rate_limiter.get_user_id is None
        assert isinstance(rate_limiter.request_store, dict)
        
        # Inicializar con valores personalizados
        custom_get_user_id = lambda request: "test_user"
        rate_limiter = RateLimiter(
            self.app,
            requests_per_minute=30,
            requests_per_hour=500,
            admin_exempt=False,
            whitelist_ips=["127.0.0.1"],
            whitelist_paths=["/docs"],
            get_user_id=custom_get_user_id
        )
        
        # Verificar valores personalizados
        assert rate_limiter.requests_per_minute == 30
        assert rate_limiter.requests_per_hour == 500
        assert rate_limiter.admin_exempt is False
        assert rate_limiter.whitelist_ips == ["127.0.0.1"]
        assert rate_limiter.whitelist_paths == ["/docs"]
        assert rate_limiter.get_user_id == custom_get_user_id
    
    def test_get_key_with_ip(self):
        """Prueba obtener clave basada en IP."""
        # Inicializar el middleware
        rate_limiter = RateLimiter(self.app)
        
        # Crear una solicitud mock con IP
        request = MagicMock()
        request.client = MagicMock()
        request.client.host = "192.168.1.1"
        
        # Obtener clave
        key = rate_limiter._get_key(request)
        
        # Verificar clave
        assert key == "ip:192.168.1.1"
    
    def test_get_key_with_user(self):
        """Prueba obtener clave basada en usuario."""
        # Crear una función mock para obtener usuario
        get_user_id = MagicMock(return_value="test_user")
        
        # Inicializar el middleware con función para obtener usuario
        rate_limiter = RateLimiter(self.app, get_user_id=get_user_id)
        
        # Crear una solicitud mock
        request = MagicMock()
        
        # Obtener clave
        key = rate_limiter._get_key(request)
        
        # Verificar clave
        assert key == "user:test_user"
        get_user_id.assert_called_once_with(request)
    
    def test_is_whitelisted_by_ip(self):
        """Prueba verificar si una solicitud está en lista blanca por IP."""
        # Inicializar el middleware con IPs en lista blanca
        rate_limiter = RateLimiter(self.app, whitelist_ips=["192.168.1.1"])
        
        # Crear una solicitud mock con IP en lista blanca
        request = MagicMock()
        request.client = MagicMock()
        request.client.host = "192.168.1.1"
        
        # Verificar que está en lista blanca
        assert rate_limiter._is_whitelisted(request) is True
        
        # Crear una solicitud mock con IP no en lista blanca
        request.client.host = "192.168.1.2"
        
        # Verificar que no está en lista blanca
        assert rate_limiter._is_whitelisted(request) is False
    
    def test_is_whitelisted_by_path(self):
        """Prueba verificar si una solicitud está en lista blanca por ruta."""
        # Inicializar el middleware con rutas en lista blanca
        rate_limiter = RateLimiter(self.app, whitelist_paths=["/docs", "/api/health"])
        
        # Crear una solicitud mock con ruta en lista blanca
        request = MagicMock()
        request.url = MagicMock()
        request.url.path = "/docs"
        
        # Verificar que está en lista blanca
        assert rate_limiter._is_whitelisted(request) is True
        
        # Crear una solicitud mock con ruta no en lista blanca
        request.url.path = "/api/users"
        
        # Verificar que no está en lista blanca
        assert rate_limiter._is_whitelisted(request) is False
        
        # Crear una solicitud mock con ruta que comienza con una ruta en lista blanca
        request.url.path = "/api/health/check"
        
        # Verificar que está en lista blanca
        assert rate_limiter._is_whitelisted(request) is True
    
    def test_cleanup_old_requests(self):
        """Prueba la limpieza de solicitudes antiguas."""
        # Inicializar el middleware
        rate_limiter = RateLimiter(self.app)
        
        # Establecer tiempo de limpieza anterior
        current_time = time.time()
        rate_limiter.last_cleanup = current_time - rate_limiter.cleanup_interval - 1
        
        # Añadir solicitudes antiguas y recientes
        old_time = current_time - 3601  # Más de 1 hora
        recent_time = current_time - 60  # 1 minuto
        
        rate_limiter.request_store = {
            "ip:192.168.1.1": [(old_time, 1), (recent_time, 1)],
            "ip:192.168.1.2": [(old_time, 1)],
            "ip:192.168.1.3": [(recent_time, 1)]
        }
        
        # Ejecutar limpieza
        rate_limiter._cleanup_old_requests()
        
        # Verificar resultado
        assert "ip:192.168.1.1" in rate_limiter.request_store
        assert len(rate_limiter.request_store["ip:192.168.1.1"]) == 1
        assert "ip:192.168.1.2" not in rate_limiter.request_store
        assert "ip:192.168.1.3" in rate_limiter.request_store
    
    def test_check_rate_limit_new_key(self):
        """Prueba verificar límite de tasa para una clave nueva."""
        # Inicializar el middleware
        rate_limiter = RateLimiter(self.app)
        
        # Verificar límite para una clave nueva
        exceeded, retry_after = rate_limiter._check_rate_limit("new_key")
        
        # Verificar resultado
        assert exceeded is False
        assert retry_after is None
        assert "new_key" in rate_limiter.request_store
        assert len(rate_limiter.request_store["new_key"]) == 1
    
    def test_check_rate_limit_minute_exceeded(self):
        """Prueba verificar límite de tasa por minuto excedido."""
        # Inicializar el middleware
        rate_limiter = RateLimiter(self.app, requests_per_minute=2)
        
        # Establecer solicitudes para una clave
        current_time = time.time()
        rate_limiter.request_store = {
            "test_key": [
                (current_time - 10, 1),
                (current_time - 5, 1)
            ]
        }
        
        # Verificar límite
        exceeded, retry_after = rate_limiter._check_rate_limit("test_key")
        
        # Verificar resultado
        assert exceeded is True
        assert retry_after is not None
        assert retry_after > 0
    
    @pytest.mark.asyncio
    @patch("src.api.middleware.rate_limiter.time.time")
    async def test_dispatch_whitelisted(self, mock_time):
        """Prueba el procesamiento de una solicitud en lista blanca."""
        # Configurar mock
        mock_time.return_value = 1000.0
        
        # Inicializar el middleware
        rate_limiter = RateLimiter(self.app, whitelist_paths=["/docs"])
        
        # Crear mocks para solicitud y respuesta
        request = MagicMock()
        request.url = MagicMock()
        request.url.path = "/docs"
        
        response = MagicMock()
        call_next = AsyncMock(return_value=response)
        
        # Procesar solicitud
        result = await rate_limiter.dispatch(request, call_next)
        
        # Verificar resultado
        assert result == response
        call_next.assert_called_once_with(request)
    
    @pytest.mark.asyncio
    @patch("src.api.middleware.rate_limiter.time.time")
    async def test_dispatch_rate_limit_exceeded(self, mock_time):
        """Prueba el procesamiento de una solicitud que excede el límite de tasa."""
        # Configurar mock
        mock_time.return_value = 1000.0
        
        # Inicializar el middleware
        rate_limiter = RateLimiter(self.app, requests_per_minute=1)
        
        # Crear mock para solicitud
        request = MagicMock()
        request.client = MagicMock()
        request.client.host = "192.168.1.1"
        request.url = MagicMock()
        request.url.path = "/api/users"
        
        # Establecer solicitudes previas
        rate_limiter.request_store = {
            "ip:192.168.1.1": [(mock_time.return_value - 10, 1)]
        }
        
        # Crear mock para siguiente middleware
        call_next = AsyncMock()
        
        # Procesar solicitud debe lanzar una excepción
        with pytest.raises(HTTPException) as exc_info:
            await rate_limiter.dispatch(request, call_next)
        
        # Verificar excepción
        assert exc_info.value.status_code == 429
        assert "Retry-After" in exc_info.value.headers
