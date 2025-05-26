"""
Pruebas unitarias para las utilidades de autenticación.

Este módulo contiene pruebas para verificar el correcto funcionamiento
de las utilidades de autenticación utilizadas para manejar tokens y permisos.
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from src.auth.auth_utils import TokenData, has_permission, get_token_data, verify_permissions

class TestAuthUtils:
    """Pruebas para las utilidades de autenticación."""
    
    def test_token_data_creation(self):
        """Prueba la creación de un objeto TokenData."""
        # Crear un objeto TokenData
        token_data = TokenData(
            user_id="user123",
            username="test_user",
            permissions=["read:models", "read:analytics"]
        )
        
        # Verificar atributos
        assert token_data.user_id == "user123"
        assert token_data.username == "test_user"
        assert token_data.permissions == ["read:models", "read:analytics"]
    
    def test_token_data_default_values(self):
        """Prueba los valores por defecto de TokenData."""
        # Crear un objeto TokenData con valores mínimos
        token_data = TokenData(user_id="user123")
        
        # Verificar valores por defecto
        assert token_data.username is None
        assert token_data.permissions is None
        assert token_data.role is None
    
    def test_has_permission_with_permission(self):
        """Prueba verificar si un usuario tiene un permiso específico cuando lo tiene."""
        # Crear un objeto TokenData con permisos
        token_data = TokenData(
            user_id="user123",
            username="test_user",
            permissions=["read:models", "read:analytics"]
        )
        
        # Verificar permiso
        assert has_permission(token_data, "read:models") is True
    
    def test_has_permission_without_permission(self):
        """Prueba verificar si un usuario tiene un permiso específico cuando no lo tiene."""
        # Crear un objeto TokenData sin el permiso requerido
        token_data = TokenData(
            user_id="user123",
            username="test_user",
            permissions=["read:models"]
        )
        
        # Verificar permiso
        assert has_permission(token_data, "write:models") is False
    
    def test_has_permission_with_admin(self):
        """Prueba verificar si un usuario administrador tiene cualquier permiso."""
        # Crear un objeto TokenData de administrador
        token_data = TokenData(
            user_id="admin123",
            username="admin_user",
            role="admin"
        )
        
        # Verificar varios permisos
        assert has_permission(token_data, "read:models") is True
        assert has_permission(token_data, "write:models") is True
        assert has_permission(token_data, "cualquier:permiso") is True
    
    @patch('src.auth.auth_utils.JWTHandler')
    def test_get_token_data_valid(self, mock_jwt_handler):
        """Prueba obtener datos de token con un token válido."""
        # Configurar mock
        mock_payload = {
            "sub": "user123",
            "username": "test_user",
            "permissions": ["read:models"],
            "type": "access"
        }
        mock_jwt_handler.verify_token.return_value = mock_payload
        
        # Llamar a la función
        token_data = get_token_data("valid_token")
        
        # Verificar resultado
        assert token_data.user_id == "user123"
        assert token_data.username == "test_user"
        assert token_data.permissions == ["read:models"]
    
    @patch('src.auth.auth_utils.JWTHandler')
    def test_get_token_data_invalid(self, mock_jwt_handler):
        """Prueba obtener datos de token con un token inválido."""
        # Configurar mock para lanzar una excepción
        mock_jwt_handler.verify_token.side_effect = Exception("Token inválido")
        
        # Llamar a la función debe lanzar una excepción
        with pytest.raises(HTTPException) as exc_info:
            get_token_data("invalid_token")
        
        # Verificar excepción
        assert exc_info.value.status_code == 401
    
    def test_verify_permissions_with_permissions(self):
        """Prueba verificar permisos cuando el usuario tiene los permisos requeridos."""
        # Crear un objeto TokenData con permisos
        token_data = TokenData(
            user_id="user123",
            username="test_user",
            permissions=["read:models", "write:models"]
        )
        
        # Verificar permisos (no debe lanzar excepción)
        verify_permissions(token_data, ["read:models"])
    
    def test_verify_permissions_without_permissions(self):
        """Prueba verificar permisos cuando el usuario no tiene los permisos requeridos."""
        # Crear un objeto TokenData sin los permisos requeridos
        token_data = TokenData(
            user_id="user123",
            username="test_user",
            permissions=["read:models"]
        )
        
        # Verificar permisos debe lanzar una excepción
        with pytest.raises(HTTPException) as exc_info:
            verify_permissions(token_data, ["write:models"])
        
        # Verificar excepción
        assert exc_info.value.status_code == 403
