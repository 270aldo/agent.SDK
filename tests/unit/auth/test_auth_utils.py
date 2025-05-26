"""
Pruebas unitarias para las utilidades de autenticación.

Este módulo contiene pruebas para verificar el correcto funcionamiento
de las utilidades de autenticación utilizadas para manejar tokens y permisos.
"""

import pytest
from src.auth.auth_utils import TokenData, has_permission, has_admin_permission

class TestAuthUtils:
    """Pruebas para las utilidades de autenticación."""
    
    def test_token_data_creation(self):
        """Prueba la creación de un objeto TokenData."""
        # Crear un objeto TokenData
        token_data = TokenData(
            username="test_user",
            permissions=["read:models", "read:analytics"],
            is_active=True
        )
        
        # Verificar atributos
        assert token_data.username == "test_user"
        assert token_data.permissions == ["read:models", "read:analytics"]
        assert token_data.is_active is True
    
    def test_token_data_default_values(self):
        """Prueba los valores por defecto de TokenData."""
        # Crear un objeto TokenData con valores mínimos
        token_data = TokenData(username="test_user")
        
        # Verificar valores por defecto
        assert token_data.permissions == []
        assert token_data.is_active is True
    
    def test_has_permission_with_permission(self):
        """Prueba verificar si un usuario tiene un permiso específico cuando lo tiene."""
        # Crear un objeto TokenData con permisos
        token_data = TokenData(
            username="test_user",
            permissions=["read:models", "read:analytics"]
        )
        
        # Verificar permiso
        assert has_permission(token_data, "read:models") is True
    
    def test_has_permission_without_permission(self):
        """Prueba verificar si un usuario tiene un permiso específico cuando no lo tiene."""
        # Crear un objeto TokenData sin el permiso requerido
        token_data = TokenData(
            username="test_user",
            permissions=["read:models"]
        )
        
        # Verificar permiso
        assert has_permission(token_data, "write:models") is False
    
    def test_has_permission_with_admin(self):
        """Prueba verificar si un usuario administrador tiene cualquier permiso."""
        # Crear un objeto TokenData de administrador
        token_data = TokenData(
            username="admin_user",
            permissions=["admin"]
        )
        
        # Verificar varios permisos
        assert has_permission(token_data, "read:models") is True
        assert has_permission(token_data, "write:models") is True
        assert has_permission(token_data, "cualquier:permiso") is True
    
    def test_has_admin_permission_with_admin(self):
        """Prueba verificar si un usuario tiene permiso de administrador cuando lo tiene."""
        # Crear un objeto TokenData de administrador
        token_data = TokenData(
            username="admin_user",
            permissions=["admin"]
        )
        
        # Verificar permiso de administrador
        assert has_admin_permission(token_data) is True
    
    def test_has_admin_permission_without_admin(self):
        """Prueba verificar si un usuario tiene permiso de administrador cuando no lo tiene."""
        # Crear un objeto TokenData sin permiso de administrador
        token_data = TokenData(
            username="test_user",
            permissions=["read:models", "write:models"]
        )
        
        # Verificar permiso de administrador
        assert has_admin_permission(token_data) is False
