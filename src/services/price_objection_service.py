"""
Advanced Price Objection Handling Service.

Sistema avanzado de manejo de objeciones de precio que utiliza
cálculos de ROI biológico para transformar objeciones en oportunidades de venta.
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import random

from src.services.tier_detection_service import TierDetectionService

logger = logging.getLogger(__name__)


class ObjectionType(Enum):
    """Tipos de objeciones de precio identificadas."""
    PRECIO_ALTO = "precio_alto"
    COMPARACION_COMPETENCIA = "comparacion_competencia"
    FALTA_PRESUPUESTO = "falta_presupuesto"
    NECESITO_PENSARLO = "necesito_pensarlo"
    VALOR_DUDOSO = "valor_dudoso"


@dataclass
class BiologicalROI:
    """Cálculo de ROI biológico personalizado."""
    inversion_total: float
    ahorro_medico_anual: float
    incremento_productividad: float
    roi_percentage: float
    payback_months: float


class PriceObjectionService:
    """
    Servicio avanzado de manejo de objeciones de precio con ROI biológico.
    """
    
    def __init__(self):
        self.tier_detection_service = TierDetectionService()
        self.objection_responses = self._initialize_objection_responses()
        
    def _initialize_objection_responses(self) -> Dict[str, Dict]:
        """Inicializa respuestas a objeciones."""
        return {
            ObjectionType.PRECIO_ALTO.value: {
                "triggers": [
                    "muy caro", "precio alto", "demasiado costoso", "fuera de presupuesto",
                    "no puedo pagar", "no tengo tanto dinero", "es mucho dinero"
                ],
                "responses": [
                    "Entiendo que ${precio} puede parecer una inversión considerable. Sin embargo, cuando calculamos el ROI basado en tu perfil profesional, vemos que se paga solo en {payback_months} meses.",
                    "El costo de NO optimizar tu rendimiento es mucho mayor. Estás perdiendo aproximadamente ${costo_diario} diarios en oportunidades no aprovechadas.",
                    "Podemos ajustar el tier. Te ofrezco el plan {tier_ajustado} por ${precio_ajustado}, que mantiene los beneficios core pero es más accesible."
                ]
            },
            
            ObjectionType.FALTA_PRESUPUESTO.value: {
                "triggers": [
                    "no tengo presupuesto", "dinero ajustado", "situación económica",
                    "no puedo permitirme", "gastos apretados", "otros gastos",
                    "gastos prioritarios", "presupuesto ajustado"
                ],
                "responses": [
                    "Entiendo completamente. Basado en tu perfil, estás perdiendo ${perdida_mensual} mensuales en productividad subóptima. El programa no es un gasto, es recuperar dinero que ya estás perdiendo.",
                    "Podemos estructurar un plan de pagos en {meses_pago} cuotas. Tu incremento en productividad cubrirá las mensualidades desde el segundo mes.",
                    "Tengo disponible el tier Essential por ${precio_essential}, que mantiene los beneficios fundamentales a un precio más accesible."
                ]
            },
            
            ObjectionType.COMPARACION_COMPETENCIA.value: {
                "triggers": [
                    "otros programas", "más barato", "competencia", "he visto más económico",
                    "comparar precios", "otras opciones", "alternativas"
                ],
                "responses": [
                    "Los programas más baratos no incluyen nuestro sistema de detección automática de tier y personalización por industria. Esa precisión tiene valor específico.",
                    "La diferencia es que nuestro sistema se adapta automáticamente a tu perfil específico. No es un programa genérico, es personalización de nivel élite.",
                    "Es como comparar un traje a medida con uno de rack. Ambos te cubren, pero uno está diseñado específicamente para ti."
                ]
            },
            
            ObjectionType.NECESITO_PENSARLO.value: {
                "triggers": [
                    "necesito pensarlo", "consultar con pareja", "revisar finanzas",
                    "tomar tiempo", "decidir después", "analizar opciones",
                    "pensarlo", "consultarlo", "tiempo para decidir", "revisar mis finanzas"
                ],
                "responses": [
                    "Completamente entendible. Solo considera que tenemos capacidad limitada para {cupos_mensuales} nuevos clientes por mes. Tu perfil califica hoy, pero la disponibilidad cambia semanalmente.",
                    "Mientras lo analizas, el costo de oportunidad sigue corriendo. Cada día que pases son ${costo_diario} en eficiencia perdida.",
                    "Te puedo reservar tu lugar por 48 horas con solo ${deposito} de depósito. Así tienes tiempo para decidir sin perder la oportunidad."
                ]
            },
            
            ObjectionType.VALOR_DUDOSO.value: {
                "triggers": [
                    "no veo el valor", "qué garantías", "si no funciona",
                    "evidencia resultados", "estudios científicos", "comprobado",
                    "ver evidencia", "evidencia", "garantías", "científicos",
                    "veo claramente el valor", "no veo"
                ],
                "responses": [
                    "El valor es completamente medible. Si no incrementas tu productividad en al menos {mejora_minima}% en 30 días, te reembolsamos completamente.",
                    "Tenemos un 89% de tasa de éxito con perfiles como el tuyo. Estos no son testimonios, son métricas verificables de productividad.",
                    "Tu ROI está calculado en {roi_percentage}% anual. Es matemática, no promesas. Si no alcanzas ese ROI, reembolso total."
                ]
            }
        }
    
    def detect_objection_type(self, customer_message: str) -> ObjectionType:
        """Detecta el tipo de objeción basado en el mensaje del cliente."""
        message_lower = customer_message.lower()
        
        # Order matters - check more specific types first
        detection_order = [
            ObjectionType.NECESITO_PENSARLO,
            ObjectionType.VALOR_DUDOSO,
            ObjectionType.COMPARACION_COMPETENCIA,
            ObjectionType.FALTA_PRESUPUESTO,
            ObjectionType.PRECIO_ALTO
        ]
        
        for objection_type in detection_order:
            data = self.objection_responses[objection_type.value]
            triggers = data.get('triggers', [])
            
            for trigger in triggers:
                if trigger in message_lower:
                    logger.info(f"Detected objection type: {objection_type.value}")
                    return objection_type
        
        return ObjectionType.PRECIO_ALTO
    
    def calculate_roi(self, user_profile: Dict, program_price: float) -> BiologicalROI:
        """Calcula ROI personalizado basado en perfil del usuario."""
        try:
            hourly_rate = user_profile.get('hourly_rate', 50)
            age = user_profile.get('edad', 35)
            work_hours = user_profile.get('work_hours_per_day', 8)
            
            # Cálculo de incremento de productividad (conservador)
            productivity_improvement = 0.15  # 15% improvement
            daily_value_increase = hourly_rate * work_hours * productivity_improvement
            annual_productivity_gain = daily_value_increase * 250  # work days
            
            # Cálculo de ahorro médico por edad
            if age < 35:
                annual_health_savings = 1500
            elif age < 50:
                annual_health_savings = 3000
            else:
                annual_health_savings = 4500
                
            total_annual_value = annual_productivity_gain + annual_health_savings
            roi_percentage = ((total_annual_value - program_price) / program_price) * 100
            payback_months = program_price / (total_annual_value / 12)
            
            return BiologicalROI(
                inversion_total=program_price,
                ahorro_medico_anual=annual_health_savings,
                incremento_productividad=annual_productivity_gain,
                roi_percentage=round(roi_percentage, 1),
                payback_months=round(payback_months, 1)
            )
            
        except Exception as e:
            logger.error(f"Error calculating ROI: {str(e)}")
            # Conservative fallback
            return BiologicalROI(
                inversion_total=program_price,
                ahorro_medico_anual=2500,
                incremento_productividad=6000,
                roi_percentage=300,
                payback_months=6.0
            )
    
    def suggest_tier_adjustment(self, current_tier: str, objection_type: ObjectionType) -> Optional[Dict]:
        """Sugiere ajuste de tier basado en objeción."""
        if objection_type in [ObjectionType.PRECIO_ALTO, ObjectionType.FALTA_PRESUPUESTO]:
            if current_tier == "Elite":
                return {
                    "tier_ajustado": "Pro",
                    "precio_ajustado": 149,
                    "descuento": 0.25,
                    "razon": "Mantiene beneficios core a precio más accesible"
                }
            elif current_tier == "Pro":
                return {
                    "tier_ajustado": "Essential", 
                    "precio_ajustado": 79,
                    "descuento": 0.47,
                    "razon": "Entrada perfecta al sistema con upgrade posterior"
                }
        return None
    
    def generate_objection_response(self, 
                                  objection_message: str,
                                  user_profile: Dict,
                                  current_tier: str = "Pro",
                                  program_price: float = 149) -> Dict:
        """Genera respuesta completa a objeción de precio."""
        try:
            objection_type = self.detect_objection_type(objection_message)
            roi_data = self.calculate_roi(user_profile, program_price)
            tier_adjustment = self.suggest_tier_adjustment(current_tier, objection_type)
            
            # Get response template
            objection_data = self.objection_responses[objection_type.value]
            response_template = random.choice(objection_data['responses'])
            
            # Calculate variables for response
            edad = user_profile.get('edad', 35)
            costo_diario = round(roi_data.incremento_productividad / 250, 2)
            perdida_mensual = round(roi_data.incremento_productividad / 12, 2)
            
            # Format response
            response = response_template.format(
                precio=program_price,
                payback_months=roi_data.payback_months,
                costo_diario=costo_diario,
                perdida_mensual=perdida_mensual,
                tier_ajustado=tier_adjustment['tier_ajustado'] if tier_adjustment else current_tier,
                precio_ajustado=tier_adjustment['precio_ajustado'] if tier_adjustment else program_price,
                meses_pago=6,
                precio_essential=79,
                cupos_mensuales=15,
                deposito=29,
                mejora_minima=15,
                roi_percentage=roi_data.roi_percentage
            )
            
            return {
                "primary_response": response,
                "objection_type": objection_type.value,
                "roi_data": {
                    "roi_percentage": roi_data.roi_percentage,
                    "payback_months": roi_data.payback_months,
                    "annual_value": roi_data.incremento_productividad + roi_data.ahorro_medico_anual
                },
                "tier_adjustment": tier_adjustment,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error generating objection response: {str(e)}")
            return {
                "primary_response": f"Entiendo tu preocupación sobre el precio. Déjame mostrarte cómo el programa se paga solo en menos de 6 meses basado en incremento de productividad. ¿Te parece si revisamos los números específicos para tu situación?",
                "objection_type": "precio_alto",
                "error": str(e),
                "success": False
            }