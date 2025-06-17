"""
Configuración para pruebas de seguridad.

Este módulo proporciona funciones y variables de configuración
para las pruebas de seguridad de la API.
"""

import os
import jwt
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

# Configuración de JWT para pruebas
JWT_SECRET = "test_secret_key_for_testing_only"
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30
JWT_REFRESH_TOKEN_EXPIRE_DAYS = 7

# Asegurar que las variables de entorno estén configuradas para las pruebas
os.environ["ENVIRONMENT"] = "testing"
os.environ["JWT_SECRET"] = JWT_SECRET
os.environ["JWT_ALGORITHM"] = JWT_ALGORITHM
os.environ["JWT_ACCESS_TOKEN_EXPIRE_MINUTES"] = str(JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
os.environ["JWT_REFRESH_TOKEN_EXPIRE_DAYS"] = str(JWT_REFRESH_TOKEN_EXPIRE_DAYS)
os.environ["RATE_LIMIT_PER_MINUTE"] = "60"
os.environ["RATE_LIMIT_PER_HOUR"] = "1000"
os.environ["LOG_LEVEL"] = "INFO"
os.environ["ALLOWED_ORIGINS"] = "http://testserver,http://localhost:8000"

def get_test_client():
    """
    Obtiene un cliente de prueba para la API.
    
    Returns:
        TestClient: Cliente de prueba para la API.
    """
    # Importar aquí para evitar problemas de importación circular
    from src.api.main import app
    return TestClient(app)

def create_test_token(data, expires_delta=None, token_type="access"):
    """
    Crea un token JWT para pruebas.
    
    Args:
        data (dict): Datos a incluir en el token.
        expires_delta (timedelta, optional): Tiempo de expiración personalizado.
        token_type (str, optional): Tipo de token ("access" o "refresh").
        
    Returns:
        str: Token JWT generado.
    """
    to_encode = data.copy()
    
    # Establecer tiempo de expiración
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    elif token_type == "access":
        expire = datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    else:
        expire = datetime.utcnow() + timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    
    # Añadir claims estándar
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": token_type
    })
    
    # Generar token
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def get_auth_headers(token):
    """
    Obtiene los encabezados de autorización para un token.
    
    Args:
        token (str): Token JWT.
        
    Returns:
        dict: Encabezados de autorización.
    """
    return {"Authorization": f"Bearer {token}"}

def create_test_user_token(user_id="test_user", username="test_user", permissions=None, role=None):
    """
    Crea un token para un usuario de prueba.
    
    Args:
        user_id (str, optional): ID del usuario.
        username (str, optional): Nombre de usuario.
        permissions (list, optional): Permisos del usuario.
        role (str, optional): Rol del usuario.
        
    Returns:
        str: Token JWT generado.
    """
    data = {"sub": user_id, "username": username}
    if permissions:
        data["permissions"] = permissions
    if role:
        data["role"] = role
    
    return create_test_token(data)

def create_test_admin_token(user_id="admin_user", username="admin_user"):
    """
    Crea un token para un administrador de prueba.
    
    Args:
        user_id (str, optional): ID del administrador.
        username (str, optional): Nombre de usuario del administrador.
        
    Returns:
        str: Token JWT generado.
    """
    return create_test_user_token(
        user_id=user_id,
        username=username,
        permissions=["*"],
        role="admin"
    )
