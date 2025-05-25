"""
Servicio para análisis avanzado de sentimiento en conversaciones.
"""

import logging
import re
from typing import Dict, Any, List, Tuple, Optional
import numpy as np

# Configurar logging
logger = logging.getLogger(__name__)

class AdvancedSentimentService:
    """
    Servicio para análisis avanzado de sentimiento en conversaciones.
    Proporciona análisis detallado de emociones, cambios de sentimiento y señales de urgencia.
    """
    
    # Patrones de emociones específicas
    EMOTION_PATTERNS = {
        'frustración': [
            r'frustr[oa]d[oa]', r'molest[oa]', r'enoj[oa]d[oa]', r'irritad[oa]',
            r'no entiendo', r'no funciona', r'no puedo', r'difícil', r'complicado',
            r'(!+)', r'(?:muy|bastante|demasiado) (?:confundid[oa]|perdid[oa])',
            r'(?:esto|eso) no tiene sentido'
        ],
        'entusiasmo': [
            r'genial', r'excelente', r'fantástic[oa]', r'increíble', r'asombroso',
            r'me encanta', r'perfecto', r'maravillos[oa]', r'espectacular',
            r'(!+)', r'(?:muy|bastante|realmente) (?:buen[oa]|interesante)',
            r'(?:estoy|estamos) (?:emocionad[oa]s?|contentad[oa]s?)'
        ],
        'confusión': [
            r'confundid[oa]', r'perdid[oa]', r'no comprendo', r'no entiendo',
            r'\?{2,}', r'(?:qué|cómo|por qué)(?:\s+es|\s+significa|\s+quiere decir)?',
            r'(?:podrías|puedes) explicar', r'no (?:me|nos) queda claro',
            r'(?:estoy|estamos) (?:confundid[oa]s?|perdid[oa]s?)'
        ],
        'urgencia': [
            r'urgent[e]', r'rápido', r'pronto', r'inmediatamente', r'ahora mismo',
            r'(?:necesito|necesitamos) (?:ya|ahora|pronto|cuanto antes)',
            r'(?:es|resulta) (?:urgente|prioritario|crítico)',
            r'no (?:puedo|podemos) esperar', r'(?:para|antes de) (?:hoy|mañana|ya)'
        ],
        'indecisión': [
            r'no (?:estoy|estamos) segur[oa]s?', r'quizá[s]?', r'tal vez',
            r'(?:podría|podrías|podríamos) (?:ser|estar|tener)',
            r'(?:no sé|no sabemos|no estoy convencid[oa])',
            r'(?:por un lado|por otro lado)', r'(?:tengo|tenemos) dudas',
            r'(?:estoy|estamos) (?:indecis[oa]s?|dudos[oa]s?)'
        ]
    }
    
    # Palabras clave para análisis de sentimiento
    SENTIMENT_KEYWORDS = {
        'positivo': [
            'bueno', 'excelente', 'genial', 'fantástico', 'increíble', 'maravilloso',
            'perfecto', 'encanta', 'gusta', 'satisfecho', 'feliz', 'contento',
            'agradecido', 'impresionado', 'útil', 'claro', 'fácil', 'sencillo',
            'recomendable', 'eficiente', 'efectivo', 'valioso', 'beneficioso'
        ],
        'negativo': [
            'malo', 'terrible', 'horrible', 'pésimo', 'deficiente', 'decepcionante',
            'frustrante', 'confuso', 'difícil', 'complicado', 'molesto', 'irritante',
            'inútil', 'costoso', 'caro', 'lento', 'problemático', 'error', 'falla',
            'imposible', 'desagradable', 'insatisfecho', 'insuficiente'
        ],
        'neutral': [
            'ok', 'bien', 'normal', 'regular', 'estándar', 'promedio', 'aceptable',
            'suficiente', 'adecuado', 'común', 'típico', 'ordinario', 'usual',
            'corriente', 'convencional', 'moderado', 'tolerable'
        ]
    }
    
    # Intensificadores y atenuadores
    INTENSIFIERS = [
        'muy', 'bastante', 'extremadamente', 'increíblemente', 'realmente',
        'absolutamente', 'completamente', 'totalmente', 'sumamente', 'demasiado'
    ]
    
    DIMINISHERS = [
        'poco', 'algo', 'ligeramente', 'apenas', 'un poco', 'no muy',
        'relativamente', 'moderadamente', 'parcialmente', 'no del todo'
    ]
    
    def __init__(self):
        """Inicializar el servicio de análisis avanzado de sentimiento."""
        logger.info("Servicio de análisis avanzado de sentimiento inicializado")
        
        # Compilar patrones de emociones para mejor rendimiento
        self.compiled_patterns = {}
        for emotion, patterns in self.EMOTION_PATTERNS.items():
            self.compiled_patterns[emotion] = [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analiza el sentimiento general de un texto.
        
        Args:
            text: Texto a analizar
            
        Returns:
            Dict: Resultado del análisis con puntuación y clasificación
        """
        # Inicializar puntuación
        score = 0.0
        word_count = len(text.split())
        
        # Contar palabras positivas y negativas
        positive_count = 0
        negative_count = 0
        
        # Analizar palabras clave de sentimiento
        for word in text.lower().split():
            # Eliminar signos de puntuación
            word = re.sub(r'[^\w\s]', '', word)
            
            # Verificar palabras positivas
            if word in self.SENTIMENT_KEYWORDS['positivo']:
                positive_count += 1
                score += 1.0
                
            # Verificar palabras negativas
            elif word in self.SENTIMENT_KEYWORDS['negativo']:
                negative_count += 1
                score -= 1.0
                
            # Verificar palabras neutrales
            elif word in self.SENTIMENT_KEYWORDS['neutral']:
                score += 0.2
        
        # Ajustar por longitud del texto para evitar sesgos
        if word_count > 0:
            normalized_score = score / word_count
        else:
            normalized_score = 0
            
        # Clasificar sentimiento
        if normalized_score > 0.1:
            sentiment = "positivo"
        elif normalized_score < -0.1:
            sentiment = "negativo"
        else:
            sentiment = "neutral"
            
        # Calcular intensidad (0-1)
        intensity = min(1.0, abs(normalized_score) * 2)
            
        return {
            "score": normalized_score,
            "sentiment": sentiment,
            "intensity": intensity,
            "positive_count": positive_count,
            "negative_count": negative_count,
            "word_count": word_count
        }
    
    def detect_emotions(self, text: str) -> Dict[str, float]:
        """
        Detecta emociones específicas en un texto.
        
        Args:
            text: Texto a analizar
            
        Returns:
            Dict: Emociones detectadas con sus puntuaciones (0-1)
        """
        results = {}
        
        # Analizar cada emoción
        for emotion, patterns in self.compiled_patterns.items():
            # Contar coincidencias para cada patrón
            matches = 0
            for pattern in patterns:
                matches += len(pattern.findall(text))
                
            # Normalizar puntuación (0-1)
            word_count = max(1, len(text.split()))
            score = min(1.0, matches / (word_count / 2))
            
            results[emotion] = score
            
        return results
    
    def analyze_sentiment_change(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Analiza el cambio de sentimiento a lo largo de una conversación.
        
        Args:
            messages: Lista de mensajes de la conversación
            
        Returns:
            Dict: Análisis del cambio de sentimiento
        """
        # Extraer solo mensajes del usuario
        user_messages = [msg['content'] for msg in messages if msg.get('role') == 'user']
        
        if len(user_messages) < 2:
            return {
                "trend": "estable",
                "delta": 0.0,
                "initial_sentiment": "neutral",
                "final_sentiment": "neutral"
            }
            
        # Analizar sentimiento de cada mensaje
        sentiment_scores = []
        for message in user_messages:
            analysis = self.analyze_sentiment(message)
            sentiment_scores.append(analysis['score'])
            
        # Calcular tendencia
        initial_score = sentiment_scores[0]
        final_score = sentiment_scores[-1]
        delta = final_score - initial_score
        
        # Determinar tendencia
        if delta > 0.2:
            trend = "mejorando"
        elif delta < -0.2:
            trend = "empeorando"
        else:
            trend = "estable"
            
        # Determinar sentimientos inicial y final
        initial_sentiment = "positivo" if initial_score > 0.1 else "negativo" if initial_score < -0.1 else "neutral"
        final_sentiment = "positivo" if final_score > 0.1 else "negativo" if final_score < -0.1 else "neutral"
            
        return {
            "trend": trend,
            "delta": delta,
            "initial_sentiment": initial_sentiment,
            "final_sentiment": final_sentiment,
            "scores": sentiment_scores
        }
    
    def detect_urgency(self, text: str) -> Dict[str, Any]:
        """
        Detecta señales de urgencia en un texto.
        
        Args:
            text: Texto a analizar
            
        Returns:
            Dict: Nivel de urgencia y señales detectadas
        """
        urgency_patterns = self.compiled_patterns['urgencia']
        
        # Buscar coincidencias
        matches = []
        for pattern in urgency_patterns:
            for match in pattern.finditer(text):
                matches.append(match.group())
                
        # Calcular nivel de urgencia (0-1)
        word_count = max(1, len(text.split()))
        urgency_level = min(1.0, len(matches) / (word_count / 3))
        
        # Clasificar nivel de urgencia
        if urgency_level > 0.5:
            urgency_class = "alta"
        elif urgency_level > 0.2:
            urgency_class = "media"
        else:
            urgency_class = "baja"
            
        return {
            "level": urgency_level,
            "class": urgency_class,
            "signals": matches
        }
    
    def detect_indecision(self, text: str) -> Dict[str, Any]:
        """
        Detecta señales de indecisión en un texto.
        
        Args:
            text: Texto a analizar
            
        Returns:
            Dict: Nivel de indecisión y señales detectadas
        """
        indecision_patterns = self.compiled_patterns['indecisión']
        
        # Buscar coincidencias
        matches = []
        for pattern in indecision_patterns:
            for match in pattern.finditer(text):
                matches.append(match.group())
                
        # Calcular nivel de indecisión (0-1)
        word_count = max(1, len(text.split()))
        indecision_level = min(1.0, len(matches) / (word_count / 3))
        
        # Clasificar nivel de indecisión
        if indecision_level > 0.5:
            indecision_class = "alta"
        elif indecision_level > 0.2:
            indecision_class = "media"
        else:
            indecision_class = "baja"
            
        return {
            "level": indecision_level,
            "class": indecision_class,
            "signals": matches
        }
    
    def get_comprehensive_analysis(self, text: str) -> Dict[str, Any]:
        """
        Realiza un análisis completo de sentimiento, emociones, urgencia e indecisión.
        
        Args:
            text: Texto a analizar
            
        Returns:
            Dict: Resultados completos del análisis
        """
        results = {
            "sentiment": self.analyze_sentiment(text),
            "emotions": self.detect_emotions(text),
            "urgency": self.detect_urgency(text),
            "indecision": self.detect_indecision(text)
        }
        
        # Determinar emoción dominante
        emotions = results["emotions"]
        dominant_emotion = max(emotions.items(), key=lambda x: x[1])
        
        results["dominant_emotion"] = {
            "name": dominant_emotion[0],
            "score": dominant_emotion[1]
        }
        
        return results
    
    def analyze_conversation(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Analiza una conversación completa, incluyendo cambios de sentimiento.
        
        Args:
            messages: Lista de mensajes de la conversación
            
        Returns:
            Dict: Análisis completo de la conversación
        """
        # Extraer solo mensajes del usuario
        user_messages = [msg['content'] for msg in messages if msg.get('role') == 'user']
        
        if not user_messages:
            return {
                "overall_sentiment": "neutral",
                "sentiment_trend": "estable",
                "dominant_emotion": "ninguna",
                "urgency": "baja",
                "indecision": "baja"
            }
            
        # Concatenar todos los mensajes para análisis general
        all_text = " ".join(user_messages)
        
        # Análisis completo del texto combinado
        comprehensive = self.get_comprehensive_analysis(all_text)
        
        # Análisis de cambio de sentimiento
        sentiment_change = self.analyze_sentiment_change(messages)
        
        return {
            "overall_sentiment": comprehensive["sentiment"]["sentiment"],
            "sentiment_score": comprehensive["sentiment"]["score"],
            "sentiment_trend": sentiment_change["trend"],
            "dominant_emotion": comprehensive["dominant_emotion"]["name"],
            "emotion_score": comprehensive["dominant_emotion"]["score"],
            "urgency": comprehensive["urgency"]["class"],
            "urgency_level": comprehensive["urgency"]["level"],
            "indecision": comprehensive["indecision"]["class"],
            "indecision_level": comprehensive["indecision"]["level"],
            "detailed": {
                "sentiment": comprehensive["sentiment"],
                "emotions": comprehensive["emotions"],
                "sentiment_change": sentiment_change
            }
        }
