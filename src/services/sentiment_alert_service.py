"""
Servicio de alertas de sentimiento para detectar cambios negativos en las conversaciones.
"""

import logging
from typing import Dict, Any, List, Optional
import json
from datetime import datetime

from src.services.advanced_sentiment_service import AdvancedSentimentService
from src.services.nlp_integration_service import NLPIntegrationService

# Configurar logging
logger = logging.getLogger(__name__)

class SentimentAlertService:
    """
    Servicio que monitorea cambios de sentimiento en las conversaciones y genera alertas
    cuando se detecta frustración o insatisfacción en los usuarios.
    """
    
    def __init__(self):
        """Inicializar el servicio de alertas de sentimiento."""
        logger.info("Servicio de alertas de sentimiento inicializado")
        
        # Inicializar servicios
        self.sentiment_service = AdvancedSentimentService()
        self.nlp_service = NLPIntegrationService()
        
        # Almacenamiento de alertas
        self.alerts = {}
        
        # Configuración de umbrales
        self.thresholds = {
            "negative_sentiment": 0.6,  # Umbral para sentimiento negativo
            "frustration": 0.7,         # Umbral para detección de frustración
            "urgency": 0.7,             # Umbral para urgencia alta
            "sentiment_drop": 0.3       # Umbral para caída de sentimiento
        }
    
    def monitor_conversation(self, conversation_id: str, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Monitorea una conversación para detectar cambios negativos de sentimiento.
        
        Args:
            conversation_id: ID de la conversación
            messages: Lista de mensajes de la conversación
            
        Returns:
            Dict: Resultado del monitoreo con alertas si se detectan
        """
        # Verificar si hay suficientes mensajes para analizar
        if len(messages) < 2:
            return {
                "conversation_id": conversation_id,
                "has_alerts": False,
                "message": "No hay suficientes mensajes para analizar cambios de sentimiento."
            }
        
        # Filtrar solo mensajes del usuario
        user_messages = [msg for msg in messages if msg.get("role") == "user"]
        
        if len(user_messages) < 2:
            return {
                "conversation_id": conversation_id,
                "has_alerts": False,
                "message": "No hay suficientes mensajes del usuario para analizar cambios de sentimiento."
            }
        
        # Analizar sentimiento de los mensajes del usuario
        sentiment_scores = []
        emotions = []
        
        for msg in user_messages:
            sentiment_analysis = self.sentiment_service.analyze_sentiment(msg.get("content", ""))
            sentiment_scores.append(sentiment_analysis.get("score", 0))
            
            emotion_analysis = self.sentiment_service.detect_emotions(msg.get("content", ""))
            emotions.append(emotion_analysis)
        
        # Analizar cambios de sentimiento
        sentiment_changes = self.sentiment_service.analyze_sentiment_changes(sentiment_scores)
        
        # Detectar urgencia en el último mensaje
        last_message = user_messages[-1].get("content", "")
        urgency_analysis = self.sentiment_service.detect_urgency(last_message)
        
        # Obtener insights de NLP para la conversación
        nlp_insights = self.nlp_service.get_conversation_insights(conversation_id)
        
        # Detectar alertas
        alerts = self._detect_alerts(
            conversation_id,
            sentiment_scores,
            emotions,
            sentiment_changes,
            urgency_analysis,
            nlp_insights
        )
        
        # Guardar alertas
        if alerts["has_alerts"]:
            self.alerts[conversation_id] = alerts
        
        return alerts
    
    def get_alerts(self, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtiene las alertas para una conversación específica o todas las alertas.
        
        Args:
            conversation_id: ID opcional de la conversación
            
        Returns:
            Dict: Alertas para la conversación o todas las alertas
        """
        if conversation_id:
            return self.alerts.get(conversation_id, {
                "conversation_id": conversation_id,
                "has_alerts": False,
                "message": "No hay alertas para esta conversación."
            })
        
        # Devolver todas las alertas
        return {
            "total_alerts": len(self.alerts),
            "alerts": self.alerts
        }
    
    def clear_alerts(self, conversation_id: Optional[str] = None):
        """
        Limpia las alertas para una conversación específica o todas las alertas.
        
        Args:
            conversation_id: ID opcional de la conversación
        """
        if conversation_id and conversation_id in self.alerts:
            del self.alerts[conversation_id]
        elif conversation_id is None:
            self.alerts = {}
    
    def _detect_alerts(self, conversation_id: str, 
                      sentiment_scores: List[float], 
                      emotions: List[Dict[str, Any]], 
                      sentiment_changes: Dict[str, Any], 
                      urgency_analysis: Dict[str, Any],
                      nlp_insights: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detecta alertas basadas en los análisis de sentimiento y NLP.
        
        Args:
            conversation_id: ID de la conversación
            sentiment_scores: Puntuaciones de sentimiento
            emotions: Análisis de emociones
            sentiment_changes: Análisis de cambios de sentimiento
            urgency_analysis: Análisis de urgencia
            nlp_insights: Insights de NLP
            
        Returns:
            Dict: Alertas detectadas
        """
        detected_alerts = []
        
        # Verificar sentimiento negativo persistente
        if len(sentiment_scores) >= 3:
            recent_scores = sentiment_scores[-3:]
            if all(score <= -self.thresholds["negative_sentiment"] for score in recent_scores):
                detected_alerts.append({
                    "type": "negative_sentiment_persistent",
                    "severity": "alta",
                    "description": "Sentimiento negativo persistente en los últimos 3 mensajes.",
                    "timestamp": datetime.now().isoformat()
                })
        
        # Verificar caída significativa de sentimiento
        if sentiment_changes.get("trend") == "empeorando" and sentiment_changes.get("magnitude", 0) >= self.thresholds["sentiment_drop"]:
            detected_alerts.append({
                "type": "sentiment_drop",
                "severity": "media",
                "description": f"Caída significativa de sentimiento de {sentiment_changes.get('magnitude', 0):.2f} puntos.",
                "timestamp": datetime.now().isoformat()
            })
        
        # Verificar frustración
        last_emotions = emotions[-1] if emotions else {}
        for emotion in last_emotions.get("emotions", []):
            if emotion.get("name") == "frustración" and emotion.get("score", 0) >= self.thresholds["frustration"]:
                detected_alerts.append({
                    "type": "frustration_detected",
                    "severity": "alta",
                    "description": "Alta frustración detectada en el último mensaje.",
                    "timestamp": datetime.now().isoformat()
                })
        
        # Verificar urgencia alta
        if urgency_analysis.get("urgency_level", "baja") == "alta" and urgency_analysis.get("score", 0) >= self.thresholds["urgency"]:
            detected_alerts.append({
                "type": "high_urgency",
                "severity": "alta",
                "description": "Alta urgencia detectada en el último mensaje.",
                "timestamp": datetime.now().isoformat()
            })
        
        # Verificar insights de NLP
        if nlp_insights.get("has_insights", False):
            conversation_status = nlp_insights.get("conversation_status", {})
            
            # Verificar insatisfacción
            if conversation_status.get("satisfaction") == "insatisfecho":
                detected_alerts.append({
                    "type": "customer_dissatisfaction",
                    "severity": "alta",
                    "description": "Cliente insatisfecho según análisis de NLP.",
                    "timestamp": datetime.now().isoformat()
                })
            
            # Verificar fase de insatisfacción
            if conversation_status.get("conversation_phase") == "insatisfacción":
                detected_alerts.append({
                    "type": "dissatisfaction_phase",
                    "severity": "alta",
                    "description": "Conversación en fase de insatisfacción.",
                    "timestamp": datetime.now().isoformat()
                })
        
        # Generar resultado
        result = {
            "conversation_id": conversation_id,
            "has_alerts": len(detected_alerts) > 0,
            "alerts": detected_alerts,
            "sentiment_analysis": {
                "scores": sentiment_scores,
                "changes": sentiment_changes,
                "last_emotions": last_emotions,
                "urgency": urgency_analysis
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # Agregar recomendaciones si hay alertas
        if result["has_alerts"]:
            result["recommendations"] = self._generate_alert_recommendations(detected_alerts, nlp_insights)
        
        return result
    
    def _generate_alert_recommendations(self, alerts: List[Dict[str, Any]], 
                                       nlp_insights: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Genera recomendaciones basadas en las alertas detectadas.
        
        Args:
            alerts: Alertas detectadas
            nlp_insights: Insights de NLP
            
        Returns:
            List: Lista de recomendaciones
        """
        recommendations = []
        
        # Verificar tipos de alertas
        alert_types = [alert["type"] for alert in alerts]
        
        # Recomendaciones para sentimiento negativo persistente
        if "negative_sentiment_persistent" in alert_types:
            recommendations.append({
                "action": "transferir_humano",
                "description": "Transferir la conversación a un agente humano para manejo especializado.",
                "priority": "alta"
            })
            recommendations.append({
                "action": "ofrecer_compensación",
                "description": "Ofrecer una compensación o beneficio adicional para mejorar la experiencia.",
                "priority": "media"
            })
        
        # Recomendaciones para caída de sentimiento
        if "sentiment_drop" in alert_types:
            recommendations.append({
                "action": "verificar_problema",
                "description": "Verificar si hay un problema específico que haya causado la caída de sentimiento.",
                "priority": "alta"
            })
            recommendations.append({
                "action": "empatizar",
                "description": "Mostrar empatía y comprensión hacia la situación del usuario.",
                "priority": "media"
            })
        
        # Recomendaciones para frustración
        if "frustration_detected" in alert_types:
            recommendations.append({
                "action": "simplificar_comunicación",
                "description": "Simplificar la comunicación y proporcionar respuestas directas.",
                "priority": "alta"
            })
            recommendations.append({
                "action": "ofrecer_alternativas",
                "description": "Ofrecer alternativas o soluciones diferentes al problema.",
                "priority": "media"
            })
        
        # Recomendaciones para urgencia alta
        if "high_urgency" in alert_types:
            recommendations.append({
                "action": "priorizar_atención",
                "description": "Priorizar la atención y respuesta rápida a las necesidades del usuario.",
                "priority": "alta"
            })
        
        # Recomendaciones para insatisfacción
        if "customer_dissatisfaction" in alert_types or "dissatisfaction_phase" in alert_types:
            recommendations.append({
                "action": "escalar_caso",
                "description": "Escalar el caso a un supervisor o equipo especializado.",
                "priority": "alta"
            })
            recommendations.append({
                "action": "seguimiento_posterior",
                "description": "Programar un seguimiento posterior para verificar la resolución del problema.",
                "priority": "media"
            })
        
        # Si hay insights de NLP, personalizar recomendaciones
        if nlp_insights.get("has_insights", False):
            user_profile = nlp_insights.get("user_profile", {})
            
            # Ajustar recomendaciones según el perfil del usuario
            communication_style = user_profile.get("communication_style", "formal")
            if communication_style == "directo":
                for rec in recommendations:
                    if rec["action"] == "empatizar":
                        rec["description"] = "Ser directo y conciso, centrándose en soluciones concretas."
            
            # Ajustar recomendaciones según nivel técnico
            technical_level = user_profile.get("technical_level", "medio")
            if technical_level == "alto":
                for rec in recommendations:
                    if rec["action"] == "simplificar_comunicación":
                        rec["description"] = "Proporcionar detalles técnicos precisos y soluciones avanzadas."
        
        return recommendations
