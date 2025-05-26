"""
Pruebas unitarias para las dependencias de autenticación.

Este módulo contiene pruebas para verificar el correcto funcionamiento
de las dependencias de autenticación utilizadas para proteger endpoints.
"""

import pytest
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from unittest.mock import patch, MagicMock

from src.auth.auth_dependencies import (
    get_current_user,
    get_current_active_user,
    has_required_permissions,
    has_admin_role
)
from src.auth.auth_utils import TokenData

# Crear un mock para OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class TestAuthDependencies:
    """Pruebas para las dependencias de autenticación."""
    
    @patch("src.auth.auth_dependencies.verify_token")
    async def test_get_current_user_valid(self, mock_verify_token):
        """Prueba obtener el usuario actual con un token válido."""
        # Configurar el mock
        mock_token_data = TokenData(
            username="test_user",
            permissions=["read:models"],
            is_active=True
        )
        mock_verify_token.return_value = mock_token_data
        
        # Llamar a la función
        result = await get_current_user("valid_token")
        
        # Verificar resultado
        assert result == mock_token_data
        mock_verify_token.assert_called_once_with("valid_token")
    
    @patch("src.auth.auth_dependencies.verify_token")
    async def test_get_current_user_invalid(self, mock_verify_token):
        """Prueba obtener el usuario actual con un token inválido."""
        # Configurar el mock para lanzar una excepción
        mock_verify_token.side_effect = Exception("Invalid token")
        
        # Llamar a la función debe lanzar una excepción
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user("invalid_token")
        
        # Verificar excepción
        assert exc_info.value.status_code == 401
        assert "Credenciales inválidas" in str(exc_info.value.detail)
    
    async def test_get_current_active_user_active(self):
        """Prueba obtener el usuario activo cuando está activo."""
        # Crear un usuario activo
        token_data = TokenData(
            username="test_user",
            permissions=["read:models"],
            is_active=True
        )
        
        # Llamar a la función
        result = await get_current_active_user(token_data)
        
        # Verificar resultado
        assert result == token_data
    
    async def test_get_current_active_user_inactive(self):
        """Prueba obtener el usuario activo cuando está inactivo."""
        # Crear un usuario inactivo
        token_data = TokenData(
            username="test_user",
            permissions=["read:models"],
            is_active=False
        )
        
        # Llamar a la función debe lanzar una excepción
        with pytest.raises(HTTPException) as exc_info:
            await get_current_active_user(token_data)
        
        # Verificar excepción
        assert exc_info.value.status_code == 403
        assert "Usuario inactivo" in str(exc_info.value.detail)
    
    async def test_has_required_permissions_with_all_permissions(self):
        """Prueba verificar permisos cuando el usuario tiene todos los permisos requeridos."""
        # Crear una dependencia que requiere permisos
        dependency = has_required_permissions(["read:models", "read:analytics"])
        
        # Crear un usuario con todos los permisos requeridos
        token_data = TokenData(
            username="test_user",
            permissions=["read:models", "read:analytics", "write:models"],
            is_active=True
        )
        
        # Llamar a la función
        result = await dependency(token_data)
        
        # Verificar resultado
        assert result == token_data
    
    async def test_has_required_permissions_with_missing_permissions(self):
        """Prueba verificar permisos cuando el usuario no tiene todos los permisos requeridos."""
        # Crear una dependencia que requiere permisos
        dependency = has_required_permissions(["read:models", "write:models"])
        
        # Crear un usuario con permisos insuficientes
        token_data = TokenData(
            username="test_user",
            permissions=["read:models"],
            is_active=True
        )
        
        # Llamar a la función debe lanzar una excepción
        with pytest.raises(HTTPException) as exc_info:
            await dependency(token_data)
        
        # Verificar excepción
        assert exc_info.value.status_code == 403
        assert "Permisos insuficientes" in str(exc_info.value.detail)
    
    async def test_has_required_permissions_with_admin(self):
        """Prueba verificar permisos cuando el usuario tiene rol de administrador."""
        # Crear una dependencia que requiere permisos
        dependency = has_required_permissions(["read:models", "write:models"])
        
        # Crear un usuario administrador
        token_data = TokenData(
            username="admin_user",
            permissions=["admin"],
            is_active=True
        )
        
        # Llamar a la función
        result = await dependency(token_data)
        
        # Verificar resultado (los administradores tienen todos los permisos)
        assert result == token_data
    
    async def test_has_admin_role_with_admin(self):
        """Prueba verificar rol de administrador cuando el usuario es administrador."""
        # Crear un usuario administrador
        token_data = TokenData(
            username="admin_user",
            permissions=["admin"],
            is_active=True
        )
        
        # Llamar a la función
        result = await has_admin_role(token_data)
        
        # Verificar resultado
        assert result == token_data
    
    async def test_has_admin_role_without_admin(self):
        """Prueba verificar rol de administrador cuando el usuario no es administrador."""
        # Crear un usuario no administrador
        token_data = TokenData(
            username="test_user",
            permissions=["read:models", "write:models"],
            is_active=True
        )
        
        # Llamar a la función debe lanzar una excepción
        with pytest.raises(HTTPException) as exc_info:
            await has_admin_role(token_data)
        
        # Verificar excepción
        assert exc_info.value.status_code == 403
        assert "Se requiere rol de administrador" in str(exc_info.value.detail)
