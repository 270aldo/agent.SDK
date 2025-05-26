#!/usr/bin/env python3
"""
Script para configurar las tablas del sistema de cualificación en Supabase.
"""

import os
import logging
import asyncio
from dotenv import load_dotenv

from src.integrations.supabase import supabase_client

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

async def setup_qualification_tables():
    """Configurar tablas para el sistema de cualificación en Supabase."""
    logger.info("Iniciando configuración de tablas para el sistema de cualificación...")
    
    try:
        # Obtener cliente de Supabase con permisos de administrador
        client = supabase_client.get_client(admin=True)
        
        # Leer el archivo SQL
        sql_path = os.path.join(os.path.dirname(__file__), 'create_qualification_tables.sql')
        with open(sql_path, 'r') as f:
            sql_script = f.read()
        
        # Ejecutar el script SQL
        logger.info("Ejecutando script SQL para crear tablas de cualificación...")
        result = await client.table("_dummy").select("*").execute()
        
        if result is None:
            logger.warning("La conexión a Supabase parece estar en modo simulado.")
            logger.warning("Por favor, crea las tablas manualmente desde la interfaz web de Supabase usando el siguiente esquema:")
            logger.info("=== ESQUEMA PARA LAS TABLAS DE CUALIFICACIÓN ===")
            logger.info(sql_script)
        else:
            # Intentar ejecutar el SQL directamente
            try:
                # Nota: Esto puede no funcionar directamente con la API de Supabase
                # y podría requerir usar la interfaz web de SQL
                await client.rpc("exec_sql", {"sql": sql_script}).execute()
                logger.info("Tablas de cualificación creadas exitosamente.")
            except Exception as e:
                logger.warning(f"No se pudieron crear las tablas automáticamente: {e}")
                logger.warning("Por favor, crea las tablas manualmente desde la interfaz web de Supabase usando el siguiente esquema:")
                logger.info("=== ESQUEMA PARA LAS TABLAS DE CUALIFICACIÓN ===")
                logger.info(sql_script)
    
    except Exception as e:
        logger.error(f"Error al configurar tablas de cualificación: {e}")
        logger.warning("Por favor, crea las tablas manualmente desde la interfaz web de Supabase.")
    
    logger.info("Configuración de tablas de cualificación completada.")

if __name__ == "__main__":
    asyncio.run(setup_qualification_tables())
