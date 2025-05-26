"""
API para el entrenamiento automático de modelos predictivos.

Esta API expone los servicios de entrenamiento automático para los modelos
predictivos del agente de ventas NGX, permitiendo programar entrenamientos,
verificar su estado y obtener métricas de rendimiento.
"""

from fastapi import APIRouter, Body, Query, Depends
from fastapi.responses import JSONResponse
from typing import Dict, List, Any, Optional

from src.auth.auth_dependencies import get_current_user, get_current_active_user, has_required_permissions, has_admin_role
from src.auth.auth_utils import TokenData

from src.integrations.supabase.resilient_client import ResilientSupabaseClient
from src.services.predictive_model_service import PredictiveModelService
from src.services.model_training_service import ModelTrainingService

# Crear router
router = APIRouter(
    prefix="/training",
    tags=["model_training"],
    responses={
        404: {
            "model": dict,
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "data": None,
                        "error": {
                            "code": "RESOURCE_NOT_FOUND",
                            "message": "El recurso solicitado no existe"
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
predictive_model_service = PredictiveModelService(supabase_client)
model_training_service = ModelTrainingService(supabase_client, predictive_model_service)

@router.post("/schedule")
async def schedule_model_training(
    model_name: str,
    force_training: bool = False,
    training_config: Optional[Dict[str, Any]] = Body(None),
    current_user: TokenData = Depends(has_required_permissions(["write:models", "write:training"]))
) -> Dict[str, Any]:
    """
    Programa el entrenamiento de un modelo predictivo.
    
    Args:
        model_name: Nombre del modelo a entrenar
        force_training: Si es True, fuerza el entrenamiento aunque no se cumplan los criterios
        training_config: Configuración específica para el entrenamiento (opcional)
        
    Returns:
        Dict: Resultado de la programación del entrenamiento
    """
    try:
        result = await model_training_service.schedule_training(
            model_name=model_name,
            force_training=force_training,
            training_config=training_config
        )
        
        if not result.get("success", False):
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "data": None,
                    "error": {
                        "code": "TRAINING_ERROR",
                        "message": result.get("message", "Error al programar entrenamiento")
                    }
                }
            )
        
        return {
            "success": True,
            "data": result,
            "error": None
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "data": None,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": f"Error al programar entrenamiento: {str(e)}"
                }
            }
        )

@router.get("/status/{training_id}")
async def get_training_status(
    training_id: str,
    current_user: TokenData = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Obtiene el estado actual de un entrenamiento.
    
    Args:
        training_id: ID del entrenamiento
        
    Returns:
        Dict: Estado del entrenamiento
    """
    try:
        result = await model_training_service.get_training_status(training_id)
        
        if not result.get("success", False):
            return JSONResponse(
                status_code=404 if "no encontrado" in result.get("message", "") else 500,
                content={
                    "success": False,
                    "data": None,
                    "error": {
                        "code": "RESOURCE_NOT_FOUND" if "no encontrado" in result.get("message", "") else "INTERNAL_SERVER_ERROR",
                        "message": result.get("message", "Error al obtener estado del entrenamiento")
                    }
                }
            )
        
        return {
            "success": True,
            "data": result,
            "error": None
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "data": None,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": f"Error al obtener estado del entrenamiento: {str(e)}"
                }
            }
        )

@router.get("/list")
async def list_model_trainings(
    model_name: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(10, ge=1, le=100),
    current_user: TokenData = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Lista los entrenamientos de modelos con filtros opcionales.
    
    Args:
        model_name: Filtrar por nombre de modelo (opcional)
        status: Filtrar por estado (opcional)
        limit: Número máximo de registros a devolver (1-100)
        
    Returns:
        Dict: Lista de entrenamientos
    """
    try:
        result = await model_training_service.list_model_trainings(
            model_name=model_name,
            status=status,
            limit=limit
        )
        
        if not result.get("success", False):
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "data": None,
                    "error": {
                        "code": "INTERNAL_SERVER_ERROR",
                        "message": result.get("message", "Error al listar entrenamientos")
                    }
                }
            )
        
        return {
            "success": True,
            "data": result,
            "error": None
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "data": None,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": f"Error al listar entrenamientos: {str(e)}"
                }
            }
        )

@router.get("/criteria/{model_name}")
async def check_training_criteria(
    model_name: str,
    current_user: TokenData = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Verifica si un modelo cumple con los criterios para ser reentrenado.
    
    Args:
        model_name: Nombre del modelo a verificar
        
    Returns:
        Dict: Resultado de la verificación
    """
    try:
        should_train, reason = await model_training_service._should_train_model(model_name)
        
        return {
            "success": True,
            "data": {
                "model_name": model_name,
                "should_train": should_train,
                "reason": reason
            },
            "error": None
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "data": None,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": f"Error al verificar criterios de entrenamiento: {str(e)}"
                }
            }
        )

@router.post("/auto-schedule")
async def auto_schedule_trainings(
    current_user: TokenData = Depends(has_admin_role)
) -> Dict[str, Any]:
    """
    Programa automáticamente el entrenamiento de todos los modelos que cumplan con los criterios.
    
    Returns:
        Dict: Resultado de la programación automática
    """
    try:
        # Obtener todos los modelos
        models_result = await predictive_model_service.list_models()
        
        if isinstance(models_result, dict) and not models_result.get("success", False):
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "data": None,
                    "error": {
                        "code": "INTERNAL_SERVER_ERROR",
                        "message": "Error al obtener lista de modelos"
                    }
                }
            )
        
        models = models_result if isinstance(models_result, list) else models_result.get("data", [])
        
        # Verificar criterios y programar entrenamiento para cada modelo
        scheduled_trainings = []
        skipped_models = []
        
        for model in models:
            model_name = model.get("name")
            should_train, reason = await model_training_service._should_train_model(model_name)
            
            if should_train:
                # Programar entrenamiento
                result = await model_training_service.schedule_training(
                    model_name=model_name,
                    force_training=False
                )
                
                if result.get("success", False):
                    scheduled_trainings.append({
                        "model_name": model_name,
                        "training_id": result.get("training_id"),
                        "reason": reason
                    })
                else:
                    skipped_models.append({
                        "model_name": model_name,
                        "reason": result.get("message", "Error desconocido")
                    })
            else:
                skipped_models.append({
                    "model_name": model_name,
                    "reason": reason
                })
        
        return {
            "success": True,
            "data": {
                "scheduled_trainings": scheduled_trainings,
                "skipped_models": skipped_models,
                "total_scheduled": len(scheduled_trainings),
                "total_skipped": len(skipped_models)
            },
            "error": None
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "data": None,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": f"Error al programar entrenamientos automáticos: {str(e)}"
                }
            }
        )
