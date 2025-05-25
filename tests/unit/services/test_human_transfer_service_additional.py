"""
Pruebas adicionales para el servicio de transferencia humana.
"""

import pytest
from unittest.mock import MagicMock
from src.services.human_transfer_service import HumanTransferService

class TestHumanTransferServiceAdditional:
    """Pruebas adicionales para la clase HumanTransferService."""
    
    def test_detect_transfer_request(self):
        """Prueba que detect_transfer_request detecta correctamente una solicitud de transferencia."""
        # Crear servicio
        service = HumanTransferService()
        
        # Probar con un mensaje que contiene una solicitud de transferencia
        result = service.detect_transfer_request("Quiero hablar con una persona real, por favor")
        
        # Verificar resultado
        assert result is True
        
        # Probar con un mensaje que no contiene una solicitud de transferencia
        result = service.detect_transfer_request("¿Cuáles son los precios de sus productos?")
        
        # Verificar resultado
        assert result is False
    
    def test_generate_transfer_message(self):
        """Prueba que generate_transfer_message genera correctamente un mensaje de transferencia."""
        # Crear servicio
        service = HumanTransferService()
        
        # Generar mensaje de transferencia
        result = service.generate_transfer_message(wait_time=3)
        
        # Verificar resultado
        assert isinstance(result, str)
        assert "3 minutos" in result
        assert "transfiriendo" in result.lower()
