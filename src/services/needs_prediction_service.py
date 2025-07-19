"""
Servicio de Predicción de Necesidades para NGX Voice Sales Agent.

Este servicio se encarga de anticipar las necesidades de los clientes
basándose en el análisis de la conversación, el perfil del usuario
y patrones históricos.
"""

from typing import Dict, List, Any, Optional, Tuple
import logging
import json
from datetime import datetime

from src.integrations.supabase.resilient_client import ResilientSupabaseClient
from src.services.predictive_model_service import PredictiveModelService
from src.services.nlp_integration_service import NLPIntegrationService
from src.services.entity_recognition_service import EntityRecognitionService
from src.services.base_predictive_service import BasePredictiveService
from src.services.utils.signal_detection import detect_sentiment_signals, detect_keyword_signals, detect_question_patterns
from src.services.utils.scoring import normalize_scores, apply_weights, calculate_confidence, rank_items
from src.services.utils.recommendations import generate_response_suggestions
from src.services.utils.data_processing import extract_features_from_conversation

logger = logging.getLogger(__name__)

class NeedsPredictionService(BasePredictiveService):
    """
    Servicio para anticipar las necesidades de los clientes.
    
    Características principales:
    - Análisis de patrones de conversación
    - Integración con perfil de usuario
    - Predicción basada en comportamientos similares
    - Recomendaciones proactivas de productos y servicios
    """
    
    def __init__(self, 
                 supabase_client: ResilientSupabaseClient,
                 predictive_model_service: PredictiveModelService,
                 nlp_integration_service: NLPIntegrationService,
                 entity_recognition_service: EntityRecognitionService):
        """
        Inicializa el servicio de predicción de necesidades.
        
        Args:
            supabase_client: Cliente de Supabase para persistencia
            predictive_model_service: Servicio base para modelos predictivos
            nlp_integration_service: Servicio de integración NLP
            entity_recognition_service: Servicio de reconocimiento de entidades
        """
        super().__init__(
            supabase=supabase_client,
            predictive_model_service=predictive_model_service,
            nlp_integration_service=nlp_integration_service,
            model_name="needs_prediction_model",
            model_type="needs"
        )
        self.entity_service = entity_recognition_service
        self._initialized = False
    
    async def initialize(self) -> None:
        """
        Inicializa el servicio de forma asíncrona.
        """
        if not self._initialized:
            await self._initialize_model()
            self._initialized = True
        
    async def _initialize_model(self) -> None:
        """
        Inicializa el modelo de predicción de necesidades.
        """
        model_params = {
            "need_categories": [
                "information", "pricing", "features", "support",
                "customization", "integration", "training", "comparison",
                "technical_details", "case_studies", "alternatives"
            ],
            "confidence_threshold": 0.6,
            "context_window": 10,  # Número de mensajes a considerar
            "feature_weights": {
                "explicit_requests": 0.5,
                "implicit_interests": 0.3,
                "question_patterns": 0.4,
                "entity_mentions": 0.35,
                "similar_profiles": 0.25
            }
        }
        
        await self.initialize_model(
            model_params=model_params,
            description="Modelo para predicción de necesidades de clientes"
        )
    
    async def predict_needs(self, conversation_id: str, 
                      messages: List[Dict[str, Any]],
                      customer_profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Predice las necesidades del cliente basándose en la conversación actual.
        
        Args:
            conversation_id: ID de la conversación
            messages: Lista de mensajes de la conversación
            customer_profile: Perfil del cliente (opcional)
            
        Returns:
            Predicciones de necesidades con niveles de confianza
        """
        try:
            await self.initialize()
            if not messages:
                return {"needs": [], "confidence": 0, "features": {}}
            
            # Obtener parámetros del modelo
            model = await self.predictive_model_service.get_model(self.model_name)
            if not model or "parameters" not in model:
                logger.error("Modelo de predicción de necesidades no encontrado")
                return {"needs": [], "confidence": 0, "features": {}}
            
            model_params = json.loads(model["parameters"])
            need_categories = model_params.get("need_categories", [])
            confidence_threshold = model_params.get("confidence_threshold", 0.6)
            context_window = model_params.get("context_window", 10)
            feature_weights = model_params.get("feature_weights", {})
            
            # Limitar a los últimos N mensajes para el análisis
            recent_messages = messages[-context_window:] if len(messages) > context_window else messages
            
            # Extraer texto de los mensajes del cliente
            client_messages = [msg["content"] for msg in recent_messages if msg.get("role") == "user"]
            
            if not client_messages:
                return {"needs": [], "confidence": 0, "features": {}}
            
            # Extraer características de la conversación
            features = await self._extract_need_features(client_messages, customer_profile)
            
            # Calcular puntuaciones para cada categoría de necesidad
            need_scores = await self._calculate_need_scores(features, need_categories, feature_weights)
            
            # Determinar las necesidades más probables
            predicted_needs = []
            for need_category, score in need_scores.items():
                if score >= confidence_threshold:
                    predicted_needs.append({
                        "category": need_category,
                        "confidence": score,
                        "suggested_actions": await self._get_suggested_actions(need_category, customer_profile)
                    })
            
            # Ordenar por nivel de confianza
            predicted_needs.sort(key=lambda x: x["confidence"], reverse=True)
            
            # Calcular confianza general
            overall_confidence = max(need_scores.values()) if need_scores else 0
            
            # Almacenar predicción
            prediction_data = {
                "need_categories": [need["category"] for need in predicted_needs],
                "features": features
            }
            
            await self.predictive_model_service.store_prediction(
                model_name=self.model_name,
                conversation_id=conversation_id,
                prediction_type="needs",
                prediction_data=prediction_data,
                confidence=overall_confidence
            )
            
            return {
                "needs": predicted_needs,
                "confidence": overall_confidence,
                "features": features
            }
            
        except Exception as e:
            logger.error(f"Error al predecir necesidades: {e}")
            return {"needs": [], "confidence": 0, "features": {}}
    
    async def _extract_need_features(self, messages: List[str],
                               customer_profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Extrae características relevantes para la predicción de necesidades.
        
        Args:
            messages: Lista de mensajes del cliente
            customer_profile: Perfil del cliente (opcional)
            
        Returns:
            Características extraídas para predicción
        """
        features = {
            "explicit_requests": {},
            "implicit_interests": {},
            "question_patterns": {},
            "entity_mentions": {},
            "similar_profiles": {}
        }
        
        try:
            # Extraer características básicas de la conversación
            base_features = extract_features_from_conversation(messages, customer_profile)
            
            # Extraer solo los mensajes del cliente
            client_messages = [msg for msg in messages if msg.get("role") == "user"]
            client_texts = [msg.get("content", "") for msg in client_messages]
            
            if not client_texts:
                return features
            
            # Detectar solicitudes explícitas
            explicit_phrases = [
                "necesito", "quiero", "busco", "me gustaría", "estoy buscando", 
                "me interesa", "podrías darme", "me puedes dar"
            ]
            
            for message in client_texts:
                for phrase in explicit_phrases:
                    if phrase in message.lower():
                        # Extraer contexto alrededor de la frase
                        start_idx = message.lower().find(phrase)
                        context = message[start_idx:start_idx + 50].strip()
                        features["explicit_requests"][context] = features["explicit_requests"].get(context, 0) + 1
            
            # Detectar patrones de preguntas usando la utilidad compartida
            question_signals = await detect_question_patterns(client_messages)
            for question_type, value in question_signals.items():
                if value > 0.2:  # Umbral para considerar la señal relevante
                    features["question_patterns"][question_type] = value
            
            # Detectar menciones de entidades
            for message in client_texts:
                entities = await self.entity_service.extract_entities(message)
                
                for entity in entities:
                    entity_type = entity.get("type")
                    entity_text = entity.get("text")
                    
                    if entity_type and entity_text:
                        key = f"{entity_type}:{entity_text}"
                        features["entity_mentions"][key] = features["entity_mentions"].get(key, 0) + 1
            
            # Analizar perfil del cliente para perfiles similares
            if customer_profile:
                # Extraer características del perfil
                if "segment" in customer_profile:
                    features["similar_profiles"]["segment"] = customer_profile["segment"]
                
                if "industry" in customer_profile:
                    features["similar_profiles"]["industry"] = customer_profile["industry"]
                
                if "company_size" in customer_profile:
                    features["similar_profiles"]["company_size"] = customer_profile["company_size"]
            
            # Integrar características básicas
            features["conversation_metrics"] = base_features.get("conversation_features", {})
            features["message_metrics"] = base_features.get("message_features", {})
            
            return features
            
        except Exception as e:
            logger.error(f"Error al extraer características para predicción de necesidades: {e}")
            return features
    
    async def _calculate_need_scores(self, features: Dict[str, Any], 
                               need_categories: List[str],
                               feature_weights: Dict[str, float]) -> Dict[str, float]:
        """
        Calcula puntuaciones para cada categoría de necesidad.
        
        Args:
            features: Características extraídas de la conversación
            need_categories: Categorías de necesidad a evaluar
            feature_weights: Pesos para diferentes tipos de características
            
        Returns:
            Diccionario con categorías de necesidad y sus puntuaciones
        """
        need_scores = {category: 0.0 for category in need_categories}
        
        # Procesar solicitudes explícitas
        explicit_requests = features.get("explicit_requests", {})
        for category, score in explicit_requests.items():
            if category in need_scores:
                need_scores[category] += score * feature_weights.get("explicit_requests", 0.5)
        
        # Procesar intereses implícitos
        implicit_interests = features.get("implicit_interests", {})
        for category, score in implicit_interests.items():
            if category in need_scores:
                need_scores[category] += score * feature_weights.get("implicit_interests", 0.3)
        
        # Procesar patrones de preguntas
        question_patterns = features.get("question_patterns", {})
        for category, score in question_patterns.items():
            if category in need_scores:
                need_scores[category] += score * feature_weights.get("question_patterns", 0.4)
        
        # Procesar menciones de entidades
        entity_mentions = features.get("entity_mentions", {})
        for category, score in entity_mentions.items():
            if category in need_scores:
                need_scores[category] += score * feature_weights.get("entity_mentions", 0.35)
        
        # Ajustar basado en perfil del cliente (si está disponible)
        customer_profile = features.get("customer_profile")
        if customer_profile:
            industry = customer_profile.get("industry")
            
            # Ajustes específicos por industria
            industry_adjustments = {
                "healthcare": {"technical_details": 0.2, "compliance": 0.3, "security": 0.3},
                "finance": {"security": 0.3, "compliance": 0.3, "technical_details": 0.2},
                "education": {"training": 0.3, "support": 0.2, "pricing": 0.2},
                "retail": {"integration": 0.2, "customization": 0.2},
                "technology": {"technical_details": 0.3, "integration": 0.3, "features": 0.2}
            }
            
            # Aplicar ajustes por industria
            if industry and industry in industry_adjustments:
                for category, adjustment in industry_adjustments[industry].items():
                    if category in need_scores:
                        need_scores[category] += adjustment * feature_weights.get("similar_profiles", 0.25)
        
        # Normalizar puntuaciones (0-1)
        max_score = max(need_scores.values()) if need_scores.values() else 1.0
        if max_score > 0:
            for category in need_scores:
                need_scores[category] /= max_score
        
        return need_scores
    
    async def _get_suggested_actions(self, need_category: str, 
                               customer_profile: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Obtiene acciones sugeridas para una categoría de necesidad.
        
        Args:
            need_category: Categoría de necesidad
            customer_profile: Perfil del cliente (opcional)
            
        Returns:
            Lista de acciones sugeridas
        """
        # Biblioteca de acciones sugeridas por categoría
        actions_by_category = {
            "information": [
                {"type": "content", "action": "Compartir folleto informativo general", "priority": "high"},
                {"type": "content", "action": "Enviar enlace a página de información detallada", "priority": "medium"},
                {"type": "conversation", "action": "Preguntar qué aspectos específicos le interesan más", "priority": "high"}
            ],
            "pricing": [
                {"type": "content", "action": "Compartir lista de precios", "priority": "high"},
                {"type": "content", "action": "Enviar comparativa de planes", "priority": "medium"},
                {"type": "conversation", "action": "Preguntar sobre presupuesto disponible", "priority": "medium"},
                {"type": "offer", "action": "Ofrecer descuento por tiempo limitado", "priority": "low"}
            ],
            "features": [
                {"type": "content", "action": "Compartir lista de características principales", "priority": "high"},
                {"type": "demo", "action": "Ofrecer demostración de producto", "priority": "high"},
                {"type": "conversation", "action": "Preguntar qué funcionalidades son más importantes", "priority": "medium"}
            ],
            "support": [
                {"type": "content", "action": "Compartir detalles de planes de soporte", "priority": "high"},
                {"type": "conversation", "action": "Preguntar sobre necesidades específicas de soporte", "priority": "medium"},
                {"type": "contact", "action": "Ofrecer contacto con equipo de soporte", "priority": "medium"}
            ],
            "customization": [
                {"type": "content", "action": "Compartir opciones de personalización", "priority": "high"},
                {"type": "conversation", "action": "Preguntar sobre requisitos específicos de personalización", "priority": "high"},
                {"type": "contact", "action": "Programar llamada con consultor de soluciones", "priority": "medium"}
            ],
            "integration": [
                {"type": "content", "action": "Compartir lista de integraciones disponibles", "priority": "high"},
                {"type": "conversation", "action": "Preguntar sobre sistemas actuales", "priority": "high"},
                {"type": "content", "action": "Enviar documentación técnica de APIs", "priority": "medium"}
            ],
            "training": [
                {"type": "content", "action": "Compartir opciones de capacitación", "priority": "high"},
                {"type": "content", "action": "Enviar enlace a recursos de aprendizaje", "priority": "medium"},
                {"type": "conversation", "action": "Preguntar sobre necesidades específicas de formación", "priority": "medium"}
            ],
            "comparison": [
                {"type": "content", "action": "Compartir tabla comparativa con competidores", "priority": "high"},
                {"type": "conversation", "action": "Preguntar qué otras soluciones está considerando", "priority": "high"},
                {"type": "content", "action": "Destacar ventajas competitivas", "priority": "medium"}
            ],
            "technical_details": [
                {"type": "content", "action": "Compartir especificaciones técnicas", "priority": "high"},
                {"type": "contact", "action": "Ofrecer consulta con especialista técnico", "priority": "medium"},
                {"type": "content", "action": "Enviar documentación de arquitectura", "priority": "medium"}
            ],
            "case_studies": [
                {"type": "content", "action": "Compartir casos de éxito relevantes", "priority": "high"},
                {"type": "content", "action": "Enviar testimonios de clientes", "priority": "medium"},
                {"type": "conversation", "action": "Ofrecer referencias de clientes similares", "priority": "medium"}
            ],
            "alternatives": [
                {"type": "conversation", "action": "Preguntar qué está buscando en una solución", "priority": "high"},
                {"type": "content", "action": "Presentar diferentes opciones de producto", "priority": "high"},
                {"type": "content", "action": "Compartir comparativa de planes/versiones", "priority": "medium"}
            ]
        }
        
        # Obtener acciones base para la categoría
        suggested_actions = actions_by_category.get(need_category, [])
        
        # Personalizar acciones según el perfil del cliente (si está disponible)
        if customer_profile:
            industry = customer_profile.get("industry")
            company_size = customer_profile.get("company_size")
            
            # Ajustes específicos por industria
            if industry:
                industry_specific_actions = {
                    "healthcare": [
                        {"type": "content", "action": f"Compartir caso de éxito en sector salud", "priority": "high"},
                        {"type": "content", "action": f"Enviar información sobre cumplimiento normativo en salud", "priority": "high"}
                    ],
                    "finance": [
                        {"type": "content", "action": f"Compartir caso de éxito en sector financiero", "priority": "high"},
                        {"type": "content", "action": f"Enviar información sobre seguridad y cumplimiento", "priority": "high"}
                    ],
                    "education": [
                        {"type": "content", "action": f"Compartir caso de éxito en sector educativo", "priority": "high"},
                        {"type": "content", "action": f"Enviar información sobre planes para instituciones educativas", "priority": "high"}
                    ],
                    "retail": [
                        {"type": "content", "action": f"Compartir caso de éxito en retail", "priority": "high"},
                        {"type": "content", "action": f"Enviar información sobre integración con sistemas de punto de venta", "priority": "high"}
                    ],
                    "technology": [
                        {"type": "content", "action": f"Compartir documentación técnica avanzada", "priority": "high"},
                        {"type": "content", "action": f"Enviar información sobre APIs y extensibilidad", "priority": "high"}
                    ]
                }
                
                if industry in industry_specific_actions:
                    suggested_actions.extend(industry_specific_actions[industry])
            
            # Ajustes por tamaño de empresa
            if company_size:
                size_specific_actions = {
                    "small": [
                        {"type": "content", "action": "Compartir planes para pequeñas empresas", "priority": "high"},
                        {"type": "offer", "action": "Ofrecer paquete inicial con descuento", "priority": "medium"}
                    ],
                    "medium": [
                        {"type": "content", "action": "Compartir planes para empresas medianas", "priority": "high"},
                        {"type": "contact", "action": "Ofrecer consultoría de implementación", "priority": "medium"}
                    ],
                    "large": [
                        {"type": "content", "action": "Compartir planes empresariales", "priority": "high"},
                        {"type": "contact", "action": "Ofrecer gestor de cuenta dedicado", "priority": "high"}
                    ]
                }
                
                if company_size in size_specific_actions:
                    suggested_actions.extend(size_specific_actions[company_size])
        
        # Ordenar por prioridad
        priority_values = {"high": 3, "medium": 2, "low": 1}
        suggested_actions.sort(key=lambda x: priority_values.get(x.get("priority"), 0), reverse=True)
        
        return suggested_actions
    
    async def record_actual_need(self, conversation_id: str, 
                           need_category: str,
                           need_description: str) -> Dict[str, Any]:
        """
        Registra una necesidad real para mejorar el modelo.
        
        Args:
            conversation_id: ID de la conversación
            need_category: Categoría de necesidad detectada
            need_description: Descripción de la necesidad
            
        Returns:
            Resultado del registro
        """
        try:
            # Registrar el resultado real
            actual_result = {
                "need_category": need_category,
                "need_description": need_description,
                "timestamp": datetime.now().isoformat()
            }
            
            result = await self.record_actual_result(
                conversation_id=conversation_id,
                actual_result=actual_result,
                was_correct=None  # Se determinará automáticamente en record_actual_result
            )
            
            # Añadir datos para entrenamiento futuro
            features = {
                "need_description": need_description,
                "conversation_id": conversation_id
            }
            
            await self.add_training_data(
                features=features,
                label=need_category
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error al registrar necesidad real: {e}")
            return {}
    
    async def get_needs_statistics(self, time_period: Optional[int] = None) -> Dict[str, Any]:
        """
        Obtiene estadísticas sobre necesidades detectadas.
        
        Args:
            time_period: Período de tiempo en días (opcional)
            
        Returns:
            Estadísticas de necesidades
        """
        try:
            # Obtener estadísticas básicas
            basic_stats = await self.get_statistics(time_period)
            
            # Obtener distribución de categorías de necesidades
            query = self.supabase.table("prediction_results").select("*").eq("model_name", self.model_name).eq("status", "completed").execute()
            
            if not query.data:
                return {
                    **basic_stats,
                    "needs_distribution": {},
                    "total_needs": 0
                }
            
            # Contar categorías de necesidades
            needs_counts = {}
            for prediction in query.data:
                actual_result = json.loads(prediction["result"]) if prediction["result"] else {}
                need_category = actual_result.get("need_category")
                
                if need_category:
                    needs_counts[need_category] = needs_counts.get(need_category, 0) + 1
            
            total_needs = sum(needs_counts.values())
            
            # Calcular distribución porcentual
            needs_distribution = {}
            for need_category, count in needs_counts.items():
                needs_distribution[need_category] = count / total_needs if total_needs > 0 else 0
            
            return {
                **basic_stats,
                "needs_distribution": needs_distribution,
                "total_needs": total_needs
            }
            
        except Exception as e:
            logger.error(f"Error al obtener estadísticas de necesidades: {e}")
            return {
                "accuracy": {"accuracy": 0, "total_predictions": 0},
                "needs_distribution": {},
                "total_needs": 0
            }
