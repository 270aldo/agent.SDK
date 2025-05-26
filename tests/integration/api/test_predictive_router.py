"""
Pruebas de integración para el router predictivo.

Este módulo contiene pruebas para verificar el correcto funcionamiento
de los endpoints predictivos, incluyendo la autenticación y validación de datos.
"""

import pytest
import json
from datetime import datetime
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

class TestPredictiveRouter:
    """Pruebas para el router predictivo."""
    
    def test_predict_objections_authenticated(self, client, auth_headers):
        """Prueba la predicción de objeciones con usuario autenticado."""
        # Datos para la solicitud
        request_data = {
            "conversation_id": "test_conv_1",
            "messages": [
                {
                    "role": "user",
                    "content": "Me parece que el precio es muy alto para lo que ofrece.",
                    "timestamp": datetime.utcnow().isoformat()
                },
                {
                    "role": "assistant",
                    "content": "Entiendo su preocupación por el precio. ¿Podría decirme más sobre qué características son importantes para usted?",
                    "timestamp": datetime.utcnow().isoformat()
                }
            ],
            "customer_profile": {
                "id": "customer_123",
                "demographics": {
                    "age": 35,
                    "industry": "tecnología"
                }
            }
        }
        
        # Realizar solicitud
        response = client.post(
            "/predictive/objection/predict",
            json=request_data,
            headers=auth_headers
        )
        
        # Verificar respuesta
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert "data" in response.json()
        assert "predictions" in response.json()["data"]
        assert "prediction_id" in response.json()["data"]
    
    def test_predict_objections_unauthenticated(self, client):
        """Prueba la predicción de objeciones sin autenticación."""
        # Datos para la solicitud
        request_data = {
            "conversation_id": "test_conv_1",
            "messages": [
                {
                    "role": "user",
                    "content": "Me parece que el precio es muy alto para lo que ofrece.",
                    "timestamp": datetime.utcnow().isoformat()
                }
            ]
        }
        
        # Realizar solicitud sin token
        response = client.post(
            "/predictive/objection/predict",
            json=request_data
        )
        
        # Verificar respuesta de error
        assert response.status_code == 401
        assert response.json()["success"] is False
        assert "error" in response.json()
        assert "code" in response.json()["error"]
        assert response.json()["error"]["code"] == "UNAUTHORIZED"
    
    def test_predict_objections_invalid_data(self, client, auth_headers):
        """Prueba la predicción de objeciones con datos inválidos."""
        # Datos inválidos para la solicitud (falta timestamp)
        request_data = {
            "conversation_id": "test_conv_1",
            "messages": [
                {
                    "role": "user",
                    "content": "Me parece que el precio es muy alto para lo que ofrece."
                    # Falta timestamp
                }
            ]
        }
        
        # Realizar solicitud
        response = client.post(
            "/predictive/objection/predict",
            json=request_data,
            headers=auth_headers
        )
        
        # Verificar respuesta de error de validación
        assert response.status_code == 422
        assert response.json()["success"] is False
        assert "error" in response.json()
        assert "code" in response.json()["error"]
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"
    
    def test_record_objection_with_permission(self, client, admin_headers):
        """Prueba el registro de objeciones con permisos adecuados."""
        # Datos para la solicitud
        request_data = {
            "conversation_id": "test_conv_1",
            "objection_type": "price",
            "objection_text": "El precio es demasiado alto para mi presupuesto."
        }
        
        # Realizar solicitud
        response = client.post(
            "/predictive/objection/record",
            json=request_data,
            headers=admin_headers
        )
        
        # Verificar respuesta
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert "data" in response.json()
        assert "record_id" in response.json()["data"]
    
    def test_record_objection_without_permission(self, client, auth_headers):
        """Prueba el registro de objeciones sin permisos adecuados."""
        # Datos para la solicitud
        request_data = {
            "conversation_id": "test_conv_1",
            "objection_type": "price",
            "objection_text": "El precio es demasiado alto para mi presupuesto."
        }
        
        # Realizar solicitud con usuario sin permisos
        response = client.post(
            "/predictive/objection/record",
            json=request_data,
            headers=auth_headers
        )
        
        # Verificar respuesta de error
        assert response.status_code == 403
        assert response.json()["success"] is False
        assert "error" in response.json()
        assert "code" in response.json()["error"]
        assert response.json()["error"]["code"] == "FORBIDDEN"
    
    def test_predict_needs_authenticated(self, client, auth_headers):
        """Prueba la predicción de necesidades con usuario autenticado."""
        # Datos para la solicitud
        request_data = {
            "conversation_id": "test_conv_2",
            "messages": [
                {
                    "role": "user",
                    "content": "Necesito una solución que se integre con nuestro CRM actual.",
                    "timestamp": datetime.utcnow().isoformat()
                },
                {
                    "role": "assistant",
                    "content": "Entiendo. ¿Qué CRM están utilizando actualmente?",
                    "timestamp": datetime.utcnow().isoformat()
                }
            ],
            "customer_profile": {
                "id": "customer_456",
                "demographics": {
                    "industry": "retail"
                }
            }
        }
        
        # Realizar solicitud
        response = client.post(
            "/predictive/needs/predict",
            json=request_data,
            headers=auth_headers
        )
        
        # Verificar respuesta
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert "data" in response.json()
        assert "predictions" in response.json()["data"]
        assert "prediction_id" in response.json()["data"]
    
    def test_optimize_flow_authenticated(self, client, auth_headers):
        """Prueba la optimización de flujo de conversación con usuario autenticado."""
        # Datos para la solicitud
        request_data = {
            "conversation_id": "test_conv_3",
            "messages": [
                {
                    "role": "user",
                    "content": "Estoy interesado en su producto pero tengo algunas dudas.",
                    "timestamp": datetime.utcnow().isoformat()
                },
                {
                    "role": "assistant",
                    "content": "Claro, estaré encantado de resolver sus dudas. ¿Qué le gustaría saber?",
                    "timestamp": datetime.utcnow().isoformat()
                }
            ],
            "current_objectives": {
                "conversion": 0.6,
                "satisfaction": 0.4
            }
        }
        
        # Realizar solicitud
        response = client.post(
            "/predictive/decision/optimize-flow",
            json=request_data,
            headers=auth_headers
        )
        
        # Verificar respuesta
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert "data" in response.json()
        assert "optimized_flow" in response.json()["data"]
    
    def test_submit_feedback_authenticated(self, client, auth_headers):
        """Prueba el envío de retroalimentación con usuario autenticado."""
        # Datos para la solicitud
        request_data = {
            "conversation_id": "test_conv_1",
            "model_type": "objection",
            "prediction_id": "pred_123",
            "feedback_rating": 0.8,
            "feedback_details": {
                "comment": "La predicción fue bastante precisa"
            }
        }
        
        # Realizar solicitud
        response = client.post(
            "/predictive/feedback",
            json=request_data,
            headers=auth_headers
        )
        
        # Verificar respuesta
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert "data" in response.json()
        assert "feedback_id" in response.json()["data"]
