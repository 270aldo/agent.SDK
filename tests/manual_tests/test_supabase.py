import pytest
pytest.skip("manual script", allow_module_level=True)
import os
import sys
import asyncio
import uuid
from dotenv import load_dotenv
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

# Asegurar que el directorio raíz está en el path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.integrations.supabase import supabase_client

async def test_supabase_operations():
    """Probar operaciones básicas con Supabase."""
    
    # 1. Obtener cliente
    client = supabase_client.get_client()
    logger.info(f"Cliente obtenido. Modo simulado: {supabase_client._mock_enabled}")
    
    # 2. Crear un cliente de prueba
    test_customer_id = str(uuid.uuid4())
    test_customer = {
        "id": test_customer_id,
        "name": "Cliente de Prueba",
        "email": f"test_{test_customer_id[:8]}@example.com",
        "age": 35,
        "gender": "male",
        "occupation": "Desarrollador",
        "goals": {"principal": "Mejorar rendimiento cognitivo"},
        "fitness_metrics": {"peso": 75, "altura": 180},
        "lifestyle": {"ejercicio": "3 veces por semana"},
        "interaction_history": {}
    }
    
    logger.info(f"Insertando cliente de prueba con ID: {test_customer_id}")
    
    try:
        # Insertar el cliente
        response = await asyncio.to_thread(
            lambda: client.table("customers").upsert(test_customer).execute()
        )
        logger.info(f"Cliente insertado: {response.data}")
        
        # Consultar el cliente insertado
        query_response = await asyncio.to_thread(
            lambda: client.table("customers").select("*").eq("id", test_customer_id).single().execute()
        )
        
        if query_response.data:
            logger.info(f"Cliente recuperado: {query_response.data}")
        else:
            logger.error("No se pudo recuperar el cliente insertado")
        
        # 3. Crear una conversación para este cliente
        conversation_id = str(uuid.uuid4())
        conversation = {
            "conversation_id": conversation_id,
            "customer_id": test_customer_id,
            "program_type": "PRIME",
            "phase": "initial_contact",
            "messages": [],
            "customer_data": {},
            "session_insights": {},
            "objections_raised": [],
            "next_steps_agreed": False,
            "call_duration_seconds": 0
        }
        
        logger.info(f"Insertando conversación de prueba con ID: {conversation_id}")
        
        # Insertar la conversación
        conv_response = await asyncio.to_thread(
            lambda: client.table("conversations").insert(conversation).execute()
        )
        logger.info(f"Conversación insertada: {conv_response.data}")
        
        # Consultar la conversación insertada
        conv_query_response = await asyncio.to_thread(
            lambda: client.table("conversations").select("*").eq("conversation_id", conversation_id).single().execute()
        )
        
        if conv_query_response.data:
            logger.info(f"Conversación recuperada: {conv_query_response.data}")
        else:
            logger.error("No se pudo recuperar la conversación insertada")
            
        return True
        
    except Exception as e:
        logger.error(f"Error durante la prueba de Supabase: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_supabase_operations())
    sys.exit(0 if result else 1) 