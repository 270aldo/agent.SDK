"""
Servicio de integración de capacidades avanzadas de NLP.
"""

import logging
from typing import Dict, Any, List, Optional
import json

from src.services.advanced_sentiment_service import AdvancedSentimentService
from src.services.entity_recognition_service import EntityRecognitionService
from src.services.question_classification_service import QuestionClassificationService
from src.services.contextual_intent_service import ContextualIntentService
from src.services.keyword_extraction_service import KeywordExtractionService

# Configurar logging
logger = logging.getLogger(__name__)

class NLPIntegrationService:
    """
    Servicio que integra todas las capacidades avanzadas de NLP.
    Proporciona una interfaz unificada para el análisis de texto y conversaciones.
    """
    
    def __init__(self):
        """Inicializar el servicio de integración de NLP."""
        logger.info("Servicio de integración de NLP inicializado")
        
        # Inicializar servicios individuales
        self.sentiment_service = AdvancedSentimentService()
        self.entity_service = EntityRecognitionService()
        self.question_service = QuestionClassificationService()
        self.intent_service = ContextualIntentService()
        self.keyword_service = KeywordExtractionService()
        
        # Caché de análisis para conversaciones
        self.conversation_analyses = {}
    
    def analyze_message(self, text: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Realiza un análisis completo de un mensaje individual.
        
        Args:
            text: Texto del mensaje a analizar
            conversation_id: ID opcional de la conversación
            
        Returns:
            Dict: Resultados completos del análisis
        """
        # Análisis de sentimiento
        sentiment_analysis = self.sentiment_service.get_comprehensive_analysis(text)
        
        # Reconocimiento de entidades
        entities = self.entity_service.extract_entities_from_text(text)
        
        # Análisis de preguntas
        question_analysis = self.question_service.analyze_text(text)
        
        # Análisis de intención
        intent_analysis = self.intent_service.analyze_message(text)
        
        # Extracción de palabras clave
        keyword_analysis = self.keyword_service.analyze_text(text)
        
        # Actualizar análisis de conversación si se proporciona ID
        if conversation_id:
            # Actualizar entidades
            self.entity_service.update_conversation_entities(conversation_id, text, 'user')
            
            # Actualizar intenciones
            self.intent_service.update_conversation_intents(conversation_id, text, 'user')
            
            # Actualizar palabras clave
            self.keyword_service.update_conversation_keywords(conversation_id, text, 'user')
        
        # Combinar resultados
        return {
            "sentiment": sentiment_analysis,
            "entities": entities,
            "questions": question_analysis,
            "intent": intent_analysis,
            "keywords": keyword_analysis
        }
    
    def analyze_conversation(self, messages: List[Dict[str, str]], conversation_id: str) -> Dict[str, Any]:
        """
        Realiza un análisis completo de una conversación.
        
        Args:
            messages: Lista de mensajes de la conversación
            conversation_id: ID de la conversación
            
        Returns:
            Dict: Resultados completos del análisis
        """
        # Análisis de sentimiento de la conversación
        sentiment_analysis = self.sentiment_service.analyze_conversation(messages)
        
        # Análisis de entidades de la conversación
        entities = self.entity_service.extract_entities_from_conversation(messages, conversation_id)
        entity_summary = self.entity_service.get_entity_summary(conversation_id)
        
        # Análisis de preguntas de la conversación
        question_analysis = self.question_service.analyze_conversation(messages)
        
        # Análisis de intención de la conversación
        intent_analysis = self.intent_service.analyze_conversation(messages, conversation_id)
        intent_summary = self.intent_service.get_intent_summary(conversation_id)
        
        # Análisis de palabras clave de la conversación
        keyword_analysis = self.keyword_service.analyze_conversation(messages, conversation_id)
        keyword_summary = self.keyword_service.get_keyword_summary(conversation_id)
        
        # Guardar análisis en caché
        self.conversation_analyses[conversation_id] = {
            "sentiment": sentiment_analysis,
            "entities": entity_summary,
            "questions": question_analysis,
            "intent": intent_summary,
            "keywords": keyword_summary
        }
        
        # Combinar resultados
        return {
            "sentiment": sentiment_analysis,
            "entities": {
                "extracted": entities,
                "summary": entity_summary
            },
            "questions": question_analysis,
            "intent": {
                "analysis": intent_analysis,
                "summary": intent_summary
            },
            "keywords": {
                "analysis": keyword_analysis,
                "summary": keyword_summary
            }
        }
    
    def get_conversation_analysis(self, conversation_id: str) -> Dict[str, Any]:
        """
        Obtiene el análisis almacenado para una conversación.
        
        Args:
            conversation_id: ID de la conversación
            
        Returns:
            Dict: Análisis almacenado de la conversación
        """
        return self.conversation_analyses.get(conversation_id, {})
    
    def clear_conversation_analysis(self, conversation_id: str):
        """
        Limpia el análisis almacenado para una conversación.
        
        Args:
            conversation_id: ID de la conversación
        """
        if conversation_id in self.conversation_analyses:
            del self.conversation_analyses[conversation_id]
            
        # Limpiar análisis en servicios individuales
        self.entity_service.clear_conversation_entities(conversation_id)
        self.intent_service.clear_conversation_intents(conversation_id)
        self.keyword_service.clear_conversation_keywords(conversation_id)
    
    def get_conversation_insights(self, conversation_id: str) -> Dict[str, Any]:
        """
        Genera insights útiles basados en el análisis de la conversación.
        
        Args:
            conversation_id: ID de la conversación
            
        Returns:
            Dict: Insights de la conversación
        """
        # Obtener análisis almacenado
        analysis = self.get_conversation_analysis(conversation_id)
        
        if not analysis:
            return {
                "has_insights": False,
                "message": "No hay análisis disponible para esta conversación."
            }
            
        insights = {
            "has_insights": True,
            "user_profile": self._generate_user_profile(conversation_id, analysis),
            "conversation_status": self._determine_conversation_status(analysis),
            "recommended_actions": self._generate_recommended_actions(analysis),
            "key_topics": self._extract_key_topics(analysis)
        }
        
        return insights
    
    def _generate_user_profile(self, conversation_id: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Genera un perfil de usuario basado en el análisis de la conversación.
        
        Args:
            conversation_id: ID de la conversación
            analysis: Análisis de la conversación
            
        Returns:
            Dict: Perfil del usuario
        """
        # Extraer información relevante del análisis
        entities = self.entity_service.get_conversation_entities(conversation_id)
        
        # Datos personales
        personal_info = {}
        if "nombre_persona" in entities:
            personal_info["name"] = entities["nombre_persona"][0]
        if "correo_electronico" in entities:
            personal_info["email"] = entities["correo_electronico"][0]
        if "telefono" in entities:
            personal_info["phone"] = entities["telefono"][0]
        
        # Intereses basados en palabras clave
        keywords = self.keyword_service.get_top_keywords(conversation_id, 5)
        interests = [keyword for keyword, _ in keywords]
        
        # Estilo de comunicación basado en análisis de sentimiento
        communication_style = "formal"
        if "sentiment" in analysis and "overall_sentiment" in analysis["sentiment"]:
            if analysis["sentiment"]["overall_sentiment"] == "positivo":
                if analysis["sentiment"].get("dominant_emotion", {}).get("name") == "entusiasmo":
                    communication_style = "entusiasta"
            elif analysis["sentiment"]["overall_sentiment"] == "negativo":
                if analysis["sentiment"].get("dominant_emotion", {}).get("name") == "frustración":
                    communication_style = "directo"
        
        # Nivel técnico basado en complejidad de preguntas
        technical_level = "medio"
        if "questions" in analysis and "predominant_complexity" in analysis["questions"]:
            if analysis["questions"]["predominant_complexity"] == "alta":
                technical_level = "alto"
            elif analysis["questions"]["predominant_complexity"] == "baja":
                technical_level = "bajo"
        
        return {
            "personal_info": personal_info,
            "interests": interests,
            "communication_style": communication_style,
            "technical_level": technical_level
        }
    
    def _determine_conversation_status(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determina el estado actual de la conversación.
        
        Args:
            analysis: Análisis de la conversación
            
        Returns:
            Dict: Estado de la conversación
        """
        # Estado de satisfacción
        satisfaction = "neutral"
        if "sentiment" in analysis and "sentiment_trend" in analysis["sentiment"]:
            if analysis["sentiment"]["sentiment_trend"] == "mejorando":
                satisfaction = "satisfecho"
            elif analysis["sentiment"]["sentiment_trend"] == "empeorando":
                satisfaction = "insatisfecho"
        
        # Nivel de urgencia
        urgency = "baja"
        if "sentiment" in analysis and "urgency" in analysis["sentiment"]:
            urgency = analysis["sentiment"]["urgency"]
        
        # Fase de la conversación
        conversation_phase = "exploración"
        if "intent" in analysis and "predominant_intent" in analysis["intent"]:
            intent = analysis["intent"]["predominant_intent"]
            if intent in ["transacción_compra", "transacción_pago"]:
                conversation_phase = "decisión"
            elif intent in ["soporte_técnico", "soporte_cuenta"]:
                conversation_phase = "resolución"
            elif intent in ["queja_servicio", "queja_producto"]:
                conversation_phase = "insatisfacción"
        
        # Nivel de compromiso
        engagement = "medio"
        if "questions" in analysis and "question_count" in analysis["questions"]:
            question_count = analysis["questions"]["question_count"]
            if question_count > 5:
                engagement = "alto"
            elif question_count < 2:
                engagement = "bajo"
        
        return {
            "satisfaction": satisfaction,
            "urgency": urgency,
            "conversation_phase": conversation_phase,
            "engagement": engagement
        }
    
    def _generate_recommended_actions(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Genera acciones recomendadas basadas en el análisis.
        
        Args:
            analysis: Análisis de la conversación
            
        Returns:
            List: Lista de acciones recomendadas
        """
        recommendations = []
        
        # Recomendaciones basadas en sentimiento
        if "sentiment" in analysis:
            sentiment = analysis["sentiment"].get("overall_sentiment", "neutral")
            if sentiment == "negativo":
                recommendations.append({
                    "type": "sentiment",
                    "action": "mejorar_experiencia",
                    "description": "El usuario muestra sentimiento negativo. Considerar ofrecer soluciones adicionales."
                })
        
        # Recomendaciones basadas en intención
        if "intent" in analysis and "predominant_intent" in analysis["intent"]:
            intent = analysis["intent"]["predominant_intent"]
            if intent in ["información_producto", "información_precio"]:
                recommendations.append({
                    "type": "intent",
                    "action": "proporcionar_información",
                    "description": "El usuario busca información. Proporcionar detalles relevantes y precisos."
                })
            elif intent in ["transacción_compra"]:
                recommendations.append({
                    "type": "intent",
                    "action": "facilitar_compra",
                    "description": "El usuario muestra intención de compra. Facilitar el proceso de adquisición."
                })
            elif intent in ["soporte_técnico", "soporte_cuenta"]:
                recommendations.append({
                    "type": "intent",
                    "action": "resolver_problema",
                    "description": "El usuario necesita soporte. Priorizar la resolución rápida del problema."
                })
        
        # Recomendaciones basadas en preguntas
        if "questions" in analysis and "predominant_complexity" in analysis["questions"]:
            complexity = analysis["questions"]["predominant_complexity"]
            if complexity == "alta":
                recommendations.append({
                    "type": "questions",
                    "action": "simplificar_respuestas",
                    "description": "El usuario hace preguntas complejas. Proporcionar respuestas detalladas pero claras."
                })
        
        # Recomendaciones basadas en urgencia
        if "sentiment" in analysis and "urgency" in analysis["sentiment"]:
            urgency = analysis["sentiment"]["urgency"]
            if urgency == "alta":
                recommendations.append({
                    "type": "urgency",
                    "action": "priorizar_atención",
                    "description": "El usuario muestra alta urgencia. Priorizar la atención y respuesta rápida."
                })
        
        return recommendations
    
    def _extract_key_topics(self, analysis: Dict[str, Any]) -> List[str]:
        """
        Extrae los temas clave de la conversación.
        
        Args:
            analysis: Análisis de la conversación
            
        Returns:
            List: Lista de temas clave
        """
        topics = []
        
        # Temas basados en palabras clave
        if "keywords" in analysis and "top_keywords" in analysis["keywords"]:
            topics.extend([keyword for keyword, _ in analysis["keywords"]["top_keywords"][:3]])
        
        # Temas basados en categorías dominantes
        if "keywords" in analysis and "dominant_categories" in analysis["keywords"]:
            topics.extend([category for category, _ in analysis["keywords"]["dominant_categories"][:2]])
        
        # Eliminar duplicados
        topics = list(set(topics))
        
        return topics
