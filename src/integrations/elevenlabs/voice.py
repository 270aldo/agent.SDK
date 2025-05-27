import logging
from typing import Optional, Dict, Any, Union, BinaryIO # Keep typing if used by class
from io import BytesIO # Keep BytesIO if used by class
# from dotenv import load_dotenv # Removed
# Importaciones correctas para la versión actual
from elevenlabs import VoiceSettings # Keep if used by class
from elevenlabs.client import ElevenLabs # Keep if used by class
from enum import Enum # Keep if used by class
import asyncio # Keep if used by class

from src.config import settings # Importar la configuración centralizada

# Configurar logging
logger = logging.getLogger(__name__)

# load_dotenv() is no longer needed here.

class ProgramVoice(str, Enum):
    """Voces predefinidas para cada programa."""
    PRIME_MALE = "prime_male"
    PRIME_FEMALE = "prime_female"
    LONGEVITY_MALE = "longevity_male"
    LONGEVITY_FEMALE = "longevity_female"

class VoiceEngine:
    """Motor de síntesis de voz utilizando ElevenLabs."""
    
    # Mapeo de voces de programa a ID de voz en ElevenLabs
    # Estos IDs son ejemplos y deben ser reemplazados por IDs reales
    VOICE_MAPPING = {
        "PRIME_MALE": "pNInz6obpgDQGcFmaJgB",      # Adam (ejemplo)
        "PRIME_FEMALE": "EXAVITQu4vr4xnSDxMaL",    # Nicole (ejemplo)
        "LONGEVITY_MALE": "VR6AewLTigWG4xSOukaG",  # Arnold (ejemplo)
        "LONGEVITY_FEMALE": "oWAxZDx7w5VEj9dCyTzz"  # Grace (ejemplo)
    }
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VoiceEngine, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Inicializar el motor de voz con la API key desde variables de entorno."""
        self.api_key = settings.ELEVENLABS_API_KEY # Use settings
        self.mock_mode = False
        
        if not self.api_key:
            logger.warning("Falta variable de entorno ELEVENLABS_API_KEY - usando modo simulado")
            self.mock_mode = True
        
        # Configuración para voces
        self.voice_settings = VoiceSettings(
            stability=0.71,
            similarity_boost=0.5,
            style=0.0,
            use_speaker_boost=True
        )
        
        # Inicializar cliente si no estamos en modo simulado
        if not self.mock_mode:
            try:
                self.client = ElevenLabs(api_key=self.api_key)
                logger.info("Motor de voz ElevenLabs inicializado")
            except Exception as e:
                logger.warning(f"Error al inicializar ElevenLabs: {e} - cambiando a modo simulado")
                self.mock_mode = True
        
        if self.mock_mode:
            logger.info("Motor de voz ElevenLabs en MODO SIMULADO")
    
    def get_voice_id(self, program_type: str, gender: str = "male") -> str:
        """
        Obtener ID de voz según programa y género.
        
        Args:
            program_type (str): Tipo de programa ("PRIME" o "LONGEVITY")
            gender (str): Género de la voz ("male" o "female")
            
        Returns:
            str: ID de voz en ElevenLabs
        """
        key = f"{program_type}_{gender}".upper()
        voice_id = self.VOICE_MAPPING.get(key)
        
        if not voice_id:
            logger.warning(f"No se encontró voz para {key}, usando voz por defecto")
            # Usar una voz por defecto si no hay mapeo específico
            voice_id = next(iter(self.VOICE_MAPPING.values()))
        
        return voice_id
    
    def text_to_speech(self, text: str, program_type: str = "PRIME", gender: str = "male") -> BytesIO:
        """
        Convertir texto a voz.
        
        Args:
            text (str): Texto a convertir a voz
            program_type (str): Tipo de programa ("PRIME" o "LONGEVITY")
            gender (str): Género de la voz ("male" o "female")
            
        Returns:
            BytesIO: Stream de audio
        """
        try:
            # Si estamos en modo simulado, devolver un stream vacío
            if self.mock_mode:
                logger.info(f"MODO SIMULADO: Texto que se convertiría a voz: {text[:50]}...")
                return BytesIO(b"audio_simulado")
                
            voice_id = self.get_voice_id(program_type, gender)
            
            # Utilizamos client.text_to_speech.convert según la API actual
            audio_generator = self.client.text_to_speech.convert(
                voice_id=voice_id,
                text=text,
                model_id="eleven_multilingual_v2",
                output_format="mp3_44100_128",
                voice_settings=self.voice_settings
            )
            
            # El método devuelve un generator, lo convertimos a bytes
            audio_bytes = b""
            try:
                # Si es un generador, combinamos todos los fragmentos
                for chunk in audio_generator:
                    if chunk:
                        audio_bytes += chunk
            except TypeError:
                # Si no es un generador (ya es bytes), lo usamos directamente
                audio_bytes = audio_generator
            
            # Convertir a BytesIO para devolver como stream
            audio_stream = BytesIO(audio_bytes)
            audio_stream.seek(0)  # Resetear posición para lectura
            
            return audio_stream
            
        except Exception as e:
            logger.error(f"Error al convertir texto a voz: {e}")
            if not self.mock_mode:
                logger.warning("Cambiando a modo simulado después del error")
                self.mock_mode = True
                return self.text_to_speech(text, program_type, gender)
            else:
                raise
    
    async def text_to_speech_async(self, text: str, program_type: str = "PRIME", gender: str = "male") -> BytesIO:
        """
        Convertir texto a voz de forma asíncrona.
        
        Args:
            text (str): Texto a convertir a voz
            program_type (str): Tipo de programa ("PRIME" o "LONGEVITY")
            gender (str): Género de la voz ("male" o "female")
            
        Returns:
            BytesIO: Stream de audio
        """
        # Usamos to_thread para ejecutar el método síncrono en un thread separado
        return await asyncio.to_thread(self.text_to_speech, text, program_type, gender)

# Singleton instance
voice_engine = VoiceEngine() 