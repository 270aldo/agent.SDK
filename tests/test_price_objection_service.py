"""
Tests for Price Objection Service.
"""

import pytest
from src.services.price_objection_service import (
    PriceObjectionService,
    ObjectionType,
    BiologicalROI
)


class TestPriceObjectionService:
    """Test suite for Price Objection Service."""
    
    def setup_method(self):
        """Setup test environment."""
        self.objection_service = PriceObjectionService()
    
    def test_service_initialization(self):
        """Test that service initializes correctly."""
        assert self.objection_service is not None
        assert self.objection_service.tier_detection_service is not None
        assert self.objection_service.objection_responses is not None
    
    def test_objection_type_detection_precio_alto(self):
        """Test detection of high price objection."""
        messages = [
            "Este programa es muy caro",
            "El precio es demasiado alto",
            "No puedo pagar tanto dinero"
        ]
        
        for message in messages:
            objection_type = self.objection_service.detect_objection_type(message)
            assert objection_type == ObjectionType.PRECIO_ALTO
    
    def test_objection_type_detection_falta_presupuesto(self):
        """Test detection of budget constraint objection."""
        messages = [
            "No tengo presupuesto para esto",
            "Tengo otros gastos prioritarios",
            "Mi situación económica está ajustada"
        ]
        
        for message in messages:
            objection_type = self.objection_service.detect_objection_type(message)
            assert objection_type == ObjectionType.FALTA_PRESUPUESTO
    
    def test_roi_calculation_executive(self):
        """Test ROI calculation for executive profile."""
        user_profile = {
            'edad': 38,
            'hourly_rate': 100,
            'work_hours_per_day': 8
        }
        
        program_price = 149
        roi = self.objection_service.calculate_roi(user_profile, program_price)
        
        assert isinstance(roi, BiologicalROI)
        assert roi.inversion_total == program_price
        assert roi.incremento_productividad > 0
        assert roi.roi_percentage > 100  # Should have positive ROI
        assert roi.payback_months < 12
    
    def test_tier_adjustment_elite_to_pro(self):
        """Test tier adjustment from Elite to Pro."""
        adjustment = self.objection_service.suggest_tier_adjustment(
            "Elite", ObjectionType.PRECIO_ALTO
        )
        
        assert adjustment is not None
        assert adjustment["tier_ajustado"] == "Pro"
        assert adjustment["precio_ajustado"] == 149
        assert adjustment["descuento"] > 0
    
    def test_generate_objection_response_precio_alto(self):
        """Test complete objection response generation."""
        objection_message = "El programa es muy caro"
        user_profile = {
            'edad': 35,
            'hourly_rate': 80,
            'work_hours_per_day': 8
        }
        
        response = self.objection_service.generate_objection_response(
            objection_message, user_profile, "Pro", 149
        )
        
        assert response["success"] is True
        assert response["objection_type"] == "precio_alto"
        assert len(response["primary_response"]) > 50
        assert len(response["primary_response"]) > 20  # Just check it's a substantial response
    
    def test_generate_objection_response_with_tier_adjustment(self):
        """Test objection response that suggests tier adjustment."""
        objection_message = "No tengo presupuesto para esto"
        user_profile = {
            'edad': 28,
            'hourly_rate': 45,
            'work_hours_per_day': 8
        }
        
        response = self.objection_service.generate_objection_response(
            objection_message, user_profile, "Elite", 199
        )
        
        assert response["success"] is True
        assert response["tier_adjustment"] is not None
        assert response["tier_adjustment"]["tier_ajustado"] == "Pro"