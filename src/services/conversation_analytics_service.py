"""
Servicio de análisis de conversaciones para generar estadísticas y métricas.
"""

import logging
from typing import Dict, Any, List, Optional
import json
from datetime import datetime, timedelta
import statistics

from src.services.nlp_integration_service import NLPIntegrationService
from src.services.sentiment_alert_service import SentimentAlertService
from src.services.recommendation_service import RecommendationService
from src.integrations.supabase import supabase_client

# Configurar logging
logger = logging.getLogger(__name__)

class ConversationAnalyticsService:
    """
    Servicio que recopila y procesa datos de conversaciones para generar
    estadísticas y métricas para el panel de análisis.
    """
    
    def __init__(self):
        """Inicializar el servicio de análisis de conversaciones."""
        logger.info("Servicio de análisis de conversaciones inicializado")
        
        # Inicializar servicios
        self.nlp_service = NLPIntegrationService()
        self.alert_service = SentimentAlertService()
        self.recommendation_service = RecommendationService()
        
        # Caché de análisis
        self.analytics_cache = {}
    
    async def get_conversation_analytics(self, conversation_id: str) -> Dict[str, Any]:
        """
        Obtiene análisis detallado para una conversación específica.
        
        Args:
            conversation_id: ID de la conversación
            
        Returns:
            Dict: Análisis detallado de la conversación
        """
        # Verificar si ya está en caché
        if conversation_id in self.analytics_cache:
            return self.analytics_cache[conversation_id]
        
        try:
            # Obtener datos de la conversación desde Supabase
            client = supabase_client.get_client()
            response = await client.table("conversations").select("*").eq("conversation_id", conversation_id).execute()
            
            if not response.data:
                return {
                    "conversation_id": conversation_id,
                    "has_analytics": False,
                    "message": "No se encontró la conversación."
                }
            
            conversation_data = response.data[0]
            
            # Obtener mensajes
            messages = conversation_data.get("messages", [])
            if isinstance(messages, str):
                messages = json.loads(messages)
            
            # Obtener insights de NLP
            nlp_insights = self.nlp_service.get_conversation_insights(conversation_id)
            
            # Obtener alertas de sentimiento
            sentiment_alerts = self.alert_service.get_alerts(conversation_id)
            
            # Obtener recomendaciones
            recommendations = self.recommendation_service.get_cached_recommendations(conversation_id)
            
            # Calcular métricas básicas
            total_messages = len(messages)
            user_messages = [msg for msg in messages if msg.get("role") == "user"]
            assistant_messages = [msg for msg in messages if msg.get("role") == "assistant"]
            
            user_message_count = len(user_messages)
            assistant_message_count = len(assistant_messages)
            
            # Calcular duración de la conversación
            start_time = None
            end_time = None
            
            if total_messages > 0:
                # Obtener timestamp del primer mensaje
                first_msg = messages[0]
                if isinstance(first_msg, dict) and "timestamp" in first_msg:
                    start_time = first_msg["timestamp"]
                
                # Obtener timestamp del último mensaje
                last_msg = messages[-1]
                if isinstance(last_msg, dict) and "timestamp" in last_msg:
                    end_time = last_msg["timestamp"]
            
            duration_seconds = None
            if start_time and end_time:
                if isinstance(start_time, str):
                    start_time = datetime.fromisoformat(start_time)
                if isinstance(end_time, str):
                    end_time = datetime.fromisoformat(end_time)
                
                duration = end_time - start_time
                duration_seconds = duration.total_seconds()
            
            # Calcular tiempo promedio de respuesta
            response_times = []
            for i in range(1, len(messages)):
                current_msg = messages[i]
                prev_msg = messages[i-1]
                
                if (current_msg.get("role") == "assistant" and prev_msg.get("role") == "user" and
                    "timestamp" in current_msg and "timestamp" in prev_msg):
                    
                    current_time = current_msg["timestamp"]
                    prev_time = prev_msg["timestamp"]
                    
                    if isinstance(current_time, str):
                        current_time = datetime.fromisoformat(current_time)
                    if isinstance(prev_time, str):
                        prev_time = datetime.fromisoformat(prev_time)
                    
                    response_time = (current_time - prev_time).total_seconds()
                    response_times.append(response_time)
            
            avg_response_time = None
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
            
            # Construir análisis completo
            analytics = {
                "conversation_id": conversation_id,
                "has_analytics": True,
                "basic_metrics": {
                    "total_messages": total_messages,
                    "user_messages": user_message_count,
                    "assistant_messages": assistant_message_count,
                    "duration_seconds": duration_seconds,
                    "avg_response_time": avg_response_time
                },
                "nlp_insights": nlp_insights,
                "sentiment_alerts": sentiment_alerts,
                "recommendations": recommendations,
                "session_insights": conversation_data.get("session_insights", {}),
                "timestamp": datetime.now().isoformat()
            }
            
            # Guardar en caché
            self.analytics_cache[conversation_id] = analytics
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error al obtener análisis de conversación {conversation_id}: {e}")
            return {
                "conversation_id": conversation_id,
                "has_analytics": False,
                "message": f"Error al obtener análisis: {str(e)}"
            }
    
    async def get_aggregate_analytics(self, days: int = 7) -> Dict[str, Any]:
        """
        Obtiene análisis agregado de todas las conversaciones en un período de tiempo.
        
        Args:
            days: Número de días para el análisis
            
        Returns:
            Dict: Análisis agregado de conversaciones
        """
        try:
            # Calcular fecha de inicio
            start_date = datetime.now() - timedelta(days=days)
            
            # Obtener conversaciones desde Supabase
            client = supabase_client.get_client()
            response = await client.table("conversations").select("*").gte("created_at", start_date.isoformat()).execute()
            
            if not response.data:
                return {
                    "has_analytics": False,
                    "message": f"No se encontraron conversaciones en los últimos {days} días."
                }
            
            conversations = response.data
            
            # Inicializar contadores y acumuladores
            total_conversations = len(conversations)
            total_messages = 0
            total_duration = 0
            durations = []
            sentiment_scores = []
            intents = {}
            entities = {}
            alerts_by_type = {}
            recommendations_by_type = {}
            
            # Procesar cada conversación
            for conv in conversations:
                # Contar mensajes
                messages = conv.get("messages", [])
                if isinstance(messages, str):
                    messages = json.loads(messages)
                
                total_messages += len(messages)
                
                # Calcular duración
                if conv.get("created_at") and conv.get("updated_at"):
                    start_time = conv["created_at"]
                    end_time = conv["updated_at"]
                    
                    if isinstance(start_time, str):
                        start_time = datetime.fromisoformat(start_time)
                    if isinstance(end_time, str):
                        end_time = datetime.fromisoformat(end_time)
                    
                    duration = (end_time - start_time).total_seconds()
                    total_duration += duration
                    durations.append(duration)
                
                # Procesar insights de sesión
                session_insights = conv.get("session_insights", {})
                
                # Extraer sentimiento
                if "intent_analysis" in session_insights:
                    sentiment_score = session_insights["intent_analysis"].get("sentiment_score")
                    if sentiment_score is not None:
                        sentiment_scores.append(sentiment_score)
                
                # Extraer intenciones
                if "nlp_analysis" in session_insights and "intent" in session_insights["nlp_analysis"]:
                    for intent, score in session_insights["nlp_analysis"]["intent"].items():
                        if score > 0.5:  # Solo contar intenciones relevantes
                            intents[intent] = intents.get(intent, 0) + 1
                
                # Extraer entidades
                if "nlp_analysis" in session_insights and "entities" in session_insights["nlp_analysis"]:
                    for entity_type, entity_list in session_insights["nlp_analysis"]["entities"].items():
                        if entity_type not in entities:
                            entities[entity_type] = []
                        entities[entity_type].extend(entity_list)
                
                # Procesar alertas
                conv_id = conv.get("conversation_id")
                if conv_id:
                    alerts = self.alert_service.get_alerts(conv_id)
                    if alerts.get("has_alerts", False):
                        for alert in alerts.get("alerts", []):
                            alert_type = alert.get("type")
                            if alert_type:
                                alerts_by_type[alert_type] = alerts_by_type.get(alert_type, 0) + 1
                
                # Procesar recomendaciones
                if conv_id:
                    recs = self.recommendation_service.get_cached_recommendations(conv_id)
                    if recs.get("has_recommendations", False):
                        # Contar recomendaciones de productos
                        for product in recs.get("products", []):
                            rec_type = "product"
                            recommendations_by_type[rec_type] = recommendations_by_type.get(rec_type, 0) + 1
                        
                        # Contar recomendaciones de contenido
                        for content in recs.get("content", []):
                            rec_type = f"content_{content.get('type', 'general')}"
                            recommendations_by_type[rec_type] = recommendations_by_type.get(rec_type, 0) + 1
                        
                        # Contar recomendaciones de acciones
                        for action in recs.get("next_actions", []):
                            rec_type = f"action_{action.get('action', 'general')}"
                            recommendations_by_type[rec_type] = recommendations_by_type.get(rec_type, 0) + 1
            
            # Calcular promedios y estadísticas
            avg_messages_per_conversation = total_messages / total_conversations if total_conversations > 0 else 0
            avg_duration = total_duration / total_conversations if total_conversations > 0 else 0
            
            # Calcular distribución de duración
            duration_stats = {
                "min": min(durations) if durations else None,
                "max": max(durations) if durations else None,
                "avg": avg_duration,
                "median": statistics.median(durations) if durations else None
            }
            
            # Calcular distribución de sentimiento
            sentiment_stats = {}
            if sentiment_scores:
                sentiment_stats = {
                    "min": min(sentiment_scores),
                    "max": max(sentiment_scores),
                    "avg": sum(sentiment_scores) / len(sentiment_scores),
                    "median": statistics.median(sentiment_scores)
                }
            
            # Obtener top intenciones
            top_intents = sorted(intents.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Obtener top entidades por tipo
            top_entities = {}
            for entity_type, entity_list in entities.items():
                # Contar frecuencia de cada entidad
                entity_counts = {}
                for entity in entity_list:
                    entity_counts[entity] = entity_counts.get(entity, 0) + 1
                
                # Obtener top 5 entidades más frecuentes
                top_entities[entity_type] = sorted(entity_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Construir análisis agregado
            aggregate_analytics = {
                "has_analytics": True,
                "time_period": {
                    "days": days,
                    "start_date": start_date.isoformat(),
                    "end_date": datetime.now().isoformat()
                },
                "conversation_metrics": {
                    "total_conversations": total_conversations,
                    "total_messages": total_messages,
                    "avg_messages_per_conversation": avg_messages_per_conversation,
                    "duration_stats": duration_stats
                },
                "sentiment_metrics": sentiment_stats,
                "intent_metrics": {
                    "top_intents": top_intents
                },
                "entity_metrics": {
                    "top_entities": top_entities
                },
                "alert_metrics": {
                    "total_alerts": sum(alerts_by_type.values()),
                    "alerts_by_type": alerts_by_type
                },
                "recommendation_metrics": {
                    "total_recommendations": sum(recommendations_by_type.values()),
                    "recommendations_by_type": recommendations_by_type
                },
                "timestamp": datetime.now().isoformat()
            }
            
            return aggregate_analytics
            
        except Exception as e:
            logger.error(f"Error al obtener análisis agregado: {e}")
            return {
                "has_analytics": False,
                "message": f"Error al obtener análisis agregado: {str(e)}"
            }
    
    async def get_sentiment_trend_analysis(self, days: int = 30) -> Dict[str, Any]:
        """
        Obtiene análisis de tendencias de sentimiento a lo largo del tiempo.
        
        Args:
            days: Número de días para el análisis
            
        Returns:
            Dict: Análisis de tendencias de sentimiento
        """
        try:
            # Calcular fecha de inicio
            start_date = datetime.now() - timedelta(days=days)
            
            # Obtener conversaciones desde Supabase
            client = supabase_client.get_client()
            response = await client.table("conversations").select("*").gte("created_at", start_date.isoformat()).execute()
            
            if not response.data:
                return {
                    "has_analytics": False,
                    "message": f"No se encontraron conversaciones en los últimos {days} días."
                }
            
            conversations = response.data
            
            # Agrupar conversaciones por día
            conversations_by_day = {}
            sentiment_by_day = {}
            alerts_by_day = {}
            
            for conv in conversations:
                # Obtener fecha
                created_at = conv.get("created_at")
                if not created_at:
                    continue
                
                if isinstance(created_at, str):
                    created_at = datetime.fromisoformat(created_at)
                
                day_key = created_at.strftime("%Y-%m-%d")
                
                # Inicializar contadores para el día
                if day_key not in conversations_by_day:
                    conversations_by_day[day_key] = 0
                    sentiment_by_day[day_key] = []
                    alerts_by_day[day_key] = 0
                
                # Incrementar contador de conversaciones
                conversations_by_day[day_key] += 1
                
                # Extraer sentimiento
                session_insights = conv.get("session_insights", {})
                if "intent_analysis" in session_insights:
                    sentiment_score = session_insights["intent_analysis"].get("sentiment_score")
                    if sentiment_score is not None:
                        sentiment_by_day[day_key].append(sentiment_score)
                
                # Contar alertas
                conv_id = conv.get("conversation_id")
                if conv_id:
                    alerts = self.alert_service.get_alerts(conv_id)
                    if alerts.get("has_alerts", False):
                        alerts_by_day[day_key] += len(alerts.get("alerts", []))
            
            # Calcular promedios de sentimiento por día
            avg_sentiment_by_day = {}
            for day, scores in sentiment_by_day.items():
                if scores:
                    avg_sentiment_by_day[day] = sum(scores) / len(scores)
                else:
                    avg_sentiment_by_day[day] = 0
            
            # Ordenar días cronológicamente
            sorted_days = sorted(conversations_by_day.keys())
            
            # Construir series temporales
            conversation_series = [{"date": day, "count": conversations_by_day[day]} for day in sorted_days]
            sentiment_series = [{"date": day, "score": avg_sentiment_by_day[day]} for day in sorted_days]
            alert_series = [{"date": day, "count": alerts_by_day[day]} for day in sorted_days]
            
            # Construir análisis de tendencias
            trend_analysis = {
                "has_analytics": True,
                "time_period": {
                    "days": days,
                    "start_date": start_date.isoformat(),
                    "end_date": datetime.now().isoformat()
                },
                "conversation_trend": conversation_series,
                "sentiment_trend": sentiment_series,
                "alert_trend": alert_series,
                "timestamp": datetime.now().isoformat()
            }
            
            return trend_analysis
            
        except Exception as e:
            logger.error(f"Error al obtener análisis de tendencias: {e}")
            return {
                "has_analytics": False,
                "message": f"Error al obtener análisis de tendencias: {str(e)}"
            }
    
    def clear_analytics_cache(self, conversation_id: Optional[str] = None):
        """
        Limpia la caché de análisis para una conversación específica o todas las conversaciones.
        
        Args:
            conversation_id: ID opcional de la conversación
        """
        if conversation_id and conversation_id in self.analytics_cache:
            del self.analytics_cache[conversation_id]
        elif conversation_id is None:
            self.analytics_cache = {}
