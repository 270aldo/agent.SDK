"""
Utilidades para el cálculo de puntuaciones en modelos predictivos.

Este módulo proporciona funciones comunes para calcular y normalizar puntuaciones
utilizadas por los servicios predictivos.
"""

from typing import Dict, List, Any, Optional
import logging
import numpy as np

logger = logging.getLogger(__name__)

def normalize_scores(scores: Dict[str, float]) -> Dict[str, float]:
    """
    Normaliza puntuaciones a un rango 0-1 utilizando softmax.
    
    Args:
        scores: Diccionario de puntuaciones a normalizar
        
    Returns:
        Diccionario con puntuaciones normalizadas
    """
    if not scores:
        return {}
        
    try:
        # Extraer valores
        values = list(scores.values())
        
        # Aplicar softmax para normalización
        exp_values = np.exp(values - np.max(values))
        softmax_values = exp_values / exp_values.sum()
        
        # Reconstruir diccionario
        normalized = {k: float(s) for k, s in zip(scores.keys(), softmax_values)}
        
        return normalized
        
    except Exception as e:
        logger.error(f"Error al normalizar puntuaciones: {e}")
        # Fallback a normalización simple
        total = sum(scores.values()) or 1
        return {k: v / total for k, v in scores.items()}

def apply_weights(signals: Dict[str, float], weights: Dict[str, float]) -> Dict[str, float]:
    """
    Aplica pesos a señales detectadas.
    
    Args:
        signals: Diccionario de señales detectadas
        weights: Diccionario de pesos a aplicar
        
    Returns:
        Diccionario con señales ponderadas
    """
    weighted_signals = {}
    
    try:
        for signal_type, signal_value in signals.items():
            weight = weights.get(signal_type, 1.0)
            weighted_signals[signal_type] = signal_value * weight
            
        return weighted_signals
        
    except Exception as e:
        logger.error(f"Error al aplicar pesos a señales: {e}")
        return signals

def calculate_confidence(scores: Dict[str, float], diversity_factor: float = 0.5) -> float:
    """
    Calcula nivel de confianza basado en puntuaciones.
    
    Args:
        scores: Diccionario de puntuaciones
        diversity_factor: Factor de diversidad (0-1) que influye en la confianza
        
    Returns:
        Nivel de confianza (0-1)
    """
    if not scores:
        return 0.0
        
    try:
        # Obtener puntuación máxima
        max_score = max(scores.values())
        
        # Calcular diversidad de puntuaciones (entropía normalizada)
        values = list(scores.values())
        total = sum(values) or 1
        probabilities = [v / total for v in values]
        
        # Evitar log(0)
        entropy = -sum(p * np.log(p) if p > 0 else 0 for p in probabilities)
        max_entropy = np.log(len(probabilities)) if len(probabilities) > 1 else 1
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
        
        # Calcular confianza basada en puntuación máxima y diversidad
        # - Alta puntuación máxima y baja entropía = alta confianza
        # - Baja puntuación máxima o alta entropía = baja confianza
        confidence = max_score * (1 - normalized_entropy * diversity_factor)
        
        return min(max(confidence, 0.0), 1.0)  # Asegurar rango 0-1
        
    except Exception as e:
        logger.error(f"Error al calcular confianza: {e}")
        # Fallback a confianza basada solo en puntuación máxima
        return max(scores.values()) if scores else 0.0

def rank_items(items: Dict[str, float], top_n: int = None, min_score: float = 0.0) -> List[str]:
    """
    Ordena elementos por puntuación y devuelve los mejores.
    
    Args:
        items: Diccionario de elementos con sus puntuaciones
        top_n: Número máximo de elementos a devolver
        min_score: Puntuación mínima para incluir un elemento
        
    Returns:
        Lista de elementos ordenados por puntuación
    """
    if not items:
        return []
        
    try:
        # Filtrar por puntuación mínima
        filtered_items = {k: v for k, v in items.items() if v >= min_score}
        
        # Ordenar por puntuación (descendente)
        sorted_items = sorted(filtered_items.items(), key=lambda x: x[1], reverse=True)
        
        # Limitar a top_n si se especifica
        if top_n is not None:
            sorted_items = sorted_items[:top_n]
            
        # Devolver solo las claves (nombres de elementos)
        return [item[0] for item in sorted_items]
        
    except Exception as e:
        logger.error(f"Error al ordenar elementos: {e}")
        return list(items.keys())[:top_n] if top_n else list(items.keys())
