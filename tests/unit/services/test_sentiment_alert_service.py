"""
Pruebas unitarias para el servicio de alertas de sentimiento.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from src.services.sentiment_alert_service import SentimentAlertService

class TestSentimentAlertService:
    """Pruebas para el servicio de alertas de sentimiento."""
    
    @pytest.fixture
    def alert_service(self):
        """Fixture para crear una instancia del servicio de alertas de sentimiento."""
        return SentimentAlertService()
    
    def test_monitor_conversation_insufficient_messages(self, alert_service):
        """Prueba que monitor_conversation maneje correctamente conversaciones con mensajes insuficientes."""
        messages = [
            {"role": "user", "content": "Hola, ¿cómo estás?"}
        ]
        
        result = alert_service.monitor_conversation("conv123", messages)
        
        assert result["has_alerts"] == False
        assert "No hay suficientes mensajes" in result["message"]
    
    def test_monitor_conversation_insufficient_user_messages(self, alert_service):
        """Prueba que monitor_conversation maneje correctamente conversaciones con mensajes de usuario insuficientes."""
        messages = [
            {"role": "user", "content": "Hola, ¿cómo estás?"},
            {"role": "assistant", "content": "Hola, estoy bien. ¿En qué puedo ayudarte?"}
        ]
        
        result = alert_service.monitor_conversation("conv123", messages)
        
        assert result["has_alerts"] == False
        assert "No hay suficientes mensajes del usuario" in result["message"]
    
    def test_monitor_conversation_no_alerts(self, alert_service):
        """Prueba que monitor_conversation no genere alertas cuando no hay problemas."""
        # Mock de los servicios
        alert_service.sentiment_service.analyze_sentiment = MagicMock(
            side_effect=[
                {"score": 0.5},  # Positivo
                {"score": 0.6}   # Más positivo
            ]
        )
        
        alert_service.sentiment_service.detect_emotions = MagicMock(
            side_effect=[
                {"emotions": [{"name": "alegría", "score": 0.8}]},
                {"emotions": [{"name": "alegría", "score": 0.9}]}
            ]
        )
        
        alert_service.sentiment_service.analyze_sentiment_changes = MagicMock(
            return_value={"trend": "mejorando", "magnitude": 0.1}
        )
        
        alert_service.sentiment_service.detect_urgency = MagicMock(
            return_value={"urgency_level": "baja", "score": 0.2}
        )
        
        alert_service.nlp_service.get_conversation_insights = MagicMock(
            return_value={
                "has_insights": True,
                "conversation_status": {
                    "satisfaction": "satisfecho",
                    "conversation_phase": "exploración"
                }
            }
        )
        
        messages = [
            {"role": "user", "content": "Hola, me gustaría información sobre el producto."},
            {"role": "assistant", "content": "Claro, ¿qué te gustaría saber?"},
            {"role": "user", "content": "Me interesa conocer las características y el precio."}
        ]
        
        result = alert_service.monitor_conversation("conv123", messages)
        
        assert result["has_alerts"] == False
        assert "alerts" in result
        assert len(result["alerts"]) == 0
    
    def test_monitor_conversation_negative_sentiment_alert(self, alert_service):
        """Prueba que monitor_conversation genere alertas cuando hay sentimiento negativo persistente."""
        # Mock de los servicios
        alert_service.sentiment_service.analyze_sentiment = MagicMock(
            side_effect=[
                {"score": -0.7},  # Negativo
                {"score": -0.8},  # Más negativo
                {"score": -0.9}   # Aún más negativo
            ]
        )
        
        alert_service.sentiment_service.detect_emotions = MagicMock(
            side_effect=[
                {"emotions": [{"name": "decepción", "score": 0.7}]},
                {"emotions": [{"name": "decepción", "score": 0.8}]},
                {"emotions": [{"name": "frustración", "score": 0.6}]}  # No llega al umbral
            ]
        )
        
        alert_service.sentiment_service.analyze_sentiment_changes = MagicMock(
            return_value={"trend": "empeorando", "magnitude": 0.2}  # No llega al umbral
        )
        
        alert_service.sentiment_service.detect_urgency = MagicMock(
            return_value={"urgency_level": "media", "score": 0.5}
        )
        
        alert_service.nlp_service.get_conversation_insights = MagicMock(
            return_value={
                "has_insights": True,
                "conversation_status": {
                    "satisfaction": "neutral",
                    "conversation_phase": "exploración"
                }
            }
        )
        
        messages = [
            {"role": "user", "content": "Hola, tengo un problema con el producto."},
            {"role": "assistant", "content": "Lamento escuchar eso. ¿Puedes darme más detalles?"},
            {"role": "user", "content": "El producto no funciona como esperaba."},
            {"role": "assistant", "content": "Entiendo tu frustración. ¿Qué problema específico estás experimentando?"},
            {"role": "user", "content": "He intentado varias soluciones pero nada funciona."}
        ]
        
        result = alert_service.monitor_conversation("conv123", messages)
        
        assert result["has_alerts"] == True
        assert "alerts" in result
        assert len(result["alerts"]) > 0
        assert any(alert["type"] == "negative_sentiment_persistent" for alert in result["alerts"])
    
    def test_monitor_conversation_frustration_alert(self, alert_service):
        """Prueba que monitor_conversation genere alertas cuando hay frustración."""
        # Mock de los servicios
        alert_service.sentiment_service.analyze_sentiment = MagicMock(
            side_effect=[
                {"score": -0.3},  # Ligeramente negativo
                {"score": -0.5}   # Más negativo
            ]
        )
        
        alert_service.sentiment_service.detect_emotions = MagicMock(
            side_effect=[
                {"emotions": [{"name": "decepción", "score": 0.5}]},
                {"emotions": [{"name": "frustración", "score": 0.8}]}  # Supera el umbral
            ]
        )
        
        alert_service.sentiment_service.analyze_sentiment_changes = MagicMock(
            return_value={"trend": "empeorando", "magnitude": 0.2}  # No llega al umbral
        )
        
        alert_service.sentiment_service.detect_urgency = MagicMock(
            return_value={"urgency_level": "media", "score": 0.5}
        )
        
        alert_service.nlp_service.get_conversation_insights = MagicMock(
            return_value={
                "has_insights": True,
                "conversation_status": {
                    "satisfaction": "neutral",
                    "conversation_phase": "exploración"
                }
            }
        )
        
        messages = [
            {"role": "user", "content": "Hola, tengo una pregunta sobre el producto."},
            {"role": "assistant", "content": "Claro, ¿en qué puedo ayudarte?"},
            {"role": "user", "content": "¡Esto es muy frustrante! No puedo hacer que funcione."}
        ]
        
        result = alert_service.monitor_conversation("conv123", messages)
        
        assert result["has_alerts"] == True
        assert "alerts" in result
        assert len(result["alerts"]) > 0
        assert any(alert["type"] == "frustration_detected" for alert in result["alerts"])
    
    def test_monitor_conversation_sentiment_drop_alert(self, alert_service):
        """Prueba que monitor_conversation genere alertas cuando hay una caída significativa de sentimiento."""
        # Mock de los servicios
        alert_service.sentiment_service.analyze_sentiment = MagicMock(
            side_effect=[
                {"score": 0.5},   # Positivo
                {"score": -0.3}   # Negativo
            ]
        )
        
        alert_service.sentiment_service.detect_emotions = MagicMock(
            side_effect=[
                {"emotions": [{"name": "alegría", "score": 0.7}]},
                {"emotions": [{"name": "decepción", "score": 0.6}]}
            ]
        )
        
        alert_service.sentiment_service.analyze_sentiment_changes = MagicMock(
            return_value={"trend": "empeorando", "magnitude": 0.8}  # Supera el umbral
        )
        
        alert_service.sentiment_service.detect_urgency = MagicMock(
            return_value={"urgency_level": "baja", "score": 0.3}
        )
        
        alert_service.nlp_service.get_conversation_insights = MagicMock(
            return_value={
                "has_insights": True,
                "conversation_status": {
                    "satisfaction": "neutral",
                    "conversation_phase": "exploración"
                }
            }
        )
        
        messages = [
            {"role": "user", "content": "Hola, estoy interesado en el producto."},
            {"role": "assistant", "content": "¡Genial! ¿Qué te gustaría saber?"},
            {"role": "user", "content": "Acabo de ver las reseñas y son bastante malas."}
        ]
        
        result = alert_service.monitor_conversation("conv123", messages)
        
        assert result["has_alerts"] == True
        assert "alerts" in result
        assert len(result["alerts"]) > 0
        assert any(alert["type"] == "sentiment_drop" for alert in result["alerts"])
    
    def test_monitor_conversation_high_urgency_alert(self, alert_service):
        """Prueba que monitor_conversation genere alertas cuando hay alta urgencia."""
        # Mock de los servicios
        alert_service.sentiment_service.analyze_sentiment = MagicMock(
            side_effect=[
                {"score": 0.2},   # Ligeramente positivo
                {"score": -0.2}   # Ligeramente negativo
            ]
        )
        
        alert_service.sentiment_service.detect_emotions = MagicMock(
            side_effect=[
                {"emotions": [{"name": "interés", "score": 0.7}]},
                {"emotions": [{"name": "preocupación", "score": 0.6}]}
            ]
        )
        
        alert_service.sentiment_service.analyze_sentiment_changes = MagicMock(
            return_value={"trend": "empeorando", "magnitude": 0.2}  # No llega al umbral
        )
        
        alert_service.sentiment_service.detect_urgency = MagicMock(
            return_value={"urgency_level": "alta", "score": 0.8}  # Supera el umbral
        )
        
        alert_service.nlp_service.get_conversation_insights = MagicMock(
            return_value={
                "has_insights": True,
                "conversation_status": {
                    "satisfaction": "neutral",
                    "conversation_phase": "exploración"
                }
            }
        )
        
        messages = [
            {"role": "user", "content": "Hola, tengo una pregunta sobre el producto."},
            {"role": "assistant", "content": "Claro, ¿en qué puedo ayudarte?"},
            {"role": "user", "content": "¡Necesito una solución urgente! Es muy importante."}
        ]
        
        result = alert_service.monitor_conversation("conv123", messages)
        
        assert result["has_alerts"] == True
        assert "alerts" in result
        assert len(result["alerts"]) > 0
        assert any(alert["type"] == "high_urgency" for alert in result["alerts"])
    
    def test_monitor_conversation_dissatisfaction_alert(self, alert_service):
        """Prueba que monitor_conversation genere alertas cuando hay insatisfacción según NLP."""
        # Mock de los servicios
        alert_service.sentiment_service.analyze_sentiment = MagicMock(
            side_effect=[
                {"score": -0.3},  # Ligeramente negativo
                {"score": -0.4}   # Ligeramente negativo
            ]
        )
        
        alert_service.sentiment_service.detect_emotions = MagicMock(
            side_effect=[
                {"emotions": [{"name": "decepción", "score": 0.5}]},
                {"emotions": [{"name": "decepción", "score": 0.6}]}
            ]
        )
        
        alert_service.sentiment_service.analyze_sentiment_changes = MagicMock(
            return_value={"trend": "estable", "magnitude": 0.1}
        )
        
        alert_service.sentiment_service.detect_urgency = MagicMock(
            return_value={"urgency_level": "media", "score": 0.5}
        )
        
        alert_service.nlp_service.get_conversation_insights = MagicMock(
            return_value={
                "has_insights": True,
                "conversation_status": {
                    "satisfaction": "insatisfecho",  # Insatisfacción
                    "conversation_phase": "insatisfacción"  # Fase de insatisfacción
                }
            }
        )
        
        messages = [
            {"role": "user", "content": "Hola, tengo un problema con el producto."},
            {"role": "assistant", "content": "Lamento escuchar eso. ¿Puedes darme más detalles?"},
            {"role": "user", "content": "No estoy contento con el servicio recibido."}
        ]
        
        result = alert_service.monitor_conversation("conv123", messages)
        
        assert result["has_alerts"] == True
        assert "alerts" in result
        assert len(result["alerts"]) > 0
        assert any(alert["type"] == "customer_dissatisfaction" for alert in result["alerts"])
        assert any(alert["type"] == "dissatisfaction_phase" for alert in result["alerts"])
    
    def test_get_alerts_specific_conversation(self, alert_service):
        """Prueba que get_alerts obtenga correctamente las alertas para una conversación específica."""
        # Crear una alerta de ejemplo
        alert = {
            "conversation_id": "conv123",
            "has_alerts": True,
            "alerts": [
                {
                    "type": "frustration_detected",
                    "severity": "alta",
                    "description": "Alta frustración detectada en el último mensaje.",
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }
        
        # Almacenar la alerta
        alert_service.alerts["conv123"] = alert
        
        # Obtener la alerta
        result = alert_service.get_alerts("conv123")
        
        assert result == alert
    
    def test_get_alerts_nonexistent_conversation(self, alert_service):
        """Prueba que get_alerts maneje correctamente conversaciones inexistentes."""
        result = alert_service.get_alerts("nonexistent_id")
        
        assert result["has_alerts"] == False
        assert "message" in result
    
    def test_get_all_alerts(self, alert_service):
        """Prueba que get_alerts obtenga correctamente todas las alertas."""
        # Crear alertas de ejemplo
        alert1 = {
            "conversation_id": "conv123",
            "has_alerts": True,
            "alerts": [
                {
                    "type": "frustration_detected",
                    "severity": "alta",
                    "description": "Alta frustración detectada en el último mensaje.",
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }
        
        alert2 = {
            "conversation_id": "conv456",
            "has_alerts": True,
            "alerts": [
                {
                    "type": "high_urgency",
                    "severity": "alta",
                    "description": "Alta urgencia detectada en el último mensaje.",
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }
        
        # Almacenar las alertas
        alert_service.alerts["conv123"] = alert1
        alert_service.alerts["conv456"] = alert2
        
        # Obtener todas las alertas
        result = alert_service.get_alerts()
        
        assert result["total_alerts"] == 2
        assert "alerts" in result
        assert "conv123" in result["alerts"]
        assert "conv456" in result["alerts"]
    
    def test_clear_alerts_specific_conversation(self, alert_service):
        """Prueba que clear_alerts limpie correctamente las alertas para una conversación específica."""
        # Crear alertas de ejemplo
        alert_service.alerts["conv123"] = {"has_alerts": True}
        alert_service.alerts["conv456"] = {"has_alerts": True}
        
        # Verificar que existan
        assert "conv123" in alert_service.alerts
        assert "conv456" in alert_service.alerts
        
        # Limpiar alertas para una conversación
        alert_service.clear_alerts("conv123")
        
        # Verificar que se haya eliminado solo la conversación especificada
        assert "conv123" not in alert_service.alerts
        assert "conv456" in alert_service.alerts
    
    def test_clear_all_alerts(self, alert_service):
        """Prueba que clear_alerts limpie correctamente todas las alertas."""
        # Crear alertas de ejemplo
        alert_service.alerts["conv123"] = {"has_alerts": True}
        alert_service.alerts["conv456"] = {"has_alerts": True}
        
        # Verificar que existan
        assert "conv123" in alert_service.alerts
        assert "conv456" in alert_service.alerts
        
        # Limpiar todas las alertas
        alert_service.clear_alerts()
        
        # Verificar que se hayan eliminado todas
        assert len(alert_service.alerts) == 0
    
    def test_generate_alert_recommendations(self, alert_service):
        """Prueba que _generate_alert_recommendations genere correctamente recomendaciones basadas en alertas."""
        alerts = [
            {
                "type": "negative_sentiment_persistent",
                "severity": "alta",
                "description": "Sentimiento negativo persistente en los últimos 3 mensajes.",
                "timestamp": datetime.now().isoformat()
            },
            {
                "type": "frustration_detected",
                "severity": "alta",
                "description": "Alta frustración detectada en el último mensaje.",
                "timestamp": datetime.now().isoformat()
            }
        ]
        
        nlp_insights = {
            "has_insights": True,
            "user_profile": {
                "communication_style": "formal",
                "technical_level": "medio"
            }
        }
        
        result = alert_service._generate_alert_recommendations(alerts, nlp_insights)
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert all("action" in rec for rec in result)
        assert all("description" in rec for rec in result)
        assert all("priority" in rec for rec in result)
        
        # Verificar recomendaciones específicas
        assert any(rec["action"] == "transferir_humano" for rec in result)
        assert any(rec["action"] == "simplificar_comunicación" for rec in result)
    
    def test_generate_alert_recommendations_with_user_profile(self, alert_service):
        """Prueba que _generate_alert_recommendations personalice recomendaciones según el perfil del usuario."""
        alerts = [
            {
                "type": "frustration_detected",
                "severity": "alta",
                "description": "Alta frustración detectada en el último mensaje.",
                "timestamp": datetime.now().isoformat()
            }
        ]
        
        nlp_insights = {
            "has_insights": True,
            "user_profile": {
                "communication_style": "directo",
                "technical_level": "alto"
            }
        }
        
        result = alert_service._generate_alert_recommendations(alerts, nlp_insights)
        
        assert isinstance(result, list)
        assert len(result) > 0
        
        # Verificar personalización
        for rec in result:
            if rec["action"] == "empatizar":
                assert "directo y conciso" in rec["description"]
            if rec["action"] == "simplificar_comunicación":
                assert "detalles técnicos precisos" in rec["description"]
