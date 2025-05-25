import logging
import asyncio
import os
from typing import Optional, Dict, Any, Tuple, List
from io import BytesIO
from datetime import datetime
import uuid

# SDK de OpenAI Agents
try:
    from agents import Runner
except ImportError:
    # Si no está instalado, creamos un Runner simulado
    class Runner:
        @staticmethod
        async def run(agent, messages):
            return None

from src.models.conversation import ConversationState, CustomerData, Message
# from src.integrations.openai import ConversationEngine
from src.integrations.elevenlabs import voice_engine
from src.integrations.supabase import supabase_client
from src.agents import NGXBaseAgent

# Importar el agente simulado
from src.agents.mock_agent import MockAgent, MockRunner

# Importar servicios adicionales
from src.services.intent_analysis_service import IntentAnalysisService
from src.services.qualification_service import LeadQualificationService
from src.services.human_transfer_service import HumanTransferService
from src.services.follow_up_service import FollowUpService
from src.services.personalization_service import PersonalizationService

# Configurar logging
logger = logging.getLogger(__name__)

class ConversationService:
    """
    Servicio que integra los motores de conversación (OpenAI Agents SDK), síntesis de voz (ElevenLabs)
    y persistencia (Supabase) para gestionar las conversaciones con clientes.
    """
    
    def __init__(self):
        """
        Inicializar el servicio de conversación.
        """
        logger.info("Servicio de conversación inicializado para usar OpenAI Agents SDK")
        
        # Inicializar servicios adicionales
        self.intent_analysis_service = IntentAnalysisService()
        self.qualification_service = LeadQualificationService()
        self.human_transfer_service = HumanTransferService()
        self.follow_up_service = FollowUpService()
        self.personalization_service = PersonalizationService()
    
    async def start_conversation(self, customer_data: CustomerData, program_type: str = "PRIME") -> ConversationState:
        """
        Iniciar una nueva conversación con un cliente.
        
        Args:
            customer_data (CustomerData): Datos del cliente
            program_type (str): Tipo de programa ("PRIME" o "LONGEVITY")
            
        Returns:
            ConversationState: Estado inicial de la conversación
        """
        # Verificar si el usuario ya tuvo una llamada en las últimas 48 horas
        cooldown_status = await self.qualification_service._check_cooldown(str(customer_data.id))
        if cooldown_status['in_cooldown']:
            raise ValueError(f"Solo se permite una llamada cada 48 horas. Disponible en {cooldown_status['hours_remaining']} horas")
        
        # Crear estado inicial de la conversación
        conversation_id = str(uuid.uuid4())
        state = ConversationState(
            id=conversation_id,
            customer_id=customer_data.id,
            program_type=program_type,
            customer_data=customer_data.model_dump(mode='json'),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Registrar sesión del agente de voz
        try:
            session = await self.qualification_service.register_voice_agent_session(
                user_id=str(customer_data.id),
                conversation_id=conversation_id
            )
            
            # Almacenar información de la sesión en el estado
            state.session_id = session.get('id')
            state.max_duration_seconds = session.get('max_duration_seconds')
            state.intent_detection_timeout = session.get('intent_detection_timeout')
            state.session_start_time = datetime.now()
        except Exception as e:
            logger.warning(f"No se pudo registrar la sesión del agente de voz: {e}")
            # Establecer valores por defecto
            state.max_duration_seconds = 7 * 60  # 7 minutos
            state.intent_detection_timeout = 3 * 60  # 3 minutos
            state.session_start_time = datetime.now()
        
        greeting = self._generate_greeting(customer_data, program_type)
        state.add_message(role="assistant", content=greeting)
        
        await self._save_conversation_state(state)
        
        logger.info(f"Conversación {state.id} iniciada para cliente {customer_data.id} con programa {program_type}")
        return state
    
    async def process_message(
        self, 
        conversation_id: str, 
        message_text: str,
        check_intent: bool = True
    ) -> Tuple[ConversationState, BytesIO]:
        """
        Procesar un mensaje del cliente y generar una respuesta con audio.
        
        Args:
            conversation_id (str): ID de la conversación
            message_text (str): Mensaje del cliente (solo el texto)
            
        Returns:
            Tuple[ConversationState, BytesIO]: Estado actualizado y audio de respuesta
        """
        state = await self._get_conversation_state(conversation_id)
        if not state:
            logger.error(f"No se encontró conversación con ID {conversation_id}")
            raise ValueError(f"No se encontró conversación con ID {conversation_id}")
        
        state.add_message(role="user", content=message_text)
        
        # Verificar si es una solicitud de transferencia a agente humano
        is_transfer_request = self.human_transfer_service.detect_transfer_request(message_text)
        
        if is_transfer_request:
            # Registrar solicitud de transferencia
            try:
                transfer_request = await self.human_transfer_service.request_human_transfer(
                    conversation_id=state.id,
                    user_id=state.customer_id,
                    reason="Solicitud explícita del usuario"
                )
                
                # Guardar ID de solicitud en el estado de la conversación
                state.transfer_request_id = transfer_request.get('id')
                state.transfer_status = 'requested'
                
                # Generar mensaje de transferencia
                response_text = self.human_transfer_service.generate_transfer_message(wait_time=2)
                
                state.add_message(role="assistant", content=response_text)
                state.updated_at = datetime.now()
                await self._save_conversation_state(state)
                
                # Generar audio de respuesta
                customer_gender = "male"
                if state.customer_data and isinstance(state.customer_data, dict):
                    customer_gender = state.customer_data.get("gender", "male")
                
                audio_stream = await voice_engine.text_to_speech_async(
                    text=response_text,
                    program_type=state.program_type,
                    gender=customer_gender
                )
                
                logger.info(f"Solicitud de transferencia a humano registrada para conversación {state.id}")
                return state, audio_stream
                
            except Exception as e:
                logger.error(f"Error al procesar solicitud de transferencia: {e}")
                # Continuar con el flujo normal si hay un error
        
        # Verificar si debemos aplicar el corte inteligente
        if check_intent and hasattr(state, 'session_start_time') and hasattr(state, 'intent_detection_timeout'):
            should_continue, end_reason = self.intent_analysis_service.should_continue_conversation(
                messages=state.get_formatted_message_history(),
                session_start_time=state.session_start_time,
                intent_detection_timeout=state.intent_detection_timeout
            )
            
            if not should_continue:
                # Actualizar estado de la sesión si existe
                if hasattr(state, 'session_id'):
                    try:
                        await self.qualification_service.update_session_status(
                            session_id=state.session_id,
                            status='timeout',
                            end_reason=end_reason
                        )
                    except Exception as e:
                        logger.error(f"Error al actualizar estado de sesión: {e}")
                
                # Generar mensaje de cierre basado en la razón
                if end_reason == 'rejection_detected':
                    response_text = "Entiendo que no estés interesado en este momento. Gracias por tu tiempo. Si cambias de opinión o tienes alguna pregunta en el futuro, no dudes en contactarnos."
                else:  # no_intent_detected
                    response_text = "Parece que este no es el mejor momento para hablar sobre nuestro programa. Te enviaré más información por correo electrónico para que puedas revisarla cuando te sea conveniente. ¡Gracias por tu tiempo!"
                
                state.add_message(role="assistant", content=response_text)
                state.updated_at = datetime.now()
                await self._save_conversation_state(state)
                
                # Generar audio de respuesta
                customer_gender = "male"
                if state.customer_data and isinstance(state.customer_data, dict):
                    customer_gender = state.customer_data.get("gender", "male")
                
                audio_stream = await voice_engine.text_to_speech_async(
                    text=response_text,
                    program_type=state.program_type,
                    gender=customer_gender
                )
                
                logger.info(f"Conversación {state.id} finalizada por corte inteligente: {end_reason}")
                return state, audio_stream
        
        formatted_history = state.get_formatted_message_history()

        # Verificar si debemos usar el agente simulado
        use_mock_agent = False
        try:
            # Intentar verificar la clave API de OpenAI
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key or api_key.startswith("sk-proj-"):
                # Las claves que comienzan con sk-proj- son claves de proyecto y pueden requerir configuración adicional
                # Por seguridad, usamos el agente simulado
                logger.warning(f"Usando agente simulado para la conversación {state.id} debido a formato de clave API")
                use_mock_agent = True
        except Exception:
            use_mock_agent = True

        if use_mock_agent:
            # Usar el agente simulado
            logger.info(f"Ejecutando agente simulado NGX {state.program_type} para conversación {state.id}...")
            try:
                mock_agent = MockAgent(program_type=state.program_type)
                agent_run_result = await MockRunner.run(mock_agent, formatted_history)
                response_text = agent_run_result.final_output
            except Exception as e:
                logger.error(f"Error al ejecutar el agente simulado para la conversación {state.id}: {e}")
                response_text = "Lo siento, tuve un problema al procesar tu solicitud. Por favor, inténtalo de nuevo."
        else:
            # Usar el agente real de OpenAI
            agent = NGXBaseAgent(program_type=state.program_type)
            
            logger.info(f"Ejecutando agente NGX {state.program_type} para conversación {state.id}...")
            try:
                agent_run_result = await Runner.run(agent, formatted_history)
                response_text = agent_run_result.final_output
                
                if response_text is None:
                    logger.warning(f"El agente no devolvió un final_output para la conversación {state.id}. Usando respuesta por defecto.")
                    response_text = "No estoy seguro de cómo responder a eso en este momento. ¿Podrías reformular tu pregunta?"

            except Exception as e:
                logger.error(f"Error al ejecutar el agente SDK para la conversación {state.id}: {e}")
                response_text = "Lo siento, tuve un problema al procesar tu solicitud. Por favor, inténtalo de nuevo."

        state.add_message(role="assistant", content=response_text)
        
        customer_gender = "male"
        if state.customer_data and isinstance(state.customer_data, dict):
             customer_gender = state.customer_data.get("gender", "male")

        audio_stream = await voice_engine.text_to_speech_async(
            text=response_text,
            program_type=state.program_type,
            gender=customer_gender
        )
        
        state.updated_at = datetime.now()
        await self._save_conversation_state(state)
        
        logger.info(f"Mensaje procesado para conversación {state.id}. Respuesta: {response_text[:100]}...")
        return state, audio_stream
    
    async def end_conversation(self, conversation_id: str) -> ConversationState:
        """
        Finalizar una conversación.
        
        Args:
            conversation_id (str): ID de la conversación
            
        Returns:
            ConversationState: Estado final de la conversación
        """
        state = await self._get_conversation_state(conversation_id)
        if not state:
            logger.error(f"No se encontró conversación con ID {conversation_id}")
            raise ValueError(f"No se encontró conversación con ID {conversation_id}")
        
        # Actualizar estado de la sesión si existe
        if hasattr(state, 'session_id'):
            try:
                await self.qualification_service.update_session_status(
                    session_id=state.session_id,
                    status='completed',
                    end_reason='user_ended'
                )
                logger.info(f"Estado de sesión {state.session_id} actualizado a 'completed'")
            except Exception as e:
                logger.error(f"Error al actualizar estado de sesión: {e}")
        
        # Verificar si el último mensaje ya es una despedida
        last_assistant_message_content = None
        if state.messages:
            for i in range(len(state.messages) - 1, -1, -1):
                if state.messages[i].role == "assistant":
                    last_assistant_message_content = state.messages[i].content.lower()
                    break
        
        should_add_farewell = True
        if last_assistant_message_content:
            farewell_keywords = ["hasta luego", "gracias por", "ha sido un placer", "nos vemos pronto"]
            if any(kw in last_assistant_message_content for kw in farewell_keywords):
                should_add_farewell = False
        
        # Añadir mensaje de despedida si es necesario
        if should_add_farewell:
            farewell = "Ha sido un placer hablar contigo hoy. Espero verte pronto en nuestra sesión estratégica inicial. Si tienes alguna pregunta adicional, no dudes en contactarnos. ¡Hasta pronto!"
            state.add_message(role="assistant", content=farewell)
        
        # Marcar como finalizada
        state.phase = "completed"
        state.updated_at = datetime.now()
        await self._save_conversation_state(state)
        
        # Analizar intención de compra para programar seguimiento
        try:
            # Obtener todas las conversaciones para analizar intención
            formatted_history = state.get_formatted_message_history()
            intent_analysis = self.intent_analysis_service.analyze_purchase_intent(formatted_history)
            
            # Si hay alta intención de compra, programar seguimiento
            if intent_analysis["has_purchase_intent"] and intent_analysis["purchase_intent_probability"] >= 0.6:
                # Obtener nombre del usuario
                user_name = "Cliente"
                if state.customer_data and isinstance(state.customer_data, dict):
                    user_name = state.customer_data.get("name", "Cliente").split()[0]
                
                # Programar seguimiento para alta intención
                follow_up = await self.follow_up_service.schedule_follow_up(
                    user_id=state.customer_id,
                    conversation_id=state.id,
                    follow_up_type="high_intent",
                    days_delay=1  # Seguimiento al día siguiente
                )
                
                logger.info(f"Seguimiento programado para conversación {state.id} con alta intención de compra")
                
            # Si hay objeciones pero no rechazo total, programar seguimiento para manejo de objeciones
            elif intent_analysis["rejection_indicators"] and not intent_analysis["has_rejection"]:
                # Obtener nombre del usuario
                user_name = "Cliente"
                if state.customer_data and isinstance(state.customer_data, dict):
                    user_name = state.customer_data.get("name", "Cliente").split()[0]
                
                # Programar seguimiento para manejo de objeciones
                follow_up = await self.follow_up_service.schedule_follow_up(
                    user_id=state.customer_id,
                    conversation_id=state.id,
                    follow_up_type="objection_handling",
                    days_delay=2  # Seguimiento a los 2 días
                )
                
                logger.info(f"Seguimiento programado para conversación {state.id} para manejo de objeciones")
            
            # Si hubo transferencia a humano, programar seguimiento de transferencia
            elif hasattr(state, 'transfer_request_id') and state.transfer_request_id:
                # Obtener nombre del usuario
                user_name = "Cliente"
                if state.customer_data and isinstance(state.customer_data, dict):
                    user_name = state.customer_data.get("name", "Cliente").split()[0]
                
                # Programar seguimiento para transferencia
                follow_up = await self.follow_up_service.schedule_follow_up(
                    user_id=state.customer_id,
                    conversation_id=state.id,
                    follow_up_type="transfer_follow_up",
                    days_delay=1  # Seguimiento al día siguiente
                )
                
                logger.info(f"Seguimiento programado para conversación {state.id} después de transferencia a humano")
        
        except Exception as e:
            logger.error(f"Error al programar seguimiento: {e}")
        
        logger.info(f"Conversación {conversation_id} finalizada")
        return state
    
    def _generate_greeting(self, customer_data: CustomerData, program_type: str) -> str:
        """
        Generar un mensaje de bienvenida personalizado.
        
        Args:
            customer_data (CustomerData): Datos del cliente
            program_type (str): Tipo de programa
            
        Returns:
            str: Mensaje de bienvenida
        """
        # Convertir CustomerData a diccionario para el servicio de personalización
        user_data = customer_data.model_dump(mode='json')
        
        # Generar saludo personalizado según el perfil del usuario
        personalized_greeting = self.personalization_service.generate_personalized_greeting(user_data)
        
        # Añadir información específica del programa
        if program_type == "PRIME":
            program_info = "Soy tu asistente de NGX Prime."
        else:  # LONGEVITY
            program_info = "Soy tu asistente de NGX Longevity."
            
        # Determinar el perfil de comunicación
        profile = self.personalization_service.determine_communication_profile(user_data)
        
        # Ajustar la presentación según el perfil
        if profile == 'formal':
            greeting = f"{personalized_greeting} {program_info} ¿En qué puedo asistirle hoy?"
        elif profile == 'enthusiastic':
            greeting = f"{personalized_greeting} ¡{program_info}! ¿En qué puedo ayudarte hoy? ¡Estoy aquí para ti!"
        elif profile == 'technical':
            greeting = f"{personalized_greeting} {program_info} Estoy aquí para proporcionarte información detallada sobre nuestro programa. ¿En qué área específica puedo ayudarte?"
        else:  # casual
            greeting = f"{personalized_greeting} {program_info} ¿En qué puedo ayudarte hoy?"
            
        return greeting
    
    async def _get_conversation_state(self, conversation_id: str) -> Optional[ConversationState]:
        """
{{ ... }}
        
        Args:
            conversation_id (str): ID de la conversación
            
        Returns:
            Optional[ConversationState]: Estado de la conversación o None si no existe
        """
        try:
            client = supabase_client.get_client()
            
            # Usar eq() en lugar de single() para evitar el error con múltiples filas
            response = await asyncio.to_thread(
                lambda: client.table("conversations").select("*").eq("conversation_id", conversation_id).execute()
            )
            
            # Comprobar si hay datos
            if response.data and len(response.data) > 0:
                data = response.data[0]  # Tomar el primer resultado
                
                # Procesar fechas
                for date_field in ['created_at', 'updated_at']:
                    if isinstance(data.get(date_field), str):
                        data[date_field] = datetime.fromisoformat(data[date_field])
                
                # Procesar mensajes
                raw_messages = data.get('messages', [])
                if isinstance(raw_messages, str):
                    import json
                    raw_messages = json.loads(raw_messages)
                
                parsed_messages = []
                if isinstance(raw_messages, list):
                    for msg_data in raw_messages:
                        if isinstance(msg_data, dict):
                            message_fields = {k: v for k, v in msg_data.items() if k in Message.model_fields}
                            parsed_messages.append(Message(**message_fields))
                        elif isinstance(msg_data, Message):
                            parsed_messages.append(msg_data)
                data['messages'] = parsed_messages

                # Procesar datos del cliente
                if isinstance(data.get('customer_data'), str):
                    import json
                    data['customer_data'] = json.loads(data['customer_data'])
                
                # Asegurar que el ID del modelo coincide con el ID de la conversación
                data['id'] = data['conversation_id']
                
                return ConversationState(**data)
            
            logger.warning(f"No se encontró conversación con ID {conversation_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error al recuperar conversación {conversation_id}: {e}")
            return None
    
    async def _save_conversation_state(self, state: ConversationState) -> bool:
        """
        Guardar el estado de la conversación en Supabase.
        
        Args:
            state (ConversationState): Estado de la conversación
            
        Returns:
            bool: True si se guardó correctamente
        """
        try:
            # Convertir el estado a un diccionario
            data_to_save = state.model_dump(mode='json')
            
            # Adaptar el formato para Supabase
            supabase_data = {
                "conversation_id": state.id,  # Usar el id del modelo como conversation_id
                "customer_id": data_to_save.get("customer_id"),
                "program_type": data_to_save.get("program_type"),
                "phase": data_to_save.get("phase"),
                "messages": data_to_save.get("messages", []),
                "customer_data": data_to_save.get("customer_data", {}),
                "session_insights": data_to_save.get("session_insights", {}),
                "objections_raised": data_to_save.get("objections_raised", []),
                "next_steps_agreed": data_to_save.get("next_steps_agreed", False),
                "call_duration_seconds": data_to_save.get("call_duration_seconds", 0),
                "created_at": data_to_save.get("created_at"),
                "updated_at": data_to_save.get("updated_at"),
            }
            
            client = supabase_client.get_client()
            
            await asyncio.to_thread(
                lambda: client.table("conversations").upsert(supabase_data).execute()
            )
            
            logger.info(f"Estado de conversación {state.id} guardado correctamente")
            return True
            
        except Exception as e:
            logger.error(f"Error al guardar conversación {state.id}: {e}")
            return False 