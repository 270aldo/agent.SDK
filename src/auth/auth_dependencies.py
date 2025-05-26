"""
Dependencias de autenticación para FastAPI.

Este módulo proporciona dependencias que pueden ser utilizadas en los endpoints
de FastAPI para implementar autenticación y autorización.
"""

import logging
from typing import List, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from .jwt_functions import verify_token
from .auth_utils import TokenData, get_token_data, verify_permissions

logger = logging.getLogger(__name__)

# Configurar OAuth2PasswordBearer para obtener el token de la cabecera
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    """
    Dependencia para obtener el usuario actual a partir del token JWT.
    
    Args:
        token: Token JWT obtenido de la cabecera de autorización
        
    Returns:
        TokenData: Datos del usuario extraídos del token
        
    Raises:
        HTTPException: Si el token es inválido o ha expirado
    """
    return get_token_data(token)

async def get_current_active_user(current_user: TokenData = Depends(get_current_user)) -> TokenData:
    """
    Dependencia para verificar que el usuario actual está activo.
    
    Args:
        current_user: Datos del usuario actual
        
    Returns:
        TokenData: Datos del usuario si está activo
        
    Raises:
        HTTPException: Si el usuario no está activo
    """
    # Aquí se podría verificar si el usuario está activo en la base de datos
    # Por ahora, asumimos que todos los usuarios con token válido están activos
    return current_user

def has_required_permissions(required_permissions: List[str] = []):
    """
    Crea una dependencia para verificar que el usuario tiene los permisos requeridos.
    
    Args:
        required_permissions: Lista de permisos requeridos
        
    Returns:
        Callable: Dependencia que verifica los permisos
    """
    async def verify_user_permissions(current_user: TokenData = Depends(get_current_active_user)) -> TokenData:
        """
        Verifica que el usuario tiene los permisos requeridos.
        
        Args:
            current_user: Datos del usuario actual
            
        Returns:
            TokenData: Datos del usuario si tiene los permisos requeridos
            
        Raises:
            HTTPException: Si el usuario no tiene los permisos requeridos
        """
        verify_permissions(current_user, required_permissions)
        return current_user
    
    return verify_user_permissions

def has_admin_role(current_user: TokenData = Depends(get_current_active_user)) -> TokenData:
    """
    Dependencia para verificar que el usuario tiene rol de administrador.
    
    Args:
        current_user: Datos del usuario actual
        
    Returns:
        TokenData: Datos del usuario si es administrador
        
    Raises:
        HTTPException: Si el usuario no es administrador
    """
    if current_user.role != "admin":
        logger.warning(f"Usuario {current_user.username} intentó acceder a un recurso de administrador")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol de administrador para acceder a este recurso"
        )
    return current_user
