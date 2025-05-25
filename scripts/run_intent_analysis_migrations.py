"""
Script para ejecutar las migraciones SQL del sistema mejorado de análisis de intención.
"""

import os
import logging
import asyncio
from dotenv import load_dotenv

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
        
        # Ejecutar cada comando
        for i, command in enumerate(commands):
            if command.strip():
                try:
                    # Ejecutar comando SQL
                    result = await supabase_client.rpc('run_sql_query', {'query': command}).execute()
                    logger.info(f"Comando SQL #{i+1} ejecutado correctamente")
                except Exception as e:
                    logger.error(f"Error al ejecutar comando SQL #{i+1}: {e}")
                    # Continuar con el siguiente comando
        
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
