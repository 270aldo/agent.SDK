"""
Utilidades para el procesamiento de datos en modelos predictivos.

Este módulo proporciona funciones comunes para el procesamiento de datos
utilizadas por los servicios predictivos.
"""

from typing import Dict, List, Any, Optional
import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)

def preprocess_text_data(text_list: List[str]) -> List[str]:
    """
    Preprocesa una lista de textos para análisis.
    
    Args:
        text_list: Lista de textos a preprocesar
        
    Returns:
        Lista de textos preprocesados
    """
    processed_texts = []
    
    try:
        for text in text_list:
            if not text:
                continue
                
            # Convertir a minúsculas
            text = text.lower()
            
            # Eliminar caracteres especiales y mantener espacios
            text = re.sub(r'[^\w\s]', '', text)
            
            # Eliminar espacios múltiples
            text = re.sub(r'\s+', ' ', text).strip()
            
            processed_texts.append(text)
            
        return processed_texts
        
    except Exception as e:
        logger.error(f"Error al preprocesar textos: {e}")
        return text_list

def extract_features_from_conversation(messages: List[Dict[str, Any]], 
                                 customer_profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Extrae características relevantes de una conversación y perfil de cliente.
    
    Args:
        messages: Lista de mensajes de la conversación
        customer_profile: Perfil del cliente (opcional)
        
    Returns:
        Diccionario con características extraídas
    """
    features = {
        "message_features": {},
        "conversation_features": {},
        "customer_features": {}
    }
    
    try:
        # Extraer características de mensajes
        if messages:
            # Separar mensajes por rol
            client_messages = [msg for msg in messages if msg.get("role") == "user"]
            agent_messages = [msg for msg in messages if msg.get("role") == "assistant"]
            
            # Características de mensajes del cliente
            if client_messages:
                client_text = [msg.get("content", "") for msg in client_messages]
                features["message_features"]["client_message_count"] = len(client_messages)
                features["message_features"]["avg_client_message_length"] = sum(len(txt) for txt in client_text) / len(client_text) if client_text else 0
                features["message_features"]["question_count"] = sum(1 for txt in client_text if "?" in txt)
                
            # Características de mensajes del agente
            if agent_messages:
                agent_text = [msg.get("content", "") for msg in agent_messages]
                features["message_features"]["agent_message_count"] = len(agent_messages)
                features["message_features"]["avg_agent_message_length"] = sum(len(txt) for txt in agent_text) / len(agent_text) if agent_text else 0
            
            # Características de la conversación
            features["conversation_features"]["total_messages"] = len(messages)
            features["conversation_features"]["conversation_turns"] = len(messages) // 2  # Aproximación de turnos
            
            # Calcular duración si hay timestamps
            if all("timestamp" in msg for msg in messages):
                try:
                    start_time = datetime.fromisoformat(messages[0]["timestamp"])
                    end_time = datetime.fromisoformat(messages[-1]["timestamp"])
                    duration_seconds = (end_time - start_time).total_seconds()
                    features["conversation_features"]["duration_seconds"] = duration_seconds
                    features["conversation_features"]["avg_response_time"] = duration_seconds / (len(messages) - 1) if len(messages) > 1 else 0
                except (ValueError, KeyError) as e:
                    logger.warning(f"Error parsing timestamps for conversation duration: {e}")
                    features["conversation_features"]["duration_seconds"] = 0
                    features["conversation_features"]["avg_response_time"] = 0
        
        # Extraer características del perfil del cliente
        if customer_profile:
            # Características demográficas
            if "demographics" in customer_profile:
                demographics = customer_profile["demographics"]
                features["customer_features"]["age"] = demographics.get("age")
                features["customer_features"]["gender"] = demographics.get("gender")
                features["customer_features"]["location"] = demographics.get("location")
            
            # Historial de compras
            if "purchase_history" in customer_profile:
                purchase_history = customer_profile["purchase_history"]
                features["customer_features"]["purchase_count"] = len(purchase_history)
                features["customer_features"]["avg_purchase_value"] = sum(p.get("value", 0) for p in purchase_history) / len(purchase_history) if purchase_history else 0
                features["customer_features"]["last_purchase_days"] = (datetime.now() - datetime.fromisoformat(purchase_history[-1]["date"])).days if purchase_history else None
            
            # Interacciones previas
            if "interactions" in customer_profile:
                interactions = customer_profile["interactions"]
                features["customer_features"]["previous_interactions"] = len(interactions)
                features["customer_features"]["successful_interactions"] = sum(1 for i in interactions if i.get("outcome") == "successful")
                
        return features
        
    except Exception as e:
        logger.error(f"Error al extraer características: {e}")
        return features

def filter_messages_by_timeframe(messages: List[Dict[str, Any]], 
                           max_messages: int = 10,
                           max_hours: Optional[float] = None) -> List[Dict[str, Any]]:
    """
    Filtra mensajes por marco temporal o cantidad.
    
    Args:
        messages: Lista de mensajes a filtrar
        max_messages: Número máximo de mensajes a considerar
        max_hours: Máximo de horas hacia atrás (opcional)
        
    Returns:
        Lista filtrada de mensajes
    """
    try:
        # Ordenar mensajes por timestamp si existe
        if messages and "timestamp" in messages[0]:
            sorted_messages = sorted(messages, key=lambda x: x.get("timestamp", ""))
        else:
            sorted_messages = messages
            
        # Limitar por cantidad
        recent_messages = sorted_messages[-max_messages:] if len(sorted_messages) > max_messages else sorted_messages
        
        # Limitar por tiempo si se especifica
        if max_hours is not None and recent_messages and "timestamp" in recent_messages[0]:
            now = datetime.now()
            time_limit = now.timestamp() - (max_hours * 3600)  # Convertir horas a segundos
            
            time_filtered = [
                msg for msg in recent_messages 
                if datetime.fromisoformat(msg.get("timestamp", now.isoformat())).timestamp() >= time_limit
            ]
            
            return time_filtered
            
        return recent_messages
        
    except Exception as e:
        logger.error(f"Error al filtrar mensajes por timeframe: {e}")
        # Fallback a limitar solo por cantidad
        return messages[-max_messages:] if len(messages) > max_messages else messages
