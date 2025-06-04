#!/usr/bin/env python3
import pytest
pytest.skip("manual script", allow_module_level=True)
"""
Script para probar las capacidades del agente de ventas NGX refactorizado con SDK de OpenAI Agents.
Permite enviar mensajes específicos y observar la respuesta del agente.
"""

import os
import asyncio
import argparse
import logging
from dotenv import load_dotenv

print("DEBUG: Comienzo del script test_agent.py")

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
print("DEBUG: Logging configurado.")

# Cargar variables de entorno
load_dotenv()
print("DEBUG: load_dotenv() llamado.")

# Importar componentes necesarios
print("DEBUG: Intentando importar CustomerData y ConversationService...")
from src.models.conversation import CustomerData
from src.services.conversation_service import ConversationService # Usaremos nuestro servicio refactorizado
print("DEBUG: CustomerData y ConversationService importados.")

async def test_agent_interaction(
    customer_name: str,
    program_type: str = "PRIME",
    test_messages: list[str] = None
):
    print(f"DEBUG: Dentro de test_agent_interaction para {customer_name}")
    """
    Simula interacciones específicas con el agente a través del ConversationService.
    
    Args:
        customer_name (str): Nombre del cliente.
        program_type (str): Tipo de programa ("PRIME" o "LONGEVITY").
        test_messages (list[str]): Lista de mensajes para enviar al agente secuencialmente.
    """
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("La variable de entorno OPENAI_API_KEY no está configurada. Por favor, configúrala en tu archivo .env")
        print("DEBUG: OPENAI_API_KEY no encontrada.") # DEBUG
        return
    print("DEBUG: OPENAI_API_KEY encontrada.") # DEBUG

    # Inicializar el servicio de conversación
    print("DEBUG: Inicializando ConversationService...") # DEBUG
    service = ConversationService()
    print("DEBUG: ConversationService inicializado.") # DEBUG
    
    # Crear datos de cliente de prueba
    print("DEBUG: Creando CustomerData...") # DEBUG
    customer = CustomerData(
        name=customer_name,
        email=f"{customer_name.lower().replace(' ', '.')}@example.com",
        age=42, # Pydantic validará la edad
        gender="male",
        occupation="CEO",
        goals={
            "primary": "aumentar energía y rendimiento",
            "secondary": ["mejorar concentración", "gestionar estrés"]
        }
    )
    print("DEBUG: CustomerData creado.") # DEBUG
    
    # 1. Iniciar conversación
    logger.info(f"--- Iniciando conversación para {customer_name} sobre el programa {program_type} ---")
    print(f"DEBUG: Intentando iniciar conversación para {customer_name}...") # DEBUG
    try:
        state = await service.start_conversation(customer_data=customer, program_type=program_type)
        conversation_id = state.id
        logger.info(f"Conversación iniciada con ID: {conversation_id}")
        initial_message = state.messages[-1]
        print(f"\n🤖 Agente NGX ({initial_message.role}): {initial_message.content}\n")
        print(f"DEBUG: Conversación iniciada exitosamente para {customer_name}.") # DEBUG

    except Exception as e:
        logger.error(f"Error al iniciar la conversación: {e}", exc_info=True)
        print(f"DEBUG: Error al iniciar conversación: {e}") # DEBUG
        return

    if not test_messages:
        logger.info("No se proporcionaron mensajes de prueba. Finalizando.")
        print("DEBUG: No hay mensajes de prueba, finalizando test_agent_interaction.") # DEBUG
        return
    print("DEBUG: Procesando mensajes de prueba...") # DEBUG
    # 2. Procesar mensajes de prueba
    for i, user_message_text in enumerate(test_messages):
        logger.info(f"--- Enviando Mensaje de Prueba #{i+1} --- ")
        print(f"DEBUG: Enviando mensaje: {user_message_text}") # DEBUG
        print(f"👤 {customer_name}: {user_message_text}")
        
        try:
            updated_state, audio_stream = await service.process_message(
                conversation_id=conversation_id, 
                message_text=user_message_text
            )
            agent_response_message = updated_state.messages[-1]
            print(f"\n🤖 Agente NGX ({agent_response_message.role}): {agent_response_message.content}\n")
            print(f"DEBUG: Mensaje procesado exitosamente: {user_message_text}") # DEBUG

        except Exception as e:
            logger.error(f"Error al procesar el mensaje '{user_message_text}': {e}", exc_info=True)
            print(f"DEBUG: Error procesando mensaje '{user_message_text}': {e}") # DEBUG
            continue 

    logger.info("--- Simulación de interacción finalizada ---")
    print("DEBUG: Fin de test_agent_interaction.") # DEBUG

def main():
    print("DEBUG: Dentro de main().") # DEBUG
    """Función principal."""
    parser = argparse.ArgumentParser(description="Probar interacciones específicas con el Agente de Ventas NGX usando SDK")
    parser.add_argument("--name", default="Ana Torres", help="Nombre del cliente de prueba")
    parser.add_argument("--program", choices=["PRIME", "LONGEVITY"], default="PRIME", help="Tipo de programa")
    
    args = parser.parse_args()
    print(f"DEBUG: Argumentos parseados: {args}") # DEBUG

    # --- Definir aquí los escenarios de prueba --- 
    escenario_1_detalles_prime = [
        "Hola, ¿qué tal?",
        "Cuéntame más sobre el programa PRIME.",
        "¿Cuál es el precio de PRIME?"
    ]

    escenario_2_objecion_longevity = [
        "Me interesa Longevity, pero suena un poco caro.",
        "¿Qué resultados puedo esperar?"
    ]
    
    escenario_3_flujo_natural_prime = [
        "Busco mejorar mi energía durante el día.",
        "¿Qué incluye el programa PRIME exactamente?",
        "El precio me parece un poco alto, ¿hay opciones?"
    ]

    # --- Ejecutar escenarios --- 
    # Descomenta los escenarios que quieres probar
    
    logger.info("\n========== INICIANDO ESCENARIO 1: Detalles del Programa PRIME ==========")
    print("DEBUG: Llamando a asyncio.run para escenario_1_detalles_prime...") # DEBUG
    asyncio.run(test_agent_interaction(
        customer_name=args.name,
        program_type="PRIME",
        test_messages=escenario_1_detalles_prime
    ))
    print("DEBUG: asyncio.run para escenario_1_detalles_prime completado.") # DEBUG

    # logger.info("\n========== INICIANDO ESCENARIO 2: Objeción de Precio LONGEVITY ==========")
    # asyncio.run(test_agent_interaction(
    #     customer_name="Roberto Diaz",
    #     program_type="LONGEVITY",
    #     test_messages=escenario_2_objecion_longevity
    # ))
    
    # logger.info("\n========== INICIANDO ESCENARIO 3: Flujo Natural con Objeción PRIME ==========")
    # asyncio.run(test_agent_interaction(
    #     customer_name="Laura Sanchez",
    #     program_type="PRIME",
    #     test_messages=escenario_3_flujo_natural_prime
    # ))

if __name__ == "__main__":
    print("DEBUG: Bloque if __name__ == '__main__' alcanzado.") # DEBUG
    main()
    print("DEBUG: Fin del script test_agent.py.") # DEBUG 