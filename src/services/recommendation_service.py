"""
Servicio de recomendaciones basado en el análisis de NLP.
"""

import logging
from typing import Dict, Any, List, Optional
import json

from src.services.nlp_integration_service import NLPIntegrationService
from src.services.entity_recognition_service import EntityRecognitionService
from src.services.contextual_intent_service import ContextualIntentService
from src.services.keyword_extraction_service import KeywordExtractionService

# Configurar logging
logger = logging.getLogger(__name__)

class RecommendationService:
    """
    Servicio que genera recomendaciones personalizadas basadas en el análisis de NLP.
    Utiliza entidades, intenciones y palabras clave para proporcionar recomendaciones relevantes.
    """
    
    def __init__(self):
        """Inicializar el servicio de recomendaciones."""
        logger.info("Servicio de recomendaciones inicializado")
        
        # Inicializar servicios de NLP
        self.nlp_service = NLPIntegrationService()
        self.entity_service = EntityRecognitionService()
        self.intent_service = ContextualIntentService()
        self.keyword_service = KeywordExtractionService()
        
        # Caché de recomendaciones
        self.recommendations_cache = {}
    
    def generate_recommendations(self, conversation_id: str) -> Dict[str, Any]:
        """
        Genera recomendaciones personalizadas basadas en el análisis de la conversación.
        
        Args:
            conversation_id: ID de la conversación
            
        Returns:
            Dict: Recomendaciones generadas
        """
        # Obtener insights de NLP
        conversation_insights = self.nlp_service.get_conversation_insights(conversation_id)
        
        if not conversation_insights.get("has_insights", False):
            return {
                "has_recommendations": False,
                "message": "No hay suficiente información para generar recomendaciones."
            }
        
        # Obtener entidades, intenciones y palabras clave
        entities = self.entity_service.get_conversation_entities(conversation_id)
        intents = self.intent_service.get_conversation_intents(conversation_id)
        keywords = self.keyword_service.get_top_keywords(conversation_id, 10)
        
        # Generar recomendaciones basadas en diferentes criterios
        product_recommendations = self._generate_product_recommendations(entities, intents, keywords)
        content_recommendations = self._generate_content_recommendations(entities, intents, keywords)
        next_action_recommendations = self._generate_next_action_recommendations(conversation_insights)
        
        # Combinar todas las recomendaciones
        recommendations = {
            "has_recommendations": True,
            "products": product_recommendations,
            "content": content_recommendations,
            "next_actions": next_action_recommendations,
            "personalized_message": self._generate_personalized_message(conversation_insights)
        }
        
        # Guardar en caché
        self.recommendations_cache[conversation_id] = recommendations
        
        return recommendations
    
    def get_cached_recommendations(self, conversation_id: str) -> Dict[str, Any]:
        """
        Obtiene las recomendaciones almacenadas en caché para una conversación.
        
        Args:
            conversation_id: ID de la conversación
            
        Returns:
            Dict: Recomendaciones almacenadas
        """
        return self.recommendations_cache.get(conversation_id, {
            "has_recommendations": False,
            "message": "No hay recomendaciones en caché para esta conversación."
        })
    
    def clear_recommendations(self, conversation_id: str):
        """
        Limpia las recomendaciones almacenadas para una conversación.
        
        Args:
            conversation_id: ID de la conversación
        """
        if conversation_id in self.recommendations_cache:
            del self.recommendations_cache[conversation_id]
    
    def _generate_product_recommendations(self, entities: Dict[str, List[str]], 
                                         intents: Dict[str, float], 
                                         keywords: List[tuple]) -> List[Dict[str, Any]]:
        """
        Genera recomendaciones de productos basadas en entidades, intenciones y palabras clave.
        
        Args:
            entities: Entidades detectadas en la conversación
            intents: Intenciones detectadas en la conversación
            keywords: Palabras clave detectadas en la conversación
            
        Returns:
            List: Lista de recomendaciones de productos
        """
        recommendations = []
        
        # Productos de ejemplo (en una implementación real, estos vendrían de una base de datos)
        products = [
            {
                "id": "prod001",
                "name": "NGX Prime Membership",
                "description": "Membresía premium con acceso a todas las funcionalidades",
                "price": 99.99,
                "tags": ["premium", "membership", "complete"]
            },
            {
                "id": "prod002",
                "name": "NGX Longevity Basic",
                "description": "Plan básico de longevidad con seguimiento mensual",
                "price": 49.99,
                "tags": ["basic", "longevity", "monthly"]
            },
            {
                "id": "prod003",
                "name": "NGX Health Assessment",
                "description": "Evaluación completa de salud con recomendaciones personalizadas",
                "price": 149.99,
                "tags": ["health", "assessment", "personalized"]
            },
            {
                "id": "prod004",
                "name": "NGX Nutrition Plan",
                "description": "Plan nutricional personalizado basado en tu perfil genético",
                "price": 79.99,
                "tags": ["nutrition", "diet", "personalized"]
            },
            {
                "id": "prod005",
                "name": "NGX Fitness Program",
                "description": "Programa de ejercicios adaptado a tu perfil genético",
                "price": 69.99,
                "tags": ["fitness", "exercise", "personalized"]
            }
        ]
        
        # Extraer palabras clave relevantes
        keyword_terms = [k for k, _ in keywords]
        
        # Extraer productos mencionados
        mentioned_products = entities.get("producto", [])
        
        # Determinar intereses basados en intenciones
        interests = []
        for intent, score in intents.items():
            if score > 0.6:
                if "salud" in intent:
                    interests.append("health")
                if "nutricion" in intent or "dieta" in intent:
                    interests.append("nutrition")
                if "ejercicio" in intent or "fitness" in intent:
                    interests.append("fitness")
                if "premium" in intent or "completo" in intent:
                    interests.append("premium")
        
        # Puntuar productos basados en relevancia
        scored_products = []
        for product in products:
            score = 0
            
            # Aumentar puntuación si el producto fue mencionado
            if product["name"] in mentioned_products:
                score += 3
            
            # Aumentar puntuación basada en palabras clave
            for keyword in keyword_terms:
                if keyword.lower() in product["name"].lower() or keyword.lower() in product["description"].lower():
                    score += 1
                for tag in product["tags"]:
                    if keyword.lower() in tag:
                        score += 0.5
            
            # Aumentar puntuación basada en intereses
            for interest in interests:
                if interest in product["tags"]:
                    score += 2
            
            if score > 0:
                scored_products.append((product, score))
        
        # Ordenar productos por puntuación
        scored_products.sort(key=lambda x: x[1], reverse=True)
        
        # Tomar los 3 productos más relevantes
        for product, score in scored_products[:3]:
            recommendations.append({
                "id": product["id"],
                "name": product["name"],
                "description": product["description"],
                "price": product["price"],
                "relevance_score": score,
                "reason": self._generate_recommendation_reason(product, keyword_terms, interests)
            })
        
        return recommendations
    
    def _generate_content_recommendations(self, entities: Dict[str, List[str]], 
                                         intents: Dict[str, float], 
                                         keywords: List[tuple]) -> List[Dict[str, Any]]:
        """
        Genera recomendaciones de contenido basadas en entidades, intenciones y palabras clave.
        
        Args:
            entities: Entidades detectadas en la conversación
            intents: Intenciones detectadas en la conversación
            keywords: Palabras clave detectadas en la conversación
            
        Returns:
            List: Lista de recomendaciones de contenido
        """
        recommendations = []
        
        # Contenido de ejemplo (en una implementación real, estos vendrían de una base de datos)
        content = [
            {
                "id": "cont001",
                "title": "Guía de Nutrición Personalizada",
                "type": "guide",
                "url": "/content/nutrition-guide",
                "tags": ["nutrition", "diet", "health"]
            },
            {
                "id": "cont002",
                "title": "Entendiendo tu Perfil Genético",
                "type": "article",
                "url": "/content/genetic-profile",
                "tags": ["genetics", "health", "personalized"]
            },
            {
                "id": "cont003",
                "title": "Ejercicios para Optimizar tu Salud",
                "type": "video",
                "url": "/content/exercise-health",
                "tags": ["fitness", "exercise", "health"]
            },
            {
                "id": "cont004",
                "title": "Beneficios de la Membresía Premium",
                "type": "brochure",
                "url": "/content/premium-benefits",
                "tags": ["premium", "membership", "benefits"]
            },
            {
                "id": "cont005",
                "title": "Testimonios de Clientes",
                "type": "testimonials",
                "url": "/content/testimonials",
                "tags": ["success", "stories", "results"]
            }
        ]
        
        # Extraer palabras clave relevantes
        keyword_terms = [k for k, _ in keywords]
        
        # Determinar intereses basados en intenciones
        interests = []
        for intent, score in intents.items():
            if score > 0.6:
                if "informacion" in intent:
                    interests.append("information")
                if "educacion" in intent:
                    interests.append("education")
                if "testimonios" in intent:
                    interests.append("testimonials")
        
        # Puntuar contenido basado en relevancia
        scored_content = []
        for item in content:
            score = 0
            
            # Aumentar puntuación basada en palabras clave
            for keyword in keyword_terms:
                if keyword.lower() in item["title"].lower():
                    score += 1
                for tag in item["tags"]:
                    if keyword.lower() in tag:
                        score += 0.5
            
            # Aumentar puntuación basada en intereses
            for interest in interests:
                if interest in item["tags"]:
                    score += 2
            
            if score > 0:
                scored_content.append((item, score))
        
        # Ordenar contenido por puntuación
        scored_content.sort(key=lambda x: x[1], reverse=True)
        
        # Tomar los 3 contenidos más relevantes
        for item, score in scored_content[:3]:
            recommendations.append({
                "id": item["id"],
                "title": item["title"],
                "type": item["type"],
                "url": item["url"],
                "relevance_score": score,
                "reason": self._generate_content_reason(item, keyword_terms, interests)
            })
        
        return recommendations
    
    def _generate_next_action_recommendations(self, insights: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Genera recomendaciones de próximas acciones basadas en los insights de la conversación.
        
        Args:
            insights: Insights de la conversación
            
        Returns:
            List: Lista de recomendaciones de próximas acciones
        """
        recommendations = []
        
        # Verificar si hay insights disponibles
        if not insights.get("has_insights", False):
            return recommendations
        
        # Obtener estado de la conversación
        conversation_status = insights.get("conversation_status", {})
        user_profile = insights.get("user_profile", {})
        
        # Determinar fase de la conversación
        phase = conversation_status.get("conversation_phase", "exploración")
        
        # Determinar nivel de satisfacción
        satisfaction = conversation_status.get("satisfaction", "neutral")
        
        # Determinar nivel de urgencia
        urgency = conversation_status.get("urgency", "baja")
        
        # Generar recomendaciones basadas en la fase de la conversación
        if phase == "exploración":
            recommendations.append({
                "action": "proporcionar_información",
                "description": "Proporcionar información detallada sobre los productos y servicios",
                "priority": "media",
                "reason": "El usuario está en fase de exploración y necesita más información"
            })
            recommendations.append({
                "action": "ofrecer_demo",
                "description": "Ofrecer una demostración gratuita del servicio",
                "priority": "media",
                "reason": "Una demostración puede ayudar al usuario a entender mejor el valor del servicio"
            })
        
        elif phase == "decisión":
            recommendations.append({
                "action": "ofrecer_descuento",
                "description": "Ofrecer un descuento por tiempo limitado",
                "priority": "alta",
                "reason": "El usuario está considerando la compra y un incentivo puede ayudar a cerrar la venta"
            })
            recommendations.append({
                "action": "programar_llamada",
                "description": "Programar una llamada con un asesor especializado",
                "priority": "alta",
                "reason": "El usuario está cerca de tomar una decisión y necesita resolver dudas finales"
            })
        
        elif phase == "resolución":
            recommendations.append({
                "action": "resolver_problema",
                "description": "Resolver el problema técnico o de servicio",
                "priority": "alta",
                "reason": "El usuario tiene un problema que necesita ser resuelto"
            })
            recommendations.append({
                "action": "ofrecer_compensación",
                "description": "Ofrecer una compensación por las molestias",
                "priority": "media",
                "reason": "Una compensación puede ayudar a mejorar la satisfacción del usuario"
            })
        
        elif phase == "insatisfacción":
            recommendations.append({
                "action": "escalar_caso",
                "description": "Escalar el caso a un supervisor",
                "priority": "alta",
                "reason": "El usuario está insatisfecho y necesita atención especial"
            })
            recommendations.append({
                "action": "ofrecer_solución_alternativa",
                "description": "Ofrecer una solución alternativa al problema",
                "priority": "alta",
                "reason": "Es importante mostrar flexibilidad y voluntad de resolver el problema"
            })
        
        # Ajustar prioridad basada en urgencia
        if urgency == "alta":
            for rec in recommendations:
                rec["priority"] = "alta"
                rec["reason"] += " con alta urgencia"
        
        # Añadir recomendación basada en satisfacción
        if satisfaction == "insatisfecho":
            recommendations.append({
                "action": "mejorar_experiencia",
                "description": "Tomar medidas para mejorar la experiencia del usuario",
                "priority": "alta",
                "reason": "El usuario muestra signos de insatisfacción que deben ser atendidos"
            })
        
        return recommendations
    
    def _generate_recommendation_reason(self, product: Dict[str, Any], 
                                       keywords: List[str], 
                                       interests: List[str]) -> str:
        """
        Genera una razón personalizada para la recomendación de un producto.
        
        Args:
            product: Información del producto
            keywords: Palabras clave detectadas
            interests: Intereses detectados
            
        Returns:
            str: Razón personalizada
        """
        reasons = []
        
        # Razones basadas en palabras clave
        keyword_matches = []
        for keyword in keywords:
            if keyword.lower() in product["name"].lower() or keyword.lower() in product["description"].lower():
                keyword_matches.append(keyword)
            for tag in product["tags"]:
                if keyword.lower() in tag:
                    keyword_matches.append(keyword)
        
        if keyword_matches:
            unique_matches = list(set(keyword_matches))
            if len(unique_matches) > 1:
                reasons.append(f"Contiene términos relevantes como {', '.join(unique_matches[:2])}")
            else:
                reasons.append(f"Contiene el término relevante {unique_matches[0]}")
        
        # Razones basadas en intereses
        interest_matches = []
        for interest in interests:
            if interest in product["tags"]:
                interest_matches.append(interest)
        
        if interest_matches:
            interest_map = {
                "health": "salud",
                "nutrition": "nutrición",
                "fitness": "fitness",
                "premium": "servicios premium"
            }
            
            translated_interests = [interest_map.get(interest, interest) for interest in interest_matches]
            unique_interests = list(set(translated_interests))
            
            if len(unique_interests) > 1:
                reasons.append(f"Se alinea con tu interés en {' y '.join(unique_interests)}")
            else:
                reasons.append(f"Se alinea con tu interés en {unique_interests[0]}")
        
        # Razón predeterminada
        if not reasons:
            reasons.append("Este producto podría ser de tu interés basado en la conversación")
        
        return " y ".join(reasons) + "."
    
    def _generate_content_reason(self, content: Dict[str, Any], 
                                keywords: List[str], 
                                interests: List[str]) -> str:
        """
        Genera una razón personalizada para la recomendación de contenido.
        
        Args:
            content: Información del contenido
            keywords: Palabras clave detectadas
            interests: Intereses detectados
            
        Returns:
            str: Razón personalizada
        """
        reasons = []
        
        # Razones basadas en palabras clave
        keyword_matches = []
        for keyword in keywords:
            if keyword.lower() in content["title"].lower():
                keyword_matches.append(keyword)
            for tag in content["tags"]:
                if keyword.lower() in tag:
                    keyword_matches.append(keyword)
        
        if keyword_matches:
            unique_matches = list(set(keyword_matches))
            if len(unique_matches) > 1:
                reasons.append(f"Contiene información sobre {' y '.join(unique_matches[:2])}")
            else:
                reasons.append(f"Contiene información sobre {unique_matches[0]}")
        
        # Razones basadas en intereses
        interest_matches = []
        for interest in interests:
            if interest in content["tags"]:
                interest_matches.append(interest)
        
        if interest_matches:
            interest_map = {
                "information": "información detallada",
                "education": "contenido educativo",
                "testimonials": "testimonios de otros usuarios"
            }
            
            translated_interests = [interest_map.get(interest, interest) for interest in interest_matches]
            unique_interests = list(set(translated_interests))
            
            if len(unique_interests) > 1:
                reasons.append(f"Proporciona {' y '.join(unique_interests)}")
            else:
                reasons.append(f"Proporciona {unique_interests[0]}")
        
        # Tipo de contenido
        content_type_map = {
            "guide": "una guía completa",
            "article": "un artículo informativo",
            "video": "un video explicativo",
            "brochure": "un folleto detallado",
            "testimonials": "testimonios de usuarios"
        }
        
        content_type = content_type_map.get(content["type"], content["type"])
        reasons.append(f"Es {content_type}")
        
        return " y ".join(reasons) + "."
    
    def _generate_personalized_message(self, insights: Dict[str, Any]) -> str:
        """
        Genera un mensaje personalizado basado en los insights de la conversación.
        
        Args:
            insights: Insights de la conversación
            
        Returns:
            str: Mensaje personalizado
        """
        # Verificar si hay insights disponibles
        if not insights.get("has_insights", False):
            return "Gracias por tu interés en nuestros productos y servicios."
        
        # Obtener perfil de usuario
        user_profile = insights.get("user_profile", {})
        
        # Obtener nombre del usuario
        name = "estimado cliente"
        if user_profile.get("personal_info", {}).get("name"):
            name = user_profile["personal_info"]["name"]
        
        # Obtener estado de la conversación
        conversation_status = insights.get("conversation_status", {})
        
        # Determinar fase de la conversación
        phase = conversation_status.get("conversation_phase", "exploración")
        
        # Generar mensaje personalizado
        if phase == "exploración":
            return f"Hola {name}, basado en nuestra conversación, hemos seleccionado algunos productos y recursos que podrían ayudarte a conocer mejor nuestros servicios."
        
        elif phase == "decisión":
            return f"Hola {name}, vemos que estás considerando nuestros servicios. Hemos preparado algunas recomendaciones especiales para ti que podrían ayudarte a tomar la mejor decisión."
        
        elif phase == "resolución":
            return f"Hola {name}, entendemos que estás buscando soluciones. Hemos preparado algunas recomendaciones que podrían ayudarte a resolver tus dudas o problemas."
        
        elif phase == "insatisfacción":
            return f"Hola {name}, lamentamos que hayas tenido una experiencia menos que ideal. Queremos ayudarte a mejorar tu experiencia con estas recomendaciones personalizadas."
        
        return f"Hola {name}, gracias por tu interés en nuestros productos y servicios. Hemos preparado algunas recomendaciones personalizadas para ti."
