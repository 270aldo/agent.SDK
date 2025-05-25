"""
Pruebas unitarias para el servicio de predicción de conversión.
"""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch

from src.services.conversion_prediction_service import ConversionPredictionService

# Datos de prueba
MOCK_CONVERSATION_ID = "conv-123456"
MOCK_MESSAGES = [
    {"role": "user", "content": "Estoy interesado en su producto, ¿cuándo podría adquirirlo?"},
    {"role": "assistant", "content": "Nuestro producto está disponible inmediatamente. ¿Le gustaría conocer las opciones de pago?"},
    {"role": "user", "content": "Sí, me gustaría saber los precios y formas de pago disponibles."}
]
MOCK_CUSTOMER_PROFILE = {
    "industry": "technology",
    "company_size": "medium",
    "role": "CTO",
    "previous_purchases": ["product_a", "service_b"],
    "customer_since": "2023-01-15T00:00:00",
    "segment": "premium"
}

@pytest.fixture
def mock_supabase():
    """Fixture para simular el cliente de Supabase."""
    mock = MagicMock()
    mock.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
    return mock

@pytest.fixture
def mock_predictive_model_service():
    """Fixture para simular el servicio de modelos predictivos."""
    mock = AsyncMock()
    mock.get_model.return_value = {
        "parameters": json.dumps({
            "conversion_thresholds": {
                "low": 0.3,
                "medium": 0.6,
                "high": 0.8
            },
            "confidence_threshold": 0.65,
            "context_window": 10,
            "signal_weights": {
                "buying_signals": 0.4,
                "engagement_level": 0.3,
                "question_frequency": 0.2,
                "positive_sentiment": 0.25,
                "specific_inquiries": 0.35,
                "time_investment": 0.15
            }
        })
    }
    return mock

@pytest.fixture
def mock_nlp_service():
    """Fixture para simular el servicio NLP."""
    mock = AsyncMock()
    mock.analyze_message.return_value = {
        "sentiment": {"score": 0.7},
        "keywords": [
            {"text": "interesado", "relevance": 0.8},
            {"text": "precio", "relevance": 0.9},
            {"text": "formas de pago", "relevance": 0.85}
        ]
    }
    return mock

@pytest.fixture
def conversion_prediction_service(mock_supabase, mock_predictive_model_service, mock_nlp_service):
    """Fixture para crear una instancia del servicio de predicción de conversión."""
    return ConversionPredictionService(
        supabase_client=mock_supabase,
        predictive_model_service=mock_predictive_model_service,
        nlp_integration_service=mock_nlp_service
    )

@pytest.mark.asyncio
async def test_predict_conversion(conversion_prediction_service):
    """Prueba la predicción de conversión."""
    # Ejecutar la función a probar
    result = await conversion_prediction_service.predict_conversion(
        conversation_id=MOCK_CONVERSATION_ID,
        messages=MOCK_MESSAGES,
        customer_profile=MOCK_CUSTOMER_PROFILE
    )
    
    # Verificar el resultado
    assert "probability" in result
    assert "confidence" in result
    assert "category" in result
    assert "signals" in result
    assert "recommendations" in result
    
    # Verificar que la probabilidad esté en el rango correcto
    assert 0 <= result["probability"] <= 1
    
    # Verificar que la categoría sea válida
    assert result["category"] in ["low", "medium", "high", "very_high"]
    
    # Verificar que haya recomendaciones
    assert len(result["recommendations"]) > 0

@pytest.mark.asyncio
async def test_detect_conversion_signals(conversion_prediction_service):
    """Prueba la detección de señales de conversión."""
    # Ejecutar la función a probar
    signals = await conversion_prediction_service._detect_conversion_signals(
        client_messages=MOCK_MESSAGES,
        all_messages=MOCK_MESSAGES,
        signal_weights={
            "buying_signals": 0.4,
            "engagement_level": 0.3,
            "question_frequency": 0.2,
            "positive_sentiment": 0.25,
            "specific_inquiries": 0.35,
            "time_investment": 0.15
        }
    )
    
    # Verificar el resultado
    assert isinstance(signals, dict)
    
    # Verificar que se detecten señales específicas
    assert "buying_signals" in signals

@pytest.mark.asyncio
async def test_calculate_conversion_probability(conversion_prediction_service):
    """Prueba el cálculo de probabilidad de conversión."""
    # Datos de prueba
    signals = {
        "buying_signals": 0.8,
        "engagement_level": 0.7,
        "positive_sentiment": 0.6
    }
    
    # Ejecutar la función a probar
    probability, confidence = await conversion_prediction_service._calculate_conversion_probability(
        signals=signals,
        customer_profile=MOCK_CUSTOMER_PROFILE
    )
    
    # Verificar el resultado
    assert 0 <= probability <= 1
    assert 0 <= confidence <= 1

@pytest.mark.asyncio
async def test_get_conversion_recommendations(conversion_prediction_service):
    """Prueba la obtención de recomendaciones para aumentar conversión."""
    # Ejecutar la función a probar
    recommendations = await conversion_prediction_service._get_conversion_recommendations(
        conversion_category="medium",
        signals={"buying_signals": 0.6, "engagement_level": 0.5},
        customer_profile=MOCK_CUSTOMER_PROFILE
    )
    
    # Verificar el resultado
    assert isinstance(recommendations, list)
    assert len(recommendations) > 0
    
    # Verificar estructura de recomendaciones
    for recommendation in recommendations:
        assert "type" in recommendation
        assert "action" in recommendation
        assert "priority" in recommendation

@pytest.mark.asyncio
async def test_record_actual_conversion(conversion_prediction_service, mock_supabase, mock_predictive_model_service):
    """Prueba el registro de conversión real."""
    # Configurar mocks
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{
        "id": "pred-123",
        "prediction_data": json.dumps({
            "probability": 0.8,
            "category": "high",
            "signals": {"buying_signals": 0.8}
        })
    }]
    
    # Ejecutar la función a probar
    result = await conversion_prediction_service.record_actual_conversion(
        conversation_id=MOCK_CONVERSATION_ID,
        did_convert=True,
        conversion_details={"value": 1000, "product": "premium_plan"}
    )
    
    # Verificar llamadas a métodos
    mock_predictive_model_service.update_prediction_result.assert_called_once()
    mock_predictive_model_service.add_training_data.assert_called_once()

@pytest.mark.asyncio
async def test_empty_messages(conversion_prediction_service):
    """Prueba el comportamiento con mensajes vacíos."""
    # Ejecutar la función a probar
    result = await conversion_prediction_service.predict_conversion(
        conversation_id=MOCK_CONVERSATION_ID,
        messages=[],
        customer_profile=MOCK_CUSTOMER_PROFILE
    )
    
    # Verificar el resultado por defecto
    assert result["probability"] == 0
    assert result["confidence"] == 0
    assert result["category"] == "low"
    assert result["signals"] == {}
    assert result["recommendations"] == []
