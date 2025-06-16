"""
Servicio Base para Modelos Predictivos de NGX Voice Sales Agent.

Este servicio proporciona la base para todos los servicios predictivos específicos,
implementando funcionalidades comunes y reduciendo la duplicación de código.
"""

from typing import Dict, List, Any, Optional, Tuple
import logging
import json
from datetime import datetime

from src.integrations.supabase.resilient_client import ResilientSupabaseClient
from src.services.predictive_model_service import PredictiveModelService
from src.services.nlp_integration_service import NLPIntegrationService

logger = logging.getLogger(__name__)

class BasePredictiveService:
    """
    Clase base para servicios predictivos específicos.
    
    Esta clase implementa funcionalidades comunes a todos los servicios predictivos
    como inicialización de modelos, almacenamiento de predicciones y estadísticas.
    """
    
    def __init__(self, 
                 supabase: ResilientSupabaseClient,
                 predictive_model_service: PredictiveModelService,
                 nlp_integration_service: NLPIntegrationService,
                 model_name: str,
                 model_type: str):
        """
        Inicializa el servicio base para modelos predictivos.

        Args:
            supabase: Cliente de Supabase para la conexión a la base de datos.
            predictive_model_service: Instancia del servicio de modelos predictivos.
            nlp_integration_service: Instancia del servicio de integración de NLP.
            model_name: Nombre del modelo.
            model_type: Tipo de modelo (ej. 'needs_prediction', 'objection_prediction').
        """
        if not supabase or not predictive_model_service or not nlp_integration_service:
            raise ValueError("Todos los servicios y el cliente de Supabase son requeridos.")

        self.supabase = supabase
        self.predictive_model_service = predictive_model_service
        self.nlp_service = nlp_integration_service
        self.model_name = model_name
        self.model_type = model_type
        
    async def initialize_model(self, model_params: Dict[str, Any], description: str) -> None:
        """
        Inicializa el modelo predictivo.
        
        Args:
            model_params: Parámetros del modelo
            description: Descripción del modelo
        """
        try:
            # Verificar si el modelo ya existe
            model = await self.predictive_model_service.get_model(self.model_name)
            
            if not model:
                # Crear modelo si no existe
                await self.predictive_model_service.register_model(
                    model_name=self.model_name,
                    model_type=self.model_type,
                    model_params=model_params,
                    description=description
                )
                logger.info(f"Modelo predictivo inicializado: {self.model_name}")
            
        except Exception as e:
            logger.error(f"Error al inicializar modelo predictivo: {e}")
            
    async def store_prediction(self, 
                        conversation_id: str, 
                        prediction_type: str,
                        prediction_data: Dict[str, Any],
                        confidence: float) -> Dict[str, Any]:
        """
        Almacena una predicción realizada por el modelo.
        
        Args:
            conversation_id: ID de la conversación
            prediction_type: Tipo de predicción
            prediction_data: Datos de la predicción
            confidence: Nivel de confianza
            
        Returns:
            Información de la predicción almacenada
        """
        try:
            result = await self.predictive_model_service.store_prediction(
                model_name=self.model_name,
                conversation_id=conversation_id,
                prediction_type=prediction_type,
                prediction_data=prediction_data,
                confidence=confidence
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error al almacenar predicción: {e}")
            return {}
            
    async def record_actual_result(self, 
                           conversation_id: str,
                           actual_result: Dict[str, Any],
                           was_correct: bool) -> Dict[str, Any]:
        """
        Registra el resultado real para una predicción.
        
        Args:
            conversation_id: ID de la conversación
            actual_result: Resultado real observado
            was_correct: Indica si la predicción fue correcta
            
        Returns:
            Información actualizada de la predicción
        """
        try:
            # Buscar la predicción más reciente para esta conversación
            query = self.supabase.table("prediction_results").select("*").eq("model_name", self.model_name).eq("conversation_id", conversation_id).order("created_at", {"ascending": False}).limit(1).execute()
            
            if not query.data:
                logger.warning(f"No se encontraron predicciones previas para la conversación: {conversation_id}")
                return {}
            
            prediction = query.data[0]
            prediction_id = prediction["id"]
            
            # Registrar el resultado real
            result = await self.predictive_model_service.update_prediction_result(
                prediction_id=prediction_id,
                actual_result=actual_result,
                was_correct=was_correct
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error al registrar resultado real: {e}")
            return {}
            
    async def get_statistics(self, time_period: Optional[int] = None) -> Dict[str, Any]:
        """
        Obtiene estadísticas sobre predicciones realizadas.
        
        Args:
            time_period: Período de tiempo en días (opcional)
            
        Returns:
            Estadísticas de predicciones
        """
        try:
            # Obtener precisión del modelo
            accuracy_stats = await self.predictive_model_service.get_model_accuracy(
                model_name=self.model_name,
                time_period=time_period
            )
            
            # Obtener todas las predicciones
            query = self.supabase.table("prediction_results").select("*").eq("model_name", self.model_name).eq("status", "completed").execute()
            
            if not query.data:
                return {
                    "accuracy": accuracy_stats,
                    "total_predictions": 0,
                    "distribution": {}
                }
            
            # Estadísticas básicas
            total_predictions = len(query.data)
            
            # Estadísticas específicas según el tipo de modelo
            # Las clases derivadas pueden sobrescribir este método para añadir estadísticas específicas
            
            return {
                "accuracy": accuracy_stats,
                "total_predictions": total_predictions
            }
            
        except Exception as e:
            logger.error(f"Error al obtener estadísticas: {e}")
            return {
                "accuracy": {"accuracy": 0, "total_predictions": 0},
                "total_predictions": 0
            }
            
    async def add_training_data(self, 
                         features: Dict[str, Any], 
                         label: Any) -> Dict[str, Any]:
        """
        Añade datos para entrenamiento futuro del modelo.
        
        Args:
            features: Características de entrada
            label: Etiqueta o resultado esperado
            
        Returns:
            Información del dato de entrenamiento añadido
        """
        try:
            result = await self.predictive_model_service.add_training_data(
                model_name=self.model_name,
                data_type=self.model_type,
                features=features,
                label=label
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error al añadir datos de entrenamiento: {e}")
            return {}
