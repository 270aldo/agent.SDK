# Herramientas para los Agentes NGX
from .program_tools import get_program_details, handle_price_objection
from .adaptive_tools import (
    analyze_customer_profile,
    switch_program_focus,
    get_adaptive_responses,
    track_conversation_metrics
)

__all__ = [
    "get_program_details",
    "handle_price_objection",
    "analyze_customer_profile",
    "switch_program_focus", 
    "get_adaptive_responses",
    "track_conversation_metrics"
]
