"""
Servicio para gestionar el seguimiento post-conversación con usuarios.
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple

from src.integrations.supabase import supabase_client

# Configurar logging
logger = logging.getLogger(__name__)

class FollowUpService:
    """
    Servicio para gestionar el seguimiento post-conversación con usuarios.
    Implementa recordatorios y seguimiento por email después de conversaciones con alta intención.
    """
    
    # Tipos de seguimiento
    FOLLOW_UP_TYPES = {
        'high_intent': 'Alta intención',
        'objection_handling': 'Manejo de objeciones',
        'information_request': 'Solicitud de información',
        'demo_request': 'Solicitud de demo',
        'pricing_request': 'Solicitud de precios',
        'transfer_follow_up': 'Seguimiento de transferencia'
    }
    
    # Estados de seguimiento
    FOLLOW_UP_STATES = {
        'scheduled': 'Programado',
        'sent': 'Enviado',
        'responded': 'Respondido',
        'completed': 'Completado',
        'cancelled': 'Cancelado'
    }
    
    def __init__(self):
        """Inicializar el servicio de seguimiento."""
        logger.info("Servicio de seguimiento post-conversación inicializado")
    
    async def schedule_follow_up(self, 
                               user_id: str, 
                               conversation_id: str, 
                               follow_up_type: str,
                               days_delay: int = 1,
                               template_id: Optional[str] = None,
                               custom_message: Optional[str] = None) -> Dict[str, Any]:
        """
        Programa un seguimiento para un usuario después de una conversación.
        
        Args:
            user_id: ID del usuario
            conversation_id: ID de la conversación
            follow_up_type: Tipo de seguimiento
            days_delay: Días de espera antes de enviar el seguimiento
            template_id: ID de la plantilla de email (opcional)
            custom_message: Mensaje personalizado (opcional)
            
        Returns:
            Dict: Datos del seguimiento programado
        """
        try:
            if follow_up_type not in self.FOLLOW_UP_TYPES:
                raise ValueError(f"Tipo de seguimiento no válido: {follow_up_type}")
                
            # Calcular fecha de envío
            scheduled_date = datetime.now() + timedelta(days=days_delay)
            
            # Crear registro de seguimiento
            follow_up_data = {
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'conversation_id': conversation_id,
                'follow_up_type': follow_up_type,
                'status': 'scheduled',
                'scheduled_date': scheduled_date.isoformat(),
                'template_id': template_id,
                'custom_message': custom_message,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Guardar en Supabase
            result = await supabase_client.table("follow_up_requests").insert(follow_up_data).execute()
            
            if result.data:
                logger.info(f"Seguimiento programado: {result.data[0]['id']} para {scheduled_date.isoformat()}")
                return result.data[0]
            
            logger.warning("No se pudo programar el seguimiento")
            return follow_up_data
            
        except Exception as e:
            logger.error(f"Error al programar seguimiento: {e}")
            # Retornamos los datos aunque no se hayan guardado
            return {
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'conversation_id': conversation_id,
                'follow_up_type': follow_up_type,
                'status': 'error',
                'error': str(e)
            }
    
    async def get_follow_up_status(self, follow_up_id: str) -> Dict[str, Any]:
        """
        Obtiene el estado actual de un seguimiento.
        
        Args:
            follow_up_id: ID del seguimiento
            
        Returns:
            Dict: Estado actual del seguimiento
        """
        try:
            result = await supabase_client.table("follow_up_requests") \
                .select("*") \
                .eq("id", follow_up_id) \
                .execute()
                
            if result.data:
                return result.data[0]
                
            logger.warning(f"No se encontró el seguimiento {follow_up_id}")
            return {'status': 'not_found'}
            
        except Exception as e:
            logger.error(f"Error al obtener estado de seguimiento: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def update_follow_up_status(self, follow_up_id: str, status: str, 
                                    notes: Optional[str] = None) -> Dict[str, Any]:
        """
        Actualiza el estado de un seguimiento.
        
        Args:
            follow_up_id: ID del seguimiento
            status: Nuevo estado
            notes: Notas adicionales (opcional)
            
        Returns:
            Dict: Datos actualizados del seguimiento
        """
        try:
            if status not in self.FOLLOW_UP_STATES:
                raise ValueError(f"Estado de seguimiento no válido: {status}")
                
            update_data = {
                'status': status,
                'updated_at': datetime.now().isoformat()
            }
            
            # Añadir campos específicos según el estado
            if status == 'sent':
                update_data['sent_date'] = datetime.now().isoformat()
            elif status == 'responded':
                update_data['response_date'] = datetime.now().isoformat()
            
            if notes:
                update_data['notes'] = notes
                
            result = await supabase_client.table("follow_up_requests") \
                .update(update_data) \
                .eq("id", follow_up_id) \
                .execute()
                
            if result.data:
                logger.info(f"Estado de seguimiento {follow_up_id} actualizado a '{status}'")
                return result.data[0]
                
            logger.warning(f"No se pudo actualizar el estado del seguimiento {follow_up_id}")
            return {'status': 'error', 'message': 'No se pudo actualizar el estado'}
            
        except Exception as e:
            logger.error(f"Error al actualizar estado de seguimiento: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def generate_follow_up_email(self, follow_up_type: str, user_name: str) -> str:
        """
        Genera el contenido de un email de seguimiento según el tipo.
        
        Args:
            follow_up_type: Tipo de seguimiento
            user_name: Nombre del usuario
            
        Returns:
            str: Contenido del email de seguimiento
        """
        templates = {
            'high_intent': f"""
Asunto: Siguiente paso en tu camino hacia el bienestar

Hola {user_name},

Gracias por tu interés en nuestro programa. Durante nuestra conversación, noté tu entusiasmo por mejorar tu salud y bienestar.

Para ayudarte a dar el siguiente paso, he preparado un plan personalizado basado en lo que hablamos. ¿Te gustaría programar una sesión estratégica inicial para revisar este plan juntos?

Puedes reservar un espacio en mi calendario aquí: [LINK_CALENDARIO]

Estoy a tu disposición para responder cualquier pregunta adicional.

Saludos cordiales,
Equipo NGX
            """,
            
            'objection_handling': f"""
Asunto: Aclarando tus dudas sobre nuestro programa

Hola {user_name},

Gracias por tomarte el tiempo de hablar con nosotros. Entiendo que tenías algunas preguntas sobre nuestro programa.

He recopilado información específica para abordar tus inquietudes:

1. [RESPUESTA A OBJECIÓN 1]
2. [RESPUESTA A OBJECIÓN 2]
3. [RESPUESTA A OBJECIÓN 3]

¿Podríamos agendar una breve llamada para discutir estos puntos en más detalle? Estoy disponible esta semana.

Saludos cordiales,
Equipo NGX
            """,
            
            'information_request': f"""
Asunto: La información que solicitaste sobre nuestro programa

Hola {user_name},

Adjunto encontrarás la información detallada que solicitaste sobre nuestro programa. Incluye:

- Descripción completa del programa
- Planes y precios
- Testimonios de clientes
- Preguntas frecuentes

Si tienes alguna pregunta adicional, no dudes en contactarme directamente respondiendo a este email.

Saludos cordiales,
Equipo NGX
            """,
            
            'transfer_follow_up': f"""
Asunto: Continuando nuestra conversación

Hola {user_name},

Quería hacer un seguimiento después de nuestra conversación reciente. Espero que hayas tenido una buena experiencia con nuestro representante.

¿Hay algo más en lo que podamos ayudarte? Estamos aquí para responder cualquier pregunta adicional que puedas tener.

Saludos cordiales,
Equipo NGX
            """
        }
        
        return templates.get(follow_up_type, f"""
Asunto: Gracias por contactarnos

Hola {user_name},

Gracias por tu interés en nuestro programa. Estamos aquí para ayudarte en tu camino hacia el bienestar.

Si tienes alguna pregunta, no dudes en contactarnos.

Saludos cordiales,
Equipo NGX
        """)
    
    async def get_pending_follow_ups(self) -> List[Dict[str, Any]]:
        """
        Obtiene los seguimientos pendientes que deben enviarse.
        
        Returns:
            List[Dict[str, Any]]: Lista de seguimientos pendientes
        """
        try:
            now = datetime.now().isoformat()
            
            result = await supabase_client.table("follow_up_requests") \
                .select("*") \
                .eq("status", "scheduled") \
                .lt("scheduled_date", now) \
                .execute()
                
            if result.data:
                logger.info(f"Se encontraron {len(result.data)} seguimientos pendientes")
                return result.data
                
            return []
            
        except Exception as e:
            logger.error(f"Error al obtener seguimientos pendientes: {e}")
            return []
