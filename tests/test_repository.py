import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import uuid

from src.repos.base_repo import BaseRepo
from src.repos.supabase_repo import SupabaseRepo
from src.integrations.supabase.resilient_client import ResilientSupabaseClient


class TestBaseRepo(BaseRepo):
    """Implementación concreta de BaseRepo para pruebas"""
    
    async def insert(self, table_name, data):
        """Implementación de prueba para insert"""
        return {"id": str(uuid.uuid4()), **data}
    
    async def select(self, table_name, query=None):
        """Implementación de prueba para select"""
        return [{"id": str(uuid.uuid4()), "name": "test"}]
    
    async def update(self, table_name, id_value, data):
        """Implementación de prueba para update"""
        return {"id": id_value, **data}
    
    async def delete(self, table_name, id_value):
        """Implementación de prueba para delete"""
        return {"id": id_value, "deleted": True}


@pytest.fixture
def base_repo():
    """Fixture para BaseRepo"""
    return TestBaseRepo()


@pytest.fixture
def supabase_repo():
    """Fixture para SupabaseRepo"""
    # Mock Supabase client
    class _DummyClient(ResilientSupabaseClient):
        def table(self, table_name):
            class _DummyTable:
                def __init__(self):
                    self.table_name = table_name
                
                def insert(self, data, *args, **kwargs):
                    return self
                
                def select(self, *columns):
                    return self
                
                def eq(self, column, value):
                    return self
                
                def update(self, data):
                    return self
                
                def delete(self):
                    return self
                    
                def single(self):
                    return self
                    
                def limit(self, limit_value):
                    return self
                
                def execute(self):
                    class _Res:
                        def __init__(self):
                            # Asegurar que data siempre sea una lista con al menos un elemento
                            self.data = [{"id": str(uuid.uuid4()), "name": "test", "value": 123}]
                    return _Res()
                
                # Métodos encadenables adicionales
                order = filter = match = neq = gt = lt = gte = lte = eq
            
            return _DummyTable()
    
    supabase = _DummyClient()
    return SupabaseRepo(supabase)


@pytest.mark.asyncio
async def test_base_repo_crud(base_repo):
    """Test para operaciones CRUD en BaseRepo"""
    # Insert
    data = {"name": "test", "value": 123}
    result = await base_repo.insert("test_table", data)
    assert "id" in result
    assert result["name"] == "test"
    assert result["value"] == 123
    
    # Select
    items = await base_repo.select("test_table")
    assert isinstance(items, list)
    assert len(items) > 0
    
    # Update
    id_value = str(uuid.uuid4())
    updated_data = {"name": "updated", "value": 456}
    updated = await base_repo.update("test_table", id_value, updated_data)
    assert updated["id"] == id_value
    assert updated["name"] == "updated"
    
    # Delete
    deleted = await base_repo.delete("test_table", id_value)
    assert deleted["id"] == id_value
    assert deleted["deleted"] is True


@pytest.mark.asyncio
async def test_supabase_repo_insert(supabase_repo):
    """Test para inserción en SupabaseRepo"""
    data = {"name": "test", "value": 123}
    result = await supabase_repo.insert("test_table", data)
    
    assert result is not None
    assert isinstance(result, list)
    assert len(result) > 0
    assert "id" in result[0]
    assert "name" in result[0]
    assert "value" in result[0]
    assert isinstance(result[0]["id"], str)
    assert result[0]["name"] == "test"


@pytest.mark.asyncio
async def test_supabase_repo_select(supabase_repo):
    """Test para selección en SupabaseRepo"""
    # Sin query
    result = await supabase_repo.select("test_table")
    assert isinstance(result, list)
    assert len(result) > 0
    assert "id" in result[0]
    assert "name" in result[0]
    
    # Con query
    query = {"column": "id", "value": "test_id"}
    result = await supabase_repo.select("test_table", query)
    assert isinstance(result, list)
    assert len(result) > 0
    assert "id" in result[0]


@pytest.mark.asyncio
async def test_supabase_repo_update(supabase_repo):
    """Test para actualización en SupabaseRepo"""
    id_value = str(uuid.uuid4())
    data = {"name": "updated", "value": 456}
    result = await supabase_repo.update("test_table", id_value, data)
    
    assert result is not None
    assert isinstance(result, list)
    assert len(result) > 0
    assert "id" in result[0]
    # No podemos verificar que los datos actualizados estén en el resultado
    # ya que estamos usando un mock que siempre devuelve los mismos datos


@pytest.mark.asyncio
async def test_supabase_repo_delete(supabase_repo):
    """Test para eliminación en SupabaseRepo"""
    id_value = str(uuid.uuid4())
    result = await supabase_repo.delete("test_table", id_value)
    
    assert result is not None
    assert isinstance(result, list)
    assert len(result) > 0
    assert "id" in result[0]
