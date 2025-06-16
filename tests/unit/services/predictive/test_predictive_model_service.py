"""
Pruebas unitarias para el servicio base de modelos predictivos.

Este módulo contiene pruebas para verificar el correcto funcionamiento
del servicio base de modelos predictivos.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import json
import numpy as np
from datetime import datetime

from src.services.predictive_model_service import PredictiveModelService
from src.integrations.supabase.resilient_client import ResilientSupabaseClient

class TestPredictiveModelService:
    """Pruebas para el servicio base de modelos predictivos."""
    
    def setup_method(self):
        """Configuración para cada prueba."""
        # Mock para el cliente de Supabase
        self.supabase_mock = MagicMock(spec=ResilientSupabaseClient)
        self.table_mock = MagicMock()
        self.supabase_mock.table.return_value = self.table_mock
        self.select_mock = MagicMock()
        self.table_mock.select.return_value = self.select_mock
        self.execute_mock = AsyncMock()
        self.select_mock.execute = self.execute_mock
        self.select_mock.eq.return_value = self.select_mock
        self.select_mock.limit.return_value = self.select_mock
        self.insert_mock = MagicMock()
        self.table_mock.insert.return_value = self.insert_mock
        self.insert_mock.execute = AsyncMock()
        self.update_mock = MagicMock()
        self.table_mock.update.return_value = self.update_mock
        self.update_mock.eq.return_value = self.update_mock
        self.update_mock.execute = AsyncMock()
        
        # Crear una instancia del servicio
        self.service = PredictiveModelService(self.supabase_mock)
    
    def test_init(self):
        """Prueba la inicialización del servicio."""
        # Verificar atributos
        assert hasattr(self.service, "supabase")
        assert self.service.supabase == self.supabase_mock
        
        # Verificar que se llamó a _initialize_tables
        self.supabase_mock.table.assert_called()
    
    @pytest.mark.asyncio
    async def test_register_model(self):
        """Prueba el registro de un modelo."""
        # Datos de prueba
        model_name = "test_model"
        model_type = "objection"
        model_params = {"param1": "value1", "param2": "value2"}
        description = "Modelo de prueba"
        
        # Configurar mock para el resultado
        self.insert_mock.execute.return_value.data = [{"id": "123", "name": model_name}]
        
        # Registrar modelo
        result = await self.service.register_model(model_name, model_type, model_params, description)
        
        # Verificar que se llamó a la base de datos correctamente
        self.supabase_mock.table.assert_called_with("predictive_models")
        self.table_mock.insert.assert_called_once()
        
        # Verificar datos de registro
        insert_data = self.table_mock.insert.call_args[0][0]
        assert insert_data["name"] == model_name
        assert insert_data["type"] == model_type
        assert insert_data["parameters"] == json.dumps(model_params)
        assert insert_data["description"] == description
        assert "created_at" in insert_data
        
        # Verificar resultado
        assert result["id"] == "123"
        assert result["name"] == model_name
    
    @pytest.mark.asyncio
    async def test_get_model(self):
        """Prueba la obtención de información de un modelo."""
        # Datos de prueba
        model_name = "test_model"
        model_data = {"id": "123", "name": model_name, "type": "objection"}
        
        # Configurar mock para el resultado
        self.execute_mock.return_value.data = [model_data]
        
        # Obtener modelo
        result = await self.service.get_model(model_name)
        
        # Verificar que se llamó a la base de datos correctamente
        self.supabase_mock.table.assert_called_with("predictive_models")
        self.table_mock.select.assert_called_with("*")
        self.select_mock.eq.assert_called_with("name", model_name)
        
        # Verificar resultado
        assert result == model_data
    
    @pytest.mark.asyncio
    async def test_list_models(self):
        """Prueba el listado de modelos."""
        # Datos de prueba
        models = [
            {"id": "123", "name": "model1", "type": "objection"},
            {"id": "456", "name": "model2", "type": "needs"}
        ]
        
        # Configurar mock para el resultado
        self.execute_mock.return_value.data = models
        
        # Listar modelos
        result = await self.service.list_models()
        
        # Verificar que se llamó a la base de datos correctamente
        self.supabase_mock.table.assert_called_with("predictive_models")
        self.table_mock.select.assert_called_with("*")
        
        # Verificar resultado
        assert result == models
        
        # Probar con filtro de tipo
        await self.service.list_models("objection")
        self.select_mock.eq.assert_called_with("type", "objection")
    
    @pytest.mark.asyncio
    async def test_store_prediction(self):
        """Prueba el almacenamiento de una predicción."""
        # Datos de prueba
        model_name = "test_model"
        conversation_id = "test_conversation"
        prediction_type = "objection"
        prediction_data = {"prediction": "test_prediction", "confidence": 0.9}
        confidence = 0.9
        
        # Configurar mock para el resultado
        self.insert_mock.execute.return_value.data = [{"id": "123"}]
        
        # Almacenar predicción
        result = await self.service.store_prediction(model_name, conversation_id, prediction_type, prediction_data, confidence)
        
        # Verificar que se llamó a la base de datos correctamente
        self.supabase_mock.table.assert_called_with("prediction_results")
        self.table_mock.insert.assert_called_once()
        
        # Verificar datos de almacenamiento
        insert_data = self.table_mock.insert.call_args[0][0]
        assert insert_data["model_name"] == model_name
        assert insert_data["conversation_id"] == conversation_id
        assert insert_data["prediction_type"] == prediction_type
        assert insert_data["prediction_data"] == json.dumps(prediction_data)
        assert insert_data["confidence"] == confidence
        assert "created_at" in insert_data
    
    @pytest.mark.asyncio
    async def test_update_prediction_result(self):
        """Prueba la actualización del resultado de una predicción."""
        # Datos de prueba
        prediction_id = "123"
        actual_result = {"actual": "value"}
        was_correct = True
        
        # Configurar mock para el resultado
        self.update_mock.execute.return_value.data = [{"id": prediction_id}]
        
        # Actualizar resultado
        result = await self.service.update_prediction_result(prediction_id, actual_result, was_correct)
        
        # Verificar que se llamó a la base de datos correctamente
        self.supabase_mock.table.assert_called_with("prediction_results")
        self.table_mock.update.assert_called_once()
        self.update_mock.eq.assert_called_with("id", prediction_id)
        
        # Verificar datos de actualización
        update_data = self.table_mock.update.call_args[0][0]
        assert update_data["actual_result"] == json.dumps(actual_result)
        assert update_data["was_correct"] == was_correct
        assert "updated_at" in update_data
    
    @pytest.mark.asyncio
    async def test_get_training_data(self):
        """Prueba la obtención de datos de entrenamiento."""
        # Datos de prueba
        model_name = "test_model"
        training_data = [
            {"id": "1", "model_name": model_name, "features": json.dumps({"feature1": 1}), "label": "A"},
            {"id": "2", "model_name": model_name, "features": json.dumps({"feature1": 2}), "label": "B"}
        ]
        
        # Configurar mock para el resultado
        self.execute_mock.return_value.data = training_data
        
        # Obtener datos de entrenamiento
        result = await self.service.get_training_data(model_name)
        
        # Verificar que se llamó a la base de datos correctamente
        self.supabase_mock.table.assert_called_with("model_training_data")
        self.table_mock.select.assert_called_with("*")
        self.select_mock.eq.assert_called_with("model_name", model_name)
        self.select_mock.limit.assert_called_with(1000)
        
        # Verificar resultado
        assert result == training_data
    
    @pytest.mark.asyncio
    async def test_calculate_confidence_score(self):
        """Prueba el cálculo de la puntuación de confianza."""
        # Datos de prueba
        prediction_scores = {"A": 0.7, "B": 0.2, "C": 0.1}
        
        # Calcular puntuación
        prediction, confidence = await self.service.calculate_confidence_score(prediction_scores)
        
        # Verificar resultado
        assert prediction == "A"
        assert confidence > 0.5  # La confianza debe ser alta para la predicción A
        
        # Probar con un diccionario vacío
        prediction, confidence = await self.service.calculate_confidence_score({})
        assert prediction == ""
        assert confidence == 0.0
    
    @pytest.mark.asyncio
    async def test_store_feedback(self):
        """Prueba el almacenamiento de retroalimentación."""
        # Datos de prueba
        prediction_id = "123"
        feedback_type = "useful"
        feedback_data = {"comment": "Muy útil"}
        user_id = "user123"
        
        # Configurar mock para el resultado
        self.insert_mock.execute.return_value.data = [{"id": "456"}]
        
        # Almacenar retroalimentación
        result = await self.service.store_feedback(prediction_id, feedback_type, feedback_data, user_id)
        
        # Verificar que se llamó a la base de datos correctamente
        self.supabase_mock.table.assert_called_with("prediction_feedback")
        self.table_mock.insert.assert_called_once()
        
        # Verificar datos de almacenamiento
        insert_data = self.table_mock.insert.call_args[0][0]
        assert insert_data["prediction_id"] == prediction_id
        assert insert_data["feedback_type"] == feedback_type
        assert insert_data["feedback_data"] == json.dumps(feedback_data)
        assert insert_data["user_id"] == user_id
        assert "created_at" in insert_data
