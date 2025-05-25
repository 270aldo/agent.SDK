"""
Servicio para analizar la intención de compra en conversaciones.
"""

import logging
import re
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime

# Configurar logging
logger = logging.getLogger(__name__)

class IntentAnalysisService:
    """
    Servicio para analizar la intención de compra en conversaciones.
    Implementa el "corte inteligente" para optimizar costos si no hay intención de compra.
    """
    
    # Palabras clave para detectar intención de compra
    PURCHASE_INTENT_KEYWORDS = [
        'comprar', 'adquirir', 'precio', 'costo', 'tarjeta', 'pagar', 'pago', 
        'suscripción', 'suscribir', 'contratar', 'plan', 'oferta', 'promoción',
        'descuento', 'cuánto cuesta', 'cuánto vale', 'interesado', 'me interesa'
    ]
    
    # Palabras clave para detectar rechazo
    REJECTION_KEYWORDS = [
        'no me interesa', 'no quiero', 'no puedo', 'no ahora', 'tal vez después',
        'lo pensaré', 'muy caro', 'demasiado caro', 'no tengo dinero', 'no puedo pagar',
        'no estoy seguro', 'tengo dudas', 'necesito pensarlo'
    ]
    
    # Umbral de intención de compra para continuar la conversación
    INTENT_THRESHOLD = 0.4  # 40% de probabilidad de compra
    
    def __init__(self):
        """Inicializar el servicio de análisis de intención."""
        logger.info("Servicio de análisis de intención inicializado")
    
    def analyze_purchase_intent(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Analiza la intención de compra en los mensajes de una conversación.
        
        Args:
            messages: Lista de mensajes de la conversación
            
        Returns:
            Dict: Resultado del análisis con probabilidad de compra e indicadores
        """
        # Extraer solo los mensajes del usuario
        user_messages = [msg["content"] for msg in messages if msg["role"] == "user"]
        
        if not user_messages:
            return {
                "purchase_intent_probability": 0.0,
                "has_purchase_intent": False,
                "has_rejection": False,
                "intent_indicators": [],
                "rejection_indicators": []
            }
        
        # Analizar los últimos 3 mensajes del usuario (o todos si hay menos)
        recent_messages = user_messages[-3:]
        
        # Calcular indicadores de intención de compra
        intent_indicators = []
        for keyword in self.PURCHASE_INTENT_KEYWORDS:
            for msg in recent_messages:
                if re.search(r'\b' + re.escape(keyword) + r'\b', msg.lower()):
                    intent_indicators.append(keyword)
                    break
        
        # Calcular indicadores de rechazo
        rejection_indicators = []
        for phrase in self.REJECTION_KEYWORDS:
            for msg in recent_messages:
                if phrase in msg.lower():
                    rejection_indicators.append(phrase)
                    break
        
        # Eliminar duplicados
        intent_indicators = list(set(intent_indicators))
        rejection_indicators = list(set(rejection_indicators))
        
        # Calcular probabilidad de compra
        intent_score = len(intent_indicators) * 0.15  # Cada indicador suma 15%
        rejection_score = len(rejection_indicators) * 0.2  # Cada indicador resta 20%
        
        # Ajustar por longitud y engagement
        avg_msg_length = sum(len(msg) for msg in recent_messages) / len(recent_messages)
        engagement_bonus = min(0.1, avg_msg_length / 200)  # Máximo 10% de bonus
        
        # Calcular probabilidad final
        purchase_intent_probability = max(0.0, min(1.0, intent_score - rejection_score + engagement_bonus))
        
        # Determinar si hay intención de compra
        has_purchase_intent = purchase_intent_probability >= self.INTENT_THRESHOLD
        has_rejection = len(rejection_indicators) > 0
        
        result = {
            "purchase_intent_probability": round(purchase_intent_probability, 2),
            "has_purchase_intent": has_purchase_intent,
            "has_rejection": has_rejection,
            "intent_indicators": intent_indicators,
            "rejection_indicators": rejection_indicators
        }
        
        logger.info(f"Análisis de intención: {result}")
        return result
    
    def should_continue_conversation(self, 
                                    messages: List[Dict[str, str]], 
                                    session_start_time: datetime,
                                    intent_detection_timeout: int) -> Tuple[bool, Optional[str]]:
        """
        Determina si una conversación debe continuar basado en la intención de compra y el tiempo.
        
        Args:
            messages: Lista de mensajes de la conversación
            session_start_time: Hora de inicio de la sesión
            intent_detection_timeout: Tiempo límite para detectar intención en segundos
            
        Returns:
            Tuple[bool, Optional[str]]: (Continuar conversación, Razón de finalización)
        """
        # Verificar si se ha superado el tiempo límite para detectar intención
        elapsed_seconds = (datetime.now() - session_start_time).total_seconds()
        
        # Si no se ha superado el tiempo límite, continuar la conversación
        if elapsed_seconds < intent_detection_timeout:
            return True, None
        
        # Analizar intención de compra
        intent_analysis = self.analyze_purchase_intent(messages)
        
        # Si hay intención de compra, continuar la conversación
        if intent_analysis["has_purchase_intent"]:
            return True, None
        
        # Si hay rechazo explícito, finalizar la conversación
        if intent_analysis["has_rejection"]:
            return False, "rejection_detected"
        
        # Si no hay intención de compra después del tiempo límite, finalizar
        return False, "no_intent_detected"
