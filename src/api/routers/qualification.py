"""
Endpoints para el sistema de cualificación de leads.
"""

import logging
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional

from src.models.qualification import UserMetrics, QualificationResult, VoiceAgentSession
from src.services.qualification_service import LeadQualificationService

# Configurar logging
logger = logging.getLogger(__name__)

# Crear router
router = APIRouter(
    prefix="/qualification",
    tags=["qualification"],
    responses={404: {"description": "No encontrado"}},
)

# Dependencia para obtener el servicio de cualificación
async def get_qualification_service():
    return LeadQualificationService()

@router.post("/score", response_model=QualificationResult)
async def calculate_qualification_score(
    metrics: UserMetrics,
    service: LeadQualificationService = Depends(get_qualification_service)
):
    """
    Calcula el score de cualificación para un usuario y determina si califica para el agente de voz.
    
    Args:
        metrics: Métricas del usuario para calcular el score
        
    Returns:
        QualificationResult: Resultado de cualificación con score y elegibilidad
    """
    try:
        result = await service.is_qualified_for_voice(metrics.user_id, metrics.model_dump())
        return result
    except Exception as e:
        logger.error(f"Error al calcular score de cualificación: {e}")
        raise HTTPException(status_code=500, detail=f"Error al calcular score: {str(e)}")

@router.post("/sessions", response_model=VoiceAgentSession)
async def create_voice_agent_session(
    user_id: str,
    conversation_id: str,
    service: LeadQualificationService = Depends(get_qualification_service)
):
    """
    Registra una nueva sesión del agente de voz.
    
    Args:
        user_id: ID del usuario
        conversation_id: ID de la conversación
        
    Returns:
        VoiceAgentSession: Datos de la sesión creada
    """
    try:
        session = await service.register_voice_agent_session(user_id, conversation_id)
        return session
    except Exception as e:
        logger.error(f"Error al crear sesión de agente de voz: {e}")
        raise HTTPException(status_code=500, detail=f"Error al crear sesión: {str(e)}")

@router.put("/sessions/{session_id}/status")
async def update_session_status(
    session_id: str,
    status: str,
    end_reason: Optional[str] = None,
    service: LeadQualificationService = Depends(get_qualification_service)
):
    """
    Actualiza el estado de una sesión del agente de voz.
    
    Args:
        session_id: ID de la sesión
        status: Nuevo estado ('active', 'completed', 'timeout', 'abandoned')
        end_reason: Razón de finalización (opcional)
        
    Returns:
        Dict: Mensaje de confirmación
    """
    try:
        # Validar estado
        valid_statuses = ['active', 'completed', 'timeout', 'abandoned']
        if status not in valid_statuses:
            raise HTTPException(
                status_code=400, 
                detail=f"Estado inválido. Debe ser uno de: {', '.join(valid_statuses)}"
            )
            
        await service.update_session_status(session_id, status, end_reason)
        return {"message": f"Estado de sesión actualizado a '{status}'"}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error al actualizar estado de sesión: {e}")
        raise HTTPException(status_code=500, detail=f"Error al actualizar estado: {str(e)}")
