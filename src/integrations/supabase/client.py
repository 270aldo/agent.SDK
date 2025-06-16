import os
from dotenv import load_dotenv
from supabase import create_client, Client
import logging
from typing import Dict, Any, Optional
from collections import defaultdict

# Configurar logging
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

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

    def insert(self, data):
        """Simular inserción de datos."""
        self.client.tables[self.table_name].append(data)
        return {"data": data}

class SupabaseClient:
    """Cliente de Supabase simplificado con modo mock automático."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseClient, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Inicializar el cliente de Supabase."""
        # Obtener variables de entorno
        self.url = os.getenv("SUPABASE_URL")
        self.anon_key = os.getenv("SUPABASE_ANON_KEY")
        self.service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        # Determinar si usar modo mock
        self._mock_enabled = not (self.url and self.anon_key)
        
        if self._mock_enabled:
            logger.warning("Supabase environment variables not set. Using mock mode.")
            self.mock_client = MockSupabaseClient()
        else:
            logger.info(f"Supabase client initialized with URL: {self.url}")
            self.client = None
            self.admin_client = None
    
    def get_client(self, admin: bool = False) -> Client:
        """
        Obtener cliente de Supabase.
        
        Args:
            admin (bool): Si True, usa la clave de servicio para acceso administrativo
            
        Returns:
            Cliente: Cliente de Supabase (real o simulado)
        """
        if self._mock_enabled:
            return self.mock_client
        
        if admin:
            if not self.service_key:
                raise ValueError("SUPABASE_SERVICE_ROLE_KEY environment variable is required for admin access")
            
            if not self.admin_client:
                logger.info(f"Creating admin Supabase client")
                self.admin_client = create_client(self.url, self.service_key)
            return self.admin_client
        else:
            if not self.client:
                logger.info(f"Creating regular Supabase client")
                self.client = create_client(self.url, self.anon_key)
            return self.client
    
    def check_connection(self) -> bool:
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