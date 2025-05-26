"""
Servicio de entrenamiento automático para modelos predictivos.

Este servicio se encarga de reentrenar los modelos predictivos
utilizando la retroalimentación recopilada y los datos históricos
para mejorar continuamente la precisión de las predicciones.
"""

import logging
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple

from src.integrations.supabase.resilient_client import ResilientSupabaseClient
from src.services.predictive_model_service import PredictiveModelService

logger = logging.getLogger(__name__)

class ModelTrainingService:
    """
    Servicio para el entrenamiento automático de modelos predictivos
    basado en retroalimentación y datos históricos.
    """
    
    def __init__(self, 
                 supabase_client: ResilientSupabaseClient,
                 predictive_model_service: PredictiveModelService):
        """
        Inicializa el servicio de entrenamiento de modelos.
        
        Args:
            supabase_client: Cliente para interactuar con Supabase
            predictive_model_service: Servicio para gestionar modelos predictivos
        """
        self.supabase = supabase_client
        self.predictive_model_service = predictive_model_service
        self.training_in_progress = {}
        
    async def schedule_training(self, 
                         model_name: str, 
                         force_training: bool = False,
                         training_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Programa el entrenamiento de un modelo predictivo.
        
        Args:
            model_name: Nombre del modelo a entrenar
            force_training: Si es True, fuerza el entrenamiento aunque no se cumplan los criterios
            training_config: Configuración específica para el entrenamiento
            
        Returns:
            Dict: Resultado de la programación del entrenamiento
        """
        try:
            # Verificar si el modelo existe
            model = await self.predictive_model_service.get_model(model_name)
            if not model:
                return {
                    "success": False,
                    "message": f"Modelo '{model_name}' no encontrado"
                }
            
            # Verificar si el modelo ya está en entrenamiento
            if model_name in self.training_in_progress and self.training_in_progress[model_name]:
                return {
                    "success": False,
                    "message": f"El modelo '{model_name}' ya está en proceso de entrenamiento"
                }
            
            # Verificar si se cumplen los criterios para entrenamiento automático
            if not force_training:
                should_train, reason = await self._should_train_model(model_name)
                if not should_train:
                    return {
                        "success": False,
                        "message": f"No se cumplen los criterios para entrenar el modelo: {reason}"
                    }
            
            # Programar entrenamiento asíncrono
            training_id = f"training-{model_name}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Registrar el inicio del entrenamiento
            training_record = {
                "id": training_id,
                "model_name": model_name,
                "status": "scheduled",
                "start_time": datetime.now().isoformat(),
                "config": json.dumps(training_config or {})
            }
            
            result = await self.supabase.table("model_training").insert(training_record).execute()
            
            if result.get("error"):
                return {
                    "success": False,
                    "message": f"Error al registrar entrenamiento: {result.get('error')}"
                }
            
            # Iniciar entrenamiento en segundo plano
            asyncio.create_task(self._train_model_async(model_name, training_id, training_config))
            
            return {
                "success": True,
                "training_id": training_id,
                "message": f"Entrenamiento programado para el modelo '{model_name}'",
                "estimated_completion": (datetime.now() + timedelta(minutes=30)).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error al programar entrenamiento para '{model_name}': {str(e)}")
            return {
                "success": False,
                "message": f"Error al programar entrenamiento: {str(e)}"
            }
    
    async def get_training_status(self, training_id: str) -> Dict[str, Any]:
        """
        Obtiene el estado actual de un entrenamiento.
        
        Args:
            training_id: ID del entrenamiento
            
        Returns:
            Dict: Estado del entrenamiento
        """
        try:
            result = await self.supabase.table("model_training").select("*").eq("id", training_id).execute()
            
            if result.get("error"):
                return {
                    "success": False,
                    "message": f"Error al obtener estado del entrenamiento: {result.get('error')}"
                }
            
            data = result.get("data", [])
            if not data:
                return {
                    "success": False,
                    "message": f"Entrenamiento con ID '{training_id}' no encontrado"
                }
            
            training_record = data[0]
            
            # Calcular progreso estimado si está en curso
            progress = None
            if training_record["status"] == "in_progress":
                start_time = datetime.fromisoformat(training_record["start_time"])
                current_time = datetime.now()
                elapsed_minutes = (current_time - start_time).total_seconds() / 60
                
                # Estimar que un entrenamiento toma aproximadamente 30 minutos
                progress = min(elapsed_minutes / 30, 0.99)
            
            return {
                "success": True,
                "training_id": training_id,
                "model_name": training_record["model_name"],
                "status": training_record["status"],
                "start_time": training_record["start_time"],
                "end_time": training_record.get("end_time"),
                "progress": progress if progress is not None else 1.0 if training_record["status"] == "completed" else 0.0,
                "metrics": json.loads(training_record.get("metrics", "{}")) if training_record.get("metrics") else None,
                "error": training_record.get("error")
            }
            
        except Exception as e:
            logger.error(f"Error al obtener estado del entrenamiento '{training_id}': {str(e)}")
            return {
                "success": False,
                "message": f"Error al obtener estado del entrenamiento: {str(e)}"
            }
    
    async def list_model_trainings(self, 
                           model_name: Optional[str] = None, 
                           status: Optional[str] = None,
                           limit: int = 10) -> Dict[str, Any]:
        """
        Lista los entrenamientos de modelos con filtros opcionales.
        
        Args:
            model_name: Filtrar por nombre de modelo (opcional)
            status: Filtrar por estado (opcional)
            limit: Número máximo de registros a devolver
            
        Returns:
            Dict: Lista de entrenamientos
        """
        try:
            query = self.supabase.table("model_training").select("*")
            
            if model_name:
                query = query.eq("model_name", model_name)
            
            if status:
                query = query.eq("status", status)
            
            query = query.order("start_time", ascending=False).limit(limit)
            
            result = await query.execute()
            
            if result.get("error"):
                return {
                    "success": False,
                    "message": f"Error al listar entrenamientos: {result.get('error')}"
                }
            
            trainings = result.get("data", [])
            
            return {
                "success": True,
                "trainings": trainings,
                "count": len(trainings)
            }
            
        except Exception as e:
            logger.error(f"Error al listar entrenamientos: {str(e)}")
            return {
                "success": False,
                "message": f"Error al listar entrenamientos: {str(e)}"
            }
    
    async def _should_train_model(self, model_name: str) -> Tuple[bool, str]:
        """
        Determina si un modelo debe ser reentrenado basado en criterios predefinidos.
        
        Args:
            model_name: Nombre del modelo a evaluar
            
        Returns:
            Tuple[bool, str]: (Debe entrenar, Razón)
        """
        try:
            # Obtener información del modelo
            model = await self.predictive_model_service.get_model(model_name)
            if not model:
                return False, "Modelo no encontrado"
            
            # Verificar última fecha de entrenamiento
            last_training = model.get("last_training_date")
            if not last_training:
                return True, "Nunca ha sido entrenado"
            
            last_training_date = datetime.fromisoformat(last_training)
            days_since_training = (datetime.now() - last_training_date).days
            
            # Si han pasado más de 7 días desde el último entrenamiento
            if days_since_training >= 7:
                return True, f"Han pasado {days_since_training} días desde el último entrenamiento"
            
            # Verificar cantidad de retroalimentación nueva desde el último entrenamiento
            result = await self.supabase.table("feedback").select("count").gte("created_at", last_training).eq("model_name", model_name).execute()
            
            if result.get("error"):
                return False, f"Error al verificar retroalimentación: {result.get('error')}"
            
            feedback_count = result.get("count", 0)
            
            # Si hay suficiente retroalimentación nueva (más de 50 registros)
            if feedback_count >= 50:
                return True, f"Hay {feedback_count} registros de retroalimentación nuevos"
            
            # Verificar si la precisión ha disminuido
            metrics = model.get("metrics", {})
            if isinstance(metrics, str):
                metrics = json.loads(metrics)
            
            current_accuracy = metrics.get("accuracy", 0)
            
            # Si la precisión es menor al 70%
            if current_accuracy < 0.7:
                return True, f"La precisión actual ({current_accuracy:.2f}) es baja"
            
            return False, "No se cumplen los criterios para reentrenamiento"
            
        except Exception as e:
            logger.error(f"Error al evaluar si se debe entrenar el modelo '{model_name}': {str(e)}")
            return False, f"Error al evaluar criterios: {str(e)}"
    
    async def _train_model_async(self, 
                         model_name: str, 
                         training_id: str,
                         training_config: Optional[Dict[str, Any]] = None) -> None:
        """
        Ejecuta el entrenamiento de un modelo en segundo plano.
        
        Args:
            model_name: Nombre del modelo a entrenar
            training_id: ID del entrenamiento
            training_config: Configuración específica para el entrenamiento
        """
        try:
            # Marcar que el entrenamiento está en progreso
            self.training_in_progress[model_name] = True
            
            # Actualizar estado a "en progreso"
            await self.supabase.table("model_training").update({
                "status": "in_progress",
                "progress": 0.0
            }).eq("id", training_id).execute()
            
            # Obtener datos de entrenamiento
            training_data = await self._collect_training_data(model_name)
            
            # Simular entrenamiento (esto sería reemplazado por el entrenamiento real)
            # En una implementación real, aquí se llamaría a la biblioteca de ML correspondiente
            await asyncio.sleep(5)  # Simular procesamiento
            
            # Actualizar progreso
            await self.supabase.table("model_training").update({
                "progress": 0.5
            }).eq("id", training_id).execute()
            
            # Simular más procesamiento
            await asyncio.sleep(5)
            
            # Generar métricas simuladas (en una implementación real, estas vendrían del entrenamiento)
            training_metrics = {
                "accuracy": 0.85,
                "precision": 0.82,
                "recall": 0.87,
                "f1_score": 0.84,
                "training_samples": len(training_data),
                "training_time_seconds": 10
            }
            
            # Actualizar modelo con nuevos parámetros
            new_model_params = await self._generate_model_parameters(model_name, training_data, training_config)
            
            # Actualizar el modelo en la base de datos
            await self.predictive_model_service.update_model(
                model_name=model_name,
                model_params=new_model_params,
                accuracy=training_metrics["accuracy"],
                last_training_date=datetime.now().isoformat()
            )
            
            # Marcar entrenamiento como completado
            await self.supabase.table("model_training").update({
                "status": "completed",
                "end_time": datetime.now().isoformat(),
                "metrics": json.dumps(training_metrics),
                "progress": 1.0
            }).eq("id", training_id).execute()
            
            logger.info(f"Entrenamiento completado para el modelo '{model_name}' (ID: {training_id})")
            
        except Exception as e:
            logger.error(f"Error durante el entrenamiento del modelo '{model_name}': {str(e)}")
            
            # Marcar entrenamiento como fallido
            await self.supabase.table("model_training").update({
                "status": "failed",
                "end_time": datetime.now().isoformat(),
                "error": str(e)
            }).eq("id", training_id).execute()
            
        finally:
            # Marcar que el entrenamiento ha terminado
            self.training_in_progress[model_name] = False
    
    async def _collect_training_data(self, model_name: str) -> List[Dict[str, Any]]:
        """
        Recopila datos para el entrenamiento del modelo.
        
        Args:
            model_name: Nombre del modelo
            
        Returns:
            List[Dict[str, Any]]: Datos de entrenamiento
        """
        # Obtener retroalimentación para el modelo
        feedback_result = await self.supabase.table("feedback").select("*").eq("model_name", model_name).execute()
        
        feedback_data = feedback_result.get("data", [])
        
        # Obtener predicciones históricas
        predictions_result = await self.supabase.table("predictions").select("*").eq("model_name", model_name).limit(1000).execute()
        
        predictions_data = predictions_result.get("data", [])
        
        # Combinar datos
        training_data = []
        
        # Procesar predicciones y retroalimentación
        for prediction in predictions_data:
            # Buscar retroalimentación asociada a esta predicción
            related_feedback = [f for f in feedback_data if f.get("prediction_id") == prediction.get("id")]
            
            if related_feedback:
                # Si hay retroalimentación, usar para entrenamiento supervisado
                for feedback in related_feedback:
                    training_data.append({
                        "input_data": json.loads(prediction.get("input_data", "{}")),
                        "prediction": json.loads(prediction.get("prediction_data", "{}")),
                        "feedback_rating": feedback.get("rating"),
                        "feedback_details": json.loads(feedback.get("details", "{}"))
                    })
            else:
                # Si no hay retroalimentación pero la predicción tiene alta confianza,
                # usar para entrenamiento semi-supervisado
                confidence = prediction.get("confidence", 0)
                if confidence > 0.8:
                    training_data.append({
                        "input_data": json.loads(prediction.get("input_data", "{}")),
                        "prediction": json.loads(prediction.get("prediction_data", "{}")),
                        "assumed_correct": True,
                        "confidence": confidence
                    })
        
        return training_data
    
    async def _generate_model_parameters(self, 
                                 model_name: str, 
                                 training_data: List[Dict[str, Any]],
                                 training_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Genera nuevos parámetros para el modelo basado en los datos de entrenamiento.
        
        Args:
            model_name: Nombre del modelo
            training_data: Datos de entrenamiento
            training_config: Configuración específica para el entrenamiento
            
        Returns:
            Dict[str, Any]: Nuevos parámetros del modelo
        """
        # Obtener parámetros actuales del modelo
        model = await self.predictive_model_service.get_model(model_name)
        current_params = {}
        
        if model and "parameters" in model:
            if isinstance(model["parameters"], str):
                current_params = json.loads(model["parameters"])
            else:
                current_params = model["parameters"]
        
        # En una implementación real, aquí se realizaría el entrenamiento del modelo
        # y se generarían nuevos parámetros basados en los datos de entrenamiento
        
        # Para esta simulación, simplemente ajustamos algunos parámetros existentes
        new_params = current_params.copy()
        
        # Ajustar parámetros según el tipo de modelo
        if model_name.startswith("objection"):
            new_params["objection_thresholds"] = {
                "price": 0.65,
                "features": 0.7,
                "competition": 0.6,
                "timing": 0.55
            }
        elif model_name.startswith("needs"):
            new_params["need_detection_sensitivity"] = 0.75
            new_params["context_window_size"] = 5
        elif model_name.startswith("conversion"):
            new_params["conversion_threshold"] = 0.6
            new_params["buying_signals_weight"] = 0.8
        elif model_name.startswith("decision_engine"):
            new_params["exploration_rate"] = 0.15
            new_params["objective_weights"] = {
                "need_satisfaction": 0.4,
                "objection_handling": 0.3,
                "conversion_progress": 0.3
            }
        
        # Incorporar configuración específica del entrenamiento si existe
        if training_config:
            for key, value in training_config.items():
                if key.startswith("param_"):
                    param_name = key[6:]  # Quitar prefijo "param_"
                    new_params[param_name] = value
        
        # Añadir metadatos del entrenamiento
        new_params["last_training"] = {
            "timestamp": datetime.now().isoformat(),
            "training_samples": len(training_data),
            "version": new_params.get("version", 0) + 1
        }
        
        return new_params
