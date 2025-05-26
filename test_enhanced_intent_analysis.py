"""
Script para probar el servicio de análisis de intención mejorado con el cliente resiliente.
Verifica las capacidades de análisis de intención y reintentos automáticos.
"""

import asyncio
import logging
import sys
import os
import json
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

async def test_enhanced_intent_analysis():
    """Prueba las funcionalidades del servicio de análisis de intención mejorado."""
    from src.services.enhanced_intent_analysis_service import EnhancedIntentAnalysisService
    
    logger.info("=== Iniciando pruebas del servicio de análisis de intención mejorado ===")
    
    # Crear instancia del servicio para la industria de salud
    logger.info("Creando instancia del servicio para la industria de salud...")
    intent_service = await EnhancedIntentAnalysisService.create(industry="salud")
    
    # Mensajes de prueba con intención de compra positiva
    positive_messages = [
        {"role": "assistant", "content": "Hola, ¿en qué puedo ayudarte con nuestros programas de salud?"},
        {"role": "user", "content": "Me interesa saber más sobre el programa de bienestar integral."},
        {"role": "assistant", "content": "Claro, nuestro programa de bienestar integral incluye evaluaciones personalizadas, seguimiento nutricional y rutinas de ejercicio. ¿Te gustaría conocer los precios?"},
        {"role": "user", "content": "Sí, me gustaría saber cuánto cuesta y qué incluye exactamente."},
        {"role": "assistant", "content": "El programa básico cuesta $99 al mes e incluye evaluación inicial, plan personalizado y seguimiento semanal. ¿Te interesaría comenzar con este plan?"},
        {"role": "user", "content": "Suena bien. ¿Puedo pagar con tarjeta de crédito?"}
    ]
    
    # Mensajes de prueba con rechazo
    negative_messages = [
        {"role": "assistant", "content": "Hola, ¿en qué puedo ayudarte con nuestros programas de salud?"},
        {"role": "user", "content": "Solo estoy mirando, gracias."},
        {"role": "assistant", "content": "Entiendo. Nuestro programa de bienestar integral incluye evaluaciones personalizadas. ¿Te gustaría conocer más detalles?"},
        {"role": "user", "content": "No me interesa por ahora, tal vez más adelante."},
        {"role": "assistant", "content": "Claro, no hay problema. ¿Hay algo específico que estés buscando en un programa de salud?"},
        {"role": "user", "content": "No, gracias. No tengo tiempo para esto ahora mismo."}
    ]
    
    # Prueba 1: Análisis de intención en mensajes positivos
    logger.info("Prueba 1: Analizando intención en mensajes positivos...")
    try:
        positive_result = await intent_service.analyze_purchase_intent(positive_messages)
        logger.info(f"Resultado del análisis positivo: {json.dumps(positive_result, indent=2)}")
        
        if positive_result["has_purchase_intent"]:
            logger.info("✅ Prueba exitosa: Se detectó correctamente la intención de compra")
        else:
            logger.warning("❌ Prueba fallida: No se detectó la intención de compra")
    except Exception as e:
        logger.error(f"Error en análisis de mensajes positivos: {e}")
    
    # Prueba 2: Análisis de intención en mensajes negativos
    logger.info("Prueba 2: Analizando intención en mensajes negativos...")
    try:
        negative_result = await intent_service.analyze_purchase_intent(negative_messages)
        logger.info(f"Resultado del análisis negativo: {json.dumps(negative_result, indent=2)}")
        
        if negative_result["has_rejection"]:
            logger.info("✅ Prueba exitosa: Se detectó correctamente el rechazo")
        else:
            logger.warning("❌ Prueba fallida: No se detectó el rechazo")
    except Exception as e:
        logger.error(f"Error en análisis de mensajes negativos: {e}")
    
    # Prueba 3: Verificar si debe continuar la conversación
    logger.info("Prueba 3: Verificando si debe continuar la conversación...")
    try:
        session_start_time = datetime.now()
        should_continue, reason = await intent_service.should_continue_conversation(
            positive_messages, 
            session_start_time,
            intent_detection_timeout=300
        )
        
        logger.info(f"¿Debe continuar la conversación? {should_continue}, Razón: {reason}")
        
        if should_continue:
            logger.info("✅ Prueba exitosa: Se decidió correctamente continuar la conversación")
        else:
            logger.warning("❌ Prueba fallida: Se decidió incorrectamente terminar la conversación")
    except Exception as e:
        logger.error(f"Error al verificar continuación de conversación: {e}")
    
    # Prueba 4: Actualizar modelo desde conversación
    logger.info("Prueba 4: Actualizando modelo desde conversación...")
    try:
        conversation_id = "test_conversation_id"
        conversion_result = True  # Simular que hubo conversión
        
        update_success = await intent_service.update_model_from_conversation(
            conversation_id,
            positive_messages,
            conversion_result
        )
        
        if update_success:
            logger.info("✅ Prueba exitosa: Se actualizó correctamente el modelo")
        else:
            logger.warning("❌ Prueba fallida: No se pudo actualizar el modelo")
    except Exception as e:
        logger.error(f"Error al actualizar modelo: {e}")
    
    logger.info("=== Pruebas del servicio de análisis de intención completadas ===")

if __name__ == "__main__":
    asyncio.run(test_enhanced_intent_analysis())
