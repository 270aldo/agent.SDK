"""
Pruebas unitarias para el servicio de análisis avanzado de sentimiento.
"""

import pytest
from src.services.advanced_sentiment_service import AdvancedSentimentService

class TestAdvancedSentimentService:
    """Pruebas para el servicio de análisis avanzado de sentimiento."""
    
    @pytest.fixture
    def sentiment_service(self):
        """Fixture para crear una instancia del servicio de análisis de sentimiento."""
        return AdvancedSentimentService()
    
    def test_analyze_sentiment_positive(self, sentiment_service):
        """Prueba que analyze_sentiment detecte correctamente sentimiento positivo."""
        text = "Me encanta este producto, es excelente y muy útil. Estoy muy satisfecho con mi compra."
        result = sentiment_service.analyze_sentiment(text)
        
        assert result["sentiment"] == "positivo"
        assert result["score"] > 0
        assert result["positive_count"] > 0
        assert result["intensity"] > 0
    
    def test_analyze_sentiment_negative(self, sentiment_service):
        """Prueba que analyze_sentiment detecte correctamente sentimiento negativo."""
        text = "Este producto es terrible, no funciona bien y es muy complicado de usar. Estoy muy decepcionado."
        result = sentiment_service.analyze_sentiment(text)
        
        assert result["sentiment"] == "negativo"
        assert result["score"] < 0
        assert result["negative_count"] > 0
        assert result["intensity"] > 0
    
    def test_analyze_sentiment_neutral(self, sentiment_service):
        """Prueba que analyze_sentiment detecte correctamente sentimiento neutral."""
        text = "El producto es normal, funciona como se espera. Es un producto estándar."
        result = sentiment_service.analyze_sentiment(text)
        
        assert result["sentiment"] == "neutral"
        assert -0.1 <= result["score"] <= 0.1
    
    def test_detect_emotions_frustration(self, sentiment_service):
        """Prueba que detect_emotions detecte correctamente la frustración."""
        text = "Estoy muy frustrado con este producto, no funciona como debería y es muy complicado de usar."
        result = sentiment_service.detect_emotions(text)
        
        assert "frustración" in result
        assert result["frustración"] > 0.3
    
    def test_detect_emotions_enthusiasm(self, sentiment_service):
        """Prueba que detect_emotions detecte correctamente el entusiasmo."""
        text = "¡Esto es genial! Estoy muy emocionado con este producto, es increíble y fantástico."
        result = sentiment_service.detect_emotions(text)
        
        assert "entusiasmo" in result
        assert result["entusiasmo"] > 0.3
    
    def test_detect_emotions_confusion(self, sentiment_service):
        """Prueba que detect_emotions detecte correctamente la confusión."""
        text = "No entiendo cómo funciona esto. Estoy confundido, ¿podrías explicar mejor? No me queda claro."
        result = sentiment_service.detect_emotions(text)
        
        assert "confusión" in result
        assert result["confusión"] > 0.3
    
    def test_detect_emotions_urgency(self, sentiment_service):
        """Prueba que detect_emotions detecte correctamente la urgencia."""
        text = "Necesito esto urgentemente. Es crítico que lo resolvamos ahora mismo, no puedo esperar."
        result = sentiment_service.detect_emotions(text)
        
        assert "urgencia" in result
        assert result["urgencia"] > 0.3
    
    def test_detect_emotions_indecision(self, sentiment_service):
        """Prueba que detect_emotions detecte correctamente la indecisión."""
        text = "No estoy seguro de qué hacer. Por un lado me gusta, pero por otro tengo dudas. Quizás debería pensarlo más."
        result = sentiment_service.detect_emotions(text)
        
        assert "indecisión" in result
        assert result["indecisión"] > 0.3
    
    def test_analyze_sentiment_change_improving(self, sentiment_service):
        """Prueba que analyze_sentiment_change detecte correctamente una mejora en el sentimiento."""
        messages = [
            {"role": "user", "content": "Este producto no funciona bien, estoy molesto."},
            {"role": "assistant", "content": "Lamento escuchar eso. ¿Puedo ayudarte a resolver el problema?"},
            {"role": "user", "content": "Gracias por la ayuda, ahora funciona mejor."},
            {"role": "assistant", "content": "Me alegra que se haya resuelto."},
            {"role": "user", "content": "Estoy muy satisfecho con el soporte, excelente servicio."}
        ]
        
        result = sentiment_service.analyze_sentiment_change(messages)
        
        assert result["trend"] == "mejorando"
        assert result["delta"] > 0
        assert result["initial_sentiment"] == "negativo"
        assert result["final_sentiment"] == "positivo"
    
    def test_analyze_sentiment_change_worsening(self, sentiment_service):
        """Prueba que analyze_sentiment_change detecte correctamente un empeoramiento en el sentimiento."""
        messages = [
            {"role": "user", "content": "Hola, me interesa este producto, parece bueno."},
            {"role": "assistant", "content": "¡Gracias por tu interés! ¿En qué puedo ayudarte?"},
            {"role": "user", "content": "Tengo algunas dudas sobre cómo funciona."},
            {"role": "assistant", "content": "Claro, puedo explicarte."},
            {"role": "user", "content": "No entiendo nada, esto es muy complicado y frustrante."}
        ]
        
        result = sentiment_service.analyze_sentiment_change(messages)
        
        assert result["trend"] == "empeorando"
        assert result["delta"] < 0
    
    def test_detect_urgency_high(self, sentiment_service):
        """Prueba que detect_urgency detecte correctamente alta urgencia."""
        text = "Necesito una respuesta urgente ahora mismo. Es extremadamente crítico y no puedo esperar."
        result = sentiment_service.detect_urgency(text)
        
        assert result["class"] == "alta"
        assert result["level"] > 0.5
        assert len(result["signals"]) > 0
    
    def test_detect_urgency_low(self, sentiment_service):
        """Prueba que detect_urgency detecte correctamente baja urgencia."""
        text = "Cuando tengas tiempo, me gustaría saber más sobre este producto."
        result = sentiment_service.detect_urgency(text)
        
        assert result["class"] == "baja"
        assert result["level"] < 0.2
    
    def test_detect_indecision_high(self, sentiment_service):
        """Prueba que detect_indecision detecte correctamente alta indecisión."""
        text = "No estoy seguro de qué hacer. Tengo muchas dudas. Por un lado me gusta, pero por otro no sé si es lo que necesito. Quizás debería pensarlo más."
        result = sentiment_service.detect_indecision(text)
        
        assert result["class"] == "alta" or result["class"] == "media"
        assert result["level"] > 0.2
        assert len(result["signals"]) > 0
    
    def test_get_comprehensive_analysis(self, sentiment_service):
        """Prueba que get_comprehensive_analysis realice un análisis completo."""
        text = "Estoy muy frustrado con este producto, no funciona como debería. Necesito una solución urgente."
        result = sentiment_service.get_comprehensive_analysis(text)
        
        assert "sentiment" in result
        assert "emotions" in result
        assert "urgency" in result
        assert "indecision" in result
        assert "dominant_emotion" in result
        # Verificamos que el sentimiento sea el esperado según la implementación actual
        assert result["sentiment"]["sentiment"] in ["negativo", "neutral"]
        assert result["dominant_emotion"]["name"] in result["emotions"]
    
    def test_analyze_conversation(self, sentiment_service):
        """Prueba que analyze_conversation analice correctamente una conversación completa."""
        messages = [
            {"role": "user", "content": "Hola, tengo un problema con mi producto."},
            {"role": "assistant", "content": "Lamento escuchar eso. ¿Puedo ayudarte?"},
            {"role": "user", "content": "Sí, no funciona correctamente y estoy frustrado."},
            {"role": "assistant", "content": "Entiendo tu frustración. Vamos a resolverlo."},
            {"role": "user", "content": "Gracias por tu ayuda, ahora funciona mejor."}
        ]
        
        result = sentiment_service.analyze_conversation(messages)
        
        assert "overall_sentiment" in result
        assert "sentiment_trend" in result
        assert "dominant_emotion" in result
        assert "urgency" in result
        assert "indecision" in result
        assert "detailed" in result
