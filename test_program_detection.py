#!/usr/bin/env python3
"""
Script de prueba para validar la detección automática de audiencia NGX.
Simula diferentes escenarios de clientes para verificar la precisión del ProgramRouter.
"""

import asyncio
import sys
import os

# Añadir el directorio src al path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.program_router import ProgramRouter
import logging

# Configurar logging para ver el output
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Escenarios de prueba
TEST_SCENARIOS = [
    {
        "name": "Joven profesional tech - PRIME claro",
        "customer_data": {
            "id": "test_1",
            "name": "Carlos",
            "age": 28,
            "interests": ["trabajo", "productividad", "energía", "rendimiento"]
        },
        "message": "Trabajo 12 horas diarias en startup tech, necesito más energía y mejor físico para rendir mejor",
        "expected_program": "PRIME"
    },
    {
        "name": "Adulto mayor preocupado por salud - LONGEVITY claro", 
        "customer_data": {
            "id": "test_2",
            "name": "María",
            "age": 58,
            "interests": ["salud", "familia", "bienestar", "vitalidad"]
        },
        "message": "Quiero mantenerme saludable para ver crecer a mis nietos, me preocupa perder movilidad",
        "expected_program": "LONGEVITY"
    },
    {
        "name": "Zona híbrida - profesional maduro",
        "customer_data": {
            "id": "test_3", 
            "name": "Roberto",
            "age": 47,
            "interests": ["liderazgo", "familia", "salud"]
        },
        "message": "Soy director de empresa, tengo familia, pero quiero estar en forma y tener energía",
        "expected_program": ["PRIME", "LONGEVITY", "HYBRID"]  # Cualquiera es válido
    },
    {
        "name": "Ejecutivo senior - LONGEVITY tendencia",
        "customer_data": {
            "id": "test_4",
            "name": "Ana",
            "age": 52,
            "interests": ["liderazgo", "familia", "longevidad", "prevención"]
        },
        "message": "Dirijo una multinacional pero quiero envejecer bien y prevenir problemas de salud",
        "expected_program": "LONGEVITY"
    },
    {
        "name": "Joven emprendedor - PRIME claro",
        "customer_data": {
            "id": "test_5",
            "name": "Diego",
            "age": 32,
            "interests": ["emprendimiento", "eficiencia", "crecimiento personal"]
        },
        "message": "Fundé mi empresa hace 2 años, necesito optimizar mi físico para mayor productividad",
        "expected_program": "PRIME"
    },
    {
        "name": "Sin edad especificada - análisis por contenido",
        "customer_data": {
            "id": "test_6",
            "name": "Cliente",
            "age": None,
            "interests": ["fitness", "salud"]
        },
        "message": "Quiero mejorar mi condición física y tener más energía para el trabajo",
        "expected_program": ["PRIME", "HYBRID"]  # Debería inclinarse por contenido
    },
    {
        "name": "Profesora madura - LONGEVITY por edad y contenido",
        "customer_data": {
            "id": "test_7",
            "name": "Carmen",
            "age": 54,
            "interests": ["educación", "bienestar", "familia"]
        },
        "message": "Soy profesora universitaria, quiero mantener mi salud y energía para seguir enseñando años",
        "expected_program": "LONGEVITY"
    }
]

async def test_program_detection():
    """Ejecuta todos los escenarios de prueba."""
    print("🚀 Iniciando pruebas de detección automática NGX")
    print("=" * 60)
    
    router = ProgramRouter()
    results = []
    
    for i, scenario in enumerate(TEST_SCENARIOS, 1):
        print(f"\n📋 Escenario {i}: {scenario['name']}")
        print(f"👤 Cliente: {scenario['customer_data']['name']}, edad: {scenario['customer_data']['age']}")
        print(f"💬 Mensaje: {scenario['message'][:80]}...")
        
        try:
            # Ejecutar detección
            decision = await router.determine_program(
                customer_data=scenario['customer_data'],
                initial_message=scenario['message'],
                conversation_context=None
            )
            
            # Verificar resultado
            expected = scenario['expected_program']
            actual = decision.recommended_program
            
            if isinstance(expected, list):
                is_correct = actual in expected
                expected_str = f"cualquiera de {expected}"
            else:
                is_correct = actual == expected
                expected_str = expected
            
            status = "✅ CORRECTO" if is_correct else "❌ ERROR"
            
            print(f"🎯 Programa detectado: {actual}")
            print(f"📊 Confianza: {decision.confidence_score:.2f}")
            print(f"🧠 Razonamiento: {decision.reasoning}")
            print(f"🔍 Señales: {decision.signals_detected}")
            print(f"⚖️ Es híbrido: {decision.is_hybrid}")
            print(f"📈 Resultado: {status} (esperado: {expected_str})")
            
            results.append({
                'scenario': scenario['name'],
                'expected': expected,
                'actual': actual,
                'confidence': decision.confidence_score,
                'correct': is_correct,
                'is_hybrid': decision.is_hybrid
            })
            
        except Exception as e:
            print(f"💥 ERROR en escenario: {e}")
            results.append({
                'scenario': scenario['name'],
                'expected': expected,
                'actual': 'ERROR',
                'confidence': 0.0,
                'correct': False,
                'is_hybrid': False
            })
    
    # Mostrar resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE RESULTADOS")
    print("=" * 60)
    
    correct_count = sum(1 for r in results if r['correct'])
    total_count = len(results)
    accuracy = (correct_count / total_count) * 100
    
    print(f"✅ Casos correctos: {correct_count}/{total_count}")
    print(f"📈 Precisión: {accuracy:.1f}%")
    
    # Detalles por resultado
    for result in results:
        status_icon = "✅" if result['correct'] else "❌"
        print(f"{status_icon} {result['scenario']}: {result['actual']} (confianza: {result['confidence']:.2f})")
    
    # Análisis de confianza
    avg_confidence = sum(r['confidence'] for r in results if r['confidence'] > 0) / len([r for r in results if r['confidence'] > 0])
    high_confidence_count = sum(1 for r in results if r['confidence'] >= 0.7)
    
    print(f"\n📊 Análisis de confianza:")
    print(f"   • Confianza promedio: {avg_confidence:.2f}")
    print(f"   • Casos con alta confianza (≥0.7): {high_confidence_count}/{total_count}")
    
    # Recomendaciones
    print(f"\n🎯 Evaluación del sistema:")
    if accuracy >= 85:
        print("   🏆 EXCELENTE: El sistema está funcionando muy bien")
    elif accuracy >= 70:
        print("   ✅ BUENO: El sistema funciona correctamente con margen de mejora")
    elif accuracy >= 50:
        print("   ⚠️ REGULAR: El sistema necesita ajustes importantes")
    else:
        print("   🚨 CRÍTICO: El sistema requiere revisión completa")
    
    if avg_confidence < 0.6:
        print("   📝 RECOMENDACIÓN: Mejorar algoritmos de confianza")
    
    print(f"\n🎉 Pruebas completadas exitosamente!")
    return results

async def test_program_switching():
    """Prueba la funcionalidad de cambio de programa durante conversación."""
    print("\n" + "=" * 60)
    print("🔄 PRUEBAS DE CAMBIO DE PROGRAMA")
    print("=" * 60)
    
    router = ProgramRouter()
    
    # Simular conversación que evoluciona
    print("\n📋 Escenario: Cliente que revela más información")
    
    # Conversación inicial ambigua
    initial_history = [
        {"role": "user", "content": "Hola, estoy interesado en mejorar mi forma física"},
        {"role": "assistant", "content": "¡Perfecto! Cuéntame más sobre tus objetivos"},
        {"role": "user", "content": "Quiero tener más energía y verme mejor"}
    ]
    
    # Nueva información que clarifica el perfil
    new_info_scenarios = [
        {
            "name": "Revela ser joven profesional",
            "message": "Trabajo en consultoría 14 horas al día, necesito rendir más en el trabajo",
            "expected_switch_to": "PRIME"
        },
        {
            "name": "Revela preocupaciones de edad",
            "message": "Tengo 55 años y quiero prevenir problemas de salud como mi padre",
            "expected_switch_to": "LONGEVITY"
        }
    ]
    
    for scenario in new_info_scenarios:
        print(f"\n🔄 {scenario['name']}")
        print(f"💬 Nueva información: {scenario['message']}")
        
        # Simular programa inicial (HYBRID por ambigüedad)
        current_program = "HYBRID"
        print(f"📍 Programa actual: {current_program}")
        
        try:
            should_switch, new_decision = await router.should_switch_program(
                current_program=current_program,
                new_information=scenario['message'],
                conversation_history=initial_history
            )
            
            if should_switch and new_decision:
                print(f"✅ Cambio recomendado a: {new_decision.recommended_program}")
                print(f"📊 Confianza: {new_decision.confidence_score:.2f}")
                print(f"🧠 Razonamiento: {new_decision.reasoning}")
                
                is_correct = new_decision.recommended_program == scenario['expected_switch_to']
                status = "✅ CORRECTO" if is_correct else "❌ ERROR"
                print(f"📈 Resultado: {status} (esperado: {scenario['expected_switch_to']})")
            else:
                print("⏸️ No se recomienda cambio")
                print("📈 Resultado: ❌ ERROR (se esperaba cambio)")
                
        except Exception as e:
            print(f"💥 ERROR: {e}")

async def main():
    """Función principal que ejecuta todas las pruebas."""
    try:
        # Pruebas principales de detección
        await test_program_detection()
        
        # Pruebas de cambio de programa
        await test_program_switching()
        
        print(f"\n🎊 ¡Todas las pruebas completadas!")
        
    except Exception as e:
        print(f"💥 Error ejecutando pruebas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Ejecutar pruebas
    asyncio.run(main())