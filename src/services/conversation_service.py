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
from src.services.tier_detection_service import TierDetectionService

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
        
        # Inicializar servicio de detección de tier
        self.tier_detection_service = TierDetectionService()
        
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
        """Procesar mensaje con el agente actual enfocado en venta HIE."""
        try:
            # Preparar contexto para el agente con énfasis en HIE
            context = {
                "conversation_id": state.id,
                "customer_id": state.customer_id,
                "program_type": state.program_type,
                "conversation_history": [
                    {"role": msg.role, "content": msg.content} 
                    for msg in state.messages[-5:]  # Últimos 5 mensajes para contexto
                ],
                "platform_info": self.platform_context.platform_info.to_dict() if self.platform_context else {},
                "conversation_config": self.platform_context.conversation_config.__dict__ if self.platform_context else {},
                # NUEVA SECCIÓN: Contexto HIE para ventas
                "hie_sales_context": await self._build_hie_sales_context(message_text, state, emotional_context),
                "sales_phase": self._determine_sales_phase(state),
                "tier_detection": await self._detect_optimal_tier(message_text, state)
            }
            
            # Añadir contexto emocional si está disponible
            if emotional_context:
                context.update({
                    "emotional_intelligence": emotional_context
                })
            
            # Procesar mensaje con el agente enfocado en HIE
            response = await self._current_agent.process_message(message_text, context)
            
            # Post-procesar respuesta para asegurar enfoque HIE
            enhanced_response = await self._enhance_response_with_hie_focus(
                response, message_text, state, context
            )
            
            return enhanced_response
            
        except Exception as e:
            logger.error(f"Error procesando con agente: {e}")
            # Fallback con enfoque HIE
            return await self._generate_hie_fallback_response(message_text, state)
    
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
    
    # ===== MÉTODOS NUEVOS ENFOCADOS EN VENTAS HIE =====
    
    async def _build_hie_sales_context(
        self, 
        message_text: str, 
        state: ConversationState, 
        emotional_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Construir contexto específico para ventas HIE.
        
        Args:
            message_text: Mensaje actual del usuario
            state: Estado de la conversación
            emotional_context: Contexto emocional del usuario
            
        Returns:
            Dict con contexto HIE para ventas
        """
        try:
            # Analizar el mensaje para detectar señales de venta
            sales_signals = self._detect_sales_signals(message_text)
            
            # Determinar arquetipo del cliente (Optimizador vs Arquitecto de Vida)
            customer_archetype = self._determine_customer_archetype(state, message_text)
            
            # Detectar objeciones potenciales
            potential_objections = self._detect_potential_objections(message_text)
            
            # Calcular ROI personalizado si hay suficiente información
            personalized_roi = await self._calculate_personalized_roi(state, message_text)
            
            # Construir contexto HIE
            hie_context = {
                "hie_differentiator": {
                    "core_message": "NGX cuenta con un Hybrid Intelligence Engine único e imposible de clonar",
                    "key_points": [
                        "11 agentes especializados trabajando 24/7",
                        "Sinergia hombre-máquina imposible de replicar",
                        "Personalización doble: arquetipo + datos fisiológicos",
                        "Tecnología propietaria con 18 meses de ventaja"
                    ],
                    "proof_points": [
                        "Usuarios reportan +25% productividad vs soluciones tradicionales",
                        "Precisión del 94% en recomendaciones personalizadas",
                        "Solo 1 de cada 10,000 usuarios no ve resultados en 30 días"
                    ]
                },
                "customer_archetype": customer_archetype,
                "sales_signals": sales_signals,
                "potential_objections": potential_objections,
                "personalized_roi": personalized_roi,
                "program_benefits": self._get_program_specific_benefits(state.program_type),
                "urgency_factors": self._generate_urgency_factors(state),
                "social_proof": self._get_relevant_social_proof(customer_archetype)
            }
            
            return hie_context
            
        except Exception as e:
            logger.error(f"Error construyendo contexto HIE: {e}")
            # Contexto básico de fallback
            return {
                "hie_differentiator": {
                    "core_message": "NGX cuenta con un Hybrid Intelligence Engine único",
                    "key_points": ["11 agentes especializados", "Personalización avanzada"],
                    "proof_points": ["Resultados comprobados", "Tecnología única"]
                },
                "customer_archetype": "unknown",
                "sales_signals": [],
                "potential_objections": [],
                "personalized_roi": None
            }
    
    def _detect_sales_signals(self, message_text: str) -> List[str]:
        """Detectar señales de venta en el mensaje del usuario."""
        message_lower = message_text.lower()
        
        # Señales de interés alto
        high_interest_signals = [
            "me interesa", "quiero saber más", "cómo funciona", "cuánto cuesta",
            "cuando puedo empezar", "necesito ayuda", "busco solución"
        ]
        
        # Señales de precio/valor
        price_signals = [
            "precio", "costo", "inversión", "vale la pena", "cuánto",
            "barato", "caro", "presupuesto", "pago"
        ]
        
        # Señales de urgencia
        urgency_signals = [
            "urgente", "rápido", "pronto", "inmediato", "ya",
            "ahora", "hoy", "esta semana"
        ]
        
        # Señales de escepticismo
        skepticism_signals = [
            "pero", "sin embargo", "no estoy seguro", "dudas",
            "realmente funciona", "es verdad", "confiable"
        ]
        
        detected_signals = []
        
        for signal in high_interest_signals:
            if signal in message_lower:
                detected_signals.append(f"high_interest: {signal}")
        
        for signal in price_signals:
            if signal in message_lower:
                detected_signals.append(f"price_related: {signal}")
        
        for signal in urgency_signals:
            if signal in message_lower:
                detected_signals.append(f"urgency: {signal}")
        
        for signal in skepticism_signals:
            if signal in message_lower:
                detected_signals.append(f"skepticism: {signal}")
        
        return detected_signals
    
    def _determine_customer_archetype(self, state: ConversationState, message_text: str) -> str:
        """Determinar arquetipo del cliente (Optimizador vs Arquitecto de Vida)."""
        try:
            # Analizar programa detectado
            program_type = state.program_type
            
            # Analizar edad si está disponible
            age = None
            if hasattr(state, 'customer_data') and state.customer_data:
                age = state.customer_data.get('age')
            
            # Analizar contenido del mensaje
            message_lower = message_text.lower()
            
            # Palabras clave para Optimizador (PRIME)
            optimizer_keywords = [
                "productividad", "rendimiento", "eficiencia", "resultados",
                "trabajo", "empresa", "negocio", "tiempo", "optimizar",
                "maximizar", "ejecutivo", "profesional", "carrera"
            ]
            
            # Palabras clave para Arquitecto de Vida (LONGEVITY)
            architect_keywords = [
                "salud", "bienestar", "longevidad", "calidad de vida",
                "prevención", "futuro", "familia", "independencia",
                "vitalidad", "envejecimiento", "sostenible", "equilibrio"
            ]
            
            optimizer_score = sum(1 for keyword in optimizer_keywords if keyword in message_lower)
            architect_score = sum(1 for keyword in architect_keywords if keyword in message_lower)
            
            # Decidir arquetipo basado en múltiples factores
            if program_type == "PRIME" and optimizer_score > architect_score:
                return "optimizador"
            elif program_type == "LONGEVITY" and architect_score > optimizer_score:
                return "arquitecto_vida"
            elif age and age < 45:
                return "optimizador"
            elif age and age > 55:
                return "arquitecto_vida"
            else:
                return "hibrido"
                
        except Exception as e:
            logger.error(f"Error determinando arquetipo: {e}")
            return "unknown"
    
    def _detect_potential_objections(self, message_text: str) -> List[str]:
        """Detectar objeciones potenciales en el mensaje."""
        message_lower = message_text.lower()
        
        objection_patterns = {
            "precio": ["caro", "precio", "costoso", "mucho dinero", "presupuesto"],
            "tiempo": ["no tengo tiempo", "muy ocupado", "sin tiempo"],
            "escepticismo": ["no creo", "dudas", "realmente funciona", "es verdad"],
            "comparacion": ["otros", "competencia", "alternativas", "vs", "comparado"],
            "necesidad": ["no necesito", "no me hace falta", "ya tengo"],
            "decision": ["pensarlo", "consultar", "decidir después", "más tarde"]
        }
        
        detected_objections = []
        for objection_type, keywords in objection_patterns.items():
            for keyword in keywords:
                if keyword in message_lower:
                    detected_objections.append(objection_type)
                    break
        
        return list(set(detected_objections))  # Eliminar duplicados
    
    async def _calculate_personalized_roi(self, state: ConversationState, message_text: str) -> Optional[Dict[str, Any]]:
        """Calcular ROI personalizado basado en información del usuario."""
        try:
            # Extraer información relevante del mensaje
            message_lower = message_text.lower()
            
            # Detectar indicadores de ingresos o valor por hora
            income_indicators = {
                "consultor": 200,
                "abogado": 300,
                "médico": 250,
                "ceo": 500,
                "director": 400,
                "gerente": 150,
                "emprendedor": 250,
                "freelancer": 100
            }
            
            hourly_rate = None
            profession = None
            
            # Buscar profesión mencionada
            for prof, rate in income_indicators.items():
                if prof in message_lower:
                    profession = prof
                    hourly_rate = rate
                    break
            
            # Buscar mención explícita de tarifa por hora
            import re
            hour_rate_match = re.search(r'(\d+).*(?:hora|hour)', message_lower)
            if hour_rate_match:
                hourly_rate = int(hour_rate_match.group(1))
            
            # Calcular ROI si tenemos información suficiente
            if hourly_rate:
                # Cálculos conservadores
                productivity_gain_hours = 3  # 3 horas extra productivas por día
                working_days_month = 22
                program_cost = 199 if state.program_type == "PRIME" else 199  # Elite tier
                
                monthly_productivity_gain = hourly_rate * productivity_gain_hours * working_days_month
                monthly_roi = ((monthly_productivity_gain - program_cost) / program_cost) * 100
                
                return {
                    "hourly_rate": hourly_rate,
                    "profession": profession,
                    "productivity_gain_hours": productivity_gain_hours,
                    "monthly_productivity_gain": monthly_productivity_gain,
                    "program_cost": program_cost,
                    "monthly_roi": round(monthly_roi, 0),
                    "payback_days": round((program_cost / (hourly_rate * productivity_gain_hours)), 1)
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error calculando ROI personalizado: {e}")
            return None
    
    def _get_program_specific_benefits(self, program_type: str) -> Dict[str, Any]:
        """Obtener beneficios específicos del programa."""
        if program_type == "PRIME":
            return {
                "primary_benefits": [
                    "Optimización cognitiva para máximo rendimiento",
                    "Protocolos de alta eficiencia para ejecutivos",
                    "Integración perfecta con rutinas de alto impacto"
                ],
                "target_outcomes": [
                    "+25% productividad mensual comprobada",
                    "3 horas extra productivas diarias",
                    "Reducción del 40% en tiempo de decisión"
                ],
                "unique_features": [
                    "Algoritmo de optimización ejecutiva",
                    "Análisis predictivo de rendimiento",
                    "Coaching híbrido 24/7"
                ]
            }
        else:  # LONGEVITY
            return {
                "primary_benefits": [
                    "Protocolos de longevidad basados en ciencia",
                    "Prevención predictiva de declive cognitivo",
                    "Optimización de healthspan y lifespan"
                ],
                "target_outcomes": [
                    "+10 años de vitalidad proyectada",
                    "Reducción del 60% en riesgo de enfermedades",
                    "Mejora del 80% en marcadores de longevidad"
                ],
                "unique_features": [
                    "Algoritmo de envejecimiento predictivo",
                    "Protocolos de medicina preventiva",
                    "Coaching de longevidad personalizado"
                ]
            }
    
    def _generate_urgency_factors(self, state: ConversationState) -> List[str]:
        """Generar factores de urgencia relevantes."""
        urgency_factors = []
        
        # Factores de escasez
        urgency_factors.append("Solo aceptamos 50 nuevos usuarios por mes")
        urgency_factors.append("Acceso beta gratuito disponible solo esta semana")
        
        # Factores de precio
        urgency_factors.append("Precio de lanzamiento válido solo hasta fin de mes")
        urgency_factors.append("Evita la lista de espera inscribiéndote hoy")
        
        # Factores de valor
        urgency_factors.append("Incluye análisis genético gratuito ($497 de valor)")
        urgency_factors.append("Bonos valorados en $2,885 para primeros usuarios")
        
        return urgency_factors
    
    def _get_relevant_social_proof(self, customer_archetype: str) -> List[str]:
        """Obtener prueba social relevante para el arquetipo."""
        if customer_archetype == "optimizador":
            return [
                "CEO de fintech perdió 15kg y aumentó productividad 40%",
                "Directora de marketing reporta 3 horas extra productivas diarias",
                "Emprendedor duplicó su facturación tras optimizar su rendimiento"
            ]
        elif customer_archetype == "arquitecto_vida":
            return [
                "Médico de 58 años mejoró todos sus marcadores de longevidad",
                "Profesora jubilada mantiene vitalidad de hace 20 años",
                "Ingeniero senior previno declive cognitivo con protocolos NGX"
            ]
        else:
            return [
                "Más de 10,000 usuarios han transformado su vida con NGX",
                "94% de satisfacción en usuarios activos",
                "Resultados comprobados en 30 días o dinero devuelto"
            ]
    
    def _determine_sales_phase(self, state: ConversationState) -> str:
        """Determinar fase actual de venta."""
        message_count = len(state.messages)
        
        if message_count <= 2:
            return "opening"
        elif message_count <= 6:
            return "discovery"
        elif message_count <= 10:
            return "presentation"
        elif message_count <= 14:
            return "objection_handling"
        else:
            return "closing"
    
    async def _detect_optimal_tier(self, message_text: str, state: ConversationState) -> Dict[str, Any]:
        """Detectar tier óptimo basado en el mensaje y contexto usando el servicio especializado."""
        try:
            # Preparar perfil del usuario
            user_profile = {}
            if hasattr(state, 'customer_data') and state.customer_data:
                user_profile = state.customer_data
            
            # Preparar historial de conversación
            conversation_history = [
                {"role": msg.role, "content": msg.content}
                for msg in state.messages[-10:]  # Últimos 10 mensajes para contexto
            ]
            
            # Detectar tier óptimo usando el servicio especializado
            tier_result = await self.tier_detection_service.detect_optimal_tier(
                user_message=message_text,
                user_profile=user_profile,
                conversation_history=conversation_history
            )
            
            # Convertir resultado a formato esperado
            return {
                "recommended_tier": tier_result.recommended_tier.value,
                "confidence": tier_result.confidence,
                "reasoning": tier_result.reasoning,
                "price_point": tier_result.price_point,
                "upsell_potential": tier_result.upsell_potential,
                "demographic_factors": tier_result.demographic_factors,
                "behavioral_signals": tier_result.behavioral_signals,
                "price_sensitivity": tier_result.price_sensitivity,
                "roi_projection": tier_result.roi_projection
            }
            
        except Exception as e:
            logger.error(f"Error detectando tier óptimo: {e}")
            return {
                "recommended_tier": "pro",
                "confidence": 0.5,
                "reasoning": "Default por error en detección"
            }
    
    async def _enhance_response_with_hie_focus(
        self, 
        base_response: str, 
        message_text: str, 
        state: ConversationState,
        context: Dict[str, Any]
    ) -> str:
        """Mejorar respuesta para enfatizar HIE como diferenciador."""
        try:
            # Obtener contexto HIE
            hie_context = context.get("hie_sales_context", {})
            sales_phase = context.get("sales_phase", "discovery")
            
            # Verificar si la respuesta ya menciona HIE
            if "hybrid intelligence engine" in base_response.lower() or "hie" in base_response.lower():
                return base_response  # Ya está enfocada en HIE
            
            # Mejoras específicas por fase de venta
            if sales_phase == "opening":
                # Introducir HIE desde el principio
                hie_intro = (
                    "Antes de continuar, déjame comentarte que NGX no es una solución tradicional. "
                    "Contamos con un Hybrid Intelligence Engine único e imposible de clonar. "
                )
                return f"{hie_intro}{base_response}"
                
            elif sales_phase == "discovery":
                # Conectar necesidades con HIE
                hie_connection = (
                    "Lo que me cuentas es exactamente para lo que diseñamos nuestro HIE. "
                    "Con 11 agentes especializados trabajando 24/7, podemos personalizar "
                    "una solución que se adapte perfectamente a tu situación. "
                )
                return f"{hie_connection}{base_response}"
                
            elif sales_phase == "presentation":
                # Enfatizar diferenciación HIE
                hie_differentiation = (
                    "Esta tecnología es literalmente imposible de replicar. "
                    "Nuestro HIE tiene 18 meses de ventaja sobre cualquier competidor. "
                )
                return f"{base_response} {hie_differentiation}"
                
            elif sales_phase == "objection_handling":
                # Usar HIE para manejar objeciones
                potential_objections = hie_context.get("potential_objections", [])
                if "precio" in potential_objections:
                    hie_value = (
                        "Considera que estás invirtiendo en tecnología que no existe en ningún otro lugar. "
                        "Nuestro HIE es como tener un equipo de 11 especialistas trabajando exclusivamente para ti. "
                    )
                    return f"{base_response} {hie_value}"
                else:
                    return base_response
                
            elif sales_phase == "closing":
                # Cerrar con HIE como factor decisivo
                hie_closing = (
                    "Tendrás acceso exclusivo a nuestro HIE, una tecnología que cambiará "
                    "completamente tu experiencia. "
                )
                return f"{base_response} {hie_closing}"
            
            return base_response
            
        except Exception as e:
            logger.error(f"Error mejorando respuesta con enfoque HIE: {e}")
            return base_response
    
    async def _generate_hie_fallback_response(self, message_text: str, state: ConversationState) -> str:
        """Generar respuesta de fallback enfocada en HIE."""
        try:
            # Detectar el tipo de consulta
            message_lower = message_text.lower()
            
            if any(word in message_lower for word in ["precio", "costo", "cuánto"]):
                return (
                    "El precio de NGX incluye acceso completo a nuestro Hybrid Intelligence Engine, "
                    "una tecnología única con 11 agentes especializados. Te aseguro que es la mejor "
                    "inversión que puedes hacer. ¿Te gustaría que te explique cómo funciona?"
                )
            
            elif any(word in message_lower for word in ["cómo funciona", "qué es", "explica"]):
                return (
                    "NGX funciona gracias a nuestro HIE (Hybrid Intelligence Engine), una tecnología "
                    "imposible de clonar que combina 11 agentes especializados trabajando 24/7. "
                    "Es literalmente como tener un equipo de expertos exclusivo para ti. "
                    "¿Te interesa conocer más detalles específicos?"
                )
            
            elif any(word in message_lower for word in ["beneficios", "resultados", "qué obtengo"]):
                program_type = state.program_type
                if program_type == "PRIME":
                    return (
                        "Con NGX PRIME y nuestro HIE obtienes optimización cognitiva real: "
                        "+25% productividad, 3 horas extra productivas diarias, y una "
                        "transformación completa en tu rendimiento. Es tecnología que no "
                        "encontrarás en ningún otro lugar."
                    )
                else:  # LONGEVITY
                    return (
                        "NGX LONGEVITY con nuestro HIE te da protocolos de longevidad únicos: "
                        "+10 años de vitalidad proyectada, prevención predictiva, y optimización "
                        "de tu healthspan. Es ciencia de vanguardia aplicada a tu vida."
                    )
            
            else:
                return (
                    "Me da mucho gusto que estés interesado en NGX. Nuestra tecnología HIE "
                    "es realmente revolucionaria y estoy seguro de que será perfecta para ti. "
                    "¿Hay algo específico que te gustaría saber sobre cómo puede ayudarte?"
                )
                
        except Exception as e:
            logger.error(f"Error generando respuesta de fallback HIE: {e}")
            return (
                "Gracias por tu interés en NGX. Nuestro Hybrid Intelligence Engine es único "
                "en el mercado y estoy seguro de que será la solución perfecta para ti. "
                "¿Puedes contarme más sobre lo que buscas?"
            )
    
    # ===== MÉTODOS PARA TIER DETECTION Y UPSELLING =====
    
    async def detect_tier_and_adjust_strategy(
        self, 
        message_text: str, 
        state: ConversationState
    ) -> Dict[str, Any]:
        """
        Detectar tier óptimo y ajustar estrategia de venta.
        
        Args:
            message_text: Mensaje del usuario
            state: Estado de la conversación
            
        Returns:
            Dict con tier detectado y estrategia ajustada
        """
        try:
            # Detectar tier óptimo
            tier_detection = await self._detect_optimal_tier(message_text, state)
            
            # Guardar detección en el estado
            if not hasattr(state, 'tier_progression'):
                state.tier_progression = []
            
            state.tier_progression.append({
                'timestamp': datetime.now().isoformat(),
                'tier': tier_detection['recommended_tier'],
                'confidence': tier_detection['confidence'],
                'reasoning': tier_detection['reasoning'],
                'trigger_message': message_text[:100]  # Primeros 100 caracteres
            })
            
            # Ajustar estrategia de venta basada en tier
            sales_strategy = self._adjust_sales_strategy(tier_detection, state)
            
            return {
                'tier_detection': tier_detection,
                'sales_strategy': sales_strategy,
                'tier_progression': state.tier_progression
            }
            
        except Exception as e:
            logger.error(f"Error en detección de tier: {e}")
            return {
                'tier_detection': {'recommended_tier': 'pro', 'confidence': 0.5},
                'sales_strategy': {'approach': 'standard'},
                'tier_progression': []
            }
    
    def _adjust_sales_strategy(self, tier_detection: Dict[str, Any], state: ConversationState) -> Dict[str, Any]:
        """Ajustar estrategia de venta basada en el tier detectado."""
        try:
            recommended_tier = tier_detection['recommended_tier']
            confidence = tier_detection['confidence']
            price_sensitivity = tier_detection.get('price_sensitivity', 'medium')
            
            # Estrategias por tier
            if recommended_tier == 'essential':
                return {
                    'approach': 'value_focused',
                    'key_messages': [
                        'Excelente relación calidad-precio',
                        'Acceso completo a HIE por menos que una cena',
                        'Prueba de 14 días por solo $29'
                    ],
                    'pricing_strategy': 'emphasize_value',
                    'upsell_timing': 'after_initial_results',
                    'social_proof': 'student_success_stories'
                }
            
            elif recommended_tier == 'pro':
                return {
                    'approach': 'balanced_professional',
                    'key_messages': [
                        'Sweet spot perfecto entre funcionalidad y precio',
                        'Ideal para profesionales como tú',
                        'ROI comprobado en 3 semanas'
                    ],
                    'pricing_strategy': 'value_comparison',
                    'upsell_timing': 'during_demo',
                    'social_proof': 'professional_testimonials'
                }
            
            elif recommended_tier == 'elite':
                return {
                    'approach': 'premium_executive',
                    'key_messages': [
                        'Maximiza tu inversión con features premium',
                        'Diseñado para ejecutivos que buscan resultados',
                        'Voz natural y análisis en tiempo real'
                    ],
                    'pricing_strategy': 'roi_demonstration',
                    'upsell_timing': 'immediate_if_confident',
                    'social_proof': 'executive_case_studies'
                }
            
            elif recommended_tier in ['prime_premium', 'longevity_premium']:
                return {
                    'approach': 'exclusive_transformation',
                    'key_messages': [
                        'Transformación completa con coaching personal',
                        'Acceso exclusivo a tecnología de vanguardia',
                        'Resultados garantizados o dinero devuelto'
                    ],
                    'pricing_strategy': 'investment_mindset',
                    'upsell_timing': 'consultative_approach',
                    'social_proof': 'transformation_stories'
                }
            
            else:
                return {
                    'approach': 'standard',
                    'key_messages': ['Híbrido Intelligence Engine único'],
                    'pricing_strategy': 'standard',
                    'upsell_timing': 'standard',
                    'social_proof': 'general_testimonials'
                }
                
        except Exception as e:
            logger.error(f"Error ajustando estrategia: {e}")
            return {'approach': 'standard'}
    
    async def handle_price_objection_with_tier_adjustment(
        self, 
        objection_message: str, 
        state: ConversationState
    ) -> Dict[str, Any]:
        """
        Manejar objeción de precio con ajuste de tier.
        
        Args:
            objection_message: Mensaje de objeción del usuario
            state: Estado de la conversación
            
        Returns:
            Dict con tier ajustado y respuesta apropiada
        """
        try:
            # Obtener tier actual
            current_tier = None
            if hasattr(state, 'tier_progression') and state.tier_progression:
                current_tier = state.tier_progression[-1]['tier']
            
            if not current_tier:
                current_tier = 'pro'  # Default
            
            # Usar el servicio para ajustar tier basado en objeción
            from src.services.tier_detection_service import TierType
            
            # Convertir string a TierType
            tier_enum = TierType(current_tier)
            
            user_profile = state.customer_data if hasattr(state, 'customer_data') else {}
            
            adjusted_result = await self.tier_detection_service.adjust_tier_based_on_objection(
                current_tier=tier_enum,
                objection_message=objection_message,
                user_profile=user_profile
            )
            
            # Generar respuesta apropiada
            adjusted_response = self._generate_tier_adjustment_response(
                adjusted_result, objection_message, state
            )
            
            # Actualizar tier progression
            if not hasattr(state, 'tier_progression'):
                state.tier_progression = []
            
            state.tier_progression.append({
                'timestamp': datetime.now().isoformat(),
                'tier': adjusted_result.recommended_tier.value,
                'confidence': adjusted_result.confidence,
                'reasoning': adjusted_result.reasoning,
                'trigger_message': objection_message[:100],
                'adjustment_type': 'price_objection'
            })
            
            return {
                'adjusted_tier': adjusted_result.recommended_tier.value,
                'confidence': adjusted_result.confidence,
                'response': adjusted_response,
                'tier_progression': state.tier_progression
            }
            
        except Exception as e:
            logger.error(f"Error manejando objeción con ajuste de tier: {e}")
            return {
                'adjusted_tier': 'pro',
                'confidence': 0.5,
                'response': 'Entiendo tu preocupación sobre el precio. Déjame mostrarte nuestras opciones más accesibles.',
                'tier_progression': []
            }
    
    def _generate_tier_adjustment_response(
        self, 
        adjusted_result, 
        objection_message: str, 
        state: ConversationState
    ) -> str:
        """Generar respuesta apropiada para ajuste de tier."""
        try:
            tier = adjusted_result.recommended_tier.value
            price_point = adjusted_result.price_point
            
            # Respuestas específicas por tier ajustado
            if tier == 'essential':
                return (
                    f"Entiendo perfectamente tu preocupación sobre el precio. "
                    f"NGX Essential por {price_point} te da acceso completo a nuestro "
                    f"Hybrid Intelligence Engine - es menos de lo que gastas en café al mes. "
                    f"Puedes hacer upgrade cuando veas los resultados. ¿Te parece más razonable?"
                )
            
            elif tier == 'pro':
                return (
                    f"Comprendo tu punto de vista sobre el precio. NGX Pro por {price_point} "
                    f"es el sweet spot perfecto: tienes acceso completo a nuestros 11 agentes "
                    f"especializados, análisis de comidas con foto, y reportes semanales. "
                    f"Es una excelente inversión para los resultados que obtienes."
                )
            
            elif tier == 'elite':
                return (
                    f"Te entiendo completamente. NGX Elite por {price_point} incluye TODO "
                    f"lo que necesitas: voz natural con los agentes, análisis en tiempo real, "
                    f"y soporte prioritario. Considera que un coach personal cuesta $400-800/mes. "
                    f"Con NGX tienes 11 especialistas por mucho menos."
                )
            
            else:
                return (
                    f"Entiendo tu preocupación. {price_point} es una inversión significativa, "
                    f"pero considera que estás invirtiendo en tecnología única que no existe "
                    f"en ningún otro lugar. Nuestro HIE es como tener un equipo completo de "
                    f"especialistas trabajando exclusivamente para ti."
                )
                
        except Exception as e:
            logger.error(f"Error generando respuesta de ajuste: {e}")
            return "Entiendo tu preocupación sobre el precio. Déjame mostrarte nuestras opciones."
    
    async def suggest_upsell_opportunity(
        self, 
        current_tier: str, 
        state: ConversationState
    ) -> Optional[Dict[str, Any]]:
        """
        Sugerir oportunidad de upsell basada en progreso de conversación.
        
        Args:
            current_tier: Tier actual del usuario
            state: Estado de la conversación
            
        Returns:
            Dict con sugerencia de upsell o None
        """
        try:
            # Verificar si es buen momento para upsell
            message_count = len(state.messages)
            
            # Solo sugerir upsell después de cierto engagement
            if message_count < 6:
                return None
            
            # Analizar señales de engagement alto
            recent_user_messages = [
                msg.content for msg in state.messages[-5:] 
                if msg.role == 'user'
            ]
            
            # Señales de interés alto
            high_interest_signals = [
                'me gusta', 'interesante', 'impresionante', 'quiero saber más',
                'cómo funciona', 'necesito esto', 'perfecto para mí'
            ]
            
            interest_score = sum(
                1 for message in recent_user_messages
                for signal in high_interest_signals
                if signal in message.lower()
            )
            
            # Solo sugerir upsell si hay interés alto
            if interest_score < 2:
                return None
            
            # Determinar tier de upsell
            tier_hierarchy = ['essential', 'pro', 'elite', 'prime_premium', 'longevity_premium']
            
            try:
                current_index = tier_hierarchy.index(current_tier)
                if current_index < len(tier_hierarchy) - 1:
                    suggested_tier = tier_hierarchy[current_index + 1]
                else:
                    return None  # Ya está en el tier más alto
            except ValueError:
                return None  # Tier no reconocido
            
            # Preparar sugerencia de upsell
            upsell_benefits = self._get_upsell_benefits(current_tier, suggested_tier)
            
            return {
                'suggested_tier': suggested_tier,
                'current_tier': current_tier,
                'upsell_benefits': upsell_benefits,
                'interest_score': interest_score,
                'timing': 'optimal',
                'upsell_message': self._generate_upsell_message(current_tier, suggested_tier, upsell_benefits)
            }
            
        except Exception as e:
            logger.error(f"Error sugiriendo upsell: {e}")
            return None
    
    def _get_upsell_benefits(self, current_tier: str, suggested_tier: str) -> List[str]:
        """Obtener beneficios específicos del upsell."""
        upsell_benefits = {
            ('essential', 'pro'): [
                'Análisis de comidas con foto',
                'Reportes semanales detallados',
                'Integración con wearables',
                'Soporte prioritario'
            ],
            ('pro', 'elite'): [
                'Voz natural con los agentes',
                'Análisis en tiempo real por HRV',
                'Coaching personalizado avanzado',
                'Acceso a funciones beta'
            ],
            ('elite', 'prime_premium'): [
                'Coaching personal híbrido',
                'Análisis genético incluido',
                'Sesiones 1:1 con especialistas',
                'Transformación completa garantizada'
            ]
        }
        
        return upsell_benefits.get((current_tier, suggested_tier), [
            'Funciones premium adicionales',
            'Mejor experiencia de usuario',
            'Resultados más rápidos'
        ])
    
    def _generate_upsell_message(self, current_tier: str, suggested_tier: str, benefits: List[str]) -> str:
        """Generar mensaje de upsell personalizado."""
        try:
            benefits_text = ', '.join(benefits[:3])  # Top 3 beneficios
            
            if suggested_tier == 'pro':
                return (
                    f"Veo que estás realmente interesado en NGX. Por solo $70 más al mes, "
                    f"NGX Pro te da {benefits_text}. Es como pasar de un auto básico a uno "
                    f"con todas las comodidades. ¿Te gustaría maximizar tu experiencia?"
                )
            
            elif suggested_tier == 'elite':
                return (
                    f"Perfecto, noto que aprecias la calidad. NGX Elite incluye {benefits_text}. "
                    f"Por $50 adicionales al mes, tienes la experiencia premium completa. "
                    f"¿Te interesa tener acceso a todo lo que NGX puede ofrecer?"
                )
            
            elif suggested_tier in ['prime_premium', 'longevity_premium']:
                program_name = 'PRIME' if suggested_tier == 'prime_premium' else 'LONGEVITY'
                return (
                    f"Basándome en tu perfil, NGX {program_name} sería perfecto para ti. "
                    f"Incluye {benefits_text} y es una transformación completa. "
                    f"¿Te gustaría conocer más sobre esta opción exclusiva?"
                )
            
            else:
                return (
                    f"Veo que NGX te está gustando. El siguiente nivel incluye {benefits_text}. "
                    f"¿Te interesa conocer más sobre esta opción premium?"
                )
                
        except Exception as e:
            logger.error(f"Error generando mensaje de upsell: {e}")
            return "¿Te interesa conocer nuestras opciones premium?" 