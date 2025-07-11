"""
Sistema avanzado de síntesis de voz con ElevenLabs v3 Alpha.

Este módulo implementa capacidades mejoradas de voice synthesis incluyendo:
- Modelo Eleven v3 Alpha para máxima expresividad emocional
- Voice settings dinámicos basados en contexto
- Multi-voice support para diferentes etapas de venta
- Emotional voice morphing en tiempo real
"""

import os
import logging
from typing import Optional, Dict, Any, Union, List, Tuple
from io import BytesIO
from dataclasses import dataclass
from enum import Enum
import asyncio
from dotenv import load_dotenv

# Configurar logging
logger = logging.getLogger(__name__)

try:
    from elevenlabs import VoiceSettings, Voice
    from elevenlabs.client import ElevenLabs
except ImportError:
    logger.warning("ElevenLabs not installed. Voice features will be limited.")
    VoiceSettings = None
    Voice = None
    ElevenLabs = None

# Cargar variables de entorno
load_dotenv()

@dataclass
class EmotionalVoiceSettings:
    """Configuración de voz basada en estado emocional."""
    stability: float
    similarity_boost: float
    style: float
    use_speaker_boost: bool
    
    # Nuevos parámetros para control emocional
    speaking_rate: float = 1.0  # 0.5-2.0 (lento a rápido)
    pitch_variance: float = 1.0  # 0.5-2.0 (monótono a expresivo)
    energy_level: float = 1.0    # 0.5-2.0 (calmado a energético)

class EmotionalState(str, Enum):
    """Estados emocionales detectados en conversación."""
    NEUTRAL = "neutral"
    EXCITED = "excited"
    ANXIOUS = "anxious"
    FRUSTRATED = "frustrated"
    CONFUSED = "confused"
    CONFIDENT = "confident"
    SKEPTICAL = "skeptical"
    INTERESTED = "interested"
    SATISFIED = "satisfied"
    DECISIVE = "decisive"

class VoicePersona(str, Enum):
    """Personas de voz para diferentes etapas de venta."""
    WELCOMER = "welcomer"          # Bienvenida cálida
    EDUCATOR = "educator"          # Explicación clara
    CONSULTANT = "consultant"      # Asesoría experta
    NEGOTIATOR = "negotiator"      # Manejo de objeciones
    CLOSER = "closer"              # Cierre autorizado
    SUPPORTER = "supporter"        # Soporte post-venta

class AdvancedVoiceEngine:
    """Motor avanzado de síntesis de voz con capacidades emocionales."""
    
    # Voice IDs actualizados para v3 Alpha (ejemplos - actualizar con IDs reales)
    VOICE_MAPPING = {
        # Voces principales por programa/género
        "PRIME_MALE": "pNInz6obpgDQGcFmaJgB",      # Voz energética masculina
        "PRIME_FEMALE": "EXAVITQu4vr4xnSDxMaL",    # Voz energética femenina
        "LONGEVITY_MALE": "VR6AewLTigWG4xSOukaG",  # Voz calmada masculina
        "LONGEVITY_FEMALE": "oWAxZDx7w5VEj9dCyTzz", # Voz calmada femenina
        
        # Voces especializadas por persona
        "WELCOMER": "21m00Tcm4TlvDq8ikWAM",        # Rachel - cálida y acogedora
        "EDUCATOR": "yoZ06aMxZJJ28mfd3POQ",        # Sam - clara y articulada
        "CONSULTANT": "AZnzlk1XvdvUeBnXmlld",      # Domi - profesional y confiable
        "NEGOTIATOR": "CYw3kZ02Hs0563khs1Fj",     # Dave - persuasivo y firme
        "CLOSER": "TX3LPaxmHKxFdv7VOQHJ",          # Marcus - autoritativo
        "SUPPORTER": "ThT5KcBeYPX3keUQqHPh",       # Sarah - empática y paciente
    }
    
    # Configuraciones emocionales optimizadas
    EMOTIONAL_SETTINGS = {
        EmotionalState.NEUTRAL: EmotionalVoiceSettings(
            stability=0.75, similarity_boost=0.75, style=0.0, 
            use_speaker_boost=True, speaking_rate=1.0, 
            pitch_variance=1.0, energy_level=1.0
        ),
        EmotionalState.EXCITED: EmotionalVoiceSettings(
            stability=0.65, similarity_boost=0.8, style=0.3,
            use_speaker_boost=True, speaking_rate=1.15,
            pitch_variance=1.3, energy_level=1.4
        ),
        EmotionalState.ANXIOUS: EmotionalVoiceSettings(
            stability=0.85, similarity_boost=0.7, style=0.1,
            use_speaker_boost=True, speaking_rate=0.95,
            pitch_variance=0.9, energy_level=0.8
        ),
        EmotionalState.FRUSTRATED: EmotionalVoiceSettings(
            stability=0.9, similarity_boost=0.65, style=0.0,
            use_speaker_boost=True, speaking_rate=0.9,
            pitch_variance=0.85, energy_level=0.7
        ),
        EmotionalState.CONFUSED: EmotionalVoiceSettings(
            stability=0.8, similarity_boost=0.7, style=0.1,
            use_speaker_boost=True, speaking_rate=0.85,
            pitch_variance=1.1, energy_level=0.9
        ),
        EmotionalState.CONFIDENT: EmotionalVoiceSettings(
            stability=0.7, similarity_boost=0.85, style=0.2,
            use_speaker_boost=True, speaking_rate=1.05,
            pitch_variance=1.1, energy_level=1.2
        ),
        EmotionalState.SKEPTICAL: EmotionalVoiceSettings(
            stability=0.8, similarity_boost=0.75, style=0.0,
            use_speaker_boost=True, speaking_rate=0.95,
            pitch_variance=0.95, energy_level=0.95
        ),
        EmotionalState.INTERESTED: EmotionalVoiceSettings(
            stability=0.7, similarity_boost=0.8, style=0.15,
            use_speaker_boost=True, speaking_rate=1.05,
            pitch_variance=1.15, energy_level=1.1
        ),
        EmotionalState.SATISFIED: EmotionalVoiceSettings(
            stability=0.75, similarity_boost=0.8, style=0.1,
            use_speaker_boost=True, speaking_rate=1.0,
            pitch_variance=1.05, energy_level=1.05
        ),
        EmotionalState.DECISIVE: EmotionalVoiceSettings(
            stability=0.65, similarity_boost=0.85, style=0.25,
            use_speaker_boost=True, speaking_rate=1.1,
            pitch_variance=1.0, energy_level=1.25
        )
    }
    
    def __init__(self):
        """Inicializar el motor avanzado de voz."""
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.mock_mode = False
        
        if not self.api_key:
            logger.warning("Falta ELEVENLABS_API_KEY - usando modo simulado")
            self.mock_mode = True
        
        # Inicializar cliente con v3 Alpha
        if not self.mock_mode:
            try:
                self.client = ElevenLabs(api_key=self.api_key)
                logger.info("Motor avanzado de voz ElevenLabs v3 Alpha inicializado")
            except Exception as e:
                logger.warning(f"Error al inicializar ElevenLabs: {e} - modo simulado")
                self.mock_mode = True
        
        # Cache de voces para performance
        self._voice_cache = {}
        
    def _get_emotional_settings(self, emotional_state: EmotionalState) -> VoiceSettings:
        """
        Obtener configuración de voz basada en estado emocional.
        
        Args:
            emotional_state: Estado emocional detectado
            
        Returns:
            VoiceSettings configurado para el estado emocional
        """
        settings = self.EMOTIONAL_SETTINGS.get(
            emotional_state, 
            self.EMOTIONAL_SETTINGS[EmotionalState.NEUTRAL]
        )
        
        return VoiceSettings(
            stability=settings.stability,
            similarity_boost=settings.similarity_boost,
            style=settings.style,
            use_speaker_boost=settings.use_speaker_boost
        )
    
    def _select_voice_by_context(
        self, 
        program_type: str,
        gender: str,
        persona: Optional[VoicePersona] = None,
        emotional_state: Optional[EmotionalState] = None
    ) -> str:
        """
        Seleccionar voz óptima basada en contexto completo.
        
        Args:
            program_type: Tipo de programa (PRIME/LONGEVITY)
            gender: Género de voz preferido
            persona: Persona de venta actual
            emotional_state: Estado emocional del cliente
            
        Returns:
            Voice ID óptimo para el contexto
        """
        # Si hay una persona específica, priorizar
        if persona and persona in self.VOICE_MAPPING:
            return self.VOICE_MAPPING[persona]
        
        # Para estados emocionales específicos, ajustar selección
        if emotional_state in [EmotionalState.ANXIOUS, EmotionalState.FRUSTRATED]:
            # Usar voces más calmadas para estados negativos
            if program_type == "PRIME":
                program_type = "LONGEVITY"  # Cambiar a voces más calmadas
        
        # Selección base por programa y género
        key = f"{program_type}_{gender}".upper()
        return self.VOICE_MAPPING.get(key, self.VOICE_MAPPING["PRIME_MALE"])
    
    async def text_to_speech_advanced(
        self,
        text: str,
        program_type: str = "PRIME",
        gender: str = "male",
        persona: Optional[VoicePersona] = None,
        emotional_state: Optional[EmotionalState] = None,
        language: str = "es",
        optimize_streaming: bool = False
    ) -> BytesIO:
        """
        Conversión avanzada de texto a voz con capacidades emocionales.
        
        Args:
            text: Texto a convertir
            program_type: Tipo de programa
            gender: Género de voz
            persona: Persona de venta actual
            emotional_state: Estado emocional detectado
            language: Idioma (soporta 70+ idiomas)
            optimize_streaming: Optimizar para streaming de baja latencia
            
        Returns:
            BytesIO con audio generado
        """
        try:
            if self.mock_mode or not ElevenLabs:
                logger.info(f"MODO SIMULADO - Texto: {text[:50]}...")
                logger.info(f"Configuración: {persona}, {emotional_state}, {language}")
                return BytesIO(b"audio_simulado_avanzado")
            
            # Seleccionar voz óptima
            voice_id = self._select_voice_by_context(
                program_type, gender, persona, emotional_state
            )
            
            # Obtener configuración emocional
            voice_settings = self._get_emotional_settings(
                emotional_state or EmotionalState.NEUTRAL
            )
            
            # Seleccionar modelo según necesidad
            if optimize_streaming:
                model_id = "eleven_flash_v2_5"  # Ultra-baja latencia (~75ms)
            else:
                model_id = "eleven_v3_alpha"    # Máxima calidad emocional
            
            # Generar audio con configuración avanzada
            audio_generator = self.client.text_to_speech.convert(
                voice_id=voice_id,
                text=text,
                model_id=model_id,
                output_format="mp3_44100_128",
                voice_settings=voice_settings,
                language_code=language
            )
            
            # Procesar audio
            audio_bytes = b""
            for chunk in audio_generator:
                if chunk:
                    audio_bytes += chunk
            
            audio_stream = BytesIO(audio_bytes)
            audio_stream.seek(0)
            
            # Log para analytics
            logger.info(f"Audio generado: {len(audio_bytes)} bytes, "
                       f"modelo: {model_id}, persona: {persona}, "
                       f"estado: {emotional_state}")
            
            return audio_stream
            
        except Exception as e:
            logger.error(f"Error en generación avanzada de voz: {e}")
            raise
    
    async def generate_multi_voice_conversation(
        self,
        conversation_parts: List[Dict[str, Any]]
    ) -> List[BytesIO]:
        """
        Generar conversación con múltiples voces/personas.
        
        Args:
            conversation_parts: Lista de partes de conversación con:
                - text: Texto a decir
                - persona: Persona que habla
                - emotional_state: Estado emocional
                
        Returns:
            Lista de streams de audio
        """
        audio_streams = []
        
        for part in conversation_parts:
            stream = await self.text_to_speech_advanced(
                text=part["text"],
                persona=part.get("persona", VoicePersona.CONSULTANT),
                emotional_state=part.get("emotional_state", EmotionalState.NEUTRAL)
            )
            audio_streams.append(stream)
        
        return audio_streams
    
    def get_voice_analytics(self) -> Dict[str, Any]:
        """Obtener analytics de uso de voces."""
        # TODO: Implementar tracking de uso
        return {
            "voices_available": len(self.VOICE_MAPPING),
            "emotional_states": len(self.EMOTIONAL_SETTINGS),
            "models_available": ["eleven_v3_alpha", "eleven_flash_v2_5"],
            "languages_supported": 70
        }

# Singleton instance
advanced_voice_engine = AdvancedVoiceEngine()