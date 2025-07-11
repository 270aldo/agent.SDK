"""
Servicio de Personalidad Adaptativa para NGX Voice Sales Agent.

Este servicio adapta la personalidad y estilo de comunicación del agente
basándose en el perfil psicológico y preferencias del cliente para
maximizar la conexión y efectividad de la venta.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import json

from src.integrations.supabase import supabase_client
from src.integrations.elevenlabs.advanced_voice import VoicePersona
from src.services.emotional_intelligence_service import EmotionalProfile

logger = logging.getLogger(__name__)

class CommunicationStyle(str, Enum):
    """Estilos de comunicación adaptados del modelo DISC."""
    ANALYTICAL = "analytical"      # Detallado, datos, lógico
    DRIVER = "driver"              # Directo, resultados, eficiente
    EXPRESSIVE = "expressive"      # Emocional, entusiasta, social
    AMIABLE = "amiable"           # Paciente, amigable, cooperativo
    TECHNICAL = "technical"        # Técnico, preciso, experto
    VISIONARY = "visionary"        # Inspirador, futuro, posibilidades
    PRAGMATIC = "pragmatic"        # Práctico, realista, tangible
    NURTURING = "nurturing"        # Cuidadoso, protector, guía

class PersonalityTrait(str, Enum):
    """Rasgos de personalidad del modelo Big Five."""
    OPENNESS = "openness"                # Apertura a experiencias
    CONSCIENTIOUSNESS = "conscientiousness"  # Responsabilidad
    EXTRAVERSION = "extraversion"        # Extroversión
    AGREEABLENESS = "agreeableness"     # Amabilidad
    NEUROTICISM = "neuroticism"          # Neuroticismo/Estabilidad

@dataclass
class PersonalityProfile:
    """Perfil de personalidad completo del cliente."""
    communication_style: CommunicationStyle
    primary_traits: Dict[PersonalityTrait, float] = field(default_factory=dict)
    decision_style: str = "collaborative"  # analytical, intuitive, collaborative, decisive
    risk_tolerance: float = 0.5           # 0 (aversión) - 1 (buscador)
    pace_preference: str = "moderate"     # slow, moderate, fast
    detail_orientation: float = 0.5       # 0 (big picture) - 1 (detail focused)
    social_preference: str = "balanced"   # task-focused, balanced, people-focused
    
@dataclass
class AdaptedCommunication:
    """Comunicación adaptada al perfil de personalidad."""
    message_structure: str          # Estructura del mensaje
    vocabulary_level: str           # simple, moderate, complex
    example_types: List[str]        # Tipos de ejemplos a usar
    proof_elements: List[str]       # Elementos de prueba preferidos
    pacing_recommendation: str      # Velocidad de comunicación
    voice_characteristics: Dict[str, Any]  # Características de voz

class AdaptivePersonalityService:
    """
    Servicio para adaptar la personalidad del agente al cliente.
    
    Características:
    - Detección de estilo de comunicación
    - Adaptación de personalidad en tiempo real
    - Matching de estilos para rapport
    - Personalización cultural
    - Optimización de decisión
    """
    
    def __init__(self):
        """Inicializar servicio de personalidad adaptativa."""
        self.supabase = supabase_client
        self.style_indicators = self._initialize_style_indicators()
        self.adaptation_strategies = self._initialize_adaptation_strategies()
        
    def _initialize_style_indicators(self) -> Dict[CommunicationStyle, Dict[str, Any]]:
        """Inicializar indicadores para detectar estilos de comunicación."""
        return {
            CommunicationStyle.ANALYTICAL: {
                "keywords": ["datos", "cifras", "evidencia", "análisis", "específicamente", 
                           "exactamente", "detalles", "comparar", "métricas"],
                "patterns": ["¿Cuáles son los números?", "¿Puedes ser más específico?", 
                           "¿Hay estudios que lo respalden?"],
                "response_preference": "detailed_data",
                "decision_speed": "slow"
            },
            CommunicationStyle.DRIVER: {
                "keywords": ["resultados", "rápido", "directo", "eficiente", "objetivo",
                           "meta", "lograr", "conseguir", "ahora"],
                "patterns": ["Al grano", "¿Cuál es el resultado?", "No tengo mucho tiempo"],
                "response_preference": "brief_results",
                "decision_speed": "fast"
            },
            CommunicationStyle.EXPRESSIVE: {
                "keywords": ["emocionante", "increíble", "sentir", "experiencia", "wow",
                           "genial", "fantástico", "amor", "pasión"],
                "patterns": ["¡Esto es increíble!", "Me encanta", "¡Qué emocionante!"],
                "response_preference": "enthusiastic_stories",
                "decision_speed": "moderate"
            },
            CommunicationStyle.AMIABLE: {
                "keywords": ["equipo", "juntos", "ayudar", "apoyar", "cómodo",
                           "seguro", "tranquilo", "confianza", "relación"],
                "patterns": ["¿Cómo ayuda esto a mi equipo?", "Necesito sentirme seguro"],
                "response_preference": "supportive_guidance",
                "decision_speed": "slow"
            },
            CommunicationStyle.TECHNICAL: {
                "keywords": ["API", "integración", "arquitectura", "protocolo", "algoritmo",
                           "framework", "stack", "deployment", "specs"],
                "patterns": ["¿Cómo se integra?", "¿Qué tecnología usa?", "¿Es escalable?"],
                "response_preference": "technical_depth",
                "decision_speed": "moderate"
            },
            CommunicationStyle.VISIONARY: {
                "keywords": ["futuro", "innovación", "transformar", "revolucionar", "visión",
                           "potencial", "posibilidades", "cambiar", "impacto"],
                "patterns": ["¿Cómo esto cambia el futuro?", "¿Cuál es la visión?"],
                "response_preference": "future_possibilities",
                "decision_speed": "fast"
            },
            CommunicationStyle.PRAGMATIC: {
                "keywords": ["práctico", "funciona", "realidad", "concreto", "tangible",
                           "implementar", "costo-beneficio", "ROI", "viable"],
                "patterns": ["¿Cómo funciona en la práctica?", "¿Cuál es el ROI real?"],
                "response_preference": "practical_examples",
                "decision_speed": "moderate"
            },
            CommunicationStyle.NURTURING: {
                "keywords": ["cuidar", "proteger", "bienestar", "desarrollo", "crecer",
                           "aprender", "mejorar", "guiar", "educar"],
                "patterns": ["¿Cómo esto cuida a mi gente?", "¿Ayuda al desarrollo?"],
                "response_preference": "growth_focused",
                "decision_speed": "slow"
            }
        }
    
    def _initialize_adaptation_strategies(self) -> Dict[CommunicationStyle, Dict[str, Any]]:
        """Inicializar estrategias de adaptación por estilo."""
        return {
            CommunicationStyle.ANALYTICAL: {
                "message_structure": "datos→análisis→conclusión→recomendación",
                "vocabulary": "preciso y técnico",
                "proof_types": ["estudios", "estadísticas", "comparativas", "ROI calculado"],
                "voice_recommendation": {
                    "pace": "moderado",
                    "tone": "profesional",
                    "persona": VoicePersona.CONSULTANT
                }
            },
            CommunicationStyle.DRIVER: {
                "message_structure": "resultado→beneficio→acción",
                "vocabulary": "directo y conciso",
                "proof_types": ["casos de éxito", "resultados rápidos", "ROI directo"],
                "voice_recommendation": {
                    "pace": "rápido",
                    "tone": "asertivo",
                    "persona": VoicePersona.CLOSER
                }
            },
            CommunicationStyle.EXPRESSIVE: {
                "message_structure": "historia→emoción→visión→inspiración",
                "vocabulary": "emotivo y descriptivo",
                "proof_types": ["testimonios emotivos", "historias de transformación"],
                "voice_recommendation": {
                    "pace": "energético",
                    "tone": "entusiasta",
                    "persona": VoicePersona.WELCOMER
                }
            },
            CommunicationStyle.AMIABLE: {
                "message_structure": "relación→seguridad→apoyo→decisión conjunta",
                "vocabulary": "cálido y colaborativo",
                "proof_types": ["garantías", "soporte continuo", "comunidad"],
                "voice_recommendation": {
                    "pace": "pausado",
                    "tone": "amigable",
                    "persona": VoicePersona.SUPPORTER
                }
            }
        }
    
    async def analyze_personality(
        self,
        messages: List[Dict[str, Any]],
        customer_profile: Optional[Dict[str, Any]] = None,
        behavioral_data: Optional[Dict[str, Any]] = None
    ) -> PersonalityProfile:
        """
        Analizar personalidad del cliente basado en comunicación.
        
        Args:
            messages: Historial de mensajes
            customer_profile: Perfil del cliente
            behavioral_data: Datos de comportamiento
            
        Returns:
            PersonalityProfile completo
        """
        try:
            # Extraer mensajes del cliente
            customer_messages = [
                msg for msg in messages 
                if msg.get("role") == "customer"
            ]
            
            if not customer_messages:
                return self._default_personality_profile()
            
            # Detectar estilo de comunicación
            communication_style = await self._detect_communication_style(customer_messages)
            
            # Analizar rasgos Big Five
            personality_traits = await self._analyze_big_five_traits(customer_messages)
            
            # Determinar estilo de decisión
            decision_style = await self._analyze_decision_style(
                customer_messages, 
                behavioral_data
            )
            
            # Calcular tolerancia al riesgo
            risk_tolerance = await self._calculate_risk_tolerance(
                customer_messages,
                customer_profile
            )
            
            # Determinar preferencias
            pace_preference = self._determine_pace_preference(customer_messages)
            detail_orientation = self._calculate_detail_orientation(customer_messages)
            social_preference = self._determine_social_preference(customer_messages)
            
            # Construir perfil
            profile = PersonalityProfile(
                communication_style=communication_style,
                primary_traits=personality_traits,
                decision_style=decision_style,
                risk_tolerance=risk_tolerance,
                pace_preference=pace_preference,
                detail_orientation=detail_orientation,
                social_preference=social_preference
            )
            
            # Guardar análisis
            await self._store_personality_analysis(
                profile, 
                messages[0].get("conversation_id")
            )
            
            return profile
            
        except Exception as e:
            logger.error(f"Error analizando personalidad: {e}")
            return self._default_personality_profile()
    
    async def _detect_communication_style(
        self, 
        messages: List[Dict[str, Any]]
    ) -> CommunicationStyle:
        """
        Detectar estilo de comunicación dominante.
        
        Args:
            messages: Mensajes del cliente
            
        Returns:
            Estilo de comunicación detectado
        """
        style_scores = {style: 0 for style in CommunicationStyle}
        
        for msg in messages:
            text = msg.get("content", "").lower()
            
            for style, indicators in self.style_indicators.items():
                # Contar keywords
                for keyword in indicators["keywords"]:
                    if keyword in text:
                        style_scores[style] += 1
                
                # Buscar patrones
                for pattern in indicators["patterns"]:
                    if pattern.lower() in text:
                        style_scores[style] += 2
        
        # Determinar estilo dominante
        if max(style_scores.values()) == 0:
            return CommunicationStyle.AMIABLE  # Default amigable
        
        return max(style_scores.items(), key=lambda x: x[1])[0]
    
    async def _analyze_big_five_traits(
        self, 
        messages: List[Dict[str, Any]]
    ) -> Dict[PersonalityTrait, float]:
        """
        Analizar rasgos Big Five de personalidad.
        
        Args:
            messages: Mensajes del cliente
            
        Returns:
            Puntuaciones de rasgos (0-1)
        """
        traits = {
            PersonalityTrait.OPENNESS: 0.5,
            PersonalityTrait.CONSCIENTIOUSNESS: 0.5,
            PersonalityTrait.EXTRAVERSION: 0.5,
            PersonalityTrait.AGREEABLENESS: 0.5,
            PersonalityTrait.NEUROTICISM: 0.5
        }
        
        # Indicadores lingüísticos simplificados
        for msg in messages:
            text = msg.get("content", "").lower()
            
            # Openness - vocabulario variado, ideas nuevas
            if any(word in text for word in ["innovador", "creativo", "nuevo", "diferente"]):
                traits[PersonalityTrait.OPENNESS] += 0.1
            
            # Conscientiousness - organización, planificación
            if any(word in text for word in ["plan", "organizar", "detalles", "proceso"]):
                traits[PersonalityTrait.CONSCIENTIOUSNESS] += 0.1
            
            # Extraversion - energía social
            if len(text) > 100 or text.count("!") > 1:
                traits[PersonalityTrait.EXTRAVERSION] += 0.1
            
            # Agreeableness - cooperación
            if any(word in text for word in ["ayudar", "juntos", "colaborar", "equipo"]):
                traits[PersonalityTrait.AGREEABLENESS] += 0.1
            
            # Neuroticism - ansiedad, preocupación
            if any(word in text for word in ["preocupado", "nervioso", "ansioso", "temo"]):
                traits[PersonalityTrait.NEUROTICISM] += 0.1
        
        # Normalizar valores
        for trait in traits:
            traits[trait] = min(1.0, max(0.0, traits[trait]))
        
        return traits
    
    async def _analyze_decision_style(
        self,
        messages: List[Dict[str, Any]],
        behavioral_data: Optional[Dict[str, Any]]
    ) -> str:
        """
        Analizar estilo de toma de decisiones.
        
        Args:
            messages: Mensajes del cliente
            behavioral_data: Datos de comportamiento
            
        Returns:
            Estilo de decisión
        """
        # Contar indicadores
        analytical_indicators = 0
        intuitive_indicators = 0
        collaborative_indicators = 0
        decisive_indicators = 0
        
        for msg in messages:
            text = msg.get("content", "").lower()
            
            if any(word in text for word in ["analizar", "comparar", "datos"]):
                analytical_indicators += 1
            if any(word in text for word in ["siento", "intuición", "corazonada"]):
                intuitive_indicators += 1
            if any(word in text for word in ["equipo", "consultar", "opinión"]):
                collaborative_indicators += 1
            if any(word in text for word in ["decidir", "listo", "ahora"]):
                decisive_indicators += 1
        
        # Determinar estilo dominante
        styles = {
            "analytical": analytical_indicators,
            "intuitive": intuitive_indicators,
            "collaborative": collaborative_indicators,
            "decisive": decisive_indicators
        }
        
        return max(styles.items(), key=lambda x: x[1])[0]
    
    async def _calculate_risk_tolerance(
        self,
        messages: List[Dict[str, Any]],
        customer_profile: Optional[Dict[str, Any]]
    ) -> float:
        """
        Calcular tolerancia al riesgo (0-1).
        
        Args:
            messages: Mensajes del cliente
            customer_profile: Perfil del cliente
            
        Returns:
            Puntuación de tolerancia al riesgo
        """
        risk_score = 0.5  # Neutral por defecto
        
        # Analizar lenguaje
        for msg in messages:
            text = msg.get("content", "").lower()
            
            # Indicadores de aversión al riesgo
            if any(word in text for word in ["seguro", "garantía", "proteger", "riesgo"]):
                risk_score -= 0.1
            
            # Indicadores de búsqueda de riesgo
            if any(word in text for word in ["oportunidad", "aventura", "probar", "innovar"]):
                risk_score += 0.1
        
        # Ajustar por perfil si está disponible
        if customer_profile:
            age = customer_profile.get("age", 35)
            if age < 30:
                risk_score += 0.1
            elif age > 50:
                risk_score -= 0.1
        
        return min(1.0, max(0.0, risk_score))
    
    def _determine_pace_preference(self, messages: List[Dict[str, Any]]) -> str:
        """Determinar preferencia de ritmo de conversación."""
        avg_message_length = sum(
            len(msg.get("content", "")) for msg in messages
        ) / max(len(messages), 1)
        
        response_times = []  # TODO: Implementar análisis de tiempos
        
        if avg_message_length < 50:
            return "fast"
        elif avg_message_length > 150:
            return "slow"
        else:
            return "moderate"
    
    def _calculate_detail_orientation(self, messages: List[Dict[str, Any]]) -> float:
        """Calcular orientación al detalle (0-1)."""
        detail_indicators = 0
        total_indicators = 0
        
        for msg in messages:
            text = msg.get("content", "").lower()
            total_indicators += 1
            
            if any(word in text for word in ["específico", "detalle", "exacto", "preciso"]):
                detail_indicators += 1
            if "?" in text and len(text) > 50:
                detail_indicators += 0.5
        
        return detail_indicators / max(total_indicators, 1)
    
    def _determine_social_preference(self, messages: List[Dict[str, Any]]) -> str:
        """Determinar preferencia social."""
        people_references = 0
        task_references = 0
        
        for msg in messages:
            text = msg.get("content", "").lower()
            
            # Referencias a personas
            if any(word in text for word in ["equipo", "gente", "personas", "nosotros"]):
                people_references += 1
            
            # Referencias a tareas
            if any(word in text for word in ["objetivo", "tarea", "proceso", "resultado"]):
                task_references += 1
        
        if people_references > task_references * 1.5:
            return "people-focused"
        elif task_references > people_references * 1.5:
            return "task-focused"
        else:
            return "balanced"
    
    def _default_personality_profile(self) -> PersonalityProfile:
        """Perfil de personalidad por defecto."""
        return PersonalityProfile(
            communication_style=CommunicationStyle.AMIABLE,
            primary_traits={
                PersonalityTrait.OPENNESS: 0.5,
                PersonalityTrait.CONSCIENTIOUSNESS: 0.5,
                PersonalityTrait.EXTRAVERSION: 0.5,
                PersonalityTrait.AGREEABLENESS: 0.6,
                PersonalityTrait.NEUROTICISM: 0.4
            }
        )
    
    async def adapt_communication(
        self,
        profile: PersonalityProfile,
        message: str,
        context: Dict[str, Any]
    ) -> AdaptedCommunication:
        """
        Adaptar comunicación al perfil de personalidad.
        
        Args:
            profile: Perfil de personalidad
            message: Mensaje a adaptar
            context: Contexto de conversación
            
        Returns:
            Comunicación adaptada
        """
        # Obtener estrategia base
        strategy = self.adaptation_strategies.get(
            profile.communication_style,
            self.adaptation_strategies[CommunicationStyle.AMIABLE]
        )
        
        # Determinar estructura del mensaje
        message_structure = strategy["message_structure"]
        
        # Determinar nivel de vocabulario
        if profile.detail_orientation > 0.7:
            vocabulary_level = "complex"
        elif profile.detail_orientation < 0.3:
            vocabulary_level = "simple"
        else:
            vocabulary_level = "moderate"
        
        # Seleccionar tipos de ejemplos
        example_types = self._select_example_types(profile)
        
        # Elementos de prueba preferidos
        proof_elements = strategy.get("proof_types", ["testimonios"])
        
        # Recomendación de ritmo
        pacing_recommendation = profile.pace_preference
        
        # Características de voz
        voice_characteristics = {
            "persona": strategy["voice_recommendation"]["persona"],
            "pace": strategy["voice_recommendation"]["pace"],
            "tone": strategy["voice_recommendation"]["tone"],
            "energy_adjustment": self._calculate_energy_adjustment(profile)
        }
        
        return AdaptedCommunication(
            message_structure=message_structure,
            vocabulary_level=vocabulary_level,
            example_types=example_types,
            proof_elements=proof_elements,
            pacing_recommendation=pacing_recommendation,
            voice_characteristics=voice_characteristics
        )
    
    def _select_example_types(self, profile: PersonalityProfile) -> List[str]:
        """Seleccionar tipos de ejemplos según perfil."""
        examples = []
        
        if profile.communication_style == CommunicationStyle.ANALYTICAL:
            examples = ["datos_comparativos", "métricas_específicas", "estudios_caso"]
        elif profile.communication_style == CommunicationStyle.EXPRESSIVE:
            examples = ["historias_inspiradoras", "transformaciones", "testimonios_emotivos"]
        elif profile.communication_style == CommunicationStyle.DRIVER:
            examples = ["resultados_rápidos", "ROI_claro", "casos_éxito_ejecutivos"]
        elif profile.communication_style == CommunicationStyle.TECHNICAL:
            examples = ["diagramas_técnicos", "arquitectura", "benchmarks"]
        else:
            examples = ["casos_diversos", "testimonios_variados", "ejemplos_prácticos"]
        
        return examples
    
    def _calculate_energy_adjustment(self, profile: PersonalityProfile) -> float:
        """Calcular ajuste de energía para la voz."""
        base_energy = 1.0
        
        # Ajustar por extroversión
        extraversion = profile.primary_traits.get(PersonalityTrait.EXTRAVERSION, 0.5)
        base_energy += (extraversion - 0.5) * 0.4
        
        # Ajustar por estilo de comunicación
        if profile.communication_style in [CommunicationStyle.EXPRESSIVE, CommunicationStyle.VISIONARY]:
            base_energy += 0.2
        elif profile.communication_style in [CommunicationStyle.ANALYTICAL, CommunicationStyle.AMIABLE]:
            base_energy -= 0.1
        
        return min(1.5, max(0.5, base_energy))
    
    async def _store_personality_analysis(
        self,
        profile: PersonalityProfile,
        conversation_id: Optional[str]
    ) -> None:
        """Guardar análisis de personalidad."""
        if not conversation_id:
            return
        
        try:
            data = {
                "conversation_id": conversation_id,
                "communication_style": profile.communication_style.value,
                "personality_traits": {
                    k.value: v for k, v in profile.primary_traits.items()
                },
                "decision_style": profile.decision_style,
                "risk_tolerance": profile.risk_tolerance,
                "pace_preference": profile.pace_preference,
                "detail_orientation": profile.detail_orientation,
                "social_preference": profile.social_preference,
                "timestamp": datetime.now().isoformat()
            }
            
            await self.supabase.table("personality_analysis").insert(data).execute()
            
        except Exception as e:
            logger.error(f"Error guardando análisis de personalidad: {e}")
    
    def generate_personality_insights(
        self, 
        profile: PersonalityProfile
    ) -> Dict[str, Any]:
        """
        Generar insights sobre la personalidad del cliente.
        
        Args:
            profile: Perfil de personalidad
            
        Returns:
            Insights y recomendaciones
        """
        insights = {
            "communication_style": profile.communication_style.value,
            "key_characteristics": [],
            "do_recommendations": [],
            "dont_recommendations": [],
            "closing_strategy": "",
            "objection_handling": ""
        }
        
        # Características clave
        if profile.communication_style == CommunicationStyle.ANALYTICAL:
            insights["key_characteristics"] = [
                "Orientado a datos y hechos",
                "Necesita tiempo para analizar",
                "Valora la precisión y exactitud"
            ]
            insights["do_recommendations"] = [
                "Proporcionar datos detallados y comparativas",
                "Usar lenguaje preciso y técnico",
                "Dar tiempo para procesar información"
            ]
            insights["dont_recommendations"] = [
                "Presionar para decisión rápida",
                "Usar generalizaciones",
                "Apelar solo a emociones"
            ]
            insights["closing_strategy"] = "Resumen lógico con ROI claro"
            insights["objection_handling"] = "Datos y evidencia concreta"
            
        elif profile.communication_style == CommunicationStyle.DRIVER:
            insights["key_characteristics"] = [
                "Orientado a resultados",
                "Toma decisiones rápidas",
                "Valora la eficiencia"
            ]
            insights["do_recommendations"] = [
                "Ir directo al punto",
                "Enfocarse en resultados y beneficios",
                "Ser conciso y eficiente"
            ]
            insights["dont_recommendations"] = [
                "Dar demasiados detalles",
                "Ser indeciso",
                "Perder tiempo en charla social"
            ]
            insights["closing_strategy"] = "Cierre directo con beneficios claros"
            insights["objection_handling"] = "Soluciones rápidas y directas"
        
        # Personalización por rasgos
        if profile.primary_traits.get(PersonalityTrait.NEUROTICISM, 0) > 0.6:
            insights["do_recommendations"].append("Proporcionar garantías y seguridad")
            insights["dont_recommendations"].append("Crear presión innecesaria")
        
        if profile.risk_tolerance < 0.3:
            insights["do_recommendations"].append("Enfatizar seguridad y estabilidad")
            insights["closing_strategy"] += " con garantías"
        
        return insights