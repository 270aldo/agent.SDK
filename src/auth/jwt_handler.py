"""
Módulo para la gestión de tokens JWT.

Este módulo proporciona funciones para generar, validar y gestionar
tokens JWT utilizados para la autenticación y autorización en la API.
"""

import jwt
import time
import asyncio
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import os
import logging
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

logger = logging.getLogger(__name__)

# Import secrets manager
try:
    from src.infrastructure.security import secrets_manager, get_secret
except ImportError:
    # Fallback for backward compatibility
    logger.warning("Secrets manager not available, using environment variables directly")
    secrets_manager = None
    async def get_secret(key: str, required: bool = True) -> Optional[str]:
        value = os.getenv(key)
        if not value and required:
            logger.error(f"Required secret not found: {key}")
        return value

# JWT Configuration with secure defaults
_jwt_secret_cache = None
_jwt_secret_last_refresh = None
JWT_SECRET_REFRESH_INTERVAL = 3600  # Refresh secret from manager every hour

async def get_jwt_secret() -> str:
    """Get JWT secret with caching and fallback."""
    global _jwt_secret_cache, _jwt_secret_last_refresh
    
    # Check if we need to refresh the secret
    now = time.time()
    if (_jwt_secret_cache is None or 
        _jwt_secret_last_refresh is None or
        now - _jwt_secret_last_refresh > JWT_SECRET_REFRESH_INTERVAL):
        
        # Try to get from secrets manager
        if secrets_manager:
            secret = await get_secret("JWT_SECRET", required=False)
            if secret:
                _jwt_secret_cache = secret
                _jwt_secret_last_refresh = now
                return secret
        
        # Fallback to environment variable
        secret = os.getenv("JWT_SECRET")
        if secret:
            _jwt_secret_cache = secret
            _jwt_secret_last_refresh = now
            return secret
        
        # Generate a secure default (only for development)
        if os.getenv("ENVIRONMENT", "production").lower() in ["development", "test"]:
            logger.warning("JWT_SECRET not configured, generating a random secret for development")
            secret = secrets.token_urlsafe(32)
            os.environ["JWT_SECRET"] = secret
            _jwt_secret_cache = secret
            _jwt_secret_last_refresh = now
            return secret
        
        # Production requires explicit configuration
        raise ValueError("JWT_SECRET must be configured in production environment")
    
    return _jwt_secret_cache

# Synchronous wrapper for backward compatibility
def get_jwt_secret_sync() -> str:
    """Synchronous wrapper for get_jwt_secret."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If we're already in an async context, we can't use run_until_complete
            # Return cached value or raise error
            if _jwt_secret_cache:
                return _jwt_secret_cache
            else:
                # Try environment variable as last resort
                secret = os.getenv("JWT_SECRET")
                if secret:
                    return secret
                raise ValueError("JWT_SECRET not available in cache")
        else:
            return loop.run_until_complete(get_jwt_secret())
    except RuntimeError:
        # No event loop, create one
        return asyncio.run(get_jwt_secret())

JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
JWT_REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))

class JWTHandler:
    """Clase para manejar operaciones relacionadas con JWT."""
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Crea un token JWT de acceso.
        
        Args:
            data: Datos a incluir en el token (claims)
            expires_delta: Tiempo de expiración personalizado (opcional)
            
        Returns:
            str: Token JWT generado
        """
        to_encode = data.copy()
        
        # Establecer tiempo de expiración
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        
        # Añadir claims estándar
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access",
            "jti": secrets.token_urlsafe(16)  # JWT ID for revocation support
        })
        
        # Generar token con secret seguro
        try:
            jwt_secret = get_jwt_secret_sync()
            encoded_jwt = jwt.encode(to_encode, jwt_secret, algorithm=JWT_ALGORITHM)
            return encoded_jwt
        except Exception as e:
            logger.error(f"Error al generar token JWT: {str(e)}")
            raise
    
    @staticmethod
    def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Crea un token JWT de actualización.
        
        Args:
            data: Datos a incluir en el token (claims)
            expires_delta: Tiempo de expiración personalizado (opcional)
            
        Returns:
            str: Token JWT de actualización generado
        """
        to_encode = data.copy()
        
        # Establecer tiempo de expiración
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        
        # Añadir claims estándar
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh",
            "jti": secrets.token_urlsafe(16)  # JWT ID for revocation support
        })
        
        # Generar token con secret seguro
        try:
            jwt_secret = get_jwt_secret_sync()
            encoded_jwt = jwt.encode(to_encode, jwt_secret, algorithm=JWT_ALGORITHM)
            return encoded_jwt
        except Exception as e:
            logger.error(f"Error al generar token de actualización JWT: {str(e)}")
            raise
    
    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        """
        Decodifica y valida un token JWT.
        
        Args:
            token: Token JWT a decodificar
            
        Returns:
            Dict: Datos contenidos en el token
            
        Raises:
            jwt.PyJWTError: Si el token es inválido o ha expirado
        """
        try:
            jwt_secret = get_jwt_secret_sync()
            payload = jwt.decode(token, jwt_secret, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token JWT expirado")
            raise
        except jwt.InvalidTokenError as e:
            logger.warning(f"Token JWT inválido: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error al decodificar token JWT: {str(e)}")
            raise
    
    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> Dict[str, Any]:
        """
        Verifica un token JWT y su tipo.
        
        Args:
            token: Token JWT a verificar
            token_type: Tipo de token esperado ("access" o "refresh")
            
        Returns:
            Dict: Datos contenidos en el token si es válido
            
        Raises:
            ValueError: Si el token no es del tipo esperado
            jwt.PyJWTError: Si el token es inválido o ha expirado
        """
        payload = JWTHandler.decode_token(token)
        
        # Verificar tipo de token
        if payload.get("type") != token_type:
            logger.warning(f"Tipo de token incorrecto. Esperado: {token_type}, Recibido: {payload.get('type')}")
            raise ValueError(f"Token no es de tipo {token_type}")
        
        return payload
