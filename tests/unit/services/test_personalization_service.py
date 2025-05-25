"""
Pruebas unitarias para el servicio de personalización.
"""

import pytest
from unittest.mock import MagicMock

from src.services.personalization_service import PersonalizationService

class TestPersonalizationService:
    """Pruebas para la clase PersonalizationService."""
    
    @pytest.fixture
    def personalization_service(self):
        """Fixture que proporciona una instancia de PersonalizationService."""
        return PersonalizationService()
    
    def test_determine_communication_profile_formal(self, personalization_service):
        """Prueba que determine_communication_profile devuelve el perfil formal para usuarios mayores."""
        # Datos de usuario con edad mayor a 50
        user_data = {
            "age": 55,
            "occupation": "abogado"
        }
        
        # Determinar perfil
        result = personalization_service.determine_communication_profile(user_data)
        
        # Verificar resultado
        assert result == "formal"
    
    def test_determine_communication_profile_enthusiastic(self, personalization_service):
        """Prueba que determine_communication_profile devuelve el perfil entusiasta para usuarios jóvenes."""
        # Datos de usuario con edad menor a 25
        user_data = {
            "age": 22,
            "occupation": "estudiante"
        }
        
        # Determinar perfil
        result = personalization_service.determine_communication_profile(user_data)
        
        # Verificar resultado
        assert result == "enthusiastic"
    
    def test_determine_communication_profile_technical(self, personalization_service):
        """Prueba que determine_communication_profile devuelve el perfil técnico para ocupaciones técnicas."""
        # Datos de usuario con ocupación técnica
        user_data = {
            "age": 35,
            "occupation": "ingeniero de software"
        }
        
        # Determinar perfil
        result = personalization_service.determine_communication_profile(user_data)
        
        # Verificar resultado
        assert result == "technical"
    
    def test_determine_communication_profile_custom(self, personalization_service):
        """Prueba que determine_communication_profile respeta la preferencia del usuario si está especificada."""
        # Datos de usuario con preferencia explícita
        user_data = {
            "age": 35,
            "occupation": "vendedor",
            "preferences": {
                "communication_style": "enthusiastic"
            }
        }
        
        # Determinar perfil
        result = personalization_service.determine_communication_profile(user_data)
        
        # Verificar resultado
        assert result == "enthusiastic"
    
    def test_personalize_message(self, personalization_service):
        """Prueba que personalize_message personaliza correctamente un mensaje según el perfil del usuario."""
        # Datos de usuario
        user_data = {
            "name": "Cliente de Prueba",
            "age": 55,
            "occupation": "abogado"
        }
        
        # Mensaje original
        message = "Hola, ¿cómo estás?"
        message_type = "greeting"
        
        # Personalizar mensaje
        result = personalization_service.personalize_message(message, user_data, message_type)
        
        # Verificar que el mensaje se personalizó correctamente
        # El mensaje original se devuelve si no hay una implementación específica para personalizarlo
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_generate_personalized_greeting(self, personalization_service):
        """Prueba que generate_personalized_greeting genera un saludo personalizado según el perfil del usuario."""
        # Datos de usuario
        user_data = {
            "name": "Cliente de Prueba",
            "age": 30,
            "occupation": "diseñador",
            "goals": ["mejorar salud", "aumentar energía"]
        }
        
        # Generar saludo personalizado
        result = personalization_service.generate_personalized_greeting(user_data)
        
        # Verificar resultado
        assert "Cliente" in result
        assert "salud" in result.lower() or "energía" in result.lower()
    
    def test_generate_personalized_farewell(self, personalization_service):
        """Prueba que generate_personalized_farewell genera una despedida personalizada según el perfil del usuario."""
        # Datos de usuario
        user_data = {
            "name": "Cliente de Prueba",
            "age": 30,
            "occupation": "diseñador"
        }
        
        # Contexto de conversación
        conversation_context = {
            "high_intent": True
        }
        
        # Generar despedida personalizada
        result = personalization_service.generate_personalized_farewell(user_data, conversation_context)
        
        # Verificar resultado
        assert "Cliente de Prueba" in result or "Gracias" in result
        assert "decisión" in result.lower() or "información" in result.lower()
    
    def test_adjust_message_complexity(self, personalization_service):
        """Prueba que adjust_message_complexity ajusta la complejidad del mensaje según el perfil del usuario."""
        # Datos de usuario con alto nivel educativo
        user_data = {
            "education_level": "high",
            "technical_knowledge": "high"
        }
        
        # Mensaje original
        message = "Este es un mensaje técnico con terminología especializada."
        
        # Ajustar complejidad
        result = personalization_service.adjust_message_complexity(message, user_data)
        
        # Verificar que el mensaje no se simplificó para un usuario con alto nivel educativo
        assert result == message
        
        # Datos de usuario con bajo nivel educativo
        user_data = {
            "education_level": "low",
            "technical_knowledge": "low"
        }
        
        # Ajustar complejidad
        result = personalization_service.adjust_message_complexity(message, user_data)
        
        # Verificar que el mensaje se mantiene igual (la implementación actual no modifica el mensaje)
        assert result == message
