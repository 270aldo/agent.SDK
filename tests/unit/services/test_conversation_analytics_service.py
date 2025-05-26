"""
Pruebas unitarias para el servicio de análisis de conversaciones.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timedelta
import json

from src.services.conversation_analytics_service import ConversationAnalyticsService

class TestConversationAnalyticsService:
    """Pruebas para el servicio de análisis de conversaciones."""
    
    @pytest.fixture
    def analytics_service(self):
        """Fixture para crear una instancia del servicio de análisis de conversaciones."""
        return ConversationAnalyticsService()
    
    @pytest.mark.asyncio
    async def test_get_conversation_analytics_from_cache(self, analytics_service):
        """Prueba que get_conversation_analytics devuelva datos de caché si están disponibles."""
        # Preparar datos de caché
        cached_analytics = {
            "conversation_id": "conv123",
            "has_analytics": True,
            "basic_metrics": {
                "total_messages": 10
            }
        }
        
        # Almacenar en caché
        analytics_service.analytics_cache["conv123"] = cached_analytics
        
        # Obtener análisis
        result = await analytics_service.get_conversation_analytics("conv123")
        
        assert result == cached_analytics
    
    @pytest.mark.asyncio
    async def test_get_conversation_analytics_not_found(self, analytics_service):
        """Prueba que get_conversation_analytics maneje correctamente conversaciones no encontradas."""
        # Mock de Supabase
        mock_response = MagicMock()
        mock_response.data = []
        
        mock_execute = AsyncMock(return_value=mock_response)
        mock_eq = MagicMock()
        mock_eq.execute = mock_execute
        
        mock_select = MagicMock()
        mock_select.eq = MagicMock(return_value=mock_eq)
        
        mock_table = MagicMock()
        mock_table.select = MagicMock(return_value=mock_select)
        
        mock_client = MagicMock()
        mock_client.table = MagicMock(return_value=mock_table)
        
        with patch('src.services.conversation_analytics_service.supabase_client.get_client', return_value=mock_client):
            result = await analytics_service.get_conversation_analytics("nonexistent_id")
        
        assert result["has_analytics"] == False
        assert "No se encontró la conversación" in result["message"]
    
    @pytest.mark.asyncio
    async def test_get_conversation_analytics_success(self, analytics_service):
        """Prueba que get_conversation_analytics procese correctamente los datos de una conversación."""
        # Preparar datos de conversación
        conversation_data = {
            "conversation_id": "conv123",
            "messages": json.dumps([
                {"role": "user", "content": "Hola", "timestamp": datetime.now().isoformat()},
                {"role": "assistant", "content": "Hola, ¿en qué puedo ayudarte?", "timestamp": (datetime.now() + timedelta(seconds=2)).isoformat()},
                {"role": "user", "content": "Necesito información", "timestamp": (datetime.now() + timedelta(seconds=5)).isoformat()},
                {"role": "assistant", "content": "Claro, aquí tienes", "timestamp": (datetime.now() + timedelta(seconds=8)).isoformat()}
            ]),
            "session_insights": {
                "intent_analysis": {
                    "sentiment_score": 0.7
                }
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": (datetime.now() + timedelta(seconds=10)).isoformat()
        }
        
        # Mock de Supabase
        mock_response = MagicMock()
        mock_response.data = [conversation_data]
        
        mock_execute = AsyncMock(return_value=mock_response)
        mock_eq = MagicMock()
        mock_eq.execute = mock_execute
        
        mock_select = MagicMock()
        mock_select.eq = MagicMock(return_value=mock_eq)
        
        mock_table = MagicMock()
        mock_table.select = MagicMock(return_value=mock_select)
        
        mock_client = MagicMock()
        mock_client.table = MagicMock(return_value=mock_table)
        
        # Mock de servicios
        analytics_service.nlp_service.get_conversation_insights = MagicMock(
            return_value={"has_insights": True, "user_profile": {"personal_info": {"name": "Juan"}}}
        )
        
        analytics_service.alert_service.get_alerts = MagicMock(
            return_value={"has_alerts": False}
        )
        
        analytics_service.recommendation_service.get_cached_recommendations = MagicMock(
            return_value={"has_recommendations": False}
        )
        
        with patch('src.services.conversation_analytics_service.supabase_client.get_client', return_value=mock_client):
            result = await analytics_service.get_conversation_analytics("conv123")
        
        assert result["has_analytics"] == True
        assert result["conversation_id"] == "conv123"
        assert "basic_metrics" in result
        assert result["basic_metrics"]["total_messages"] == 4
        assert result["basic_metrics"]["user_messages"] == 2
        assert result["basic_metrics"]["assistant_messages"] == 2
        assert result["basic_metrics"]["duration_seconds"] is not None
        assert result["basic_metrics"]["avg_response_time"] is not None
        
        # Verificar que se guarde en caché
        assert "conv123" in analytics_service.analytics_cache
    
    @pytest.mark.asyncio
    async def test_get_conversation_analytics_error(self, analytics_service):
        """Prueba que get_conversation_analytics maneje correctamente los errores."""
        # Mock de Supabase para lanzar una excepción
        with patch('src.services.conversation_analytics_service.supabase_client.get_client', side_effect=Exception("Error de prueba")):
            result = await analytics_service.get_conversation_analytics("conv123")
        
        assert result["has_analytics"] == False
        assert "Error al obtener análisis" in result["message"]
    
    @pytest.mark.asyncio
    async def test_get_aggregate_analytics_no_conversations(self, analytics_service):
        """Prueba que get_aggregate_analytics maneje correctamente el caso sin conversaciones."""
        # Mock de Supabase
        mock_response = MagicMock()
        mock_response.data = []
        
        mock_execute = AsyncMock(return_value=mock_response)
        mock_gte = MagicMock()
        mock_gte.execute = mock_execute
        
        mock_select = MagicMock()
        mock_select.gte = MagicMock(return_value=mock_gte)
        
        mock_table = MagicMock()
        mock_table.select = MagicMock(return_value=mock_select)
        
        mock_client = MagicMock()
        mock_client.table = MagicMock(return_value=mock_table)
        
        with patch('src.services.conversation_analytics_service.supabase_client.get_client', return_value=mock_client):
            result = await analytics_service.get_aggregate_analytics(days=7)
        
        assert result["has_analytics"] == False
        assert "No se encontraron conversaciones" in result["message"]
    
    @pytest.mark.asyncio
    async def test_get_aggregate_analytics_success(self, analytics_service):
        """Prueba que get_aggregate_analytics procese correctamente los datos de múltiples conversaciones."""
        # Preparar datos de conversaciones
        conversations = [
            {
                "conversation_id": "conv1",
                "messages": json.dumps([
                    {"role": "user", "content": "Hola", "timestamp": datetime.now().isoformat()},
                    {"role": "assistant", "content": "Hola, ¿en qué puedo ayudarte?", "timestamp": (datetime.now() + timedelta(seconds=2)).isoformat()}
                ]),
                "session_insights": {
                    "intent_analysis": {"sentiment_score": 0.7},
                    "nlp_analysis": {
                        "intent": {"información_producto": 0.8},
                        "entities": {"producto": ["ProductoA"]}
                    }
                },
                "created_at": datetime.now().isoformat(),
                "updated_at": (datetime.now() + timedelta(seconds=5)).isoformat()
            },
            {
                "conversation_id": "conv2",
                "messages": json.dumps([
                    {"role": "user", "content": "Tengo un problema", "timestamp": datetime.now().isoformat()},
                    {"role": "assistant", "content": "¿Qué problema tienes?", "timestamp": (datetime.now() + timedelta(seconds=2)).isoformat()},
                    {"role": "user", "content": "No funciona", "timestamp": (datetime.now() + timedelta(seconds=5)).isoformat()}
                ]),
                "session_insights": {
                    "intent_analysis": {"sentiment_score": -0.3},
                    "nlp_analysis": {
                        "intent": {"soporte_técnico": 0.9},
                        "entities": {"producto": ["ProductoB"]}
                    }
                },
                "created_at": datetime.now().isoformat(),
                "updated_at": (datetime.now() + timedelta(seconds=8)).isoformat()
            }
        ]
        
        # Mock de Supabase
        mock_response = MagicMock()
        mock_response.data = conversations
        
        mock_execute = AsyncMock(return_value=mock_response)
        mock_gte = MagicMock()
        mock_gte.execute = mock_execute
        
        mock_select = MagicMock()
        mock_select.gte = MagicMock(return_value=mock_gte)
        
        mock_table = MagicMock()
        mock_table.select = MagicMock(return_value=mock_select)
        
        mock_client = MagicMock()
        mock_client.table = MagicMock(return_value=mock_table)
        
        # Mock de servicios
        analytics_service.alert_service.get_alerts = MagicMock(
            side_effect=[
                {"has_alerts": False},
                {"has_alerts": True, "alerts": [{"type": "frustration_detected"}]}
            ]
        )
        
        analytics_service.recommendation_service.get_cached_recommendations = MagicMock(
            side_effect=[
                {"has_recommendations": False},
                {
                    "has_recommendations": True,
                    "products": [{"id": "prod1"}],
                    "content": [{"type": "guide"}],
                    "next_actions": [{"action": "ofrecer_descuento"}]
                }
            ]
        )
        
        with patch('src.services.conversation_analytics_service.supabase_client.get_client', return_value=mock_client):
            result = await analytics_service.get_aggregate_analytics(days=7)
        
        assert result["has_analytics"] == True
        assert "time_period" in result
        assert result["time_period"]["days"] == 7
        
        assert "conversation_metrics" in result
        assert result["conversation_metrics"]["total_conversations"] == 2
        assert result["conversation_metrics"]["total_messages"] == 5
        
        assert "sentiment_metrics" in result
        assert "intent_metrics" in result
        assert "entity_metrics" in result
        assert "alert_metrics" in result
        assert "recommendation_metrics" in result
    
    @pytest.mark.asyncio
    async def test_get_aggregate_analytics_error(self, analytics_service):
        """Prueba que get_aggregate_analytics maneje correctamente los errores."""
        # Mock de Supabase para lanzar una excepción
        with patch('src.services.conversation_analytics_service.supabase_client.get_client', side_effect=Exception("Error de prueba")):
            result = await analytics_service.get_aggregate_analytics(days=7)
        
        assert result["has_analytics"] == False
        assert "Error al obtener análisis agregado" in result["message"]
    
    @pytest.mark.asyncio
    async def test_get_sentiment_trend_analysis_no_conversations(self, analytics_service):
        """Prueba que get_sentiment_trend_analysis maneje correctamente el caso sin conversaciones."""
        # Mock de Supabase
        mock_response = MagicMock()
        mock_response.data = []
        
        mock_execute = AsyncMock(return_value=mock_response)
        mock_gte = MagicMock()
        mock_gte.execute = mock_execute
        
        mock_select = MagicMock()
        mock_select.gte = MagicMock(return_value=mock_gte)
        
        mock_table = MagicMock()
        mock_table.select = MagicMock(return_value=mock_select)
        
        mock_client = MagicMock()
        mock_client.table = MagicMock(return_value=mock_table)
        
        with patch('src.services.conversation_analytics_service.supabase_client.get_client', return_value=mock_client):
            result = await analytics_service.get_sentiment_trend_analysis(days=30)
        
        assert result["has_analytics"] == False
        assert "No se encontraron conversaciones" in result["message"]
    
    @pytest.mark.asyncio
    async def test_get_sentiment_trend_analysis_success(self, analytics_service):
        """Prueba que get_sentiment_trend_analysis procese correctamente los datos para análisis de tendencias."""
        # Preparar datos de conversaciones en diferentes días
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        
        conversations = [
            {
                "conversation_id": "conv1",
                "session_insights": {
                    "intent_analysis": {"sentiment_score": 0.7}
                },
                "created_at": today.isoformat()
            },
            {
                "conversation_id": "conv2",
                "session_insights": {
                    "intent_analysis": {"sentiment_score": 0.8}
                },
                "created_at": today.isoformat()
            },
            {
                "conversation_id": "conv3",
                "session_insights": {
                    "intent_analysis": {"sentiment_score": -0.3}
                },
                "created_at": yesterday.isoformat()
            }
        ]
        
        # Mock de Supabase
        mock_response = MagicMock()
        mock_response.data = conversations
        
        mock_execute = AsyncMock(return_value=mock_response)
        mock_gte = MagicMock()
        mock_gte.execute = mock_execute
        
        mock_select = MagicMock()
        mock_select.gte = MagicMock(return_value=mock_gte)
        
        mock_table = MagicMock()
        mock_table.select = MagicMock(return_value=mock_select)
        
        mock_client = MagicMock()
        mock_client.table = MagicMock(return_value=mock_table)
        
        # Mock de servicios
        analytics_service.alert_service.get_alerts = MagicMock(
            side_effect=[
                {"has_alerts": False},
                {"has_alerts": True, "alerts": [{"type": "frustration_detected"}]},
                {"has_alerts": False}
            ]
        )
        
        with patch('src.services.conversation_analytics_service.supabase_client.get_client', return_value=mock_client):
            result = await analytics_service.get_sentiment_trend_analysis(days=30)
        
        assert result["has_analytics"] == True
        assert "time_period" in result
        assert result["time_period"]["days"] == 30
        
        assert "conversation_trend" in result
        assert "sentiment_trend" in result
        assert "alert_trend" in result
        
        # Verificar que haya datos para ambos días
        today_key = today.strftime("%Y-%m-%d")
        yesterday_key = yesterday.strftime("%Y-%m-%d")
        
        conversation_trend = {item["date"]: item["count"] for item in result["conversation_trend"]}
        sentiment_trend = {item["date"]: item["score"] for item in result["sentiment_trend"]}
        
        assert today_key in conversation_trend
        assert yesterday_key in conversation_trend
        assert conversation_trend[today_key] == 2
        assert conversation_trend[yesterday_key] == 1
        
        assert today_key in sentiment_trend
        assert yesterday_key in sentiment_trend
        assert sentiment_trend[today_key] == 0.75  # Promedio de 0.7 y 0.8
        assert sentiment_trend[yesterday_key] == -0.3
    
    @pytest.mark.asyncio
    async def test_get_sentiment_trend_analysis_error(self, analytics_service):
        """Prueba que get_sentiment_trend_analysis maneje correctamente los errores."""
        # Mock de Supabase para lanzar una excepción
        with patch('src.services.conversation_analytics_service.supabase_client.get_client', side_effect=Exception("Error de prueba")):
            result = await analytics_service.get_sentiment_trend_analysis(days=30)
        
        assert result["has_analytics"] == False
        assert "Error al obtener análisis de tendencias" in result["message"]
    
    def test_clear_analytics_cache_specific_conversation(self, analytics_service):
        """Prueba que clear_analytics_cache limpie correctamente la caché para una conversación específica."""
        # Almacenar análisis en caché
        analytics_service.analytics_cache["conv1"] = {"has_analytics": True}
        analytics_service.analytics_cache["conv2"] = {"has_analytics": True}
        
        # Verificar que existan
        assert "conv1" in analytics_service.analytics_cache
        assert "conv2" in analytics_service.analytics_cache
        
        # Limpiar caché para una conversación
        analytics_service.clear_analytics_cache("conv1")
        
        # Verificar que se haya eliminado solo la conversación especificada
        assert "conv1" not in analytics_service.analytics_cache
        assert "conv2" in analytics_service.analytics_cache
    
    def test_clear_analytics_cache_all(self, analytics_service):
        """Prueba que clear_analytics_cache limpie correctamente toda la caché."""
        # Almacenar análisis en caché
        analytics_service.analytics_cache["conv1"] = {"has_analytics": True}
        analytics_service.analytics_cache["conv2"] = {"has_analytics": True}
        
        # Verificar que existan
        assert "conv1" in analytics_service.analytics_cache
        assert "conv2" in analytics_service.analytics_cache
        
        # Limpiar toda la caché
        analytics_service.clear_analytics_cache()
        
        # Verificar que se haya eliminado todo
        assert len(analytics_service.analytics_cache) == 0
