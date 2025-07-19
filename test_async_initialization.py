#!/usr/bin/env python3
"""
Test script para verificar que la inicialización asíncrona funciona correctamente.
"""

import asyncio
import sys
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent))

async def test_services_initialization():
    """Test de inicialización de servicios predictivos."""
    print("🔧 Iniciando test de inicialización asíncrona...")
    
    try:
        # Importar servicios
        from src.integrations.supabase.resilient_client import ResilientSupabaseClient
        from src.services.predictive_model_service import PredictiveModelService
        from src.services.nlp_integration_service import NLPIntegrationService
        from src.services.entity_recognition_service import EntityRecognitionService
        from src.services.objection_prediction_service import ObjectionPredictionService
        from src.services.needs_prediction_service import NeedsPredictionService
        from src.services.conversion_prediction_service import ConversionPredictionService
        from src.services.decision_engine_service import DecisionEngineService
        
        print("✅ Imports completados")
        
        # Instanciar servicios base
        print("\n📦 Instanciando servicios base...")
        supabase_client = ResilientSupabaseClient()
        predictive_model_service = PredictiveModelService(supabase_client)
        nlp_integration_service = NLPIntegrationService()
        entity_recognition_service = EntityRecognitionService()
        print("✅ Servicios base instanciados")
        
        # Test ObjectionPredictionService
        print("\n🔍 Probando ObjectionPredictionService...")
        objection_service = ObjectionPredictionService(
            supabase_client,
            predictive_model_service,
            nlp_integration_service
        )
        await objection_service.initialize()
        print("✅ ObjectionPredictionService inicializado correctamente")
        
        # Test NeedsPredictionService
        print("\n🔍 Probando NeedsPredictionService...")
        needs_service = NeedsPredictionService(
            supabase_client,
            predictive_model_service,
            nlp_integration_service,
            entity_recognition_service
        )
        await needs_service.initialize()
        print("✅ NeedsPredictionService inicializado correctamente")
        
        # Test ConversionPredictionService
        print("\n🔍 Probando ConversionPredictionService...")
        conversion_service = ConversionPredictionService(
            supabase_client,
            predictive_model_service,
            nlp_integration_service
        )
        await conversion_service.initialize()
        print("✅ ConversionPredictionService inicializado correctamente")
        
        # Test DecisionEngineService
        print("\n🔍 Probando DecisionEngineService...")
        decision_service = DecisionEngineService(
            supabase_client,
            predictive_model_service,
            nlp_integration_service,
            objection_service,
            needs_service,
            conversion_service
        )
        await decision_service.initialize()
        print("✅ DecisionEngineService inicializado correctamente")
        
        # Test predict methods
        print("\n🧪 Probando métodos de predicción...")
        test_messages = [
            {"role": "user", "content": "¿Cuál es el precio del producto?"},
            {"role": "assistant", "content": "El precio base es de $299 al mes."},
            {"role": "user", "content": "Me parece un poco caro..."}
        ]
        
        # Test objection prediction
        objection_result = await objection_service.predict_objections(
            conversation_id="test-123",
            messages=test_messages
        )
        print(f"✅ Predicción de objeciones: {objection_result.get('objections', [])}")
        
        # Test needs prediction
        needs_result = await needs_service.predict_needs(
            conversation_id="test-123",
            messages=test_messages
        )
        print(f"✅ Predicción de necesidades: {needs_result.get('needs', [])}")
        
        # Test conversion prediction
        conversion_result = await conversion_service.predict_conversion(
            conversation_id="test-123",
            messages=test_messages
        )
        print(f"✅ Predicción de conversión: {conversion_result.get('probability', 0):.2%}")
        
        print("\n🎉 ¡Todos los tests pasaron exitosamente!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error durante el test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_api_endpoints():
    """Test de endpoints de API."""
    print("\n\n🌐 Probando endpoints de API...")
    
    try:
        from src.api.routers.predictive import get_services
        
        # Test lazy initialization
        print("📦 Probando inicialización lazy de servicios...")
        services = await get_services()
        
        print("✅ Servicios obtenidos:")
        for name, service in services.items():
            print(f"   - {name}: {type(service).__name__}")
        
        # Verificar que los servicios estén inicializados
        assert services["objection"]._initialized, "ObjectionPredictionService no inicializado"
        assert services["needs"]._initialized, "NeedsPredictionService no inicializado"
        assert services["conversion"]._initialized, "ConversionPredictionService no inicializado"
        assert services["decision"]._initialized, "DecisionEngineService no inicializado"
        
        print("✅ Todos los servicios están correctamente inicializados")
        
        # Test segunda llamada (debe usar cache)
        print("\n📦 Probando cache de servicios...")
        services2 = await get_services()
        assert services["objection"] is services2["objection"], "Los servicios no están siendo cacheados"
        print("✅ Cache funcionando correctamente")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error durante el test de API: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Función principal de test."""
    print("=" * 60)
    print("TEST DE INICIALIZACIÓN ASÍNCRONA")
    print("=" * 60)
    
    # Test servicios individuales
    test1_passed = await test_services_initialization()
    
    # Test endpoints de API
    test2_passed = await test_api_endpoints()
    
    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE TESTS")
    print("=" * 60)
    print(f"Test de servicios individuales: {'✅ PASÓ' if test1_passed else '❌ FALLÓ'}")
    print(f"Test de endpoints de API: {'✅ PASÓ' if test2_passed else '❌ FALLÓ'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 ¡Todos los tests pasaron exitosamente!")
        return 0
    else:
        print("\n❌ Algunos tests fallaron. Revisa los errores arriba.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)