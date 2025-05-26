"""
Utilidades para la detección de señales en conversaciones.

Este módulo proporciona funciones comunes para detectar diferentes tipos de señales
en mensajes de conversación, utilizadas por los servicios predictivos.
"""

from typing import Dict, List, Any, Optional
import logging
import re

logger = logging.getLogger(__name__)

async def detect_sentiment_signals(messages: List[Dict[str, Any]], nlp_service) -> Dict[str, float]:
    """
    Detecta señales basadas en sentimiento en mensajes.
    
    Args:
        messages: Lista de mensajes a analizar
        nlp_service: Servicio NLP para análisis de sentimiento
        
    Returns:
        Diccionario con señales de sentimiento detectadas y sus intensidades
    """
    sentiment_signals = {
        "positive_sentiment": 0.0,
        "negative_sentiment": 0.0,
        "neutral_sentiment": 0.0
    }
    
    try:
        # Extraer solo el texto de los mensajes del cliente
        client_messages = [msg["content"] for msg in messages if msg.get("role") == "user"]
        
        if not client_messages:
            return sentiment_signals
            
        # Analizar sentimiento de los mensajes
        for message in client_messages:
            sentiment_result = await nlp_service.analyze_sentiment(message)
            
            if sentiment_result:
                sentiment = sentiment_result.get("sentiment", "neutral")
                score = sentiment_result.get("score", 0.5)
                
                if sentiment == "positive":
                    sentiment_signals["positive_sentiment"] += score
                elif sentiment == "negative":
                    sentiment_signals["negative_sentiment"] += score
                else:
                    sentiment_signals["neutral_sentiment"] += score
        
        # Normalizar las señales
        total_messages = len(client_messages) or 1
        for key in sentiment_signals:
            sentiment_signals[key] /= total_messages
            
        return sentiment_signals
        
    except Exception as e:
        logger.error(f"Error al detectar señales de sentimiento: {e}")
        return sentiment_signals

async def detect_keyword_signals(messages: List[Dict[str, Any]], keywords_dict: Dict[str, List[str]]) -> Dict[str, float]:
    """
    Detecta señales basadas en palabras clave en mensajes.
    
    Args:
        messages: Lista de mensajes a analizar
        keywords_dict: Diccionario de categorías con sus palabras clave asociadas
        
    Returns:
        Diccionario con señales de palabras clave detectadas y sus intensidades
    """
    keyword_signals = {category: 0.0 for category in keywords_dict}
    
    try:
        # Extraer solo el texto de los mensajes del cliente
        client_messages = [msg["content"].lower() for msg in messages if msg.get("role") == "user"]
        
        if not client_messages:
            return keyword_signals
            
        # Buscar palabras clave en los mensajes
        for message in client_messages:
            for category, keywords in keywords_dict.items():
                for keyword in keywords:
                    if re.search(r'\b' + re.escape(keyword.lower()) + r'\b', message):
                        keyword_signals[category] += 1
        
        # Normalizar las señales
        total_messages = len(client_messages) or 1
        for key in keyword_signals:
            keyword_signals[key] /= total_messages
            
        return keyword_signals
        
    except Exception as e:
        logger.error(f"Error al detectar señales de palabras clave: {e}")
        return keyword_signals

async def detect_question_patterns(messages: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Detecta patrones de preguntas en mensajes.
    
    Args:
        messages: Lista de mensajes a analizar
        
    Returns:
        Diccionario con señales de patrones de preguntas detectadas y sus intensidades
    """
    question_signals = {
        "direct_questions": 0.0,
        "clarification_questions": 0.0,
        "comparison_questions": 0.0
    }
    
    try:
        # Extraer solo el texto de los mensajes del cliente
        client_messages = [msg["content"] for msg in messages if msg.get("role") == "user"]
        
        if not client_messages:
            return question_signals
            
        # Patrones de expresiones regulares para diferentes tipos de preguntas
        patterns = {
            "direct_questions": r'\b(qué|cómo|cuándo|dónde|por qué|quién|cuál|cuánto)\b.*\?',
            "clarification_questions": r'\b(podrías|puedes|podría|puede|me puedes|me podrías|explica|explique|aclara|aclare)\b.*\?',
            "comparison_questions": r'\b(versus|vs|comparado|comparar|diferencia|mejor|peor|entre)\b'
        }
        
        # Buscar patrones en los mensajes
        for message in client_messages:
            for pattern_type, pattern in patterns.items():
                if re.search(pattern, message, re.IGNORECASE):
                    question_signals[pattern_type] += 1
        
        # Normalizar las señales
        total_messages = len(client_messages) or 1
        for key in question_signals:
            question_signals[key] /= total_messages
            
        return question_signals
        
    except Exception as e:
        logger.error(f"Error al detectar patrones de preguntas: {e}")
        return question_signals

async def detect_engagement_signals(messages: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Detecta señales de engagement en la conversación.
    
    Args:
        messages: Lista de mensajes a analizar
        
    Returns:
        Diccionario con señales de engagement detectadas y sus intensidades
    """
    engagement_signals = {
        "message_length": 0.0,
        "response_time": 0.0,
        "conversation_continuity": 0.0
    }
    
    try:
        # Extraer solo los mensajes del cliente
        client_messages = [msg for msg in messages if msg.get("role") == "user"]
        
        if not client_messages:
            return engagement_signals
            
        # Calcular longitud promedio de mensajes
        avg_length = sum(len(msg["content"]) for msg in client_messages) / len(client_messages)
        # Normalizar a un rango aproximado de 0-1 (asumiendo que 200 caracteres es un mensaje largo)
        engagement_signals["message_length"] = min(avg_length / 200, 1.0)
        
        # Calcular continuidad de la conversación (proporción de mensajes del cliente)
        engagement_signals["conversation_continuity"] = len(client_messages) / len(messages) if messages else 0
        
        # TODO: Implementar cálculo de tiempo de respuesta si los mensajes tienen timestamps
        
        return engagement_signals
        
    except Exception as e:
        logger.error(f"Error al detectar señales de engagement: {e}")
        return engagement_signals
