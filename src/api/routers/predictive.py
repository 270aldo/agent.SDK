"""
API para los modelos predictivos del agente de ventas NGX.

Esta API expone los servicios de predicción de objeciones, necesidades,
conversión y el motor de decisiones para optimizar las conversaciones de ventas.
"""

from fastapi import APIRouter, HTTPException, Depends, Body
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
    responses={404: {"description": "No encontrado"}},
)

# Instanciar servicios
supabase_client = ResilientSupabaseClient()
predictive_model_service = PredictiveModelService(supabase_client)
nlp_integration_service = NLPIntegrationService()
entity_recognition_service = EntityRecognitionService()

objection_prediction_service = ObjectionPredictionService(
    supabase_client,
    predictive_model_service,
    nlp_integration_service
)

needs_prediction_service = NeedsPredictionService(
    supabase_client,
    predictive_model_service,
    nlp_integration_service,
    entity_recognition_service
)

conversion_prediction_service = ConversionPredictionService(
    supabase_client,
    predictive_model_service,
    nlp_integration_service
)

decision_engine_service = DecisionEngineService(
    supabase_client,
    predictive_model_service,
    objection_prediction_service,
    needs_prediction_service,
    conversion_prediction_service
)

# Rutas para predicción de objeciones
@router.post("/objections/predict")
async def predict_objections(
    conversation_id: str,
    messages: List[Dict[str, Any]] = Body(...),
    customer_profile: Optional[Dict[str, Any]] = Body(None)
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
        prediction = await objection_prediction_service.predict_objections(
            conversation_id=conversation_id,
            messages=messages,
            customer_profile=customer_profile
        )
        
        return prediction
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al predecir objeciones: {str(e)}")

@router.post("/objections/record")
async def record_objection(
    conversation_id: str,
    objection_type: str = Body(...),
    objection_text: str = Body(...)
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
        result = await objection_prediction_service.record_actual_objection(
            conversation_id=conversation_id,
            objection_type=objection_type,
            objection_text=objection_text
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al registrar objeción: {str(e)}")

@router.get("/objections/statistics")
async def get_objection_statistics(time_period: Optional[int] = None) -> Dict[str, Any]:
    """
    Obtiene estadísticas sobre objeciones detectadas.
    
    Args:
        time_period: Período de tiempo en días (opcional)
        
    Returns:
        Dict: Estadísticas de objeciones
    """
    try:
        statistics = await objection_prediction_service.get_objection_statistics(time_period)
        return statistics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas: {str(e)}")

# Rutas para predicción de necesidades
@router.post("/needs/predict")
async def predict_needs(
    conversation_id: str,
    messages: List[Dict[str, Any]] = Body(...),
    customer_profile: Optional[Dict[str, Any]] = Body(None)
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
        prediction = await needs_prediction_service.predict_needs(
            conversation_id=conversation_id,
            messages=messages,
            customer_profile=customer_profile
        )
        
        return prediction
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al predecir necesidades: {str(e)}")

@router.post("/needs/record")
async def record_need(
    conversation_id: str,
    need_category: str = Body(...),
    need_description: str = Body(...)
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
        result = await needs_prediction_service.record_actual_need(
            conversation_id=conversation_id,
            need_category=need_category,
            need_description=need_description
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al registrar necesidad: {str(e)}")

@router.get("/needs/statistics")
async def get_needs_statistics(time_period: Optional[int] = None) -> Dict[str, Any]:
    """
    Obtiene estadísticas sobre necesidades detectadas.
    
    Args:
        time_period: Período de tiempo en días (opcional)
        
    Returns:
        Dict: Estadísticas de necesidades
    """
    try:
        statistics = await needs_prediction_service.get_needs_statistics(time_period)
        return statistics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas: {str(e)}")

# Rutas para predicción de conversión
@router.post("/conversion/predict")
async def predict_conversion(
    conversation_id: str,
    messages: List[Dict[str, Any]] = Body(...),
    customer_profile: Optional[Dict[str, Any]] = Body(None)
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
        prediction = await conversion_prediction_service.predict_conversion(
            conversation_id=conversation_id,
            messages=messages,
            customer_profile=customer_profile
        )
        
        return prediction
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al predecir conversión: {str(e)}")

@router.post("/conversion/record")
async def record_conversion(
    conversation_id: str,
    did_convert: bool = Body(...),
    conversion_details: Optional[Dict[str, Any]] = Body(None)
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
        result = await conversion_prediction_service.record_actual_conversion(
            conversation_id=conversation_id,
            did_convert=did_convert,
            conversion_details=conversion_details
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al registrar conversión: {str(e)}")

@router.get("/conversion/statistics")
async def get_conversion_statistics(time_period: Optional[int] = None) -> Dict[str, Any]:
    """
    Obtiene estadísticas sobre predicciones de conversión.
    
    Args:
        time_period: Período de tiempo en días (opcional)
        
    Returns:
        Dict: Estadísticas de conversión
    """
    try:
        statistics = await conversion_prediction_service.get_conversion_statistics(time_period)
        return statistics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas: {str(e)}")

# Rutas para motor de decisiones
@router.post("/decision/optimize")
async def optimize_conversation_flow(
    conversation_id: str,
    messages: List[Dict[str, Any]] = Body(...),
    customer_profile: Optional[Dict[str, Any]] = Body(None),
    current_objectives: Optional[Dict[str, float]] = Body(None)
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
        optimization = await decision_engine_service.optimize_conversation_flow(
            conversation_id=conversation_id,
            messages=messages,
            customer_profile=customer_profile,
            current_objectives=current_objectives
        )
        
        return optimization
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al optimizar flujo: {str(e)}")

@router.post("/decision/adapt")
async def adapt_strategy_realtime(
    conversation_id: str,
    messages: List[Dict[str, Any]] = Body(...),
    current_strategy: Dict[str, Any] = Body(...),
    feedback: Optional[Dict[str, Any]] = Body(None),
    customer_profile: Optional[Dict[str, Any]] = Body(None)
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
        adaptation = await decision_engine_service.adapt_strategy_realtime(
            conversation_id=conversation_id,
            messages=messages,
            current_strategy=current_strategy,
            feedback=feedback,
            customer_profile=customer_profile
        )
        
        return adaptation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al adaptar estrategia: {str(e)}")

@router.post("/decision/prioritize")
async def prioritize_objectives(
    conversation_id: str,
    messages: List[Dict[str, Any]] = Body(...),
    customer_profile: Optional[Dict[str, Any]] = Body(None)
) -> Dict[str, float]:
    """
    Prioriza objetivos de conversación basado en el contexto actual.
    
    Args:
        conversation_id: ID de la conversación
        messages: Lista de mensajes de la conversación
        customer_profile: Perfil del cliente (opcional)
        
    Returns:
        Dict: Objetivos priorizados con sus pesos
    """
    try:
        priorities = await decision_engine_service.prioritize_objectives(
            conversation_id=conversation_id,
            messages=messages,
            customer_profile=customer_profile
        )
        
        return priorities
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al priorizar objetivos: {str(e)}")

@router.post("/decision/evaluate")
async def evaluate_conversation_path(
    conversation_id: str,
    messages: List[Dict[str, Any]] = Body(...),
    path_actions: List[Dict[str, Any]] = Body(...),
    customer_profile: Optional[Dict[str, Any]] = Body(None)
) -> Dict[str, Any]:
    """
    Evalúa la efectividad de una ruta de conversación específica.
    
    Args:
        conversation_id: ID de la conversación
        messages: Lista de mensajes de la conversación
        path_actions: Acciones tomadas en la ruta a evaluar
        customer_profile: Perfil del cliente (opcional)
        
    Returns:
        Dict: Evaluación de la ruta con métricas de efectividad
    """
    try:
        evaluation = await decision_engine_service.evaluate_conversation_path(
            conversation_id=conversation_id,
            messages=messages,
            path_actions=path_actions,
            customer_profile=customer_profile
        )
        
        return evaluation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al evaluar ruta: {str(e)}")

@router.get("/decision/statistics")
async def get_decision_statistics(time_period: Optional[int] = None) -> Dict[str, Any]:
    """
    Obtiene estadísticas sobre decisiones tomadas por el motor.
    
    Args:
        time_period: Período de tiempo en días (opcional)
        
    Returns:
        Dict: Estadísticas de decisiones
    """
    try:
        statistics = await decision_engine_service.get_decision_statistics(time_period)
        return statistics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas: {str(e)}")

# Rutas para gestión de modelos predictivos
@router.get("/models")
async def list_models(model_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Lista todos los modelos predictivos registrados.
    
    Args:
        model_type: Tipo de modelo para filtrar (opcional)
        
    Returns:
        List: Lista de modelos predictivos
    """
    try:
        models = await predictive_model_service.list_models(model_type)
        return models
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar modelos: {str(e)}")

@router.get("/models/{model_name}")
async def get_model(model_name: str) -> Dict[str, Any]:
    """
    Obtiene información de un modelo predictivo.
    
    Args:
        model_name: Nombre del modelo a obtener
        
    Returns:
        Dict: Información del modelo
    """
    try:
        model = await predictive_model_service.get_model(model_name)
        
        if not model:
            raise HTTPException(status_code=404, detail=f"Modelo '{model_name}' no encontrado")
        
        return model
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener modelo: {str(e)}")

@router.put("/models/{model_name}")
async def update_model(
    model_name: str,
    model_params: Optional[Dict[str, Any]] = Body(None),
    status: Optional[str] = Body(None),
    accuracy: Optional[float] = Body(None)
) -> Dict[str, Any]:
    """
    Actualiza un modelo predictivo existente.
    
    Args:
        model_name: Nombre del modelo a actualizar
        model_params: Nuevos parámetros del modelo (opcional)
        status: Nuevo estado del modelo (opcional)
        accuracy: Nueva precisión del modelo (opcional)
        
    Returns:
        Dict: Información actualizada del modelo
    """
    try:
        model = await predictive_model_service.get_model(model_name)
        
        if not model:
            raise HTTPException(status_code=404, detail=f"Modelo '{model_name}' no encontrado")
        
        updated_model = await predictive_model_service.update_model(
            model_name=model_name,
            model_params=model_params,
            status=status,
            accuracy=accuracy
        )
        
        return updated_model
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar modelo: {str(e)}")
