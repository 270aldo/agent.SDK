"""
Pruebas unitarias para las utilidades de reintento.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import time
from src.utils.retry_utils import (
    retry_async_operation,
    retry_operation,
    retry_async,
    retry,
    retry_db_operation,
    retry_db
)

# Pruebas para retry_operation
def test_retry_operation_success():
    """Prueba que retry_operation funciona correctamente cuando la operación tiene éxito."""
    mock_func = Mock(return_value="success")
    result = retry_operation(mock_func, max_retries=3)
    assert result == "success"
    assert mock_func.call_count == 1

def test_retry_operation_failure_then_success():
    """Prueba que retry_operation reintenta cuando la operación falla inicialmente."""
    mock_func = Mock(side_effect=[ValueError("Error"), "success"])
    result = retry_operation(mock_func, max_retries=3)
    assert result == "success"
    assert mock_func.call_count == 2

def test_retry_operation_all_failures():
    """Prueba que retry_operation lanza una excepción cuando se agotan los reintentos."""
    mock_func = Mock(side_effect=ValueError("Error"))
    with pytest.raises(ValueError):
        retry_operation(mock_func, max_retries=3)
    assert mock_func.call_count == 4  # 1 intento inicial + 3 reintentos

def test_retry_operation_with_specific_exceptions():
    """Prueba que retry_operation solo reintenta para excepciones específicas."""
    mock_func = Mock(side_effect=[ValueError("Error"), "success"])
    # Solo reintentar para ValueError
    result = retry_operation(mock_func, max_retries=3, exceptions_to_retry=(ValueError,))
    assert result == "success"
    assert mock_func.call_count == 2
    
    # Reiniciar mock
    mock_func.reset_mock()
    mock_func.side_effect = [TypeError("Error"), "success"]
    
    # No debería reintentar para TypeError
    with pytest.raises(TypeError):
        retry_operation(mock_func, max_retries=3, exceptions_to_retry=(ValueError,))
    assert mock_func.call_count == 1

def test_retry_operation_with_condition():
    """Prueba que retry_operation usa la condición para determinar si reintentar."""
    mock_func = Mock(side_effect=[ValueError("Retry"), ValueError("Don't retry"), "success"])
    
    # Solo reintentar si el mensaje de error contiene "Retry"
    def retry_condition(e):
        return "Retry" in str(e)
    
    with pytest.raises(ValueError):
        retry_operation(mock_func, max_retries=3, retry_condition=retry_condition)
    assert mock_func.call_count == 2  # Solo reintenta una vez

# Pruebas para retry_async_operation
@pytest.mark.asyncio
async def test_retry_async_operation_success():
    """Prueba que retry_async_operation funciona correctamente cuando la operación tiene éxito."""
    mock_func = AsyncMock(return_value="success")
    result = await retry_async_operation(mock_func, max_retries=3)
    assert result == "success"
    assert mock_func.call_count == 1

@pytest.mark.asyncio
async def test_retry_async_operation_failure_then_success():
    """Prueba que retry_async_operation reintenta cuando la operación falla inicialmente."""
    mock_func = AsyncMock(side_effect=[ValueError("Error"), "success"])
    result = await retry_async_operation(mock_func, max_retries=3)
    assert result == "success"
    assert mock_func.call_count == 2

@pytest.mark.asyncio
async def test_retry_async_operation_all_failures():
    """Prueba que retry_async_operation lanza una excepción cuando se agotan los reintentos."""
    mock_func = AsyncMock(side_effect=ValueError("Error"))
    with pytest.raises(ValueError):
        await retry_async_operation(mock_func, max_retries=3)
    assert mock_func.call_count == 4  # 1 intento inicial + 3 reintentos

# Pruebas para los decoradores
def test_retry_decorator():
    """Prueba que el decorador retry funciona correctamente."""
    mock_func = Mock(side_effect=[ValueError("Error"), "success"])
    
    @retry(max_retries=3)
    def decorated_func():
        return mock_func()
    
    result = decorated_func()
    assert result == "success"
    assert mock_func.call_count == 2

@pytest.mark.asyncio
async def test_retry_async_decorator():
    """Prueba que el decorador retry_async funciona correctamente."""
    mock_func = AsyncMock(side_effect=[ValueError("Error"), "success"])
    
    @retry_async(max_retries=3)
    async def decorated_func():
        return await mock_func()
    
    result = await decorated_func()
    assert result == "success"
    assert mock_func.call_count == 2

# Pruebas para retry_db_operation
@pytest.mark.asyncio
async def test_retry_db_operation():
    """Prueba que retry_db_operation funciona correctamente para operaciones de base de datos."""
    mock_func = AsyncMock(return_value="db_success")
    result = await retry_db_operation(mock_func, max_retries=3)
    assert result == "db_success"
    assert mock_func.call_count == 1
    
    # Probar con error de conexión (debería reintentar)
    mock_func.reset_mock()
    mock_func.side_effect = [ConnectionError("connection error"), "db_success"]
    result = await retry_db_operation(mock_func, max_retries=3)
    assert result == "db_success"
    assert mock_func.call_count == 2
    
    # Probar con error de tiempo de espera (debería reintentar)
    mock_func.reset_mock()
    mock_func.side_effect = [TimeoutError("timeout"), "db_success"]
    result = await retry_db_operation(mock_func, max_retries=3)
    assert result == "db_success"
    assert mock_func.call_count == 2

@pytest.mark.asyncio
async def test_retry_db_decorator():
    """Prueba que el decorador retry_db funciona correctamente."""
    mock_func = AsyncMock(side_effect=[ConnectionError("connection error"), "db_success"])
    
    @retry_db(max_retries=3)
    async def decorated_func():
        return await mock_func()
    
    result = await decorated_func()
    assert result == "db_success"
    assert mock_func.call_count == 2
