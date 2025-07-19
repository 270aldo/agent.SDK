"""
API para los modelos predictivos del agente de ventas NGX.

Esta API expone los servicios de predicción de objeciones, necesidades,
conversión y el motor de decisiones para optimizar las conversaciones de ventas.
"""

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Dict, List, Any, Optional

from src.api.models.predictive_models import (
    ObjectionPredictionRequest, ObjectionRecord,
    NeedsPredictionRequest, NeedRecord,
    ConversionPredictionRequest, ConversionRecord,
    OptimizeFlowRequest, AdaptStrategyRequest, EvaluatePathRequest,
    FeedbackRequest, ModelUpdate
)
from src.auth.auth_dependencies import get_current_user, get_current_active_user, has_required_permissions
from src.auth.auth_utils import TokenData
from typing import Dict, List, Any, Optional
from datetime import datetime

from src.integrations.supabase.resilient_client import ResilientSupabaseClient
from src.services.predictive_model_service import PredictiveModelService
from src.services.objection_prediction_service import ObjectionPredictionService
from src.services.needs_prediction_service import NeedsPredictionService
from src.services.conversion_prediction_service import ConversionPredictionService
from src.services.decision_engine_service import DecisionEngineService
from src.services.nlp_integration_service import NLPIntegrationService
from src.services.entity_recognition_service import EntityRecognitionService

# Crear router
router = APIRouter(
    prefix="/predictive",
    tags=["predictive"],
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

# Variables globales para servicios (lazy initialization)
_services_initialized = False
supabase_client = None
predictive_model_service = None
nlp_integration_service = None
entity_recognition_service = None
objection_prediction_service = None
needs_prediction_service = None
conversion_prediction_service = None
decision_engine_service = None

async def get_services():
    """
    Obtiene o inicializa los servicios de forma lazy.
    """
    global _services_initialized, supabase_client, predictive_model_service
    global nlp_integration_service, entity_recognition_service
    global objection_prediction_service, needs_prediction_service
    global conversion_prediction_service, decision_engine_service
    
    if not _services_initialized:
        # Instanciar servicios base
        supabase_client = ResilientSupabaseClient()
        predictive_model_service = PredictiveModelService(supabase_client)
        nlp_integration_service = NLPIntegrationService()
        entity_recognition_service = EntityRecognitionService()
        
        # Instanciar servicios predictivos
        objection_prediction_service = ObjectionPredictionService(
            supabase_client,
            predictive_model_service,
            nlp_integration_service
        )
        await objection_prediction_service.initialize()
        
        needs_prediction_service = NeedsPredictionService(
            supabase_client,
            predictive_model_service,
            nlp_integration_service,
            entity_recognition_service
        )
        await needs_prediction_service.initialize()
        
        conversion_prediction_service = ConversionPredictionService(
            supabase_client,
            predictive_model_service,
            nlp_integration_service
        )
        await conversion_prediction_service.initialize()
        
        decision_engine_service = DecisionEngineService(
            supabase_client,
            predictive_model_service,
            nlp_integration_service,
            objection_prediction_service,
            needs_prediction_service,
            conversion_prediction_service
        )
        await decision_engine_service.initialize()
        
        _services_initialized = True
    
    return {
        "objection": objection_prediction_service,
        "needs": needs_prediction_service,
        "conversion": conversion_prediction_service,
        "decision": decision_engine_service
    }

# Rutas para predicción de objeciones
@router.post("/objection/predict")
async def predict_objections(
    request: ObjectionPredictionRequest,
    current_user: TokenData = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Predice posibles objeciones basadas en la conversación actual.
    
    Args:
        conversation_id: ID de la conversación
        messages: Lista de mensajes de la conversación
        customer_profile: Perfil del cliente (opcional)
        
    Returns:
        Dict: Predicciones de objeciones con niveles de confianza
    """
    try:
        services = await get_services()
        prediction = await services["objection"].predict_objections(
            conversation_id=request.conversation_id,
            messages=[message.model_dump() for message in request.messages],
            customer_profile=request.customer_profile.model_dump() if request.customer_profile else None
        )
        
        return {
            "success": True,
            "data": prediction,
            "error": None
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "data": None,
                "error": {
                    "code": "MODEL_ERROR",
                    "message": f"Error al predecir objeciones: {str(e)}"
                }
            }
        )

@router.post("/objection/record")
async def record_objection(
    objection: ObjectionRecord,
    current_user: TokenData = Depends(has_required_permissions(["write:objections"]))
) -> Dict[str, Any]:
    """
    Registra una objeción real para mejorar el modelo.
    
    Args:
        conversation_id: ID de la conversación
        objection_type: Tipo de objeción detectada
        objection_text: Texto de la objeción
        
    Returns:
        Dict: Resultado del registro
    """
    try:
        services = await get_services()
        result = await services["objection"].record_objection(
            conversation_id=objection.conversation_id,
            objection_type=objection.objection_type,
            objection_text=objection.objection_text
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
                    "code": "MODEL_ERROR",
                    "message": f"Error al registrar objeción: {str(e)}"
                }
            }
        )

# Rutas para predicción de necesidades
@router.post("/needs/predict")
async def predict_needs(
    request: NeedsPredictionRequest,
    current_user: TokenData = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Predice las necesidades del cliente basándose en la conversación actual.
    
    Args:
        conversation_id: ID de la conversación
        messages: Lista de mensajes de la conversación
        customer_profile: Perfil del cliente (opcional)
        
    Returns:
        Dict: Predicciones de necesidades con niveles de confianza
    """
    try:
        services = await get_services()
        prediction = await services["needs"].predict_needs(
            conversation_id=request.conversation_id,
            messages=[message.model_dump() for message in request.messages],
            customer_profile=request.customer_profile.model_dump() if request.customer_profile else None
        )
        
        return {
            "success": True,
            "data": prediction,
            "error": None
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "data": None,
                "error": {
                    "code": "MODEL_ERROR",
                    "message": f"Error al predecir necesidades: {str(e)}"
                }
            }
        )

@router.post("/needs/record")
async def record_need(
    need: NeedRecord,
    current_user: TokenData = Depends(has_required_permissions(["write:needs"]))
) -> Dict[str, Any]:
    """
    Registra una necesidad real para mejorar el modelo.
    
    Args:
        conversation_id: ID de la conversación
        need_category: Categoría de necesidad detectada
        need_description: Descripción de la necesidad
        
    Returns:
        Dict: Resultado del registro
    """
    try:
        services = await get_services()
        result = await services["needs"].record_need(
            conversation_id=need.conversation_id,
            need_category=need.need_category,
            need_description=need.need_description
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
                    "code": "MODEL_ERROR",
                    "message": f"Error al registrar necesidad: {str(e)}"
                }
            }
        )

# Rutas para predicción de conversión
@router.post("/conversion/predict")
async def predict_conversion(
    request: ConversionPredictionRequest,
    current_user: TokenData = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Predice la probabilidad de conversión basada en la conversación actual.
    
    Args:
        conversation_id: ID de la conversación
        messages: Lista de mensajes de la conversación
        customer_profile: Perfil del cliente (opcional)
        
    Returns:
        Dict: Predicción de probabilidad de conversión con recomendaciones
    """
    try:
        services = await get_services()
        prediction = await services["conversion"].predict_conversion(
            conversation_id=request.conversation_id,
            messages=[message.model_dump() for message in request.messages],
            customer_profile=request.customer_profile.model_dump() if request.customer_profile else None,
            product_id=request.product_id
        )
        
        return {
            "success": True,
            "data": prediction,
            "error": None
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "data": None,
                "error": {
                    "code": "MODEL_ERROR",
                    "message": f"Error al predecir conversión: {str(e)}"
                }
            }
        )

@router.post("/conversion/record")
async def record_conversion(
    conversion: ConversionRecord,
    current_user: TokenData = Depends(has_required_permissions(["write:conversions"]))
) -> Dict[str, Any]:
    """
    Registra el resultado real de conversión para mejorar el modelo.
    
    Args:
        conversation_id: ID de la conversación
        did_convert: Indica si el cliente realmente se convirtió
        conversion_details: Detalles adicionales de la conversión (opcional)
        
    Returns:
        Dict: Resultado del registro
    """
    try:
        services = await get_services()
        result = await services["conversion"].record_conversion(
            conversation_id=conversion.conversation_id,
            did_convert=conversion.did_convert,
            conversion_details=conversion.conversion_details
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
                    "code": "MODEL_ERROR",
                    "message": f"Error al registrar conversión: {str(e)}"
                }
            }
        )

# Rutas para motor de decisiones
@router.post("/decision/optimize-flow")
async def optimize_conversation_flow(
    request: OptimizeFlowRequest,
    current_user: TokenData = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Optimiza el flujo de conversación basado en predicciones y objetivos.
    
    Args:
        conversation_id: ID de la conversación
        messages: Lista de mensajes de la conversación
        customer_profile: Perfil del cliente (opcional)
        current_objectives: Objetivos actuales con pesos (opcional)
        
    Returns:
        Dict: Recomendaciones de flujo optimizado
    """
    try:
        services = await get_services()
        optimized_flow = await services["decision"].optimize_conversation_flow(
            conversation_id=request.conversation_id,
            messages=[message.model_dump() for message in request.messages],
            customer_profile=request.customer_profile.model_dump() if request.customer_profile else None,
            current_objectives=request.current_objectives
        )
        
        return {
            "success": True,
            "data": optimized_flow,
            "error": None
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "data": None,
                "error": {
                    "code": "MODEL_ERROR",
                    "message": f"Error al optimizar flujo: {str(e)}"
                }
            }
        )

@router.post("/decision/adapt-strategy")
async def adapt_strategy(
    request: AdaptStrategyRequest,
    current_user: TokenData = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Adapta la estrategia de conversación en tiempo real.
    
    Args:
        conversation_id: ID de la conversación
        messages: Lista de mensajes de la conversación
        current_strategy: Estrategia actual (árbol de decisión y acciones)
        feedback: Feedback sobre acciones previas (opcional)
        customer_profile: Perfil del cliente (opcional)
        
    Returns:
        Dict: Estrategia adaptada con nuevas acciones recomendadas
    """
    try:
        services = await get_services()
        adapted_strategy = await services["decision"].adapt_strategy(
            conversation_id=request.conversation_id,
            messages=[message.model_dump() for message in request.messages],
            current_strategy=request.current_strategy,
            feedback=request.feedback,
            customer_profile=request.customer_profile.model_dump() if request.customer_profile else None
        )
        
        return {
            "success": True,
            "data": adapted_strategy,
            "error": None
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "data": None,
                "error": {
                    "code": "MODEL_ERROR",
                    "message": f"Error al adaptar estrategia: {str(e)}"
                }
            }
        )

# Rutas para retroalimentación de modelos
@router.post("/feedback")
async def submit_feedback(
    feedback: FeedbackRequest,
    current_user: TokenData = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Registra retroalimentación sobre una predicción para mejorar el modelo.
    
    Args:
        conversation_id: ID de la conversación
        model_type: Tipo de modelo (objection, needs, conversion, decision_engine)
        prediction_id: ID de la predicción
        feedback_rating: Valoración de 0 a 1 sobre la precisión
        feedback_details: Detalles adicionales sobre la retroalimentación
        
    Returns:
        Dict: Resultado del registro de retroalimentación
    """
    try:
        # Seleccionar el servicio adecuado según el tipo de modelo
        service = None
        if feedback.model_type == "objection":
            service = objection_prediction_service
        elif feedback.model_type == "needs":
            service = needs_prediction_service
        elif feedback.model_type == "conversion":
            service = conversion_prediction_service
        elif feedback.model_type == "decision_engine":
            service = decision_engine_service
        else:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "data": None,
                    "error": {
                        "code": "INVALID_REQUEST",
                        "message": f"Tipo de modelo '{feedback.model_type}' no válido"
                    }
                }
            )
        
        # Registrar retroalimentación
        result = await service.log_feedback(
            conversation_id=feedback.conversation_id,
            prediction_id=feedback.prediction_id,
            feedback_rating=feedback.feedback_rating,
            feedback_details=feedback.feedback_details
        )
        
        # Actualizar métricas del modelo
        await service._update_feedback_metrics(feedback.feedback_rating, feedback.feedback_details)
        
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
                    "code": "MODEL_ERROR",
                    "message": f"Error al registrar retroalimentación: {str(e)}"
                }
            }
        )

# Rutas para gestión de modelos predictivos
@router.get("/models")
async def list_models(
    model_type: Optional[str] = None,
    current_user: TokenData = Depends(get_current_active_user)
) -> List[Dict[str, Any]]:
    """
    Lista todos los modelos predictivos registrados.
    
    Args:
        model_type: Tipo de modelo para filtrar (opcional)
        
    Returns:
        List: Lista de modelos predictivos
    """
    try:
        models = await predictive_model_service.list_models(model_type)
        return {
            "success": True,
            "data": models,
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
                    "message": f"Error al listar modelos: {str(e)}"
                }
            }
        )

@router.get("/models/{model_id}")
async def get_model(
    model_id: str,
    current_user: TokenData = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Obtiene información de un modelo predictivo.
    
    Args:
        model_id: ID del modelo a obtener
        
    Returns:
        Dict: Información del modelo
    """
    try:
        model = await predictive_model_service.get_model(model_id)
        
        if not model:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "data": None,
                    "error": {
                        "code": "RESOURCE_NOT_FOUND",
                        "message": f"Modelo '{model_id}' no encontrado"
                    }
                }
            )
        
        return {
            "success": True,
            "data": model,
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
                    "message": f"Error al obtener modelo: {str(e)}"
                }
            }
        )

@router.put("/models/{model_id}")
async def update_model(
    model_id: str,
    model_update: ModelUpdate,
    current_user: TokenData = Depends(has_required_permissions(["write:models"]))
) -> Dict[str, Any]:
    """
    Actualiza un modelo predictivo existente.
    
    Args:
        model_id: ID del modelo a actualizar
        model_params: Nuevos parámetros del modelo (opcional)
        status: Nuevo estado del modelo (opcional)
        accuracy: Nueva precisión del modelo (opcional)
        
    Returns:
        Dict: Información actualizada del modelo
    """
    try:
        model = await predictive_model_service.get_model(model_id)
        
        if not model:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "data": None,
                    "error": {
                        "code": "RESOURCE_NOT_FOUND",
                        "message": f"Modelo '{model_id}' no encontrado"
                    }
                }
            )
        
        updated_model = await predictive_model_service.update_model(
            model_id=model_id,
            model_params=model_update.model_params,
            status=model_update.status,
            accuracy=model_update.accuracy
        )
        
        return {
            "success": True,
            "data": updated_model,
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
                    "message": f"Error al actualizar modelo: {str(e)}"
                }
            }
        )
