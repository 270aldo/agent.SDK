import logging
import asyncio
from typing import Optional, Dict, Any, Tuple, List
from io import BytesIO
from datetime import datetime
import uuid

# SDK de OpenAI Agents
from agents import Runner

from src.models.conversation import ConversationState, CustomerData, Message
# from src.integrations.openai import ConversationEngine
from src.integrations.elevenlabs import voice_engine
from src.integrations.supabase import supabase_client
from src.agents import NGXBaseAgent

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
    
    async def start_conversation(self, customer_data: CustomerData, program_type: str = "PRIME") -> ConversationState:
        """
        Iniciar una nueva conversación con un cliente.
        
        Args:
            customer_data (CustomerData): Datos del cliente
            program_type (str): Tipo de programa ("PRIME" o "LONGEVITY")
            
        Returns:
            ConversationState: Estado inicial de la conversación
        """
        state = ConversationState(
            id=str(uuid.uuid4()),
            customer_id=customer_data.id,
            program_type=program_type,
            customer_data=customer_data.model_dump(mode='json'),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        greeting = self._generate_greeting(customer_data, program_type)
        state.add_message(role="assistant", content=greeting)
        
        await self._save_conversation_state(state)
        
        logger.info(f"Conversación {state.id} iniciada para cliente {customer_data.id} con programa {program_type}")
        return state
    
    async def process_message(
        self, 
        conversation_id: str, 
        message_text: str
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
        
        formatted_history = state.get_formatted_message_history()

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
        
        if should_add_farewell:
            farewell = "Ha sido un placer hablar contigo hoy. Espero verte pronto en nuestra sesión estratégica inicial. Si tienes alguna pregunta adicional, no dudes en contactarnos. ¡Hasta pronto!"
            state.add_message(role="assistant", content=farewell)
        
        state.updated_at = datetime.now()
        await self._save_conversation_state(state)
        
        logger.info(f"Conversación {state.id} finalizada")
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
        name = customer_data.name.split()[0]  # Primer nombre
        
        if program_type == "PRIME":
            return f"Hola {name}, soy tu asesor de NGX PRIME. Gracias por completar nuestra evaluación de optimización biológica. Veo que tienes interés en mejorar tu rendimiento cognitivo y energía. ¿Es un buen momento para hablar sobre cómo nuestro programa podría ayudarte a lograr tus objetivos?"
        else:  # LONGEVITY
            return f"Hola {name}, soy tu asesor de NGX LONGEVITY. Gracias por completar nuestra evaluación de vitalidad y bienestar. Veo que estás interesado en mantener tu independencia funcional y mejorar tu calidad de vida. ¿Te parece bien si conversamos sobre cómo nuestro programa podría adaptarse a tus necesidades específicas?"
    
    async def _get_conversation_state(self, conversation_id: str) -> Optional[ConversationState]:
        """
        Recuperar el estado de una conversación desde Supabase.
        
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