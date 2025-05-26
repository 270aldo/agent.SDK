"""
Pruebas de integración para el router de autenticación.

Este módulo contiene pruebas para verificar el correcto funcionamiento
de los endpoints de autenticación, incluyendo registro, inicio de sesión
y refresco de tokens.
"""

import pytest
import jwt
import time
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

class TestAuthRouter:
    """Pruebas para el router de autenticación."""
    
    def test_register_success(self, client):
        """Prueba el registro exitoso de un nuevo usuario."""
        # Datos de usuario para registro
        user_data = {
            "username": f"test_user_{int(time.time())}",
            "email": f"test_{int(time.time())}@example.com",
            "password": "test_password",
            "full_name": "Test User"
        }
        
        # Realizar solicitud de registro
        response = client.post("/auth/register", json=user_data)
        
        # Verificar respuesta
        assert response.status_code == 201
        assert response.json()["success"] is True
        assert "data" in response.json()
        assert "user_id" in response.json()["data"]
        assert "username" in response.json()["data"]
        assert response.json()["data"]["username"] == user_data["username"]
    
    def test_register_duplicate_username(self, client, test_user):
        """Prueba el registro con un nombre de usuario duplicado."""
        # Primero registrar un usuario
        user_data = {
            "username": test_user["username"],
            "email": f"another_{int(time.time())}@example.com",
            "password": "test_password",
            "full_name": "Test User"
        }
        
        # Intentar registrar con el mismo nombre de usuario
        response = client.post("/auth/register", json=user_data)
        
        # Verificar respuesta de error
        assert response.status_code == 400
        assert response.json()["success"] is False
        assert "error" in response.json()
        assert "code" in response.json()["error"]
        assert response.json()["error"]["code"] == "DUPLICATE_USERNAME"
    
    def test_login_success(self, client, test_user):
        """Prueba el inicio de sesión exitoso."""
        # Datos para inicio de sesión
        login_data = {
            "username": test_user["username"],
            "password": test_user["password"]
        }
        
        # Realizar solicitud de inicio de sesión
        response = client.post("/auth/login", data=login_data)
        
        # Verificar respuesta
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert "data" in response.json()
        assert "access_token" in response.json()["data"]
        assert "refresh_token" in response.json()["data"]
        assert "token_type" in response.json()["data"]
        assert response.json()["data"]["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, client):
        """Prueba el inicio de sesión con credenciales inválidas."""
        # Datos para inicio de sesión inválidos
        login_data = {
            "username": "nonexistent_user",
            "password": "wrong_password"
        }
        
        # Realizar solicitud de inicio de sesión
        response = client.post("/auth/login", data=login_data)
        
        # Verificar respuesta de error
        assert response.status_code == 401
        assert response.json()["success"] is False
        assert "error" in response.json()
        assert "code" in response.json()["error"]
        assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"
    
    def test_refresh_token_success(self, client, auth_headers):
        """Prueba el refresco exitoso de token."""
        # Obtener token de refresco
        login_response = client.post(
            "/auth/login",
            data={
                "username": "test_user",
                "password": "test_password"
            }
        )
        refresh_token = login_response.json()["data"]["refresh_token"]
        
        # Realizar solicitud de refresco de token
        response = client.post(
            "/auth/refresh-token",
            json={"refresh_token": refresh_token}
        )
        
        # Verificar respuesta
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert "data" in response.json()
        assert "access_token" in response.json()["data"]
        assert "refresh_token" in response.json()["data"]
    
    def test_refresh_token_invalid(self, client):
        """Prueba el refresco de token con un token inválido."""
        # Realizar solicitud de refresco con token inválido
        response = client.post(
            "/auth/refresh-token",
            json={"refresh_token": "invalid_token"}
        )
        
        # Verificar respuesta de error
        assert response.status_code == 401
        assert response.json()["success"] is False
        assert "error" in response.json()
        assert "code" in response.json()["error"]
        assert response.json()["error"]["code"] == "INVALID_TOKEN"
    
    def test_get_user_info(self, client, auth_headers):
        """Prueba obtener información del usuario autenticado."""
        # Realizar solicitud para obtener información del usuario
        response = client.get("/auth/me", headers=auth_headers)
        
        # Verificar respuesta
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert "data" in response.json()
        assert "username" in response.json()["data"]
        assert "email" in response.json()["data"]
        assert "permissions" in response.json()["data"]
    
    def test_get_user_info_unauthorized(self, client):
        """Prueba obtener información del usuario sin autenticación."""
        # Realizar solicitud sin token
        response = client.get("/auth/me")
        
        # Verificar respuesta de error
        assert response.status_code == 401
        assert response.json()["success"] is False
        assert "error" in response.json()
        assert "code" in response.json()["error"]
