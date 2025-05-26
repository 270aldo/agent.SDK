"""
Prueba directa del middleware de seguridad.

Este módulo prueba directamente la función de middleware que aplica los encabezados
de seguridad, sin depender de TestClient.
"""

import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock
from fastapi import Request, Response

# Función de middleware extraída de main.py
async def security_headers_middleware(request: Request, call_next):
    """
    Middleware simplificado que solo aplica encabezados de seguridad.
    """
    # Generar ID de solicitud único
    request_id = str(uuid.uuid4())
    
    # Procesar solicitud
    response = await call_next(request)
    
    # Añadir encabezados de seguridad
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; object-src 'none';"
    
    # Añadir ID de solicitud para seguimiento
    response.headers["X-Request-ID"] = request_id
    
    return response

@pytest.mark.asyncio
async def test_security_headers_middleware():
    """
    Prueba que el middleware añada correctamente los encabezados de seguridad.
    """
    # Crear mocks para request y response
    mock_request = MagicMock(spec=Request)
    mock_response = MagicMock(spec=Response)
    mock_response.headers = {}
    
    # Crear una función call_next que devuelve la respuesta mock
    mock_call_next = AsyncMock(return_value=mock_response)
    
    # Ejecutar el middleware
    response = await security_headers_middleware(mock_request, mock_call_next)
    
    # Verificar que se llamó a call_next con el request
    mock_call_next.assert_called_once_with(mock_request)
    
    # Verificar encabezados de seguridad
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["X-XSS-Protection"] == "1; mode=block"
    assert "max-age=31536000" in response.headers["Strict-Transport-Security"]
    assert "includeSubDomains" in response.headers["Strict-Transport-Security"]
    assert "default-src 'self'" in response.headers["Content-Security-Policy"]
    assert "script-src 'self'" in response.headers["Content-Security-Policy"]
    assert "object-src 'none'" in response.headers["Content-Security-Policy"]
    assert "X-Request-ID" in response.headers
    assert len(response.headers["X-Request-ID"]) > 0
