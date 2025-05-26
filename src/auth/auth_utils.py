"""
Utilidades para la autenticación y autorización.

Este módulo proporciona funciones y clases de utilidad para
la autenticación y autorización en la API.
"""

import logging
from typing import Dict, List, Optional, Any
from fastapi import HTTPException, status
from pydantic import BaseModel

from .jwt_functions import verify_token

logger = logging.getLogger(__name__)

# Modelos de datos para autenticación
class TokenData(BaseModel):
    """Modelo para los datos contenidos en un token JWT."""
    user_id: str
    username: Optional[str] = None
    role: Optional[str] = None
    permissions: Optional[List[str]] = None
    exp: Optional[int] = None
    iat: Optional[int] = None
    type: Optional[str] = None

class Token(BaseModel):
    """Modelo para la respuesta de token."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class UserCredentials(BaseModel):
    """Modelo para las credenciales de usuario."""
    username: str
    password: str

class RefreshTokenRequest(BaseModel):
    """Modelo para la solicitud de actualización de token."""
    refresh_token: str

def get_token_data(token: str) -> TokenData:
    """
    Extrae y valida los datos de un token JWT.
    
    Args:
        token: Token JWT a validar
        
    Returns:
        TokenData: Datos extraídos del token
        
    Raises:
        HTTPException: Si el token es inválido o ha expirado
    """
    try:
        payload = verify_token(token)
        token_data = TokenData(
            user_id=payload.get("sub"),
            username=payload.get("username"),
            role=payload.get("role"),
            permissions=payload.get("permissions"),
            exp=payload.get("exp"),
            iat=payload.get("iat"),
            type=payload.get("type")
        )
        return token_data
    except Exception as e:
        logger.warning(f"Error al validar token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

def has_permission(token_data: TokenData, required_permission: str) -> bool:
    """
    Verifica si el usuario tiene un permiso específico.
    
    Args:
        token_data: Datos del token del usuario
        required_permission: Permiso requerido
        
    Returns:
        bool: True si el usuario tiene el permiso, False en caso contrario
    """
    # Si el usuario es administrador, tiene todos los permisos
    if token_data.role == "admin":
        return True
    
    # Verificar si el permiso está en la lista de permisos del usuario
    if token_data.permissions and required_permission in token_data.permissions:
        return True
    
    return False

def verify_permissions(token_data: TokenData, required_permissions: List[str]) -> None:
    """
    Verifica si el usuario tiene los permisos requeridos.
    
    Args:
        token_data: Datos del token del usuario
        required_permissions: Lista de permisos requeridos
        
    Raises:
        HTTPException: Si el usuario no tiene los permisos requeridos
    """
    # Si no hay permisos requeridos, permitir acceso
    if not required_permissions:
        return
    
    # Si el usuario es administrador, tiene todos los permisos
    if token_data.role == "admin":
        return
    
    # Verificar si el usuario tiene al menos uno de los permisos requeridos
    if token_data.permissions:
        for permission in required_permissions:
            if permission in token_data.permissions:
                return
    
    # Si no tiene ninguno de los permisos requeridos, denegar acceso
    logger.warning(f"Usuario {token_data.username} no tiene los permisos requeridos: {required_permissions}")
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="No tienes permisos suficientes para acceder a este recurso"
    )
