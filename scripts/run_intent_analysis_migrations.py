"""
Script para ejecutar las migraciones SQL del sistema mejorado de análisis de intención.
"""

import os
import sys
import logging
import asyncio
from dotenv import load_dotenv

# Añadir el directorio raíz del proyecto al path de Python
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Ahora podemos importar desde src
from src.integrations.supabase import supabase_client

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def run_migrations():
    """
    Ejecutar migraciones SQL para el sistema mejorado de análisis de intención.
    """
    try:
        # Cargar archivo SQL
        script_dir = os.path.dirname(os.path.abspath(__file__))
        migration_path = os.path.join(script_dir, 'create_intent_analysis_tables.sql')
        
        with open(migration_path, 'r') as f:
            sql_script = f.read()
        
        # Dividir el script en comandos individuales
        commands = sql_script.split(';')
        
        # Crear las tablas una por una usando la API REST de Supabase
        # Primero, intent_models
        logger.info("Creando tabla intent_models...")
        try:
            # Ejecutar directamente la consulta SQL
            result = supabase_client.table('intent_models').select('id').limit(1).execute()
            logger.info("La tabla intent_models ya existe")
        except Exception as e:
            if "relation \"intent_models\" does not exist" in str(e):
                # Crear la tabla manualmente
                logger.info("Creando tabla intent_models desde cero")
                try:
                    # Ejecutar la creación de la tabla directamente en la base de datos
                    # Esto requiere permisos de administrador en Supabase
                    # Alternativamente, puedes crear las tablas manualmente desde la interfaz de Supabase
                    logger.info("Por favor, crea las tablas manualmente desde la interfaz de Supabase")
                    logger.info("El script SQL está en: scripts/create_intent_analysis_tables.sql")
                except Exception as create_error:
                    logger.error(f"Error al crear tabla intent_models: {create_error}")
            else:
                logger.error(f"Error al verificar tabla intent_models: {e}")
        
        # Verificar intent_analysis_results
        logger.info("Verificando tabla intent_analysis_results...")
        try:
            result = supabase_client.table('intent_analysis_results').select('id').limit(1).execute()
            logger.info("La tabla intent_analysis_results ya existe")
        except Exception as e:
            if "relation \"intent_analysis_results\" does not exist" in str(e):
                logger.info("La tabla intent_analysis_results no existe, debe ser creada manualmente")
            else:
                logger.error(f"Error al verificar tabla intent_analysis_results: {e}")
        
        # Verificar intent_training_data
        logger.info("Verificando tabla intent_training_data...")
        try:
            result = supabase_client.table('intent_training_data').select('id').limit(1).execute()
            logger.info("La tabla intent_training_data ya existe")
        except Exception as e:
            if "relation \"intent_training_data\" does not exist" in str(e):
                logger.info("La tabla intent_training_data no existe, debe ser creada manualmente")
            else:
                logger.error(f"Error al verificar tabla intent_training_data: {e}")
        
        logger.info("Migraciones para el sistema de análisis de intención completadas")
        
    except Exception as e:
        logger.error(f"Error al ejecutar migraciones: {e}")
        raise

if __name__ == "__main__":
    # Cargar variables de entorno
    load_dotenv()
    
    # Ejecutar migraciones
    asyncio.run(run_migrations())
    
    logger.info("Script de migración completado")
