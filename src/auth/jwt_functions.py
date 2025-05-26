"""
Funciones a nivel de módulo para la gestión de tokens JWT.

Este módulo proporciona funciones de utilidad para generar, validar y gestionar
tokens JWT utilizados para la autenticación y autorización en la API.
"""

from typing import Dict, Optional, Any
from datetime import timedelta

from src.auth.jwt_handler import JWTHandler

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Crea un token JWT de acceso.

    Args:
        data (Dict[str, Any]): Datos a incluir en el token (claims)
        expires_delta (Optional[timedelta], optional): Tiempo de expiración personalizado. Defaults to None.

    Returns:
        str: Token JWT generado
    """
    return JWTHandler.create_access_token(data, expires_delta)

def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Crea un token JWT de actualización.

    Args:
        data (Dict[str, Any]): Datos a incluir en el token (claims)
        expires_delta (Optional[timedelta], optional): Tiempo de expiración personalizado. Defaults to None.

    Returns:
        str: Token JWT de actualización generado
    """
    return JWTHandler.create_refresh_token(data, expires_delta)

def decode_token(token: str) -> Dict[str, Any]:
    """Decodifica y valida un token JWT.

    Args:
        token (str): Token JWT a decodificar

    Returns:
        Dict[str, Any]: Datos contenidos en el token

    Raises:
        jwt.PyJWTError: Si el token es inválido o ha expirado
    """
    return JWTHandler.decode_token(token)

def verify_token(token: str, token_type: str = "access") -> Dict[str, Any]:
    """Verifica un token JWT y su tipo.

    Args:
        token (str): Token JWT a verificar
        token_type (str, optional): Tipo de token esperado ("access" o "refresh"). Defaults to "access".

    Returns:
        Dict[str, Any]: Datos contenidos en el token si es válido

    Raises:
        ValueError: Si el token no es del tipo esperado
        jwt.PyJWTError: Si el token es inválido o ha expirado
    """
    return JWTHandler.verify_token(token, token_type)
