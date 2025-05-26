"""
Script para programar el entrenamiento automático de modelos predictivos.

Este script verifica qué modelos cumplen con los criterios para ser reentrenados
y programa su entrenamiento automáticamente. Está diseñado para ejecutarse
como una tarea programada (cron job) de forma periódica.
"""

import asyncio
import logging
import sys
import os
import json
from datetime import datetime
from pathlib import Path

# Añadir el directorio raíz al path para poder importar los módulos
sys.path.append(str(Path(__file__).parent.parent))

from src.integrations.supabase.resilient_client import ResilientSupabaseClient
from src.services.predictive_model_service import PredictiveModelService
from src.services.model_training_service import ModelTrainingService

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("model_training.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("model_training")

async def main():
    """Función principal que programa el entrenamiento de modelos."""
    logger.info("Iniciando verificación de modelos para entrenamiento automático")
    
    try:
        # Inicializar servicios
        supabase_client = ResilientSupabaseClient()
        predictive_model_service = PredictiveModelService(supabase_client)
        model_training_service = ModelTrainingService(supabase_client, predictive_model_service)
        
        # Obtener todos los modelos
        models_result = await predictive_model_service.list_models()
        
        if isinstance(models_result, dict):
            models = models_result.get("data", [])
        else:
            models = models_result
        
        logger.info(f"Se encontraron {len(models)} modelos para verificar")
        
        # Verificar criterios y programar entrenamiento para cada modelo
        scheduled_trainings = []
        skipped_models = []
        
        for model in models:
            model_name = model.get("name")
            logger.info(f"Verificando criterios para el modelo '{model_name}'")
            
            should_train, reason = await model_training_service._should_train_model(model_name)
            
            if should_train:
                logger.info(f"El modelo '{model_name}' cumple con los criterios para entrenamiento: {reason}")
                
                # Programar entrenamiento
                result = await model_training_service.schedule_training(
                    model_name=model_name,
                    force_training=False
                )
                
                if result.get("success", False):
                    scheduled_trainings.append({
                        "model_name": model_name,
                        "training_id": result.get("training_id"),
                        "reason": reason
                    })
                    logger.info(f"Entrenamiento programado para '{model_name}' con ID: {result.get('training_id')}")
                else:
                    skipped_models.append({
                        "model_name": model_name,
                        "reason": result.get("message", "Error desconocido")
                    })
                    logger.warning(f"No se pudo programar entrenamiento para '{model_name}': {result.get('message')}")
            else:
                skipped_models.append({
                    "model_name": model_name,
                    "reason": reason
                })
                logger.info(f"El modelo '{model_name}' no necesita ser reentrenado: {reason}")
        
        # Guardar registro de la ejecución
        execution_log = {
            "timestamp": datetime.now().isoformat(),
            "scheduled_trainings": scheduled_trainings,
            "skipped_models": skipped_models,
            "total_scheduled": len(scheduled_trainings),
            "total_skipped": len(skipped_models)
        }
        
        log_file = Path("training_executions.json")
        
        # Cargar registros anteriores si existen
        previous_logs = []
        if log_file.exists():
            try:
                with open(log_file, "r") as f:
                    previous_logs = json.load(f)
            except:
                previous_logs = []
        
        # Añadir nuevo registro y guardar
        previous_logs.append(execution_log)
        with open(log_file, "w") as f:
            json.dump(previous_logs, f, indent=2)
        
        logger.info(f"Ejecución completada: {len(scheduled_trainings)} modelos programados para entrenamiento, {len(skipped_models)} modelos omitidos")
        
    except Exception as e:
        logger.error(f"Error durante la verificación y programación de entrenamientos: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
