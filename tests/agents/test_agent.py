"""
Pruebas de interacción con el Agente de Ventas NGX.
Permite simular conversaciones y observar las respuestas del agente.
"""
import pytest
import os
import asyncio
import logging
from dotenv import load_dotenv

from src.models.conversation import CustomerData, Message  # Message importado para tipado si es necesario
from src.services.conversation_service import ConversationService

# Configurar logging (pytest lo captura por defecto, pero puede ser útil para debug)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno (pytest-dotenv puede manejar esto también)
load_dotenv()

# Datos de prueba para escenarios
ESCENARIO_DETALLES_PRIME = {
    "customer_name": "Ana Torres",
    "program_type": "PRIME",
    "messages": [
        "Hola, ¿qué tal?",
        "Cuéntame más sobre el programa PRIME.",
        "¿Cuál es el precio de PRIME?"
    ]
}

ESCENARIO_OBJECION_LONGEVITY = {
    "customer_name": "Roberto Diaz",
    "program_type": "LONGEVITY",
    "messages": [
        "Me interesa Longevity, pero suena un poco caro.",
        "¿Qué resultados puedo esperar?"
    ]
}

# Fixture para inicializar ConversationService (opcional, podría instanciarse directamente)
@pytest.fixture(scope="module")
def conversation_service():
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY no está configurada. Saltando pruebas de agente.")
    return ConversationService()

async def run_agent_interaction_scenario(
    service: ConversationService,
    customer_name: str,
    program_type: str,
    test_messages: list[str]
):
    """
    Helper para simular una interacción completa con el agente.
    """
    logger.info(f"--- Iniciando escenario para {customer_name} ({program_type}) ---")
    
    customer = CustomerData(
        name=customer_name,
        email=f"{customer_name.lower().replace(' ', '.')}@example.com",
        age=42,
        gender="male", # Ajustar según el escenario si es necesario
        occupation="CEO", # Ajustar según el escenario
        goals={"primary": "aumentar energía", "secondary": ["mejorar concentración"]}
    )
    
    # 1. Iniciar conversación
    try:
        state = await service.start_conversation(customer_data=customer, program_type=program_type)
        conversation_id = state.id
        logger.info(f"Conversación iniciada con ID: {conversation_id}")
        initial_message = state.messages[-1]
        logger.info(f"🤖 Agente NGX ({initial_message.role}): {initial_message.content}")
        assert initial_message.role == "assistant"
        assert len(initial_message.content) > 0

    except Exception as e:
        logger.error(f"Error al iniciar la conversación: {e}", exc_info=True)
        pytest.fail(f"Error al iniciar la conversación: {e}")
        return # Necesario para que el linter no se queje de un posible uso antes de asignación

    if not test_messages:
        logger.info("No se proporcionaron mensajes de prueba para este escenario.")
        return

    # 2. Procesar mensajes de prueba
    for i, user_message_text in enumerate(test_messages):
        logger.info(f"--- Enviando Mensaje #{i+1}: {user_message_text} ---")
        print(f"👤 {customer_name}: {user_message_text}") # Para visibilidad en la salida de pytest
        
        try:
            updated_state, audio_stream = await service.process_message(
                conversation_id=conversation_id, 
                message_text=user_message_text
            )
            agent_response_message = updated_state.messages[-1]
            logger.info(f"🤖 Agente NGX ({agent_response_message.role}): {agent_response_message.content}")
            print(f"🤖 Agente NGX: {agent_response_message.content}") # Para visibilidad

            assert agent_response_message.role == "assistant"
            assert len(agent_response_message.content) > 0
            # Aquí se podrían añadir aserciones más específicas sobre el contenido de la respuesta si es necesario

        except Exception as e:
            logger.error(f"Error al procesar el mensaje '{user_message_text}': {e}", exc_info=True)
            pytest.fail(f"Error al procesar el mensaje '{user_message_text}': {e}")
            continue 

    logger.info(f"--- Escenario para {customer_name} ({program_type}) finalizado ---")

@pytest.mark.asyncio
async def test_agent_scenario_detalles_prime(conversation_service: ConversationService):
    """Prueba el escenario de solicitud de detalles del programa PRIME."""
    scenario = ESCENARIO_DETALLES_PRIME
    await run_agent_interaction_scenario(
        service=conversation_service,
        customer_name=scenario["customer_name"],
        program_type=scenario["program_type"],
        test_messages=scenario["messages"]
    )

@pytest.mark.asyncio
@pytest.mark.skip(reason="Deshabilitado temporalmente para enfocarse en el primer escenario.") # Ejemplo de cómo saltar una prueba
async def test_agent_scenario_objecion_longevity(conversation_service: ConversationService):
    """Prueba el escenario de objeción de precio para el programa LONGEVITY."""
    scenario = ESCENARIO_OBJECION_LONGEVITY
    await run_agent_interaction_scenario(
        service=conversation_service,
        customer_name=scenario["customer_name"],
        program_type=scenario["program_type"],
        test_messages=scenario["messages"]
    )

# Consideraciones adicionales para estas pruebas de agente:
# 1. Dependencia de API Externa: Estas pruebas dependen de la API de OpenAI.
#    Se recomienda marcarlas (e.g., @pytest.mark.integration, @pytest.mark.openai_api)
#    para poder incluirlas o excluirlas selectivamente durante la ejecución de pruebas.
# 2. Costos: Cada ejecución de estas pruebas incurre en costos de API.
# 3. No Determinismo: Las respuestas del LLM pueden variar ligeramente, lo que puede
#    hacer que las aserciones exactas sobre el contenido del mensaje fallen.
#    Es mejor enfocarse en:
#    - Que la conversación no falle.
#    - Que el agente responda (contenido no vacío).
#    - Que el rol del mensaje sea 'assistant'.
#    - Validar la lógica de negocio si es posible (ej. si se detecta una objeción correctamente).
# 4. Mocking: Para pruebas unitarias verdaderas del ConversationService, se debería mockear
#    el cliente de OpenAI (OpenAIEngine o similar) para controlar las respuestas y evitar
#    llamadas reales a la API. Estas pruebas actuales son más bien pruebas de integración.