"""
Motor de Empatía para NGX Voice Sales Agent.

Este servicio genera respuestas empáticas y personalizadas basadas
en el estado emocional del cliente, utilizando técnicas avanzadas
de comunicación empática.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import re

from src.integrations.elevenlabs.advanced_voice import EmotionalState, VoicePersona
from src.services.emotional_intelligence_service import EmotionalProfile, EmotionalTrigger

logger = logging.getLogger(__name__)

class EmpathyTechnique(str, Enum):
    """Técnicas de empatía para aplicar en respuestas."""
    VALIDATION = "validation"              # Validar sentimientos
    MIRRORING = "mirroring"               # Reflejar lenguaje/tono
    REFRAMING = "reframing"               # Reencuadrar perspectiva
    NORMALIZATION = "normalization"        # Normalizar experiencia
    ACKNOWLEDGMENT = "acknowledgment"      # Reconocer preocupaciones
    REASSURANCE = "reassurance"           # Tranquilizar
    EMPOWERMENT = "empowerment"           # Empoderar al cliente
    BRIDGING = "bridging"                 # Conectar con solución

@dataclass
class EmpathyResponse:
    """Respuesta empática estructurada."""
    intro_phrase: str                     # Frase de apertura empática
    core_message: str                     # Mensaje principal
    closing_phrase: str                   # Cierre empático
    technique_used: EmpathyTechnique     # Técnica aplicada
    voice_persona: VoicePersona           # Persona de voz recomendada
    emotional_tone: str                   # Tono emocional a usar

class EmpathyEngineService:
    """
    Motor para generar respuestas empáticas avanzadas.
    
    Características:
    - Adaptación empática por estado emocional
    - Técnicas de comunicación validadas
    - Personalización cultural y demográfica
    - Frases empáticas contextuales
    - Integración con voice personas
    """
    
    def __init__(self):
        """Inicializar motor de empatía."""
        self.empathy_templates = self._initialize_empathy_templates()
        self.cultural_adaptations = self._initialize_cultural_adaptations()
        
    def _initialize_empathy_templates(self) -> Dict[EmotionalState, Dict[str, Any]]:
        """Inicializar plantillas de empatía por estado emocional."""
        return {
            EmotionalState.ANXIOUS: {
                "intro_phrases": [
                    "Entiendo perfectamente tu preocupación",
                    "Es completamente normal sentirse así",
                    "Comprendo que esto puede generar inquietud"
                ],
                "techniques": [EmpathyTechnique.VALIDATION, EmpathyTechnique.REASSURANCE],
                "voice_persona": VoicePersona.SUPPORTER,
                "tone": "calmante y tranquilizador"
            },
            EmotionalState.FRUSTRATED: {
                "intro_phrases": [
                    "Lamento mucho que estés experimentando esto",
                    "Entiendo tu frustración, es totalmente válida",
                    "Comprendo lo molesto que debe ser esto para ti"
                ],
                "techniques": [EmpathyTechnique.ACKNOWLEDGMENT, EmpathyTechnique.REFRAMING],
                "voice_persona": VoicePersona.CONSULTANT,
                "tone": "comprensivo y solucionador"
            },
            EmotionalState.CONFUSED: {
                "intro_phrases": [
                    "Permíteme aclararte esto de manera más simple",
                    "Es normal tener dudas, déjame explicártelo mejor",
                    "Entiendo que puede parecer complejo, vamos paso a paso"
                ],
                "techniques": [EmpathyTechnique.NORMALIZATION, EmpathyTechnique.BRIDGING],
                "voice_persona": VoicePersona.EDUCATOR,
                "tone": "claro y paciente"
            },
            EmotionalState.SKEPTICAL: {
                "intro_phrases": [
                    "Entiendo tu escepticismo, es una reacción inteligente",
                    "Es bueno que seas cauteloso, déjame mostrarte",
                    "Aprecio que quieras verificar esto a fondo"
                ],
                "techniques": [EmpathyTechnique.VALIDATION, EmpathyTechnique.EMPOWERMENT],
                "voice_persona": VoicePersona.CONSULTANT,
                "tone": "respetuoso y factual"
            },
            EmotionalState.INTERESTED: {
                "intro_phrases": [
                    "¡Me alegra mucho que esto te resulte interesante!",
                    "Excelente pregunta, me encanta tu curiosidad",
                    "Qué bueno que quieras saber más sobre esto"
                ],
                "techniques": [EmpathyTechnique.MIRRORING, EmpathyTechnique.EMPOWERMENT],
                "voice_persona": VoicePersona.EDUCATOR,
                "tone": "entusiasta y educativo"
            },
            EmotionalState.EXCITED: {
                "intro_phrases": [
                    "¡Comparto totalmente tu entusiasmo!",
                    "¡Me encanta ver tu energía positiva!",
                    "¡Tu emoción es contagiosa, esto es genial!"
                ],
                "techniques": [EmpathyTechnique.MIRRORING, EmpathyTechnique.VALIDATION],
                "voice_persona": VoicePersona.WELCOMER,
                "tone": "energético y celebratorio"
            },
            EmotionalState.DECISIVE: {
                "intro_phrases": [
                    "Excelente decisión, vamos a hacerlo realidad",
                    "Me alegra que estés listo para dar este paso",
                    "Perfecto, procedamos con tu decisión"
                ],
                "techniques": [EmpathyTechnique.VALIDATION, EmpathyTechnique.EMPOWERMENT],
                "voice_persona": VoicePersona.CLOSER,
                "tone": "afirmativo y orientado a acción"
            }
        }
    
    def _initialize_cultural_adaptations(self) -> Dict[str, Dict[str, Any]]:
        """Inicializar adaptaciones culturales para empatía."""
        return {
            "latin_america": {
                "formality": "informal_warm",
                "personal_space": "close",
                "empathy_style": "expressive",
                "preferred_phrases": ["mi amigo", "con mucho gusto", "por supuesto"]
            },
            "spain": {
                "formality": "informal_direct",
                "personal_space": "moderate",
                "empathy_style": "direct_warm",
                "preferred_phrases": ["desde luego", "por supuesto", "entiendo"]
            },
            "mexico": {
                "formality": "formal_warm",
                "personal_space": "close",
                "empathy_style": "highly_expressive",
                "preferred_phrases": ["con todo gusto", "por favor", "muchas gracias"]
            },
            "usa_hispanic": {
                "formality": "moderate",
                "personal_space": "moderate",
                "empathy_style": "balanced",
                "preferred_phrases": ["claro que sí", "absolutamente", "entiendo"]
            }
        }
    
    async def generate_empathetic_response(
        self,
        emotional_profile: EmotionalProfile,
        original_message: str,
        context: Dict[str, Any],
        cultural_context: Optional[str] = None
    ) -> EmpathyResponse:
        """
        Generar respuesta empática basada en perfil emocional.
        
        Args:
            emotional_profile: Perfil emocional del cliente
            original_message: Mensaje original a responder
            context: Contexto de la conversación
            cultural_context: Contexto cultural del cliente
            
        Returns:
            EmpathyResponse con respuesta estructurada
        """
        try:
            # Obtener plantilla base para el estado emocional
            template = self.empathy_templates.get(
                emotional_profile.primary_emotion,
                self.empathy_templates[EmotionalState.NEUTRAL]
            )
            
            # Seleccionar técnica de empatía apropiada
            technique = self._select_empathy_technique(
                emotional_profile,
                context
            )
            
            # Generar componentes de respuesta
            intro = await self._generate_intro_phrase(
                emotional_profile,
                template,
                cultural_context
            )
            
            core = await self._adapt_core_message(
                original_message,
                emotional_profile,
                technique,
                context
            )
            
            closing = await self._generate_closing_phrase(
                emotional_profile,
                technique,
                cultural_context
            )
            
            # Construir respuesta completa
            response = EmpathyResponse(
                intro_phrase=intro,
                core_message=core,
                closing_phrase=closing,
                technique_used=technique,
                voice_persona=template["voice_persona"],
                emotional_tone=template["tone"]
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error generando respuesta empática: {e}")
            # Respuesta por defecto
            return EmpathyResponse(
                intro_phrase="Entiendo tu punto",
                core_message=original_message,
                closing_phrase="¿Hay algo más en lo que pueda ayudarte?",
                technique_used=EmpathyTechnique.ACKNOWLEDGMENT,
                voice_persona=VoicePersona.CONSULTANT,
                emotional_tone="neutral y profesional"
            )
    
    def _select_empathy_technique(
        self,
        profile: EmotionalProfile,
        context: Dict[str, Any]
    ) -> EmpathyTechnique:
        """
        Seleccionar técnica de empatía más apropiada.
        
        Args:
            profile: Perfil emocional
            context: Contexto de conversación
            
        Returns:
            Técnica de empatía seleccionada
        """
        # Mapeo de triggers a técnicas
        trigger_technique_map = {
            EmotionalTrigger.PRICE_MENTION: EmpathyTechnique.REFRAMING,
            EmotionalTrigger.TECHNICAL_COMPLEXITY: EmpathyTechnique.BRIDGING,
            EmotionalTrigger.TIME_PRESSURE: EmpathyTechnique.REASSURANCE,
            EmotionalTrigger.COMPETITOR_COMPARISON: EmpathyTechnique.EMPOWERMENT,
            EmotionalTrigger.FEATURE_LIMITATION: EmpathyTechnique.ACKNOWLEDGMENT,
            EmotionalTrigger.SUCCESS_STORY: EmpathyTechnique.VALIDATION,
            EmotionalTrigger.PERSONAL_BENEFIT: EmpathyTechnique.MIRRORING
        }
        
        # Buscar técnica por trigger
        for trigger in profile.triggers:
            if trigger in trigger_technique_map:
                return trigger_technique_map[trigger]
        
        # Técnica por defecto según estado emocional
        default_techniques = self.empathy_templates.get(
            profile.primary_emotion, {}
        ).get("techniques", [EmpathyTechnique.ACKNOWLEDGMENT])
        
        return default_techniques[0] if default_techniques else EmpathyTechnique.ACKNOWLEDGMENT
    
    async def _generate_intro_phrase(
        self,
        profile: EmotionalProfile,
        template: Dict[str, Any],
        cultural_context: Optional[str]
    ) -> str:
        """
        Generar frase de introducción empática.
        
        Args:
            profile: Perfil emocional
            template: Plantilla de empatía
            cultural_context: Contexto cultural
            
        Returns:
            Frase de introducción
        """
        base_phrases = template.get("intro_phrases", ["Entiendo"])
        
        # Seleccionar frase base
        intro = base_phrases[hash(str(profile.confidence)) % len(base_phrases)]
        
        # Adaptar culturalmente si es necesario
        if cultural_context and cultural_context in self.cultural_adaptations:
            adaptation = self.cultural_adaptations[cultural_context]
            if adaptation["empathy_style"] == "highly_expressive":
                intro = f"¡{intro}!"
            elif adaptation["formality"] == "formal_warm":
                intro = intro.replace("tu", "su").replace("Entiendo", "Comprendo")
        
        return intro
    
    async def _adapt_core_message(
        self,
        original_message: str,
        profile: EmotionalProfile,
        technique: EmpathyTechnique,
        context: Dict[str, Any]
    ) -> str:
        """
        Adaptar mensaje principal con técnica empática.
        
        Args:
            original_message: Mensaje original
            profile: Perfil emocional
            technique: Técnica de empatía
            context: Contexto
            
        Returns:
            Mensaje adaptado
        """
        # Aplicar técnica específica
        if technique == EmpathyTechnique.VALIDATION:
            return f"{original_message} Y es totalmente comprensible que te sientas así."
        
        elif technique == EmpathyTechnique.MIRRORING:
            # Reflejar el nivel de energía del cliente
            if profile.primary_emotion == EmotionalState.EXCITED:
                return f"¡{original_message}! ¡Esto es realmente emocionante!"
            else:
                return original_message
        
        elif technique == EmpathyTechnique.REFRAMING:
            return f"Aunque entiendo tu perspectiva, también podemos verlo así: {original_message}"
        
        elif technique == EmpathyTechnique.NORMALIZATION:
            return f"Muchos de nuestros clientes tienen la misma inquietud. {original_message}"
        
        elif technique == EmpathyTechnique.ACKNOWLEDGMENT:
            return f"Tienes razón en señalar eso. {original_message}"
        
        elif technique == EmpathyTechnique.REASSURANCE:
            return f"{original_message} Puedes estar tranquilo, estamos aquí para apoyarte."
        
        elif technique == EmpathyTechnique.EMPOWERMENT:
            return f"{original_message} Y tú tienes el control total de esta decisión."
        
        elif technique == EmpathyTechnique.BRIDGING:
            return f"Para conectar con lo que mencionas, {original_message}"
        
        return original_message
    
    async def _generate_closing_phrase(
        self,
        profile: EmotionalProfile,
        technique: EmpathyTechnique,
        cultural_context: Optional[str]
    ) -> str:
        """
        Generar frase de cierre empática.
        
        Args:
            profile: Perfil emocional
            technique: Técnica usada
            cultural_context: Contexto cultural
            
        Returns:
            Frase de cierre
        """
        # Mapeo de estados emocionales a cierres
        closing_map = {
            EmotionalState.ANXIOUS: "¿Te gustaría que revisemos esto con más calma?",
            EmotionalState.FRUSTRATED: "¿Cómo puedo hacer esto más fácil para ti?",
            EmotionalState.CONFUSED: "¿Quedó más claro ahora o prefieres que lo explique de otra forma?",
            EmotionalState.SKEPTICAL: "¿Qué información adicional necesitas para sentirte seguro?",
            EmotionalState.INTERESTED: "¿Qué aspecto te gustaría explorar más a fondo?",
            EmotionalState.EXCITED: "¿Estás listo para dar el siguiente paso?",
            EmotionalState.DECISIVE: "¿Comenzamos con el proceso entonces?"
        }
        
        closing = closing_map.get(
            profile.primary_emotion,
            "¿En qué más puedo ayudarte?"
        )
        
        # Adaptar culturalmente
        if cultural_context == "mexico":
            closing = f"¿{closing} Por favor no dude en decirme."
        elif cultural_context == "spain":
            closing = closing.replace("ti", "usted") if "formal" in str(context) else closing
        
        return closing
    
    def enhance_message_with_empathy(
        self,
        message: str,
        empathy_level: str = "moderate"
    ) -> str:
        """
        Mejorar mensaje con elementos empáticos.
        
        Args:
            message: Mensaje original
            empathy_level: Nivel de empatía (low, moderate, high)
            
        Returns:
            Mensaje mejorado
        """
        if empathy_level == "low":
            return message
        
        elif empathy_level == "moderate":
            # Añadir suavizadores
            message = message.replace("debes", "podrías considerar")
            message = message.replace("tienes que", "sería bueno que")
            message = message.replace("no puedes", "actualmente no es posible")
        
        elif empathy_level == "high":
            # Transformación más profunda
            message = self._add_empathy_markers(message)
            message = self._soften_directives(message)
            message = self._add_personal_touch(message)
        
        return message
    
    def _add_empathy_markers(self, text: str) -> str:
        """Añadir marcadores de empatía al texto."""
        # Añadir frases empáticas al inicio si no las tiene
        empathy_starters = [
            "Entiendo que", "Comprendo que", "Me doy cuenta de que"
        ]
        
        if not any(text.startswith(starter) for starter in empathy_starters):
            if "?" in text:
                text = f"Entiendo tu pregunta. {text}"
            elif "no" in text.lower():
                text = f"Comprendo tu preocupación. {text}"
        
        return text
    
    def _soften_directives(self, text: str) -> str:
        """Suavizar directivas en el texto."""
        replacements = {
            "debes": "sería recomendable",
            "tienes que": "te sugiero que",
            "necesitas": "podría ser útil",
            "haz": "considera hacer",
            "no hagas": "preferiría evitar",
            "es necesario": "sería beneficioso"
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
    
    def _add_personal_touch(self, text: str) -> str:
        """Añadir toque personal al mensaje."""
        # Añadir expresiones de apoyo
        if "problema" in text.lower():
            text += " Estoy aquí para ayudarte a resolverlo."
        elif "difícil" in text.lower():
            text += " Juntos encontraremos la mejor solución."
        elif "no entiendo" in text.lower():
            text += " No te preocupes, lo explicaré de otra manera."
        
        return text
    
    async def generate_emotional_bridge(
        self,
        from_emotion: EmotionalState,
        to_emotion: EmotionalState,
        context: Dict[str, Any]
    ) -> str:
        """
        Generar frase puente entre estados emocionales.
        
        Args:
            from_emotion: Estado emocional actual
            to_emotion: Estado emocional deseado
            context: Contexto de conversación
            
        Returns:
            Frase puente empática
        """
        bridges = {
            (EmotionalState.FRUSTRATED, EmotionalState.SATISFIED): 
                "Entiendo tu frustración, y precisamente por eso quiero mostrarte cómo podemos solucionarlo",
            (EmotionalState.ANXIOUS, EmotionalState.CONFIDENT):
                "Es normal sentir inquietud, pero déjame mostrarte por qué puedes estar tranquilo",
            (EmotionalState.CONFUSED, EmotionalState.INTERESTED):
                "Sé que puede parecer complejo, pero verás que es más simple de lo que parece",
            (EmotionalState.SKEPTICAL, EmotionalState.CONVINCED):
                "Tu escepticismo es válido, por eso quiero compartir contigo datos concretos",
            (EmotionalState.NEUTRAL, EmotionalState.EXCITED):
                "Déjame mostrarte algo que creo que te va a entusiasmar"
        }
        
        bridge = bridges.get(
            (from_emotion, to_emotion),
            f"Notando cómo te sientes, creo que esto te ayudará"
        )
        
        return bridge