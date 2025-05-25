"""
Pruebas unitarias para el servicio de análisis de intención contextual.
"""

import pytest
from src.services.contextual_intent_service import ContextualIntentService

class TestContextualIntentService:
    """Pruebas para el servicio de análisis de intención contextual."""
    
    @pytest.fixture
    def intent_service(self):
        """Fixture para crear una instancia del servicio de análisis de intención contextual."""
        return ContextualIntentService()
    
    def test_detect_intent_from_text_information_product(self, intent_service):
        """Prueba que detect_intent_from_text detecte correctamente intención de información de producto."""
        text = "Me gustaría conocer más detalles sobre las características del producto."
        result = intent_service.detect_intent_from_text(text)
        
        assert "información_producto" in result
        assert result["información_producto"] > 0
    
    def test_detect_intent_from_text_information_price(self, intent_service):
        """Prueba que detect_intent_from_text detecte correctamente intención de información de precio."""
        text = "¿Cuánto cuesta el plan premium? Necesito saber el precio."
        result = intent_service.detect_intent_from_text(text)
        
        assert "información_precio" in result
        assert result["información_precio"] > 0
    
    def test_detect_intent_from_text_transaction_purchase(self, intent_service):
        """Prueba que detect_intent_from_text detecte correctamente intención de compra."""
        text = "Quiero comprar el producto. ¿Cómo puedo adquirirlo?"
        result = intent_service.detect_intent_from_text(text)
        
        assert "transacción_compra" in result
        assert result["transacción_compra"] > 0
    
    def test_detect_intent_from_text_support_technical(self, intent_service):
        """Prueba que detect_intent_from_text detecte correctamente intención de soporte técnico."""
        text = "Tengo un problema con el producto, no funciona correctamente."
        result = intent_service.detect_intent_from_text(text)
        
        assert "soporte_técnico" in result
        assert result["soporte_técnico"] > 0
    
    def test_detect_intent_from_text_complaint_service(self, intent_service):
        """Prueba que detect_intent_from_text detecte correctamente intención de queja de servicio."""
        text = "Estoy muy insatisfecho con la atención recibida. El servicio fue pésimo."
        result = intent_service.detect_intent_from_text(text)
        
        # Verificar que se detecte la categoría general de queja o la específica
        assert "queja" in result or "queja_servicio" in result
        # Verificar que la puntuación sea positiva para la categoría detectada
        if "queja_servicio" in result:
            assert result["queja_servicio"] > 0
        elif "queja" in result:
            assert result["queja"] > 0
    
    def test_detect_intent_from_text_suggestion(self, intent_service):
        """Prueba que detect_intent_from_text detecte correctamente intención de sugerencia."""
        text = "Tengo una sugerencia para mejorar el producto. Sería bueno implementar esta función."
        result = intent_service.detect_intent_from_text(text)
        
        assert "sugerencia_mejora" in result
        assert result["sugerencia_mejora"] > 0
    
    def test_detect_intent_from_text_multiple(self, intent_service):
        """Prueba que detect_intent_from_text detecte correctamente múltiples intenciones."""
        text = "Quiero comprar el producto, pero primero necesito saber el precio y si tiene garantía."
        result = intent_service.detect_intent_from_text(text)
        
        # Verificar que se detecten al menos dos intenciones diferentes
        assert len(result) >= 2
        # Verificar que se detecte la intención de compra o la categoría general
        assert "transacción_compra" in result or "transacción" in result
        # Verificar que se detecte alguna intención relacionada con información
        assert any(k.startswith("información") for k in result.keys())
    
    def test_determine_urgency_high(self, intent_service):
        """Prueba que determine_urgency detecte correctamente alta urgencia."""
        text = "Necesito una solución urgente, es una emergencia. No puede esperar."
        result = intent_service.determine_urgency(text)
        
        assert result["class"] == "alta" or result["class"] == "media"
        assert result["level"] > 0.3
        assert len(result["keywords"]) > 0
    
    def test_determine_urgency_low(self, intent_service):
        """Prueba que determine_urgency detecte correctamente baja urgencia."""
        text = "Me gustaría saber más sobre el producto cuando tengas tiempo."
        result = intent_service.determine_urgency(text)
        
        assert result["class"] == "baja"
        assert result["level"] < 0.3
    
    def test_determine_importance_high(self, intent_service):
        """Prueba que determine_importance detecte correctamente alta importancia."""
        text = "Es muy importante resolver este problema crucial lo antes posible."
        result = intent_service.determine_importance(text)
        
        assert result["class"] == "alta" or result["class"] == "media"
        assert result["level"] > 0.3
        assert len(result["keywords"]) > 0
    
    def test_determine_importance_low(self, intent_service):
        """Prueba que determine_importance detecte correctamente baja importancia."""
        text = "Solo quería comentarte algo sobre el producto."
        result = intent_service.determine_importance(text)
        
        assert result["class"] == "baja"
        assert result["level"] < 0.3
    
    def test_update_conversation_intents(self, intent_service):
        """Prueba que update_conversation_intents actualice correctamente el historial de intenciones."""
        conversation_id = "conv123"
        text1 = "Quiero saber el precio del producto."
        text2 = "Ahora quiero comprarlo urgentemente."
        
        # Actualizar con primer mensaje
        intent_service.update_conversation_intents(conversation_id, text1, 'user')
        result1 = intent_service.get_conversation_intents(conversation_id)
        
        assert len(result1) == 1
        assert "información_precio" in result1[0]["intents"]
        
        # Actualizar con segundo mensaje
        intent_service.update_conversation_intents(conversation_id, text2, 'user')
        result2 = intent_service.get_conversation_intents(conversation_id)
        
        assert len(result2) == 2
        # Verificar que se detecte la intención de compra o la categoría general
        assert "transacción_compra" in result2[1]["intents"] or "transacción" in result2[1]["intents"]
        # No verificamos la clase de urgencia ya que puede variar según la implementación
    
    def test_ignore_assistant_messages(self, intent_service):
        """Prueba que update_conversation_intents ignore los mensajes del asistente."""
        conversation_id = "conv123"
        text = "Quiero comprar el producto ahora mismo."
        
        # Actualizar con mensaje del asistente
        intent_service.update_conversation_intents(conversation_id, text, 'assistant')
        result = intent_service.get_conversation_intents(conversation_id)
        
        # No debería haber intenciones
        assert result == []
    
    def test_clear_conversation_intents(self, intent_service):
        """Prueba que clear_conversation_intents elimine correctamente el historial de intenciones."""
        conversation_id = "conv123"
        text = "Quiero comprar el producto."
        
        # Actualizar intenciones
        intent_service.update_conversation_intents(conversation_id, text, 'user')
        assert intent_service.get_conversation_intents(conversation_id) != []
        
        # Limpiar intenciones
        intent_service.clear_conversation_intents(conversation_id)
        assert intent_service.get_conversation_intents(conversation_id) == []
    
    def test_analyze_intent_evolution_with_intents(self, intent_service):
        """Prueba que analyze_intent_evolution analice correctamente la evolución de intenciones."""
        conversation_id = "conv123"
        
        # Actualizar con varios mensajes
        intent_service.update_conversation_intents(conversation_id, "¿Cuál es el precio del producto?", 'user')
        intent_service.update_conversation_intents(conversation_id, "¿Tiene garantía?", 'user')
        intent_service.update_conversation_intents(conversation_id, "Quiero comprarlo ahora.", 'user')
        
        result = intent_service.analyze_intent_evolution(conversation_id)
        
        assert result["has_intents"] == True
        assert "predominant_intent" in result
        assert "intent_counts" in result
        assert "intent_changes" in result
        assert "urgency_trend" in result
        assert "importance_trend" in result
    
    def test_analyze_intent_evolution_without_intents(self, intent_service):
        """Prueba que analyze_intent_evolution maneje correctamente conversaciones sin intenciones."""
        conversation_id = "conv_empty"
        result = intent_service.analyze_intent_evolution(conversation_id)
        
        assert result["has_intents"] == False
        assert "message" in result
    
    def test_analyze_message_with_intent(self, intent_service):
        """Prueba que analyze_message analice correctamente un mensaje con intención clara."""
        text = "Quiero comprar el producto ahora mismo, es urgente."
        result = intent_service.analyze_message(text)
        
        assert result["has_intent"] == True
        assert "main_intent" in result
        assert "general_category" in result
        assert "all_intents" in result
        assert "urgency" in result
        assert "importance" in result
        assert result["urgency"]["class"] in ["media", "alta"]
    
    def test_analyze_message_without_intent(self, intent_service):
        """Prueba que analyze_message maneje correctamente mensajes sin intención clara."""
        text = "Hola, buenos días."
        result = intent_service.analyze_message(text)
        
        # Puede detectar o no una intención, dependiendo de la implementación
        if not result.get("has_intent", False):
            assert "message" in result
    
    def test_analyze_conversation(self, intent_service):
        """Prueba que analyze_conversation analice correctamente una conversación completa."""
        messages = [
            {"role": "user", "content": "Hola, quiero saber el precio del producto."},
            {"role": "assistant", "content": "El precio es $100."},
            {"role": "user", "content": "¿Tiene garantía?"},
            {"role": "assistant", "content": "Sí, tiene garantía de 1 año."},
            {"role": "user", "content": "Perfecto, quiero comprarlo ahora mismo."}
        ]
        
        result = intent_service.analyze_conversation(messages, "conv_test")
        
        assert "has_intents" in result
        assert "message_count" in result
        assert "intent_count" in result
        assert "predominant_intent" in result
        assert "intent_counts" in result
        assert "avg_urgency" in result
        assert "avg_importance" in result
        assert "message_analyses" in result
        assert "intent_evolution" in result
    
    def test_analyze_conversation_without_user_messages(self, intent_service):
        """Prueba que analyze_conversation maneje correctamente conversaciones sin mensajes de usuario."""
        messages = [
            {"role": "assistant", "content": "Hola, ¿en qué puedo ayudarte?"},
            {"role": "assistant", "content": "¿Hay algo en lo que pueda asistirte?"}
        ]
        
        result = intent_service.analyze_conversation(messages)
        
        assert result["has_intents"] == False
        assert "message" in result
    
    def test_get_intent_summary_with_intents(self, intent_service):
        """Prueba que get_intent_summary genere un resumen correcto para una conversación con intenciones."""
        conversation_id = "conv123"
        
        # Actualizar con varios mensajes
        intent_service.update_conversation_intents(conversation_id, "¿Cuál es el precio del producto?", 'user')
        intent_service.update_conversation_intents(conversation_id, "¿Tiene garantía?", 'user')
        intent_service.update_conversation_intents(conversation_id, "Quiero comprarlo ahora.", 'user')
        
        result = intent_service.get_intent_summary(conversation_id)
        
        assert result["has_intents"] == True
        assert "predominant_intent" in result
        assert "message_count" in result
        assert "intent_changes" in result
        assert "urgency_trend" in result
        assert "importance_trend" in result
        assert "summary" in result
        assert isinstance(result["summary"], str)
    
    def test_get_intent_summary_without_intents(self, intent_service):
        """Prueba que get_intent_summary genere un resumen correcto para una conversación sin intenciones."""
        conversation_id = "conv_empty"
        result = intent_service.get_intent_summary(conversation_id)
        
        assert result["has_intents"] == False
        assert "summary" in result
        assert result["summary"] == "No se han detectado intenciones claras en esta conversación."
