"""
Pruebas unitarias para las utilidades de caché local.
"""

import pytest
import os
import json
import shutil
import tempfile
from unittest.mock import patch, mock_open
from datetime import datetime, timedelta

from src.utils.cache_utils import LocalCache

class TestLocalCache:
    """Pruebas para la clase LocalCache."""
    
    @pytest.fixture
    def temp_cache_dir(self):
        """Fixture que proporciona un directorio temporal para la caché."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Limpiar después de las pruebas
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def cache(self, temp_cache_dir):
        """Fixture que proporciona una instancia de LocalCache con un directorio temporal."""
        return LocalCache(cache_dir=temp_cache_dir)
    
    def test_init(self, temp_cache_dir):
        """Prueba que la inicialización crea el directorio de caché si no existe."""
        # Eliminar el directorio para probar que se crea
        shutil.rmtree(temp_cache_dir)
        
        # Crear caché (debería crear el directorio)
        cache = LocalCache(cache_dir=temp_cache_dir)
        
        # Verificar que el directorio existe
        assert os.path.exists(temp_cache_dir)
        assert os.path.isdir(temp_cache_dir)
    
    def test_get_cache_file_path(self, cache, temp_cache_dir):
        """Prueba que _get_cache_file_path devuelve la ruta correcta."""
        table = "test_table"
        expected_path = os.path.join(temp_cache_dir, f"{table}.json")
        
        assert cache._get_cache_file_path(table) == expected_path
    
    def test_get_pending_operations_file_path(self, cache, temp_cache_dir):
        """Prueba que _get_pending_operations_file_path devuelve la ruta correcta."""
        expected_path = os.path.join(temp_cache_dir, "pending_operations.json")
        
        assert cache._get_pending_operations_file_path() == expected_path
    
    def test_set_and_get(self, cache):
        """Prueba que set y get funcionan correctamente."""
        table = "test_table"
        data = {"id": "1", "name": "Test"}
        
        # Guardar datos
        cache.set(table, data)
        
        # Obtener datos
        result = cache.get(table)
        
        assert len(result) == 1
        assert result[0] == data
    
    def test_get_with_id(self, cache):
        """Prueba que get con ID funciona correctamente."""
        table = "test_table"
        data1 = {"id": "1", "name": "Test 1"}
        data2 = {"id": "2", "name": "Test 2"}
        
        # Guardar datos
        cache.set(table, [data1, data2])
        
        # Obtener datos por ID
        result = cache.get(table, id="1")
        
        assert len(result) == 1
        assert result[0] == data1
    
    def test_get_with_filters(self, cache):
        """Prueba que get con filtros funciona correctamente."""
        table = "test_table"
        data1 = {"id": "1", "name": "Test 1", "category": "A"}
        data2 = {"id": "2", "name": "Test 2", "category": "B"}
        data3 = {"id": "3", "name": "Test 3", "category": "A"}
        
        # Guardar datos
        cache.set(table, [data1, data2, data3])
        
        # Obtener datos por filtro
        result = cache.get(table, filters={"category": "A"})
        
        assert len(result) == 2
        assert data1 in result
        assert data3 in result
    
    def test_update(self, cache):
        """Prueba que la operación de actualización funciona correctamente."""
        table = "test_table"
        data = {"id": "1", "name": "Test", "value": 10}
        
        # Guardar datos iniciales
        cache.set(table, data)
        
        # Actualizar datos
        updated_data = {"id": "1", "value": 20}
        cache.set(table, updated_data, operation="update")
        
        # Obtener datos actualizados
        result = cache.get(table, id="1")
        
        assert len(result) == 1
        assert result[0]["id"] == "1"
        assert result[0]["name"] == "Test"  # No debería cambiar
        assert result[0]["value"] == 20  # Debería actualizarse
    
    def test_upsert_new(self, cache):
        """Prueba que upsert añade un nuevo registro si no existe."""
        table = "test_table"
        data = {"id": "1", "name": "Test"}
        
        # Upsert (debería insertar)
        cache.set(table, data, operation="upsert")
        
        # Obtener datos
        result = cache.get(table)
        
        assert len(result) == 1
        assert result[0] == data
    
    def test_upsert_existing(self, cache):
        """Prueba que upsert actualiza un registro existente."""
        table = "test_table"
        data = {"id": "1", "name": "Test", "value": 10}
        
        # Guardar datos iniciales
        cache.set(table, data)
        
        # Upsert (debería actualizar)
        updated_data = {"id": "1", "name": "Updated", "value": 20}
        cache.set(table, updated_data, operation="upsert")
        
        # Obtener datos actualizados
        result = cache.get(table, id="1")
        
        assert len(result) == 1
        assert result[0] == updated_data
    
    def test_delete(self, cache):
        """Prueba que la operación de eliminación funciona correctamente."""
        table = "test_table"
        data1 = {"id": "1", "name": "Test 1", "category": "A"}
        data2 = {"id": "2", "name": "Test 2", "category": "B"}
        
        # Guardar datos
        cache.set(table, [data1, data2])
        
        # Eliminar un registro
        cache.set(table, {"id": "1"}, operation="delete")
        
        # Verificar que se eliminó
        result = cache.get(table)
        
        assert len(result) == 1
        assert result[0] == data2
    
    def test_pending_operations(self, cache):
        """Prueba que las operaciones pendientes se registran correctamente."""
        table = "test_table"
        data = {"id": "1", "name": "Test"}
        
        # Realizar operación
        cache.set(table, data)
        
        # Obtener operaciones pendientes
        pending = cache.get_pending_operations()
        
        assert len(pending) == 1
        assert pending[0]["table"] == table
        assert pending[0]["operation"] == "upsert"  # Por defecto es upsert
        assert pending[0]["data"] == data
    
    def test_mark_operation_completed(self, cache):
        """Prueba que mark_operation_completed elimina una operación pendiente."""
        table = "test_table"
        data = {"id": "1", "name": "Test"}
        
        # Realizar operación
        cache.set(table, data)
        
        # Marcar como completada
        result = cache.mark_operation_completed(0)
        
        assert result is True
        assert len(cache.get_pending_operations()) == 0
    
    def test_clear_expired(self, cache):
        """Prueba que clear_expired elimina los elementos expirados."""
        table = "test_table"
        
        # Crear un registro con timestamp actual
        current_data = {
            "id": "1", 
            "name": "Current",
            "cached_at": datetime.now().isoformat()
        }
        
        # Crear un registro con timestamp expirado
        expired_data = {
            "id": "2", 
            "name": "Expired",
            "cached_at": (datetime.now() - timedelta(seconds=3600*2)).isoformat()
        }
        
        # Establecer max_age_seconds a 1 hora
        cache.max_age_seconds = 3600
        
        # Guardar datos directamente en memory_cache para evitar que se establezca cached_at
        cache.memory_cache[table] = [current_data, expired_data]
        
        # Limpiar expirados
        removed = cache.clear_expired()
        
        assert removed == 1
        result = cache.get(table)
        assert len(result) == 1
        assert result[0]["id"] == "1"
    
    def test_clear_all(self, cache):
        """Prueba que clear_all elimina toda la caché."""
        table1 = "test_table1"
        table2 = "test_table2"
        
        # Guardar datos en diferentes tablas
        cache.set(table1, {"id": "1", "name": "Test 1"})
        cache.set(table2, {"id": "2", "name": "Test 2"})
        
        # Limpiar todo
        cache.clear_all()
        
        assert len(cache.get(table1)) == 0
        assert len(cache.get(table2)) == 0
        assert len(cache.get_pending_operations()) == 0
    
    def test_save_and_load_cache(self, cache, temp_cache_dir):
        """Prueba que la caché se guarda y carga correctamente desde disco."""
        table = "test_table"
        data = {"id": "1", "name": "Test"}
        
        # Guardar datos
        cache.set(table, data)
        
        # Crear nueva instancia de caché (debería cargar desde disco)
        new_cache = LocalCache(cache_dir=temp_cache_dir)
        
        # Verificar que los datos se cargaron
        result = new_cache.get(table)
        
        assert len(result) == 1
        assert result[0] == data
