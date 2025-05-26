"""
Configuración para pruebas con pytest.

Este módulo contiene fixtures y configuraciones comunes para las pruebas.
"""

import os
import sys
import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient

# Añadir el directorio raíz al path para importaciones
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Cargar variables de entorno para pruebas
load_dotenv(".env.test", override=True)

# Configurar variables de entorno para pruebas si no existen
if not os.getenv("JWT_SECRET"):
    os.environ["JWT_SECRET"] = "test_secret_key_for_testing_only"
if not os.getenv("JWT_ALGORITHM"):
    os.environ["JWT_ALGORITHM"] = "HS256"
if not os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES"):
    os.environ["JWT_ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
if not os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS"):
    os.environ["JWT_REFRESH_TOKEN_EXPIRE_DAYS"] = "7"
if not os.getenv("ENVIRONMENT"):
    os.environ["ENVIRONMENT"] = "testing"

# Importar la aplicación después de configurar las variables de entorno
from src.api.main import app

@pytest.fixture
def client():
    """
    Fixture que proporciona un cliente de prueba para la API.
    """
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def test_user():
    """
    Fixture que proporciona datos de un usuario de prueba.
    """
    return {
        "username": "test_user",
        "email": "test@example.com",
        "password": "test_password",
        "full_name": "Test User",
        "permissions": ["read:models", "read:analytics"]
    }

@pytest.fixture
def test_admin():
    """
    Fixture que proporciona datos de un usuario administrador de prueba.
    """
    return {
        "username": "test_admin",
        "email": "admin@example.com",
        "password": "admin_password",
        "full_name": "Test Admin",
        "permissions": ["admin"]
    }

@pytest.fixture
def auth_headers(client, test_user):
    """
    Fixture que proporciona encabezados de autenticación para un usuario normal.
    """
    # Iniciar sesión para obtener token
    response = client.post(
        "/auth/login",
        data={
            "username": test_user["username"],
            "password": test_user["password"]
        }
    )
    
    # Si el usuario no existe, crearlo primero
    if response.status_code == 401:
        client.post(
            "/auth/register",
            json={
                "username": test_user["username"],
                "email": test_user["email"],
                "password": test_user["password"],
                "full_name": test_user["full_name"]
            }
        )
        
        # Ahora iniciar sesión
        response = client.post(
            "/auth/login",
            data={
                "username": test_user["username"],
                "password": test_user["password"]
            }
        )
    
    token = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def admin_headers(client, test_admin):
    """
    Fixture que proporciona encabezados de autenticación para un usuario administrador.
    """
    # Iniciar sesión para obtener token
    response = client.post(
        "/auth/login",
        data={
            "username": test_admin["username"],
            "password": test_admin["password"]
        }
    )
    
    # Si el administrador no existe, crearlo primero
    if response.status_code == 401:
        client.post(
            "/auth/register",
            json={
                "username": test_admin["username"],
                "email": test_admin["email"],
                "password": test_admin["password"],
                "full_name": test_admin["full_name"],
                "is_admin": True
            }
        )
        
        # Ahora iniciar sesión
        response = client.post(
            "/auth/login",
            data={
                "username": test_admin["username"],
                "password": test_admin["password"]
            }
        )
    
    token = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def mock_supabase():
    """
    Fixture que proporciona un mock para Supabase.
    """
    # Aquí implementaremos mocks para Supabase cuando sea necesario
    pass
