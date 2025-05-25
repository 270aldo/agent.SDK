"""
Pruebas unitarias para el servicio de integración de NLP.
"""

import pytest
from unittest.mock import patch, MagicMock
from src.services.nlp_integration_service import NLPIntegrationService

class TestNLPIntegrationService:
    """Pruebas para el servicio de integración de NLP."""
    
    @pytest.fixture
    def nlp_service(self):
        """Fixture para crear una instancia del servicio de integración de NLP."""
        return NLPIntegrationService()
    
    def test_analyze_message(self, nlp_service):
        """Prueba que analyze_message realice un análisis completo de un mensaje."""
        text = "Me gustaría saber el precio del producto XYZ. Estoy muy interesado."
        result = nlp_service.analyze_message(text)
        
        assert "sentiment" in result
        assert "entities" in result
        assert "questions" in result
        assert "intent" in result
        assert "keywords" in result
    
    def test_analyze_message_with_conversation_id(self, nlp_service):
        """Prueba que analyze_message actualice el análisis de la conversación cuando se proporciona un ID."""
        text = "Me gustaría saber el precio del producto XYZ. Estoy muy interesado."
        conversation_id = "conv123"
        result = nlp_service.analyze_message(text, conversation_id)
        
        # Verificar que se actualicen las entidades, intenciones y palabras clave
        entity_summary = nlp_service.entity_service.get_entity_summary(conversation_id)
        intent_summary = nlp_service.intent_service.get_intent_summary(conversation_id)
        keyword_summary = nlp_service.keyword_service.get_keyword_summary(conversation_id)
        
        assert entity_summary["has_entities"] == True
        assert intent_summary["has_intents"] == True
        assert keyword_summary["has_keywords"] == True
    
    def test_analyze_conversation(self, nlp_service):
        """Prueba que analyze_conversation realice un análisis completo de una conversación."""
        messages = [
            {"role": "user", "content": "Hola, me gustaría información sobre el producto XYZ."},
            {"role": "assistant", "content": "Claro, ¿qué te gustaría saber sobre el producto XYZ?"},
            {"role": "user", "content": "¿Cuál es su precio y características principales?"}
        ]
        conversation_id = "conv123"
        
        result = nlp_service.analyze_conversation(messages, conversation_id)
        
        assert "sentiment" in result
        assert "entities" in result
        assert "questions" in result
        assert "intent" in result
        assert "keywords" in result
        
        # Verificar que se guarde el análisis en caché
        cached_analysis = nlp_service.get_conversation_analysis(conversation_id)
        assert cached_analysis != {}
    
    def test_get_conversation_analysis(self, nlp_service):
        """Prueba que get_conversation_analysis obtenga correctamente el análisis almacenado."""
        messages = [
            {"role": "user", "content": "Hola, me gustaría información sobre el producto XYZ."}
        ]
        conversation_id = "conv123"
        
        # Analizar conversación
        nlp_service.analyze_conversation(messages, conversation_id)
        
        # Obtener análisis
        result = nlp_service.get_conversation_analysis(conversation_id)
        
        assert result != {}
        assert "sentiment" in result
        assert "entities" in result
        assert "questions" in result
        assert "intent" in result
        assert "keywords" in result
    
    def test_get_conversation_analysis_nonexistent(self, nlp_service):
        """Prueba que get_conversation_analysis devuelva un diccionario vacío para conversaciones inexistentes."""
        result = nlp_service.get_conversation_analysis("nonexistent_id")
        assert result == {}
    
    def test_clear_conversation_analysis(self, nlp_service):
        """Prueba que clear_conversation_analysis limpie correctamente el análisis almacenado."""
        messages = [
            {"role": "user", "content": "Hola, me gustaría información sobre el producto XYZ."}
        ]
        conversation_id = "conv123"
        
        # Analizar conversación
        nlp_service.analyze_conversation(messages, conversation_id)
        
        # Verificar que se haya guardado el análisis
        assert nlp_service.get_conversation_analysis(conversation_id) != {}
        
        # Limpiar análisis
        nlp_service.clear_conversation_analysis(conversation_id)
        
        # Verificar que se haya limpiado el análisis
        assert nlp_service.get_conversation_analysis(conversation_id) == {}
    
    def test_get_conversation_insights(self, nlp_service):
        """Prueba que get_conversation_insights genere insights útiles basados en el análisis."""
        messages = [
            {"role": "user", "content": "Hola, me llamo Juan y mi correo es juan@example.com. Me gustaría información sobre el producto XYZ."},
            {"role": "assistant", "content": "Hola Juan, ¿qué te gustaría saber sobre el producto XYZ?"},
            {"role": "user", "content": "¿Cuál es su precio y características técnicas principales?"}
        ]
        conversation_id = "conv123"
        
        # Analizar conversación
        nlp_service.analyze_conversation(messages, conversation_id)
        
        # Obtener insights
        result = nlp_service.get_conversation_insights(conversation_id)
        
        assert result["has_insights"] == True
        assert "user_profile" in result
        assert "conversation_status" in result
        assert "recommended_actions" in result
        assert "key_topics" in result
    
    def test_get_conversation_insights_nonexistent(self, nlp_service):
        """Prueba que get_conversation_insights maneje correctamente conversaciones inexistentes."""
        result = nlp_service.get_conversation_insights("nonexistent_id")
        
        assert result["has_insights"] == False
        assert "message" in result
    
    def test_generate_user_profile(self, nlp_service):
        """Prueba que _generate_user_profile genere correctamente un perfil de usuario."""
        messages = [
            {"role": "user", "content": "Hola, me llamo María y mi correo es maria@example.com. Mi teléfono es 123-456-7890."},
            {"role": "assistant", "content": "Hola María, ¿en qué puedo ayudarte?"},
            {"role": "user", "content": "Me interesa el producto XYZ por sus características técnicas avanzadas."}
        ]
        conversation_id = "conv123"
        
        # Analizar conversación
        analysis = nlp_service.analyze_conversation(messages, conversation_id)
        
        # Generar perfil de usuario
        profile = nlp_service._generate_user_profile(conversation_id, analysis)
        
        assert "personal_info" in profile
        assert "interests" in profile
        assert "communication_style" in profile
        assert "technical_level" in profile
    
    def test_determine_conversation_status(self, nlp_service):
        """Prueba que _determine_conversation_status determine correctamente el estado de la conversación."""
        analysis = {
            "sentiment": {
                "overall_sentiment": "positivo",
                "sentiment_trend": "mejorando",
                "urgency": "baja"
            },
            "intent": {
                "predominant_intent": "información_producto"
            },
            "questions": {
                "question_count": 3
            }
        }
        
        status = nlp_service._determine_conversation_status(analysis)
        
        assert "satisfaction" in status
        assert "urgency" in status
        assert "conversation_phase" in status
        assert "engagement" in status
    
    def test_generate_recommended_actions(self, nlp_service):
        """Prueba que _generate_recommended_actions genere correctamente acciones recomendadas."""
        analysis = {
            "sentiment": {
                "overall_sentiment": "negativo",
                "urgency": "alta"
            },
            "intent": {
                "predominant_intent": "soporte_técnico"
            },
            "questions": {
                "predominant_complexity": "alta"
            }
        }
        
        actions = nlp_service._generate_recommended_actions(analysis)
        
        assert len(actions) > 0
        assert all("type" in action for action in actions)
        assert all("action" in action for action in actions)
        assert all("description" in action for action in actions)
    
    def test_extract_key_topics(self, nlp_service):
        """Prueba que _extract_key_topics extraiga correctamente los temas clave."""
        analysis = {
            "keywords": {
                "top_keywords": [("producto", 0.8), ("precio", 0.7), ("calidad", 0.6)],
                "dominant_categories": [("tecnología", 3), ("ventas", 2)]
            }
        }
        
        topics = nlp_service._extract_key_topics(analysis)
        
        assert len(topics) > 0
        assert "producto" in topics
        assert "tecnología" in topics
