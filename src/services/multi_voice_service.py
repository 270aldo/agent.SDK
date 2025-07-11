"""
Servicio Multi-Voice para NGX Voice Sales Agent.

Este servicio orquesta el uso de diferentes voice personas y configuraciones
según la sección de venta, estado emocional del cliente y progreso de la conversación.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from io import BytesIO

from src.integrations.elevenlabs.advanced_voice import (
    AdvancedVoiceEngine, VoicePersona, EmotionalState, advanced_voice_engine
)
from src.services.emotional_intelligence_service import EmotionalProfile
from src.services.adaptive_personality_service import PersonalityProfile
from src.services.empathy_engine_service import EmpathyResponse

logger = logging.getLogger(__name__)

class SalesSection(str, Enum):
    """Secciones del proceso de venta."""
    OPENING = "opening"                    # Apertura y bienvenida
    DISCOVERY = "discovery"                # Descubrimiento de necesidades
    QUALIFICATION = "qualification"        # Calificación del lead
    PRESENTATION = "presentation"          # Presentación de solución
    OBJECTION_HANDLING = "objection_handling"  # Manejo de objeciones
    CLOSING = "closing"                    # Cierre de venta
    FOLLOW_UP = "follow_up"               # Seguimiento post-venta

class VoiceIntensity(str, Enum):
    """Intensidad de la voz para diferentes momentos."""
    GENTLE = "gentle"          # Suave y calmante
    NORMAL = "normal"          # Neutral y profesional
    ENERGETIC = "energetic"    # Energético y entusiasta
    AUTHORITATIVE = "authoritative"  # Autoritativo y seguro
    EMPATHETIC = "empathetic"  # Empático y comprensivo

@dataclass
class VoiceConfiguration:
    """Configuración completa de voz para un momento específico."""
    persona: VoicePersona
    emotional_state: EmotionalState
    intensity: VoiceIntensity
    speaking_rate_modifier: float  # 0.8-1.2 (modificador del rate base)
    energy_level_modifier: float   # 0.8-1.2 (modificador del energy base)
    cultural_adaptation: str       # Adaptación cultural específica
    voice_instructions: Dict[str, Any]  # Instrucciones específicas para TTS

@dataclass
class MultiVoiceResponse:
    """Respuesta del sistema multi-voice."""
    audio_stream: BytesIO
    voice_config_used: VoiceConfiguration
    adaptation_reason: str
    emotional_alignment: float  # 0-1, qué tan bien se alinea con el estado emocional
    personality_match: float    # 0-1, qué tan bien coincide con la personalidad

class MultiVoiceService:
    """
    Servicio para gestión inteligente de múltiples voces.
    
    Características:
    - Selección automática de voice persona por sección de venta
    - Adaptación emocional en tiempo real
    - Configuración dinámica según personalidad del cliente
    - Optimización cultural y contextual
    - Analytics de efectividad por combinación
    """
    
    def __init__(self):
        """Inicializar servicio multi-voice."""
        self.voice_engine = advanced_voice_engine
        self.voice_configurations = self._initialize_voice_configurations()
        self.adaptation_rules = self._initialize_adaptation_rules()
        self.usage_analytics = {}
        
    def _initialize_voice_configurations(self) -> Dict[SalesSection, Dict[str, VoiceConfiguration]]:
        """Inicializar configuraciones de voz por sección de venta."""
        return {
            SalesSection.OPENING: {
                "default": VoiceConfiguration(
                    persona=VoicePersona.WELCOMER,
                    emotional_state=EmotionalState.CONFIDENT,
                    intensity=VoiceIntensity.NORMAL,
                    speaking_rate_modifier=1.0,
                    energy_level_modifier=1.1,
                    cultural_adaptation="warm_professional",
                    voice_instructions={"tone": "welcoming", "pace": "comfortable"}
                ),
                "anxious_client": VoiceConfiguration(
                    persona=VoicePersona.SUPPORTER,
                    emotional_state=EmotionalState.NEUTRAL,
                    intensity=VoiceIntensity.GENTLE,
                    speaking_rate_modifier=0.9,
                    energy_level_modifier=0.8,
                    cultural_adaptation="reassuring",
                    voice_instructions={"tone": "calming", "pace": "slow"}
                ),
                "excited_client": VoiceConfiguration(
                    persona=VoicePersona.WELCOMER,
                    emotional_state=EmotionalState.EXCITED,
                    intensity=VoiceIntensity.ENERGETIC,
                    speaking_rate_modifier=1.1,
                    energy_level_modifier=1.3,
                    cultural_adaptation="enthusiastic",
                    voice_instructions={"tone": "enthusiastic", "pace": "energetic"}
                )
            },
            SalesSection.DISCOVERY: {
                "default": VoiceConfiguration(
                    persona=VoicePersona.CONSULTANT,
                    emotional_state=EmotionalState.INTERESTED,
                    intensity=VoiceIntensity.NORMAL,
                    speaking_rate_modifier=0.95,
                    energy_level_modifier=1.0,
                    cultural_adaptation="curious_professional",
                    voice_instructions={"tone": "inquisitive", "pace": "thoughtful"}
                ),
                "analytical_client": VoiceConfiguration(
                    persona=VoicePersona.CONSULTANT,
                    emotional_state=EmotionalState.CONFIDENT,
                    intensity=VoiceIntensity.AUTHORITATIVE,
                    speaking_rate_modifier=0.9,
                    energy_level_modifier=0.9,
                    cultural_adaptation="data_focused",
                    voice_instructions={"tone": "analytical", "pace": "measured"}
                ),
                "expressive_client": VoiceConfiguration(
                    persona=VoicePersona.EDUCATOR,
                    emotional_state=EmotionalState.INTERESTED,
                    intensity=VoiceIntensity.ENERGETIC,
                    speaking_rate_modifier=1.05,
                    energy_level_modifier=1.2,
                    cultural_adaptation="storytelling",
                    voice_instructions={"tone": "engaging", "pace": "dynamic"}
                )
            },
            SalesSection.PRESENTATION: {
                "default": VoiceConfiguration(
                    persona=VoicePersona.EDUCATOR,
                    emotional_state=EmotionalState.CONFIDENT,
                    intensity=VoiceIntensity.NORMAL,
                    speaking_rate_modifier=1.0,
                    energy_level_modifier=1.1,
                    cultural_adaptation="educational",
                    voice_instructions={"tone": "informative", "pace": "clear"}
                ),
                "skeptical_client": VoiceConfiguration(
                    persona=VoicePersona.CONSULTANT,
                    emotional_state=EmotionalState.CONFIDENT,
                    intensity=VoiceIntensity.AUTHORITATIVE,
                    speaking_rate_modifier=0.95,
                    energy_level_modifier=1.0,
                    cultural_adaptation="evidence_based",
                    voice_instructions={"tone": "authoritative", "pace": "deliberate"}
                ),
                "interested_client": VoiceConfiguration(
                    persona=VoicePersona.EDUCATOR,
                    emotional_state=EmotionalState.EXCITED,
                    intensity=VoiceIntensity.ENERGETIC,
                    speaking_rate_modifier=1.05,
                    energy_level_modifier=1.2,
                    cultural_adaptation="motivational",
                    voice_instructions={"tone": "inspiring", "pace": "engaging"}
                )
            },
            SalesSection.OBJECTION_HANDLING: {
                "default": VoiceConfiguration(
                    persona=VoicePersona.NEGOTIATOR,
                    emotional_state=EmotionalState.CONFIDENT,
                    intensity=VoiceIntensity.EMPATHETIC,
                    speaking_rate_modifier=0.9,
                    energy_level_modifier=0.9,
                    cultural_adaptation="understanding",
                    voice_instructions={"tone": "empathetic", "pace": "patient"}
                ),
                "frustrated_client": VoiceConfiguration(
                    persona=VoicePersona.SUPPORTER,
                    emotional_state=EmotionalState.NEUTRAL,
                    intensity=VoiceIntensity.GENTLE,
                    speaking_rate_modifier=0.85,
                    energy_level_modifier=0.8,
                    cultural_adaptation="calming",
                    voice_instructions={"tone": "soothing", "pace": "slow"}
                ),
                "price_objection": VoiceConfiguration(
                    persona=VoicePersona.CONSULTANT,
                    emotional_state=EmotionalState.CONFIDENT,
                    intensity=VoiceIntensity.AUTHORITATIVE,
                    speaking_rate_modifier=0.9,
                    energy_level_modifier=1.0,
                    cultural_adaptation="value_focused",
                    voice_instructions={"tone": "confident", "pace": "clear"}
                )
            },
            SalesSection.CLOSING: {
                "default": VoiceConfiguration(
                    persona=VoicePersona.CLOSER,
                    emotional_state=EmotionalState.DECISIVE,
                    intensity=VoiceIntensity.AUTHORITATIVE,
                    speaking_rate_modifier=1.0,
                    energy_level_modifier=1.2,
                    cultural_adaptation="decisive",
                    voice_instructions={"tone": "confident", "pace": "decisive"}
                ),
                "hesitant_client": VoiceConfiguration(
                    persona=VoicePersona.SUPPORTER,
                    emotional_state=EmotionalState.CONFIDENT,
                    intensity=VoiceIntensity.EMPATHETIC,
                    speaking_rate_modifier=0.9,
                    energy_level_modifier=1.0,
                    cultural_adaptation="supportive",
                    voice_instructions={"tone": "reassuring", "pace": "gentle"}
                ),
                "ready_client": VoiceConfiguration(
                    persona=VoicePersona.CLOSER,
                    emotional_state=EmotionalState.EXCITED,
                    intensity=VoiceIntensity.ENERGETIC,
                    speaking_rate_modifier=1.1,
                    energy_level_modifier=1.3,
                    cultural_adaptation="celebratory",
                    voice_instructions={"tone": "enthusiastic", "pace": "energetic"}
                )
            },
            SalesSection.FOLLOW_UP: {
                "default": VoiceConfiguration(
                    persona=VoicePersona.SUPPORTER,
                    emotional_state=EmotionalState.SATISFIED,
                    intensity=VoiceIntensity.NORMAL,
                    speaking_rate_modifier=1.0,
                    energy_level_modifier=1.0,
                    cultural_adaptation="supportive",
                    voice_instructions={"tone": "helpful", "pace": "comfortable"}
                ),
                "satisfied_client": VoiceConfiguration(
                    persona=VoicePersona.SUPPORTER,
                    emotional_state=EmotionalState.SATISFIED,
                    intensity=VoiceIntensity.NORMAL,
                    speaking_rate_modifier=1.0,
                    energy_level_modifier=1.1,
                    cultural_adaptation="positive",
                    voice_instructions={"tone": "positive", "pace": "upbeat"}
                )
            }
        }
    
    def _initialize_adaptation_rules(self) -> Dict[str, Any]:
        """Inicializar reglas de adaptación emocional y de personalidad."""
        return {
            "emotional_adaptations": {
                EmotionalState.ANXIOUS: {
                    "persona_preference": VoicePersona.SUPPORTER,
                    "intensity_adjustment": -0.3,
                    "speaking_rate_adjustment": -0.15,
                    "energy_adjustment": -0.2,
                    "cultural_emphasis": "reassuring"
                },
                EmotionalState.EXCITED: {
                    "persona_preference": VoicePersona.WELCOMER,
                    "intensity_adjustment": 0.2,
                    "speaking_rate_adjustment": 0.1,
                    "energy_adjustment": 0.3,
                    "cultural_emphasis": "enthusiastic"
                },
                EmotionalState.FRUSTRATED: {
                    "persona_preference": VoicePersona.SUPPORTER,
                    "intensity_adjustment": -0.4,
                    "speaking_rate_adjustment": -0.2,
                    "energy_adjustment": -0.3,
                    "cultural_emphasis": "calming"
                },
                EmotionalState.SKEPTICAL: {
                    "persona_preference": VoicePersona.CONSULTANT,
                    "intensity_adjustment": 0.1,
                    "speaking_rate_adjustment": -0.05,
                    "energy_adjustment": 0.0,
                    "cultural_emphasis": "evidence_based"
                },
                EmotionalState.INTERESTED: {
                    "persona_preference": VoicePersona.EDUCATOR,
                    "intensity_adjustment": 0.15,
                    "speaking_rate_adjustment": 0.05,
                    "energy_adjustment": 0.2,
                    "cultural_emphasis": "engaging"
                },
                EmotionalState.DECISIVE: {
                    "persona_preference": VoicePersona.CLOSER,
                    "intensity_adjustment": 0.3,
                    "speaking_rate_adjustment": 0.1,
                    "energy_adjustment": 0.25,
                    "cultural_emphasis": "decisive"
                }
            },
            "personality_adaptations": {
                "analytical": {
                    "persona_preference": VoicePersona.CONSULTANT,
                    "speaking_rate_adjustment": -0.1,
                    "cultural_emphasis": "data_focused"
                },
                "driver": {
                    "persona_preference": VoicePersona.CLOSER,
                    "speaking_rate_adjustment": 0.1,
                    "cultural_emphasis": "results_focused"
                },
                "expressive": {
                    "persona_preference": VoicePersona.WELCOMER,
                    "energy_adjustment": 0.2,
                    "cultural_emphasis": "expressive"
                },
                "amiable": {
                    "persona_preference": VoicePersona.SUPPORTER,
                    "intensity_adjustment": -0.1,
                    "cultural_emphasis": "warm"
                },
                "technical": {
                    "persona_preference": VoicePersona.CONSULTANT,
                    "speaking_rate_adjustment": -0.05,
                    "cultural_emphasis": "precise"
                }
            }
        }
    
    async def generate_adaptive_voice_response(
        self,
        text: str,
        sales_section: SalesSection,
        emotional_profile: Optional[EmotionalProfile] = None,
        personality_profile: Optional[PersonalityProfile] = None,
        empathy_response: Optional[EmpathyResponse] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> MultiVoiceResponse:
        """
        Generar respuesta de voz adaptativa basada en múltiples factores.
        
        Args:
            text: Texto a convertir a voz
            sales_section: Sección actual del proceso de venta
            emotional_profile: Perfil emocional del cliente
            personality_profile: Perfil de personalidad del cliente
            empathy_response: Respuesta empática generada
            context: Contexto adicional de la conversación
            
        Returns:
            MultiVoiceResponse con audio y metadata de adaptación
        """
        try:
            # Seleccionar configuración base por sección
            base_config = self._select_base_configuration(
                sales_section, emotional_profile, personality_profile, context
            )
            
            # Adaptar configuración según factores emocionales y de personalidad
            adapted_config = await self._adapt_voice_configuration(
                base_config, emotional_profile, personality_profile, empathy_response
            )
            
            # Calcular métricas de alineación
            emotional_alignment = self._calculate_emotional_alignment(
                adapted_config, emotional_profile
            )
            personality_match = self._calculate_personality_match(
                adapted_config, personality_profile
            )
            
            # Generar audio con configuración adaptada
            audio_stream = await self._generate_audio_with_config(
                text, adapted_config, context
            )
            
            # Crear respuesta completa
            response = MultiVoiceResponse(
                audio_stream=audio_stream,
                voice_config_used=adapted_config,
                adaptation_reason=self._generate_adaptation_reason(
                    sales_section, emotional_profile, personality_profile
                ),
                emotional_alignment=emotional_alignment,
                personality_match=personality_match
            )
            
            # Registrar analytics
            await self._track_voice_usage(adapted_config, response, context)
            
            logger.info(
                f"Voice response generado: {adapted_config.persona.value}, "
                f"sección: {sales_section.value}, alineación emocional: {emotional_alignment:.2f}"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error generando respuesta multi-voice: {e}")
            # Fallback a configuración básica
            return await self._generate_fallback_response(text, sales_section)
    
    def _select_base_configuration(
        self,
        sales_section: SalesSection,
        emotional_profile: Optional[EmotionalProfile],
        personality_profile: Optional[PersonalityProfile],
        context: Optional[Dict[str, Any]]
    ) -> VoiceConfiguration:
        """Seleccionar configuración base según la sección y contexto."""
        section_configs = self.voice_configurations.get(sales_section, {})
        
        # Seleccionar configuración específica si hay match emocional/contextual
        if emotional_profile:
            primary_emotion = emotional_profile.primary_emotion.value
            
            # Configuraciones específicas por emoción y sección
            if sales_section == SalesSection.OPENING:
                if primary_emotion in ["anxious", "frustrated"]:
                    return section_configs.get("anxious_client", section_configs["default"])
                elif primary_emotion in ["excited", "interested"]:
                    return section_configs.get("excited_client", section_configs["default"])
            
            elif sales_section == SalesSection.DISCOVERY:
                if personality_profile and personality_profile.communication_style.value == "analytical":
                    return section_configs.get("analytical_client", section_configs["default"])
                elif personality_profile and personality_profile.communication_style.value == "expressive":
                    return section_configs.get("expressive_client", section_configs["default"])
            
            elif sales_section == SalesSection.PRESENTATION:
                if primary_emotion == "skeptical":
                    return section_configs.get("skeptical_client", section_configs["default"])
                elif primary_emotion in ["interested", "excited"]:
                    return section_configs.get("interested_client", section_configs["default"])
            
            elif sales_section == SalesSection.OBJECTION_HANDLING:
                if primary_emotion == "frustrated":
                    return section_configs.get("frustrated_client", section_configs["default"])
                elif context and "price_objection" in context.get("triggers", []):
                    return section_configs.get("price_objection", section_configs["default"])
            
            elif sales_section == SalesSection.CLOSING:
                if primary_emotion in ["anxious", "confused"]:
                    return section_configs.get("hesitant_client", section_configs["default"])
                elif primary_emotion in ["decisive", "excited"]:
                    return section_configs.get("ready_client", section_configs["default"])
        
        return section_configs.get("default", self.voice_configurations[SalesSection.OPENING]["default"])
    
    async def _adapt_voice_configuration(
        self,
        base_config: VoiceConfiguration,
        emotional_profile: Optional[EmotionalProfile],
        personality_profile: Optional[PersonalityProfile],
        empathy_response: Optional[EmpathyResponse]
    ) -> VoiceConfiguration:
        """Adaptar configuración base según perfiles emocionales y de personalidad."""
        adapted_config = VoiceConfiguration(
            persona=base_config.persona,
            emotional_state=base_config.emotional_state,
            intensity=base_config.intensity,
            speaking_rate_modifier=base_config.speaking_rate_modifier,
            energy_level_modifier=base_config.energy_level_modifier,
            cultural_adaptation=base_config.cultural_adaptation,
            voice_instructions=base_config.voice_instructions.copy()
        )
        
        # Adaptar según perfil emocional
        if emotional_profile:
            emotion_adaptation = self.adaptation_rules["emotional_adaptations"].get(
                emotional_profile.primary_emotion, {}
            )
            
            # Ajustar persona si es necesario
            preferred_persona = emotion_adaptation.get("persona_preference")
            if preferred_persona and emotional_profile.confidence > 0.7:
                adapted_config.persona = preferred_persona
            
            # Ajustar parámetros de voz
            if "intensity_adjustment" in emotion_adaptation:
                # Mantener el enum pero ajustar modificadores
                intensity_adj = emotion_adaptation["intensity_adjustment"]
                adapted_config.energy_level_modifier += intensity_adj
                adapted_config.energy_level_modifier = max(0.5, min(1.5, adapted_config.energy_level_modifier))
            
            if "speaking_rate_adjustment" in emotion_adaptation:
                rate_adj = emotion_adaptation["speaking_rate_adjustment"]
                adapted_config.speaking_rate_modifier += rate_adj
                adapted_config.speaking_rate_modifier = max(0.7, min(1.3, adapted_config.speaking_rate_modifier))
            
            # Ajustar adaptación cultural
            cultural_emphasis = emotion_adaptation.get("cultural_emphasis")
            if cultural_emphasis:
                adapted_config.cultural_adaptation = cultural_emphasis
        
        # Adaptar según perfil de personalidad
        if personality_profile:
            personality_adaptation = self.adaptation_rules["personality_adaptations"].get(
                personality_profile.communication_style.value, {}
            )
            
            # Ajustar persona según estilo de comunicación
            preferred_persona = personality_adaptation.get("persona_preference")
            if preferred_persona:
                adapted_config.persona = preferred_persona
            
            # Ajustar ritmo según preferencias
            if personality_profile.pace_preference == "fast":
                adapted_config.speaking_rate_modifier += 0.1
            elif personality_profile.pace_preference == "slow":
                adapted_config.speaking_rate_modifier -= 0.1
            
            # Límites de seguridad
            adapted_config.speaking_rate_modifier = max(0.7, min(1.3, adapted_config.speaking_rate_modifier))
        
        # Adaptar según respuesta empática
        if empathy_response:
            # Usar la persona recomendada por el motor de empatía
            adapted_config.persona = empathy_response.voice_persona
            
            # Ajustar tono según técnica empática
            technique = empathy_response.technique_used.value
            if technique in ["validation", "reassurance"]:
                adapted_config.intensity = VoiceIntensity.GENTLE
                adapted_config.energy_level_modifier *= 0.9
            elif technique in ["mirroring", "empowerment"]:
                adapted_config.intensity = VoiceIntensity.ENERGETIC
                adapted_config.energy_level_modifier *= 1.1
        
        return adapted_config
    
    async def _generate_audio_with_config(
        self,
        text: str,
        config: VoiceConfiguration,
        context: Optional[Dict[str, Any]]
    ) -> BytesIO:
        """Generar audio usando configuración adaptada."""
        try:
            # Determinar configuraciones para el advanced voice engine
            program_type = context.get("program_type", "PRIME") if context else "PRIME"
            gender = context.get("voice_gender", "male") if context else "male"
            
            # Generar audio con configuración avanzada
            audio_stream = await self.voice_engine.text_to_speech_advanced(
                text=text,
                program_type=program_type,
                gender=gender,
                persona=config.persona,
                emotional_state=config.emotional_state,
                language="es",
                optimize_streaming=False
            )
            
            return audio_stream
            
        except Exception as e:
            logger.error(f"Error generando audio con configuración: {e}")
            # Fallback a síntesis básica
            return await self.voice_engine.text_to_speech_advanced(
                text=text,
                persona=VoicePersona.CONSULTANT,
                emotional_state=EmotionalState.NEUTRAL
            )
    
    def _calculate_emotional_alignment(
        self,
        config: VoiceConfiguration,
        emotional_profile: Optional[EmotionalProfile]
    ) -> float:
        """Calcular qué tan bien se alinea la configuración con el estado emocional."""
        if not emotional_profile:
            return 0.5  # Neutral si no hay perfil
        
        # Scoring basado en alineación de configuración
        alignment_score = 0.5  # Base score
        
        # Bonus por persona apropiada
        primary_emotion = emotional_profile.primary_emotion
        if primary_emotion in [EmotionalState.ANXIOUS, EmotionalState.FRUSTRATED]:
            if config.persona == VoicePersona.SUPPORTER:
                alignment_score += 0.3
        elif primary_emotion in [EmotionalState.EXCITED, EmotionalState.INTERESTED]:
            if config.persona in [VoicePersona.WELCOMER, VoicePersona.EDUCATOR]:
                alignment_score += 0.3
        elif primary_emotion == EmotionalState.SKEPTICAL:
            if config.persona == VoicePersona.CONSULTANT:
                alignment_score += 0.3
        
        # Bonus por intensidad apropiada
        if primary_emotion == EmotionalState.ANXIOUS and config.intensity == VoiceIntensity.GENTLE:
            alignment_score += 0.2
        elif primary_emotion == EmotionalState.EXCITED and config.intensity == VoiceIntensity.ENERGETIC:
            alignment_score += 0.2
        
        return min(1.0, alignment_score)
    
    def _calculate_personality_match(
        self,
        config: VoiceConfiguration,
        personality_profile: Optional[PersonalityProfile]
    ) -> float:
        """Calcular qué tan bien coincide la configuración con la personalidad."""
        if not personality_profile:
            return 0.5  # Neutral si no hay perfil
        
        match_score = 0.5  # Base score
        
        communication_style = personality_profile.communication_style.value
        
        # Scoring por coincidencia de persona
        persona_matches = {
            "analytical": VoicePersona.CONSULTANT,
            "driver": VoicePersona.CLOSER,
            "expressive": VoicePersona.WELCOMER,
            "amiable": VoicePersona.SUPPORTER,
            "technical": VoicePersona.CONSULTANT
        }
        
        if config.persona == persona_matches.get(communication_style):
            match_score += 0.3
        
        # Bonus por ritmo apropiado
        if personality_profile.pace_preference == "fast" and config.speaking_rate_modifier > 1.0:
            match_score += 0.1
        elif personality_profile.pace_preference == "slow" and config.speaking_rate_modifier < 1.0:
            match_score += 0.1
        
        # Bonus por nivel de detalle
        if personality_profile.detail_orientation > 0.7 and config.persona == VoicePersona.CONSULTANT:
            match_score += 0.1
        
        return min(1.0, match_score)
    
    def _generate_adaptation_reason(
        self,
        sales_section: SalesSection,
        emotional_profile: Optional[EmotionalProfile],
        personality_profile: Optional[PersonalityProfile]
    ) -> str:
        """Generar razón de adaptación para analytics."""
        reasons = [f"Sección: {sales_section.value}"]
        
        if emotional_profile:
            reasons.append(f"Emoción: {emotional_profile.primary_emotion.value}")
            if emotional_profile.confidence > 0.8:
                reasons.append("(alta confianza)")
        
        if personality_profile:
            reasons.append(f"Estilo: {personality_profile.communication_style.value}")
        
        return " | ".join(reasons)
    
    async def _track_voice_usage(
        self,
        config: VoiceConfiguration,
        response: MultiVoiceResponse,
        context: Optional[Dict[str, Any]]
    ) -> None:
        """Registrar uso de configuración para analytics."""
        try:
            usage_key = f"{config.persona.value}_{config.intensity.value}"
            
            if usage_key not in self.usage_analytics:
                self.usage_analytics[usage_key] = {
                    "count": 0,
                    "total_emotional_alignment": 0.0,
                    "total_personality_match": 0.0,
                    "contexts": []
                }
            
            analytics = self.usage_analytics[usage_key]
            analytics["count"] += 1
            analytics["total_emotional_alignment"] += response.emotional_alignment
            analytics["total_personality_match"] += response.personality_match
            
            # Mantener solo los últimos 10 contextos
            if len(analytics["contexts"]) >= 10:
                analytics["contexts"].pop(0)
            
            analytics["contexts"].append({
                "timestamp": datetime.now().isoformat(),
                "adaptation_reason": response.adaptation_reason
            })
            
        except Exception as e:
            logger.error(f"Error tracking voice usage: {e}")
    
    async def _generate_fallback_response(
        self,
        text: str,
        sales_section: SalesSection
    ) -> MultiVoiceResponse:
        """Generar respuesta de fallback en caso de error."""
        try:
            # Configuración segura por defecto
            fallback_config = VoiceConfiguration(
                persona=VoicePersona.CONSULTANT,
                emotional_state=EmotionalState.NEUTRAL,
                intensity=VoiceIntensity.NORMAL,
                speaking_rate_modifier=1.0,
                energy_level_modifier=1.0,
                cultural_adaptation="neutral",
                voice_instructions={"tone": "professional", "pace": "normal"}
            )
            
            audio_stream = await self.voice_engine.text_to_speech_advanced(
                text=text,
                persona=fallback_config.persona,
                emotional_state=fallback_config.emotional_state
            )
            
            return MultiVoiceResponse(
                audio_stream=audio_stream,
                voice_config_used=fallback_config,
                adaptation_reason=f"Fallback para {sales_section.value}",
                emotional_alignment=0.5,
                personality_match=0.5
            )
            
        except Exception as e:
            logger.error(f"Error en fallback response: {e}")
            raise
    
    def get_voice_analytics(self) -> Dict[str, Any]:
        """Obtener analytics de uso de voces."""
        analytics_summary = {}
        
        for config_key, data in self.usage_analytics.items():
            if data["count"] > 0:
                analytics_summary[config_key] = {
                    "usage_count": data["count"],
                    "avg_emotional_alignment": data["total_emotional_alignment"] / data["count"],
                    "avg_personality_match": data["total_personality_match"] / data["count"],
                    "recent_contexts": data["contexts"][-3:]  # Últimos 3 contextos
                }
        
        return {
            "total_configurations_used": len(analytics_summary),
            "configuration_performance": analytics_summary,
            "voice_engine_info": self.voice_engine.get_voice_analytics()
        }

# Singleton instance
multi_voice_service = MultiVoiceService()