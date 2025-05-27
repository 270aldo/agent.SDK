"""
Pruebas para el servicio de análisis de intención de compra.
"""
import pytest
import asyncio
import logging
from datetime import datetime, timedelta
from src.services.intent_analysis_service import IntentAnalysisService
from src.models.conversation import Message  # Asumiendo que Message es un Pydantic model o similar

# Configurar logging básico para pytest (opcional, pytest tiene su propio sistema de captura)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Datos de prueba reutilizables
MESSAGES_NO_INTENT = [
    Message(role="user", content="Hola, quiero saber más sobre el programa"),
    Message(role="assistant", content="Claro, nuestro programa ofrece entrenamiento personalizado y seguimiento nutricional"),
    Message(role="user", content="¿Cuánto tiempo lleva ver resultados?"),
    Message(role="assistant", content="La mayoría de nuestros clientes ven resultados en 4-6 semanas"),
    Message(role="user", content="Interesante, lo pensaré")
]

MESSAGES_WITH_INTENT = [
    Message(role="user", content="Hola, quiero saber más sobre el programa"),
    Message(role="assistant", content="Claro, nuestro programa ofrece entrenamiento personalizado y seguimiento nutricional"),
    Message(role="user", content="¿Cuánto cuesta el programa?"),
    Message(role="assistant", content="El programa tiene un costo de $99 mensuales"),
    Message(role="user", content="Me interesa, ¿puedo pagar con tarjeta de crédito?")
]

MESSAGES_WITH_REJECTION = [
    Message(role="user", content="Hola, quiero saber más sobre el programa"),
    Message(role="assistant", content="Claro, nuestro programa ofrece entrenamiento personalizado y seguimiento nutricional"),
    Message(role="user", content="¿Cuánto cuesta el programa?"),
    Message(role="assistant", content="El programa tiene un costo de $99 mensuales"),
    Message(role="user", content="Es muy caro, no me interesa por ahora")
]

@pytest.fixture
def intent_service():
    """Provee una instancia de IntentAnalysisService para las pruebas."""
    return IntentAnalysisService()

def test_analyze_purchase_intent_no_intent(intent_service: IntentAnalysisService):
    """Prueba el análisis de intención para una conversación sin intención de compra."""
    logger.info("Ejecutando: test_analyze_purchase_intent_no_intent")
    result = intent_service.analyze_purchase_intent(MESSAGES_NO_INTENT)
    logger.info(f"Resultado (sin intención): {result}")
    assert result.intent == "no_intent"
    assert result.confidence >= 0.0 # Ejemplo, ajustar según la lógica real
    # Se podría agregar más aserciones sobre los detalles si es necesario

def test_analyze_purchase_intent_with_intent(intent_service: IntentAnalysisService):
    """Prueba el análisis de intención para una conversación con intención de compra."""
    logger.info("Ejecutando: test_analyze_purchase_intent_with_intent")
    result = intent_service.analyze_purchase_intent(MESSAGES_WITH_INTENT)
    logger.info(f"Resultado (con intención): {result}")
    assert result.intent == "purchase"
    assert result.confidence > 0.5 # Ejemplo
    assert "pagar con tarjeta de crédito" in result.details.lower()

def test_analyze_purchase_intent_with_rejection(intent_service: IntentAnalysisService):
    """Prueba el análisis de intención para una conversación con rechazo explícito."""
    logger.info("Ejecutando: test_analyze_purchase_intent_with_rejection")
    result = intent_service.analyze_purchase_intent(MESSAGES_WITH_REJECTION)
    logger.info(f"Resultado (con rechazo): {result}")
    assert result.intent == "rejection"
    assert result.confidence > 0.5 # Ejemplo
    assert "muy caro" in result.details.lower()


@pytest.mark.asyncio
async def test_should_continue_conversation_scenarios(intent_service: IntentAnalysisService):
    """Prueba la lógica de corte inteligente de la conversación."""
    logger.info("Ejecutando: test_should_continue_conversation_scenarios")

    # Caso 1: Tiempo no excedido
    session_start_recent = datetime.now() - timedelta(minutes=2)
    should_continue, reason = await intent_service.should_continue_conversation(
        MESSAGES_NO_INTENT, 
        session_start_recent,
        180  # 3 minutos
    )
    logger.info(f"Caso 1 (tiempo no excedido): Continuar={should_continue}, Razón={reason}")
    assert should_continue is True
    assert reason == "Tiempo de sesión no excedido"

    # Caso 2: Tiempo excedido, sin intención
    session_start_old = datetime.now() - timedelta(minutes=4)
    should_continue, reason = await intent_service.should_continue_conversation(
        MESSAGES_NO_INTENT, 
        session_start_old,
        180  # 3 minutos
    )
    logger.info(f"Caso 2 (tiempo excedido, sin intención): Continuar={should_continue}, Razón={reason}")
    assert should_continue is False
    assert reason == "Tiempo de sesión excedido y sin intención clara de compra."

    # Caso 3: Tiempo excedido, con intención
    should_continue, reason = await intent_service.should_continue_conversation(
        MESSAGES_WITH_INTENT, 
        session_start_old,
        180  # 3 minutos
    )
    logger.info(f"Caso 3 (tiempo excedido, con intención): Continuar={should_continue}, Razón={reason}")
    assert should_continue is True
    assert reason == "Tiempo de sesión excedido, pero hay intención de compra."
    
    # Caso 4: Tiempo excedido, con rechazo
    should_continue, reason = await intent_service.should_continue_conversation(
        MESSAGES_WITH_REJECTION, 
        session_start_old,
        180  # 3 minutos
    )
    logger.info(f"Caso 4 (tiempo excedido, con rechazo): Continuar={should_continue}, Razón={reason}")
    assert should_continue is False
    assert reason == "Tiempo de sesión excedido y cliente ha rechazado la oferta."

# Para ejecutar estas pruebas con pytest, simplemente corre `pytest` en la terminal
# en el directorio raíz del proyecto.
# Asegúrate de que `pytest` y `pytest-asyncio` están instalados.
# (pip install pytest pytest-asyncio)
#
# El `if __name__ == "__main__":` block ya no es necesario con pytest.
