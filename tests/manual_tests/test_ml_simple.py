#!/usr/bin/env python3
"""
Test Simple del Sistema ML Adaptativo

Prueba básica para validar que los servicios ML están funcionando.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Añadir src al path
sys.path.append(str(Path(__file__).parent / 'src'))

async def test_ml_imports():
    """Test básico de importación de servicios ML."""
    logger.info("🧪 Testing ML imports...")
    
    try:
        # Test 1: Importar servicios ML básicos
        from src.services.conversation_outcome_tracker import ConversationOutcomeTracker
        logger.info("✅ ConversationOutcomeTracker importado correctamente")
        
        from src.services.adaptive_learning_service import AdaptiveLearningService
        logger.info("✅ AdaptiveLearningService importado correctamente")
        
        from src.services.ab_testing_framework import ABTestingFramework
        logger.info("✅ ABTestingFramework importado correctamente")
        
        from src.models.learning_models import AdaptiveLearningConfig
        logger.info("✅ AdaptiveLearningConfig importado correctamente")
        
        # Test 2: Crear instancias básicas
        tracker = ConversationOutcomeTracker()
        logger.info("✅ ConversationOutcomeTracker instanciado")
        
        learning_service = AdaptiveLearningService(tracker)
        logger.info("✅ AdaptiveLearningService instanciado")
        
        config = AdaptiveLearningConfig()
        ab_framework = ABTestingFramework(config)
        logger.info("✅ ABTestingFramework instanciado")
        
        # Test 3: Verificar métodos principales
        learning_summary = learning_service.get_learning_summary()
        assert isinstance(learning_summary, dict), "Learning summary debe ser un diccionario"
        logger.info(f"✅ Learning summary obtenido: {learning_summary}")
        
        # Test 4: Verificar que el tracker tiene los métodos necesarios
        assert hasattr(tracker, 'start_tracking_conversation'), "Método start_tracking_conversation faltante"
        assert hasattr(tracker, 'update_conversation_metrics'), "Método update_conversation_metrics faltante"
        assert hasattr(tracker, 'record_conversation_outcome'), "Método record_conversation_outcome faltante"
        logger.info("✅ Todos los métodos del tracker están presentes")
        
        # Test 5: Verificar que el AB framework tiene los métodos necesarios
        assert hasattr(ab_framework, 'get_active_experiments'), "Método get_active_experiments faltante"
        assert hasattr(ab_framework, 'record_experiment_outcome'), "Método record_experiment_outcome faltante"
        logger.info("✅ Todos los métodos del AB framework están presentes")
        
        logger.info("🎉 TODOS LOS TESTS ML BÁSICOS PASARON EXITOSAMENTE")
        return True
        
    except ImportError as e:
        logger.error(f"❌ Error de importación: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"❌ Error en tests ML: {str(e)}")
        return False

async def test_ml_conversation_tracker():
    """Test del tracker de conversaciones."""
    logger.info("🧪 Testing ConversationOutcomeTracker...")
    
    try:
        from src.services.conversation_outcome_tracker import ConversationOutcomeTracker
        from src.models.conversation import Message
        from datetime import datetime
        
        # Crear tracker
        tracker = ConversationOutcomeTracker()
        
        # Test datos de cliente simulados
        test_conversation_id = "test_conv_001"
        client_data = {
            "customer_id": "test_customer_001",
            "program_type": "PRIME",
            "age": 35,
            "interests": ["fitness", "productividad"]
        }
        
        # Iniciar tracking
        await tracker.start_tracking_conversation(
            conversation_id=test_conversation_id,
            initial_client_data=client_data,
            experiment_assignments=[]
        )
        logger.info("✅ Tracking iniciado correctamente")
        
        # Obtener resumen
        summary = tracker.get_conversation_summary(test_conversation_id)
        assert summary is not None, "Summary no debe ser None"
        assert summary['conversation_id'] == test_conversation_id, "ID de conversación incorrecto"
        logger.info(f"✅ Summary obtenido: {summary}")
        
        # Crear mensaje simulado
        test_message = Message(
            role="user", 
            content="Hola, estoy interesado en el programa PRIME",
            timestamp=datetime.now()
        )
        
        # Actualizar métricas
        await tracker.update_conversation_metrics(
            conversation_id=test_conversation_id,
            message=test_message,
            response_time_seconds=2.5,
            additional_metrics={"emotional_intelligence_score": 0.8}
        )
        logger.info("✅ Métricas actualizadas correctamente")
        
        # Obtener summary actualizado
        updated_summary = tracker.get_conversation_summary(test_conversation_id)
        assert updated_summary['message_count'] >= 1, "Contador de mensajes no actualizado"
        logger.info("✅ Summary actualizado correctamente")
        
        logger.info("🎉 CONVERSATION TRACKER TESTS PASARON EXITOSAMENTE")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en conversation tracker tests: {str(e)}")
        return False

async def main():
    """Función principal."""
    logger.info("🚀 Iniciando tests ML simplificados...")
    
    # Test 1: Imports básicos
    test1_result = await test_ml_imports()
    
    # Test 2: Conversation tracker
    test2_result = await test_ml_conversation_tracker()
    
    # Resumen final
    total_tests = 2
    passed_tests = sum([test1_result, test2_result])
    success_rate = (passed_tests / total_tests) * 100
    
    logger.info("\n" + "="*50)
    logger.info("📊 RESUMEN DE TESTS ML SIMPLIFICADOS")
    logger.info("="*50)
    logger.info(f"📈 TOTAL TESTS: {total_tests}")
    logger.info(f"✅ PASSED: {passed_tests}")
    logger.info(f"❌ FAILED: {total_tests - passed_tests}")
    logger.info(f"🎯 SUCCESS RATE: {success_rate:.1f}%")
    
    if success_rate >= 100.0:
        logger.info("\n🎉 RESULTADO: SERVICIOS ML BÁSICOS FUNCIONANDO CORRECTAMENTE")
        return True
    else:
        logger.error("\n💥 RESULTADO: ALGUNOS SERVICIOS ML REQUIEREN CORRECCIONES")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n⚡ Tests interrumpidos por usuario")
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 Error crítico: {str(e)}")
        sys.exit(1)