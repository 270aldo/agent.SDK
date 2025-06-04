import os
import re
from dotenv import load_dotenv
from supabase import create_client, Client
import logging
import json
from typing import Dict, Any, Optional
from collections import defaultdict
import uuid

# Configurar logging
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

# Función para leer variables directamente del archivo .env
def read_env_file(var_name, default=""):
    """Lee una variable directamente del archivo .env"""
    try:
        with open(".env", "r") as f:
            content = f.read()
            pattern = fr"{var_name}=(.*?)($|\n)"
            match = re.search(pattern, content)
            if match:
                return match.group(1).strip()
    except Exception as e:
        logger.error(f"Error al leer variable {var_name} del archivo .env: {e}")
    return default

class MockSupabaseClient:
    """Implementación simulada del cliente de Supabase para desarrollo/pruebas."""

    def __init__(self):
        self.tables = defaultdict(list)
        logger.info("Cliente simulado de Supabase inicializado (MODO SIN CONEXIÓN)")

    def table(self, table_name: str):
        """Simular acceso a tabla."""
        return MockTableQuery(self, table_name)

    def insert(self, table_name: str, data: Dict[str, Any]):
        """Insertar datos en la tabla simulada."""
        self.tables[table_name].append(data)
        return data

    def upsert(self, table_name: str, data: Dict[str, Any]):
        """Guardar o actualizar datos en la tabla simulada."""
        record_id = data.get('id')

        if not record_id:
            return {"error": "ID missing"}

        for i, record in enumerate(self.tables[table_name]):
            if record.get('id') == record_id:
                self.tables[table_name][i] = data
                return data

        self.tables[table_name].append(data)
        return data

    def update(self, table_name: str, data: Dict[str, Any], filters: Optional[Dict[str, Any]] = None):
        """Actualizar datos en la tabla simulada."""
        if not filters:
            return []

        updated = []
        for record in self.tables[table_name]:
            match = all(record.get(k) == v for k, v in filters.items())
            if match:
                record.update(data)
                updated.append(record)
        return updated

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
        self._operation = None
        self._data = None
    
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
        if self._operation == 'insert':
            inserted = self.client.insert(self.table_name, self._data)
            return {"data": [inserted]}
        elif self._operation == 'upsert':
            upserted = self.client.upsert(self.table_name, self._data)
            return {"data": [upserted]}
        elif self._operation == 'update':
            filters = {f: v for f, _, v in self._filters}
            updated = self.client.update(self.table_name, self._data, filters)
            return {"data": updated}
        else:
            if not self._filters:
                return {"data": self.client.tables[self.table_name]}

            for field, op, value in self._filters:
                if field == 'id' and op == '=':
                    return self.client.select_by_id(self.table_name, value)

            return {"data": None}

    def upsert(self, data):
        """Simular upsert."""
        self._operation = 'upsert'
        self._data = data
        return self

    def insert(self, data):
        """Simular insert."""
        self._operation = 'insert'
        self._data = data
        return self

    def update(self, data):
        """Simular update."""
        self._operation = 'update'
        self._data = data
        return self

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
        # Leer las variables directamente del archivo .env
        url = read_env_file("SUPABASE_URL", os.getenv("SUPABASE_URL", ""))
        self.key = read_env_file("SUPABASE_ANON_KEY", os.getenv("SUPABASE_ANON_KEY", ""))
        self.service_key = read_env_file("SUPABASE_SERVICE_ROLE_KEY", os.getenv("SUPABASE_SERVICE_ROLE_KEY", ""))
        
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