"""
Módulo para la gestión de tokens JWT.

Este módulo proporciona funciones para generar, validar y gestionar
tokens JWT utilizados para la autenticación y autorización en la API.
"""

import jwt
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import os
import logging
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

logger = logging.getLogger(__name__)

# Configuración de JWT
JWT_SECRET = os.getenv("JWT_SECRET", "default_secret_key_change_in_production")
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
            "type": "access"
        })
        
        # Generar token
        try:
            encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
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
            "type": "refresh"
        })
        
        # Generar token
        try:
            encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
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
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
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
