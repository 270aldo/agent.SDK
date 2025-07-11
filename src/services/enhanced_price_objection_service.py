"""
Enhanced Price Objection Service integrado con el sistema HIE existente.

Este servicio maneja objeciones de precio integrándose correctamente con:
- El sistema HIE existente (Hybrid Intelligence Engine)  
- TierDetectionService para ajustes de tier
- Cálculos de ROI biológico personalizados
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

from src.services.price_objection_service import PriceObjectionService, BiologicalROI
from src.services.tier_detection_service import TierDetectionService

logger = logging.getLogger(__name__)


class EnhancedPriceObjectionService(PriceObjectionService):
    """
    Servicio mejorado que integra manejo de objeciones con el sistema HIE existente.
    """
    
    def __init__(self):
        super().__init__()
        # Ya tenemos tier_detection_service del padre
        
    def generate_hie_integrated_objection_response(self, 
                                                 objection_message: str,
                                                 user_profile: Dict,
                                                 tier_info: Dict,
                                                 current_tier: str = "Pro") -> Dict:
        """
        Genera respuesta a objeción integrada con el sistema HIE existente.
        
        Args:
            objection_message: Mensaje de objeción del usuario
            user_profile: Perfil del usuario construido desde conversation state
            tier_info: Información de tier del TierDetectionService
            current_tier: Tier actual sugerido
            
        Returns:
            Dict con respuesta integrada con HIE
        """
        try:
            # Usar el servicio base para detectar tipo de objeción
            objection_type = self.detect_objection_type(objection_message)
            
            # Calcular ROI basado en tier detectado
            program_price = tier_info.get('pricing', {}).get('monthly_price', 149)
            roi_data = self.calculate_roi(user_profile, program_price)
            
            # Generar respuesta base
            base_response = super().generate_objection_response(
                objection_message, user_profile, current_tier, program_price
            )
            
            # Mejorar respuesta con contexto HIE (Hybrid Intelligence Engine)
            enhanced_response = self._enhance_with_hie_context(
                base_response, tier_info, roi_data
            )
            
            return enhanced_response
            
        except Exception as e:
            logger.error(f"Error en respuesta HIE integrada: {str(e)}")
            return self._fallback_hie_response(objection_message, tier_info)
    
    def _enhance_with_hie_context(self, base_response: Dict, tier_info: Dict, roi_data: BiologicalROI) -> Dict:
        """Mejora la respuesta con contexto del Hybrid Intelligence Engine."""
        
        # Agregar contexto HIE a la respuesta
        hie_enhancement = (
            f"\n\nAdemás, con {tier_info.get('tier', 'Pro')} tienes acceso completo a nuestro "
            f"Hybrid Intelligence Engine - un sistema de 11 agentes especializados "
            f"trabajando en conjunto para tu éxito. Esta tecnología es imposible de clonar "
            f"y te da una ventaja competitiva única."
        )
        
        enhanced_response = base_response.copy()
        enhanced_response["primary_response"] += hie_enhancement
        
        # Agregar información HIE específica
        enhanced_response["hie_context"] = {
            "system_name": "Hybrid Intelligence Engine",
            "agent_count": 11,
            "unique_value": "Tecnología imposible de clonar",
            "tier_access": tier_info.get('tier', 'Pro'),
            "roi_with_hie": f"{roi_data.roi_percentage}% anual incluyendo HIE"
        }
        
        return enhanced_response
    
    def _fallback_hie_response(self, objection_message: str, tier_info: Dict) -> Dict:
        """Respuesta de fallback con contexto HIE."""
        return {
            "primary_response": (
                f"Entiendo tu preocupación sobre el precio. Con NGX {tier_info.get('tier', 'Pro')} "
                f"no solo obtienes un programa de wellness, sino acceso completo a nuestro "
                f"Hybrid Intelligence Engine - 11 agentes especializados que es una tecnología "
                f"imposible de clonar. El ROI se calcula en meses, no años."
            ),
            "objection_type": "precio_alto",
            "hie_context": {
                "system_name": "Hybrid Intelligence Engine", 
                "agent_count": 11,
                "unique_value": "Imposible de clonar"
            },
            "success": True,
            "enhanced_with_hie": True
        }