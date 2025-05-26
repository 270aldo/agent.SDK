"""
Pruebas unitarias para el manejador de JWT.

Este módulo contiene pruebas para verificar el correcto funcionamiento
de la creación, decodificación y validación de tokens JWT.
"""

import pytest
import jwt
import time
from datetime import datetime, timedelta
from src.auth.jwt_handler import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_token
)

class TestJWTHandler:
    """Pruebas para el manejador de JWT."""
    
    def test_create_access_token(self):
        """Prueba la creación de un token de acceso."""
        # Datos para el token
        data = {"sub": "test_user", "permissions": ["read:models"]}
        
        # Crear token
        token = create_access_token(data)
        
        # Verificar que el token es una cadena no vacía
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Decodificar token para verificar contenido
        decoded = jwt.decode(
            token,
            key=pytest.MonkeyPatch().context.environ.get("JWT_SECRET", "test_secret_key_for_testing_only"),
            algorithms=[pytest.MonkeyPatch().context.environ.get("JWT_ALGORITHM", "HS256")]
        )
        
        # Verificar que los datos están presentes
        assert decoded["sub"] == "test_user"
        assert decoded["permissions"] == ["read:models"]
        assert "exp" in decoded
        assert "iat" in decoded
        assert decoded["token_type"] == "access"
    
    def test_create_access_token_with_expiration(self):
        """Prueba la creación de un token de acceso con tiempo de expiración personalizado."""
        # Datos para el token
        data = {"sub": "test_user"}
        expires_delta = timedelta(minutes=5)
        
        # Crear token
        token = create_access_token(data, expires_delta)
        
        # Decodificar token
        decoded = jwt.decode(
            token,
            key=pytest.MonkeyPatch().context.environ.get("JWT_SECRET", "test_secret_key_for_testing_only"),
            algorithms=[pytest.MonkeyPatch().context.environ.get("JWT_ALGORITHM", "HS256")]
        )
        
        # Verificar tiempo de expiración
        now = datetime.utcnow().timestamp()
        assert decoded["exp"] - now <= 5 * 60 + 1  # 5 minutos + 1 segundo de margen
    
    def test_create_refresh_token(self):
        """Prueba la creación de un token de refresco."""
        # Datos para el token
        data = {"sub": "test_user"}
        
        # Crear token
        token = create_refresh_token(data)
        
        # Verificar que el token es una cadena no vacía
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Decodificar token
        decoded = jwt.decode(
            token,
            key=pytest.MonkeyPatch().context.environ.get("JWT_SECRET", "test_secret_key_for_testing_only"),
            algorithms=[pytest.MonkeyPatch().context.environ.get("JWT_ALGORITHM", "HS256")]
        )
        
        # Verificar que los datos están presentes
        assert decoded["sub"] == "test_user"
        assert "exp" in decoded
        assert "iat" in decoded
        assert decoded["token_type"] == "refresh"
    
    def test_decode_token_valid(self):
        """Prueba la decodificación de un token válido."""
        # Datos para el token
        data = {"sub": "test_user", "permissions": ["read:models"]}
        
        # Crear token
        token = create_access_token(data)
        
        # Decodificar token
        decoded = decode_token(token)
        
        # Verificar que los datos están presentes
        assert decoded["sub"] == "test_user"
        assert decoded["permissions"] == ["read:models"]
        assert decoded["token_type"] == "access"
    
    def test_decode_token_invalid(self):
        """Prueba la decodificación de un token inválido."""
        # Token inválido
        token = "invalid.token.here"
        
        # Decodificar token debe lanzar una excepción
        with pytest.raises(jwt.PyJWTError):
            decode_token(token)
    
    def test_decode_token_expired(self):
        """Prueba la decodificación de un token expirado."""
        # Datos para el token
        data = {"sub": "test_user"}
        
        # Crear token que expire inmediatamente
        expires_delta = timedelta(seconds=-1)
        token = create_access_token(data, expires_delta)
        
        # Decodificar token debe lanzar una excepción
        with pytest.raises(jwt.PyJWTError):
            decode_token(token)
    
    def test_verify_token_valid(self):
        """Prueba la verificación de un token válido."""
        # Datos para el token
        data = {"sub": "test_user", "permissions": ["read:models"]}
        
        # Crear token
        token = create_access_token(data)
        
        # Verificar token
        token_data = verify_token(token)
        
        # Verificar que los datos están presentes
        assert token_data.username == "test_user"
        assert token_data.permissions == ["read:models"]
    
    def test_verify_token_invalid(self):
        """Prueba la verificación de un token inválido."""
        # Token inválido
        token = "invalid.token.here"
        
        # Verificar token debe lanzar una excepción
        with pytest.raises(Exception):
            verify_token(token)
    
    def test_verify_token_missing_sub(self):
        """Prueba la verificación de un token sin campo 'sub'."""
        # Datos para el token sin 'sub'
        data = {"permissions": ["read:models"]}
        
        # Crear token manualmente
        secret = pytest.MonkeyPatch().context.environ.get("JWT_SECRET", "test_secret_key_for_testing_only")
        algorithm = pytest.MonkeyPatch().context.environ.get("JWT_ALGORITHM", "HS256")
        expiration = datetime.utcnow() + timedelta(minutes=30)
        
        payload = {
            "permissions": ["read:models"],
            "exp": expiration,
            "iat": datetime.utcnow(),
            "token_type": "access"
        }
        
        token = jwt.encode(payload, secret, algorithm=algorithm)
        
        # Verificar token debe lanzar una excepción
        with pytest.raises(Exception):
            verify_token(token)
