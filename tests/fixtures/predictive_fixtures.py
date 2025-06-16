"""
Fixtures comunes para pruebas de servicios predictivos.

Este módulo contiene fixtures reutilizables para las pruebas de los servicios predictivos.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from src.services.nlp_integration_service import NLPIntegrationService
from src.services.predictive_model_service import PredictiveModelService
from src.services.entity_recognition_service import EntityRecognitionService
from src.services.keyword_extraction_service import KeywordExtractionService


class MockNLPService(NLPIntegrationService):
    """Mock para NLPIntegrationService"""
    
    async def analyze_sentiment(self, text):
        """Mock para análisis de sentimiento"""
        return {
            "positive": 0.3,
            "negative": 0.6,
            "neutral": 0.1,
        }
    
    async def extract_keywords(self, text):
        """Mock para extracción de palabras clave"""
        return ["precio", "calidad", "servicio"]
        
    async def analyze_entities(self, text):
        """Mock para análisis de entidades"""
        return {"products": ["producto1"], "features": ["característica1"]}
        
    async def detect_keyword_signals(self, text, keywords):
        """Mock para detección de señales de palabras clave"""
        return {"price_mentions": 0.7, "hesitation_words": 0.3}


@pytest.fixture
def mock_nlp_service():
    """Fixture que proporciona un servicio NLP mock para pruebas."""
    return MockNLPService()


@pytest.fixture
def mock_predictive_model_service():
    """Fixture que proporciona un servicio de modelo predictivo mock para pruebas."""
    service = MagicMock(spec=PredictiveModelService)
    service.initialize_model = AsyncMock()
    service.store_prediction = AsyncMock()
    service.get_model_data = AsyncMock(return_value={"model_version": "1.0"})
    service.add_training_data = AsyncMock()
    service.record_actual_result = AsyncMock()
    return service


@pytest.fixture
def mock_entity_recognition_service():
    """Fixture que proporciona un servicio de reconocimiento de entidades mock para pruebas."""
    service = MagicMock(spec=EntityRecognitionService)
    service.extract_entities = AsyncMock(return_value={
        "products": ["producto1", "producto2"],
        "features": ["característica1", "característica2"],
        "needs": ["necesidad1", "necesidad2"]
    })
    service.get_entity_context = AsyncMock(return_value={
        "product_context": {"producto1": "Descripción del producto 1"},
        "feature_context": {"característica1": "Descripción de la característica 1"}
    })
    return service


@pytest.fixture
def mock_keyword_extraction_service():
    """Fixture que proporciona un servicio de extracción de palabras clave mock para pruebas."""
    service = MagicMock(spec=KeywordExtractionService)
    service.extract_keywords = AsyncMock(return_value=[
        {"keyword": "precio", "score": 0.9, "category": "pricing"},
        {"keyword": "calidad", "score": 0.8, "category": "quality"}
    ])
    service.analyze_conversation = AsyncMock(return_value={
        "main_topics": ["precio", "calidad"],
        "sentiment": {"positive": 0.3, "negative": 0.6, "neutral": 0.1},
        "key_phrases": ["mejor precio", "alta calidad"]
    })
    return service
