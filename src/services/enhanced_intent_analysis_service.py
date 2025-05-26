"""
Servicio mejorado para analizar la intención de compra en conversaciones.
Incluye análisis de sentimiento, personalización por industria y aprendizaje continuo.
"""

import logging
import re
import json
import os
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
import numpy as np
from collections import Counter

from src.integrations.supabase import resilient_supabase_client

# Configurar logging
logger = logging.getLogger(__name__)

class EnhancedIntentAnalysisService:
    """
    Servicio mejorado para analizar la intención de compra en conversaciones.
    Implementa análisis de sentimiento, personalización por industria y aprendizaje continuo.
    """
    
    # Palabras clave base para detectar intención de compra
    BASE_PURCHASE_INTENT_KEYWORDS = [
        'comprar', 'adquirir', 'precio', 'costo', 'tarjeta', 'pagar', 'pago', 
        'suscripción', 'suscribir', 'contratar', 'plan', 'oferta', 'promoción',
        'descuento', 'cuánto cuesta', 'cuánto vale', 'interesado', 'me interesa',
        'quiero', 'necesito', 'inversión', 'presupuesto', 'opciones', 'alternativas'
    ]
    
    # Palabras clave base para detectar rechazo
    BASE_REJECTION_KEYWORDS = [
        'no me interesa', 'no quiero', 'no puedo', 'no ahora', 'tal vez después',
        'lo pensaré', 'muy caro', 'demasiado caro', 'no tengo dinero', 'no puedo pagar',
        'no estoy seguro', 'tengo dudas', 'necesito pensarlo', 'no es lo que busco',
        'no me convence', 'no es el momento', 'no es prioridad', 'no es para mí'
    ]
    
    # Palabras clave específicas por industria
    INDUSTRY_KEYWORDS = {
        'salud': {
            'intent': [
                'resultados', 'beneficios', 'mejora', 'salud', 'bienestar', 'tratamiento',
                'consulta', 'cita', 'programa', 'seguimiento', 'progreso', 'evaluación'
            ],
            'rejection': [
                'efectos secundarios', 'riesgos', 'no es seguro', 'prefiero alternativas naturales',
                'necesito consultar con mi médico', 'no tengo síntomas'
            ]
        },
        'finanzas': {
            'intent': [
                'rendimiento', 'retorno', 'inversión', 'portfolio', 'cartera', 'interés',
                'dividendos', 'ganancias', 'rentabilidad', 'plazo', 'riesgo', 'asesoría'
            ],
            'rejection': [
                'mercado inestable', 'prefiero esperar', 'demasiado riesgo', 'comisiones altas',
                'prefiero otro tipo de inversión', 'no es buen momento económico'
            ]
        },
        'tecnología': {
            'intent': [
                'características', 'funcionalidades', 'especificaciones', 'versión', 'actualización',
                'compatibilidad', 'integración', 'implementación', 'soporte', 'mantenimiento'
            ],
            'rejection': [
                'incompatible', 'demasiado complejo', 'prefiero otra solución', 'no tenemos infraestructura',
                'necesitamos más tiempo para evaluar', 'no cumple con nuestros requisitos'
            ]
        },
        'educación': {
            'intent': [
                'curso', 'programa', 'certificación', 'clases', 'aprendizaje', 'formación',
                'inscripción', 'matrícula', 'contenido', 'materiales', 'metodología'
            ],
            'rejection': [
                'no tengo tiempo para estudiar', 'prefiero otro formato', 'no es lo que busco aprender',
                'necesito algo más avanzado/básico', 'prefiero educación presencial/virtual'
            ]
        }
    }
    
    # Frases que indican sentimiento positivo
    POSITIVE_SENTIMENT_PHRASES = [
        'me gusta', 'suena bien', 'interesante', 'excelente', 'perfecto', 'genial',
        'fantástico', 'maravilloso', 'increíble', 'impresionante', 'me encanta',
        'buena idea', 'de acuerdo', 'claro', 'por supuesto', 'definitivamente',
        'sin duda', 'absolutamente', 'me parece bien', 'estoy satisfecho'
    ]
    
    # Frases que indican sentimiento negativo
    NEGATIVE_SENTIMENT_PHRASES = [
        'no me gusta', 'no suena bien', 'no es interesante', 'malo', 'terrible',
        'horrible', 'decepcionante', 'frustrante', 'no me convence', 'no estoy de acuerdo',
        'en desacuerdo', 'no es lo que esperaba', 'no cumple mis expectativas',
        'no es suficiente', 'deja mucho que desear', 'no me satisface'
    ]
    
    # Umbral de intención de compra para continuar la conversación
    INTENT_THRESHOLD = 0.4  # 40% de probabilidad de compra
    
    def __init__(self, industry: str = 'salud'):
        """
        Inicializar el servicio de análisis de intención mejorado.
        
        Args:
            industry: Industria para personalizar las palabras clave
        """
        self.industry = industry.lower()
        self.purchase_intent_keywords = self._get_industry_intent_keywords(industry)
        self.rejection_keywords = self._get_industry_rejection_keywords(industry)
        self.intent_model = None
        logger.info(f"Servicio de análisis de intención mejorado inicializado para industria: {industry}")
        
    @classmethod
    async def create(cls, industry: str = 'salud'):
        """
        Método de fábrica para crear una instancia del servicio de forma asíncrona.
        
        Args:
            industry: Industria para personalizar las palabras clave
            
        Returns:
            EnhancedIntentAnalysisService: Instancia inicializada del servicio
        """
        instance = cls(industry)
        instance.intent_model = await instance._load_intent_model()
        return instance
    
    def _get_industry_intent_keywords(self, industry: str) -> List[str]:
        """
        Obtiene las palabras clave de intención de compra para una industria específica.
        
        Args:
            industry: Nombre de la industria
            
        Returns:
            List[str]: Lista combinada de palabras clave
        """
        # Combinar palabras clave base con las específicas de la industria
        industry_keywords = self.INDUSTRY_KEYWORDS.get(industry, {}).get('intent', [])
        return self.BASE_PURCHASE_INTENT_KEYWORDS + industry_keywords
    
    def _get_industry_rejection_keywords(self, industry: str) -> List[str]:
        """
        Obtiene las palabras clave de rechazo para una industria específica.
        
        Args:
            industry: Nombre de la industria
            
        Returns:
            List[str]: Lista combinada de palabras clave
        """
        # Combinar palabras clave base con las específicas de la industria
        industry_keywords = self.INDUSTRY_KEYWORDS.get(industry, {}).get('rejection', [])
        return self.BASE_REJECTION_KEYWORDS + industry_keywords
    
    async def _load_intent_model(self) -> Dict[str, Any]:
        """
        Carga el modelo de intención de compra desde el almacenamiento.
        Si no existe, crea uno nuevo.
        
        Returns:
            Dict: Modelo de intención de compra
        """
        try:
            # Buscar modelo existente para la industria usando el cliente resiliente
            result = await resilient_supabase_client.select(
                table='intent_models',
                filters={'industry': self.industry}
            )
            
            if result and len(result) > 0:
                model_data = result[0]
                logger.info(f"Modelo de intención cargado para industria {self.industry}")
                return {
                    'id': model_data['id'],
                    'industry': model_data['industry'],
                    'intent_keywords': json.loads(model_data['intent_keywords']),
                    'rejection_keywords': json.loads(model_data['rejection_keywords']),
                    'keyword_weights': json.loads(model_data['keyword_weights']),
                    'sentiment_weights': json.loads(model_data['sentiment_weights']),
                    'created_at': model_data['created_at']
                }
        except Exception as e:
            logger.warning(f"No se pudo cargar el modelo de intención: {e}")
        
        # Si no se pudo cargar, crear un modelo nuevo
        logger.info(f"Creando nuevo modelo de intención para industria {self.industry}")
        
        # Modelo inicial con pesos uniformes
        intent_keywords = self.purchase_intent_keywords
        rejection_keywords = self.rejection_keywords
        
        # Pesos iniciales para palabras clave (1.0 para todas)
        keyword_weights = {keyword: 1.0 for keyword in intent_keywords}
        
        # Pesos iniciales para análisis de sentimiento
        sentiment_weights = {
            'positive': 0.2,  # Impacto del sentimiento positivo
            'negative': -0.3,  # Impacto del sentimiento negativo
            'engagement': 0.1,  # Impacto del nivel de engagement
            'question_ratio': -0.1  # Impacto de la proporción de preguntas
        }
        
        # Crear nuevo modelo
        model = {
            'id': None,
            'industry': self.industry,
            'intent_keywords': intent_keywords,
            'rejection_keywords': rejection_keywords,
            'keyword_weights': keyword_weights,
            'sentiment_weights': sentiment_weights,
            'created_at': datetime.now().isoformat()
        }
        
        # Intentar guardar el modelo en Supabase
        try:
            model_data = {
                'industry': model['industry'],
                'intent_keywords': json.dumps(model['intent_keywords']),
                'rejection_keywords': json.dumps(model['rejection_keywords']),
                'keyword_weights': json.dumps(model['keyword_weights']),
                'sentiment_weights': json.dumps(model['sentiment_weights']),
                'created_at': model['created_at']
            }
            
            result = await resilient_supabase_client.insert(
                table='intent_models',
                data=model_data
            )
            
            if result and len(result) > 0:
                model['id'] = result[0]['id']
                logger.info(f"Nuevo modelo de intención guardado con ID: {model['id']}")
        except Exception as e:
            logger.error(f"Error al guardar el modelo de intención: {e}")
        
        return model
    
    async def analyze_purchase_intent(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Analiza la intención de compra en los mensajes de una conversación.
        Incorpora análisis de sentimiento y palabras clave específicas por industria.
        
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
                "rejection_indicators": [],
                "sentiment_score": 0.0,
                "engagement_score": 0.0
            }
        
        # Analizar los últimos 3 mensajes del usuario (o todos si hay menos)
        recent_messages = user_messages[-3:]
        
        # Calcular indicadores de intención de compra con pesos personalizados
        intent_indicators = []
        intent_scores = []
        
        for keyword in self.intent_model['intent_keywords']:
            for msg in recent_messages:
                if re.search(r'\b' + re.escape(keyword) + r'\b', msg.lower()):
                    weight = self.intent_model['keyword_weights'].get(keyword, 1.0)
                    intent_indicators.append(keyword)
                    intent_scores.append(weight)
                    break
        
        # Calcular indicadores de rechazo
        rejection_indicators = []
        for phrase in self.intent_model['rejection_keywords']:
            for msg in recent_messages:
                if phrase in msg.lower():
                    rejection_indicators.append(phrase)
                    break
        
        # Eliminar duplicados
        intent_indicators = list(set(intent_indicators))
        rejection_indicators = list(set(rejection_indicators))
        
        # Análisis de sentimiento
        sentiment_score = await self._analyze_sentiment(recent_messages)
        
        # Análisis de engagement
        engagement_score = await self._analyze_engagement(recent_messages)
        
        # Calcular probabilidad de compra
        intent_score = sum(intent_scores) * 0.15  # Cada indicador suma según su peso
        rejection_score = len(rejection_indicators) * 0.2  # Cada indicador resta 20%
        
        # Ajustar por sentimiento y engagement
        sentiment_adjustment = sentiment_score * self.intent_model['sentiment_weights']['positive']
        if sentiment_score < 0:
            sentiment_adjustment = sentiment_score * abs(self.intent_model['sentiment_weights']['negative'])
            
        engagement_adjustment = engagement_score * self.intent_model['sentiment_weights']['engagement']
        
        # Calcular probabilidad final
        purchase_intent_probability = max(0.0, min(1.0, 
            intent_score - rejection_score + sentiment_adjustment + engagement_adjustment
        ))
        
        # Determinar si hay intención de compra
        has_purchase_intent = purchase_intent_probability >= self.INTENT_THRESHOLD
        has_rejection = len(rejection_indicators) > 0
        
        result = {
            "purchase_intent_probability": round(purchase_intent_probability, 2),
            "has_purchase_intent": has_purchase_intent,
            "has_rejection": has_rejection,
            "intent_indicators": intent_indicators,
            "rejection_indicators": rejection_indicators,
            "sentiment_score": round(sentiment_score, 2),
            "engagement_score": round(engagement_score, 2)
        }
        
        logger.info(f"Análisis de intención mejorado: {result}")
        
        return result
    
    async def _analyze_sentiment(self, messages: List[str]) -> float:
        """
        Analiza el sentimiento en los mensajes del usuario.
        
        Args:
            messages: Lista de mensajes del usuario
            
        Returns:
            float: Puntuación de sentimiento (-1.0 a 1.0)
        """
        if not messages:
            return 0.0
        
        positive_count = 0
        negative_count = 0
        
        # Contar frases positivas y negativas
        for msg in messages:
            msg_lower = msg.lower()
            
            for phrase in self.POSITIVE_SENTIMENT_PHRASES:
                if phrase in msg_lower:
                    positive_count += 1
            
            for phrase in self.NEGATIVE_SENTIMENT_PHRASES:
                if phrase in msg_lower:
                    negative_count += 1
        
        # Calcular puntuación de sentimiento
        total_indicators = positive_count + negative_count
        if total_indicators == 0:
            return 0.0
        
        return (positive_count - negative_count) / total_indicators
    
    async def _analyze_engagement(self, messages: List[str]) -> float:
        """
        Analiza el nivel de engagement del usuario basado en la longitud de los mensajes,
        uso de preguntas, etc.
        
        Args:
            messages: Lista de mensajes del usuario
            
        Returns:
            float: Puntuación de engagement (0.0 a 1.0)
        """
        if not messages:
            return 0.0
        
        # Calcular longitud promedio de mensajes
        avg_length = sum(len(msg) for msg in messages) / len(messages)
        length_score = min(1.0, avg_length / 200)  # Normalizar a 0-1
        
        # Contar preguntas (indicador de interés)
        question_count = sum(1 for msg in messages if '?' in msg)
        question_ratio = question_count / len(messages)
        
        # Penalizar si hay demasiadas preguntas (podría indicar confusión)
        question_score = 0.5 if question_ratio <= 0.5 else 1.0 - question_ratio
        
        # Combinar factores
        engagement_score = (length_score * 0.7) + (question_score * 0.3)
        
        return engagement_score
    
    async def should_continue_conversation(self, messages: List[Dict[str, str]], 
                                    session_start_time: datetime,
                                    intent_detection_timeout: int = 300) -> Tuple[bool, Optional[str]]:
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
        intent_analysis = await self.analyze_purchase_intent(messages)
        
        # Si hay intención de compra, continuar la conversación
        if intent_analysis["has_purchase_intent"]:
            return True, None
        
        # Si hay rechazo explícito, finalizar la conversación
        if intent_analysis["has_rejection"]:
            return False, "rejection_detected"
        
        # Si no hay intención de compra después del tiempo límite, finalizar
        return False, "no_intent_detected"
    
    async def update_model_from_conversation(self, conversation_id: str, 
                                           messages: List[Dict[str, str]], 
                                           conversion_result: bool) -> bool:
        """
        Actualiza el modelo de intención basado en los resultados de una conversación.
        Implementa aprendizaje continuo para mejorar la detección de intención.
        
        Args:
            conversation_id: ID de la conversación
            messages: Lista de mensajes de la conversación
            conversion_result: Si la conversación resultó en una conversión
            
        Returns:
            bool: True si el modelo se actualizó correctamente
        """
        try:
            # Extraer mensajes del usuario
            user_messages = [msg["content"] for msg in messages if msg["role"] == "user"]
            
            if not user_messages:
                logger.warning(f"No hay mensajes de usuario para actualizar el modelo de {conversation_id}")
                return False
            
            # Analizar palabras y frases en los mensajes
            all_words = []
            for msg in user_messages:
                # Tokenizar mensaje en palabras
                words = re.findall(r'\b\w+\b', msg.lower())
                all_words.extend(words)
            
            # Contar frecuencia de palabras
            word_counts = Counter(all_words)
            
            # Actualizar pesos de palabras clave existentes
            keyword_weights = self.intent_model['keyword_weights'].copy()
            
            # Factor de ajuste basado en el resultado de la conversación
            adjustment_factor = 0.1 if conversion_result else -0.05
            
            # Actualizar pesos de palabras clave existentes
            for keyword in self.intent_model['intent_keywords']:
                # Si la palabra clave aparece en la conversación
                if any(keyword in msg.lower() for msg in user_messages):
                    current_weight = keyword_weights.get(keyword, 1.0)
                    # Ajustar peso según resultado de conversión
                    new_weight = max(0.1, min(2.0, current_weight + adjustment_factor))
                    keyword_weights[keyword] = new_weight
            
            # Identificar nuevas palabras clave potenciales
            common_words = [word for word, count in word_counts.items() 
                          if count >= 2 and len(word) > 3 and word not in self.intent_model['intent_keywords']]
            
            # Añadir nuevas palabras clave con peso inicial
            new_keywords = []
            for word in common_words[:5]:  # Limitar a 5 nuevas palabras por conversación
                if conversion_result:  # Solo añadir nuevas palabras si hubo conversión
                    self.intent_model['intent_keywords'].append(word)
                    keyword_weights[word] = 0.5  # Peso inicial conservador
                    new_keywords.append(word)
            
            if new_keywords:
                logger.info(f"Nuevas palabras clave añadidas al modelo: {new_keywords}")
            
            # Actualizar modelo con nuevos pesos
            updated_model = {
                'id': self.intent_model['id'],
                'industry': self.industry,
                'intent_keywords': self.intent_model['intent_keywords'],
                'rejection_keywords': self.intent_model['rejection_keywords'],
                'keyword_weights': keyword_weights,
                'sentiment_weights': self.intent_model['sentiment_weights'],
                'updated_at': datetime.now().isoformat()
            }
            
            # Guardar modelo actualizado en Supabase
            if self.intent_model['id']:
                model_data = {
                    'intent_keywords': json.dumps(updated_model['intent_keywords']),
                    'keyword_weights': json.dumps(updated_model['keyword_weights']),
                    'updated_at': updated_model['updated_at']
                }
                
                result = await resilient_supabase_client.update(
                    table='intent_models',
                    data=model_data,
                    filters={'id': self.intent_model['id']}
                )
                
                if result.get('data'):
                    logger.info(f"Modelo de intención actualizado con ID: {self.intent_model['id']}")
                    # Actualizar modelo local
                    self.intent_model = updated_model
                    return True
            
            logger.warning(f"No se pudo actualizar el modelo de intención para {conversation_id}")
            return False
            
        except Exception as e:
            logger.error(f"Error al actualizar modelo de intención: {e}")
            return False
