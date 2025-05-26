"""
API para la autenticación de usuarios.

Esta API expone los endpoints necesarios para la autenticación de usuarios,
incluyendo inicio de sesión, registro y actualización de tokens.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging
import json

from src.auth.jwt_handler import JWTHandler
from src.auth.auth_utils import Token, UserCredentials, RefreshTokenRequest
from src.auth.auth_dependencies import get_current_user, has_admin_role
from src.integrations.supabase.resilient_client import ResilientSupabaseClient

# Configurar logging
logger = logging.getLogger(__name__)

# Crear router
router = APIRouter(
    prefix="/auth",
    tags=["autenticación"],
    responses={
        401: {
            "model": dict,
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "data": None,
                        "error": {
                            "code": "UNAUTHORIZED",
                            "message": "Credenciales inválidas"
                        }
                    }
                }
            }
        },
        403: {
            "model": dict,
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "data": None,
                        "error": {
                            "code": "FORBIDDEN",
                            "message": "No tienes permisos suficientes"
                        }
                    }
                }
            }
        },
        500: {
            "model": dict,
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "data": None,
                        "error": {
                            "code": "INTERNAL_SERVER_ERROR",
                            "message": "Error interno del servidor"
                        }
                    }
                }
            }
        }
    },
)

# Instanciar servicios
supabase_client = ResilientSupabaseClient()

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Dict[str, Any]:
    """
    Autentica a un usuario y genera tokens JWT.
    
    Args:
        form_data: Formulario con username y password
        
    Returns:
        Dict: Tokens de acceso y actualización
    """
    try:
        # Autenticar usuario en Supabase
        result = await supabase_client.auth.sign_in_with_password({
            "email": form_data.username,
            "password": form_data.password
        })
        
        if result.get("error"):
            logger.warning(f"Error de autenticación: {result.get('error')}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "success": False,
                    "data": None,
                    "error": {
                        "code": "UNAUTHORIZED",
                        "message": "Credenciales inválidas"
                    }
                }
            )
        
        # Obtener datos del usuario
        user_data = result.get("data", {}).get("user", {})
        
        if not user_data:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "success": False,
                    "data": None,
                    "error": {
                        "code": "UNAUTHORIZED",
                        "message": "Credenciales inválidas"
                    }
                }
            )
        
        # Obtener rol y permisos del usuario
        user_metadata = user_data.get("user_metadata", {})
        role = user_metadata.get("role", "user")
        permissions = user_metadata.get("permissions", [])
        
        # Generar tokens JWT
        token_data = {
            "sub": user_data.get("id"),
            "username": user_data.get("email"),
            "role": role,
            "permissions": permissions
        }
        
        access_token = JWTHandler.create_access_token(token_data)
        refresh_token = JWTHandler.create_refresh_token(token_data)
        
        # Calcular tiempo de expiración
        expires_in = 30 * 60  # 30 minutos en segundos
        
        return {
            "success": True,
            "data": {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": expires_in,
                "user": {
                    "id": user_data.get("id"),
                    "email": user_data.get("email"),
                    "role": role,
                    "permissions": permissions
                }
            },
            "error": None
        }
    except Exception as e:
        logger.error(f"Error en login: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "data": None,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": f"Error al procesar la solicitud: {str(e)}"
                }
            }
        )

@router.post("/register")
async def register(user_data: UserCredentials) -> Dict[str, Any]:
    """
    Registra un nuevo usuario.
    
    Args:
        user_data: Datos del nuevo usuario
        
    Returns:
        Dict: Resultado del registro
    """
    try:
        # Registrar usuario en Supabase
        result = await supabase_client.auth.sign_up({
            "email": user_data.username,
            "password": user_data.password,
            "options": {
                "data": {
                    "role": "user",
                    "permissions": ["read:own_data"]
                }
            }
        })
        
        if result.get("error"):
            logger.warning(f"Error de registro: {result.get('error')}")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "success": False,
                    "data": None,
                    "error": {
                        "code": "REGISTRATION_ERROR",
                        "message": result.get("error", {}).get("message", "Error al registrar usuario")
                    }
                }
            )
        
        # Obtener datos del usuario registrado
        user_data = result.get("data", {}).get("user", {})
        
        return {
            "success": True,
            "data": {
                "id": user_data.get("id"),
                "email": user_data.get("email"),
                "message": "Usuario registrado correctamente. Por favor, verifica tu correo electrónico."
            },
            "error": None
        }
    except Exception as e:
        logger.error(f"Error en registro: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "data": None,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": f"Error al procesar la solicitud: {str(e)}"
                }
            }
        )

@router.post("/refresh")
async def refresh_token(refresh_request: RefreshTokenRequest) -> Dict[str, Any]:
    """
    Actualiza un token de acceso utilizando un token de actualización.
    
    Args:
        refresh_request: Solicitud con el token de actualización
        
    Returns:
        Dict: Nuevo token de acceso
    """
    try:
        # Verificar token de actualización
        payload = JWTHandler.verify_token(refresh_request.refresh_token, token_type="refresh")
        
        # Generar nuevo token de acceso
        token_data = {
            "sub": payload.get("sub"),
            "username": payload.get("username"),
            "role": payload.get("role"),
            "permissions": payload.get("permissions")
        }
        
        access_token = JWTHandler.create_access_token(token_data)
        
        # Calcular tiempo de expiración
        expires_in = 30 * 60  # 30 minutos en segundos
        
        return {
            "success": True,
            "data": {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": expires_in
            },
            "error": None
        }
    except Exception as e:
        logger.error(f"Error en refresh_token: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "success": False,
                "data": None,
                "error": {
                    "code": "INVALID_REFRESH_TOKEN",
                    "message": "Token de actualización inválido o expirado"
                }
            }
        )

@router.get("/me")
async def get_user_info(current_user = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Obtiene información del usuario autenticado.
    
    Args:
        current_user: Usuario actual (obtenido del token)
        
    Returns:
        Dict: Información del usuario
    """
    try:
        return {
            "success": True,
            "data": {
                "id": current_user.user_id,
                "username": current_user.username,
                "role": current_user.role,
                "permissions": current_user.permissions
            },
            "error": None
        }
    except Exception as e:
        logger.error(f"Error en get_user_info: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "data": None,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": f"Error al procesar la solicitud: {str(e)}"
                }
            }
        )
