"""
Script para probar el servicio de análisis de intención de compra.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from src.services.intent_analysis_service import IntentAnalysisService

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

async def test_intent_analysis():
    """Probar el análisis de intención de compra."""
    
    # Inicializar el servicio
    intent_service = IntentAnalysisService()
    
    # Caso 1: Conversación sin intención de compra
    messages_no_intent = [
        {"role": "user", "content": "Hola, quiero saber más sobre el programa"},
        {"role": "assistant", "content": "Claro, nuestro programa ofrece entrenamiento personalizado y seguimiento nutricional"},
        {"role": "user", "content": "¿Cuánto tiempo lleva ver resultados?"},
        {"role": "assistant", "content": "La mayoría de nuestros clientes ven resultados en 4-6 semanas"},
        {"role": "user", "content": "Interesante, lo pensaré"}
    ]
    
    # Caso 2: Conversación con intención de compra
    messages_with_intent = [
        {"role": "user", "content": "Hola, quiero saber más sobre el programa"},
        {"role": "assistant", "content": "Claro, nuestro programa ofrece entrenamiento personalizado y seguimiento nutricional"},
        {"role": "user", "content": "¿Cuánto cuesta el programa?"},
        {"role": "assistant", "content": "El programa tiene un costo de $99 mensuales"},
        {"role": "user", "content": "Me interesa, ¿puedo pagar con tarjeta de crédito?"}
    ]
    
    # Caso 3: Conversación con rechazo explícito
    messages_with_rejection = [
        {"role": "user", "content": "Hola, quiero saber más sobre el programa"},
        {"role": "assistant", "content": "Claro, nuestro programa ofrece entrenamiento personalizado y seguimiento nutricional"},
        {"role": "user", "content": "¿Cuánto cuesta el programa?"},
        {"role": "assistant", "content": "El programa tiene un costo de $99 mensuales"},
        {"role": "user", "content": "Es muy caro, no me interesa por ahora"}
    ]
    
    # Probar análisis de intención
    logger.info("Caso 1: Conversación sin intención de compra")
    result_no_intent = intent_service.analyze_purchase_intent(messages_no_intent)
    logger.info(f"Resultado: {result_no_intent}")
    
    logger.info("\nCaso 2: Conversación con intención de compra")
    result_with_intent = intent_service.analyze_purchase_intent(messages_with_intent)
    logger.info(f"Resultado: {result_with_intent}")
    
    logger.info("\nCaso 3: Conversación con rechazo explícito")
    result_with_rejection = intent_service.analyze_purchase_intent(messages_with_rejection)
    logger.info(f"Resultado: {result_with_rejection}")
    
    # Probar corte inteligente
    logger.info("\nProbando corte inteligente:")
    
    # Caso 1: Tiempo no excedido
    session_start_recent = datetime.now() - timedelta(minutes=2)
    should_continue, reason = intent_service.should_continue_conversation(
        messages_no_intent, 
        session_start_recent,
        180  # 3 minutos
    )
    logger.info(f"Caso 1 (tiempo no excedido): Continuar={should_continue}, Razón={reason}")
    
    # Caso 2: Tiempo excedido, sin intención
    session_start_old = datetime.now() - timedelta(minutes=4)
    should_continue, reason = intent_service.should_continue_conversation(
        messages_no_intent, 
        session_start_old,
        180  # 3 minutos
    )
    logger.info(f"Caso 2 (tiempo excedido, sin intención): Continuar={should_continue}, Razón={reason}")
    
    # Caso 3: Tiempo excedido, con intención
    should_continue, reason = intent_service.should_continue_conversation(
        messages_with_intent, 
        session_start_old,
        180  # 3 minutos
    )
    logger.info(f"Caso 3 (tiempo excedido, con intención): Continuar={should_continue}, Razón={reason}")
    
    # Caso 4: Tiempo excedido, con rechazo
    should_continue, reason = intent_service.should_continue_conversation(
        messages_with_rejection, 
        session_start_old,
        180  # 3 minutos
    )
    logger.info(f"Caso 4 (tiempo excedido, con rechazo): Continuar={should_continue}, Razón={reason}")

if __name__ == "__main__":
    asyncio.run(test_intent_analysis())
