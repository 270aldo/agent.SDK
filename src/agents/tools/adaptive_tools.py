"""
Herramientas adaptativas para el agente unificado NGX.
Permiten análisis dinámico y cambio de enfoque durante la conversación.
"""
# from agents import function_tool
# TODO: Implementar function_tool alternativo o instalar agents sin conflictos
def function_tool(func):
    """Decorador temporal para herramientas de función."""
    return func
from typing import Dict, Any, List
import re

@function_tool
async def analyze_customer_profile(transcript: str, customer_age: int = None) -> Dict[str, Any]:
    """
    Analyzes customer conversation signals to determine the most suitable program.
    Use this tool after gathering initial information about the customer (30-60 seconds into conversation).
    
    Args:
        transcript: The conversation transcript so far
        customer_age: Customer's age if mentioned (optional)
    
    Returns:
        Analysis with program recommendation and confidence score
    """
    # Palabras clave y su peso para cada programa
    prime_keywords = {
        'tiempo': 0.8, 'ocupado': 0.9, 'estrés': 0.7, 'productividad': 0.9,
        'empresa': 0.8, 'rendimiento': 0.9, 'optimizar': 0.9, 'reuniones': 0.7,
        'viajar': 0.7, 'viaje': 0.7, 'ejecutivo': 1.0, 'resultados': 0.8, 
        'eficiencia': 0.9, 'trabajo': 0.7, 'negocio': 0.8, 'ceo': 1.0,
        'director': 0.9, 'gerente': 0.8, 'emprendedor': 0.9, 'startup': 0.9
    }
    
    longevity_keywords = {
        'dolor': 0.8, 'dolores': 0.8, 'articulaciones': 0.9, 'movilidad': 0.9, 
        'energía': 0.7, 'prevenir': 0.8, 'prevención': 0.8, 'independencia': 0.9, 
        'nietos': 0.9, 'jubilación': 1.0, 'jubilado': 1.0, 'retirado': 1.0,
        'caídas': 0.9, 'caída': 0.9, 'memoria': 0.8, 'calidad de vida': 0.9, 
        'salud': 0.7, 'bienestar': 0.7, 'vitalidad': 0.8, 'mayor': 0.7
    }
    
    # Análisis del transcript
    text_lower = transcript.lower()
    
    # Calcular puntuaciones
    prime_score = sum(weight for word, weight in prime_keywords.items() 
                     if word in text_lower)
    longevity_score = sum(weight for word, weight in longevity_keywords.items() 
                         if word in text_lower)
    
    # Factor edad si está disponible
    age_factor = 1.0
    if customer_age:
        if customer_age < 45:
            age_factor = 1.3  # Favorece PRIME
            prime_score *= age_factor
        elif customer_age > 55:
            age_factor = 1.3  # Favorece LONGEVITY
            longevity_score *= age_factor
        # Entre 45-55 es zona híbrida, no se modifica
    
    # Normalizar scores
    total_score = prime_score + longevity_score + 0.1  # Evitar división por cero
    prime_normalized = prime_score / total_score
    longevity_normalized = longevity_score / total_score
    
    # Determinar programa recomendado
    if prime_normalized > longevity_normalized * 1.3:  # PRIME claramente mejor
        recommended_program = "PRIME"
        confidence = min(prime_normalized * 1.2, 0.95)
    elif longevity_normalized > prime_normalized * 1.3:  # LONGEVITY claramente mejor
        recommended_program = "LONGEVITY"
        confidence = min(longevity_normalized * 1.2, 0.95)
    else:  # Zona híbrida
        recommended_program = "HYBRID"
        confidence = max(prime_normalized, longevity_normalized)
    
    # Extraer insights específicos
    detected_signals = []
    for word in prime_keywords:
        if word in text_lower:
            detected_signals.append(f"ejecutivo ({word})")
    for word in longevity_keywords:
        if word in text_lower:
            detected_signals.append(f"senior ({word})")
    
    return {
        "recommended_program": recommended_program,
        "confidence_score": round(confidence, 2),
        "prime_affinity": round(prime_normalized, 2),
        "longevity_affinity": round(longevity_normalized, 2),
        "detected_signals": detected_signals[:5],  # Top 5 señales
        "is_hybrid_zone": recommended_program == "HYBRID",
        "age_considered": customer_age is not None,
        "analysis_summary": f"Basándome en las señales detectadas ({', '.join(detected_signals[:3])}), "
                          f"recomiendo el programa {recommended_program} con {confidence:.0%} de confianza."
    }


@function_tool
async def switch_program_focus(from_program: str, to_program: str, reason: str) -> Dict[str, str]:
    """
    Switches the conversation focus from one program to another when detection changes.
    Use this when you realize the initial program focus was incorrect based on new information.
    
    Args:
        from_program: Current program focus (PRIME or LONGEVITY)
        to_program: New program to focus on (PRIME or LONGEVITY)
        reason: Brief explanation of why switching (e.g., "cliente mencionó jubilación reciente")
    
    Returns:
        Transition script and new conversation guidelines
    """
    from src.conversation.prompts.unified_prompts import PROGRAM_TRANSITIONS, ADAPTIVE_TEMPLATES
    
    # Validar programas
    valid_programs = ["PRIME", "LONGEVITY"]
    from_program = from_program.upper()
    to_program = to_program.upper()
    
    if from_program not in valid_programs or to_program not in valid_programs:
        return {
            "error": "Programas inválidos. Usa PRIME o LONGEVITY.",
            "transition_script": "",
            "new_focus_guidelines": ""
        }
    
    if from_program == to_program:
        return {
            "message": "Ya estás enfocado en este programa.",
            "transition_script": "",
            "new_focus_guidelines": ""
        }
    
    # Obtener frases de transición
    transition_key = f"{from_program}_TO_{to_program}"
    transition_phrases = PROGRAM_TRANSITIONS.get(transition_key, PROGRAM_TRANSITIONS["UNCERTAIN"])
    
    # Seleccionar una frase y personalizarla
    import random
    transition_template = random.choice(transition_phrases)
    
    # Personalizar según la razón
    reason_mapping = {
        "jubilación": "prevención y calidad de vida",
        "empresa": "optimización y rendimiento",
        "estrés": "productividad y energía",
        "dolor": "bienestar y movilidad",
        "tiempo": "eficiencia y resultados",
        "familia": "independencia y vitalidad"
    }
    
    # Encontrar palabra clave en la razón
    focus_keyword = "tus objetivos"
    for keyword, focus in reason_mapping.items():
        if keyword in reason.lower():
            focus_keyword = focus
            break
    
    transition_script = transition_template.format(
        objetivo=focus_keyword,
        preocupacion=focus_keyword,
        interes=focus_keyword,
        rutina="rutina diaria"
    )
    
    # Obtener nuevas directrices
    new_mode = f"{to_program}_FOCUSED"
    new_guidelines = ADAPTIVE_TEMPLATES.get(new_mode, {})
    
    return {
        "transition_script": transition_script,
        "new_program_focus": to_program,
        "conversation_mode": new_mode,
        "key_vocabulary": new_guidelines.get("vocabulary", []),
        "recommended_pace": new_guidelines.get("pace", "natural"),
        "value_propositions": new_guidelines.get("value_props", [])[:2],
        "implementation_tip": f"Usa la transición de forma natural en tu próxima respuesta. "
                            f"Luego, ajusta tu vocabulario para incluir términos como: "
                            f"{', '.join(new_guidelines.get('vocabulary', [])[:3])}"
    }


@function_tool  
async def get_adaptive_responses(current_mode: str, conversation_stage: str) -> Dict[str, List[str]]:
    """
    Gets context-appropriate responses based on current detection mode and conversation stage.
    Use this to get suggested questions, transitions, or value propositions.
    
    Args:
        current_mode: Current detection mode (DISCOVERY, PRIME_FOCUSED, LONGEVITY_FOCUSED, or HYBRID)
        conversation_stage: Stage of conversation (opening, discovery, presentation, closing)
    
    Returns:
        Appropriate responses for the current context
    """
    from src.conversation.prompts.unified_prompts import ADAPTIVE_TEMPLATES
    
    # Validar modo
    valid_modes = ["DISCOVERY", "PRIME_FOCUSED", "LONGEVITY_FOCUSED", "HYBRID"]
    if current_mode not in valid_modes:
        current_mode = "DISCOVERY"
    
    # Obtener templates del modo actual
    mode_templates = ADAPTIVE_TEMPLATES.get(current_mode, ADAPTIVE_TEMPLATES["DISCOVERY"])
    
    # Preparar respuestas según etapa
    responses = {
        "mode": current_mode,
        "stage": conversation_stage
    }
    
    if conversation_stage == "opening" or conversation_stage == "discovery":
        responses["suggested_questions"] = mode_templates.get("questions", [])[:3]
        responses["transition_phrases"] = mode_templates.get("transitions", [])
        responses["conversation_tip"] = "Haz preguntas abiertas y escucha activamente las señales del cliente."
        
    elif conversation_stage == "presentation":
        responses["value_propositions"] = mode_templates.get("value_props", [])
        responses["key_benefits"] = mode_templates.get("value_props", [])[:3]
        responses["vocabulary_to_use"] = mode_templates.get("vocabulary", [])
        responses["conversation_tip"] = f"Usa un ritmo {mode_templates.get('pace', 'natural')} y enfócate en los beneficios relevantes."
        
    elif conversation_stage == "closing":
        if current_mode == "HYBRID":
            responses["closing_options"] = mode_templates.get("comparison", [])
            responses["bridge_phrases"] = mode_templates.get("bridge_phrases", [])
            responses["conversation_tip"] = "Presenta ambas opciones brevemente y deja que el cliente elija."
        else:
            program = "PRIME" if "PRIME" in current_mode else "LONGEVITY"
            responses["closing_phrases"] = [
                f"¿Listo para comenzar tu transformación con NGX {program}?",
                f"¿Qué te parece si aseguramos tu lugar en {program} ahora mismo?",
                f"¿Prefieres el pago completo con descuento o el plan mensual?"
            ]
            responses["urgency_phrases"] = [
                "El precio especial es solo para quienes se inscriben hoy",
                "Tenemos cupos limitados para garantizar atención personalizada",
                "Incluye el análisis genético de regalo solo esta semana"
            ]
            responses["conversation_tip"] = "Crea urgencia sin presionar. Si hay dudas, ofrece agendar seguimiento."
    
    else:  # Default
        responses = mode_templates
    
    return responses


from pydantic import BaseModel, Field

class ConversationMetrics(BaseModel):
    program_detected: str = Field(default="UNKNOWN", description="Programa detectado durante la conversación")
    confidence: float = Field(default=0.0, description="Nivel de confianza en la detección")
    stage_reached: str = Field(default="", description="Etapa alcanzada en la conversación")
    objection_handled: bool = Field(default=False, description="Si se manejó alguna objeción")
    call_duration: int = Field(default=0, description="Duración de la llamada en segundos")

@function_tool
async def track_conversation_metrics(conversation_id: str, metrics: ConversationMetrics) -> Dict[str, str]:
    """
    Tracks important conversation metrics for optimization and learning.
    Use this to log detection changes, confidence scores, and key conversation events.
    
    Args:
        conversation_id: Unique identifier for the conversation
        metrics: Dictionary containing metrics like program_detected, confidence, stage_reached, etc.
    
    Returns:
        Confirmation of tracking
    """
    import json
    from datetime import datetime
    
    # Métricas importantes a trackear
    tracked_metrics = {
        "conversation_id": conversation_id,
        "timestamp": datetime.now().isoformat(),
        "program_detected": metrics.program_detected,
        "confidence_score": metrics.confidence,
        "stage_reached": metrics.stage_reached,
        "objection_handled": metrics.objection_handled,
        "call_duration": metrics.call_duration
    }
    
    # En producción, esto se guardaría en base de datos
    # Por ahora, solo lo formateamos para logging
    
    return {
        "status": "tracked",
        "conversation_id": conversation_id,
        "metrics_summary": f"Programa detectado: {tracked_metrics['program_detected']} "
                          f"(confianza: {tracked_metrics['confidence_score']:.0%})",
        "recommendation": "Continúa con el enfoque actual" if tracked_metrics['confidence_score'] > 0.7 
                         else "Considera hacer más preguntas de descubrimiento"
    }
