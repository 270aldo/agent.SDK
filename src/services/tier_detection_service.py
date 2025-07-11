"""
Servicio de detección de tier óptimo por lead.

Este servicio analiza el perfil del cliente y la conversación para determinar
qué tier de suscripción es más adecuado para maximizar la conversión.
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class TierType(str, Enum):
    """Tipos de tier disponibles."""
    ESSENTIAL = "essential"  # $79/mes
    PRO = "pro"             # $149/mes  
    ELITE = "elite"         # $199/mes
    PRIME_PREMIUM = "prime_premium"      # $3,997
    LONGEVITY_PREMIUM = "longevity_premium"  # $3,997


@dataclass
class TierDetectionResult:
    """Resultado de detección de tier."""
    recommended_tier: TierType
    confidence: float
    reasoning: str
    price_point: str
    upsell_potential: str
    demographic_factors: Dict[str, Any]
    behavioral_signals: List[str]
    price_sensitivity: str
    roi_projection: Optional[Dict[str, Any]] = None


class TierDetectionService:
    """Servicio para detectar el tier óptimo por lead."""
    
    def __init__(self):
        """Inicializar el servicio de detección de tier."""
        self.tier_pricing = {
            TierType.ESSENTIAL: 79,
            TierType.PRO: 149,
            TierType.ELITE: 199,
            TierType.PRIME_PREMIUM: 3997,
            TierType.LONGEVITY_PREMIUM: 3997
        }
        
        # Indicadores de ingresos por profesión
        self.income_indicators = {
            "estudiante": {"tier": TierType.ESSENTIAL, "budget": "low", "hourly_rate": 0},
            "freelancer": {"tier": TierType.PRO, "budget": "medium", "hourly_rate": 50},
            "gerente": {"tier": TierType.PRO, "budget": "medium", "hourly_rate": 75},
            "consultor": {"tier": TierType.ELITE, "budget": "high", "hourly_rate": 200},
            "director": {"tier": TierType.ELITE, "budget": "high", "hourly_rate": 300},
            "abogado": {"tier": TierType.PRIME_PREMIUM, "budget": "very_high", "hourly_rate": 400},
            "médico": {"tier": TierType.LONGEVITY_PREMIUM, "budget": "very_high", "hourly_rate": 300},
            "ceo": {"tier": TierType.PRIME_PREMIUM, "budget": "very_high", "hourly_rate": 500},
            "emprendedor": {"tier": TierType.ELITE, "budget": "high", "hourly_rate": 250},
            "ingeniero": {"tier": TierType.PRO, "budget": "medium", "hourly_rate": 100},
            "desarrollador": {"tier": TierType.PRO, "budget": "medium", "hourly_rate": 80}
        }
    
    async def detect_optimal_tier(
        self,
        user_message: str,
        user_profile: Dict[str, Any],
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> TierDetectionResult:
        """
        Detectar el tier óptimo para un lead específico.
        
        Args:
            user_message: Mensaje actual del usuario
            user_profile: Perfil del usuario con información demográfica
            conversation_history: Historial de conversación para contexto
            
        Returns:
            TierDetectionResult: Resultado con tier recomendado y reasoning
        """
        try:
            # Análisis demográfico
            demographic_score = self._analyze_demographics(user_profile)
            
            # Análisis del mensaje
            message_analysis = self._analyze_message_content(user_message)
            
            # Análisis de historial si está disponible
            behavioral_analysis = self._analyze_behavioral_patterns(conversation_history) if conversation_history else {}
            
            # Análisis de sensibilidad al precio
            price_sensitivity = self._analyze_price_sensitivity(user_message, user_profile)
            
            # Determinar tier basado en múltiples factores
            tier_recommendation = self._calculate_tier_recommendation(
                demographic_score,
                message_analysis,
                behavioral_analysis,
                price_sensitivity
            )
            
            # Calcular ROI si es posible
            roi_projection = self._calculate_roi_projection(user_profile, tier_recommendation)
            
            return TierDetectionResult(
                recommended_tier=tier_recommendation['tier'],
                confidence=tier_recommendation['confidence'],
                reasoning=tier_recommendation['reasoning'],
                price_point=f"${self.tier_pricing[tier_recommendation['tier']]}/mes" if tier_recommendation['tier'] in [TierType.ESSENTIAL, TierType.PRO, TierType.ELITE] else f"${self.tier_pricing[tier_recommendation['tier']]}",
                upsell_potential=tier_recommendation['upsell_potential'],
                demographic_factors=demographic_score,
                behavioral_signals=message_analysis.get('signals', []),
                price_sensitivity=price_sensitivity,
                roi_projection=roi_projection
            )
            
        except Exception as e:
            logger.error(f"Error detectando tier óptimo: {e}")
            # Fallback a tier PRO por defecto
            return TierDetectionResult(
                recommended_tier=TierType.PRO,
                confidence=0.5,
                reasoning="Tier por defecto debido a error en análisis",
                price_point="$149/mes",
                upsell_potential="medium",
                demographic_factors={},
                behavioral_signals=[],
                price_sensitivity="medium"
            )
    
    def _analyze_demographics(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Analizar factores demográficos del usuario."""
        try:
            age = user_profile.get('age', 0)
            occupation = user_profile.get('occupation', '').lower()
            location = user_profile.get('location', '').lower()
            income_bracket = user_profile.get('income_bracket', 'medium')
            
            # Análisis por ocupación
            occupation_analysis = {}
            for prof, data in self.income_indicators.items():
                if prof in occupation:
                    occupation_analysis = {
                        'detected_profession': prof,
                        'suggested_tier': data['tier'],
                        'budget_category': data['budget'],
                        'estimated_hourly_rate': data['hourly_rate']
                    }
                    break
            
            # Análisis por edad
            age_analysis = {}
            if age > 0:
                if age < 25:
                    age_analysis = {'tier_preference': TierType.ESSENTIAL, 'budget_impact': 'low'}
                elif age < 35:
                    age_analysis = {'tier_preference': TierType.PRO, 'budget_impact': 'medium'}
                elif age < 50:
                    age_analysis = {'tier_preference': TierType.ELITE, 'budget_impact': 'high'}
                else:
                    age_analysis = {'tier_preference': TierType.LONGEVITY_PREMIUM, 'budget_impact': 'very_high'}
            
            # Análisis por ubicación (simplificado)
            location_analysis = {}
            if any(city in location for city in ['mexico', 'cdmx', 'guadalajara', 'monterrey']):
                location_analysis = {'market': 'mexico', 'purchasing_power': 'medium'}
            elif any(city in location for city in ['madrid', 'barcelona', 'españa']):
                location_analysis = {'market': 'spain', 'purchasing_power': 'high'}
            else:
                location_analysis = {'market': 'other', 'purchasing_power': 'medium'}
            
            return {
                'occupation_analysis': occupation_analysis,
                'age_analysis': age_analysis,
                'location_analysis': location_analysis,
                'declared_income_bracket': income_bracket
            }
            
        except Exception as e:
            logger.error(f"Error analizando demografía: {e}")
            return {}
    
    def _analyze_message_content(self, message: str) -> Dict[str, Any]:
        """Analizar contenido del mensaje para detectar señales de tier."""
        try:
            message_lower = message.lower()
            
            # Señales de presupuesto alto
            high_budget_signals = [
                "empresa propia", "mi empresa", "soy ceo", "soy director",
                "resultados máximos", "lo mejor", "no importa el precio",
                "vale la pena", "transformación completa", "premium",
                "exclusivo", "personalizado", "vip"
            ]
            
            # Señales de presupuesto medio
            medium_budget_signals = [
                "profesional", "gerente", "trabajo en", "freelancer",
                "razonable", "dentro del presupuesto", "inversión inteligente",
                "vale la pena la inversión", "buen precio", "competitivo"
            ]
            
            # Señales de presupuesto bajo
            low_budget_signals = [
                "estudiante", "presupuesto limitado", "barato", "económico",
                "no tengo mucho", "más barato", "descuento", "oferta",
                "precio bajo", "ahorro"
            ]
            
            # Señales de urgencia
            urgency_signals = [
                "urgente", "rápido", "pronto", "inmediato", "ya",
                "hoy", "esta semana", "no puedo esperar"
            ]
            
            # Señales de comparación
            comparison_signals = [
                "vs", "comparado con", "otros", "alternativas",
                "competencia", "mejor que", "diferente a"
            ]
            
            # Detectar señales
            detected_signals = []
            budget_score = 0
            
            for signal in high_budget_signals:
                if signal in message_lower:
                    detected_signals.append(f"high_budget: {signal}")
                    budget_score += 3
            
            for signal in medium_budget_signals:
                if signal in message_lower:
                    detected_signals.append(f"medium_budget: {signal}")
                    budget_score += 2
            
            for signal in low_budget_signals:
                if signal in message_lower:
                    detected_signals.append(f"low_budget: {signal}")
                    budget_score -= 1
            
            for signal in urgency_signals:
                if signal in message_lower:
                    detected_signals.append(f"urgency: {signal}")
                    budget_score += 1
            
            for signal in comparison_signals:
                if signal in message_lower:
                    detected_signals.append(f"comparison: {signal}")
            
            return {
                'signals': detected_signals,
                'budget_score': budget_score,
                'message_length': len(message),
                'sophistication_level': self._calculate_sophistication(message)
            }
            
        except Exception as e:
            logger.error(f"Error analizando mensaje: {e}")
            return {'signals': [], 'budget_score': 0}
    
    def _analyze_behavioral_patterns(self, conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """Analizar patrones de comportamiento en la conversación."""
        try:
            if not conversation_history:
                return {}
            
            user_messages = [msg['content'] for msg in conversation_history if msg['role'] == 'user']
            
            # Análisis de engagement
            engagement_score = len(user_messages)
            avg_message_length = sum(len(msg) for msg in user_messages) / len(user_messages) if user_messages else 0
            
            # Análisis de preguntas específicas
            questions_asked = sum(1 for msg in user_messages if '?' in msg)
            
            # Análisis de menciones de precio
            price_mentions = sum(1 for msg in user_messages if any(word in msg.lower() for word in ['precio', 'costo', 'cuánto', 'pago']))
            
            # Análisis de objeciones
            objections = sum(1 for msg in user_messages if any(word in msg.lower() for word in ['pero', 'sin embargo', 'no estoy seguro']))
            
            return {
                'engagement_score': engagement_score,
                'avg_message_length': avg_message_length,
                'questions_asked': questions_asked,
                'price_mentions': price_mentions,
                'objections_raised': objections,
                'conversation_depth': 'high' if engagement_score > 5 else 'medium' if engagement_score > 2 else 'low'
            }
            
        except Exception as e:
            logger.error(f"Error analizando patrones: {e}")
            return {}
    
    def _analyze_price_sensitivity(self, message: str, user_profile: Dict[str, Any]) -> str:
        """Analizar sensibilidad al precio del usuario."""
        try:
            message_lower = message.lower()
            
            # Indicadores de baja sensibilidad al precio
            if any(phrase in message_lower for phrase in [
                "no importa el precio", "vale la pena", "inversión",
                "calidad", "premium", "lo mejor"
            ]):
                return "low"
            
            # Indicadores de alta sensibilidad al precio
            if any(phrase in message_lower for phrase in [
                "barato", "económico", "presupuesto limitado",
                "descuento", "oferta", "precio bajo"
            ]):
                return "high"
            
            # Análisis demográfico
            age = user_profile.get('age', 0)
            occupation = user_profile.get('occupation', '').lower()
            
            if age > 45 and any(prof in occupation for prof in ['ceo', 'director', 'médico', 'abogado']):
                return "low"
            elif age < 25 or 'estudiante' in occupation:
                return "high"
            
            return "medium"
            
        except Exception as e:
            logger.error(f"Error analizando sensibilidad al precio: {e}")
            return "medium"
    
    def _calculate_sophistication(self, message: str) -> str:
        """Calcular nivel de sofisticación del mensaje."""
        try:
            # Palabras técnicas o sofisticadas
            sophisticated_words = [
                "optimización", "eficiencia", "productividad", "estrategia",
                "metodología", "sistemático", "integral", "holístico",
                "personalizado", "algoritmo", "análisis", "métricas"
            ]
            
            sophisticated_count = sum(1 for word in sophisticated_words if word in message.lower())
            
            if sophisticated_count >= 3:
                return "high"
            elif sophisticated_count >= 1:
                return "medium"
            else:
                return "low"
                
        except Exception as e:
            logger.error(f"Error calculando sofisticación: {e}")
            return "medium"
    
    def _calculate_tier_recommendation(
        self,
        demographic_score: Dict[str, Any],
        message_analysis: Dict[str, Any],
        behavioral_analysis: Dict[str, Any],
        price_sensitivity: str
    ) -> Dict[str, Any]:
        """Calcular recomendación de tier basada en todos los factores."""
        try:
            # Puntajes por tier
            tier_scores = {
                TierType.ESSENTIAL: 0,
                TierType.PRO: 0,
                TierType.ELITE: 0,
                TierType.PRIME_PREMIUM: 0,
                TierType.LONGEVITY_PREMIUM: 0
            }
            
            # Factor demográfico
            occupation_analysis = demographic_score.get('occupation_analysis', {})
            if occupation_analysis:
                suggested_tier = occupation_analysis.get('suggested_tier')
                if suggested_tier:
                    tier_scores[suggested_tier] += 5
            
            # Factor de edad
            age_analysis = demographic_score.get('age_analysis', {})
            if age_analysis:
                age_tier = age_analysis.get('tier_preference')
                if age_tier:
                    tier_scores[age_tier] += 3
            
            # Factor de mensaje
            budget_score = message_analysis.get('budget_score', 0)
            if budget_score >= 6:
                tier_scores[TierType.PRIME_PREMIUM] += 4
                tier_scores[TierType.ELITE] += 2
            elif budget_score >= 3:
                tier_scores[TierType.ELITE] += 3
                tier_scores[TierType.PRO] += 1
            elif budget_score >= 0:
                tier_scores[TierType.PRO] += 2
                tier_scores[TierType.ESSENTIAL] += 1
            else:
                tier_scores[TierType.ESSENTIAL] += 3
            
            # Factor de sensibilidad al precio
            if price_sensitivity == "low":
                tier_scores[TierType.PRIME_PREMIUM] += 2
                tier_scores[TierType.ELITE] += 1
            elif price_sensitivity == "high":
                tier_scores[TierType.ESSENTIAL] += 2
                tier_scores[TierType.PRO] += 1
            
            # Factor de sofisticación
            sophistication = message_analysis.get('sophistication_level', 'medium')
            if sophistication == "high":
                tier_scores[TierType.ELITE] += 1
                tier_scores[TierType.PRIME_PREMIUM] += 1
            
            # Factor de engagement
            engagement = behavioral_analysis.get('conversation_depth', 'medium')
            if engagement == "high":
                tier_scores[TierType.ELITE] += 1
                tier_scores[TierType.PRIME_PREMIUM] += 1
            
            # Determinar tier ganador
            recommended_tier = max(tier_scores, key=tier_scores.get)
            max_score = tier_scores[recommended_tier]
            
            # Calcular confianza
            total_score = sum(tier_scores.values())
            confidence = max_score / total_score if total_score > 0 else 0.5
            
            # Determinar potencial de upsell
            upsell_potential = "high" if confidence > 0.7 else "medium" if confidence > 0.5 else "low"
            
            # Generar reasoning
            reasoning_parts = []
            if occupation_analysis:
                reasoning_parts.append(f"Profesión: {occupation_analysis.get('detected_profession', 'detectada')}")
            if budget_score > 0:
                reasoning_parts.append(f"Señales de presupuesto: {budget_score}")
            if price_sensitivity != "medium":
                reasoning_parts.append(f"Sensibilidad al precio: {price_sensitivity}")
            
            reasoning = f"Recomendado por: {', '.join(reasoning_parts) if reasoning_parts else 'análisis general'}"
            
            return {
                'tier': recommended_tier,
                'confidence': round(confidence, 2),
                'reasoning': reasoning,
                'upsell_potential': upsell_potential,
                'tier_scores': tier_scores
            }
            
        except Exception as e:
            logger.error(f"Error calculando recomendación: {e}")
            return {
                'tier': TierType.PRO,
                'confidence': 0.5,
                'reasoning': 'Tier por defecto',
                'upsell_potential': 'medium',
                'tier_scores': {}
            }
    
    def _calculate_roi_projection(self, user_profile: Dict[str, Any], tier_recommendation: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Calcular proyección de ROI para el tier recomendado."""
        try:
            occupation = user_profile.get('occupation', '').lower()
            
            # Buscar tarifa por hora estimada
            hourly_rate = None
            for prof, data in self.income_indicators.items():
                if prof in occupation:
                    hourly_rate = data['hourly_rate']
                    break
            
            if not hourly_rate or hourly_rate == 0:
                return None
            
            recommended_tier = tier_recommendation['tier']
            monthly_cost = self.tier_pricing[recommended_tier]
            
            # Calcular ROI conservador
            if recommended_tier in [TierType.ESSENTIAL, TierType.PRO, TierType.ELITE]:
                # Para suscripciones mensuales
                productivity_hours_gain = 2 if recommended_tier == TierType.ESSENTIAL else 3 if recommended_tier == TierType.PRO else 4
                working_days_month = 22
                
                monthly_productivity_value = hourly_rate * productivity_hours_gain * working_days_month
                monthly_roi = ((monthly_productivity_value - monthly_cost) / monthly_cost) * 100
                payback_days = monthly_cost / (hourly_rate * productivity_hours_gain)
                
                return {
                    'monthly_cost': monthly_cost,
                    'productivity_hours_gain': productivity_hours_gain,
                    'monthly_productivity_value': monthly_productivity_value,
                    'monthly_roi': round(monthly_roi, 0),
                    'payback_days': round(payback_days, 1),
                    'annual_value': monthly_productivity_value * 12
                }
            else:
                # Para programas premium
                productivity_hours_gain = 5
                working_days_year = 250
                
                annual_productivity_value = hourly_rate * productivity_hours_gain * working_days_year
                annual_roi = ((annual_productivity_value - monthly_cost) / monthly_cost) * 100
                payback_days = monthly_cost / (hourly_rate * productivity_hours_gain)
                
                return {
                    'program_cost': monthly_cost,
                    'productivity_hours_gain': productivity_hours_gain,
                    'annual_productivity_value': annual_productivity_value,
                    'annual_roi': round(annual_roi, 0),
                    'payback_days': round(payback_days, 1),
                    'monthly_equivalent_value': annual_productivity_value / 12
                }
            
        except Exception as e:
            logger.error(f"Error calculando ROI: {e}")
            return None
    
    async def adjust_tier_based_on_objection(
        self,
        current_tier: TierType,
        objection_message: str,
        user_profile: Dict[str, Any]
    ) -> TierDetectionResult:
        """Ajustar tier basado en objeciones del usuario."""
        try:
            objection_lower = objection_message.lower()
            
            # Detectar tipo de objeción
            if any(word in objection_lower for word in ['caro', 'precio', 'costoso', 'mucho dinero']):
                # Objeción de precio - bajar tier
                tier_hierarchy = [
                    TierType.PRIME_PREMIUM, TierType.LONGEVITY_PREMIUM,
                    TierType.ELITE, TierType.PRO, TierType.ESSENTIAL
                ]
                
                current_index = tier_hierarchy.index(current_tier)
                if current_index < len(tier_hierarchy) - 1:
                    adjusted_tier = tier_hierarchy[current_index + 1]
                else:
                    adjusted_tier = current_tier
                
                return TierDetectionResult(
                    recommended_tier=adjusted_tier,
                    confidence=0.8,
                    reasoning=f"Ajustado de {current_tier.value} a {adjusted_tier.value} por objeción de precio",
                    price_point=f"${self.tier_pricing[adjusted_tier]}/mes" if adjusted_tier in [TierType.ESSENTIAL, TierType.PRO, TierType.ELITE] else f"${self.tier_pricing[adjusted_tier]}",
                    upsell_potential="medium",
                    demographic_factors={},
                    behavioral_signals=["price_objection"],
                    price_sensitivity="high"
                )
            
            # Si no hay objeción de precio, mantener tier actual
            return TierDetectionResult(
                recommended_tier=current_tier,
                confidence=0.7,
                reasoning="Tier mantenido - objeción no relacionada con precio",
                price_point=f"${self.tier_pricing[current_tier]}/mes" if current_tier in [TierType.ESSENTIAL, TierType.PRO, TierType.ELITE] else f"${self.tier_pricing[current_tier]}",
                upsell_potential="medium",
                demographic_factors={},
                behavioral_signals=["objection_handled"],
                price_sensitivity="medium"
            )
            
        except Exception as e:
            logger.error(f"Error ajustando tier por objeción: {e}")
            return TierDetectionResult(
                recommended_tier=current_tier,
                confidence=0.5,
                reasoning="Error en ajuste, tier mantenido",
                price_point=f"${self.tier_pricing[current_tier]}/mes" if current_tier in [TierType.ESSENTIAL, TierType.PRO, TierType.ELITE] else f"${self.tier_pricing[current_tier]}",
                upsell_potential="low",
                demographic_factors={},
                behavioral_signals=["error"],
                price_sensitivity="unknown"
            )
    
    async def track_tier_progression(self, conversation_id: str, tier_progression: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Trackear progresión de tier durante la conversación."""
        try:
            if not tier_progression:
                return {
                    'conversation_id': conversation_id,
                    'tier_progression': [],
                    'final_tier': None,
                    'progression_score': 0.0
                }
            
            # Analizar progresión
            initial_tier = tier_progression[0]['tier']
            final_tier = tier_progression[-1]['tier']
            
            # Calcular score de progresión
            tier_values = {
                TierType.ESSENTIAL: 1,
                TierType.PRO: 2,
                TierType.ELITE: 3,
                TierType.PRIME_PREMIUM: 4,
                TierType.LONGEVITY_PREMIUM: 4
            }
            
            initial_value = tier_values.get(initial_tier, 1)
            final_value = tier_values.get(final_tier, 1)
            
            progression_score = min(final_value / initial_value, 2.0)  # Max 2.0 para upgrade significativo
            
            return {
                'conversation_id': conversation_id,
                'tier_progression': tier_progression,
                'final_tier': final_tier,
                'progression_score': round(progression_score, 2),
                'tier_upgrades': final_value - initial_value,
                'progression_analysis': 'upgraded' if final_value > initial_value else 'maintained' if final_value == initial_value else 'downgraded'
            }
            
        except Exception as e:
            logger.error(f"Error tracking tier progression: {e}")
            return {
                'conversation_id': conversation_id,
                'tier_progression': [],
                'final_tier': None,
                'progression_score': 0.0,
                'error': str(e)
            }