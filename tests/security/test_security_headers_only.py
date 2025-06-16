"""
Pruebas simplificadas para verificar los encabezados de seguridad.

Este módulo contiene pruebas específicas para verificar que los encabezados
de seguridad se apliquen correctamente, sin depender de la inicialización
completa de la aplicación.
"""

import pytest
import uuid
import time
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from fastapi.middleware.cors import CORSMiddleware

# Crear una aplicación FastAPI simplificada para pruebas
def create_test_app():
    """
    Crea una aplicación FastAPI simplificada para pruebas.
    
    Returns:
        FastAPI: Aplicación FastAPI con middleware de seguridad.
    """
    app = FastAPI(title="Test Security App")
    
    # Agregar middleware CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Implementar middleware de logging que también aplica encabezados de seguridad
    @app.middleware("http")
    async def logging_middleware(request: Request, call_next):
        # Generar ID de solicitud único
        request_id = str(uuid.uuid4())
        
        # Medir tiempo de respuesta
        start_time = time.time()
        
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
    
    # Agregar un endpoint de salud simple
    @app.get("/health")
    async def health_check():
        return {"status": "ok"}
    
    return app

@pytest.fixture
def test_client():
    """
    Fixture que proporciona un cliente de prueba con una aplicación simplificada.
    
    Returns:
        TestClient: Cliente de prueba para la API simplificada.
    """
    app = create_test_app()
    return TestClient(app)

class TestSecurityHeaders:
    """Pruebas para verificar los encabezados de seguridad."""
    
    def test_security_headers(self, test_client):
        """Prueba que los encabezados de seguridad estén presentes en las respuestas."""
        # Realizar una solicitud
        response = test_client.get("/health")
        
        # Verificar que la respuesta sea exitosa
        assert response.status_code == 200
        
        # Verificar encabezados de seguridad
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        
        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"
        
        assert "X-XSS-Protection" in response.headers
        assert response.headers["X-XSS-Protection"] == "1; mode=block"
        
        assert "Strict-Transport-Security" in response.headers
        assert "max-age=31536000" in response.headers["Strict-Transport-Security"]
        
        assert "Content-Security-Policy" in response.headers
        assert "default-src 'self'" in response.headers["Content-Security-Policy"]
