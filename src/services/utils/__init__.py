"""
Utilidades para los servicios predictivos de NGX Voice Sales Agent.

Este paquete contiene módulos de utilidades compartidas por los diferentes
servicios predictivos, incluyendo detección de señales, cálculo de puntuaciones,
generación de recomendaciones y procesamiento de datos.
"""

from src.services.utils.signal_detection import (
    detect_sentiment_signals,
    detect_keyword_signals,
    detect_question_patterns,
    detect_engagement_signals
)

from src.services.utils.scoring import (
    normalize_scores,
    apply_weights,
    calculate_confidence,
    rank_items
)

from src.services.utils.recommendations import (
    generate_response_suggestions,
    generate_next_best_action
)

from src.services.utils.data_processing import (
    preprocess_text_data,
    extract_features_from_conversation,
    filter_messages_by_timeframe
)

__all__ = [
    'detect_sentiment_signals',
    'detect_keyword_signals',
    'detect_question_patterns',
    'detect_engagement_signals',
    'normalize_scores',
    'apply_weights',
    'calculate_confidence',
    'rank_items',
    'generate_response_suggestions',
    'generate_next_best_action',
    'preprocess_text_data',
    'extract_features_from_conversation',
    'filter_messages_by_timeframe'
]
