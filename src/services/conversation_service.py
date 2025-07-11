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
from src.services.program_router import ProgramRouter

# Importar nuevos servicios de inteligencia emocional
from src.services.emotional_intelligence_service import EmotionalIntelligenceService
from src.services.empathy_engine_service import EmpathyEngineService
from src.services.adaptive_personality_service import AdaptivePersonalityService
from src.services.multi_voice_service import MultiVoiceService, SalesSection

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
        
        # Inicializar servicios de inteligencia emocional
        self.emotional_intelligence_service = EmotionalIntelligenceService(
            nlp_service=self.nlp_service,
            sentiment_service=None  # TODO: Initialize sentiment service if needed
        )
        self.empathy_engine_service = EmpathyEngineService()
        self.adaptive_personality_service = AdaptivePersonalityService()
        self.multi_voice_service = MultiVoiceService()
        
        # Inicializar router de programas para detección automática
        self.program_router = ProgramRouter()
        
        # Instancia de agente actual
        self._current_agent: Optional[AgentInterface] = None
        
        # Verificar adaptadores disponibles
        available_adapters = agent_factory.get_available_adapters()
        logger.info(f"Adaptadores de agente disponibles: {available_adapters}")
    
    async def start_conversation(
        self, 
        customer_data: CustomerData, 
        program_type: Optional[str] = None,
        platform_info: Optional[PlatformInfo] = None
    ) -> ConversationState:
        """
        Iniciar una nueva conversación multi-plataforma con detección automática de programa.
        
        Args:
            customer_data: Datos del cliente
            program_type: Tipo de programa ("PRIME" o "LONGEVITY"), opcional - se detecta automáticamente si no se proporciona
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
            
            # Detectar programa automáticamente si no se especificó
            if not program_type:
                logger.info(f"Iniciando detección automática de programa para cliente: {customer_data.name}")
                
                # Convertir CustomerData a diccionario para el router
                customer_data_dict = {
                    "id": customer_data.id,
                    "name": customer_data.name,
                    "age": getattr(customer_data, 'age', None),
                    "interests": getattr(customer_data, 'interests', [])
                }
                
                # Determinar programa usando el router
                program_decision = await self.program_router.determine_program(
                    customer_data=customer_data_dict,
                    initial_message="",  # Sin mensaje inicial por ahora
                    conversation_context=None
                )
                
                # Usar la recomendación del router
                if program_decision.recommended_program == "HYBRID":
                    # Para casos híbridos, defaultear a PRIME si es menor de 50, LONGEVITY si es mayor
                    customer_age = customer_data_dict.get("age")
                    if customer_age and customer_age >= 50:
                        program_type = "LONGEVITY"
                    else:
                        program_type = "PRIME"
                    logger.info(f"Caso híbrido detectado, asignando {program_type} basado en edad")
                else:
                    program_type = program_decision.recommended_program
                
                logger.info(
                    f"Programa detectado automáticamente: {program_type} "
                    f"(confianza: {program_decision.confidence_score:.2f}, "
                    f"reasoning: {program_decision.reasoning})"
                )
            else:
                logger.info(f"Usando programa especificado manualmente: {program_type}")
            
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
            
            # Verificar si debemos cambiar de programa basado en nueva información
            await self._check_program_switch(message_text, state)
            
            # Verificar si debemos forzar análisis de perfil en los primeros 60 segundos
            await self._check_forced_profile_analysis(state)
            
            # Realizar análisis emocional del mensaje del usuario
            emotional_profile = await self._analyze_emotional_state(message_text, conversation_id, state)
            
            # Analizar personalidad del usuario
            personality_profile = await self._analyze_personality(conversation_id, state, emotional_profile)
            
            # Generar respuesta empática usando el motor de empatía
            empathic_response = await self._generate_empathic_response(
                emotional_profile, personality_profile, state, message_text
            )
            
            # Procesar mensaje con el agente usando contexto emocional
            response_message = await self._process_with_agent(message_text, state, {
                'emotional_profile': emotional_profile,
                'personality_profile': personality_profile,
                'empathic_guidance': empathic_response
            })
            
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
            
            # Generar audio para la respuesta usando multi-voice service
            audio_response = await self._generate_adaptive_audio(
                response_message, state, emotional_profile, personality_profile, empathic_response
            )
            
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
    
    async def _process_with_agent(self, message_text: str, state: ConversationState, emotional_context: Optional[Dict[str, Any]] = None) -> str:
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
            
            # Añadir contexto emocional si está disponible
            if emotional_context:
                context.update({
                    "emotional_intelligence": emotional_context
                })
            
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
        """Generar audio básico para el texto dado (método de fallback)."""
        try:
            # Verificar si la síntesis de voz está habilitada
            if not self.platform_context.conversation_config.enable_voice:
                # Retornar audio vacío si no está habilitado
                return BytesIO()
            
            # Generar audio usando ElevenLabs básico
            audio_response = await asyncio.to_thread(
                lambda: voice_engine.text_to_speech(text)
            )
            
            return audio_response
            
        except Exception as e:
            logger.error(f"Error generando audio: {e}")
            # Retornar audio vacío en caso de error
            return BytesIO()
    
    async def _generate_adaptive_audio(
        self,
        text: str,
        state: ConversationState,
        emotional_profile: Any,
        personality_profile: Any,
        empathy_response: Any
    ) -> BytesIO:
        """
        Generar audio adaptativo usando el sistema multi-voice.
        
        Args:
            text: Texto a convertir a voz
            state: Estado actual de la conversación
            emotional_profile: Perfil emocional del usuario
            personality_profile: Perfil de personalidad del usuario
            empathy_response: Respuesta empática generada
            
        Returns:
            BytesIO: Stream de audio adaptativo
        """
        try:
            # Verificar si la síntesis de voz está habilitada
            if not self.platform_context.conversation_config.enable_voice:
                return BytesIO()
            
            # Determinar sección de venta basada en el estado de conversación
            sales_section = self._determine_sales_section(state)
            
            # Preparar contexto para multi-voice
            voice_context = {
                "conversation_id": state.id,
                "program_type": state.program_type,
                "voice_gender": "male",  # TODO: Could be configurable per customer
                "platform_source": self.platform_context.platform_info.source.value if self.platform_context else "unknown",
                "triggers": empathy_response.intro_phrase[:50] if empathy_response else ""
            }
            
            # Generar respuesta adaptativa
            multi_voice_response = await self.multi_voice_service.generate_adaptive_voice_response(
                text=text,
                sales_section=sales_section,
                emotional_profile=emotional_profile,
                personality_profile=personality_profile,
                empathy_response=empathy_response,
                context=voice_context
            )
            
            # Guardar insights de voz en el estado
            if not hasattr(state, 'voice_insights'):
                state.voice_insights = []
            
            state.voice_insights.append({
                'timestamp': datetime.now().isoformat(),
                'sales_section': sales_section.value,
                'voice_persona': multi_voice_response.voice_config_used.persona.value,
                'emotional_alignment': multi_voice_response.emotional_alignment,
                'personality_match': multi_voice_response.personality_match,
                'adaptation_reason': multi_voice_response.adaptation_reason
            })
            
            logger.info(
                f"Audio adaptativo generado: {multi_voice_response.voice_config_used.persona.value}, "
                f"alineación emocional: {multi_voice_response.emotional_alignment:.2f}"
            )
            
            return multi_voice_response.audio_stream
            
        except Exception as e:
            logger.error(f"Error generando audio adaptativo: {e}")
            # Fallback a audio básico
            return await self._generate_audio(text)
    
    def _determine_sales_section(self, state: ConversationState) -> SalesSection:
        """
        Determinar la sección de venta actual basada en el estado de conversación.
        
        Args:
            state: Estado de la conversación
            
        Returns:
            SalesSection: Sección identificada
        """
        try:
            # Analizar número de mensajes
            message_count = len(state.messages)
            
            # Analizar fase actual si está disponible
            current_phase = getattr(state, 'phase', 'active')
            
            # Determinar sección basada en múltiples factores
            if message_count <= 2:
                return SalesSection.OPENING
            elif current_phase == "human_transfer":
                return SalesSection.FOLLOW_UP
            elif current_phase == "ended":
                return SalesSection.CLOSING
            elif message_count <= 6:
                return SalesSection.DISCOVERY
            elif message_count <= 10:
                # Buscar indicadores de objeciones en mensajes recientes
                recent_messages = [msg.content.lower() for msg in state.messages[-3:] if msg.role == "user"]
                objection_keywords = ["pero", "no estoy seguro", "caro", "precio", "no puedo", "problema"]
                
                if any(keyword in " ".join(recent_messages) for keyword in objection_keywords):
                    return SalesSection.OBJECTION_HANDLING
                else:
                    return SalesSection.PRESENTATION
            elif message_count <= 15:
                # Fase avanzada - buscar indicadores de cierre
                recent_messages = [msg.content.lower() for msg in state.messages[-3:] if msg.role == "user"]
                closing_keywords = ["listo", "quiero", "empezar", "cuando", "cómo procedo"]
                
                if any(keyword in " ".join(recent_messages) for keyword in closing_keywords):
                    return SalesSection.CLOSING
                else:
                    return SalesSection.OBJECTION_HANDLING
            else:
                return SalesSection.CLOSING
                
        except Exception as e:
            logger.error(f"Error determinando sección de venta: {e}")
            return SalesSection.DISCOVERY  # Default seguro
    
    def _generate_closing_message(self, end_reason: str) -> str:
        """Generar mensaje de cierre basado en la razón."""
        closing_messages = {
            'rejection_detected': "Entiendo que no es el momento adecuado. Gracias por tu tiempo y estaremos aquí cuando estés listo.",
            'timeout': "Ha sido un placer conversar contigo. Si tienes más preguntas, no dudes en contactarnos.",
            'intent_achieved': "Perfecto, hemos cubierto todo lo que necesitabas. ¡Gracias por tu tiempo!",
            'default': "Gracias por conversar con nosotros. ¡Que tengas un excelente día!"
        }
        
        return closing_messages.get(end_reason, closing_messages['default'])
    
    async def _analyze_emotional_state(
        self, 
        message_text: str, 
        conversation_id: str, 
        state: ConversationState
    ) -> Any:
        """
        Analizar el estado emocional del usuario en el mensaje actual.
        
        Args:
            message_text: Texto del mensaje del usuario
            conversation_id: ID de la conversación
            state: Estado actual de la conversación
            
        Returns:
            EmotionalProfile: Perfil emocional del usuario
        """
        try:
            # Preparar historial de conversación para contexto
            conversation_history = [
                {"role": msg.role, "content": msg.content}
                for msg in state.messages[-10:]  # Últimos 10 mensajes para contexto
            ]
            
            # Analizar estado emocional
            emotional_profile = await self.emotional_intelligence_service.analyze_emotional_state(
                messages=conversation_history,
                customer_profile=state.customer_data if hasattr(state, 'customer_data') else None
            )
            
            # Guardar en el estado de la conversación
            if not hasattr(state, 'emotional_journey'):
                state.emotional_journey = []
            
            state.emotional_journey.append({
                'timestamp': datetime.now().isoformat(),
                'emotional_state': emotional_profile.primary_emotion.value,
                'confidence': emotional_profile.confidence,
                'secondary_emotions': {k.value: v for k, v in emotional_profile.secondary_emotions.items()},
                'triggers': emotional_profile.triggers,
                'stability_score': emotional_profile.stability_score
            })
            
            logger.info(f"Estado emocional analizado para {conversation_id}: {emotional_profile.primary_emotion.value}")
            return emotional_profile
            
        except Exception as e:
            logger.error(f"Error analizando estado emocional: {e}")
            # Retornar perfil emocional neutral por defecto
            from src.integrations.elevenlabs.advanced_voice import EmotionalState
            from src.services.emotional_intelligence_service import EmotionalProfile
            return EmotionalProfile(
                primary_emotion=EmotionalState.NEUTRAL,
                confidence=0.5,
                secondary_emotions={},
                emotional_journey=[],
                triggers=[],
                emotional_velocity=0.0,
                stability_score=1.0
            )
    
    async def _analyze_personality(
        self, 
        conversation_id: str, 
        state: ConversationState,
        emotional_profile: Any
    ) -> Any:
        """
        Analizar la personalidad del usuario basándose en la conversación.
        
        Args:
            conversation_id: ID de la conversación
            state: Estado actual de la conversación
            emotional_profile: Perfil emocional del usuario
            
        Returns:
            PersonalityProfile: Perfil de personalidad del usuario
        """
        try:
            # Preparar mensajes de conversación
            conversation_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in state.messages
            ]
            
            # Analizar personalidad
            personality_profile = await self.adaptive_personality_service.analyze_personality(
                messages=conversation_messages,
                customer_profile=state.customer_data if hasattr(state, 'customer_data') else None,
                behavioral_data=None
            )
            
            # Guardar en el estado de la conversación
            state.personality_insights = {
                'communication_style': personality_profile.communication_style.value,
                'formality_preference': personality_profile.formality_preference,
                'detail_preference': personality_profile.detail_preference,
                'pace_preference': personality_profile.pace_preference,
                'confidence_score': personality_profile.confidence_score
            }
            
            logger.info(f"Personalidad analizada para {conversation_id}: {personality_profile.communication_style.value}")
            return personality_profile
            
        except Exception as e:
            logger.error(f"Error analizando personalidad: {e}")
            # Retornar perfil de personalidad neutral por defecto
            from src.services.adaptive_personality_service import (
                PersonalityProfile, PersonalityTrait, CommunicationStyle
            )
            return PersonalityProfile(
                communication_style=CommunicationStyle.AMIABLE,
                primary_traits={
                    PersonalityTrait.OPENNESS: 0.5,
                    PersonalityTrait.CONSCIENTIOUSNESS: 0.5,
                    PersonalityTrait.EXTRAVERSION: 0.5,
                    PersonalityTrait.AGREEABLENESS: 0.5,
                    PersonalityTrait.NEUROTICISM: 0.5
                },
                decision_style="collaborative",
                risk_tolerance=0.5,
                pace_preference="moderate",
                detail_orientation=0.5,
                social_preference="balanced"
            )
    
    async def _generate_empathic_response(
        self, 
        emotional_profile: Any, 
        personality_profile: Any,
        state: ConversationState,
        user_message: str
    ) -> Any:
        """
        Generar respuesta empática basada en el perfil emocional y de personalidad.
        
        Args:
            emotional_profile: Perfil emocional del usuario
            personality_profile: Perfil de personalidad del usuario
            state: Estado actual de la conversación
            user_message: Mensaje actual del usuario
            
        Returns:
            EmpathicResponse: Respuesta empática generada
        """
        try:
            # Preparar contexto de conversación
            conversation_context = {
                'user_message': user_message,
                'conversation_history': [
                    {"role": msg.role, "content": msg.content}
                    for msg in state.messages[-5:]
                ],
                'program_type': state.program_type,
                'conversation_phase': getattr(state, 'phase', 'active'),
                'personality_profile': personality_profile,
                'platform_context': self.platform_context.platform_info.source.value if self.platform_context else 'unknown'
            }
            
            # Determinar objetivo de ventas basado en el programa
            sales_objective = f"Promocionar {state.program_type} de manera empática y personalizada"
            
            # Obtener respuestas previas para evitar repetición
            previous_responses = [
                msg.content for msg in state.messages[-3:] 
                if msg.role == "assistant"
            ]
            
            # Generar respuesta empática
            empathic_response = await self.empathy_engine_service.generate_empathetic_response(
                emotional_profile=emotional_profile,
                original_message=user_message,
                context=conversation_context,
                cultural_context=None  # Could be inferred from customer data
            )
            
            # Guardar insights empáticos en el estado
            if not hasattr(state, 'empathy_insights'):
                state.empathy_insights = []
            
            state.empathy_insights.append({
                'timestamp': datetime.now().isoformat(),
                'technique': empathic_response.technique_used.value,
                'emotional_tone': empathic_response.emotional_tone,
                'voice_persona': empathic_response.voice_persona.value,
                'intro_phrase': empathic_response.intro_phrase[:100]  # Truncate for storage
            })
            
            logger.info(f"Respuesta empática generada para {state.id}: {empathic_response.technique_used.value}")
            return empathic_response
            
        except Exception as e:
            logger.error(f"Error generando respuesta empática: {e}")
            # Retornar respuesta empática básica por defecto
            from src.services.empathy_engine_service import EmpathyTechnique, EmpathyResponse
            from src.integrations.elevenlabs.advanced_voice import VoicePersona
            return EmpathyResponse(
                intro_phrase="Entiendo tu perspectiva",
                core_message="Es natural que tengas esas preocupaciones",
                closing_phrase="¿Hay algo específico que te preocupa?",
                technique_used=EmpathyTechnique.VALIDATION,
                voice_persona=VoicePersona.CONSULTANT,
                emotional_tone="empático y comprensivo"
            )
    
    async def _check_program_switch(self, message_text: str, state: ConversationState) -> None:
        """
        Verificar si debemos cambiar de programa basado en nueva información del usuario.
        
        Args:
            message_text: Nuevo mensaje del usuario
            state: Estado actual de la conversación
        """
        try:
            # Solo verificar cambio después de los primeros mensajes para evitar switches prematuros
            if len(state.messages) < 4:
                return
            
            # Obtener historial de conversación para contexto
            conversation_history = [
                {"role": msg.role, "content": msg.content}
                for msg in state.messages[-5:]  # Últimos 5 mensajes para contexto
            ]
            
            # Verificar si debemos cambiar de programa
            should_switch, new_decision = await self.program_router.should_switch_program(
                current_program=state.program_type,
                new_information=message_text,
                conversation_history=conversation_history
            )
            
            if should_switch and new_decision:
                old_program = state.program_type
                state.program_type = new_decision.recommended_program
                
                # Añadir mensaje explicativo del cambio
                switch_message = (
                    f"Entiendo mejor tus necesidades ahora. Basándome en lo que me has contado, "
                    f"creo que NGX {new_decision.recommended_program} sería perfecto para ti. "
                    f"Permíteme contarte más sobre este programa específico."
                )
                
                state.add_message(role="assistant", content=switch_message)
                
                # Guardar información del switch para analytics
                if not hasattr(state, 'program_switches'):
                    state.program_switches = []
                
                state.program_switches.append({
                    'timestamp': datetime.now().isoformat(),
                    'from_program': old_program,
                    'to_program': new_decision.recommended_program,
                    'confidence': new_decision.confidence_score,
                    'reasoning': new_decision.reasoning,
                    'trigger_message': message_text[:100]  # Primeros 100 caracteres
                })
                
                logger.info(
                    f"Programa cambiado automáticamente de {old_program} a {new_decision.recommended_program} "
                    f"en conversación {state.id} (confianza: {new_decision.confidence_score:.2f})"
                )
                
        except Exception as e:
            logger.error(f"Error verificando cambio de programa: {e}")
            # No hacer nada en caso de error - continuar con programa actual
    
    async def _check_forced_profile_analysis(self, state: ConversationState) -> None:
        """
        Verificar si debemos forzar análisis de perfil en los primeros 60 segundos.
        
        Args:
            state: Estado actual de la conversación
        """
        try:
            # Solo intentar si tenemos un agente unificado
            if not self._current_agent or not hasattr(self._current_agent, 'should_force_profile_analysis'):
                return
            
            # Verificar si debemos forzar análisis
            if not self._current_agent.should_force_profile_analysis():
                return
            
            logger.info(f"Iniciando análisis forzado de perfil para conversación {state.id}")
            
            # Obtener contexto para análisis forzado
            analysis_context = self._current_agent.get_profile_analysis_context()
            
            # Preparar transcripción completa para análisis
            conversation_transcript = "\n".join([
                f"{msg.role}: {msg.content}" 
                for msg in state.messages[-10:]  # Últimos 10 mensajes
            ])
            
            # Realizar análisis usando las herramientas adaptativas existentes
            try:
                # Usar la herramienta de análisis de perfil del cliente
                from src.agents.tools.adaptive_tools import analyze_customer_profile
                
                analysis_result = await analyze_customer_profile(
                    transcript=conversation_transcript,
                    customer_age=state.customer_data.get('age') if hasattr(state, 'customer_data') else None
                )
                
                # Procesar resultados en el agente
                self._current_agent.process_forced_analysis_result(analysis_result)
                
                # Guardar información del análisis forzado en el estado
                if not hasattr(state, 'forced_analysis_log'):
                    state.forced_analysis_log = []
                
                state.forced_analysis_log.append({
                    'timestamp': datetime.now().isoformat(),
                    'trigger_time': analysis_context['elapsed_seconds'],
                    'previous_confidence': analysis_context['current_confidence'],
                    'analysis_result': {
                        'recommended_program': analysis_result.get('recommended_program', 'UNKNOWN'),
                        'confidence_score': analysis_result.get('confidence_score', 0.0),
                        'analysis_summary': analysis_result.get('analysis_summary', 'Sin resumen disponible')
                    }
                })
                
                logger.info(
                    f"Análisis forzado completado para conversación {state.id}: "
                    f"{analysis_result.get('recommended_program', 'UNKNOWN')} "
                    f"(confianza: {analysis_result.get('confidence_score', 0.0):.2f})"
                )
                
            except Exception as analysis_error:
                logger.error(f"Error en análisis forzado: {analysis_error}")
                # Fallback: usar análisis básico del router
                await self._fallback_forced_analysis(state, analysis_context)
                
        except Exception as e:
            logger.error(f"Error verificando análisis forzado: {e}")
    
    async def _fallback_forced_analysis(self, state: ConversationState, analysis_context: Dict[str, Any]) -> None:
        """
        Análisis forzado de fallback usando el program router.
        
        Args:
            state: Estado de la conversación
            analysis_context: Contexto del análisis
        """
        try:
            # Crear mensaje combinado de los últimos intercambios
            recent_messages = [msg.content for msg in state.messages[-6:] if msg.role == "user"]
            combined_message = " ".join(recent_messages)
            
            # Usar el program router para análisis
            customer_data_dict = {
                "id": state.customer_id,
                "name": state.customer_data.get('name', 'Cliente') if hasattr(state, 'customer_data') else 'Cliente',
                "age": state.customer_data.get('age') if hasattr(state, 'customer_data') else None,
                "interests": state.customer_data.get('interests', []) if hasattr(state, 'customer_data') else []
            }
            
            # Obtener historial para contexto
            conversation_history = [
                {"role": msg.role, "content": msg.content}
                for msg in state.messages[-5:]
            ]
            
            program_decision = await self.program_router.determine_program(
                customer_data=customer_data_dict,
                initial_message=combined_message,
                conversation_context={'forced_analysis': True, 'elapsed_seconds': analysis_context['elapsed_seconds']}
            )
            
            # Crear resultado simulado para el agente
            fallback_result = {
                'recommended_program': program_decision.recommended_program,
                'confidence_score': program_decision.confidence_score,
                'analysis_summary': f"Análisis de fallback - {program_decision.reasoning}"
            }
            
            # Procesar en el agente
            self._current_agent.process_forced_analysis_result(fallback_result)
            
            logger.info(
                f"Análisis forzado de fallback completado: {program_decision.recommended_program} "
                f"(confianza: {program_decision.confidence_score:.2f})"
            )
            
        except Exception as e:
            logger.error(f"Error en análisis forzado de fallback: {e}") 