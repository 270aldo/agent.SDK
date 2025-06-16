"""
Pruebas unitarias para el servicio de predicción de necesidades.

Este módulo contiene pruebas para verificar el correcto funcionamiento
del servicio de predicción de necesidades.
"""

import pytest
from unittest.mock import patch, MagicMock
import json
from datetime import datetime

from src.services.needs_prediction_service import NeedsPredictionService

class TestNeedsPredictionService:
    """Pruebas para el servicio de predicción de necesidades."""
    
    def setup_method(self):
        """Configuración para cada prueba."""
        # Crear una instancia del servicio
        self.service = NeedsPredictionService()
        
        # Mock para la base de datos
        self.db_mock = MagicMock()
        self.service.db = self.db_mock
        
        # Mock para el modelo
        self.model_mock = MagicMock()
        self.service.model = self.model_mock
    
    def test_init(self):
        """Prueba la inicialización del servicio."""
        # Verificar atributos
        assert self.service.model_name == "needs_prediction"
        assert self.service.model_version == "1.0.0"
        assert hasattr(self.service, "need_categories")
        assert len(self.service.need_categories) > 0
    
    def test_preprocess_conversation(self):
        """Prueba el preprocesamiento de una conversación."""
        # Datos de prueba
        conversation = {
            "conversation_id": "test_conversation",
            "messages": [
                {"role": "user", "content": "Necesito algo que me ayude a organizar mi tiempo."},
                {"role": "assistant", "content": "Entiendo. ¿Qué tipo de actividades necesita organizar?"},
                {"role": "user", "content": "Principalmente reuniones y tareas diarias."}
            ],
            "user_profile": {
                "industry": "tecnología",
                "role": "gerente",
                "company_size": "mediana"
            }
        }
        
        # Preprocesar conversación
        features = self.service.preprocess_conversation(conversation)
        
        # Verificar características extraídas
        assert "text" in features
        assert "message_count" in features
        assert "user_profile" in features
        assert features["message_count"] == 3
        assert "organizar" in features["text"].lower()
        assert "tiempo" in features["text"].lower()
        assert features["user_profile"]["industry"] == "tecnología"
    
    def test_predict(self):
        """Prueba la predicción de necesidades."""
        # Datos de prueba
        conversation = {
            "conversation_id": "test_conversation",
            "messages": [
                {"role": "user", "content": "Necesito algo que me ayude a organizar mi tiempo."}
            ],
            "user_profile": {
                "industry": "tecnología",
                "role": "gerente"
            }
        }
        
        # Mock para el preprocesamiento
        with patch.object(self.service, "preprocess_conversation") as preprocess_mock:
            preprocess_mock.return_value = {
                "text": "Necesito algo que me ayude a organizar mi tiempo.",
                "message_count": 1,
                "user_profile": {"industry": "tecnología", "role": "gerente"}
            }
            
            # Mock para la predicción del modelo
            self.model_mock.predict_proba.return_value = [[0.2, 0.6, 0.2]]
            self.service.need_categories = ["eficiencia", "organización", "colaboración"]
            
            # Realizar predicción
            result = self.service.predict(conversation)
            
            # Verificar resultado
            assert "needs" in result
            assert len(result["needs"]) > 0
            assert result["needs"][0]["category"] == "organización"
            assert result["needs"][0]["probability"] > 0.5
            assert "top_needs" in result
            assert len(result["top_needs"]) > 0
            
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
            {
                "text": "Necesito organizar mejor mi tiempo.",
                "message_count": 2,
                "user_profile": {"industry": "tecnología", "role": "gerente"}
            },
            {
                "text": "Quiero mejorar la eficiencia de mi equipo.",
                "message_count": 3,
                "user_profile": {"industry": "finanzas", "role": "director"}
            },
            {
                "text": "Necesitamos herramientas de colaboración.",
                "message_count": 1,
                "user_profile": {"industry": "educación", "role": "profesor"}
            }
        ]
        y = ["organización", "eficiencia", "colaboración"]
        
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
            assert set(self.service.need_categories) == set(y)
    
    def test_get_need_details(self):
        """Prueba la obtención de detalles de necesidades."""
        # Configurar categorías de necesidades
        self.service.need_categories = ["organización", "eficiencia", "colaboración"]
        
        # Obtener detalles para la categoría "organización"
        details = self.service.get_need_details("organización")
        
        # Verificar detalles
        assert "description" in details
        assert "examples" in details
        assert "solutions" in details
        assert len(details["examples"]) > 0
        assert len(details["solutions"]) > 0
    
    def test_get_solution_suggestions(self):
        """Prueba la obtención de sugerencias de solución."""
        # Datos de prueba
        needs = [
            {"category": "organización", "probability": 0.6},
            {"category": "eficiencia", "probability": 0.3}
        ]
        
        # Mock para obtener detalles
        with patch.object(self.service, "get_need_details") as details_mock:
            details_mock.return_value = {
                "solutions": [
                    {"name": "Calendario compartido", "description": "Herramienta para organizar reuniones y eventos."},
                    {"name": "Gestor de tareas", "description": "Aplicación para gestionar tareas y proyectos."}
                ]
            }
            
            # Obtener sugerencias
            suggestions = self.service.get_solution_suggestions(needs)
            
            # Verificar sugerencias
            assert len(suggestions) > 0
            assert suggestions[0]["need_category"] == "organización"
            assert len(suggestions[0]["solutions"]) == 2
            assert suggestions[0]["solutions"][0]["name"] == "Calendario compartido"
            
            # Verificar que se llamó a get_need_details
            details_mock.assert_called_with("organización")
    
    def test_analyze_user_profile(self):
        """Prueba el análisis del perfil de usuario."""
        # Datos de prueba
        user_profile = {
            "industry": "tecnología",
            "role": "gerente",
            "company_size": "mediana"
        }
        
        # Analizar perfil
        profile_features = self.service.analyze_user_profile(user_profile)
        
        # Verificar características extraídas
        assert "industry" in profile_features
        assert "role" in profile_features
        assert "company_size" in profile_features
        assert profile_features["industry"] == "tecnología"
        assert profile_features["role"] == "gerente"
        assert profile_features["company_size"] == "mediana"
    
    def test_get_personalized_recommendations(self):
        """Prueba la obtención de recomendaciones personalizadas."""
        # Datos de prueba
        needs = [
            {"category": "organización", "probability": 0.6},
            {"category": "eficiencia", "probability": 0.3}
        ]
        user_profile = {
            "industry": "tecnología",
            "role": "gerente",
            "company_size": "mediana"
        }
        
        # Mock para obtener sugerencias de solución
        with patch.object(self.service, "get_solution_suggestions") as suggestions_mock:
            suggestions_mock.return_value = [
                {
                    "need_category": "organización",
                    "solutions": [
                        {"name": "Calendario compartido", "description": "Herramienta para organizar reuniones y eventos."},
                        {"name": "Gestor de tareas", "description": "Aplicación para gestionar tareas y proyectos."}
                    ]
                }
            ]
            
            # Obtener recomendaciones
            recommendations = self.service.get_personalized_recommendations(needs, user_profile)
            
            # Verificar recomendaciones
            assert len(recommendations) > 0
            assert "industry_specific" in recommendations
            assert "role_specific" in recommendations
            assert len(recommendations["industry_specific"]) > 0
            assert len(recommendations["role_specific"]) > 0
            
            # Verificar que se llamó a get_solution_suggestions
            suggestions_mock.assert_called_once_with(needs)
