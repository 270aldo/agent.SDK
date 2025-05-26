"""
Script para probar el cliente resiliente de Supabase.
Verifica las capacidades de reintento y manejo de errores.
"""

import asyncio
import logging
import sys
import os
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

async def test_resilient_client():
    """Prueba las funcionalidades del cliente resiliente de Supabase."""
    from src.integrations.supabase import resilient_supabase_client
    
    logger.info("=== Iniciando pruebas del cliente resiliente de Supabase ===")
    
    # Prueba 1: Verificar conexión
    logger.info("Prueba 1: Verificando conexión...")
    connection_ok = await resilient_supabase_client.check_connection()
    logger.info(f"Conexión exitosa: {connection_ok}")
    
    if not connection_ok:
        logger.error("No se pudo establecer conexión con Supabase. Abortando pruebas.")
        return
    
    # Prueba 2: Operación de selección básica
    logger.info("Prueba 2: Realizando operación de selección básica...")
    try:
        # Intentar seleccionar registros de la tabla de conversaciones
        conversations = await resilient_supabase_client.select(
            table="conversations",
            limit=5
        )
        logger.info(f"Selección exitosa. Registros encontrados: {len(conversations)}")
        if conversations:
            logger.info(f"Primer registro: {conversations[0]}")
    except Exception as e:
        logger.error(f"Error en operación de selección: {e}")
    
    # Prueba 3: Operación de inserción
    logger.info("Prueba 3: Realizando operación de inserción...")
    try:
        # Crear un registro de prueba
        import uuid
        test_id = str(uuid.uuid4())
        test_data = {
            "id": test_id,
            "user_id": "test_user",
            "message": "Mensaje de prueba del cliente resiliente",
            "created_at": "2025-05-24T23:45:00",
            "test_flag": True
        }
        
        # Intentar insertar el registro
        result = await resilient_supabase_client.insert(
            table="test_resilient_client",
            data=test_data
        )
        logger.info(f"Inserción exitosa: {result}")
    except Exception as e:
        logger.error(f"Error en operación de inserción: {e}")
        logger.info("Nota: Es normal que falle si la tabla 'test_resilient_client' no existe")
    
    # Prueba 4: Simulación de error y reintento
    logger.info("Prueba 4: Simulando error y reintento...")
    try:
        # Intentar acceder a una tabla que no existe para forzar un error
        result = await resilient_supabase_client.select(
            table="non_existent_table",
            max_retries=2
        )
        logger.info(f"Resultado inesperado (no debería llegar aquí): {result}")
    except Exception as e:
        logger.info(f"Error esperado capturado después de reintentos: {e}")
    
    logger.info("=== Pruebas del cliente resiliente completadas ===")

if __name__ == "__main__":
    asyncio.run(test_resilient_client())
