"""
Servicio para gestionar la transferencia de conversaciones a agentes humanos.
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple

from src.integrations.supabase import supabase_client

# Configurar logging
logger = logging.getLogger(__name__)

class HumanTransferService:
    """
    Servicio para gestionar la transferencia de conversaciones a agentes humanos.
    Permite identificar solicitudes de transferencia y coordinar el traspaso.
    """
    
    # Frases que indican solicitud de transferencia a humano
    TRANSFER_REQUEST_PHRASES = [
        'hablar con una persona',
        'hablar con un humano',
        'hablar con un agente',
        'hablar con un representante',
        'hablar con alguien real',
        'transferir a un humano',
        'transferir a una persona',
        'transferir a un agente',
        'transferir a un representante',
        'quiero hablar con una persona',
        'necesito hablar con un humano',
        'prefiero hablar con un agente',
        'me gustaría hablar con un representante',
        'no quiero hablar con un bot',
        'no quiero hablar con una máquina',
        'no quiero hablar con una IA',
        'agente humano por favor'
    ]
    
    # Estados de transferencia
    TRANSFER_STATES = {
        'requested': 'Solicitada',
        'pending': 'Pendiente',
        'accepted': 'Aceptada',
        'rejected': 'Rechazada',
        'completed': 'Completada',
        'timed_out': 'Tiempo agotado'
    }
    
    def __init__(self):
        """Inicializar el servicio de transferencia a humanos."""
        logger.info("Servicio de transferencia a humanos inicializado")
    
    def detect_transfer_request(self, message: str) -> bool:
        """
        Detecta si un mensaje contiene una solicitud de transferencia a un agente humano.
        
        Args:
            message: Texto del mensaje del usuario
            
        Returns:
            bool: True si se detecta una solicitud de transferencia
        """
        message_lower = message.lower()
        
        # Verificar frases explícitas de solicitud de transferencia
        for phrase in self.TRANSFER_REQUEST_PHRASES:
            if phrase in message_lower:
                logger.info(f"Solicitud de transferencia detectada: '{phrase}' en mensaje")
                return True
                
        return False
    
    async def request_human_transfer(self, conversation_id: str, user_id: str, 
                                    reason: str = "Solicitud del usuario") -> Dict[str, Any]:
        """
        Registra una solicitud de transferencia a un agente humano.
        
        Args:
            conversation_id: ID de la conversación
            user_id: ID del usuario
            reason: Motivo de la transferencia
            
        Returns:
            Dict: Datos de la solicitud de transferencia
        """
        try:
            # Crear registro de transferencia
            transfer_data = {
                'id': str(uuid.uuid4()),
                'conversation_id': conversation_id,
                'user_id': user_id,
                'reason': reason,
                'status': 'requested',
                'requested_at': datetime.now().isoformat(),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Guardar en Supabase
            result = await supabase_client.table("human_transfer_requests").insert(transfer_data).execute()
            
            if result.data:
                logger.info(f"Solicitud de transferencia registrada: {result.data[0]['id']}")
                return result.data[0]
            
            logger.warning("No se pudo registrar la solicitud de transferencia")
            return transfer_data
            
        except Exception as e:
            logger.error(f"Error al registrar solicitud de transferencia: {e}")
            # Retornamos los datos aunque no se hayan guardado
            return transfer_data
    
    async def get_transfer_status(self, transfer_id: str) -> Dict[str, Any]:
        """
        Obtiene el estado actual de una solicitud de transferencia.
        
        Args:
            transfer_id: ID de la solicitud de transferencia
            
        Returns:
            Dict: Estado actual de la transferencia
        """
        try:
            result = await supabase_client.table("human_transfer_requests") \
                .select("*") \
                .eq("id", transfer_id) \
                .execute()
                
            if result.data:
                return result.data[0]
                
            logger.warning(f"No se encontró la solicitud de transferencia {transfer_id}")
            return {'status': 'not_found'}
            
        except Exception as e:
            logger.error(f"Error al obtener estado de transferencia: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def update_transfer_status(self, transfer_id: str, status: str, 
                                    agent_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Actualiza el estado de una solicitud de transferencia.
        
        Args:
            transfer_id: ID de la solicitud de transferencia
            status: Nuevo estado
            agent_id: ID del agente humano asignado (opcional)
            
        Returns:
            Dict: Datos actualizados de la transferencia
        """
        try:
            if status not in self.TRANSFER_STATES:
                raise ValueError(f"Estado de transferencia no válido: {status}")
                
            update_data = {
                'status': status,
                'updated_at': datetime.now().isoformat()
            }
            
            # Añadir campos específicos según el estado
            if status == 'accepted' and agent_id:
                update_data['agent_id'] = agent_id
                update_data['accepted_at'] = datetime.now().isoformat()
            elif status == 'completed':
                update_data['completed_at'] = datetime.now().isoformat()
            elif status == 'rejected':
                update_data['rejected_at'] = datetime.now().isoformat()
                
            result = await supabase_client.table("human_transfer_requests") \
                .update(update_data) \
                .eq("id", transfer_id) \
                .execute()
                
            if result.data:
                logger.info(f"Estado de transferencia {transfer_id} actualizado a '{status}'")
                return result.data[0]
                
            logger.warning(f"No se pudo actualizar el estado de la transferencia {transfer_id}")
            return {'status': 'error', 'message': 'No se pudo actualizar el estado'}
            
        except Exception as e:
            logger.error(f"Error al actualizar estado de transferencia: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def generate_transfer_message(self, wait_time: int = 2) -> str:
        """
        Genera un mensaje para informar al usuario sobre la transferencia.
        
        Args:
            wait_time: Tiempo estimado de espera en minutos
            
        Returns:
            str: Mensaje para el usuario
        """
        return (
            f"Entiendo que prefieres hablar con un agente humano. Estoy transfiriendo tu "
            f"conversación a uno de nuestros representantes. El tiempo estimado de espera "
            f"es de aproximadamente {wait_time} minutos. Mientras tanto, ¿hay algo más "
            f"en lo que pueda ayudarte?"
        )
