import pytest
from src.services.intent_analysis_service import IntentAnalysisService

@pytest.fixture
def intent_service():
    return IntentAnalysisService()

@pytest.fixture
def messages_no_intent():
    return [
        {"role": "user", "content": "Hola, ¿podrías darme información del programa?"},
        {"role": "assistant", "content": "Claro, nuestro programa ofrece entrenamiento personalizado"},
        {"role": "user", "content": "¿Cuáles son los horarios disponibles?"},
        {"role": "assistant", "content": "Tenemos horarios flexibles"},
        {"role": "user", "content": "Gracias por la info"},
    ]

@pytest.fixture
def messages_with_intent():
    return [
        {"role": "user", "content": "Hola, quiero saber más sobre el programa"},
        {"role": "assistant", "content": "Claro, nuestro programa ofrece entrenamiento personalizado y seguimiento nutricional"},
        {"role": "user", "content": "¿Cuánto cuesta el programa?"},
        {"role": "assistant", "content": "El programa tiene un costo de $99 mensuales"},
        {"role": "user", "content": "Me interesa, ¿puedo pagar con tarjeta de crédito?"},
    ]

@pytest.fixture
def messages_with_rejection():
    return [
        {"role": "user", "content": "Hola, quiero saber más sobre el programa"},
        {"role": "assistant", "content": "Claro, nuestro programa ofrece entrenamiento personalizado y seguimiento nutricional"},
        {"role": "user", "content": "¿Cuánto cuesta el programa?"},
        {"role": "assistant", "content": "El programa tiene un costo de $99 mensuales"},
        {"role": "user", "content": "Es muy caro, no me interesa por ahora"},
    ]

def test_no_purchase_intent(intent_service, messages_no_intent):
    result = intent_service.analyze_purchase_intent(messages_no_intent)
    assert not result["has_purchase_intent"]
    assert not result["has_rejection"]
    assert result["purchase_intent_probability"] < intent_service.INTENT_THRESHOLD


def test_detects_purchase_intent(intent_service, messages_with_intent):
    result = intent_service.analyze_purchase_intent(messages_with_intent)
    assert result["has_purchase_intent"]
    assert not result["has_rejection"]
    assert "cuánto cuesta" in result["intent_indicators"]
    assert result["purchase_intent_probability"] >= intent_service.INTENT_THRESHOLD


def test_detects_rejection(intent_service, messages_with_rejection):
    result = intent_service.analyze_purchase_intent(messages_with_rejection)
    assert result["has_rejection"]
    assert "no me interesa" in result["rejection_indicators"]
    assert not result["has_purchase_intent"]
    assert result["purchase_intent_probability"] < intent_service.INTENT_THRESHOLD

