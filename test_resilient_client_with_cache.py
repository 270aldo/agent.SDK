"""
Script para probar el cliente resiliente de Supabase con caché local.
Verifica las capacidades de reintento, manejo de errores y funcionamiento sin conexión.
"""

import asyncio
import logging
import sys
import os
import json
import uuid
from datetime import datetime
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

async def test_resilient_client_with_cache():
    """Prueba las funcionalidades del cliente resiliente de Supabase con caché local."""
    from src.integrations.supabase import resilient_supabase_client
    from src.utils.cache_utils import local_cache
    
    logger.info("=== Iniciando pruebas del cliente resiliente con caché local ===")
    
    # Prueba 1: Operación de selección básica con caché
    logger.info("Prueba 1: Realizando operación de selección básica con caché...")
    try:
        # Intentar seleccionar registros de la tabla de conversaciones
        conversations = await resilient_supabase_client.select(
            table="conversations",
            limit=2,
            use_cache=True
        )
        logger.info(f"Selección exitosa. Registros encontrados: {len(conversations)}")
        if conversations:
            logger.info(f"Primer registro: {conversations[0].get('conversation_id', 'N/A')}")
            
            # Verificar si los datos se guardaron en caché
            cached_data = local_cache.get("conversations")
            logger.info(f"Datos en caché: {len(cached_data)} registros")
    except Exception as e:
        logger.error(f"Error en operación de selección: {e}")
    
    # Prueba 2: Operación de inserción con caché
    logger.info("Prueba 2: Realizando operación de inserción con caché...")
    try:
        # Crear un registro de prueba
        test_id = str(uuid.uuid4())
        test_data = {
            "id": test_id,
            "user_id": "test_user",
            "message": "Mensaje de prueba del cliente resiliente con caché",
            "created_at": datetime.now().isoformat(),
            "test_flag": True
        }
        
        # Intentar insertar el registro
        result = await resilient_supabase_client.insert(
            table="test_cache",
            data=test_data,
            use_cache=True
        )
        logger.info(f"Inserción exitosa: {result.get('data', [])}")
        
        # Verificar si los datos se guardaron en caché
        cached_data = local_cache.get("test_cache")
        logger.info(f"Datos en caché después de inserción: {len(cached_data)} registros")
    except Exception as e:
        logger.error(f"Error en operación de inserción: {e}")
    
    # Prueba 3: Operación de selección sin conexión (simulando error)
    logger.info("Prueba 3: Simulando operación de selección sin conexión...")
    try:
        # Forzar un error de conexión simulado
        async def force_error(*args, **kwargs):
            raise ConnectionError("Error de conexión simulado")
        
        # Guardar la función original
        original_execute_query = resilient_supabase_client.execute_query
        
        # Reemplazar con la función que fuerza el error
        resilient_supabase_client.execute_query = force_error
        
        # Intentar seleccionar registros (debería usar la caché)
        conversations = await resilient_supabase_client.select(
            table="conversations",
            limit=2,
            use_cache=True
        )
        
        logger.info(f"Selección desde caché exitosa. Registros encontrados: {len(conversations)}")
        
        # Restaurar la función original
        resilient_supabase_client.execute_query = original_execute_query
    except Exception as e:
        logger.error(f"Error inesperado en prueba sin conexión: {e}")
        # Restaurar la función original en caso de error
        resilient_supabase_client.execute_query = original_execute_query
    
    # Prueba 4: Operaciones pendientes
    logger.info("Prueba 4: Verificando operaciones pendientes...")
    try:
        pending_operations = local_cache.get_pending_operations()
        logger.info(f"Operaciones pendientes: {len(pending_operations)}")
        
        if pending_operations:
            logger.info(f"Primera operación pendiente: {pending_operations[0]}")
    except Exception as e:
        logger.error(f"Error al verificar operaciones pendientes: {e}")
    
    # Prueba 5: Limpieza de caché
    logger.info("Prueba 5: Limpiando caché...")
    try:
        # Eliminar elementos expirados
        removed = local_cache.clear_expired()
        logger.info(f"Elementos expirados eliminados: {removed}")
    except Exception as e:
        logger.error(f"Error al limpiar caché: {e}")
    
    logger.info("=== Pruebas del cliente resiliente con caché completadas ===")

if __name__ == "__main__":
    # Crear directorio de caché si no existe
    if not os.path.exists(".cache"):
        os.makedirs(".cache")
        
    asyncio.run(test_resilient_client_with_cache())
