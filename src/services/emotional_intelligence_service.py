"""
Servicio de Inteligencia Emocional para NGX Voice Sales Agent.

Este servicio analiza el estado emocional del cliente en tiempo real
y proporciona insights para adaptar la conversación de manera empática
y efectiva.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import json

from src.integrations.supabase import supabase_client
from src.services.nlp_integration_service import NLPIntegrationService
from src.services.advanced_sentiment_service import AdvancedSentimentService
from src.integrations.elevenlabs.advanced_voice import EmotionalState

logger = logging.getLogger(__name__)

@dataclass
class EmotionalProfile:
    """Perfil emocional del cliente durante la conversación."""
    primary_emotion: EmotionalState
    confidence: float
    secondary_emotions: Dict[EmotionalState, float] = field(default_factory=dict)
    emotional_journey: List[Dict[str, Any]] = field(default_factory=list)
    triggers: List[str] = field(default_factory=list)
    emotional_velocity: float = 0.0  # Qué tan rápido cambian las emociones
    stability_score: float = 1.0     # Qué tan estable es emocionalmente

class EmotionalTrigger(str, Enum):
    """Triggers que causan cambios emocionales."""
    PRICE_MENTION = "price_mention"
    TECHNICAL_COMPLEXITY = "technical_complexity"
    TIME_PRESSURE = "time_pressure"
    COMPETITOR_COMPARISON = "competitor_comparison"
    FEATURE_LIMITATION = "feature_limitation"
    SUCCESS_STORY = "success_story"
    PERSONAL_BENEFIT = "personal_benefit"
    SOCIAL_PROOF = "social_proof"

class EmotionalIntelligenceService:
    """
    Servicio para análisis y gestión de inteligencia emocional.
    
    Características:
    - Detección de estado emocional en tiempo real
    - Tracking de journey emocional
    - Identificación de triggers emocionales
    - Predicción de cambios emocionales
    - Recomendaciones de respuesta empática
    """
    
    def __init__(self, nlp_service: NLPIntegrationService, 
                 sentiment_service: AdvancedSentimentService):
        """
        Inicializar servicio de inteligencia emocional.
        
        Args:
            nlp_service: Servicio de NLP para análisis de texto
            sentiment_service: Servicio avanzado de sentimientos
        """
        self.nlp_service = nlp_service
        self.sentiment_service = sentiment_service
        self.supabase = supabase_client
        
        # Mapeo de sentimientos a estados emocionales
        self.sentiment_to_emotion_map = {
            "positive": EmotionalState.SATISFIED,
            "very_positive": EmotionalState.EXCITED,
            "negative": EmotionalState.FRUSTRATED,
            "very_negative": EmotionalState.ANXIOUS,
            "neutral": EmotionalState.NEUTRAL,
            "mixed": EmotionalState.CONFUSED
        }
        
        # Palabras clave para detectar triggers
        self.trigger_keywords = {
            EmotionalTrigger.PRICE_MENTION: [
                "precio", "costo", "caro", "barato", "presupuesto", 
                "inversión", "pagar", "cuota", "mensualidad"
            ],
            EmotionalTrigger.TECHNICAL_COMPLEXITY: [
                "complicado", "difícil", "no entiendo", "confuso",
                "técnico", "complejo", "explicar", "cómo funciona"
            ],
            EmotionalTrigger.TIME_PRESSURE: [
                "urgente", "rápido", "ya", "ahora", "prisa",
                "tiempo", "cuándo", "demora", "esperar"
            ],
            EmotionalTrigger.COMPETITOR_COMPARISON: [
                "competencia", "otros", "comparar", "versus",
                "mejor que", "diferencia", "ventaja", "por qué ustedes"
            ],
            EmotionalTrigger.FEATURE_LIMITATION: [
                "no tiene", "falta", "necesito", "requiero",
                "sin", "pero no", "quisiera", "debería tener"
            ],
            EmotionalTrigger.SUCCESS_STORY: [
                "resultados", "casos", "éxito", "logros",
                "testimonios", "clientes", "experiencia", "prueba"
            ],
            EmotionalTrigger.PERSONAL_BENEFIT: [
                "yo", "mi", "me ayuda", "beneficio", "ganar",
                "mejorar", "solución", "resolver", "facilitar"
            ],
            EmotionalTrigger.SOCIAL_PROOF: [
                "quién usa", "empresas", "referencias", "popular",
                "recomendado", "conocido", "confían", "usan"
            ]
        }
        
    async def analyze_emotional_state(
        self, 
        messages: List[Dict[str, Any]], 
        customer_profile: Optional[Dict[str, Any]] = None
    ) -> EmotionalProfile:
        """
        Analizar el estado emocional actual del cliente.
        
        Args:
            messages: Historial de mensajes de la conversación
            customer_profile: Perfil del cliente (opcional)
            
        Returns:
            EmotionalProfile con análisis completo
        """
        try:
            if not messages:
                return EmotionalProfile(
                    primary_emotion=EmotionalState.NEUTRAL,
                    confidence=1.0
                )
            
            # Extraer mensajes del cliente
            customer_messages = [
                msg for msg in messages 
                if msg.get("role") == "customer"
            ]
            
            if not customer_messages:
                return EmotionalProfile(
                    primary_emotion=EmotionalState.NEUTRAL,
                    confidence=1.0
                )
            
            # Analizar último mensaje para estado actual
            latest_message = customer_messages[-1]
            current_emotion = await self._detect_emotion_from_message(latest_message)
            
            # Analizar journey emocional
            emotional_journey = await self._analyze_emotional_journey(customer_messages)
            
            # Detectar triggers
            triggers = await self._detect_emotional_triggers(customer_messages)
            
            # Calcular velocidad y estabilidad emocional
            velocity, stability = self._calculate_emotional_dynamics(emotional_journey)
            
            # Detectar emociones secundarias
            secondary_emotions = await self._detect_secondary_emotions(
                customer_messages[-3:] if len(customer_messages) > 3 else customer_messages
            )
            
            # Construir perfil completo
            profile = EmotionalProfile(
                primary_emotion=current_emotion["emotion"],
                confidence=current_emotion["confidence"],
                secondary_emotions=secondary_emotions,
                emotional_journey=emotional_journey,
                triggers=triggers,
                emotional_velocity=velocity,
                stability_score=stability
            )
            
            # Guardar análisis para analytics
            await self._store_emotional_analysis(profile, messages[0].get("conversation_id"))
            
            return profile
            
        except Exception as e:
            logger.error(f"Error analizando estado emocional: {e}")
            return EmotionalProfile(
                primary_emotion=EmotionalState.NEUTRAL,
                confidence=0.5
            )
    
    async def _detect_emotion_from_message(
        self, 
        message: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Detectar emoción de un mensaje específico.
        
        Args:
            message: Mensaje a analizar
            
        Returns:
            Dict con emoción detectada y confianza
        """
        text = message.get("content", "")
        
        # Análisis de sentimiento
        sentiment = await self.sentiment_service.analyze_sentiment(text)
        base_emotion = self.sentiment_to_emotion_map.get(
            sentiment.get("sentiment", "neutral"),
            EmotionalState.NEUTRAL
        )
        
        # Análisis de características lingüísticas
        linguistic_features = await self._analyze_linguistic_features(text)
        
        # Detectar emociones específicas por patrones
        if self._contains_keywords(text, ["no entiendo", "confundido", "explicar"]):
            return {"emotion": EmotionalState.CONFUSED, "confidence": 0.8}
        
        if self._contains_keywords(text, ["excelente", "perfecto", "genial", "wow"]):
            return {"emotion": EmotionalState.EXCITED, "confidence": 0.85}
        
        if self._contains_keywords(text, ["preocupado", "nervioso", "no estoy seguro"]):
            return {"emotion": EmotionalState.ANXIOUS, "confidence": 0.8}
        
        if self._contains_keywords(text, ["no me gusta", "molesto", "frustrante"]):
            return {"emotion": EmotionalState.FRUSTRATED, "confidence": 0.85}
        
        if self._contains_keywords(text, ["dudo", "no creo", "será verdad"]):
            return {"emotion": EmotionalState.SKEPTICAL, "confidence": 0.75}
        
        if self._contains_keywords(text, ["interesante", "cuéntame más", "quiero saber"]):
            return {"emotion": EmotionalState.INTERESTED, "confidence": 0.8}
        
        if self._contains_keywords(text, ["seguro", "claro", "definitivamente"]):
            return {"emotion": EmotionalState.CONFIDENT, "confidence": 0.8}
        
        if self._contains_keywords(text, ["listo", "hagámoslo", "quiero proceder"]):
            return {"emotion": EmotionalState.DECISIVE, "confidence": 0.85}
        
        # Ajustar confianza basada en características lingüísticas
        confidence = sentiment.get("confidence", 0.7)
        if linguistic_features.get("exclamations", 0) > 0:
            confidence += 0.1
        if linguistic_features.get("questions", 0) > 1:
            confidence += 0.05
        
        confidence = min(confidence, 0.95)
        
        return {"emotion": base_emotion, "confidence": confidence}
    
    async def _analyze_emotional_journey(
        self, 
        messages: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Analizar la evolución emocional durante la conversación.
        
        Args:
            messages: Lista de mensajes del cliente
            
        Returns:
            Journey emocional con timestamps
        """
        journey = []
        
        for msg in messages:
            emotion_data = await self._detect_emotion_from_message(msg)
            journey.append({
                "timestamp": msg.get("timestamp", datetime.now().isoformat()),
                "emotion": emotion_data["emotion"].value,
                "confidence": emotion_data["confidence"],
                "message_preview": msg.get("content", "")[:50] + "..."
            })
        
        return journey
    
    async def _detect_emotional_triggers(
        self, 
        messages: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Detectar triggers emocionales en los mensajes.
        
        Args:
            messages: Lista de mensajes del cliente
            
        Returns:
            Lista de triggers detectados
        """
        detected_triggers = set()
        
        for msg in messages:
            text = msg.get("content", "").lower()
            
            for trigger, keywords in self.trigger_keywords.items():
                if any(keyword in text for keyword in keywords):
                    detected_triggers.add(trigger.value)
        
        return list(detected_triggers)
    
    def _calculate_emotional_dynamics(
        self, 
        journey: List[Dict[str, Any]]
    ) -> Tuple[float, float]:
        """
        Calcular velocidad y estabilidad emocional.
        
        Args:
            journey: Journey emocional
            
        Returns:
            Tupla de (velocidad, estabilidad)
        """
        if len(journey) < 2:
            return 0.0, 1.0
        
        # Calcular cambios entre estados consecutivos
        changes = 0
        for i in range(1, len(journey)):
            if journey[i]["emotion"] != journey[i-1]["emotion"]:
                changes += 1
        
        # Velocidad: cambios por mensaje
        velocity = changes / len(journey)
        
        # Estabilidad: inverso de la velocidad
        stability = 1.0 - min(velocity, 0.9)
        
        return velocity, stability
    
    async def _detect_secondary_emotions(
        self, 
        recent_messages: List[Dict[str, Any]]
    ) -> Dict[EmotionalState, float]:
        """
        Detectar emociones secundarias en mensajes recientes.
        
        Args:
            recent_messages: Últimos mensajes del cliente
            
        Returns:
            Dict de emociones secundarias con confianza
        """
        emotion_counts = {}
        
        for msg in recent_messages:
            emotion_data = await self._detect_emotion_from_message(msg)
            emotion = emotion_data["emotion"]
            confidence = emotion_data["confidence"]
            
            if emotion in emotion_counts:
                emotion_counts[emotion] = max(emotion_counts[emotion], confidence)
            else:
                emotion_counts[emotion] = confidence
        
        # Remover la emoción más común (será la primaria)
        if emotion_counts:
            primary = max(emotion_counts.items(), key=lambda x: x[1])[0]
            emotion_counts.pop(primary, None)
        
        return emotion_counts
    
    async def _analyze_linguistic_features(self, text: str) -> Dict[str, Any]:
        """
        Analizar características lingüísticas del texto.
        
        Args:
            text: Texto a analizar
            
        Returns:
            Características lingüísticas
        """
        features = {
            "exclamations": text.count("!"),
            "questions": text.count("?"),
            "capitals": sum(1 for c in text if c.isupper()) / max(len(text), 1),
            "length": len(text),
            "ellipsis": text.count("...")
        }
        
        return features
    
    def _contains_keywords(self, text: str, keywords: List[str]) -> bool:
        """Verificar si el texto contiene palabras clave."""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in keywords)
    
    async def _store_emotional_analysis(
        self, 
        profile: EmotionalProfile,
        conversation_id: Optional[str]
    ) -> None:
        """
        Guardar análisis emocional en base de datos.
        
        Args:
            profile: Perfil emocional
            conversation_id: ID de conversación
        """
        if not conversation_id:
            return
        
        try:
            data = {
                "conversation_id": conversation_id,
                "primary_emotion": profile.primary_emotion.value,
                "confidence": profile.confidence,
                "secondary_emotions": {
                    k.value: v for k, v in profile.secondary_emotions.items()
                },
                "triggers": profile.triggers,
                "emotional_velocity": profile.emotional_velocity,
                "stability_score": profile.stability_score,
                "timestamp": datetime.now().isoformat()
            }
            
            await self.supabase.table("emotional_analysis").insert(data).execute()
            
        except Exception as e:
            logger.error(f"Error guardando análisis emocional: {e}")
    
    async def get_emotional_insights(
        self, 
        profile: EmotionalProfile
    ) -> Dict[str, Any]:
        """
        Obtener insights accionables del perfil emocional.
        
        Args:
            profile: Perfil emocional
            
        Returns:
            Insights y recomendaciones
        """
        insights = {
            "current_state": profile.primary_emotion.value,
            "confidence": profile.confidence,
            "emotional_trend": self._determine_trend(profile.emotional_journey),
            "risk_indicators": [],
            "opportunities": [],
            "recommended_approach": "",
            "voice_recommendations": {}
        }
        
        # Análisis de riesgos
        if profile.emotional_velocity > 0.5:
            insights["risk_indicators"].append("Alta volatilidad emocional")
        
        if profile.primary_emotion in [EmotionalState.FRUSTRATED, EmotionalState.ANXIOUS]:
            insights["risk_indicators"].append("Estado emocional negativo")
        
        if EmotionalTrigger.PRICE_MENTION in profile.triggers:
            insights["risk_indicators"].append("Sensibilidad al precio detectada")
        
        # Identificar oportunidades
        if profile.primary_emotion == EmotionalState.INTERESTED:
            insights["opportunities"].append("Alto interés - momento para profundizar")
        
        if profile.primary_emotion == EmotionalState.DECISIVE:
            insights["opportunities"].append("Listo para tomar decisión - cerrar venta")
        
        if profile.stability_score > 0.8:
            insights["opportunities"].append("Cliente emocionalmente estable")
        
        # Recomendar enfoque
        approach_map = {
            EmotionalState.ANXIOUS: "Enfoque calmante y tranquilizador",
            EmotionalState.FRUSTRATED: "Validación y solución de problemas",
            EmotionalState.CONFUSED: "Clarificación y educación simple",
            EmotionalState.SKEPTICAL: "Pruebas sociales y garantías",
            EmotionalState.INTERESTED: "Profundización y beneficios",
            EmotionalState.DECISIVE: "Facilitación del cierre",
            EmotionalState.EXCITED: "Mantener momentum positivo"
        }
        
        insights["recommended_approach"] = approach_map.get(
            profile.primary_emotion,
            "Mantener tono neutral y profesional"
        )
        
        # Recomendaciones de voz
        insights["voice_recommendations"] = {
            "emotional_state": profile.primary_emotion.value,
            "speaking_rate": self._recommend_speaking_rate(profile),
            "energy_level": self._recommend_energy_level(profile),
            "empathy_level": self._recommend_empathy_level(profile)
        }
        
        return insights
    
    def _determine_trend(self, journey: List[Dict[str, Any]]) -> str:
        """Determinar tendencia emocional."""
        if len(journey) < 2:
            return "estable"
        
        # Mapeo de emociones a valores numéricos
        emotion_values = {
            EmotionalState.FRUSTRATED.value: -2,
            EmotionalState.ANXIOUS.value: -1,
            EmotionalState.CONFUSED.value: -0.5,
            EmotionalState.SKEPTICAL.value: -0.5,
            EmotionalState.NEUTRAL.value: 0,
            EmotionalState.INTERESTED.value: 1,
            EmotionalState.CONFIDENT.value: 1,
            EmotionalState.SATISFIED.value: 1.5,
            EmotionalState.EXCITED.value: 2,
            EmotionalState.DECISIVE.value: 2
        }
        
        # Calcular cambio entre inicio y fin
        start_value = emotion_values.get(journey[0]["emotion"], 0)
        end_value = emotion_values.get(journey[-1]["emotion"], 0)
        
        change = end_value - start_value
        
        if change > 0.5:
            return "mejorando"
        elif change < -0.5:
            return "deteriorando"
        else:
            return "estable"
    
    def _recommend_speaking_rate(self, profile: EmotionalProfile) -> str:
        """Recomendar velocidad de habla basada en perfil."""
        if profile.primary_emotion in [EmotionalState.ANXIOUS, EmotionalState.CONFUSED]:
            return "lenta"
        elif profile.primary_emotion in [EmotionalState.EXCITED, EmotionalState.DECISIVE]:
            return "moderada-rápida"
        else:
            return "moderada"
    
    def _recommend_energy_level(self, profile: EmotionalProfile) -> str:
        """Recomendar nivel de energía basado en perfil."""
        if profile.primary_emotion in [EmotionalState.ANXIOUS, EmotionalState.FRUSTRATED]:
            return "calmada"
        elif profile.primary_emotion in [EmotionalState.EXCITED, EmotionalState.INTERESTED]:
            return "alta"
        else:
            return "moderada"
    
    def _recommend_empathy_level(self, profile: EmotionalProfile) -> str:
        """Recomendar nivel de empatía basado en perfil."""
        if profile.primary_emotion in [EmotionalState.FRUSTRATED, EmotionalState.ANXIOUS]:
            return "muy alta"
        elif profile.primary_emotion in [EmotionalState.CONFUSED, EmotionalState.SKEPTICAL]:
            return "alta"
        else:
            return "moderada"