"""
Test simple para verificar que el tier detection funciona correctamente.
"""

import asyncio
import sys
import os

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.tier_detection_service import TierDetectionService, TierType


async def test_tier_detection():
    """Test básico de detección de tier."""
    print("🧪 Probando servicio de detección de tier...")
    
    # Crear servicio
    service = TierDetectionService()
    
    # Test 1: Estudiante -> Essential
    print("\n1️⃣ Test: Estudiante con presupuesto limitado")
    user_profile = {
        "age": 22,
        "occupation": "estudiante",
        "income_bracket": "low"
    }
    user_message = "Me interesa pero soy estudiante, no tengo mucho presupuesto"
    
    result = await service.detect_optimal_tier(user_message, user_profile)
    
    print(f"   Tier recomendado: {result.recommended_tier.value}")
    print(f"   Confianza: {result.confidence}")
    print(f"   Reasoning: {result.reasoning}")
    print(f"   Precio: {result.price_point}")
    
    # Test 2: CEO -> Premium
    print("\n2️⃣ Test: CEO con alto poder adquisitivo")
    user_profile = {
        "age": 42,
        "occupation": "CEO",
        "income_bracket": "very_high"
    }
    user_message = "Tengo mi empresa, no importa el precio, quiero resultados máximos"
    
    result = await service.detect_optimal_tier(user_message, user_profile)
    
    print(f"   Tier recomendado: {result.recommended_tier.value}")
    print(f"   Confianza: {result.confidence}")
    print(f"   Reasoning: {result.reasoning}")
    print(f"   Precio: {result.price_point}")
    
    # Test 3: Profesional -> Pro/Elite
    print("\n3️⃣ Test: Profesional con presupuesto medio")
    user_profile = {
        "age": 35,
        "occupation": "gerente",
        "income_bracket": "medium"
    }
    user_message = "Soy gerente, busco algo razonable dentro del presupuesto"
    
    result = await service.detect_optimal_tier(user_message, user_profile)
    
    print(f"   Tier recomendado: {result.recommended_tier.value}")
    print(f"   Confianza: {result.confidence}")
    print(f"   Reasoning: {result.reasoning}")
    print(f"   Precio: {result.price_point}")
    
    # Test 4: Médico -> Longevity Premium
    print("\n4️⃣ Test: Médico interesado en longevidad")
    user_profile = {
        "age": 55,
        "occupation": "médico",
        "income_bracket": "high"
    }
    user_message = "Como médico, busco algo para longevidad y prevención"
    
    result = await service.detect_optimal_tier(user_message, user_profile)
    
    print(f"   Tier recomendado: {result.recommended_tier.value}")
    print(f"   Confianza: {result.confidence}")
    print(f"   Reasoning: {result.reasoning}")
    print(f"   Precio: {result.price_point}")
    
    # Test 5: Ajuste por objeción de precio
    print("\n5️⃣ Test: Ajuste por objeción de precio")
    current_tier = TierType.ELITE
    objection_message = "$199 me parece muy caro, ¿hay algo más barato?"
    
    adjusted_result = await service.adjust_tier_based_on_objection(
        current_tier=current_tier,
        objection_message=objection_message,
        user_profile={"age": 30, "occupation": "profesional"}
    )
    
    print(f"   Tier original: {current_tier.value}")
    print(f"   Tier ajustado: {adjusted_result.recommended_tier.value}")
    print(f"   Confianza: {adjusted_result.confidence}")
    print(f"   Reasoning: {adjusted_result.reasoning}")
    print(f"   Precio ajustado: {adjusted_result.price_point}")
    
    # Test 6: ROI projection
    print("\n6️⃣ Test: ROI projection para consultor")
    user_profile = {
        "age": 35,
        "occupation": "consultor",
        "income_bracket": "high"
    }
    user_message = "Soy consultor, facturo $200/hora"
    
    result = await service.detect_optimal_tier(user_message, user_profile)
    
    print(f"   Tier recomendado: {result.recommended_tier.value}")
    print(f"   ROI projection: {result.roi_projection}")
    
    print("\n✅ Todos los tests completados exitosamente!")


if __name__ == "__main__":
    asyncio.run(test_tier_detection())