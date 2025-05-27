import re
# import os # os might still be needed for other things, but not for getenv for these vars
from supabase import create_client, Client # Keep Client if used by mock
import logging
import json # Keep json if used by mock
from typing import Dict, Any, Optional # Keep typing if used by mock
from collections import defaultdict # Keep defaultdict if used by mock
import uuid # Keep uuid if used by mock

from src.config import settings # Importar la configuración centralizada

# Configurar logging
logger = logging.getLogger(__name__)

# load_dotenv() is no longer needed here; Pydantic handles .env loading.

# read_env_file function is no longer needed.

class MockSupabaseClient:
    """Implementación simulada del cliente de Supabase para desarrollo/pruebas."""
    
    def __init__(self):
        self.tables = defaultdict(list)
        logger.info("Cliente simulado de Supabase inicializado (MODO SIN CONEXIÓN)")
    
    def table(self, table_name: str):
        """Simular acceso a tabla."""
        return MockTableQuery(self, table_name)
    
    def upsert(self, table_name: str, data: Dict[str, Any]):
        """Guardar o actualizar datos en la tabla simulada."""
        # Buscar registro existente por id
        record_id = data.get('id')
        
        if not record_id:
            return {"error": "ID missing"}
        
        # Verificar si el registro ya existe
        for i, record in enumerate(self.tables[table_name]):
            if record.get('id') == record_id:
                # Actualizar registro existente
                self.tables[table_name][i] = data
                return {"data": data}
        
        # Insertar nuevo registro
        self.tables[table_name].append(data)
        return {"data": data}
    
    def select_by_id(self, table_name: str, record_id: str):
        """Simular búsqueda por ID."""
        for record in self.tables[table_name]:
            if record.get('id') == record_id:
                return {"data": record}
        return {"data": None}

class MockTableQuery:
    """Simulador de consultas a tablas de Supabase."""
    
    def __init__(self, client, table_name):
        self.client = client
        self.table_name = table_name
        self._filters = []
    
    def select(self, *fields):
        """Simular selección de campos."""
        return self
    
    def eq(self, field, value):
        """Simular filtro de igualdad."""
        self._filters.append((field, '=', value))
        return self
    
    def single(self):
        """Simular consulta que devuelve un único registro."""
        return self
    
    def execute(self):
        """Ejecutar la consulta simulada."""
        if not self._filters:
            return {"data": self.client.tables[self.table_name]}
        
        # Aplicar filtros (simplificado - solo filtra por igualdad en id)
        for field, op, value in self._filters:
            if field == 'id' and op == '=':
                return self.client.select_by_id(self.table_name, value)
        
        # Si no hay coincidencias
        return {"data": None}
    
    def upsert(self, data):
        """Simular upsert."""
        return {"data": self.client.upsert(self.table_name, data)}

class SupabaseClient:
    _instance = None
    _mock_enabled = False  # Cambiar a False para usar el cliente real de Supabase
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseClient, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Inicializar el cliente de Supabase con credenciales desde variables de entorno o en modo simulado."""
        # Leer las variables desde Pydantic settings
        url = settings.SUPABASE_URL
        self.key = settings.SUPABASE_ANON_KEY
        self.service_key = settings.SUPABASE_SERVICE_ROLE_KEY
        
        # Asegurar que la URL tenga el formato correcto
        if url and not url.startswith("http"):
            url = f"https://{url}"
        
        # Corregir URL: eliminar '@' inicial si existe
        self.url = url[1:] if url.startswith('@') else url
        
        # Para modo simulado
        self.mock_client = MockSupabaseClient()
        
        # Inicialmente, intentamos determinar si deberíamos usar el modo simulado
        # basado en la presencia de variables de entorno
        if not self.url or not self.key:
            self._mock_enabled = True
            logger.warning("Faltan variables de entorno SUPABASE_URL o SUPABASE_ANON_KEY. Usando modo simulado.")
        else:
            # Si tenemos las credenciales, intentamos verificar si podemos conectarnos
            try:
                self._mock_enabled = False  # Temporalmente desactivamos el modo simulado para probar la conexión
                logger.info(f"Verificando conexión a Supabase con URL: {self.url}")
                
                # Intentamos crear el cliente real
                from supabase import create_client, Client
                test_client = create_client(self.url, self.key)
                
                # Hacemos una prueba de conexión simple
                try:
                    # Intentar acceder a alguna tabla existente
                    test_client.table("conversations").select("*").limit(1).execute()
                    logger.info("Conexión a Supabase exitosa. Usando cliente real.")
                except Exception as table_error:
                    # Si hay un error específico de tabla, podría ser que la tabla no existe
                    # pero la conexión es buena
                    if "404" in str(table_error):
                        logger.info("Conexión a Supabase exitosa, pero la tabla de verificación no existe. Usando cliente real de todos modos.")
                    else:
                        # Si hay otro tipo de error, usamos el modo simulado
                        self._mock_enabled = True
                        logger.warning(f"Error al acceder a tablas en Supabase: {table_error}. Usando modo simulado.")
            except Exception as e:
                self._mock_enabled = True
                logger.warning(f"Error al conectar con Supabase: {e}. Usando modo simulado.")
        
        # Informar del modo seleccionado
        if self._mock_enabled:
            logger.info("Cliente de Supabase inicializado en MODO SIMULADO (sin conexión real)")
        else:
            logger.info(f"Cliente de Supabase inicializado con URL: {self.url}")
        
        # No creamos el cliente real de inmediato, solo cuando se necesite
        self.client = None
        self.admin_client = None
    
    def get_client(self, admin=False):
        """
        Obtener cliente de Supabase (real o simulado).
        
        Args:
            admin (bool): Si True, usa la clave de servicio para acceso administrativo
            
        Returns:
            Cliente: Cliente de Supabase (real o simulado)
        """
        # Si estamos en modo simulado, siempre devolver el cliente simulado
        if self._mock_enabled:
            return self.mock_client
            
        # Si queremos el cliente real
        if admin:
            if not self.service_key:
                logger.error("Falta variable de entorno SUPABASE_SERVICE_ROLE_KEY")
                raise ValueError("Falta clave de servicio para acceso administrativo a Supabase")
            
            # Depuración
            logger.info(f"Creando cliente admin con URL: '{self.url}' (primeros 10 caracteres de la clave: {self.service_key[:10]}...)")
            
            if not self.admin_client:
                from supabase import create_client, Client
                self.admin_client = create_client(self.url, self.service_key)
            return self.admin_client
        else:
            # Depuración
            logger.info(f"Creando cliente regular con URL: '{self.url}' (primeros 10 caracteres de la clave: {self.key[:10]}...)")
            
            if not self.client:
                from supabase import create_client, Client
                self.client = create_client(self.url, self.key)
            return self.client
            
    def check_connection(self):
        """
        Verificar que la conexión a Supabase funciona correctamente.
        
        Returns:
            bool: True si la conexión es exitosa, False en caso contrario
        """
        if self._mock_enabled:
            logger.info("En modo simulado, la conexión siempre es exitosa")
            return True
            
        try:
            client = self.get_client()
            # Intentar realizar una consulta simple para verificar la conexión
            response = client.table("conversations").select("*").limit(1).execute()
            logger.info("Conexión a Supabase exitosa")
            return True
        except Exception as e:
            logger.error(f"Error al verificar la conexión a Supabase: {e}")
            return False

# Singleton instance
supabase_client = SupabaseClient() 