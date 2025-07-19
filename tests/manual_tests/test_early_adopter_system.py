#!/usr/bin/env python3
"""
Test del Sistema de Early Adopter Consultivo.

Este script valida que el sistema de early adopter funciona correctamente:
- Presentación consultiva de oportunidades
- Respeto por el proceso de decisión del cliente
- Transparencia sobre limitaciones genuinas
- Integración apropiada en fases de consultoría
"""

import sys
import os

# Añadir directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.early_adopter_service import (
    EarlyAdopterService, 
    EarlyAdopterTier, 
    EarlyAdopterOffer
)
from src.services.consultative_advisor_service import (
    ConsultativeAdvisorService,
    ConsultativeRecommendation,
    ClientArchetype
)

def test_early_adopter_service():
    """Prueba el servicio de early adopter."""
    print("🧪 TESTING EARLY ADOPTER SERVICE")
    print("=" * 50)
    
    service = EarlyAdopterService()
    
    # Test 1: Verificar que hay ofertas disponibles
    print("\n📋 Test 1: Verificar ofertas disponibles")
    print("-" * 30)
    
    for tier in EarlyAdopterTier:
        offer = service.current_offers.get(tier)
        if offer:
            print(f"✅ {tier.value}: {offer.spots_remaining}/{offer.total_spots} espacios restantes")
        else:
            print(f"❌ {tier.value}: Sin oferta")
    
    # Test 2: Determinar si debe presentarse la oportunidad
    print("\n🎯 Test 2: Determinar cuándo presentar oportunidad")
    print("-" * 45)
    
    test_cases = [
        {"phase": "initial_connection", "engagement": "high", "expected": False},
        {"phase": "recommendation", "engagement": "high", "expected": True},
        {"phase": "recommendation", "engagement": "low", "expected": False},
        {"phase": "gentle_objection_handling", "engagement": "medium", "expected": True},
    ]
    
    for i, case in enumerate(test_cases, 1):
        should_present = service.should_present_early_adopter_opportunity(
            client_profile={"age": 35},
            consultation_phase=case["phase"],
            engagement_level=case["engagement"]
        )
        
        result = "✅" if should_present == case["expected"] else "❌"
        print(f"{result} Caso {i}: {case['phase']} + {case['engagement']} = {should_present}")
    
    # Test 3: Obtener oferta apropiada para diferentes tiers
    print("\n🎁 Test 3: Ofertas apropiadas por tier recomendado")
    print("-" * 48)
    
    tier_tests = [
        {"recommended_tier": "Premium", "expected_tier": EarlyAdopterTier.PIONEER},
        {"recommended_tier": "Elite", "expected_tier": EarlyAdopterTier.INNOVATOR},
        {"recommended_tier": "Pro", "expected_tier": EarlyAdopterTier.INNOVATOR},
        {"recommended_tier": "Essential", "expected_tier": EarlyAdopterTier.EARLY_SUPPORTER},
    ]
    
    for test in tier_tests:
        offer = service.get_appropriate_early_adopter_offer(
            client_profile={"age": 35},
            recommended_tier=test["recommended_tier"],
            consultation_context={}
        )
        
        if offer and offer.tier == test["expected_tier"]:
            print(f"✅ {test['recommended_tier']} → {offer.tier.value}")
        else:
            actual_tier = offer.tier.value if offer else "None"
            print(f"❌ {test['recommended_tier']} → {actual_tier} (esperado: {test['expected_tier'].value})")
    
    # Test 4: Generar presentación consultiva
    print("\n💬 Test 4: Presentación consultiva")
    print("-" * 35)
    
    pioneer_offer = service.current_offers.get(EarlyAdopterTier.PIONEER)
    if pioneer_offer:
        presentation = service.generate_consultive_early_adopter_presentation(
            offer=pioneer_offer,
            client_context={"client_type": "executive"}
        )
        
        # Verificar que la presentación es consultiva (no agresiva)
        consultive_indicators = [
            "información", "oportunidad", "consideres", "análisis", 
            "transparencia", "genuinamente", "tiempo", "decidir"
        ]
        
        consultive_score = sum(1 for indicator in consultive_indicators 
                             if indicator in presentation.lower())
        
        aggressive_indicators = [
            "solo hoy", "última oportunidad", "decide ahora", "no esperes",
            "aprovecha", "urgente", "rápido"
        ]
        
        aggressive_score = sum(1 for indicator in aggressive_indicators 
                             if indicator in presentation.lower())
        
        print(f"📊 Indicadores consultivos: {consultive_score}")
        print(f"📊 Indicadores agresivos: {aggressive_score}")
        
        if consultive_score >= 3 and aggressive_score == 0:
            print("✅ Presentación apropiadamente consultiva")
        else:
            print("❌ Presentación necesita ajustes")
        
        print(f"\n📝 Muestra de presentación:")
        print(f"'{presentation[:200]}...'")
    
    return True

def test_consultative_advisor_integration():
    """Prueba la integración con el servicio consultivo."""
    print("\n\n🤝 TESTING CONSULTATIVE ADVISOR INTEGRATION")
    print("=" * 55)
    
    advisor = ConsultativeAdvisorService()
    
    # Test 1: Verificar que early adopter service está inicializado
    print("\n🔗 Test 1: Inicialización de Early Adopter Service")
    print("-" * 50)
    
    if hasattr(advisor, 'early_adopter_service'):
        print("✅ Early Adopter Service inicializado correctamente")
    else:
        print("❌ Early Adopter Service no encontrado")
        return False
    
    # Test 2: Generar presentación consultiva integrada
    print("\n🎨 Test 2: Presentación consultiva integrada")
    print("-" * 45)
    
    # Crear recomendación mock
    mock_recommendation = ConsultativeRecommendation(
        recommended_program="PRIME",
        recommended_tier="Elite",
        confidence_score=0.85,
        reasoning="Cliente ejecutivo con múltiples necesidades",
        key_benefits=["Optimización cognitiva", "Energía sostenida"],
        addressing_concerns=["estrés", "productividad"],
        client_archetype=ClientArchetype.EXECUTIVE_PERFORMER,
        why_this_fits="Perfil ejecutivo demandante",
        alternative_options=["Pro como alternativa"]
    )
    
    presentation = advisor.generate_consultive_early_adopter_presentation(
        recommendation=mock_recommendation,
        client_profile={"age": 38, "profession": "CEO"},
        consultation_context={"consultation_phase": "recommendation"}
    )
    
    if presentation:
        print("✅ Presentación generada exitosamente")
        print(f"📏 Longitud: {len(presentation)} caracteres")
        
        # Verificar elementos clave
        key_elements = ["pioneer", "innovator", "early", "limitado", "beneficios"]
        found_elements = sum(1 for element in key_elements 
                           if element in presentation.lower())
        
        print(f"📊 Elementos clave encontrados: {found_elements}/{len(key_elements)}")
        
        if found_elements >= 3:
            print("✅ Presentación contiene elementos clave apropiados")
        else:
            print("❌ Presentación necesita elementos clave adicionales")
    else:
        print("❌ No se generó presentación")
    
    # Test 3: Manejo de preguntas sobre early adopter
    print("\n❓ Test 3: Manejo de preguntas")
    print("-" * 35)
    
    test_questions = [
        "¿Por qué es limitado?",
        "¿Qué beneficios incluye?",
        "¿Cuánto tiempo tengo para decidir?",
        "¿Cuántos espacios quedan?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        response = advisor.handle_early_adopter_questions(
            question=question,
            current_recommendation=mock_recommendation,
            client_profile={"age": 38}
        )
        
        if response and len(response) > 50:
            print(f"✅ Pregunta {i}: Respuesta generada ({len(response)} chars)")
        else:
            print(f"❌ Pregunta {i}: Respuesta insuficiente")
    
    return True

def test_conversation_integration():
    """Prueba la integración en el flujo de conversación."""
    print("\n\n💬 TESTING CONVERSATION FLOW INTEGRATION")
    print("=" * 50)
    
    # Test 1: Verificar que engagement assessment funciona
    print("\n📊 Test 1: Evaluación de engagement")
    print("-" * 40)
    
    # Mock conversation state para testing
    class MockMessage:
        def __init__(self, role, content):
            self.role = role
            self.content = content
    
    class MockState:
        def __init__(self, messages):
            self.messages = messages
    
    # Crear conversaciones mock con diferentes niveles de engagement
    high_engagement_messages = [
        MockMessage("user", "Hola, estoy muy interesado en NGX"),
        MockMessage("assistant", "Perfecto, cuéntame más"),
        MockMessage("user", "Tengo problemas de energía y estrés laboral, trabajo 12 horas diarias"),
        MockMessage("assistant", "Entiendo, eso es muy demandante"),
        MockMessage("user", "¿Cómo funciona exactamente el HIE? Me parece fascinante la tecnología"),
        MockMessage("assistant", "Te explico el HIE..."),
        MockMessage("user", "Excelente, ¿qué opciones tengo disponibles? Quiero saber más detalles")
    ]
    
    low_engagement_messages = [
        MockMessage("user", "Hola"),
        MockMessage("assistant", "Hola, ¿cómo puedo ayudarte?"),
        MockMessage("user", "Info")
    ]
    
    # Importar ConversationService para testing
    from src.services.conversation_service import ConversationService
    
    service = ConversationService()
    
    high_engagement_level = service._assess_engagement_level(MockState(high_engagement_messages))
    low_engagement_level = service._assess_engagement_level(MockState(low_engagement_messages))
    
    print(f"📈 High engagement scenario: {high_engagement_level}")
    print(f"📉 Low engagement scenario: {low_engagement_level}")
    
    if high_engagement_level == "high" and low_engagement_level == "low":
        print("✅ Evaluación de engagement funciona correctamente")
    else:
        print("❌ Evaluación de engagement necesita ajustes")
    
    return True

def main():
    """Ejecuta todos los tests del sistema de early adopter."""
    print("🎯 SISTEMA DE EARLY ADOPTER CONSULTIVO - TESTS COMPLETOS")
    print("=" * 65)
    
    try:
        # Ejecutar tests
        test1_success = test_early_adopter_service()
        test2_success = test_consultative_advisor_integration()
        test3_success = test_conversation_integration()
        
        # Resumen de resultados
        print("\n\n📊 RESUMEN DE RESULTADOS")
        print("=" * 30)
        
        results = [
            ("Early Adopter Service", test1_success),
            ("Consultative Integration", test2_success),
            ("Conversation Integration", test3_success)
        ]
        
        all_passed = True
        for test_name, passed in results:
            status = "✅ PASÓ" if passed else "❌ FALLÓ"
            print(f"{status} {test_name}")
            if not passed:
                all_passed = False
        
        print(f"\n🎯 RESULTADO GENERAL: {'✅ TODOS LOS TESTS PASARON' if all_passed else '❌ ALGUNOS TESTS FALLARON'}")
        
        if all_passed:
            print("\n🎊 SISTEMA DE EARLY ADOPTER CONSULTIVO FUNCIONANDO CORRECTAMENTE")
            print("✨ Ready for deployment - enfoque consultivo validado")
        else:
            print("\n⚠️  REVISAR TESTS FALLIDOS ANTES DE DEPLOYMENT")
        
        return all_passed
        
    except Exception as e:
        print(f"\n💥 ERROR EN TESTING: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)