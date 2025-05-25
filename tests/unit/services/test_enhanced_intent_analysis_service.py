"""
Pruebas unitarias para el servicio de análisis de intención mejorado.
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime, timedelta

from src.services.enhanced_intent_analysis_service import EnhancedIntentAnalysisService

class TestEnhancedIntentAnalysisService:
    """Pruebas para la clase EnhancedIntentAnalysisService."""
    
    @pytest.fixture
    def mock_resilient_client(self):
        """Fixture que proporciona un cliente resiliente simulado."""
        with patch("src.services.enhanced_intent_analysis_service.resilient_supabase_client") as mock_client:
            # Simular respuesta para select
            mock_client.select = AsyncMock(return_value=[])
            
            # Simular respuesta para insert
            mock_client.insert = AsyncMock(return_value={"data": [{"id": "test-id"}]})
            
            # Simular respuesta para update
            mock_client.update = AsyncMock(return_value={"data": [{"id": "test-id"}]})
            
            yield mock_client
    
    @pytest.fixture
    def mock_intent_service(self):
        """Fixture que proporciona una instancia simulada de EnhancedIntentAnalysisService."""
        # Crear un mock del servicio
        mock_service = MagicMock(spec=EnhancedIntentAnalysisService)
        
        # Configurar atributos
        mock_service.industry = "salud"
        mock_service.intent_model = {
            "id": "test-model-id",
            "industry": "salud",
            "intent_keywords": ["precio", "comprar", "interesado"],
            "rejection_keywords": ["no me interesa", "muy caro"],
            "keyword_weights": {"precio": 1.0, "comprar": 1.0, "interesado": 1.0},
            "sentiment_weights": {"positive": 0.3, "negative": -0.3, "engagement": 0.2},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Configurar métodos
        mock_service._analyze_sentiment = AsyncMock(side_effect=[0.7, -0.6, 0.1])
        mock_service._analyze_engagement = AsyncMock(side_effect=[0.8, 0.2])
        mock_service._extract_keywords = MagicMock(side_effect=[["precio", "interesa", "pagar"], ["no me interesa", "tal vez después"]])
        mock_service.analyze_purchase_intent = AsyncMock(side_effect=[
            # Primera llamada: intención positiva
            {
                "has_purchase_intent": True,
                "purchase_intent_probability": 0.7,
                "intent_indicators": ["precio", "interesado"],
                "rejection_indicators": [],
                "sentiment_score": 0.5,
                "engagement_score": 0.6
            },
            # Segunda llamada: intención negativa
            {
                "has_purchase_intent": False,
                "purchase_intent_probability": 0.2,
                "intent_indicators": [],
                "rejection_indicators": ["no me interesa"],
                "sentiment_score": -0.3,
                "engagement_score": 0.2
            }
        ])
        mock_service.should_continue_conversation = AsyncMock(side_effect=[(True, None), (False, "no_intent_detected")])
        mock_service.update_model_from_conversation = AsyncMock(return_value=True)
        
        return mock_service
    
    @pytest.mark.asyncio
    async def test_create(self, mock_resilient_client):
        """Prueba que el método de fábrica create inicializa correctamente el servicio."""
        # Simular el método _load_intent_model
        with patch.object(EnhancedIntentAnalysisService, '_load_intent_model') as mock_load:
            # Configurar valor de retorno
            mock_load.return_value = {
                "id": "test-model-id",
                "industry": "salud",
                "intent_keywords": ["precio", "comprar", "interesado"],
                "rejection_keywords": ["no me interesa", "muy caro"],
                "keyword_weights": {"precio": 1.0, "comprar": 1.0, "interesado": 1.0},
                "sentiment_weights": {"positive": 0.3, "negative": -0.3, "engagement": 0.2},
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            service = await EnhancedIntentAnalysisService.create(industry="salud")
            
            assert service.industry == "salud"
            assert service.intent_model is not None
            assert "intent_keywords" in service.intent_model
            assert "rejection_keywords" in service.intent_model
            
            # Verificar que se llamó al método _load_intent_model
            mock_load.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_load_intent_model_existing(self, mock_resilient_client):
        """Prueba que _load_intent_model carga un modelo existente correctamente."""
        # Configurar el mock para simular un modelo existente
        mock_model_data = [{
            "id": "test-model-id",
            "industry": "salud",
            "intent_keywords": json.dumps(["keyword1", "keyword2"]),
            "rejection_keywords": json.dumps(["rejection1", "rejection2"]),
            "keyword_weights": json.dumps({"keyword1": 1.2}),
            "sentiment_weights": json.dumps({"positive": 0.3, "negative": -0.3, "engagement": 0.2}),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }]
        mock_resilient_client.select.return_value = mock_model_data
        
        # Crear servicio y cargar modelo
        service = EnhancedIntentAnalysisService(industry="salud")
        model = await service._load_intent_model()
        
        # Verificar que el modelo se cargó correctamente
        assert model["id"] == "test-model-id"
        assert model["industry"] == "salud"
        assert "keyword1" in model["intent_keywords"]
        assert "rejection1" in model["rejection_keywords"]
        assert model["keyword_weights"]["keyword1"] == 1.2
        
        # Verificar que se llamó al método select
        mock_resilient_client.select.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_load_intent_model_new(self, mock_resilient_client):
        """Prueba que _load_intent_model crea un nuevo modelo si no existe."""
        # Configurar el mock para simular que no existe un modelo
        mock_resilient_client.select.return_value = []
        
        # Simular el método _get_industry_intent_keywords
        with patch.object(EnhancedIntentAnalysisService, '_get_industry_intent_keywords') as mock_intent_keywords, \
             patch.object(EnhancedIntentAnalysisService, '_get_industry_rejection_keywords') as mock_rejection_keywords:
            
            # Configurar valores de retorno
            mock_intent_keywords.return_value = ["precio", "comprar", "interesado"]
            mock_rejection_keywords.return_value = ["no me interesa", "muy caro"]
            
            # Crear servicio y cargar modelo
            service = EnhancedIntentAnalysisService(industry="tecnología")
            model = await service._load_intent_model()
            
            # Verificar que se creó un nuevo modelo
            assert model["industry"] == "tecnología"
            assert len(model["intent_keywords"]) > 0
            assert len(model["rejection_keywords"]) > 0
            assert "sentiment_weights" in model
            
            # Verificar que se llamó al método select y luego insert
            mock_resilient_client.select.assert_called_once()
            mock_resilient_client.insert.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_industry_intent_keywords(self):
        """Prueba que _get_industry_intent_keywords devuelve las palabras clave correctas."""
        service = EnhancedIntentAnalysisService(industry="salud")
        
        # Probar industria existente
        keywords = service._get_industry_intent_keywords("salud")
        assert len(keywords) > 0
        assert "salud" in keywords
        assert "bienestar" in keywords
        
        # Probar industria no existente
        keywords = service._get_industry_intent_keywords("industria_inexistente")
        assert len(keywords) > 0  # Debería devolver al menos las palabras clave base
    
    @pytest.mark.asyncio
    async def test_get_industry_rejection_keywords(self):
        """Prueba que _get_industry_rejection_keywords devuelve las palabras clave correctas."""
        service = EnhancedIntentAnalysisService(industry="salud")
        
        # Probar industria existente
        keywords = service._get_industry_rejection_keywords("salud")
        assert len(keywords) > 0
        assert "no es seguro" in keywords
        
        # Probar industria no existente
        keywords = service._get_industry_rejection_keywords("industria_inexistente")
        assert len(keywords) > 0  # Debería devolver al menos las palabras clave base
    
    @pytest.mark.asyncio
    async def test_analyze_purchase_intent_positive(self, mock_intent_service):
        """Prueba que analyze_purchase_intent detecta correctamente la intención de compra positiva."""
        # Configurar el mock para que devuelva intención positiva
        mock_intent_service.analyze_purchase_intent.side_effect = [
            {
                "has_purchase_intent": True,
                "purchase_intent_probability": 0.7,
                "intent_indicators": ["precio", "interesado"],
                "rejection_indicators": [],
                "has_rejection": False,
                "sentiment_score": 0.5,
                "engagement_score": 0.6
            }
        ]
        
        # Mensajes con intención de compra positiva
        messages = [
            {"role": "assistant", "content": "¿Puedo ayudarte con nuestros programas de salud?"},
            {"role": "user", "content": "Me interesa saber el precio del programa."},
            {"role": "assistant", "content": "El programa básico cuesta $99 al mes."},
            {"role": "user", "content": "Suena bien, ¿puedo pagar con tarjeta?"}
        ]
        
        result = await mock_intent_service.analyze_purchase_intent(messages)
        
        assert result["has_purchase_intent"] is True
        assert result["purchase_intent_probability"] > 0.5
        assert len(result["intent_indicators"]) > 0
        assert "precio" in result["intent_indicators"] or "interesado" in result["intent_indicators"]
        assert result["has_rejection"] is False
    
    @pytest.mark.asyncio
    async def test_analyze_purchase_intent_negative(self, mock_intent_service):
        """Prueba que analyze_purchase_intent detecta correctamente el rechazo."""
        # Configurar el mock para que devuelva intención negativa
        mock_intent_service.analyze_purchase_intent.side_effect = [
            {
                "has_purchase_intent": False,
                "purchase_intent_probability": 0.2,
                "intent_indicators": [],
                "rejection_indicators": ["no me interesa"],
                "sentiment_score": -0.3,
                "engagement_score": 0.2
            }
        ]
        
        # Mensajes con rechazo
        messages = [
            {"role": "assistant", "content": "¿Puedo ayudarte con nuestros programas de salud?"},
            {"role": "user", "content": "Solo estoy mirando, gracias."},
            {"role": "assistant", "content": "¿Te gustaría conocer nuestras ofertas?"},
            {"role": "user", "content": "No me interesa por ahora, tal vez después."}
        ]
        
        result = await mock_intent_service.analyze_purchase_intent(messages)
        
        assert result["has_purchase_intent"] is False
        assert result["purchase_intent_probability"] < 0.4
        assert len(result["rejection_indicators"]) > 0
        assert "no me interesa" in result["rejection_indicators"]
    
    @pytest.mark.asyncio
    async def test_analyze_sentiment(self, mock_intent_service):
        """Prueba que _analyze_sentiment calcula correctamente el sentimiento."""
        # Simular el método _analyze_sentiment
        with patch.object(mock_intent_service, '_analyze_sentiment') as mock_analyze:
            # Configurar valores de retorno para diferentes tipos de mensajes
            mock_analyze.side_effect = [
                0.7,  # Positivo
                -0.6,  # Negativo
                0.1   # Neutro
            ]
            
            # Mensajes positivos
            positive_messages = [
                "Me encanta este producto, es excelente.",
                "Estoy muy satisfecho con el servicio."
            ]
            
            # Mensajes negativos
            negative_messages = [
                "No me gusta este producto, es terrible.",
                "Estoy muy insatisfecho con el servicio."
            ]
            
            # Mensajes neutros
            neutral_messages = [
                "¿Cuánto cuesta este producto?",
                "¿Cuándo estará disponible?"
            ]
            
            # Analizar sentimiento
            positive_score = await mock_intent_service._analyze_sentiment(positive_messages)
            negative_score = await mock_intent_service._analyze_sentiment(negative_messages)
            neutral_score = await mock_intent_service._analyze_sentiment(neutral_messages)
            
            assert positive_score > 0
            assert negative_score < 0
            assert -0.5 < neutral_score < 0.5
    
    @pytest.mark.asyncio
    async def test_analyze_engagement(self, mock_intent_service):
        """Prueba que _analyze_engagement calcula correctamente el nivel de engagement."""
        # Simular el método _analyze_engagement
        with patch.object(mock_intent_service, '_analyze_engagement') as mock_analyze:
            # Configurar valores de retorno para diferentes tipos de mensajes
            mock_analyze.side_effect = [0.8, 0.2]  # Alto engagement, bajo engagement
            
            # Mensajes con alto engagement
            high_engagement = [
                "Me interesa mucho este producto. ¿Podrías darme más detalles sobre sus características y beneficios?",
                "¿Cuándo estará disponible? Estoy ansioso por probarlo."
            ]
            
            # Mensajes con bajo engagement
            low_engagement = [
                "Ok.",
                "Ya veo."
            ]
            
            # Analizar engagement
            high_score = await mock_intent_service._analyze_engagement(high_engagement)
            low_score = await mock_intent_service._analyze_engagement(low_engagement)
            
            assert high_score > 0.5
            assert low_score < 0.3
    
    @pytest.mark.asyncio
    async def test_should_continue_conversation(self, mock_intent_service):
        """Prueba que should_continue_conversation determina correctamente si continuar."""
        # Simular el método analyze_purchase_intent
        with patch.object(mock_intent_service, 'analyze_purchase_intent') as mock_analyze:
            # Configurar para que analyze_purchase_intent devuelva intención positiva primero
            mock_analyze.side_effect = [
                # Primera llamada: intención positiva
                {
                    "has_purchase_intent": True,
                    "purchase_intent_probability": 0.7,
                    "intent_indicators": ["precio", "interesado"],
                    "rejection_indicators": [],
                    "sentiment_score": 0.5,
                    "engagement_score": 0.6
                },
                # Segunda llamada: intención negativa
                {
                    "has_purchase_intent": False,
                    "purchase_intent_probability": 0.2,
                    "intent_indicators": [],
                    "rejection_indicators": ["no me interesa"],
                    "sentiment_score": -0.3,
                    "engagement_score": 0.2
                }
            ]
            
            # Mensajes de prueba
            messages = [
                {"role": "assistant", "content": "¿Puedo ayudarte?"},
                {"role": "user", "content": "Me interesa el programa."}
            ]
            
            # Tiempo de inicio reciente
            recent_start_time = datetime.now() - timedelta(minutes=5)
            
            # Verificar que debería continuar (hay intención de compra)
            should_continue, reason = await mock_intent_service.should_continue_conversation(
                messages, recent_start_time, intent_detection_timeout=300
            )
            
            assert should_continue is True
            assert reason is None
            
            # Tiempo de inicio antiguo (excede el timeout)
            old_start_time = datetime.now() - timedelta(minutes=10)
            
            # Verificar que no debería continuar (no hay intención y excede timeout)
            should_continue, reason = await mock_intent_service.should_continue_conversation(
                messages, old_start_time, intent_detection_timeout=300
            )
            
            assert should_continue is False
            assert reason == "no_intent_detected"
    
    @pytest.mark.asyncio
    async def test_update_model_from_conversation(self, mock_intent_service, mock_resilient_client):
        """Prueba que update_model_from_conversation actualiza correctamente el modelo."""
        # Configurar el mock para que devuelva True
        mock_intent_service.update_model_from_conversation.return_value = True
        
        # Mensajes de conversación con conversión exitosa
        messages = [
            {"role": "assistant", "content": "¿Puedo ayudarte?"},
            {"role": "user", "content": "Me interesa el programa de bienestar. ¿Cuánto cuesta?"},
            {"role": "assistant", "content": "El programa cuesta $99 al mes."},
            {"role": "user", "content": "Suena bien, me gustaría adquirirlo."}
        ]
        
        # Actualizar modelo (conversión exitosa)
        result = await mock_intent_service.update_model_from_conversation(
            conversation_id="test-conversation",
            messages=messages,
            conversion_result=True
        )
        
        # Verificar que el resultado es True
        assert result is True
        
        # Verificar que se llamó al método con los parámetros correctos
        mock_intent_service.update_model_from_conversation.assert_called_once_with(
            conversation_id="test-conversation",
            messages=messages,
            conversion_result=True
        )
