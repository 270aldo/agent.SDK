"""
Pruebas unitarias para el servicio de motor de decisiones.
"""

import pytest
import json
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

from src.services.decision_engine_service import DecisionEngineService

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
    mock = MagicMock()
    mock.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
    return mock

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
def decision_engine_service(
    mock_supabase, 
    mock_predictive_model_service, 
    mock_objection_service, 
    mock_needs_service, 
    mock_conversion_service
):
    """Fixture para crear una instancia del servicio de motor de decisiones."""
    return DecisionEngineService(
        supabase_client=mock_supabase,
        predictive_model_service=mock_predictive_model_service,
        objection_prediction_service=mock_objection_service,
        needs_prediction_service=mock_needs_service,
        conversion_prediction_service=mock_conversion_service
    )

@pytest.mark.asyncio
async def test_optimize_conversation_flow(decision_engine_service):
    """Prueba la optimización del flujo de conversación."""
    # Ejecutar la función a probar
    result = await decision_engine_service.optimize_conversation_flow(
        conversation_id=MOCK_CONVERSATION_ID,
        messages=MOCK_MESSAGES,
        customer_profile=MOCK_CUSTOMER_PROFILE
    )
    
    # Verificar el resultado
    assert "next_actions" in result
    assert "decision_tree" in result
    assert "objectives" in result
    assert "confidence" in result
    
    # Verificar que haya acciones recomendadas
    assert len(result["next_actions"]) > 0
    
    # Verificar que el árbol de decisión tenga la estructura correcta
    assert "id" in result["decision_tree"]
    assert "type" in result["decision_tree"]
    assert "children" in result["decision_tree"]

@pytest.mark.asyncio
async def test_generate_decision_tree(decision_engine_service, mock_objection_service, mock_needs_service, mock_conversion_service):
    """Prueba la generación del árbol de decisión."""
    # Obtener predicciones de los servicios
    objection_prediction = await mock_objection_service.predict_objections(MOCK_CONVERSATION_ID, MOCK_MESSAGES, MOCK_CUSTOMER_PROFILE)
    needs_prediction = await mock_needs_service.predict_needs(MOCK_CONVERSATION_ID, MOCK_MESSAGES, MOCK_CUSTOMER_PROFILE)
    conversion_prediction = await mock_conversion_service.predict_conversion(MOCK_CONVERSATION_ID, MOCK_MESSAGES, MOCK_CUSTOMER_PROFILE)
    
    # Ejecutar la función a probar
    decision_tree = await decision_engine_service._generate_decision_tree(
        objection_prediction=objection_prediction,
        needs_prediction=needs_prediction,
        conversion_prediction=conversion_prediction,
        objective_weights={"need_satisfaction": 0.35, "objection_handling": 0.25, "conversion_progress": 0.4},
        customer_profile=MOCK_CUSTOMER_PROFILE
    )
    
    # Verificar el resultado
    assert "id" in decision_tree
    assert "type" in decision_tree
    assert "children" in decision_tree
    assert len(decision_tree["children"]) > 0

@pytest.mark.asyncio
async def test_determine_next_actions(decision_engine_service):
    """Prueba la determinación de las próximas acciones óptimas."""
    # Crear un árbol de decisión de prueba
    decision_tree = {
        "id": str(uuid.uuid4()),
        "type": "root",
        "description": "Punto de inicio de decisión",
        "children": [
            {
                "id": str(uuid.uuid4()),
                "type": "objection_handling",
                "description": "Manejar objeción: price",
                "confidence": 0.75,
                "score": 0.8,
                "children": [
                    {
                        "id": str(uuid.uuid4()),
                        "type": "response",
                        "description": "Respuesta 1",
                        "content": "Entiendo su preocupación por el precio...",
                        "score": 0.9
                    }
                ]
            },
            {
                "id": str(uuid.uuid4()),
                "type": "need_satisfaction",
                "description": "Satisfacer necesidad: pricing",
                "confidence": 0.85,
                "score": 0.85,
                "children": [
                    {
                        "id": str(uuid.uuid4()),
                        "type": "action",
                        "description": "Compartir lista de precios",
                        "action_type": "content",
                        "priority": "high",
                        "score": 0.9
                    }
                ]
            }
        ]
    }
    
    # Ejecutar la función a probar
    next_actions, confidence = await decision_engine_service._determine_next_actions(
        decision_tree=decision_tree,
        objective_weights={"need_satisfaction": 0.35, "objection_handling": 0.25, "conversion_progress": 0.4},
        min_confidence=0.6
    )
    
    # Verificar el resultado
    assert len(next_actions) > 0
    assert 0 <= confidence <= 1
    
    # Verificar estructura de acciones
    for action in next_actions:
        assert "id" in action
        assert "type" in action
        assert "description" in action
        assert "score" in action

@pytest.mark.asyncio
async def test_adapt_strategy_realtime(decision_engine_service):
    """Prueba la adaptación de estrategia en tiempo real."""
    # Crear una estrategia actual
    current_strategy = {
        "next_actions": [
            {
                "id": str(uuid.uuid4()),
                "type": "response",
                "action_category": "objection_response",
                "description": "Respuesta a objeción de precio",
                "content": "Entiendo su preocupación por el precio...",
                "score": 0.7
            }
        ],
        "decision_tree": {
            "id": str(uuid.uuid4()),
            "type": "root",
            "children": []
        },
        "objectives": {
            "need_satisfaction": 0.35,
            "objection_handling": 0.25,
            "conversion_progress": 0.4
        },
        "confidence": 0.7
    }
    
    # Crear feedback negativo
    feedback = {
        "success": False,
        "type": "objection_not_addressed",
        "details": "El cliente sigue preocupado por el precio"
    }
    
    # Ejecutar la función a probar
    result = await decision_engine_service.adapt_strategy_realtime(
        conversation_id=MOCK_CONVERSATION_ID,
        messages=MOCK_MESSAGES,
        current_strategy=current_strategy,
        feedback=feedback,
        customer_profile=MOCK_CUSTOMER_PROFILE
    )
    
    # Verificar el resultado
    assert "next_actions" in result
    assert "decision_tree" in result
    assert "objectives" in result
    assert "confidence" in result
    assert "adapted" in result
    assert result["adapted"] is True

@pytest.mark.asyncio
async def test_prioritize_objectives(decision_engine_service):
    """Prueba la priorización de objetivos de conversación."""
    # Ejecutar la función a probar
    result = await decision_engine_service.prioritize_objectives(
        conversation_id=MOCK_CONVERSATION_ID,
        messages=MOCK_MESSAGES,
        customer_profile=MOCK_CUSTOMER_PROFILE
    )
    
    # Verificar el resultado
    assert "need_satisfaction" in result
    assert "objection_handling" in result
    assert "conversion_progress" in result
    
    # Verificar que los pesos sumen aproximadamente 1
    total_weight = sum(result.values())
    assert 0.99 <= total_weight <= 1.01

@pytest.mark.asyncio
async def test_evaluate_conversation_path(decision_engine_service):
    """Prueba la evaluación de una ruta de conversación específica."""
    # Crear acciones de ruta
    path_actions = [
        {
            "id": str(uuid.uuid4()),
            "action_category": "objection_response",
            "objection_type": "price",
            "description": "Respuesta a objeción de precio",
            "content": "Entiendo su preocupación por el precio..."
        },
        {
            "id": str(uuid.uuid4()),
            "action_category": "need_satisfaction",
            "need_category": "pricing",
            "description": "Compartir lista de precios",
            "content": "Aquí tiene nuestra lista de precios..."
        }
    ]
    
    # Ejecutar la función a probar
    result = await decision_engine_service.evaluate_conversation_path(
        conversation_id=MOCK_CONVERSATION_ID,
        messages=MOCK_MESSAGES,
        path_actions=path_actions,
        customer_profile=MOCK_CUSTOMER_PROFILE
    )
    
    # Verificar el resultado
    assert "effectiveness" in result
    assert "metrics" in result
    assert "recommendations" in result
    
    # Verificar que la efectividad esté en el rango correcto
    assert 0 <= result["effectiveness"] <= 1
    
    # Verificar métricas específicas
    assert "conversion_probability" in result["metrics"]
    assert "objections_addressed" in result["metrics"]
    assert "needs_satisfied" in result["metrics"]
