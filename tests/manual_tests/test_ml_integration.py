#!/usr/bin/env python3
"""
Test de Integración del Sistema ML Adaptativo en ConversationService

Este script valida que el sistema ML adaptativo esté completamente integrado
y funcionando correctamente en el ConversationService.

Ejecutar: python test_ml_integration.py
"""

import asyncio
import logging
import sys
import json
from datetime import datetime
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Añadir src al path
sys.path.append(str(Path(__file__).parent / 'src'))

# Importar servicios necesarios
from src.services.conversation_service import ConversationService
from src.models.conversation import CustomerData
from src.models.platform_context import PlatformInfo, SourceType

class MLIntegrationTester:
    """Tester para validar integración ML en ConversationService."""
    
    def __init__(self):
        self.conversation_service = None
        self.test_results = []
        
    async def setup(self):
        """Configurar el test environment."""
        try:
            logger.info("🔧 Configurando test environment...")
            
            # Inicializar ConversationService
            self.conversation_service = ConversationService(industry='fitness')
            
            # Configurar platform context
            platform_info = PlatformInfo(
                source=SourceType.WEB_WIDGET,
                source_type="lead_magnet",
                campaign_id="test_ml_integration"
            )
            
            logger.info("✅ Test environment configurado correctamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error configurando test environment: {str(e)}")
            return False
    
    async def test_ml_services_initialization(self):
        """Test 1: Verificar que los servicios ML están inicializados."""
        logger.info("🧪 Test 1: Inicialización de servicios ML")
        
        try:
            # Verificar que los servicios ML están inicializados
            assert hasattr(self.conversation_service, 'outcome_tracker'), "OutcomeTracker no inicializado"
            assert hasattr(self.conversation_service, 'adaptive_learning_service'), "AdaptiveLearningService no inicializado"
            assert hasattr(self.conversation_service, 'ab_testing_framework'), "ABTestingFramework no inicializado"
            assert hasattr(self.conversation_service, 'active_experiments'), "Cache de experimentos no inicializado"
            
            logger.info("✅ Test 1 PASSED: Todos los servicios ML están inicializados")
            self.test_results.append({"test": "ml_services_initialization", "status": "PASSED"})
            return True
            
        except AssertionError as e:
            logger.error(f"❌ Test 1 FAILED: {str(e)}")
            self.test_results.append({"test": "ml_services_initialization", "status": "FAILED", "error": str(e)})
            return False
        except Exception as e:
            logger.error(f"❌ Test 1 ERROR: {str(e)}")
            self.test_results.append({"test": "ml_services_initialization", "status": "ERROR", "error": str(e)})
            return False
    
    async def test_conversation_start_with_ml_tracking(self):
        """Test 2: Verificar que el tracking ML se inicia correctamente."""
        logger.info("🧪 Test 2: Inicio de tracking ML en nueva conversación")
        
        try:
            # Crear datos de cliente de prueba
            customer_data = CustomerData(
                id="test_client_001",
                name="Carlos Testeo",
                age=35,
                interests=["fitness", "productividad"]
            )
            
            # Iniciar conversación
            state = await self.conversation_service.start_conversation(customer_data)
            
            # Verificar que la conversación se creó
            assert state is not None, "Estado de conversación no creado"
            assert state.id is not None, "ID de conversación no asignado"
            
            # Verificar que el tracking ML está activo
            ml_summary = await self.conversation_service.get_ml_conversation_summary(state.id)
            assert ml_summary is not None, "Tracking ML no iniciado"
            
            logger.info(f"✅ Test 2 PASSED: Tracking ML iniciado para conversación {state.id}")
            self.test_results.append({
                "test": "conversation_start_ml_tracking", 
                "status": "PASSED",
                "conversation_id": state.id
            })
            return state
            
        except Exception as e:
            logger.error(f"❌ Test 2 FAILED: {str(e)}")
            self.test_results.append({"test": "conversation_start_ml_tracking", "status": "FAILED", "error": str(e)})
            return None
    
    async def test_message_processing_with_ml_updates(self, state):
        """Test 3: Verificar que las métricas ML se actualizan durante mensajes."""
        logger.info("🧪 Test 3: Actualización de métricas ML durante procesamiento")
        
        if not state:
            logger.error("❌ Test 3 SKIPPED: No hay estado de conversación")
            self.test_results.append({"test": "message_processing_ml_updates", "status": "SKIPPED"})
            return False
        
        try:
            # Procesar un mensaje de prueba
            test_message = "Hola, estoy interesado en mejorar mi rendimiento físico y mental"
            
            # Obtener resumen ML antes del mensaje
            ml_before = await self.conversation_service.get_ml_conversation_summary(state.id)
            message_count_before = ml_before.get("message_count", 0) if ml_before else 0
            
            # Procesar mensaje (esto debería actualizar métricas ML)
            updated_state, audio_response = await self.conversation_service.process_message(
                conversation_id=state.id,
                message_text=test_message
            )
            
            # Obtener resumen ML después del mensaje
            ml_after = await self.conversation_service.get_ml_conversation_summary(state.id)
            
            # Verificar que las métricas se actualizaron
            assert ml_after is not None, "Resumen ML no disponible después del mensaje"
            message_count_after = ml_after.get("message_count", 0)
            assert message_count_after > message_count_before, "Contador de mensajes no actualizado"
            
            # Verificar que hay métricas actuales
            current_metrics = ml_after.get("current_metrics", {})
            assert len(current_metrics) > 0, "Métricas actuales no disponibles"
            
            logger.info(f"✅ Test 3 PASSED: Métricas ML actualizadas (mensajes: {message_count_before} → {message_count_after})")
            self.test_results.append({
                "test": "message_processing_ml_updates", 
                "status": "PASSED",
                "metrics_before": message_count_before,
                "metrics_after": message_count_after
            })
            return updated_state
            
        except Exception as e:
            logger.error(f"❌ Test 3 FAILED: {str(e)}")
            self.test_results.append({"test": "message_processing_ml_updates", "status": "FAILED", "error": str(e)})
            return state
    
    async def test_adaptive_learning_status(self):
        """Test 4: Verificar que el estado del sistema adaptativo es accesible."""
        logger.info("🧪 Test 4: Estado del sistema de aprendizaje adaptativo")
        
        try:
            # Obtener estado del sistema de aprendizaje
            learning_status = await self.conversation_service.get_adaptive_learning_status()
            
            # Verificar que el estado es válido
            assert learning_status is not None, "Estado de aprendizaje no disponible"
            assert isinstance(learning_status, dict), "Estado de aprendizaje no es un diccionario"
            
            # Log del estado para debugging
            logger.info(f"Estado del sistema ML: {json.dumps(learning_status, indent=2, default=str)}")
            
            logger.info("✅ Test 4 PASSED: Estado del sistema de aprendizaje accesible")
            self.test_results.append({
                "test": "adaptive_learning_status", 
                "status": "PASSED",
                "learning_status": learning_status
            })
            return True
            
        except Exception as e:
            logger.error(f"❌ Test 4 FAILED: {str(e)}")
            self.test_results.append({"test": "adaptive_learning_status", "status": "FAILED", "error": str(e)})
            return False
    
    async def test_conversation_outcome_recording(self, state):
        """Test 5: Verificar que los outcomes se registran correctamente para ML."""
        logger.info("🧪 Test 5: Registro de outcome para ML")
        
        if not state:
            logger.error("❌ Test 5 SKIPPED: No hay estado de conversación")
            self.test_results.append({"test": "conversation_outcome_recording", "status": "SKIPPED"})
            return False
        
        try:
            # Simular un outcome de conversación
            await self.conversation_service._record_conversation_outcome_for_ml(
                state=state,
                outcome_type="test_completed",
                additional_context={
                    "tier_accepted": "PRIME_pro",
                    "satisfaction_score": 8.5,
                    "test_mode": True
                }
            )
            
            logger.info("✅ Test 5 PASSED: Outcome registrado correctamente para ML")
            self.test_results.append({
                "test": "conversation_outcome_recording", 
                "status": "PASSED",
                "outcome_type": "test_completed"
            })
            return True
            
        except Exception as e:
            logger.error(f"❌ Test 5 FAILED: {str(e)}")
            self.test_results.append({"test": "conversation_outcome_recording", "status": "FAILED", "error": str(e)})
            return False
    
    def print_test_summary(self):
        """Imprimir resumen de todos los tests."""
        logger.info("\n" + "="*60)
        logger.info("📊 RESUMEN DE TESTS ML INTEGRATION")
        logger.info("="*60)
        
        passed_tests = [t for t in self.test_results if t["status"] == "PASSED"]
        failed_tests = [t for t in self.test_results if t["status"] == "FAILED"]
        error_tests = [t for t in self.test_results if t["status"] == "ERROR"]
        skipped_tests = [t for t in self.test_results if t["status"] == "SKIPPED"]
        
        total_tests = len(self.test_results)
        success_rate = (len(passed_tests) / total_tests * 100) if total_tests > 0 else 0
        
        logger.info(f"📈 TOTAL TESTS: {total_tests}")
        logger.info(f"✅ PASSED: {len(passed_tests)}")
        logger.info(f"❌ FAILED: {len(failed_tests)}")
        logger.info(f"🔥 ERROR: {len(error_tests)}")
        logger.info(f"⏭️  SKIPPED: {len(skipped_tests)}")
        logger.info(f"🎯 SUCCESS RATE: {success_rate:.1f}%")
        
        if failed_tests or error_tests:
            logger.info("\n🔍 DETALLES DE FALLOS:")
            for test in failed_tests + error_tests:
                logger.error(f"  - {test['test']}: {test.get('error', 'Unknown error')}")
        
        # Determinar resultado final
        if success_rate >= 80.0:
            logger.info("\n🎉 RESULTADO: SISTEMA ML ADAPTATIVO INTEGRADO EXITOSAMENTE")
            return True
        else:
            logger.error("\n💥 RESULTADO: INTEGRACIÓN ML REQUIERE CORRECCIONES")
            return False

async def main():
    """Función principal de testing."""
    logger.info("🚀 Iniciando tests de integración ML adaptativo...")
    
    tester = MLIntegrationTester()
    
    # Setup
    if not await tester.setup():
        logger.error("💥 Setup falló, abortando tests")
        return False
    
    # Ejecutar tests secuencialmente
    await tester.test_ml_services_initialization()
    
    # Test de conversación (devuelve state para tests siguientes)
    state = await tester.test_conversation_start_with_ml_tracking()
    
    # Tests que dependen del state
    final_state = await tester.test_message_processing_with_ml_updates(state)
    await tester.test_adaptive_learning_status()
    await tester.test_conversation_outcome_recording(final_state)
    
    # Mostrar resumen
    success = tester.print_test_summary()
    
    return success

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n⚡ Tests interrumpidos por usuario")
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 Error crítico ejecutando tests: {str(e)}")
        sys.exit(1)