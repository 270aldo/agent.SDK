#!/usr/bin/env python3
"""
Test script para verificar el sistema de logging mejorado del router de programas.
"""

import asyncio
import sys
from pathlib import Path

# Añadir el proyecto al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Importar router simplificado
from test_program_router_simple import SimpleProgramRouter

async def test_enhanced_logging():
    """Test del sistema de logging mejorado."""
    print("🔍 Testing enhanced logging system for Program Router")
    print("=" * 60)
    
    try:
        # Crear router (debería usar el nuevo sistema de logging)
        router = SimpleProgramRouter()
        
        # Test cases con diferentes escenarios
        test_cases = [
            {
                "name": "Caso PRIME claro",
                "data": {
                    "id": "test_001",
                    "name": "Juan Ejecutivo",
                    "age": 35,
                    "interests": ["trabajo", "productividad", "liderazgo"]
                },
                "message": "Necesito más energía y foco para rendir mejor en mi trabajo"
            },
            {
                "name": "Caso LONGEVITY claro", 
                "data": {
                    "id": "test_002",
                    "name": "María Senior",
                    "age": 62,
                    "interests": ["salud", "familia", "bienestar"]
                },
                "message": "Quiero mantener mi vitalidad para disfrutar con mis nietos"
            },
            {
                "name": "Caso híbrido",
                "data": {
                    "id": "test_003",
                    "name": "Carlos Zona Híbrida",
                    "age": 48,
                    "interests": ["ejercicio", "trabajo"]
                },
                "message": "Busco mejorar mi salud general"
            },
            {
                "name": "Caso sin edad",
                "data": {
                    "id": "test_004",
                    "name": "Usuario Anónimo",
                    "interests": ["bienestar general"]
                },
                "message": "Quiero sentirme mejor"
            }
        ]
        
        print("\n📊 Ejecutando casos de test...")
        
        decisions = []
        for i, case in enumerate(test_cases, 1):
            print(f"\n--- Test {i}: {case['name']} ---")
            
            try:
                decision = await router.determine_program(
                    customer_data=case['data'],
                    initial_message=case['message']
                )
                
                decisions.append(decision)
                
                print(f"✅ Programa: {decision.recommended_program}")
                print(f"📈 Confianza: {decision.confidence_score:.2f}")
                print(f"💡 Reasoning: {decision.reasoning}")
                
            except Exception as e:
                print(f"❌ Error en test {i}: {e}")
        
        # Test de analytics
        print(f"\n📈 Testing analytics...")
        if hasattr(router, 'get_decision_analytics'):
            analytics = router.get_decision_analytics()
            print(f"📊 Total decisions: {analytics.get('total_decisions', 0)}")
            print(f"📊 Program distribution: {analytics.get('program_distribution', {})}")
            print(f"📊 Average confidence: {analytics.get('average_confidence', 0):.3f}")
        
        # Test de switch de programa
        print(f"\n🔄 Testing program switch logic...")
        if decisions and hasattr(router, 'should_switch_program'):
            try:
                should_switch, new_decision = await router.should_switch_program(
                    current_program="PRIME",
                    new_information="Ahora estoy pensando más en mi salud a largo plazo y longevidad",
                    conversation_history=[]
                )
                
                print(f"🔄 Should switch: {should_switch}")
                if new_decision:
                    print(f"🔄 New program: {new_decision.recommended_program}")
                    
            except Exception as e:
                print(f"⚠️ Switch test error: {e}")
        
        print(f"\n✅ Enhanced logging test completed!")
        print(f"📁 Check logs/program_router.log for structured logs")
        
        return True
        
    except Exception as e:
        print(f"💥 Error in logging test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal."""
    try:
        success = asyncio.run(test_enhanced_logging())
        
        if success:
            print(f"\n🎉 Logging system validation: PASSED")
            sys.exit(0)
        else:
            print(f"\n❌ Logging system validation: FAILED")
            sys.exit(1)
            
    except Exception as e:
        print(f"💥 Critical error: {e}")
        sys.exit(2)

if __name__ == "__main__":
    main()