"""
Pruebas de seguridad para la API.

Este módulo contiene pruebas específicas para verificar que las medidas
de seguridad implementadas funcionen correctamente.
"""

import pytest
import time
import jwt
import os
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from tests.security.security_test_config import (
    get_test_client, create_test_token, get_auth_headers,
    create_test_user_token, create_test_admin_token, JWT_SECRET, JWT_ALGORITHM
)

class TestSecurityMeasures:
    """Pruebas para las medidas de seguridad."""
    
    def test_rate_limiting(self, security_client):
        # Usar el cliente de prueba proporcionado por el fixture
        client = security_client
        """Prueba que la limitación de tasa funcione correctamente."""
        # Realizar múltiples solicitudes rápidamente
        endpoint = "/health"
        num_requests = 70  # Más que el límite por minuto
        
        responses = []
        for _ in range(num_requests):
            response = client.get(endpoint)
            responses.append(response)
        
        # Verificar que algunas solicitudes fueron limitadas
        success_count = sum(1 for r in responses if r.status_code == 200)
        limited_count = sum(1 for r in responses if r.status_code == 429)
        
        # Debe haber al menos una solicitud limitada
        assert limited_count > 0
        # Y algunas solicitudes exitosas
        assert success_count > 0
        # El total debe ser igual al número de solicitudes
        assert success_count + limited_count == num_requests
    
    def test_security_headers(self, security_client):
        # Usar el cliente de prueba proporcionado por el fixture
        client = security_client
        """Prueba que los encabezados de seguridad estén presentes en las respuestas."""
        # Realizar una solicitud
        response = client.get("/health")
        
        # Verificar encabezados de seguridad
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        
        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"
        
        assert "X-XSS-Protection" in response.headers
        assert response.headers["X-XSS-Protection"] == "1; mode=block"
        
        assert "Strict-Transport-Security" in response.headers
        assert "max-age=31536000" in response.headers["Strict-Transport-Security"]
        assert "includeSubDomains" in response.headers["Strict-Transport-Security"]
        
        assert "Content-Security-Policy" in response.headers
        assert "default-src 'self'" in response.headers["Content-Security-Policy"]
        assert "script-src 'self'" in response.headers["Content-Security-Policy"]
        assert "object-src 'none'" in response.headers["Content-Security-Policy"]
        
        assert "X-Request-ID" in response.headers
        assert len(response.headers["X-Request-ID"]) > 0
    
    def test_token_expiration(self, security_client, test_user):
        # Usar el cliente de prueba proporcionado por el fixture
        client = security_client
        """Prueba que los tokens expiren correctamente."""
        # Iniciar sesión para obtener token
        login_response = client.post(
            "/auth/login",
            data={
                "username": test_user["username"],
                "password": test_user["password"]
            }
        )
        
        # Obtener token
        token = login_response.json()["data"]["access_token"]
        
        # Decodificar token para verificar tiempo de expiración
        decoded = jwt.decode(token, options={"verify_signature": False})
        
        # Verificar que el token tiene tiempo de expiración
        assert "exp" in decoded
        
        # Calcular tiempo hasta expiración
        expiration_time = datetime.fromtimestamp(decoded["exp"])
        now = datetime.utcnow()
        time_until_expiration = expiration_time - now
        
        # Verificar que el tiempo de expiración es aproximadamente el esperado
        expected_expiration = timedelta(minutes=int(pytest.MonkeyPatch().context.environ.get("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 30)))
        assert abs((time_until_expiration - expected_expiration).total_seconds()) < 60  # Margen de 1 minuto
    
    def test_invalid_token_rejection(self, security_client):
        # Usar el cliente de prueba proporcionado por el fixture
        client = security_client
        """Prueba que los tokens inválidos sean rechazados."""
        # Crear un token inválido
        invalid_token = "invalid.token.here"
        
        # Intentar acceder a un endpoint protegido
        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {invalid_token}"}
        )
        
        # Verificar que se rechaza el token
        assert response.status_code == 401
        assert response.json()["success"] is False
        assert "error" in response.json()
        assert "code" in response.json()["error"]
        assert response.json()["error"]["code"] == "UNAUTHORIZED"
    
    def test_expired_token_rejection(self, security_client):
        # Usar el cliente de prueba proporcionado por el fixture
        client = security_client
        """Prueba que los tokens expirados sean rechazados."""
        # Crear un token expirado manualmente
        payload = {
            "sub": "test_user",
            "permissions": ["read:models"],
            "exp": datetime.utcnow() - timedelta(minutes=5),  # Expirado hace 5 minutos
            "iat": datetime.utcnow() - timedelta(hours=2),
            "type": "access"  # Debe ser 'type', no 'token_type'
        }
        
        # Firmar el token
        expired_token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        
        # Intentar acceder a un endpoint protegido
        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        
        # Verificar que se rechaza el token
        assert response.status_code == 401
        assert response.json()["success"] is False
        assert "error" in response.json()
        assert "code" in response.json()["error"]
        assert response.json()["error"]["code"] == "UNAUTHORIZED"
    
    def test_permission_enforcement(self, security_client, auth_headers, admin_headers):
        # Usar el cliente de prueba proporcionado por el fixture
        client = security_client
        """Prueba que se apliquen correctamente los permisos."""
        # Endpoint que requiere permisos de administrador
        endpoint = "/predictive/models"
        
        # Intentar acceder con usuario normal
        normal_response = client.get(
            endpoint,
            headers=auth_headers
        )
        
        # Verificar que se rechaza al usuario normal
        assert normal_response.status_code == 403
        assert normal_response.json()["success"] is False
        assert "error" in normal_response.json()
        assert "code" in normal_response.json()["error"]
        assert normal_response.json()["error"]["code"] == "FORBIDDEN"
        
        # Intentar acceder con administrador
        admin_response = client.get(
            endpoint,
            headers=admin_headers
        )
        
        # Verificar que se permite al administrador
        assert admin_response.status_code == 200
        assert admin_response.json()["success"] is True
    
    def test_input_validation(self, security_client, auth_headers):
        # Usar el cliente de prueba proporcionado por el fixture
        client = security_client
        """Prueba que la validación de entradas funcione correctamente."""
        # Datos inválidos para la solicitud
        invalid_data = {
            "conversation_id": "test_conv",
            "messages": [
                {
                    "role": "invalid_role",  # Rol inválido
                    "content": "Mensaje de prueba",
                    "timestamp": datetime.utcnow().isoformat()
                }
            ]
        }
        
        # Realizar solicitud con datos inválidos
        response = client.post(
            "/predictive/objection/predict",
            json=invalid_data,
            headers=auth_headers
        )
        
        # Verificar respuesta de error de validación
        assert response.status_code == 422
        assert response.json()["success"] is False
        assert "error" in response.json()
        assert "code" in response.json()["error"]
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"
        assert "role" in response.json()["error"]["message"].lower()  # El mensaje debe mencionar el campo inválido
    
    def test_error_sanitization(self, security_client):
        # Usar el cliente de prueba proporcionado por el fixture
        client = security_client
        """Prueba que los errores internos no expongan información sensible."""
        # Intentar acceder a un endpoint que no existe para generar un error
        response = client.get("/non_existent_endpoint")
        
        # Verificar que la respuesta es un error 404
        assert response.status_code == 404
        
        # Verificar que la respuesta tiene contenido
        assert response.content
        
        # Convertir la respuesta a texto para buscar información sensible
        response_text = response.text.lower()
        
        # Verificar que no hay información sensible en la respuesta
        assert "traceback" not in response_text, "La respuesta contiene 'traceback'"
        assert "stack" not in response_text, "La respuesta contiene 'stack'"
