"""
Pruebas unitarias para el servicio de recomendaciones.
"""

import pytest
from unittest.mock import patch, MagicMock
from src.services.recommendation_service import RecommendationService

class TestRecommendationService:
    """Pruebas para el servicio de recomendaciones."""
    
    @pytest.fixture
    def recommendation_service(self):
        """Fixture para crear una instancia del servicio de recomendaciones."""
        return RecommendationService()
    
    def test_generate_recommendations_without_insights(self, recommendation_service):
        """Prueba que generate_recommendations maneje correctamente el caso sin insights."""
        # Mock del servicio NLP para devolver sin insights
        recommendation_service.nlp_service.get_conversation_insights = MagicMock(
            return_value={"has_insights": False}
        )
        
        result = recommendation_service.generate_recommendations("conv123")
        
        assert result["has_recommendations"] == False
        assert "message" in result
    
    def test_generate_recommendations_with_insights(self, recommendation_service):
        """Prueba que generate_recommendations genere recomendaciones cuando hay insights."""
        # Mock de los servicios
        recommendation_service.nlp_service.get_conversation_insights = MagicMock(
            return_value={
                "has_insights": True,
                "user_profile": {
                    "personal_info": {"name": "Juan"},
                    "interests": ["producto", "precio", "calidad"],
                    "communication_style": "formal",
                    "technical_level": "medio"
                },
                "conversation_status": {
                    "satisfaction": "neutral",
                    "urgency": "baja",
                    "conversation_phase": "exploración",
                    "engagement": "medio"
                }
            }
        )
        
        recommendation_service.entity_service.get_conversation_entities = MagicMock(
            return_value={
                "producto": ["NGX Prime Membership"],
                "nombre_persona": ["Juan"],
                "correo_electronico": ["juan@example.com"]
            }
        )
        
        recommendation_service.intent_service.get_conversation_intents = MagicMock(
            return_value={
                "información_producto": 0.8,
                "información_precio": 0.7,
                "salud": 0.6
            }
        )
        
        recommendation_service.keyword_service.get_top_keywords = MagicMock(
            return_value=[("producto", 0.8), ("precio", 0.7), ("salud", 0.6)]
        )
        
        result = recommendation_service.generate_recommendations("conv123")
        
        assert result["has_recommendations"] == True
        assert "products" in result
        assert "content" in result
        assert "next_actions" in result
        assert "personalized_message" in result
        
        # Verificar que se guarde en caché
        assert "conv123" in recommendation_service.recommendations_cache
    
    def test_get_cached_recommendations(self, recommendation_service):
        """Prueba que get_cached_recommendations obtenga correctamente las recomendaciones almacenadas."""
        # Almacenar recomendaciones en caché
        cached_recommendations = {
            "has_recommendations": True,
            "products": [{"id": "prod001", "name": "Test Product"}],
            "content": [{"id": "cont001", "title": "Test Content"}],
            "next_actions": [{"action": "test_action", "description": "Test Action"}],
            "personalized_message": "Test Message"
        }
        
        recommendation_service.recommendations_cache["conv123"] = cached_recommendations
        
        result = recommendation_service.get_cached_recommendations("conv123")
        
        assert result == cached_recommendations
    
    def test_get_cached_recommendations_nonexistent(self, recommendation_service):
        """Prueba que get_cached_recommendations maneje correctamente conversaciones inexistentes."""
        result = recommendation_service.get_cached_recommendations("nonexistent_id")
        
        assert result["has_recommendations"] == False
        assert "message" in result
    
    def test_clear_recommendations(self, recommendation_service):
        """Prueba que clear_recommendations limpie correctamente las recomendaciones almacenadas."""
        # Almacenar recomendaciones en caché
        recommendation_service.recommendations_cache["conv123"] = {
            "has_recommendations": True,
            "products": [{"id": "prod001", "name": "Test Product"}]
        }
        
        # Verificar que existan en caché
        assert "conv123" in recommendation_service.recommendations_cache
        
        # Limpiar recomendaciones
        recommendation_service.clear_recommendations("conv123")
        
        # Verificar que se hayan eliminado
        assert "conv123" not in recommendation_service.recommendations_cache
    
    def test_generate_product_recommendations(self, recommendation_service):
        """Prueba que _generate_product_recommendations genere correctamente recomendaciones de productos."""
        entities = {
            "producto": ["NGX Prime Membership"],
            "nombre_persona": ["Juan"]
        }
        
        intents = {
            "información_producto": 0.8,
            "salud": 0.7
        }
        
        keywords = [("producto", 0.8), ("salud", 0.7), ("premium", 0.6)]
        
        result = recommendation_service._generate_product_recommendations(entities, intents, keywords)
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert all("id" in product for product in result)
        assert all("name" in product for product in result)
        assert all("description" in product for product in result)
        assert all("price" in product for product in result)
        assert all("relevance_score" in product for product in result)
        assert all("reason" in product for product in result)
    
    def test_generate_content_recommendations(self, recommendation_service):
        """Prueba que _generate_content_recommendations genere correctamente recomendaciones de contenido."""
        entities = {
            "producto": ["NGX Prime Membership"],
            "nombre_persona": ["Juan"]
        }
        
        intents = {
            "información_producto": 0.8,
            "educacion": 0.7
        }
        
        keywords = [("salud", 0.8), ("nutrición", 0.7), ("ejercicio", 0.6)]
        
        result = recommendation_service._generate_content_recommendations(entities, intents, keywords)
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert all("id" in content for content in result)
        assert all("title" in content for content in result)
        assert all("type" in content for content in result)
        assert all("url" in content for content in result)
        assert all("relevance_score" in content for content in result)
        assert all("reason" in content for content in result)
    
    def test_generate_next_action_recommendations_exploration(self, recommendation_service):
        """Prueba que _generate_next_action_recommendations genere correctamente recomendaciones para fase de exploración."""
        insights = {
            "has_insights": True,
            "conversation_status": {
                "conversation_phase": "exploración",
                "satisfaction": "neutral",
                "urgency": "baja"
            }
        }
        
        result = recommendation_service._generate_next_action_recommendations(insights)
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert all("action" in action for action in result)
        assert all("description" in action for action in result)
        assert all("priority" in action for action in result)
        assert all("reason" in action for action in result)
    
    def test_generate_next_action_recommendations_decision(self, recommendation_service):
        """Prueba que _generate_next_action_recommendations genere correctamente recomendaciones para fase de decisión."""
        insights = {
            "has_insights": True,
            "conversation_status": {
                "conversation_phase": "decisión",
                "satisfaction": "neutral",
                "urgency": "baja"
            }
        }
        
        result = recommendation_service._generate_next_action_recommendations(insights)
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert any(action["action"] == "ofrecer_descuento" for action in result)
        assert any(action["action"] == "programar_llamada" for action in result)
    
    def test_generate_next_action_recommendations_high_urgency(self, recommendation_service):
        """Prueba que _generate_next_action_recommendations ajuste la prioridad con alta urgencia."""
        insights = {
            "has_insights": True,
            "conversation_status": {
                "conversation_phase": "exploración",
                "satisfaction": "neutral",
                "urgency": "alta"
            }
        }
        
        result = recommendation_service._generate_next_action_recommendations(insights)
        
        assert all(action["priority"] == "alta" for action in result)
        assert all("alta urgencia" in action["reason"] for action in result)
    
    def test_generate_recommendation_reason(self, recommendation_service):
        """Prueba que _generate_recommendation_reason genere correctamente razones para recomendaciones de productos."""
        product = {
            "id": "prod001",
            "name": "NGX Prime Membership",
            "description": "Membresía premium con acceso a todas las funcionalidades",
            "price": 99.99,
            "tags": ["premium", "membership", "complete"]
        }
        
        keywords = ["premium", "membership"]
        interests = ["premium"]
        
        result = recommendation_service._generate_recommendation_reason(product, keywords, interests)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "premium" in result.lower()
    
    def test_generate_content_reason(self, recommendation_service):
        """Prueba que _generate_content_reason genere correctamente razones para recomendaciones de contenido."""
        content = {
            "id": "cont001",
            "title": "Guía de Nutrición Personalizada",
            "type": "guide",
            "url": "/content/nutrition-guide",
            "tags": ["nutrition", "diet", "health"]
        }
        
        keywords = ["nutrición", "dieta"]
        interests = ["information"]
        
        result = recommendation_service._generate_content_reason(content, keywords, interests)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "nutrición" in result.lower() or "dieta" in result.lower()
        assert "guía" in result.lower()
    
    def test_generate_personalized_message_exploration(self, recommendation_service):
        """Prueba que _generate_personalized_message genere correctamente mensajes para fase de exploración."""
        insights = {
            "has_insights": True,
            "user_profile": {
                "personal_info": {"name": "Juan"}
            },
            "conversation_status": {
                "conversation_phase": "exploración"
            }
        }
        
        result = recommendation_service._generate_personalized_message(insights)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "Juan" in result
        assert "exploración" in result.lower() or "conocer" in result.lower()
    
    def test_generate_personalized_message_decision(self, recommendation_service):
        """Prueba que _generate_personalized_message genere correctamente mensajes para fase de decisión."""
        insights = {
            "has_insights": True,
            "user_profile": {
                "personal_info": {"name": "Juan"}
            },
            "conversation_status": {
                "conversation_phase": "decisión"
            }
        }
        
        result = recommendation_service._generate_personalized_message(insights)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "Juan" in result
        assert "decisión" in result.lower() or "considerando" in result.lower()
    
    def test_generate_personalized_message_without_insights(self, recommendation_service):
        """Prueba que _generate_personalized_message maneje correctamente el caso sin insights."""
        insights = {
            "has_insights": False
        }
        
        result = recommendation_service._generate_personalized_message(insights)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "Gracias por tu interés" in result
