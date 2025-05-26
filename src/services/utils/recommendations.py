"""
Utilidades para la generación de recomendaciones en modelos predictivos.

Este módulo proporciona funciones comunes para generar recomendaciones
utilizadas por los servicios predictivos.
"""

from typing import Dict, List, Any, Optional
import logging
import random

logger = logging.getLogger(__name__)

async def generate_response_suggestions(analysis_results: Dict[str, Any], 
                                  suggestion_templates: Dict[str, List[str]],
                                  context_factors: Optional[Dict[str, Any]] = None) -> List[str]:
    """
    Genera sugerencias de respuesta basadas en el análisis.
    
    Args:
        analysis_results: Resultados del análisis predictivo
        suggestion_templates: Plantillas de sugerencias por categoría
        context_factors: Factores contextuales adicionales (opcional)
        
    Returns:
        Lista de sugerencias de respuesta
    """
    suggestions = []
    
    try:
        # Determinar categorías relevantes basadas en resultados
        categories = []
        
        # Extraer categorías principales según el tipo de análisis
        if "objection_types" in analysis_results:
            categories = analysis_results.get("objection_types", [])
        elif "need_categories" in analysis_results:
            categories = analysis_results.get("need_categories", [])
        elif "category" in analysis_results:
            categories = [analysis_results.get("category")]
        
        # Generar sugerencias para cada categoría
        for category in categories:
            if category in suggestion_templates:
                # Seleccionar plantillas para esta categoría
                templates = suggestion_templates[category]
                
                # Seleccionar aleatoriamente hasta 2 plantillas
                selected_templates = random.sample(templates, min(2, len(templates)))
                
                # Aplicar factores contextuales si están disponibles
                for template in selected_templates:
                    if context_factors:
                        # Reemplazar placeholders en la plantilla
                        for key, value in context_factors.items():
                            placeholder = f"{{{key}}}"
                            if placeholder in template:
                                template = template.replace(placeholder, str(value))
                    
                    suggestions.append(template)
        
        # Si no hay sugerencias específicas, usar plantillas genéricas
        if not suggestions and "generic" in suggestion_templates:
            generic_templates = suggestion_templates["generic"]
            suggestions = random.sample(generic_templates, min(2, len(generic_templates)))
            
        return suggestions
        
    except Exception as e:
        logger.error(f"Error al generar sugerencias de respuesta: {e}")
        return ["Lo siento, no puedo generar sugerencias en este momento."]

async def generate_next_best_action(decision_factors: Dict[str, Any],
                              action_templates: Dict[str, Dict[str, Any]],
                              objective_weights: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
    """
    Genera la siguiente mejor acción basada en factores de decisión.
    
    Args:
        decision_factors: Factores para la toma de decisiones
        action_templates: Plantillas de acciones disponibles
        objective_weights: Pesos de objetivos para priorización (opcional)
        
    Returns:
        Acción recomendada con detalles
    """
    try:
        # Inicializar pesos de objetivos si no se proporcionan
        if not objective_weights:
            objective_weights = {
                "conversion": 0.4,
                "satisfaction": 0.3,
                "information": 0.3
            }
            
        # Calcular puntuación para cada acción posible
        action_scores = {}
        
        for action_id, action_template in action_templates.items():
            # Obtener condiciones de la acción
            conditions = action_template.get("conditions", {})
            
            # Verificar si se cumplen las condiciones
            conditions_met = True
            for condition_key, condition_value in conditions.items():
                if condition_key in decision_factors:
                    factor_value = decision_factors[condition_key]
                    
                    # Comparar según el tipo de condición
                    if isinstance(condition_value, dict):
                        # Condición con operador
                        operator = condition_value.get("operator", "eq")
                        value = condition_value.get("value")
                        
                        if operator == "eq" and factor_value != value:
                            conditions_met = False
                        elif operator == "gt" and factor_value <= value:
                            conditions_met = False
                        elif operator == "lt" and factor_value >= value:
                            conditions_met = False
                        elif operator == "in" and factor_value not in value:
                            conditions_met = False
                    else:
                        # Condición de igualdad simple
                        if factor_value != condition_value:
                            conditions_met = False
            
            # Si se cumplen las condiciones, calcular puntuación
            if conditions_met:
                # Obtener impactos de la acción
                impacts = action_template.get("impacts", {})
                
                # Calcular puntuación ponderada según impactos y objetivos
                score = 0
                for objective, weight in objective_weights.items():
                    impact = impacts.get(objective, 0)
                    score += impact * weight
                
                action_scores[action_id] = score
        
        # Seleccionar la acción con mayor puntuación
        if not action_scores:
            # Si no hay acciones que cumplan las condiciones, usar acción por defecto
            if "default" in action_templates:
                best_action = action_templates["default"]
                best_action_id = "default"
            else:
                return {
                    "action_id": "no_action",
                    "action_type": "message",
                    "content": "No hay acciones recomendadas en este momento.",
                    "confidence": 0.0
                }
        else:
            best_action_id = max(action_scores.items(), key=lambda x: x[1])[0]
            best_action = action_templates[best_action_id]
        
        # Construir respuesta
        response = {
            "action_id": best_action_id,
            "action_type": best_action.get("type", "message"),
            "content": best_action.get("content", ""),
            "confidence": action_scores.get(best_action_id, 0.5)
        }
        
        # Añadir parámetros adicionales si existen
        if "params" in best_action:
            response["params"] = best_action["params"]
            
        return response
        
    except Exception as e:
        logger.error(f"Error al generar siguiente mejor acción: {e}")
        return {
            "action_id": "error",
            "action_type": "message",
            "content": "Error al determinar la siguiente acción.",
            "confidence": 0.0
        }
