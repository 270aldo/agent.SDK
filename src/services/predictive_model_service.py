"""
Servicio de Modelos Predictivos para NGX Voice Sales Agent.

Este servicio proporciona la base para todos los modelos predictivos utilizados
en el sistema, incluyendo predicción de objeciones, anticipación de necesidades
y predicción de probabilidad de conversión.
"""

from typing import Dict, List, Any, Optional, Tuple
import logging
import json
import numpy as np
from datetime import datetime, timedelta

from src.integrations.supabase.resilient_client import ResilientSupabaseClient

logger = logging.getLogger(__name__)

class PredictiveModelService:
    """
    Servicio central para coordinar todos los modelos predictivos del sistema.
    
    Este servicio proporciona:
    - Integración con servicios NLP existentes
    - Sistema de puntuación y confianza para predicciones
    - Gestión de modelos predictivos
    - Persistencia de predicciones y resultados
    """
    
    def __init__(self, supabase_client: ResilientSupabaseClient):
        """
        Inicializa el servicio de modelos predictivos.
        
        Args:
            supabase_client: Cliente de Supabase para persistencia de datos
        """
        self.supabase = supabase_client
        self._initialize_tables()
        
    def _initialize_tables(self) -> None:
        """
        Inicializa las tablas necesarias para el servicio de modelos predictivos.
        """
        try:
            # Verificar si las tablas existen y crearlas si no
            tables = [
                "predictive_models",
                "prediction_results",
                "prediction_feedback",
                "model_training_data"
            ]
            
            for table in tables:
                result = self.supabase.table(table).select("count(*)", count="exact").execute()
                logger.info(f"Tabla {table} verificada: {result}")
                
        except Exception as e:
            logger.error(f"Error al inicializar tablas de modelos predictivos: {e}")
    
    async def register_model(self, model_name: str, model_type: str, 
                      model_params: Dict[str, Any], 
                      description: str = "") -> Dict[str, Any]:
        """
        Registra un nuevo modelo predictivo en el sistema.
        
        Args:
            model_name: Nombre único del modelo
            model_type: Tipo de modelo (objection, needs, conversion)
            model_params: Parámetros de configuración del modelo
            description: Descripción del modelo
            
        Returns:
            Información del modelo registrado
        """
        try:
            model_data = {
                "name": model_name,
                "type": model_type,
                "parameters": json.dumps(model_params),
                "description": description,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "status": "active",
                "version": "1.0.0",
                "accuracy": 0.0,
                "training_samples": 0
            }
            
            result = self.supabase.table("predictive_models").insert(model_data).execute()
            logger.info(f"Modelo predictivo registrado: {model_name}")
            
            return result.data[0] if result.data else {}
            
        except Exception as e:
            logger.error(f"Error al registrar modelo predictivo: {e}")
            return {}
    
    async def get_model(self, model_name: str) -> Dict[str, Any]:
        """
        Obtiene información de un modelo predictivo.
        
        Args:
            model_name: Nombre del modelo a obtener
            
        Returns:
            Información del modelo
        """
        try:
            result = self.supabase.table("predictive_models").select("*").eq("name", model_name).execute()
            return result.data[0] if result.data else {}
            
        except Exception as e:
            logger.error(f"Error al obtener modelo predictivo: {e}")
            return {}
    
    async def list_models(self, model_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Lista todos los modelos predictivos registrados.
        
        Args:
            model_type: Tipo de modelo para filtrar (opcional)
            
        Returns:
            Lista de modelos predictivos
        """
        try:
            query = self.supabase.table("predictive_models").select("*")
            
            if model_type:
                query = query.eq("type", model_type)
                
            result = query.execute()
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Error al listar modelos predictivos: {e}")
            return []
    
    async def update_model(self, model_name: str, 
                     model_params: Optional[Dict[str, Any]] = None,
                     status: Optional[str] = None,
                     accuracy: Optional[float] = None) -> Dict[str, Any]:
        """
        Actualiza un modelo predictivo existente.
        
        Args:
            model_name: Nombre del modelo a actualizar
            model_params: Nuevos parámetros del modelo (opcional)
            status: Nuevo estado del modelo (opcional)
            accuracy: Nueva precisión del modelo (opcional)
            
        Returns:
            Información actualizada del modelo
        """
        try:
            update_data = {"updated_at": datetime.now().isoformat()}
            
            if model_params:
                update_data["parameters"] = json.dumps(model_params)
                
            if status:
                update_data["status"] = status
                
            if accuracy is not None:
                update_data["accuracy"] = accuracy
            
            result = self.supabase.table("predictive_models").update(update_data).eq("name", model_name).execute()
            logger.info(f"Modelo predictivo actualizado: {model_name}")
            
            return result.data[0] if result.data else {}
            
        except Exception as e:
            logger.error(f"Error al actualizar modelo predictivo: {e}")
            return {}
    
    async def delete_model(self, model_name: str) -> bool:
        """
        Elimina un modelo predictivo.
        
        Args:
            model_name: Nombre del modelo a eliminar
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        try:
            result = self.supabase.table("predictive_models").delete().eq("name", model_name).execute()
            logger.info(f"Modelo predictivo eliminado: {model_name}")
            
            return len(result.data) > 0
            
        except Exception as e:
            logger.error(f"Error al eliminar modelo predictivo: {e}")
            return False
    
    async def store_prediction(self, model_name: str, conversation_id: str, 
                         prediction_type: str, prediction_data: Dict[str, Any],
                         confidence: float) -> Dict[str, Any]:
        """
        Almacena una predicción realizada por un modelo.
        
        Args:
            model_name: Nombre del modelo que realizó la predicción
            conversation_id: ID de la conversación asociada
            prediction_type: Tipo de predicción (objection, need, conversion)
            prediction_data: Datos de la predicción
            confidence: Nivel de confianza de la predicción (0-1)
            
        Returns:
            Información de la predicción almacenada
        """
        try:
            prediction = {
                "model_name": model_name,
                "conversation_id": conversation_id,
                "prediction_type": prediction_type,
                "prediction_data": json.dumps(prediction_data),
                "confidence": confidence,
                "created_at": datetime.now().isoformat(),
                "status": "pending",
                "result": None
            }
            
            result = self.supabase.table("prediction_results").insert(prediction).execute()
            logger.info(f"Predicción almacenada para conversación: {conversation_id}")
            
            return result.data[0] if result.data else {}
            
        except Exception as e:
            logger.error(f"Error al almacenar predicción: {e}")
            return {}
    
    async def update_prediction_result(self, prediction_id: str, 
                                 actual_result: Dict[str, Any],
                                 was_correct: bool) -> Dict[str, Any]:
        """
        Actualiza el resultado real de una predicción para evaluación.
        
        Args:
            prediction_id: ID de la predicción
            actual_result: Resultado real observado
            was_correct: Indica si la predicción fue correcta
            
        Returns:
            Información actualizada de la predicción
        """
        try:
            update_data = {
                "result": json.dumps(actual_result),
                "status": "completed",
                "was_correct": was_correct,
                "completed_at": datetime.now().isoformat()
            }
            
            result = self.supabase.table("prediction_results").update(update_data).eq("id", prediction_id).execute()
            logger.info(f"Resultado de predicción actualizado: {prediction_id}")
            
            return result.data[0] if result.data else {}
            
        except Exception as e:
            logger.error(f"Error al actualizar resultado de predicción: {e}")
            return {}
    
    async def get_model_accuracy(self, model_name: str, 
                           time_period: Optional[int] = None) -> Dict[str, Any]:
        """
        Calcula la precisión de un modelo basado en predicciones pasadas.
        
        Args:
            model_name: Nombre del modelo
            time_period: Período de tiempo en días para el cálculo (opcional)
            
        Returns:
            Estadísticas de precisión del modelo
        """
        try:
            query = self.supabase.table("prediction_results").select("*").eq("model_name", model_name).eq("status", "completed")
            
            if time_period:
                start_date = (datetime.now() - timedelta(days=time_period)).isoformat()
                query = query.gte("created_at", start_date)
                
            result = query.execute()
            
            if not result.data:
                return {
                    "accuracy": 0,
                    "total_predictions": 0,
                    "correct_predictions": 0,
                    "confidence_avg": 0
                }
            
            predictions = result.data
            total = len(predictions)
            correct = sum(1 for p in predictions if p.get("was_correct", False))
            confidence_avg = sum(p.get("confidence", 0) for p in predictions) / total if total > 0 else 0
            
            accuracy = correct / total if total > 0 else 0
            
            # Actualizar la precisión en el registro del modelo
            await self.update_model(model_name, accuracy=accuracy)
            
            return {
                "accuracy": accuracy,
                "total_predictions": total,
                "correct_predictions": correct,
                "confidence_avg": confidence_avg
            }
            
        except Exception as e:
            logger.error(f"Error al calcular precisión del modelo: {e}")
            return {
                "accuracy": 0,
                "total_predictions": 0,
                "correct_predictions": 0,
                "confidence_avg": 0
            }
    
    async def add_training_data(self, model_name: str, data_type: str,
                          features: Dict[str, Any], label: Any) -> Dict[str, Any]:
        """
        Añade datos de entrenamiento para un modelo predictivo.
        
        Args:
            model_name: Nombre del modelo
            data_type: Tipo de datos (objection, need, conversion)
            features: Características de entrada
            label: Etiqueta o resultado esperado
            
        Returns:
            Información del dato de entrenamiento añadido
        """
        try:
            training_data = {
                "model_name": model_name,
                "data_type": data_type,
                "features": json.dumps(features),
                "label": json.dumps(label),
                "created_at": datetime.now().isoformat(),
                "used_in_training": False
            }
            
            result = self.supabase.table("model_training_data").insert(training_data).execute()
            
            # Actualizar contador de muestras de entrenamiento
            model = await self.get_model(model_name)
            if model:
                samples = model.get("training_samples", 0) + 1
                await self.update_model(model_name, model_params={"training_samples": samples})
            
            return result.data[0] if result.data else {}
            
        except Exception as e:
            logger.error(f"Error al añadir datos de entrenamiento: {e}")
            return {}
    
    async def get_training_data(self, model_name: str, 
                          limit: int = 1000, 
                          only_unused: bool = False) -> List[Dict[str, Any]]:
        """
        Obtiene datos de entrenamiento para un modelo.
        
        Args:
            model_name: Nombre del modelo
            limit: Límite de registros a obtener
            only_unused: Si es True, solo devuelve datos no utilizados en entrenamiento
            
        Returns:
            Lista de datos de entrenamiento
        """
        try:
            query = self.supabase.table("model_training_data").select("*").eq("model_name", model_name).limit(limit)
            
            if only_unused:
                query = query.eq("used_in_training", False)
                
            result = query.execute()
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Error al obtener datos de entrenamiento: {e}")
            return []
    
    async def mark_training_data_used(self, data_ids: List[str]) -> bool:
        """
        Marca datos de entrenamiento como utilizados.
        
        Args:
            data_ids: Lista de IDs de datos de entrenamiento
            
        Returns:
            True si se actualizaron correctamente, False en caso contrario
        """
        try:
            for data_id in data_ids:
                self.supabase.table("model_training_data").update({"used_in_training": True}).eq("id", data_id).execute()
            
            return True
            
        except Exception as e:
            logger.error(f"Error al marcar datos de entrenamiento como utilizados: {e}")
            return False
    
    async def calculate_confidence_score(self, prediction_scores: Dict[str, float]) -> Tuple[str, float]:
        """
        Calcula una puntuación de confianza para una predicción.
        
        Args:
            prediction_scores: Diccionario de predicciones con sus puntuaciones
            
        Returns:
            Tupla con la predicción seleccionada y su nivel de confianza
        """
        if not prediction_scores:
            return "", 0.0
            
        # Aplicar softmax para normalizar las puntuaciones
        scores = list(prediction_scores.values())
        exp_scores = np.exp(scores - np.max(scores))
        softmax_scores = exp_scores / exp_scores.sum()
        
        # Convertir de nuevo a diccionario
        normalized_scores = {k: float(s) for k, s in zip(prediction_scores.keys(), softmax_scores)}
        
        # Obtener la predicción con mayor puntuación
        best_prediction = max(normalized_scores.items(), key=lambda x: x[1])
        
        return best_prediction[0], best_prediction[1]
    
    async def store_feedback(self, prediction_id: str, feedback_type: str, 
                       feedback_data: Dict[str, Any], user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Almacena retroalimentación sobre una predicción.
        
        Args:
            prediction_id: ID de la predicción
            feedback_type: Tipo de retroalimentación (useful, not_useful, incorrect)
            feedback_data: Datos adicionales de retroalimentación
            user_id: ID del usuario que proporciona la retroalimentación (opcional)
            
        Returns:
            Información de la retroalimentación almacenada
        """
        try:
            feedback = {
                "prediction_id": prediction_id,
                "feedback_type": feedback_type,
                "feedback_data": json.dumps(feedback_data),
                "user_id": user_id,
                "created_at": datetime.now().isoformat()
            }
            
            result = self.supabase.table("prediction_feedback").insert(feedback).execute()
            logger.info(f"Retroalimentación almacenada para predicción: {prediction_id}")
            
            return result.data[0] if result.data else {}
            
        except Exception as e:
            logger.error(f"Error al almacenar retroalimentación: {e}")
            return {}
