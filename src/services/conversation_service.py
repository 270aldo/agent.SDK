import logging
import asyncio
import os
import json
from typing import Optional, Dict, Any, Tuple, List
from io import BytesIO
from datetime import datetime
import uuid

# Importar nuevos sistemas de plataforma
from src.models.conversation import ConversationState, CustomerData, Message
from src.models.platform_context import PlatformContext, PlatformInfo, SourceType
from src.core.agent_factory import agent_factory, AgentInterface
from src.core.platform_config import PlatformConfigManager

# Importar integraciones
from src.integrations.elevenlabs import voice_engine
from src.integrations.supabase import supabase_client

# Importar servicios adicionales
from src.services.intent_analysis_service import IntentAnalysisService
from src.services.enhanced_intent_analysis_service import EnhancedIntentAnalysisService
from src.services.qualification_service import LeadQualificationService
from src.services.human_transfer_service import HumanTransferService
from src.services.follow_up_service import FollowUpService
from src.services.personalization_service import PersonalizationService
from src.services.nlp_integration_service import NLPIntegrationService

# Configurar logging
logger = logging.getLogger(__name__)

class ConversationService:
    """
    Servicio refactorizado que gestiona conversaciones multi-plataforma.
    
    Características:
    - Soporte para múltiples puntos de contacto (web, mobile, API)
    - Gestión robusta de agentes mediante factory pattern
    - Configuración específica por plataforma
    - Manejo de errores mejorado
    """
    
    def __init__(self, industry: str = 'salud', platform_context: Optional[PlatformContext] = None):
        """
        Inicializar el servicio de conversación multi-plataforma.
        
        Args:
            industry: Industria para personalizar el análisis de intención
            platform_context: Contexto de plataforma (opcional, se puede establecer después)
        """
        self.industry = industry
        self.platform_context = platform_context
        
        logger.info(f"ConversationService inicializado para industria: {industry}")
        
        # Inicializar servicios adicionales
        self.intent_analysis_service = IntentAnalysisService()
        self.enhanced_intent_service = EnhancedIntentAnalysisService(industry=industry)
        self.qualification_service = LeadQualificationService()
        self.human_transfer_service = HumanTransferService()
        self.follow_up_service = FollowUpService()
        self.personalization_service = PersonalizationService()
        self.nlp_service = NLPIntegrationService()
        
        # Instancia de agente actual
        self._current_agent: Optional[AgentInterface] = None
        
        # Verificar adaptadores disponibles
        available_adapters = agent_factory.get_available_adapters()
        logger.info(f"Adaptadores de agente disponibles: {available_adapters}")
    
    async def start_conversation(
        self, 
        customer_data: CustomerData, 
        program_type: str = "PRIME",
        platform_info: Optional[PlatformInfo] = None
    ) -> ConversationState:
        """
        Iniciar una nueva conversación multi-plataforma.
        
        Args:
            customer_data: Datos del cliente
            program_type: Tipo de programa ("PRIME" o "LONGEVITY")
            platform_info: Información de la plataforma (opcional)
            
        Returns:
            ConversationState: Estado inicial de la conversación
            
        Raises:
            ValueError: Si el usuario está en cooldown
            RuntimeError: Si no se puede crear el agente
        """
        try:
            # Verificar cooldown del usuario
            cooldown_status = await self.qualification_service._check_cooldown(str(customer_data.id))
            if cooldown_status['in_cooldown']:
                raise ValueError(
                    f"Solo se permite una llamada cada 48 horas. "
                    f"Disponible en {cooldown_status['hours_remaining']} horas"
                )
            
            # Establecer o crear contexto de plataforma
            if platform_info:
                self.platform_context = PlatformConfigManager.get_platform_config(platform_info.source)
                self.platform_context.platform_info = platform_info
            elif not self.platform_context:
                # Usar configuración por defecto
                self.platform_context = PlatformConfigManager.get_platform_config(SourceType.DIRECT_API)
                logger.info("Usando configuración de plataforma por defecto")
            
            # Crear agente usando factory
            self._current_agent = await agent_factory.create_agent(
                platform_context=self.platform_context,
                customer_data=customer_data
            )
            
            # Crear estado inicial de la conversación
            conversation_id = str(uuid.uuid4())
            state = ConversationState(
                id=conversation_id,
                customer_id=customer_data.id,
                program_type=program_type,
                customer_data=customer_data.model_dump(mode='json') if hasattr(customer_data, 'model_dump') else vars(customer_data),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Añadir contexto de plataforma al estado
            if hasattr(state, 'platform_context'):
                state.platform_context = self.platform_context.to_dict()
            
            # Registrar sesión con configuración de plataforma
            await self._register_session(state, customer_data, conversation_id)
            
            # Generar saludo personalizado por plataforma
            greeting = await self._generate_platform_greeting(customer_data, program_type)
            state.add_message(role="assistant", content=greeting)
            
            # Guardar estado inicial
            await self._save_conversation_state(state)
            
            logger.info(
                f"Conversación {state.id} iniciada para cliente {customer_data.id} "
                f"con programa {program_type} en plataforma {self.platform_context.platform_info.source.value}"
            )
            
            return state
            
        except Exception as e:
            logger.error(f"Error iniciando conversación: {e}", exc_info=True)
            raise
    
    async def _register_session(
        self, 
        state: ConversationState, 
        customer_data: CustomerData, 
        conversation_id: str
    ) -> None:
        """
        Registrar sesión con configuración de plataforma.
        """
        try:
            session = await self.qualification_service.register_voice_agent_session(
                user_id=str(customer_data.id),
                conversation_id=conversation_id
            )
            
            # Configurar sesión con valores de plataforma
            state.session_id = session.get('id')
            state.max_duration_seconds = self.platform_context.conversation_config.max_duration_seconds
            state.intent_detection_timeout = session.get('intent_detection_timeout', 180)
            state.session_start_time = datetime.now()
            
        except Exception as e:
            logger.warning(f"No se pudo registrar sesión: {e}")
            # Usar valores de configuración de plataforma como fallback
            state.max_duration_seconds = self.platform_context.conversation_config.max_duration_seconds
            state.intent_detection_timeout = 180
            state.session_start_time = datetime.now()
    
    async def _generate_platform_greeting(
        self, 
        customer_data: CustomerData, 
        program_type: str
    ) -> str:
        """
        Generar saludo personalizado por plataforma.
        """
        try:
            # Usar el agente para generar el saludo
            context = {
                "customer_name": customer_data.name,
                "program_type": program_type,
                "platform_source": self.platform_context.platform_info.source.value,
                "conversation_mode": self.platform_context.conversation_config.mode.value
            }
            
            greeting_prompt = f"Genera un saludo para {customer_data.name} interesado en {program_type}"
            greeting = await self._current_agent.process_message(greeting_prompt, context)
            
            return greeting
            
        except Exception as e:
            logger.warning(f"Error generando saludo personalizado: {e}")
            # Fallback a saludo genérico
            return self._generate_greeting(customer_data, program_type)
    
    def set_platform_context(self, platform_context: PlatformContext) -> None:
        """
        Establecer contexto de plataforma para el servicio.
        
        Args:
            platform_context: Nuevo contexto de plataforma
        """
        self.platform_context = platform_context
        logger.info(f"Contexto de plataforma actualizado: {platform_context.platform_info.source.value}")
    
    def get_platform_context(self) -> Optional[PlatformContext]:
        """Obtener contexto de plataforma actual."""
        return self.platform_context
    
    async def process_message(
        self, 
        conversation_id: str, 
        message_text: str,
        check_intent: bool = True
    ) -> Tuple[ConversationState, BytesIO]:
        """
        Procesar un mensaje del cliente usando el agente multi-plataforma.
        
        Args:
            conversation_id: ID de la conversación
            message_text: Mensaje del cliente
            check_intent: Si verificar intención y transferencias
            
        Returns:
            Tuple[ConversationState, BytesIO]: Estado actualizado y audio de respuesta
            
        Raises:
            ValueError: Si no se encuentra la conversación
            RuntimeError: Si hay error procesando el mensaje
        """
        try:
            # Obtener estado de la conversación
            state = await self._get_conversation_state(conversation_id)
            if not state:
                logger.error(f"Conversación {conversation_id} no encontrada")
                raise ValueError(f"Conversación {conversation_id} no encontrada")
            
            # Añadir mensaje del usuario
            state.add_message(role="user", content=message_text)
            
            # Verificar si necesitamos crear/recuperar el agente
            if not self._current_agent:
                await self._restore_agent_from_state(state)
            
            # Procesar mensaje con el agente
            response_message = await self._process_with_agent(message_text, state)
            
            # Realizar análisis de intención si está habilitado
            if check_intent:
                await self._analyze_intent(state, conversation_id)
                
                # Verificar transferencia a humano
                if await self._check_human_transfer(message_text, state, conversation_id):
                    # La transferencia ya maneja la respuesta
                    audio_response = await self._generate_audio(state.messages[-1].content)
                    return state, audio_response
            
            # Añadir respuesta del agente
            state.add_message(role="assistant", content=response_message)
            
            # Verificar si debe continuar la conversación
            if check_intent and not await self._should_continue_conversation(state):
                # La función ya maneja el cierre
                audio_response = await self._generate_audio(state.messages[-1].content)
                return state, audio_response
            
            # Generar audio para la respuesta
            audio_response = await self._generate_audio(response_message)
            
            # Guardar estado actualizado
            await self._save_conversation_state(state)
            
            logger.info(f"Mensaje procesado exitosamente para conversación {conversation_id}")
            return state, audio_response
            
        except Exception as e:
            logger.error(f"Error procesando mensaje en conversación {conversation_id}: {e}", exc_info=True)
            raise RuntimeError(f"Error procesando mensaje: {str(e)}") from e
        
    async def end_conversation(self, conversation_id: str, end_reason: str = "completed") -> ConversationState:
        """
        Finalizar una conversación.
        
        Args:
            conversation_id (str): ID de la conversación
            end_reason (str): Razón de finalización
            
        Returns:
            ConversationState: Estado actualizado de la conversación
        """
        state = await self._get_conversation_state(conversation_id)
        if not state:
            logger.error(f"No se encontró conversación con ID {conversation_id}")
            raise ValueError(f"No se encontró conversación con ID {conversation_id}")
        
        state.status = "ended"
        state.end_reason = end_reason
        state.ended_at = datetime.now()
        
        # Determinar si hubo conversión basado en la razón de finalización
        conversion_result = False
        if end_reason in ["completed", "high_intent", "scheduled_demo", "purchase"]:
            conversion_result = True
        
        # Actualizar el modelo de intención con los resultados de esta conversación
        try:
            await self.enhanced_intent_service.update_model_from_conversation(
                conversation_id=conversation_id,
                messages=state.get_formatted_message_history(),
                conversion_result=conversion_result
            )
            logger.info(f"Modelo de intención actualizado con resultados de conversación {conversation_id}")
            
            # Guardar datos de entrenamiento para aprendizaje continuo
            user_messages = [msg["content"] for msg in state.get_formatted_message_history() if msg["role"] == "user"]
            
            # Determinar etiqueta de intención
            intent_label = "low_intent"
            if hasattr(state, 'intent_analysis_results'):
                intent_prob = state.intent_analysis_results.get("purchase_intent_probability", 0)
                if intent_prob > 0.7:
                    intent_label = "high_intent"
                elif intent_prob > 0.4:
                    intent_label = "medium_intent"
                elif state.intent_analysis_results.get("has_rejection", False):
                    intent_label = "rejection"
            
            # Guardar cada mensaje del usuario como dato de entrenamiento
            for msg in user_messages[-3:]:  # Usar los últimos 3 mensajes
                training_data = {
                    "conversation_id": conversation_id,
                    "user_message": msg,
                    "intent_label": intent_label,
                    "industry": self.enhanced_intent_service.industry,
                    "keywords_detected": json.dumps(state.intent_analysis_results.get("intent_indicators", [])),
                    "sentiment_score": state.intent_analysis_results.get("sentiment_score", 0),
                    "conversion_result": conversion_result
                }
                
                supabase_client.table("intent_training_data").insert(training_data).execute()
            
        except Exception as e:
            logger.error(f"Error al actualizar modelo de intención: {e}")
        
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
        
        # Realizar análisis final de NLP para toda la conversación
        try:
            # Obtener todas las conversaciones para analizar
            formatted_history = state.get_formatted_message_history()
            
            # Análisis completo de NLP
            final_nlp_analysis = await asyncio.to_thread(
                lambda: self.nlp_service.analyze_conversation(formatted_history, conversation_id)
            )
            
            # Obtener insights finales
            final_insights = await asyncio.to_thread(
                lambda: self.nlp_service.get_conversation_insights(conversation_id)
            )
            
            # Guardar análisis final e insights en el estado
            if 'session_insights' not in state.model_dump():
                state.session_insights = {}
                
            state.session_insights['final_nlp_analysis'] = final_nlp_analysis
            state.session_insights['final_nlp_insights'] = final_insights
            
            # Análisis de intención tradicional (para compatibilidad)
            intent_analysis = self.intent_analysis_service.analyze_purchase_intent(formatted_history)
            
            # Enriquecer el análisis de intención con los insights de NLP
            if 'intent' in final_insights and 'conversation_status' in final_insights:
                if final_insights['conversation_status'].get('conversation_phase') == 'decisión':
                    intent_analysis['purchase_intent_probability'] = max(intent_analysis['purchase_intent_probability'], 0.7)
                    intent_analysis['has_purchase_intent'] = True
            
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
        Obtener el estado de una conversación.
        
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
    
    async def _restore_agent_from_state(self, state: ConversationState) -> None:
        """Restaurar agente desde el estado de la conversación."""
        try:
            # Restaurar contexto de plataforma si existe
            if hasattr(state, 'platform_context') and state.platform_context:
                self.platform_context = PlatformContext.from_dict(state.platform_context)
            elif not self.platform_context:
                # Usar configuración por defecto
                self.platform_context = PlatformConfigManager.get_platform_config(SourceType.DIRECT_API)
            
            # Crear agente usando factory
            customer_data = CustomerData(**state.customer_data)
            self._current_agent = await agent_factory.create_agent(
                platform_context=self.platform_context,
                customer_data=customer_data
            )
            
            logger.info(f"Agente restaurado para conversación {state.id}")
            
        except Exception as e:
            logger.error(f"Error restaurando agente: {e}")
            raise RuntimeError(f"No se pudo restaurar el agente: {str(e)}") from e
    
    async def _process_with_agent(self, message_text: str, state: ConversationState) -> str:
        """Procesar mensaje con el agente actual."""
        try:
            # Preparar contexto para el agente
            context = {
                "conversation_id": state.id,
                "customer_id": state.customer_id,
                "program_type": state.program_type,
                "conversation_history": [
                    {"role": msg.role, "content": msg.content} 
                    for msg in state.messages[-5:]  # Últimos 5 mensajes para contexto
                ],
                "platform_info": self.platform_context.platform_info.to_dict() if self.platform_context else {},
                "conversation_config": self.platform_context.conversation_config.__dict__ if self.platform_context else {}
            }
            
            # Procesar mensaje con el agente
            response = await self._current_agent.process_message(message_text, context)
            
            return response
            
        except Exception as e:
            logger.error(f"Error procesando con agente: {e}")
            # Fallback a respuesta genérica
            return "Lo siento, no pude procesar tu mensaje en este momento. ¿Podrías reformular tu pregunta?"
    
    async def _analyze_intent(self, state: ConversationState, conversation_id: str) -> None:
        """Analizar intención de compra y guardar resultados."""
        try:
            # Analizar intención con el servicio mejorado
            enhanced_intent_analysis = self.enhanced_intent_service.analyze_purchase_intent(
                state.get_formatted_message_history()
            )
            
            logger.info(f"Análisis de intención para {conversation_id}: {enhanced_intent_analysis}")
            
            # Guardar resultados en Supabase
            analysis_data = {
                "conversation_id": conversation_id,
                "user_id": state.customer_id,
                "purchase_intent_probability": enhanced_intent_analysis["purchase_intent_probability"],
                "has_purchase_intent": enhanced_intent_analysis["has_purchase_intent"],
                "has_rejection": enhanced_intent_analysis["has_rejection"],
                "intent_indicators": json.dumps(enhanced_intent_analysis["intent_indicators"]),
                "rejection_indicators": json.dumps(enhanced_intent_analysis["rejection_indicators"]),
                "sentiment_score": enhanced_intent_analysis["sentiment_score"],
                "engagement_score": enhanced_intent_analysis["engagement_score"],
                "industry": self.enhanced_intent_service.industry,
                "model_id": self.enhanced_intent_service.intent_model.get("id")
            }
            
            supabase_client.table("intent_analysis_results").insert(analysis_data).execute()
            
            # Actualizar estado con resultados
            state.intent_analysis_results = enhanced_intent_analysis
            
        except Exception as e:
            logger.error(f"Error analizando intención: {e}")
    
    async def _check_human_transfer(
        self, 
        message_text: str, 
        state: ConversationState, 
        conversation_id: str
    ) -> bool:
        """Verificar si se requiere transferencia a agente humano."""
        try:
            # Solo verificar si está habilitado en la configuración
            if not self.platform_context.conversation_config.enable_transfer:
                return False
            
            # Detectar solicitud de transferencia
            transfer_requested = self.human_transfer_service.detect_transfer_request(message_text)
            
            if transfer_requested:
                logger.info(f"Transferencia solicitada en conversación {conversation_id}")
                
                # Obtener insights de NLP
                conversation_insights = await asyncio.to_thread(
                    lambda: self.nlp_service.get_conversation_insights(conversation_id)
                )
                
                # Preparar insights combinados
                enhanced_insights = {
                    **state.session_insights,
                    'nlp_conversation_insights': conversation_insights
                }
                
                # Verificar si se necesita transferencia
                transfer_needed = await asyncio.to_thread(
                    lambda: self.human_transfer_service.check_transfer_needed(enhanced_insights)
                )
                
                if transfer_needed['transfer_needed']:
                    # Actualizar estado
                    state.phase = "human_transfer"
                    state.session_insights['human_transfer'] = transfer_needed
                    
                    # Generar mensaje de transferencia
                    transfer_message = await asyncio.to_thread(
                        lambda: self.human_transfer_service.generate_transfer_message(transfer_needed['reason'])
                    )
                    
                    # Añadir mensaje al historial
                    state.add_message(role="assistant", content=transfer_message)
                    
                    logger.info(f"Transferencia aprobada para conversación {conversation_id}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error verificando transferencia: {e}")
            return False
    
    async def _should_continue_conversation(self, state: ConversationState) -> bool:
        """Verificar si la conversación debe continuar."""
        try:
            # Verificar timeout solo si tenemos la información necesaria
            if (hasattr(state, 'session_start_time') and 
                hasattr(state, 'intent_detection_timeout') and 
                state.session_start_time and state.intent_detection_timeout):
                
                should_continue, end_reason = self.enhanced_intent_service.should_continue_conversation(
                    messages=state.get_formatted_message_history(),
                    session_start_time=state.session_start_time,
                    intent_detection_timeout=state.intent_detection_timeout
                )
                
                if not should_continue:
                    logger.info(f"Finalizando conversación {state.id}: {end_reason}")
                    
                    # Actualizar sesión si existe
                    if hasattr(state, 'session_id') and state.session_id:
                        try:
                            await self.qualification_service.update_session_status(
                                session_id=state.session_id,
                                status='timeout',
                                end_reason=end_reason
                            )
                        except Exception as e:
                            logger.error(f"Error actualizando estado de sesión: {e}")
                    
                    # Generar mensaje de cierre
                    closing_message = self._generate_closing_message(end_reason)
                    state.add_message(role="assistant", content=closing_message)
                    
                    # Actualizar fase
                    state.phase = "ended"
                    state.end_reason = end_reason
                    
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error verificando continuación de conversación: {e}")
            return True  # En caso de error, continuar por seguridad
    
    async def _generate_audio(self, text: str) -> BytesIO:
        """Generar audio para el texto dado."""
        try:
            # Verificar si la síntesis de voz está habilitada
            if not self.platform_context.conversation_config.enable_voice:
                # Retornar audio vacío si no está habilitado
                return BytesIO()
            
            # Generar audio usando ElevenLabs
            audio_response = await asyncio.to_thread(
                lambda: voice_engine.text_to_speech(text)
            )
            
            return audio_response
            
        except Exception as e:
            logger.error(f"Error generando audio: {e}")
            # Retornar audio vacío en caso de error
            return BytesIO()
    
    def _generate_closing_message(self, end_reason: str) -> str:
        """Generar mensaje de cierre basado en la razón."""
        closing_messages = {
            'rejection_detected': "Entiendo que no es el momento adecuado. Gracias por tu tiempo y estaremos aquí cuando estés listo.",
            'timeout': "Ha sido un placer conversar contigo. Si tienes más preguntas, no dudes en contactarnos.",
            'intent_achieved': "Perfecto, hemos cubierto todo lo que necesitabas. ¡Gracias por tu tiempo!",
            'default': "Gracias por conversar con nosotros. ¡Que tengas un excelente día!"
        }
        
        return closing_messages.get(end_reason, closing_messages['default']) 