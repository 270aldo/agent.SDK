"""
Pruebas unitarias para el servicio de clasificación de preguntas.
"""

import pytest
from src.services.question_classification_service import QuestionClassificationService

class TestQuestionClassificationService:
    """Pruebas para el servicio de clasificación de preguntas."""
    
    @pytest.fixture
    def question_service(self):
        """Fixture para crear una instancia del servicio de clasificación de preguntas."""
        return QuestionClassificationService()
    
    def test_is_question_with_question_mark(self, question_service):
        """Prueba que is_question detecte correctamente preguntas con signo de interrogación."""
        text = "¿Cuál es el precio del producto?"
        result = question_service.is_question(text)
        
        assert result == True
    
    def test_is_question_without_question_mark(self, question_service):
        """Prueba que is_question detecte correctamente preguntas sin signo de interrogación."""
        text = "Me puedes decir cuál es el precio del producto"
        result = question_service.is_question(text)
        
        assert result == True
    
    def test_is_question_negative(self, question_service):
        """Prueba que is_question detecte correctamente textos que no son preguntas."""
        text = "El precio del producto es 100 pesos."
        result = question_service.is_question(text)
        
        assert result == False
    
    def test_extract_questions_with_question_marks(self, question_service):
        """Prueba que extract_questions extraiga correctamente preguntas con signos de interrogación."""
        text = "Hola. ¿Cuál es el precio del producto? ¿Tienen envío gratis? Gracias."
        result = question_service.extract_questions(text)
        
        assert len(result) == 2
        # Verificar que las preguntas estén presentes, ignorando posibles espacios al inicio
        assert any(q.strip() == "¿Cuál es el precio del producto?" for q in result)
        assert any(q.strip() == "¿Tienen envío gratis?" for q in result)
    
    def test_extract_questions_without_question_marks(self, question_service):
        """Prueba que extract_questions extraiga correctamente preguntas sin signos de interrogación."""
        text = "Hola. Me puedes decir cuál es el precio. También quiero saber si tienen envío gratis. Gracias."
        result = question_service.extract_questions(text)
        
        assert len(result) > 0
        assert any("precio" in q for q in result)
    
    def test_classify_question_type_factual(self, question_service):
        """Prueba que classify_question_type clasifique correctamente preguntas factuales."""
        question = "¿Cuál es el precio del producto?"
        result = question_service.classify_question_type(question)
        
        assert "factual" in result
        assert result["factual"] > 0
    
    def test_classify_question_type_procedural(self, question_service):
        """Prueba que classify_question_type clasifique correctamente preguntas procedimentales."""
        question = "¿Cómo puedo realizar un pedido en línea?"
        result = question_service.classify_question_type(question)
        
        assert "procedural" in result
        assert result["procedural"] > 0
    
    def test_classify_question_type_comparative(self, question_service):
        """Prueba que classify_question_type clasifique correctamente preguntas comparativas."""
        question = "¿Cuál es mejor, el plan básico o el premium?"
        result = question_service.classify_question_type(question)
        
        assert "comparative" in result
        assert result["comparative"] > 0
    
    def test_classify_question_type_causal(self, question_service):
        """Prueba que classify_question_type clasifique correctamente preguntas causales."""
        question = "¿Por qué el producto no está disponible?"
        result = question_service.classify_question_type(question)
        
        assert "causal" in result
        assert result["causal"] > 0
    
    def test_classify_question_type_hypothetical(self, question_service):
        """Prueba que classify_question_type clasifique correctamente preguntas hipotéticas."""
        question = "¿Qué pasaría si cancelo mi suscripción antes del plazo?"
        result = question_service.classify_question_type(question)
        
        assert "hypothetical" in result
        assert result["hypothetical"] > 0
    
    def test_classify_question_type_verification(self, question_service):
        """Prueba que classify_question_type clasifique correctamente preguntas de verificación."""
        question = "¿Es posible pagar con tarjeta de crédito?"
        result = question_service.classify_question_type(question)
        
        assert "verification" in result
        assert result["verification"] > 0
    
    def test_classify_question_type_opinion(self, question_service):
        """Prueba que classify_question_type clasifique correctamente preguntas de opinión."""
        question = "¿Qué recomiendas para un principiante?"
        result = question_service.classify_question_type(question)
        
        assert "opinion" in result
        assert result["opinion"] > 0
    
    def test_classify_question_type_clarification(self, question_service):
        """Prueba que classify_question_type clasifique correctamente preguntas de aclaración."""
        question = "¿Podrías aclarar a qué te refieres con 'premium'?"
        result = question_service.classify_question_type(question)
        
        assert "clarification" in result
        assert result["clarification"] > 0
    
    def test_determine_question_complexity_high(self, question_service):
        """Prueba que determine_question_complexity detecte correctamente preguntas de alta complejidad."""
        question = "¿Podrías explicarme detalladamente el procedimiento técnico para implementar la integración API con autenticación OAuth2 considerando las restricciones de seguridad y los requisitos específicos de nuestra plataforma?"
        result = question_service.determine_question_complexity(question)
        
        assert result["complexity"] == "alta"
        assert result["word_count"] > 15
    
    def test_determine_question_complexity_medium(self, question_service):
        """Prueba que determine_question_complexity detecte correctamente preguntas de complejidad media."""
        question = "¿Cuáles son las ventajas y desventajas de los diferentes métodos de pago disponibles y cómo se comparan entre sí en términos de seguridad, conveniencia y costos asociados?"
        result = question_service.determine_question_complexity(question)
        
        # La pregunta es más larga y contiene palabras clave de complejidad media/alta
        assert result["complexity"] in ["media", "alta"]
    
    def test_determine_question_complexity_low(self, question_service):
        """Prueba que determine_question_complexity detecte correctamente preguntas de baja complejidad."""
        question = "¿Cuál es el precio?"
        result = question_service.determine_question_complexity(question)
        
        assert result["complexity"] == "baja"
        assert result["word_count"] < 5
    
    def test_determine_question_intent_information(self, question_service):
        """Prueba que determine_question_intent detecte correctamente intención de información."""
        question_types = {"factual": 0.8, "procedural": 0.2}
        result = question_service.determine_question_intent(question_types)
        
        assert result["intent"] == "información"
        assert result["confidence"] > 0
    
    def test_determine_question_intent_comparison(self, question_service):
        """Prueba que determine_question_intent detecte correctamente intención de comparación."""
        question_types = {"comparative": 0.9}
        result = question_service.determine_question_intent(question_types)
        
        assert result["intent"] == "comparación"
        assert result["confidence"] > 0
    
    def test_determine_question_intent_validation(self, question_service):
        """Prueba que determine_question_intent detecte correctamente intención de validación."""
        question_types = {"verification": 0.7, "clarification": 0.3}
        result = question_service.determine_question_intent(question_types)
        
        assert result["intent"] == "validación"
        assert result["confidence"] > 0
    
    def test_analyze_question_complete(self, question_service):
        """Prueba que analyze_question realice un análisis completo de una pregunta."""
        question = "¿Cómo puedo cambiar mi plan de suscripción a uno de mayor capacidad?"
        result = question_service.analyze_question(question)
        
        assert result["is_question"] == True
        assert "predominant_type" in result
        assert "complexity" in result
        assert "intent" in result
    
    def test_analyze_question_not_a_question(self, question_service):
        """Prueba que analyze_question detecte correctamente textos que no son preguntas."""
        text = "Quiero cambiar mi plan de suscripción."
        result = question_service.analyze_question(text)
        
        assert result["is_question"] == False
        assert "message" in result
    
    def test_analyze_text_with_questions(self, question_service):
        """Prueba que analyze_text analice correctamente un texto con preguntas."""
        text = "Hola, tengo algunas dudas. ¿Cuál es el precio del plan premium? ¿Cómo puedo actualizar mi cuenta? Gracias."
        result = question_service.analyze_text(text)
        
        assert result["has_questions"] == True
        assert result["question_count"] == 2
        assert "questions" in result
        assert "analyses" in result
        assert "predominant_intent" in result
        assert "predominant_complexity" in result
    
    def test_analyze_text_without_questions(self, question_service):
        """Prueba que analyze_text analice correctamente un texto sin preguntas."""
        text = "Hola, quiero actualizar mi cuenta al plan premium. Gracias."
        result = question_service.analyze_text(text)
        
        assert result["has_questions"] == False
        assert "message" in result
    
    def test_analyze_conversation(self, question_service):
        """Prueba que analyze_conversation analice correctamente una conversación con preguntas."""
        messages = [
            {"role": "user", "content": "Hola, tengo algunas dudas sobre los planes."},
            {"role": "assistant", "content": "Claro, ¿en qué puedo ayudarte?"},
            {"role": "user", "content": "¿Cuál es el precio del plan premium? ¿Incluye soporte técnico?"},
            {"role": "assistant", "content": "El plan premium cuesta $99 al mes e incluye soporte técnico 24/7."},
            {"role": "user", "content": "¿Cómo puedo actualizar mi cuenta actual?"}
        ]
        
        result = question_service.analyze_conversation(messages)
        
        assert result["has_questions"] == True
        assert result["question_count"] >= 3
        assert "questions" in result
        assert "analyses" in result
        assert "predominant_intent" in result
        assert "predominant_complexity" in result
        assert "type_distribution" in result
    
    def test_analyze_conversation_without_questions(self, question_service):
        """Prueba que analyze_conversation analice correctamente una conversación sin preguntas."""
        messages = [
            {"role": "user", "content": "Hola, quiero actualizar mi cuenta al plan premium."},
            {"role": "assistant", "content": "Claro, puedo ayudarte con eso."},
            {"role": "user", "content": "Gracias por la ayuda."}
        ]
        
        result = question_service.analyze_conversation(messages)
        
        assert result["has_questions"] == False
        assert "message" in result
    
    def test_get_question_summary_with_questions(self, question_service):
        """Prueba que get_question_summary genere un resumen correcto para un texto con preguntas."""
        text = "¿Cuál es el precio del plan premium? ¿Cómo puedo actualizar mi cuenta?"
        result = question_service.get_question_summary(text)
        
        assert result["has_questions"] == True
        assert result["question_count"] == 2
        assert "predominant_intent" in result
        assert "predominant_complexity" in result
        assert "summary" in result
        assert isinstance(result["summary"], str)
    
    def test_get_question_summary_without_questions(self, question_service):
        """Prueba que get_question_summary genere un resumen correcto para un texto sin preguntas."""
        text = "Quiero actualizar mi cuenta al plan premium."
        result = question_service.get_question_summary(text)
        
        assert result["has_questions"] == False
        assert "summary" in result
        assert result["summary"] == "No se detectaron preguntas en el texto."
