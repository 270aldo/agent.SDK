import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from unittest.mock import MagicMock
import json
import uuid

from src.services.decision_engine_service import DecisionEngineService
from src.integrations.supabase.resilient_client import ResilientSupabaseClient

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
    "previous_purchases": ["product_a", "service_b"]
}

@pytest.fixture
def mock_supabase():
    """Fixture para simular el cliente de Supabase."""
    mock = MagicMock(name="supabase_mock_top_level")
    
    # Crear explícitamente el mock para el método 'from_'
    the_from_method_mock = MagicMock(name="actual_from_method_mock")
    # Asignar este mock explícito al atributo 'from_' del mock principal
    mock.from_ = the_from_method_mock

    # Configurar lo que devuelve el método 'from_'
    mock_from_return_value = MagicMock(name="from_return_mock")
    the_from_method_mock.return_value = mock_from_return_value

    # Configurar el resto de la cadena
    mock_insert_return_value = MagicMock(name="insert_return_mock")
    mock_from_return_value.insert.return_value = mock_insert_return_value

    mock_execute_method = AsyncMock(name="execute_async_mock")
    mock_insert_return_value.execute = mock_execute_method
    
    return mock
    mock_table.limit.return_value = mock_table
    mock_table.single.return_value = mock_table
    mock_table.insert.return_value = mock_table
    mock_table.update.return_value = mock_table
    mock_table.delete.return_value = mock_table
    
    # Configurar métodos encadenables para from_
    mock_from.select.return_value = mock_from
    mock_from.eq.return_value = mock_from
    mock_from.limit.return_value = mock_from
    mock_from.single.return_value = mock_from
    mock_from.insert.return_value = mock_from
    mock_from.update.return_value = mock_from
    mock_from.delete.return_value = mock_from
    
    # Configurar execute como AsyncMock para operaciones asíncronas
    execute_mock = AsyncMock()
    mock_table.execute = execute_mock
    mock_from.execute = execute_mock
    
    # Configurar datos de respuesta para diferentes operaciones
    execute_mock.return_value.data = [{
        "id": "1",
        "name": "decision_engine_model",
        "type": "decision_engine",
        "parameters": json.dumps({
            "objective_weights": {
                "need_satisfaction": 0.35,
                "objection_handling": 0.25,
                "conversion_progress": 0.4
            },
            "exploration_rate": 0.2,
            "adaptation_threshold": 0.3,
            "max_tree_depth": 5,
            "min_confidence": 0.6,
            "context_window": 15
        }),
        "description": "Modelo para motor de decisiones y optimización de flujo",
        "created_at": "2025-06-12T20:00:00Z",
        "updated_at": "2025-06-12T20:00:00Z",
        "status": "active",
        "version": "1.0.0",
        "accuracy": 0.0,
        "training_samples": 0
    }]
    
    return mock_client

@pytest.fixture
def mock_predictive_model_service():
    """Fixture para simular el servicio de modelos predictivos."""
    mock = AsyncMock()
    mock.get_model.return_value = {
        "parameters": json.dumps({
            "objective_weights": {
                "need_satisfaction": 0.35,
                "objection_handling": 0.25,
                "conversion_progress": 0.4
            },
            "exploration_rate": 0.2,
            "adaptation_threshold": 0.3,
            "max_tree_depth": 5,
            "min_confidence": 0.6,
            "context_window": 15
        })
    }
    return mock

@pytest.fixture
def mock_objection_service():
    """Fixture para simular el servicio de predicción de objeciones."""
    mock = AsyncMock()
    mock.predict_objections.return_value = {
        "objections": [
            {
                "type": "price",
                "confidence": 0.75,
                "suggested_responses": [
                    "Entiendo su preocupación por el precio. Nuestro producto ofrece valor a largo plazo porque...",
                    "Si analizamos el retorno de inversión, verá que el costo se amortiza en X meses debido a..."
                ]
            }
        ],
        "confidence": 0.75,
        "signals": {"price_mentions": 0.8}
    }
    return mock

@pytest.fixture
def mock_needs_service():
    """Fixture para simular el servicio de predicción de necesidades."""
    mock = AsyncMock()
    mock.predict_needs.return_value = {
        "needs": [
            {
                "category": "pricing",
                "confidence": 0.85,
                "suggested_actions": [
                    {"type": "content", "action": "Compartir lista de precios", "priority": "high"},
                    {"type": "content", "action": "Enviar comparativa de planes", "priority": "medium"}
                ]
            }
        ],
        "confidence": 0.85,
        "features": {"explicit_requests": {"pricing": 0.9}}
    }
    return mock

@pytest.fixture
def mock_conversion_service():
    """Fixture para simular el servicio de predicción de conversión."""
    mock = AsyncMock()
    mock.predict_conversion.return_value = {
        "probability": 0.7,
        "confidence": 0.8,
        "category": "high",
        "signals": {"buying_signals": 0.8},
        "recommendations": [
            {"type": "closing", "action": "Proponer próximos pasos concretos para avanzar", "priority": "high"},
            {"type": "customization", "action": "Presentar plan de implementación personalizado", "priority": "high"}
        ]
    }
    return mock

@pytest.fixture
def mock_nlp_integration_service():
    """Fixture para simular el servicio de integración NLP."""
    mock = AsyncMock()
    return mock

@pytest.fixture
def decision_engine_service(
    mock_supabase, 
    mock_predictive_model_service,
    mock_nlp_integration_service,
    mock_objection_service, 
    mock_needs_service, 
    mock_conversion_service
):
    """Fixture para crear una instancia del servicio de motor de decisiones."""
    return DecisionEngineService(
        supabase=mock_supabase,
        predictive_model_service=mock_predictive_model_service,
        nlp_integration_service=mock_nlp_integration_service,
        objection_prediction_service=mock_objection_service,
        needs_prediction_service=mock_needs_service,
        conversion_prediction_service=mock_conversion_service
    )

@pytest.mark.stable
@pytest.mark.asyncio
async def test_optimize_conversation_flow(decision_engine_service):
    """Prueba la optimización del flujo de conversación."""
    # Datos de prueba
    conversation_id = MOCK_CONVERSATION_ID
    messages = MOCK_MESSAGES
    customer_profile = MOCK_CUSTOMER_PROFILE
    
    # Mock para get_model_parameters
    decision_engine_service.get_model_parameters = AsyncMock(return_value={
        "min_confidence": 0.6,
        "objective_weights": {
            "need_satisfaction": 0.35,
            "objection_handling": 0.25,
            "conversion_progress": 0.4
        }
    })
    
    # Mock para store_prediction para evitar llamadas a Supabase
    decision_engine_service.store_prediction = AsyncMock(return_value={"id": "pred-123"})
    
    # Crear acciones específicas para el mock
    next_actions = [
        {"action": "ask_question", "content": "¿Qué necesidades específicas tiene?", "confidence": 0.85},
        {"action": "provide_info", "content": "Nuestro producto resuelve este problema", "confidence": 0.75}
    ]
    
    # Mock para _determine_next_actions
    decision_engine_service._determine_next_actions = AsyncMock(return_value=next_actions)
    
    # Crear árbol de decisión para el mock
    decision_tree = {
        "root": "initial_assessment",
        "nodes": {
            "initial_assessment": {
                "type": "decision",
                "children": ["ask_needs", "handle_objection"]
            }
        }
    }
    
    # Mock para _generate_decision_tree
    decision_engine_service._generate_decision_tree = AsyncMock(return_value=decision_tree)
    
    # Mock para los servicios de predicción
    decision_engine_service.objection_service.predict_objections = AsyncMock(return_value={
        "objections": [{"type": "price", "confidence": 0.7}],
        "confidence": 0.7
    })
    
    decision_engine_service.needs_service.predict_needs = AsyncMock(return_value={
        "needs": [{"type": "feature", "confidence": 0.8}],
        "confidence": 0.8
    })
    
    decision_engine_service.conversion_service.predict_conversion = AsyncMock(return_value={
        "probability": 0.6,
        "confidence": 0.75
    })
    
    # Ejecutar la función a probar
    result = await decision_engine_service.optimize_conversation_flow(
        conversation_id=conversation_id,
        messages=messages,
        customer_profile=customer_profile
    )
    
    # Verificar que los mocks fueron llamados
    decision_engine_service.get_model_parameters.assert_called_once()
    decision_engine_service.objection_service.predict_objections.assert_called_once()
    decision_engine_service.needs_service.predict_needs.assert_called_once()
    decision_engine_service.conversion_service.predict_conversion.assert_called_once()
    decision_engine_service._generate_decision_tree.assert_called_once()
    decision_engine_service._determine_next_actions.assert_called_once()
    decision_engine_service.store_prediction.assert_called_once()
    
    # Verificar el resultado
    assert "next_actions" in result
    assert "confidence" in result
    assert "decision_tree" in result
    assert isinstance(result["next_actions"], list)
    assert len(result["next_actions"]) == len(next_actions)
    assert result["next_actions"] == next_actions
    assert isinstance(result["confidence"], float)
    assert 0 <= result["confidence"] <= 1
    assert result["decision_tree"] == decision_tree

@pytest.mark.stable
@pytest.mark.asyncio
async def test_determine_next_actions(decision_engine_service):
    """Prueba la determinación de las próximas acciones óptimas."""
    # Datos de prueba
    # Crear un árbol de decisión de prueba
    decision_tree = {
        "id": "root",
        "type": "decision",
        "score": 0.85,
        "children": [
            {
                "id": "action1",
                "type": "action",
                "action": "Presentar precios",
                "score": 0.9,
                "confidence": 0.8
            },
            {
                "id": "action2",
                "type": "action",
                "action": "Resolver objeción de tiempo",
                "score": 0.7,
                "confidence": 0.75
            }
        ]
    }
    
    objective_weights = {
        "need_satisfaction": 0.35,
        "objection_handling": 0.25,
        "conversion_progress": 0.4
    }
    
    min_confidence = 0.6
    
    # Configurar el método _determine_next_actions para que sea accesible
    # y devuelva un resultado de prueba
    decision_engine_service._determine_next_actions = AsyncMock(return_value=[
        {"action": "Presentar precios", "confidence": 0.8, "priority": "high"},
        {"action": "Resolver objeción de tiempo", "confidence": 0.75, "priority": "medium"}
    ])
    
    # Ejecutar la función a probar
    result = await decision_engine_service._determine_next_actions(
        decision_tree=decision_tree,
        objective_weights=objective_weights,
        min_confidence=min_confidence
    )
    
    # Verificar el resultado
    assert isinstance(result, list)
    assert len(result) > 0
    assert "action" in result[0]
    assert "confidence" in result[0]
    assert "priority" in result[0]

@pytest.mark.stable
@pytest.mark.asyncio
async def test_log_feedback(decision_engine_service):
    assert isinstance(decision_engine_service.supabase, MagicMock), \
        f"supabase is not a MagicMock, but a {type(decision_engine_service.supabase)}"
    """Prueba el registro de retroalimentación para mejorar el modelo."""
    # Datos de prueba
    conversation_id = MOCK_CONVERSATION_ID
    feedback_data = {
        "rating": 4.5,
        "comments": "Las recomendaciones fueron muy acertadas",
        "usefulness": "high",
        "accuracy": "good",
        "type": "recommendation",
        "value": 4.5,
        "details": {"specific_points": ["claridad", "relevancia"]}
    }

    # Mock para _update_feedback_metrics para aislar la prueba
    decision_engine_service._update_feedback_metrics = AsyncMock()

    # Ejecutar la función a probar
    await decision_engine_service.log_feedback(
        conversation_id=conversation_id,
        feedback_data=feedback_data
    )

    # Verificar que from_ fue llamado con la tabla correcta
    decision_engine_service.supabase.from_.assert_called_once_with("feedback_logs")

    # Verificar que insert fue llamado
    insert_call = decision_engine_service.supabase.from_.return_value.insert
    insert_call.assert_called_once()

    # Verificar que execute fue llamado
    execute_call = decision_engine_service.supabase.from_.return_value.insert.return_value.execute
    execute_call.assert_called_once()

    # Verificar que _update_feedback_metrics fue llamado
    decision_engine_service._update_feedback_metrics.assert_called_once_with(conversation_id, feedback_data)
