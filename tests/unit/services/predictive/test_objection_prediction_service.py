"""
Pruebas unitarias para el servicio de predicción de objeciones.

Este módulo contiene pruebas para verificar el correcto funcionamiento
del servicio de predicción de objeciones.
"""

import pytest
from unittest.mock import patch, MagicMock
import json
from datetime import datetime

from src.services.objection_prediction_service import ObjectionPredictionService

class TestObjectionPredictionService:
    """Pruebas para el servicio de predicción de objeciones."""
    
    def setup_method(self):
        """Configuración para cada prueba."""
        # Crear una instancia del servicio
        self.service = ObjectionPredictionService()
        
        # Mock para la base de datos
        self.db_mock = MagicMock()
        self.service.db = self.db_mock
        
        # Mock para el modelo
        self.model_mock = MagicMock()
        self.service.model = self.model_mock
    
    def test_init(self):
        """Prueba la inicialización del servicio."""
        # Verificar atributos
        assert self.service.model_name == "objection_prediction"
        assert self.service.model_version == "1.0.0"
        assert hasattr(self.service, "objection_categories")
        assert len(self.service.objection_categories) > 0
    
    def test_preprocess_conversation(self):
        """Prueba el preprocesamiento de una conversación."""
        # Datos de prueba
        conversation = {
            "conversation_id": "test_conversation",
            "messages": [
                {"role": "user", "content": "No estoy seguro de que esto sea lo que necesito."},
                {"role": "assistant", "content": "Entiendo su preocupación. ¿Qué aspectos le generan dudas?"},
                {"role": "user", "content": "El precio es muy alto para mí."}
            ]
        }
        
        # Preprocesar conversación
        features = self.service.preprocess_conversation(conversation)
        
        # Verificar características extraídas
        assert "text" in features
        assert "message_count" in features
        assert "user_message_count" in features
        assert features["message_count"] == 3
        assert features["user_message_count"] == 2
        assert "precio" in features["text"].lower()
        assert "alto" in features["text"].lower()
    
    def test_predict(self):
        """Prueba la predicción de objeciones."""
        # Datos de prueba
        conversation = {
            "conversation_id": "test_conversation",
            "messages": [
                {"role": "user", "content": "El precio es muy alto para mí."}
            ]
        }
        
        # Mock para el preprocesamiento
        with patch.object(self.service, "preprocess_conversation") as preprocess_mock:
            preprocess_mock.return_value = {"text": "El precio es muy alto para mí.", "message_count": 1}
            
            # Mock para la predicción del modelo
            self.model_mock.predict_proba.return_value = [[0.1, 0.7, 0.2]]
            self.service.objection_categories = ["product", "price", "service"]
            
            # Realizar predicción
            result = self.service.predict(conversation)
            
            # Verificar resultado
            assert "objections" in result
            assert len(result["objections"]) > 0
            assert result["objections"][0]["category"] == "price"
            assert result["objections"][0]["probability"] > 0.6
            assert "top_objections" in result
            assert len(result["top_objections"]) > 0
            
            # Verificar que se llamó al preprocesamiento
            preprocess_mock.assert_called_once_with(conversation)
            
            # Verificar que se llamó al modelo
            self.model_mock.predict_proba.assert_called_once()
            
            # Verificar que se almacenó la predicción
            with patch.object(self.service, "store_prediction") as store_mock:
                self.service.predict(conversation)
                store_mock.assert_called_once()
    
    def test_train(self):
        """Prueba el entrenamiento del modelo."""
        # Datos de prueba
        X = [
            {"text": "El precio es muy alto.", "message_count": 2},
            {"text": "No me gusta el producto.", "message_count": 3},
            {"text": "El servicio es lento.", "message_count": 1}
        ]
        y = ["price", "product", "service"]
        
        # Mock para el modelo
        model_class_mock = MagicMock()
        model_instance_mock = MagicMock()
        model_class_mock.return_value = model_instance_mock
        
        with patch("sklearn.pipeline.Pipeline", model_class_mock):
            # Entrenar modelo
            self.service.train(X, y)
            
            # Verificar que se creó el modelo
            model_class_mock.assert_called_once()
            
            # Verificar que se entrenó el modelo
            model_instance_mock.fit.assert_called_once()
            
            # Verificar que se registró el modelo
            assert self.service.model == model_instance_mock
            
            # Verificar que se guardaron las categorías
            assert set(self.service.objection_categories) == set(y)
    
    def test_get_objection_details(self):
        """Prueba la obtención de detalles de objeciones."""
        # Configurar categorías de objeciones
        self.service.objection_categories = ["price", "product", "service"]
        
        # Obtener detalles para la categoría "price"
        details = self.service.get_objection_details("price")
        
        # Verificar detalles
        assert "description" in details
        assert "examples" in details
        assert "responses" in details
        assert len(details["examples"]) > 0
        assert len(details["responses"]) > 0
    
    def test_get_response_suggestions(self):
        """Prueba la obtención de sugerencias de respuesta."""
        # Datos de prueba
        objections = [
            {"category": "price", "probability": 0.7},
            {"category": "product", "probability": 0.2}
        ]
        
        # Mock para obtener detalles
        with patch.object(self.service, "get_objection_details") as details_mock:
            details_mock.return_value = {
                "responses": ["Entiendo su preocupación por el precio.", "Podemos ofrecerle opciones de financiamiento."]
            }
            
            # Obtener sugerencias
            suggestions = self.service.get_response_suggestions(objections)
            
            # Verificar sugerencias
            assert len(suggestions) > 0
            assert suggestions[0]["objection_category"] == "price"
            assert len(suggestions[0]["responses"]) == 2
            
            # Verificar que se llamó a get_objection_details
            details_mock.assert_called_with("price")
