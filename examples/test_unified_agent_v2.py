"""
Ejemplo de uso del agente unificado NGX con detección dinámica.
Demuestra las nuevas capacidades de adaptación y análisis.
"""
import asyncio
from src.agents.unified_agent import NGXUnifiedAgent
from src.conversation.prompts.unified_prompts import ADAPTIVE_TEMPLATES
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def simulate_conversation():
    """Simula una conversación completa con el agente unificado."""
    
    print("=== NGX Unified Agent - Demo de Detección Dinámica ===\n")
    
    # Escenarios de prueba
    test_scenarios = [
        {
            "name": "Ejecutivo Típico",
            "context": {
                "age": 42,
                "score": 85,
                "interests": ["productividad", "energía", "rendimiento"],
                "lead_source": "lead magnet productividad ejecutiva"
            },
            "messages": [
                "Hola, acabo de hacer el test y me sorprendieron los resultados",
                "Soy CEO de una startup y trabajo unas 60 horas por semana. El estrés me está matando",
                "Necesito algo que me ayude a rendir mejor sin sacrificar más tiempo",
                "¿Cuánto cuesta el programa?"
            ]
        },
        {
            "name": "Adulto Mayor Activo",
            "context": {
                "age": 62,
                "score": 78,
                "interests": ["movilidad", "prevención", "independencia"],
                "lead_source": "lead magnet longevidad activa"
            },
            "messages": [
                "Hola Carlos, vi mis resultados del test de salud",
                "Me acabo de jubilar y quiero mantenerme activo. Tengo algunos dolores en las rodillas",
                "Mi mayor miedo es perder independencia y no poder jugar con mis nietos",
                "¿Este programa es seguro para alguien de mi edad?"
            ]
        },
        {
            "name": "Caso Híbrido (Zona 45-55)",
            "context": {
                "age": 51,
                "score": 82,
                "interests": ["energía", "prevención", "rendimiento"],
                "lead_source": "lead magnet evaluación integral"
            },
            "messages": [
                "Hola, hice el test y estoy intrigado con los resultados",
                "Tengo 51 años, dirijo 2 empresas pero también quiero cuidar mi salud a largo plazo",
                "Busco algo que me ayude con mi energía diaria pero también prevenir problemas futuros",
                "¿Qué programa sería mejor para alguien como yo?"
            ]
        }
    ]
    
    # Ejecutar cada escenario
    for scenario in test_scenarios:
        print(f"\n{'='*60}")
        print(f"ESCENARIO: {scenario['name']}")
        print(f"{'='*60}\n")
        
        # Crear agente con contexto inicial
        agent = NGXUnifiedAgent(initial_context=scenario['context'])
        
        # Información inicial
        print(f"Contexto inicial:")
        print(f"- Edad: {scenario['context']['age']}")
        print(f"- Score: {scenario['context']['score']}")
        print(f"- Intereses: {scenario['context']['interests']}")
        print(f"\nModo inicial: {agent.current_mode}")
        print(f"\n{'─'*50}\n")
        
        # Simular conversación
        for i, message in enumerate(scenario['messages']):
            print(f"Cliente: {message}")
            
            # Aquí simularíamos la respuesta del agente
            # En producción, esto sería a través de la API
            
            # Simular análisis después del segundo mensaje
            if i == 1:
                # Simular uso de analyze_customer_profile
                transcript = " ".join(scenario['messages'][:2])
                print(f"\n[Sistema: Analizando perfil del cliente...]")
                
                # Simular actualización de detección
                if "CEO" in message or "startup" in message:
                    agent.update_detection_confidence("PRIME", 0.85, "detectó rol ejecutivo")
                elif "jubilado" in message or "dolores" in message:
                    agent.update_detection_confidence("LONGEVITY", 0.80, "detectó jubilación y dolores")
                elif "empresas" in message and "prevenir" in scenario['messages'][2]:
                    agent.update_detection_confidence("HYBRID", 0.75, "detectó señales mixtas")
                
                context = agent.get_adaptive_context()
                print(f"Modo actualizado: {context['current_mode']}")
                print(f"Programa detectado: {context['detected_program']} (confianza: {context['confidence_score']})")
            
            # Simular respuesta del agente basada en el modo
            if agent.current_mode == "DISCOVERY":
                print("Agente: [Hace preguntas de descubrimiento...]")
            elif "PRIME" in agent.current_mode:
                print("Agente: [Responde con enfoque ejecutivo, vocabulario de optimización...]")
            elif "LONGEVITY" in agent.current_mode:
                print("Agente: [Responde con enfoque en bienestar, tono empático...]")
            elif agent.current_mode == "HYBRID":
                print("Agente: [Presenta ambas opciones de forma equilibrada...]")
            
            print()
            await asyncio.sleep(0.5)  # Pausa dramática
        
        # Mostrar métricas finales
        print(f"\n{'─'*50}")
        print("MÉTRICAS FINALES:")
        final_context = agent.get_adaptive_context()
        insights = agent.get_detection_insights()
        
        print(f"- Programa final: {final_context['detected_program']}")
        print(f"- Confianza: {final_context['confidence_score']:.0%}")
        print(f"- Tiempo de detección: {insights.get('first_detection_time', 'N/A')} segundos")
        print(f"- Calidad de recomendación: {insights['recommendation_quality']}")
        print(f"- Estabilidad: {insights['detection_stability']:.0%}")
        print(f"- Cambios de modo: {insights['mode_changes']}")
        
        await asyncio.sleep(1)  # Pausa entre escenarios

def demonstrate_adaptive_tools():
    """Demuestra el uso de las herramientas adaptativas."""
    
    print("\n\n=== DEMOSTRACIÓN DE HERRAMIENTAS ADAPTATIVAS ===\n")
    
    # Mostrar vocabulario adaptativo
    print("VOCABULARIO POR MODO:")
    for mode, templates in ADAPTIVE_TEMPLATES.items():
        vocab = templates.get("vocabulary", [])
        if vocab:
            print(f"\n{mode}:")
            print(f"  Vocabulario: {', '.join(vocab)}")
            print(f"  Ritmo: {templates.get('pace', 'natural')}")
    
    print("\n" + "="*60)

async def main():
    """Ejecuta la demostración completa."""
    
    # Ejecutar simulación de conversaciones
    await simulate_conversation()
    
    # Mostrar herramientas adaptativas
    demonstrate_adaptive_tools()
    
    print("\n=== FIN DE LA DEMOSTRACIÓN ===")

if __name__ == "__main__":
    asyncio.run(main())
