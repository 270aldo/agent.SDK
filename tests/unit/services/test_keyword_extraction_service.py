"""
Pruebas unitarias para el servicio de extracción de palabras clave.
"""

import pytest
from src.services.keyword_extraction_service import KeywordExtractionService

class TestKeywordExtractionService:
    """Pruebas para el servicio de extracción de palabras clave."""
    
    @pytest.fixture
    def keyword_service(self):
        """Fixture para crear una instancia del servicio de extracción de palabras clave."""
        return KeywordExtractionService()
    
    def test_preprocess_text(self, keyword_service):
        """Prueba que preprocess_text preprocese correctamente el texto."""
        text = "¡Hola! ¿Cómo estás? Me gustaría saber más sobre el producto #123."
        result = keyword_service.preprocess_text(text)
        
        assert result == "hola cómo estás me gustaría saber más sobre el producto"
        assert result.islower()
        assert "#" not in result
        assert "123" not in result
    
    def test_extract_keywords(self, keyword_service):
        """Prueba que extract_keywords extraiga correctamente palabras clave."""
        text = "Me gustaría saber más sobre el producto y sus características técnicas. El producto tiene buenas características."
        result = keyword_service.extract_keywords(text)
        
        assert len(result) > 0
        assert "producto" in result
        assert "características" in result
        # Las stopwords no deberían estar presentes
        assert "el" not in result
        assert "y" not in result
        assert "sus" not in result
    
    def test_extract_ngrams(self, keyword_service):
        """Prueba que extract_ngrams extraiga correctamente n-gramas."""
        text = "El producto tiene características técnicas avanzadas. Las características técnicas son importantes."
        result = keyword_service.extract_ngrams(text, n=2, min_freq=1)
        
        assert len(result) > 0
        assert "características técnicas" in result
    
    def test_classify_keywords(self, keyword_service):
        """Prueba que classify_keywords clasifique correctamente palabras clave."""
        keywords = ["producto", "precio", "calidad", "problema", "soporte"]
        result = keyword_service.classify_keywords(keywords)
        
        assert "producto" in result
        assert "precio" in result
        assert "calidad" in result
        assert "problema" in result
        assert "soporte" in result
    
    def test_extract_keywords_with_scores(self, keyword_service):
        """Prueba que extract_keywords_with_scores extraiga palabras clave con puntuaciones."""
        text = "El producto tiene un buen precio. El precio es importante para mí."
        result = keyword_service.extract_keywords_with_scores(text)
        
        assert len(result) > 0
        assert "producto" in result
        assert "precio" in result
        assert isinstance(result["precio"], float)
        assert 0 <= result["precio"] <= 1
    
    def test_update_conversation_keywords(self, keyword_service):
        """Prueba que update_conversation_keywords actualice correctamente las palabras clave de una conversación."""
        conversation_id = "conv123"
        text = "Me interesa conocer el precio del producto y sus características técnicas."
        
        # Actualizar palabras clave
        keyword_service.update_conversation_keywords(conversation_id, text, 'user')
        result = keyword_service.get_conversation_keywords(conversation_id)
        
        assert "keywords" in result
        assert len(result["keywords"]) > 0
        assert "ngrams" in result
        assert "categories" in result
    
    def test_ignore_assistant_messages(self, keyword_service):
        """Prueba que update_conversation_keywords ignore los mensajes del asistente."""
        conversation_id = "conv123"
        text = "El producto tiene un precio de $100 y excelentes características técnicas."
        
        # Actualizar con mensaje del asistente
        keyword_service.update_conversation_keywords(conversation_id, text, 'assistant')
        result = keyword_service.get_conversation_keywords(conversation_id)
        
        # No debería haber palabras clave
        assert result["keywords"] == {}
        assert result["ngrams"] == []
        assert result["categories"] == {}
    
    def test_clear_conversation_keywords(self, keyword_service):
        """Prueba que clear_conversation_keywords elimine correctamente las palabras clave de una conversación."""
        conversation_id = "conv123"
        text = "Me interesa conocer el precio del producto."
        
        # Actualizar palabras clave
        keyword_service.update_conversation_keywords(conversation_id, text, 'user')
        assert keyword_service.get_conversation_keywords(conversation_id)["keywords"] != {}
        
        # Limpiar palabras clave
        keyword_service.clear_conversation_keywords(conversation_id)
        result = keyword_service.get_conversation_keywords(conversation_id)
        
        assert result["keywords"] == {}
        assert result["ngrams"] == []
        assert result["categories"] == {}
    
    def test_get_top_keywords(self, keyword_service):
        """Prueba que get_top_keywords obtenga correctamente las palabras clave más relevantes."""
        conversation_id = "conv123"
        text1 = "Me interesa conocer el precio del producto."
        text2 = "El precio es un factor importante para mí."
        
        # Actualizar con varios mensajes
        keyword_service.update_conversation_keywords(conversation_id, text1, 'user')
        keyword_service.update_conversation_keywords(conversation_id, text2, 'user')
        
        result = keyword_service.get_top_keywords(conversation_id, 3)
        
        assert len(result) <= 3
        assert isinstance(result, list)
        assert all(isinstance(item, tuple) for item in result)
        assert all(isinstance(item[0], str) and isinstance(item[1], float) for item in result)
    
    def test_get_top_ngrams(self, keyword_service):
        """Prueba que get_top_ngrams obtenga correctamente los n-gramas más frecuentes."""
        conversation_id = "conv123"
        text1 = "El producto tiene características técnicas avanzadas."
        text2 = "Las características técnicas son importantes para mí."
        
        # Actualizar con varios mensajes
        keyword_service.update_conversation_keywords(conversation_id, text1, 'user')
        keyword_service.update_conversation_keywords(conversation_id, text2, 'user')
        
        result = keyword_service.get_top_ngrams(conversation_id, 2)
        
        assert len(result) <= 2
        assert isinstance(result, list)
        assert all(isinstance(item, str) for item in result)
    
    def test_get_dominant_categories(self, keyword_service):
        """Prueba que get_dominant_categories obtenga correctamente las categorías dominantes."""
        conversation_id = "conv123"
        text = "Me interesa conocer el precio del producto y su calidad. ¿Hay algún problema conocido?"
        
        # Actualizar palabras clave
        keyword_service.update_conversation_keywords(conversation_id, text, 'user')
        
        result = keyword_service.get_dominant_categories(conversation_id)
        
        assert isinstance(result, dict)
        assert all(isinstance(k, str) and isinstance(v, int) for k, v in result.items())
    
    def test_analyze_text(self, keyword_service):
        """Prueba que analyze_text realice un análisis completo de palabras clave."""
        text = "Me interesa conocer el precio del producto y sus características técnicas. La calidad es importante."
        result = keyword_service.analyze_text(text)
        
        assert "keywords" in result
        assert "ngrams" in result
        assert "categories" in result
        assert "dominant_category" in result
    
    def test_analyze_conversation(self, keyword_service):
        """Prueba que analyze_conversation analice correctamente una conversación completa."""
        messages = [
            {"role": "user", "content": "Me interesa conocer el precio del producto."},
            {"role": "assistant", "content": "El precio base es $100."},
            {"role": "user", "content": "¿Qué características técnicas tiene?"},
            {"role": "assistant", "content": "Tiene características avanzadas como..."},
            {"role": "user", "content": "La calidad es importante para mí."}
        ]
        
        result = keyword_service.analyze_conversation(messages, "conv_test")
        
        assert "has_keywords" in result
        assert "message_count" in result
        assert "full_analysis" in result
        assert "message_analyses" in result
        assert "conversation_keywords" in result
    
    def test_analyze_conversation_without_user_messages(self, keyword_service):
        """Prueba que analyze_conversation maneje correctamente conversaciones sin mensajes de usuario."""
        messages = [
            {"role": "assistant", "content": "Hola, ¿en qué puedo ayudarte?"},
            {"role": "assistant", "content": "¿Hay algo en lo que pueda asistirte?"}
        ]
        
        result = keyword_service.analyze_conversation(messages)
        
        assert result["has_keywords"] == False
        assert "message" in result
    
    def test_get_keyword_summary_with_keywords(self, keyword_service):
        """Prueba que get_keyword_summary genere un resumen correcto para una conversación con palabras clave."""
        conversation_id = "conv123"
        text = "Me interesa conocer el precio del producto y sus características técnicas. La calidad es importante."
        
        # Actualizar palabras clave
        keyword_service.update_conversation_keywords(conversation_id, text, 'user')
        
        result = keyword_service.get_keyword_summary(conversation_id)
        
        assert result["has_keywords"] == True
        assert "top_keywords" in result
        assert "top_ngrams" in result
        assert "dominant_categories" in result
        assert "summary" in result
        assert isinstance(result["summary"], str)
    
    def test_get_keyword_summary_without_keywords(self, keyword_service):
        """Prueba que get_keyword_summary genere un resumen correcto para una conversación sin palabras clave."""
        conversation_id = "conv_empty"
        result = keyword_service.get_keyword_summary(conversation_id)
        
        assert result["has_keywords"] == False
        assert "summary" in result
        assert result["summary"] == "No se han detectado palabras clave relevantes en esta conversación."
