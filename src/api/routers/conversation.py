import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Response, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import uuid
from datetime import datetime

from src.models.conversation import CustomerData, ConversationState
from src.services.conversation_service import ConversationService

# Configurar logging
logger = logging.getLogger(__name__)

# Crear router
router = APIRouter(prefix="/conversations", tags=["conversations"])

# Instancia del servicio (singleton)
conversation_service = ConversationService()

# Modelos para la API
class StartConversationRequest(BaseModel):
    """Modelo para solicitar iniciar una conversación."""
    customer_data: CustomerData
    program_type: str = "PRIME"

class MessageRequest(BaseModel):
    """Modelo para enviar un mensaje."""
    message: str = Field(..., description="Mensaje del cliente")

class ConversationResponse(BaseModel):
    """Modelo para respuestas relacionadas con una conversación."""
    conversation_id: str
    status: str
    phase: str
    message: Optional[str] = None

@router.post("/start", response_model=ConversationResponse)
async def start_conversation(request: StartConversationRequest):
    """
    Iniciar una nueva conversación.
    """
    try:
        # Iniciar conversación
        state = await conversation_service.start_conversation(
            customer_data=request.customer_data,
            program_type=request.program_type
        )
        
        # Obtener el último mensaje (saludo inicial)
        last_message = state.messages[-1].content if state.messages else None
        
        return ConversationResponse(
            conversation_id=state.conversation_id,
            status="active",
            phase=state.phase,
            message=last_message
        )
    except Exception as e:
        logger.error(f"Error al iniciar conversación: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{conversation_id}/message", response_model=ConversationResponse)
async def send_message(conversation_id: str, request: MessageRequest):
    """
    Enviar un mensaje a una conversación existente.
    """
    try:
        # Procesar mensaje
        state, audio_stream = await conversation_service.process_message(
            conversation_id=conversation_id,
            message_text=request.message
        )
        
        # Obtener el último mensaje (respuesta del asistente)
        last_message = state.messages[-1].content if state.messages else None
        
        return ConversationResponse(
            conversation_id=state.conversation_id,
            status="active",
            phase=state.phase,
            message=last_message
        )
    except ValueError as e:
        logger.error(f"Error de validación: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error al procesar mensaje: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{conversation_id}/audio")
async def get_audio_response(conversation_id: str):
    """
    Obtener la respuesta de audio para el último mensaje del asistente.
    """
    try:
        # Recuperar estado de la conversación
        state = await conversation_service._get_conversation_state(conversation_id)
        if not state:
            logger.error(f"No se encontró conversación con ID {conversation_id}")
            raise HTTPException(status_code=404, detail=f"Conversación no encontrada: {conversation_id}")
        
        # Verificar que hay al menos un mensaje del asistente
        assistant_messages = [msg for msg in state.messages if msg.role == "assistant"]
        if not assistant_messages:
            logger.error(f"No hay mensajes del asistente en la conversación {conversation_id}")
            raise HTTPException(status_code=404, detail="No hay mensajes del asistente en esta conversación")
        
        # Obtener el último mensaje del asistente
        last_message = assistant_messages[-1].content
        
        # Convertir a audio
        audio_stream = await conversation_service.voice_engine.text_to_speech_async(
            text=last_message,
            program_type=state.program_type,
            gender="male"  # Por defecto usamos voz masculina
        )
        
        # Devolver stream de audio
        return StreamingResponse(
            audio_stream, 
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": f"attachment; filename=response_{conversation_id}.mp3"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al generar audio: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{conversation_id}/end", response_model=ConversationResponse)
async def end_conversation(conversation_id: str):
    """
    Finalizar una conversación.
    """
    try:
        # Finalizar conversación
        state = await conversation_service.end_conversation(conversation_id)
        
        # Obtener el último mensaje (despedida)
        last_message = state.messages[-1].content if state.messages else None
        
        return ConversationResponse(
            conversation_id=state.conversation_id,
            status="closed",
            phase=state.phase,
            message=last_message
        )
    except ValueError as e:
        logger.error(f"Error de validación: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error al finalizar conversación: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{conversation_id}", response_model=ConversationState)
async def get_conversation(conversation_id: str):
    """
    Obtener el estado completo de una conversación.
    """
    try:
        # Recuperar estado de la conversación
        state = await conversation_service._get_conversation_state(conversation_id)
        if not state:
            logger.error(f"No se encontró conversación con ID {conversation_id}")
            raise HTTPException(status_code=404, detail=f"Conversación no encontrada: {conversation_id}")
        
        return state
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al recuperar conversación: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 