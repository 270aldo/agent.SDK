"""
Consultative Advisor Service - Consultor experto conversacional NGX.

Este servicio implementa un enfoque consultivo y conversacional para ventas NGX:
- Entiende las necesidades reales del cliente
- Hace preguntas inteligentes para diagnosticar
- Conecta problemas con soluciones NGX específicas
- Vende el HIE como diferenciador único
- Recomienda el tier CORRECTO para cada cliente

ENFOQUE: CONSULTOR EXPERTO, NO VENDEDOR AGRESIVO.
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json

# Import early adopter service for consultative presentation
from src.services.early_adopter_service import EarlyAdopterService, EarlyAdopterOffer

logger = logging.getLogger(__name__)


class ConsultationPhase(Enum):
    """Fases de la consultoría conversacional."""
    INITIAL_CONNECTION = "initial_connection"
    NEEDS_ASSESSMENT = "needs_assessment"
    PROBLEM_DIAGNOSIS = "problem_diagnosis"
    EDUCATION_NGX = "education_ngx"
    RECOMMENDATION = "recommendation"
    GENTLE_OBJECTION_HANDLING = "gentle_objection_handling"
    CONSULTATIVE_CLOSING = "consultative_closing"


class ClientArchetype(Enum):
    """Arquetipos de cliente basados en necesidades."""
    PERFORMANCE_OPTIMIZER = "performance_optimizer"  # PRIME candidate
    LONGEVITY_SEEKER = "longevity_seeker"           # LONGEVITY candidate
    HEALTH_CONSCIOUS = "health_conscious"            # General wellness
    EXECUTIVE_PERFORMER = "executive_performer"      # High-tier PRIME
    AGING_GRACEFULLY = "aging_gracefully"          # High-tier LONGEVITY


@dataclass
class ConsultativeRecommendation:
    """Recomendación consultiva basada en necesidades del cliente."""
    recommended_program: str  # PRIME or LONGEVITY
    recommended_tier: str     # Essential, Pro, Elite, Premium
    confidence_score: float
    reasoning: str
    key_benefits: List[str]
    addressing_concerns: List[str]
    client_archetype: ClientArchetype
    why_this_fits: str
    alternative_options: List[str]


class ConsultativeAdvisorService:
    """
    Servicio de consultoría conversacional para ventas NGX.
    
    Actúa como un consultor experto que:
    - Domina completamente NGX (PRIME/LONGEVITY)
    - Entiende fitness básico para conectar con el cliente
    - Vende de manera conversacional, no agresiva
    - Enfoca en encontrar LA SOLUCIÓN CORRECTA para cada cliente
    """
    
    def __init__(self):
        self.consultation_phases = self._initialize_consultation_framework()
        self.intelligent_questions = self._initialize_intelligent_questions()
        self.ngx_solutions_map = self._initialize_ngx_solutions()
        
        # Initialize early adopter service for consultative presentation
        self.early_adopter_service = EarlyAdopterService()
        
    def _initialize_consultation_framework(self) -> Dict[str, Dict]:
        """Inicializa el framework de consultoría conversacional."""
        return {
            ConsultationPhase.INITIAL_CONNECTION.value: {
                "objective": "Establecer confianza y entender contexto inicial",
                "approach": "Escucha activa, empatía, preguntas abiertas",
                "key_messages": [
                    "Mi objetivo es entender tu situación y ver si NGX puede ayudarte",
                    "No estoy aquí para venderte algo que no necesitas",
                    "Cuéntame qué te trajo hasta aquí hoy"
                ]
            },
            
            ConsultationPhase.NEEDS_ASSESSMENT.value: {
                "objective": "Identificar necesidades reales y problemas específicos",
                "approach": "Preguntas diagnósticas inteligentes",
                "key_questions": [
                    "¿Cuáles son tus principales desafíos en este momento?",
                    "¿Qué has intentado antes y cómo te ha funcionado?",
                    "¿Qué resultados ideales estarías buscando?"
                ]
            },
            
            ConsultationPhase.PROBLEM_DIAGNOSIS.value: {
                "objective": "Diagnosticar la raíz del problema",
                "approach": "Análisis consultivo, no sales pitch",
                "focus": "Entender el problema antes de ofrecer solución"
            },
            
            ConsultationPhase.EDUCATION_NGX.value: {
                "objective": "Educar sobre NGX como solución específica",
                "approach": "Conectar problemas específicos con capacidades NGX",
                "hie_emphasis": "HIE como diferenciador imposible de clonar"
            },
            
            ConsultationPhase.RECOMMENDATION.value: {
                "objective": "Recomendar la solución CORRECTA para el cliente",
                "approach": "Basado en necesidades, no en maximizar precio",
                "principle": "El tier correcto genera clientes felices a largo plazo"
            }
        }
    
    def _initialize_intelligent_questions(self) -> Dict[str, List[str]]:
        """Inicializa preguntas inteligentes para diagnóstico."""
        return {
            "lifestyle_assessment": [
                "¿Cómo es un día típico para ti?",
                "¿Qué parte de tu rutina actual sientes que no está funcionando?",
                "¿Tienes períodos del día donde tu energía baja drásticamente?"
            ],
            
            "goal_clarification": [
                "Si pudieras cambiar una cosa sobre tu bienestar actual, ¿qué sería?",
                "¿Qué te motivó a buscar una solución como NGX?",
                "¿Cómo sabrías que el programa está funcionando para ti?"
            ],
            
            "context_understanding": [
                "¿Has probado otros programas de wellness antes?",
                "¿Qué funcionó y qué no funcionó en esas experiencias?",
                "¿Tienes alguna condición de salud o limitación que deba considerar?"
            ],
            
            "priority_identification": [
                "¿Qué es más importante para ti: resultados rápidos o cambios sostenibles?",
                "¿Prefieres un enfoque más estructurado o más flexible?",
                "¿Qué rol juega la tecnología en tu vida diaria?"
            ],
            
            "commitment_assessment": [
                "¿Cuánto tiempo puedes dedicar realísticamente por día?",
                "¿Tienes apoyo de familia/pareja para hacer cambios?",
                "¿Qué podría interferir con tu consistencia en el programa?"
            ]
        }
    
    def _initialize_ngx_solutions(self) -> Dict[str, Dict]:
        """Mapea problemas específicos con soluciones NGX."""
        return {
            "low_energy": {
                "ngx_solution": "Optimización metabólica y circadiana",
                "program_fit": "PRIME",
                "hie_benefit": "Agentes especializados en energía y ciclos circadianos",
                "tier_guidance": "Pro+ para análisis completo de patrones energéticos"
            },
            
            "cognitive_performance": {
                "ngx_solution": "Optimización cognitiva y nootrópicos naturales",
                "program_fit": "PRIME",
                "hie_benefit": "IA especializada en rendimiento cognitivo",
                "tier_guidance": "Elite+ para análisis de brainwave y optimización"
            },
            
            "aging_concerns": {
                "ngx_solution": "Protocolos de longevidad y antiaging",
                "program_fit": "LONGEVITY",
                "hie_benefit": "Agentes especializados en biomarcadores de edad",
                "tier_guidance": "Pro+ para análisis predictivo de longevidad"
            },
            
            "stress_management": {
                "ngx_solution": "Adaptógenos y manejo de cortisol",
                "program_fit": "Ambos (depende de edad)",
                "hie_benefit": "Monitoreo continuo de marcadores de estrés",
                "tier_guidance": "Essential+ para comenzar, upgrade según progreso"
            },
            
            "fitness_plateau": {
                "ngx_solution": "Optimización hormonal y recovery",
                "program_fit": "PRIME",
                "hie_benefit": "Análisis de patrones de entrenamiento y recovery",
                "tier_guidance": "Pro+ para integración con wearables"
            },
            
            "preventive_health": {
                "ngx_solution": "Protocolos preventivos personalizados",
                "program_fit": "LONGEVITY",
                "hie_benefit": "Predicción de riesgos de salud",
                "tier_guidance": "Elite+ para análisis genético y biomarcadores"
            }
        }
    
    def analyze_client_needs(self, 
                           conversation_history: List[Dict],
                           user_profile: Dict) -> Dict[str, any]:
        """
        Analiza las necesidades del cliente basado en la conversación.
        
        Args:
            conversation_history: Historial completo de la conversación
            user_profile: Perfil del usuario (edad, profesión, etc.)
            
        Returns:
            Análisis completo de necesidades y problemas identificados
        """
        try:
            # Extraer información clave de la conversación
            key_concerns = self._extract_key_concerns(conversation_history)
            lifestyle_factors = self._analyze_lifestyle(conversation_history, user_profile)
            goals_priorities = self._identify_goals_and_priorities(conversation_history)
            
            # Identificar archetype del cliente
            client_archetype = self._determine_client_archetype(
                key_concerns, lifestyle_factors, user_profile
            )
            
            return {
                "key_concerns": key_concerns,
                "lifestyle_factors": lifestyle_factors,
                "goals_priorities": goals_priorities,
                "client_archetype": client_archetype,
                "readiness_level": self._assess_readiness_level(conversation_history),
                "consultation_phase": self._determine_current_phase(conversation_history)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing client needs: {str(e)}")
            return self._fallback_needs_analysis()
    
    def generate_consultative_response(self,
                                     client_message: str,
                                     needs_analysis: Dict,
                                     conversation_context: Dict) -> Dict[str, any]:
        """
        Genera respuesta consultiva basada en las necesidades del cliente.
        
        Args:
            client_message: Último mensaje del cliente
            needs_analysis: Análisis de necesidades del cliente
            conversation_context: Contexto de la conversación
            
        Returns:
            Respuesta consultiva apropiada para la fase actual
        """
        try:
            current_phase = needs_analysis.get("consultation_phase", ConsultationPhase.INITIAL_CONNECTION)
            client_archetype = needs_analysis.get("client_archetype")
            
            # Generar respuesta según la fase
            if current_phase == ConsultationPhase.INITIAL_CONNECTION:
                response = self._generate_connection_response(client_message, needs_analysis)
                
            elif current_phase == ConsultationPhase.NEEDS_ASSESSMENT:
                response = self._generate_assessment_response(client_message, needs_analysis)
                
            elif current_phase == ConsultationPhase.PROBLEM_DIAGNOSIS:
                response = self._generate_diagnostic_response(client_message, needs_analysis)
                
            elif current_phase == ConsultationPhase.EDUCATION_NGX:
                response = self._generate_education_response(client_message, needs_analysis)
                
            elif current_phase == ConsultationPhase.RECOMMENDATION:
                response = self._generate_recommendation_response(client_message, needs_analysis)
                
            else:
                response = self._generate_general_consultive_response(client_message, needs_analysis)
            
            # Siempre incluir contexto HIE de manera natural
            response = self._integrate_hie_naturally(response, current_phase)
            
            return {
                "response": response,
                "consultation_phase": current_phase.value,
                "next_recommended_phase": self._suggest_next_phase(current_phase, needs_analysis),
                "intelligent_questions": self._suggest_next_questions(current_phase, needs_analysis)
            }
            
        except Exception as e:
            logger.error(f"Error generating consultative response: {str(e)}")
            return self._fallback_consultive_response(client_message)
    
    def generate_tier_recommendation(self,
                                   needs_analysis: Dict,
                                   user_profile: Dict) -> ConsultativeRecommendation:
        """
        Genera recomendación de tier basada en NECESIDADES, no en billetera.
        
        Args:
            needs_analysis: Análisis completo de necesidades
            user_profile: Perfil del usuario
            
        Returns:
            Recomendación consultiva del tier apropiado
        """
        try:
            key_concerns = needs_analysis.get("key_concerns", [])
            client_archetype = needs_analysis.get("client_archetype")
            lifestyle_factors = needs_analysis.get("lifestyle_factors", {})
            
            # Determinar programa (PRIME vs LONGEVITY)
            recommended_program = self._determine_optimal_program(
                user_profile, key_concerns, client_archetype
            )
            
            # Determinar tier basado en NECESIDADES
            recommended_tier = self._determine_optimal_tier_by_needs(
                key_concerns, lifestyle_factors, user_profile
            )
            
            # Construir razonamiento
            reasoning = self._build_consultive_reasoning(
                recommended_program, recommended_tier, key_concerns, client_archetype
            )
            
            # Identificar beneficios clave
            key_benefits = self._identify_key_benefits(
                recommended_program, recommended_tier, key_concerns
            )
            
            # Opciones alternativas
            alternative_options = self._suggest_alternatives(
                recommended_tier, user_profile
            )
            
            return ConsultativeRecommendation(
                recommended_program=recommended_program,
                recommended_tier=recommended_tier,
                confidence_score=self._calculate_recommendation_confidence(needs_analysis),
                reasoning=reasoning,
                key_benefits=key_benefits,
                addressing_concerns=key_concerns,
                client_archetype=client_archetype,
                why_this_fits=self._explain_why_this_fits(
                    recommended_program, recommended_tier, client_archetype
                ),
                alternative_options=alternative_options
            )
            
        except Exception as e:
            logger.error(f"Error generating tier recommendation: {str(e)}")
            return self._fallback_recommendation()
    
    def handle_objections_consultively(self,
                                     objection_message: str,
                                     current_recommendation: ConsultativeRecommendation,
                                     user_profile: Dict) -> Dict[str, any]:
        """
        Maneja objeciones de manera consultiva, no agresiva.
        
        Args:
            objection_message: Mensaje de objeción del cliente
            current_recommendation: Recomendación actual
            user_profile: Perfil del usuario
            
        Returns:
            Respuesta consultiva que aborda la objeción
        """
        try:
            objection_type = self._classify_objection(objection_message)
            
            if objection_type == "price_concern":
                return self._handle_price_objection_consultively(
                    objection_message, current_recommendation, user_profile
                )
            elif objection_type == "time_concern":
                return self._handle_time_objection_consultively(
                    objection_message, current_recommendation
                )
            elif objection_type == "skepticism":
                return self._handle_skepticism_consultively(
                    objection_message, current_recommendation
                )
            elif objection_type == "need_to_think":
                return self._handle_thinking_time_consultively(
                    objection_message, current_recommendation
                )
            else:
                return self._handle_general_objection_consultively(
                    objection_message, current_recommendation
                )
                
        except Exception as e:
            logger.error(f"Error handling objection consultively: {str(e)}")
            return self._fallback_objection_response()
    
    # ===== MÉTODOS PRIVADOS DE IMPLEMENTACIÓN =====
    
    def _extract_key_concerns(self, conversation_history: List[Dict]) -> List[str]:
        """Extrae las preocupaciones principales del cliente."""
        concerns = []
        
        # Buscar patrones de problemas mencionados
        concern_keywords = {
            "energy": ["cansado", "energía", "fatiga", "agotado"],
            "stress": ["estrés", "ansiedad", "presión", "abrumado"],
            "sleep": ["sueño", "insomnio", "dormir", "descanso"],
            "focus": ["concentración", "foco", "distracción", "productividad"],
            "health": ["salud", "prevención", "bienestar", "enfermedad"],
            "aging": ["edad", "envejecimiento", "vitalidad", "longevidad"],
            "fitness": ["ejercicio", "físico", "peso", "entrenamiento"]
        }
        
        user_messages = [
            msg["content"].lower() for msg in conversation_history 
            if msg.get("role") == "user"
        ]
        
        for concern, keywords in concern_keywords.items():
            for message in user_messages:
                if any(keyword in message for keyword in keywords):
                    if concern not in concerns:
                        concerns.append(concern)
                        
        return concerns
    
    def _analyze_lifestyle(self, conversation_history: List[Dict], user_profile: Dict) -> Dict:
        """Analiza factores de estilo de vida."""
        lifestyle = {
            "activity_level": "moderate",
            "stress_level": "moderate", 
            "schedule_flexibility": "moderate",
            "tech_comfort": "high",
            "age_group": self._categorize_age(user_profile.get("age", 35))
        }
        
        # Inferir del contenido de mensajes
        user_text = " ".join([
            msg["content"].lower() for msg in conversation_history 
            if msg.get("role") == "user"
        ])
        
        if any(word in user_text for word in ["ejecutivo", "ceo", "gerente", "empresa"]):
            lifestyle["stress_level"] = "high"
            lifestyle["schedule_flexibility"] = "low"
            
        if any(word in user_text for word in ["gym", "entrenamiento", "ejercicio", "activo"]):
            lifestyle["activity_level"] = "high"
            
        return lifestyle
    
    def _identify_goals_and_priorities(self, conversation_history: List[Dict]) -> Dict:
        """Identifica metas y prioridades del cliente."""
        goals = {
            "primary_goal": "general_wellness",
            "timeline": "3-6_months",
            "priority_level": "moderate"
        }
        
        user_text = " ".join([
            msg["content"].lower() for msg in conversation_history 
            if msg.get("role") == "user"
        ])
        
        # Detectar urgencia
        if any(word in user_text for word in ["urgente", "rápido", "inmediato", "ya"]):
            goals["timeline"] = "1-3_months"
            goals["priority_level"] = "high"
            
        # Detectar objetivo principal
        if any(word in user_text for word in ["rendimiento", "productividad", "trabajo"]):
            goals["primary_goal"] = "performance"
        elif any(word in user_text for word in ["salud", "prevención", "longevidad"]):
            goals["primary_goal"] = "health_longevity"
            
        return goals
    
    def _determine_client_archetype(self, concerns: List[str], lifestyle: Dict, user_profile: Dict) -> ClientArchetype:
        """Determina el arquetipo del cliente."""
        age = user_profile.get("age", 35)
        
        # Lógica para determinar arquetipo
        if age < 45 and "performance" in str(concerns):
            if lifestyle.get("stress_level") == "high":
                return ClientArchetype.EXECUTIVE_PERFORMER
            else:
                return ClientArchetype.PERFORMANCE_OPTIMIZER
        elif age >= 50:
            if "health" in concerns or "aging" in concerns:
                return ClientArchetype.AGING_GRACEFULLY
            else:
                return ClientArchetype.LONGEVITY_SEEKER
        else:
            return ClientArchetype.HEALTH_CONSCIOUS
    
    def _determine_current_phase(self, conversation_history: List[Dict]) -> ConsultationPhase:
        """Determina la fase actual de consultoría."""
        message_count = len([msg for msg in conversation_history if msg.get("role") == "user"])
        
        if message_count <= 2:
            return ConsultationPhase.INITIAL_CONNECTION
        elif message_count <= 5:
            return ConsultationPhase.NEEDS_ASSESSMENT
        elif message_count <= 8:
            return ConsultationPhase.PROBLEM_DIAGNOSIS
        elif message_count <= 12:
            return ConsultationPhase.EDUCATION_NGX
        else:
            return ConsultationPhase.RECOMMENDATION
    
    def _generate_connection_response(self, message: str, needs_analysis: Dict) -> str:
        """Genera respuesta para fase de conexión inicial."""
        return (
            "Me da mucho gusto conectar contigo. Mi objetivo es entender tu situación "
            "específica y ver cómo NGX podría ayudarte. No estoy aquí para venderte "
            "algo que no necesitas - mi trabajo es encontrar la solución correcta para ti. "
            "¿Puedes contarme qué te motivó a buscar una solución como NGX?"
        )
    
    def _generate_assessment_response(self, message: str, needs_analysis: Dict) -> str:
        """Genera respuesta para fase de evaluación de necesidades."""
        concerns = needs_analysis.get("key_concerns", [])
        
        if "energy" in concerns:
            return (
                "Entiendo que la energía es una preocupación importante para ti. "
                "Para poder recomendarte la mejor solución, necesito entender un poco más. "
                "¿En qué momentos del día sientes que tu energía baja más? ¿Y has "
                "identificado algún patrón o trigger específico?"
            )
        else:
            return (
                "Gracias por compartir eso conmigo. Para poder ayudarte mejor, "
                "¿podrías contarme cuál sientes que es tu principal desafío en este momento? "
                "Y también, ¿qué has intentado antes para abordarlo?"
            )
    
    def _generate_education_response(self, message: str, needs_analysis: Dict) -> str:
        """Genera respuesta educativa sobre NGX."""
        archetype = needs_analysis.get("client_archetype")
        
        if archetype == ClientArchetype.PERFORMANCE_OPTIMIZER:
            return (
                "Basándome en lo que me has contado, NGX PRIME podría ser exactamente "
                "lo que necesitas. Lo que hace único a NGX es nuestro Hybrid Intelligence Engine - "
                "11 agentes especializados que analizan tu perfil específico y crean un "
                "protocolo personalizado. No es un programa genérico, es como tener un "
                "equipo de especialistas trabajando exclusivamente para optimizar tu rendimiento."
            )
        else:
            return (
                "Con base en tu perfil, NGX LONGEVITY sería ideal para ti. Nuestro "
                "Hybrid Intelligence Engine utiliza 11 agentes especializados en longevidad "
                "que crean protocolos preventivos únicos. Es tecnología que literalmente "
                "no existe en ningún otro lugar - no encontrarás esta precisión en "
                "ningún otro programa."
            )
    
    def _integrate_hie_naturally(self, response: str, phase: ConsultationPhase) -> str:
        """Integra HIE de manera natural en la respuesta."""
        if "hybrid intelligence engine" in response.lower() or "hie" in response.lower():
            return response  # Ya está integrado
            
        # Agregar HIE según la fase, de manera natural
        if phase == ConsultationPhase.EDUCATION_NGX:
            return response  # Ya maneja HIE en esta fase
        elif phase == ConsultationPhase.RECOMMENDATION:
            hie_addition = (
                " Lo que hace esto posible es nuestro Hybrid Intelligence Engine - "
                "una tecnología única que ningún competidor tiene."
            )
            return response + hie_addition
        else:
            return response
    
    def _determine_optimal_program(self, user_profile: Dict, concerns: List[str], archetype: ClientArchetype) -> str:
        """Determina el programa óptimo basado en necesidades."""
        age = user_profile.get("age", 35)
        
        if archetype in [ClientArchetype.PERFORMANCE_OPTIMIZER, ClientArchetype.EXECUTIVE_PERFORMER]:
            return "PRIME"
        elif archetype in [ClientArchetype.LONGEVITY_SEEKER, ClientArchetype.AGING_GRACEFULLY]:
            return "LONGEVITY"
        elif age < 45 and "performance" in concerns:
            return "PRIME"
        elif age >= 50:
            return "LONGEVITY"
        else:
            return "PRIME"  # Default for ambiguous cases
    
    def _determine_optimal_tier_by_needs(self, concerns: List[str], lifestyle: Dict, user_profile: Dict) -> str:
        """Determina tier basado en NECESIDADES, no en capacidad de pago."""
        complexity_score = 0
        
        # Más concerns = más complejidad = tier más alto
        complexity_score += len(concerns)
        
        # Lifestyle factors
        if lifestyle.get("stress_level") == "high":
            complexity_score += 2
        if lifestyle.get("activity_level") == "high":
            complexity_score += 1
        if lifestyle.get("schedule_flexibility") == "low":
            complexity_score += 1
            
        # Determinar tier basado en complejidad de necesidades
        if complexity_score <= 3:
            return "Essential"
        elif complexity_score <= 6:
            return "Pro"
        elif complexity_score <= 9:
            return "Elite"
        else:
            return "Premium"
    
    def _handle_price_objection_consultively(self, objection: str, recommendation: ConsultativeRecommendation, user_profile: Dict) -> Dict:
        """Maneja objeción de precio de manera consultiva."""
        # Ofrecer tier más bajo si es apropiado
        current_tier = recommendation.recommended_tier
        
        if current_tier == "Elite":
            adjusted_tier = "Pro"
            response = (
                f"Entiendo completamente tu preocupación sobre el precio. "
                f"NGX Pro podría ser una excelente opción para comenzar - mantiene "
                f"los beneficios core del Hybrid Intelligence Engine pero a un precio "
                f"más accesible. Siempre puedes hacer upgrade si ves que necesitas "
                f"las funciones adicionales. ¿Te parece más razonable empezar con Pro?"
            )
        elif current_tier == "Pro":
            adjusted_tier = "Essential"
            response = (
                f"Te entiendo perfectamente. NGX Essential te da acceso completo "
                f"al Hybrid Intelligence Engine - la tecnología core que hace la diferencia. "
                f"Es una excelente manera de comenzar y experimentar los beneficios. "
                f"¿Qué te parece si empezamos ahí?"
            )
        else:
            adjusted_tier = current_tier
            response = (
                f"Entiendo tu punto de vista sobre el precio. {current_tier} realmente "
                f"es una inversión, pero considera que estás accediendo a tecnología "
                f"que no existe en ningún otro lugar. ¿Hay alguna forma específica "
                f"en que pueda ayudarte a que esto funcione para tu presupuesto?"
            )
        
        return {
            "response": response,
            "suggested_tier": adjusted_tier,
            "maintains_value": True,
            "consultive_approach": True
        }
    
    def should_present_early_adopter_opportunity(self,
                                               client_profile: Dict,
                                               consultation_phase: str,
                                               engagement_level: str) -> bool:
        """
        Determina si debe presentarse oportunidad de early adopter de manera consultiva.
        
        Args:
            client_profile: Perfil del cliente
            consultation_phase: Fase actual de consultoría  
            engagement_level: Nivel de engagement del cliente
            
        Returns:
            True si es apropiado presentar la oportunidad
        """
        return self.early_adopter_service.should_present_early_adopter_opportunity(
            client_profile, consultation_phase, engagement_level
        )
    
    def generate_consultive_early_adopter_presentation(self,
                                                     recommendation: ConsultativeRecommendation,
                                                     client_profile: Dict,
                                                     consultation_context: Dict) -> Optional[str]:
        """
        Genera presentación consultiva de oportunidad early adopter.
        
        Args:
            recommendation: Recomendación consultiva actual
            client_profile: Perfil del cliente
            consultation_context: Contexto de la consultoría
            
        Returns:
            Presentación consultiva de early adopter o None si no aplica
        """
        try:
            # Obtener oferta apropiada
            offer = self.early_adopter_service.get_appropriate_early_adopter_offer(
                client_profile=client_profile,
                recommended_tier=recommendation.recommended_tier,
                consultation_context=consultation_context
            )
            
            if not offer:
                return None
                
            # Generar presentación consultiva
            presentation = self.early_adopter_service.generate_consultive_early_adopter_presentation(
                offer=offer,
                client_context={"recommendation": recommendation, "profile": client_profile}
            )
            
            return presentation
            
        except Exception as e:
            logger.error(f"Error generating early adopter presentation: {str(e)}")
            return None
    
    def handle_early_adopter_questions(self,
                                     question: str,
                                     current_recommendation: ConsultativeRecommendation,
                                     client_profile: Dict) -> str:
        """
        Maneja preguntas sobre oportunidades de early adopter.
        
        Args:
            question: Pregunta del cliente
            current_recommendation: Recomendación actual
            client_profile: Perfil del cliente
            
        Returns:
            Respuesta consultiva a la pregunta
        """
        try:
            # Obtener oferta apropiada
            offer = self.early_adopter_service.get_appropriate_early_adopter_offer(
                client_profile=client_profile,
                recommended_tier=current_recommendation.recommended_tier,
                consultation_context={}
            )
            
            if not offer:
                return (
                    "En este momento estamos enfocados en encontrar la solución correcta "
                    "para ti. Una vez que determinemos que NGX es el camino apropiado, "
                    "podremos revisar las oportunidades especiales disponibles."
                )
                
            return self.early_adopter_service.handle_early_adopter_questions(question, offer)
            
        except Exception as e:
            logger.error(f"Error handling early adopter questions: {str(e)}")
            return (
                "Permíteme enfocarme en asegurarme de que NGX sea la solución correcta "
                "para ti. Después podemos revisar las opciones especiales disponibles."
            )
    
    def _fallback_needs_analysis(self) -> Dict:
        """Análisis de necesidades de fallback."""
        return {
            "key_concerns": ["general_wellness"],
            "lifestyle_factors": {"activity_level": "moderate"},
            "goals_priorities": {"primary_goal": "general_wellness"},
            "client_archetype": ClientArchetype.HEALTH_CONSCIOUS,
            "consultation_phase": ConsultationPhase.INITIAL_CONNECTION
        }
    
    def _fallback_consultive_response(self, message: str) -> Dict:
        """Respuesta consultiva de fallback."""
        return {
            "response": (
                "Gracias por compartir eso conmigo. Mi objetivo es entender "
                "tu situación específica para poder recomendarte la mejor solución NGX. "
                "¿Puedes contarme un poco más sobre lo que estás buscando lograr?"
            ),
            "consultation_phase": ConsultationPhase.NEEDS_ASSESSMENT.value,
            "intelligent_questions": [
                "¿Cuál es tu principal desafío en este momento?",
                "¿Qué resultados ideales estarías buscando?"
            ]
        }