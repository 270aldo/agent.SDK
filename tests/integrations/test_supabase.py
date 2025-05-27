"""
Pruebas de integración para las operaciones con Supabase.
"""
import pytest
import os
import asyncio
import uuid
from dotenv import load_dotenv
import logging

from src.integrations.supabase import supabase_client, SupabaseClient  # Import SupabaseClient para tipado

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno (pytest-dotenv puede manejar esto también)
load_dotenv()

@pytest.fixture(scope="module")
def event_loop():
    """Sobrescribe el event loop de pytest para que sea compatible con asyncio a nivel de módulo."""
    return asyncio.get_event_loop()

@pytest.fixture(scope="module")
def db_client() -> SupabaseClient:
    """Provee un cliente Supabase para las pruebas de integración.
    Salta las pruebas si las variables de entorno no están configuradas.
    """
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_SERVICE_ROLE_KEY"):
        pytest.skip("Variables de entorno de Supabase no configuradas. Saltando pruebas de integración de Supabase.")
    
    # En un entorno de prueba real, podrías querer usar una base de datos de prueba separada
    # o asegurarte de que _mock_enabled esté configurado adecuadamente si es para pruebas offline.
    # Aquí asumimos que queremos probar contra una instancia real (de desarrollo o prueba).
    client = supabase_client.get_client(admin=True) # Usar admin client para operaciones de prueba
    logger.info(f"Cliente Supabase obtenido para pruebas. Modo simulado: {getattr(supabase_client, '_mock_enabled', 'N/A')}")
    return client

@pytest.mark.asyncio
async def test_customer_crud_operations(db_client: SupabaseClient):
    """Prueba las operaciones CRUD para la tabla 'customers'."""
    client = db_client
    test_customer_id = str(uuid.uuid4())
    test_customer_email = f"test_customer_{test_customer_id[:8]}@example.com"
    
    customer_data = {
        "id": test_customer_id,
        "name": "Test Customer",
        "email": test_customer_email,
        "age": 30,
        "gender": "other",
        "occupation": "Tester",
        "goals": {"primary": "test"},
        "fitness_metrics": {},
        "lifestyle": {},
        "interaction_history": {}
    }

    logger.info(f"Insertando cliente de prueba con ID: {test_customer_id}")
    
    # INSERT (Upsert)
    # Usamos `await asyncio.to_thread` porque el cliente de Supabase (supabase-py)
    # realiza operaciones de red síncronas por defecto.
    insert_response = await asyncio.to_thread(
        lambda: client.table("customers").upsert(customer_data).execute()
    )
    
    assert insert_response.data, f"No se recibieron datos al insertar el cliente: {insert_response.error}"
    assert len(insert_response.data) == 1
    assert insert_response.data[0]["id"] == test_customer_id
    assert insert_response.data[0]["email"] == test_customer_email
    logger.info(f"Cliente insertado: {insert_response.data[0]['id']}")

    # SELECT
    select_response = await asyncio.to_thread(
        lambda: client.table("customers").select("*").eq("id", test_customer_id).single().execute()
    )
    assert select_response.data, f"No se pudo recuperar el cliente: {select_response.error}"
    assert select_response.data["name"] == "Test Customer"
    logger.info(f"Cliente recuperado: {select_response.data['id']}")

    # UPDATE (Upsert)
    updated_customer_data = {**customer_data, "name": "Updated Test Customer"}
    update_response = await asyncio.to_thread(
        lambda: client.table("customers").upsert(updated_customer_data).execute()
    )
    assert update_response.data, f"No se recibieron datos al actualizar el cliente: {update_response.error}"
    assert update_response.data[0]["name"] == "Updated Test Customer"
    logger.info(f"Cliente actualizado: {update_response.data[0]['id']}")

    # DELETE (Limpieza)
    # Nota: La librería supabase-py podría no devolver datos en delete, verificar su API.
    # Usualmente se espera un status code o se verifica que el select posterior no encuentre nada.
    # Por simplicidad, asumimos que `execute()` no lanza error si tiene éxito.
    await asyncio.to_thread(
        lambda: client.table("customers").delete().eq("id", test_customer_id).execute()
    )
    
    # Verificar que fue eliminado
    verify_delete_response = await asyncio.to_thread(
        lambda: client.table("customers").select("*").eq("id", test_customer_id).execute()
    )
    assert not verify_delete_response.data, f"El cliente no fue eliminado correctamente: {verify_delete_response.data}"
    logger.info(f"Cliente eliminado: {test_customer_id}")


@pytest.mark.asyncio
async def test_conversation_crud_operations(db_client: SupabaseClient):
    """Prueba las operaciones CRUD para la tabla 'conversations', incluyendo la relación con 'customers'."""
    client = db_client
    
    # Primero, necesitamos un cliente existente o crear uno nuevo
    test_customer_id = str(uuid.uuid4())
    customer_data = {
        "id": test_customer_id, "name": "ConvTest Customer", 
        "email": f"conv_test_{test_customer_id[:8]}@example.com", "age": 25
    }
    await asyncio.to_thread(
        lambda: client.table("customers").upsert(customer_data).execute()
    )
    logger.info(f"Cliente para conversación creado: {test_customer_id}")

    test_conversation_id = str(uuid.uuid4())
    conversation_data = {
        "conversation_id": test_conversation_id,
        "customer_id": test_customer_id,
        "program_type": "LONGEVITY",
        "phase": "onboarding",
        "messages": [{"role": "user", "content": "Hola"}], # Asegurarse que el JSON es válido
        "customer_data": {"source": "test"},
        "session_insights": {},
        "objections_raised": [],
        "next_steps_agreed": False,
        "call_duration_seconds": 60
    }

    logger.info(f"Insertando conversación de prueba con ID: {test_conversation_id}")
    # INSERT (Upsert)
    insert_response = await asyncio.to_thread(
        lambda: client.table("conversations").upsert(conversation_data).execute()
    )
    assert insert_response.data, f"No se recibieron datos al insertar la conversación: {insert_response.error}"
    assert len(insert_response.data) == 1
    assert insert_response.data[0]["conversation_id"] == test_conversation_id
    logger.info(f"Conversación insertada: {insert_response.data[0]['conversation_id']}")

    # SELECT
    select_response = await asyncio.to_thread(
        lambda: client.table("conversations").select("*, customer:customers(name)").eq("conversation_id", test_conversation_id).single().execute()
    )
    assert select_response.data, f"No se pudo recuperar la conversación: {select_response.error}"
    assert select_response.data["program_type"] == "LONGEVITY"
    assert len(select_response.data["messages"]) == 1
    # Comprobar la relación (si la FK está bien configurada y la query la pide)
    # assert select_response.data["customer"]["name"] == "ConvTest Customer" # Descomentar si se usa join
    logger.info(f"Conversación recuperada: {select_response.data['conversation_id']}")

    # UPDATE (Upsert)
    updated_conversation_data = {**conversation_data, "phase": "follow_up"}
    update_response = await asyncio.to_thread(
        lambda: client.table("conversations").upsert(updated_conversation_data).execute()
    )
    assert update_response.data, f"No se recibieron datos al actualizar la conversación: {update_response.error}"
    assert update_response.data[0]["phase"] == "follow_up"
    logger.info(f"Conversación actualizada: {update_response.data[0]['conversation_id']}")

    # DELETE (Limpieza)
    await asyncio.to_thread(
        lambda: client.table("conversations").delete().eq("conversation_id", test_conversation_id).execute()
    )
    verify_delete_conv = await asyncio.to_thread(
        lambda: client.table("conversations").select("*").eq("conversation_id", test_conversation_id).execute()
    )
    assert not verify_delete_conv.data, "La conversación no fue eliminada."
    logger.info(f"Conversación eliminada: {test_conversation_id}")

    # Limpiar el cliente creado para esta prueba
    await asyncio.to_thread(
        lambda: client.table("customers").delete().eq("id", test_customer_id).execute()
    )
    logger.info(f"Cliente de prueba para conversación eliminado: {test_customer_id}")

# Consideraciones para estas pruebas de Supabase:
# 1. Dependencia de DB Externa: Estas pruebas requieren una instancia de Supabase activa y accesible.
#    Idealmente, se ejecutarían contra una base de datos de prueba dedicada.
# 2. Limpieza de Datos: Es crucial limpiar los datos creados durante las pruebas para evitar
#    interferencias entre ejecuciones y acumulación de datos de prueba.
#    El uso de UUIDs únicos ayuda a aislar las pruebas.
# 3. Configuración: Las credenciales de Supabase deben estar en el entorno (e.g., .env).
#    El fixture `db_client` salta las pruebas si no se encuentran.
# 4. Transacciones: Supabase (PostgREST) no soporta transacciones tradicionales a través de la API HTTP
#    de la misma forma que un ORM con conexión directa a DB. Cada request es atómico.
#    Para rollbacks automáticos, se necesitaría una conexión directa a PostgreSQL.
# 5. Mocking: Para pruebas unitarias del código que *usa* el `supabase_client`, se debería mockear
#    el cliente Supabase para aislar el código de la base de datos real.
#    Estas pruebas son de *integración*.