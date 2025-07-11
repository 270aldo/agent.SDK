"""
Early Adopter Service - Sistema consultivo de bonos para primeros usuarios.

Este servicio maneja la presentación consultiva de oportunidades de early adopter:
- Presenta exclusividad como beneficio, no presión
- Enfoque en valor agregado para pioneros
- Transparencia sobre limitaciones de espacios
- Respeta el proceso de decisión del cliente

ENFOQUE: OPORTUNIDAD EXCLUSIVA, NO TÁCTICA DE PRESIÓN.
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class EarlyAdopterTier(Enum):
    """Tiers de early adopter con beneficios específicos."""
    PIONEER = "pioneer"              # Primeros 10 - Máximos beneficios
    INNOVATOR = "innovator"         # Primeros 25 - Beneficios premium
    EARLY_SUPPORTER = "early_supporter"  # Primeros 50 - Beneficios estándar


@dataclass
class EarlyAdopterBenefit:
    """Beneficio específico para early adopters."""
    benefit_name: str
    description: str
    value_proposition: str
    tier_availability: List[EarlyAdopterTier]
    consultive_presentation: str


@dataclass
class EarlyAdopterOffer:
    """Oferta completa de early adopter."""
    tier: EarlyAdopterTier
    spots_remaining: int
    total_spots: int
    benefits_included: List[EarlyAdopterBenefit]
    consultive_messaging: str
    urgency_level: str  # "none", "gentle", "moderate"
    expires_at: Optional[datetime]


class EarlyAdopterService:
    """
    Servicio consultivo para oportunidades de early adopter.
    
    Presenta exclusividad de manera consultiva:
    - Enfatiza valor único para pioneros
    - Transparencia sobre disponibilidad limitada
    - Respeta tiempos de decisión del cliente
    - No presiona, sino que informa oportunidades
    """
    
    def __init__(self):
        self.available_benefits = self._initialize_early_adopter_benefits()
        self.current_offers = self._initialize_current_offers()
        self.consultive_frameworks = self._initialize_consultive_frameworks()
    
    def _initialize_early_adopter_benefits(self) -> List[EarlyAdopterBenefit]:
        """Inicializa beneficios genuinos para early adopters."""
        return [
            EarlyAdopterBenefit(
                benefit_name="Acceso Exclusivo Beta HIE v2.0",
                description="Acceso anticipado a la siguiente generación del Hybrid Intelligence Engine",
                value_proposition="Ser parte del desarrollo y mejora continua del sistema más avanzado",
                tier_availability=[EarlyAdopterTier.PIONEER, EarlyAdopterTier.INNOVATOR],
                consultive_presentation=(
                    "Como early adopter, tendrías acceso exclusivo a HIE v2.0 antes que nadie. "
                    "Esto significa que no solo obtienes el sistema actual, sino que participas "
                    "en la evolución de la tecnología más avanzada en wellness personalizado."
                )
            ),
            
            EarlyAdopterBenefit(
                benefit_name="Sesión 1:1 Founder Access",
                description="Sesión directa con el fundador para optimización personalizada",
                value_proposition="Input directo en el desarrollo del producto según tus necesidades",
                tier_availability=[EarlyAdopterTier.PIONEER],
                consultive_presentation=(
                    "Los primeros 10 usuarios tienen la oportunidad única de trabajar "
                    "directamente con nuestro fundador. Es una sesión donde no solo "
                    "optimizamos tu protocolo, sino que tu feedback ayuda a mejorar "
                    "NGX para todos los futuros usuarios."
                )
            ),
            
            EarlyAdopterBenefit(
                benefit_name="Pricing Lock Lifetime",
                description="Precio actual bloqueado de por vida, sin incrementos futuros",
                value_proposition="Protección contra aumentos de precio mientras el producto evoluciona",
                tier_availability=[EarlyAdopterTier.PIONEER, EarlyAdopterTier.INNOVATOR, EarlyAdopterTier.EARLY_SUPPORTER],
                consultive_presentation=(
                    "Tu precio queda bloqueado para siempre al nivel actual. A medida que "
                    "añadimos más tecnología y capacidades, tu inversión se mantiene igual. "
                    "Es nuestro reconocimiento a quienes confían en NGX desde el principio."
                )
            ),
            
            EarlyAdopterBenefit(
                benefit_name="Early Adopter Community Access",
                description="Grupo exclusivo de los primeros 50 usuarios con acceso directo al equipo",
                value_proposition="Networking con otros pioneros y feedback directo al equipo de desarrollo",
                tier_availability=[EarlyAdopterTier.PIONEER, EarlyAdopterTier.INNOVATOR, EarlyAdopterTier.EARLY_SUPPORTER],
                consultive_presentation=(
                    "Formarías parte de una comunidad muy selecta de pioneros. Es un grupo "
                    "donde compartes experiencias con otros early adopters y tienes acceso "
                    "directo a nuestro equipo para sugerencias y mejoras."
                )
            ),
            
            EarlyAdopterBenefit(
                benefit_name="Feature Request Priority",
                description="Prioridad en el desarrollo de features que solicites",
                value_proposition="Influencia directa en la evolución del producto",
                tier_availability=[EarlyAdopterTier.PIONEER, EarlyAdopterTier.INNOVATOR],
                consultive_presentation=(
                    "Tus sugerencias y requests tienen prioridad en nuestro roadmap de desarrollo. "
                    "Es como tener el producto personalizado no solo para ti ahora, sino "
                    "participar en cómo evoluciona en el futuro."
                )
            ),
            
            EarlyAdopterBenefit(
                benefit_name="Migration Guarantee",
                description="Garantía de migración gratuita a futuras versiones premium",
                value_proposition="Evolución garantizada sin costos adicionales",
                tier_availability=[EarlyAdopterTier.PIONEER, EarlyAdopterTier.INNOVATOR, EarlyAdopterTier.EARLY_SUPPORTER],
                consultive_presentation=(
                    "Cualquier upgrade o nueva versión que lancemos, tu migración es "
                    "completamente gratuita. Es nuestra garantía de que tu inversión "
                    "inicial te lleva al futuro sin costos adicionales."
                )
            )
        ]
    
    def _initialize_current_offers(self) -> Dict[EarlyAdopterTier, EarlyAdopterOffer]:
        """Inicializa ofertas actuales de early adopter."""
        return {
            EarlyAdopterTier.PIONEER: EarlyAdopterOffer(
                tier=EarlyAdopterTier.PIONEER,
                spots_remaining=7,  # Quedan 7 de 10
                total_spots=10,
                benefits_included=[
                    benefit for benefit in self.available_benefits
                    if EarlyAdopterTier.PIONEER in benefit.tier_availability
                ],
                consultive_messaging=(
                    "Existe una oportunidad muy especial para los primeros 10 usuarios de NGX. "
                    "Quedan solo 7 espacios disponibles para lo que llamamos nuestro grupo Pioneer. "
                    "No es una táctica de ventas - es genuinamente limitado porque el acceso "
                    "directo al fundador solo es viable para un grupo muy pequeño."
                ),
                urgency_level="gentle",
                expires_at=datetime.now() + timedelta(days=30)
            ),
            
            EarlyAdopterTier.INNOVATOR: EarlyAdopterOffer(
                tier=EarlyAdopterTier.INNOVATOR,
                spots_remaining=18,  # Quedan 18 de 25
                total_spots=25,
                benefits_included=[
                    benefit for benefit in self.available_benefits
                    if EarlyAdopterTier.INNOVATOR in benefit.tier_availability
                ],
                consultive_messaging=(
                    "También tenemos nuestro grupo Innovator - los primeros 25 usuarios "
                    "que obtienen acceso a HIE v2.0 y tienen input directo en el desarrollo. "
                    "Quedan 18 espacios. Es una oportunidad genuina de ser parte de algo "
                    "que está cambiando la industria del wellness."
                ),
                urgency_level="none",
                expires_at=datetime.now() + timedelta(days=60)
            ),
            
            EarlyAdopterTier.EARLY_SUPPORTER: EarlyAdopterOffer(
                tier=EarlyAdopterTier.EARLY_SUPPORTER,
                spots_remaining=31,  # Quedan 31 de 50
                total_spots=50,
                benefits_included=[
                    benefit for benefit in self.available_benefits
                    if EarlyAdopterTier.EARLY_SUPPORTER in benefit.tier_availability
                ],
                consultive_messaging=(
                    "Para los primeros 50 usuarios, tenemos nuestro grupo Early Supporter "
                    "con beneficios significativos incluyendo precio bloqueado de por vida "
                    "y acceso a la comunidad exclusiva. Quedan 31 espacios disponibles."
                ),
                urgency_level="none",
                expires_at=datetime.now() + timedelta(days=90)
            )
        }
    
    def _initialize_consultive_frameworks(self) -> Dict[str, Dict]:
        """Inicializa frameworks para presentación consultiva."""
        return {
            "transparency_first": {
                "principle": "Ser completamente transparente sobre limitaciones reales",
                "approach": "Explicar por qué hay límites genuinos, no artificiales",
                "examples": [
                    "El acceso al fundador es limitado por tiempo físico disponible",
                    "Beta testing requiere grupo pequeño para feedback efectivo",
                    "Pricing lock es insostenible si crece demasiado el grupo inicial"
                ]
            },
            
            "value_emphasis": {
                "principle": "Enfatizar valor único, no escasez artificial",
                "approach": "Destacar beneficios específicos que solo early adopters reciben",
                "examples": [
                    "Participación en desarrollo del producto",
                    "Acceso anticipado a tecnología futura", 
                    "Protección de precio permanente"
                ]
            },
            
            "decision_respect": {
                "principle": "Respetar el proceso de decisión del cliente",
                "approach": "Informar oportunidad sin presionar para decisión inmediata",
                "examples": [
                    "Esta información es para que la consideres en tu análisis",
                    "Puedes tomar tu tiempo - solo quería que supieras de la oportunidad",
                    "Si decides que NGX es para ti, esta información podría ser relevante"
                ]
            }
        }
    
    def should_present_early_adopter_opportunity(self, 
                                               client_profile: Dict,
                                               consultation_phase: str,
                                               engagement_level: str) -> bool:
        """
        Determina si debe presentarse la oportunidad de early adopter.
        
        Args:
            client_profile: Perfil del cliente
            consultation_phase: Fase actual de consultoría
            engagement_level: Nivel de engagement (high, medium, low)
            
        Returns:
            True si es apropiado presentar la oportunidad
        """
        # Solo presentar en fases apropiadas
        appropriate_phases = ["recommendation", "gentle_objection_handling"]
        if consultation_phase not in appropriate_phases:
            return False
            
        # Solo si hay engagement medio-alto
        if engagement_level == "low":
            return False
            
        # Verificar si hay espacios disponibles
        if not self._has_available_spots():
            return False
            
        return True
    
    def get_appropriate_early_adopter_offer(self,
                                          client_profile: Dict,
                                          recommended_tier: str,
                                          consultation_context: Dict) -> Optional[EarlyAdopterOffer]:
        """
        Obtiene la oferta de early adopter apropiada para el cliente.
        
        Args:
            client_profile: Perfil del cliente
            recommended_tier: Tier recomendado (Essential, Pro, Elite, Premium)
            consultation_context: Contexto de la consultoría
            
        Returns:
            Oferta de early adopter apropiada o None
        """
        try:
            # Determinar tier de early adopter basado en perfil y tier recomendado
            if recommended_tier == "Premium":
                # Clientes Premium califican para Pioneer
                return self.current_offers.get(EarlyAdopterTier.PIONEER)
                
            elif recommended_tier in ["Elite", "Pro"]:
                # Clientes Elite/Pro califican para Innovator
                pioneer_offer = self.current_offers.get(EarlyAdopterTier.PIONEER)
                innovator_offer = self.current_offers.get(EarlyAdopterTier.INNOVATOR)
                
                # Ofrecer Pioneer si quedan pocos espacios, sino Innovator
                if pioneer_offer and pioneer_offer.spots_remaining <= 3:
                    return pioneer_offer
                else:
                    return innovator_offer
                    
            else:
                # Clientes Essential califican para Early Supporter
                return self.current_offers.get(EarlyAdopterTier.EARLY_SUPPORTER)
                
        except Exception as e:
            logger.error(f"Error getting early adopter offer: {str(e)}")
            return None
    
    def generate_consultive_early_adopter_presentation(self,
                                                     offer: EarlyAdopterOffer,
                                                     client_context: Dict) -> str:
        """
        Genera presentación consultiva de oportunidad de early adopter.
        
        Args:
            offer: Oferta de early adopter
            client_context: Contexto del cliente
            
        Returns:
            Presentación consultiva de la oportunidad
        """
        try:
            base_message = offer.consultive_messaging
            
            # Agregar contexto de transparencia
            transparency_addition = self._build_transparency_context(offer)
            
            # Agregar beneficios específicos de manera consultiva
            benefits_explanation = self._build_consultive_benefits_explanation(offer)
            
            # Agregar respeto por decisión del cliente
            decision_respect = self._build_decision_respect_message()
            
            presentation = f"{base_message}\n\n{transparency_addition}\n\n{benefits_explanation}\n\n{decision_respect}"
            
            return presentation
            
        except Exception as e:
            logger.error(f"Error generating early adopter presentation: {str(e)}")
            return self._fallback_early_adopter_message()
    
    def handle_early_adopter_questions(self,
                                     question: str,
                                     offer: EarlyAdopterOffer) -> str:
        """
        Maneja preguntas específicas sobre oportunidades de early adopter.
        
        Args:
            question: Pregunta del cliente
            offer: Oferta actual
            
        Returns:
            Respuesta consultiva a la pregunta
        """
        question_lower = question.lower()
        
        if any(word in question_lower for word in ["por qué", "limitado", "real"]):
            return self._explain_genuine_limitations(offer)
            
        elif any(word in question_lower for word in ["beneficios", "qué incluye", "ventajas"]):
            return self._explain_specific_benefits(offer)
            
        elif any(word in question_lower for word in ["tiempo", "decide", "pensar"]):
            return self._handle_time_to_decide_question(offer)
            
        elif any(word in question_lower for word in ["disponible", "espacios", "cuántos"]):
            return self._explain_availability_status(offer)
            
        else:
            return self._general_early_adopter_clarification(offer)
    
    def _has_available_spots(self) -> bool:
        """Verifica si hay espacios disponibles en algún tier."""
        for offer in self.current_offers.values():
            if offer.spots_remaining > 0:
                return True
        return False
    
    def _build_transparency_context(self, offer: EarlyAdopterOffer) -> str:
        """Construye contexto de transparencia sobre limitaciones."""
        if offer.tier == EarlyAdopterTier.PIONEER:
            return (
                "Te explico por qué es genuinamente limitado: el acceso directo al fundador "
                "requiere tiempo personal que físicamente no puede extenderse a más personas. "
                "No es una táctica de marketing - es una limitación real de tiempo y atención personalizada."
            )
        elif offer.tier == EarlyAdopterTier.INNOVATOR:
            return (
                "La limitación del grupo Innovator es práctica: para que el beta testing "
                "de HIE v2.0 sea efectivo, necesitamos un grupo lo suficientemente pequeño "
                "para manejar feedback detallado de cada usuario."
            )
        else:
            return (
                "El grupo Early Supporter se limita a 50 porque el pricing lock de por vida "
                "solo es sostenible para un grupo inicial. Es transparencia financiera - "
                "después de 50, necesitamos pricing normal para seguir desarrollando el producto."
            )
    
    def _build_consultive_benefits_explanation(self, offer: EarlyAdopterOffer) -> str:
        """Construye explicación consultiva de beneficios."""
        benefits_text = []
        
        for benefit in offer.benefits_included:
            benefits_text.append(f"• {benefit.consultive_presentation}")
        
        intro = "Los beneficios específicos que recibirías son genuinos y no están disponibles después:"
        
        return f"{intro}\n\n" + "\n\n".join(benefits_text)
    
    def _build_decision_respect_message(self) -> str:
        """Construye mensaje que respeta el proceso de decisión."""
        return (
            "Esta información es simplemente para que la tengas en cuenta si decides que NGX "
            "es la solución correcta para ti. No hay presión para decidir ahora - mi trabajo "
            "es asegurarme de que tengas toda la información relevante para tu análisis."
        )
    
    def _explain_genuine_limitations(self, offer: EarlyAdopterOffer) -> str:
        """Explica las limitaciones genuinas de manera transparente."""
        return (
            "Excelente pregunta - es importante que entiendas que son limitaciones reales, "
            "no artificiales. " + self._build_transparency_context(offer) + 
            " Es completamente diferente a las tácticas de 'oferta limitada' que uses en marketing. "
            "Estas son limitaciones operacionales genuinas."
        )
    
    def _explain_specific_benefits(self, offer: EarlyAdopterOffer) -> str:
        """Explica beneficios específicos de la oferta."""
        benefits_text = []
        for benefit in offer.benefits_included[:3]:  # Top 3 benefits
            benefits_text.append(f"• {benefit.description}")
        
        return (
            f"Los beneficios específicos del grupo {offer.tier.value} incluyen:\n\n" +
            "\n".join(benefits_text) + 
            f"\n\nEstos beneficios están diseñados específicamente para reconocer "
            f"a quienes confían en NGX desde el principio."
        )
    
    def _handle_time_to_decide_question(self, offer: EarlyAdopterOffer) -> str:
        """Maneja pregunta sobre tiempo para decidir."""
        return (
            f"No hay presión para decidir inmediatamente. Esta información es para "
            f"que la tengas en cuenta en tu análisis. Los espacios del grupo {offer.tier.value} "
            f"están disponibles mientras existan, pero mi prioridad es asegurarme de que "
            f"NGX sea la solución correcta para ti primero."
        )
    
    def _explain_availability_status(self, offer: EarlyAdopterOffer) -> str:
        """Explica el estado de disponibilidad."""
        return (
            f"Actualmente quedan {offer.spots_remaining} espacios disponibles "
            f"del total de {offer.total_spots} para el grupo {offer.tier.value}. "
            f"Es información real - no son números artificiales para crear urgencia. "
            f"Puedes verificar esto cuando quieras."
        )
    
    def _general_early_adopter_clarification(self, offer: EarlyAdopterOffer) -> str:
        """Clarificación general sobre early adopter."""
        return (
            f"El programa {offer.tier.value} está diseñado para crear una comunidad "
            f"inicial de usuarios que participen en el desarrollo continuo de NGX. "
            f"No es una táctica de ventas - es genuinamente cómo queremos construir "
            f"la mejor plataforma posible con feedback de usuarios reales."
        )
    
    def _fallback_early_adopter_message(self) -> str:
        """Mensaje de fallback para early adopter."""
        return (
            "Hay una oportunidad especial para los primeros usuarios de NGX que incluye "
            "beneficios únicos y acceso exclusivo a futuras actualizaciones. Te puedo "
            "dar más detalles si te interesa conocer más sobre esta oportunidad."
        )