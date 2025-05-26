"""
API para el panel de análisis de conversaciones.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
from datetime import datetime

from src.services.conversation_analytics_service import ConversationAnalyticsService

# Crear router
router = APIRouter(
    prefix="/analytics",
    tags=["analytics"],
    responses={404: {"description": "No encontrado"}},
)

# Instanciar servicio
analytics_service = ConversationAnalyticsService()

@router.get("/conversation/{conversation_id}")
async def get_conversation_analytics(conversation_id: str) -> Dict[str, Any]:
    """
    Obtiene análisis detallado para una conversación específica.
    
    Args:
        conversation_id: ID de la conversación
        
    Returns:
        Dict: Análisis detallado de la conversación
    """
    try:
        analytics = await analytics_service.get_conversation_analytics(conversation_id)
        
        if not analytics.get("has_analytics", False):
            raise HTTPException(status_code=404, detail=analytics.get("message", "Análisis no encontrado"))
        
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener análisis: {str(e)}")

@router.get("/aggregate")
async def get_aggregate_analytics(days: int = 7) -> Dict[str, Any]:
    """
    Obtiene análisis agregado de todas las conversaciones en un período de tiempo.
    
    Args:
        days: Número de días para el análisis
        
    Returns:
        Dict: Análisis agregado de conversaciones
    """
    try:
        analytics = await analytics_service.get_aggregate_analytics(days=days)
        
        if not analytics.get("has_analytics", False):
            raise HTTPException(status_code=404, detail=analytics.get("message", "Análisis no encontrado"))
        
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener análisis agregado: {str(e)}")

@router.get("/trends")
async def get_sentiment_trend_analysis(days: int = 30) -> Dict[str, Any]:
    """
    Obtiene análisis de tendencias de sentimiento a lo largo del tiempo.
    
    Args:
        days: Número de días para el análisis
        
    Returns:
        Dict: Análisis de tendencias de sentimiento
    """
    try:
        analytics = await analytics_service.get_sentiment_trend_analysis(days=days)
        
        if not analytics.get("has_analytics", False):
            raise HTTPException(status_code=404, detail=analytics.get("message", "Análisis no encontrado"))
        
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener análisis de tendencias: {str(e)}")

@router.delete("/cache/{conversation_id}")
async def clear_analytics_cache(conversation_id: str) -> Dict[str, Any]:
    """
    Limpia la caché de análisis para una conversación específica.
    
    Args:
        conversation_id: ID de la conversación
        
    Returns:
        Dict: Mensaje de confirmación
    """
    try:
        analytics_service.clear_analytics_cache(conversation_id)
        return {"message": f"Caché limpiada para conversación {conversation_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al limpiar caché: {str(e)}")

@router.delete("/cache")
async def clear_all_analytics_cache() -> Dict[str, Any]:
    """
    Limpia toda la caché de análisis.
    
    Returns:
        Dict: Mensaje de confirmación
    """
    try:
        analytics_service.clear_analytics_cache()
        return {"message": "Toda la caché de análisis ha sido limpiada"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al limpiar caché: {str(e)}")
