"""
Servicio de Predicción de Conversión para NGX Voice Sales Agent.

Este servicio se encarga de predecir la probabilidad de conversión de un cliente
basándose en el análisis de señales de compra, comportamiento durante la conversación
y patrones históricos de conversión.
"""

from typing import Dict, List, Any, Optional, Tuple
import logging
import json
from datetime import datetime

from src.integrations.supabase.resilient_client import ResilientSupabaseClient
from src.services.predictive_model_service import PredictiveModelService
from src.services.nlp_integration_service import NLPIntegrationService
from src.services.base_predictive_service import BasePredictiveService
from src.services.utils.signal_detection import detect_sentiment_signals, detect_keyword_signals, detect_question_patterns, detect_engagement_signals
from src.services.utils.scoring import normalize_scores, apply_weights, calculate_confidence, rank_items
from src.services.utils.recommendations import generate_response_suggestions, generate_next_best_action
from src.services.utils.data_processing import extract_features_from_conversation

logger = logging.getLogger(__name__)

class ConversionPredictionService(BasePredictiveService):
    """
    Servicio para predecir la probabilidad de conversión de un cliente.
    
    Características principales:
    - Análisis de señales de compra
    - Modelo de scoring de probabilidad
    - Sistema de umbrales para acciones
    - Recomendaciones para aumentar conversión
    """
    
    def __init__(self, 
                 supabase_client: ResilientSupabaseClient,
                 predictive_model_service: PredictiveModelService,
                 nlp_integration_service: NLPIntegrationService):
        """
        Inicializa el servicio de predicción de conversión.
        
        Args:
            supabase_client: Cliente de Supabase para persistencia
            predictive_model_service: Servicio base para modelos predictivos
            nlp_integration_service: Servicio de integración NLP
        """
        super().__init__(
            supabase=supabase_client,
            predictive_model_service=predictive_model_service,
            nlp_integration_service=nlp_integration_service,
            model_name="conversion_prediction_model",
            model_type="conversion"
        )
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
        Inicializa el modelo de predicción de conversión.
        """
        model_params = {
            "conversion_thresholds": {
                "low": 0.3,
                "medium": 0.6,
                "high": 0.8
            },
            "confidence_threshold": 0.65,
            "context_window": 10,  # Número de mensajes a considerar
            "signal_weights": {
                "buying_signals": 0.4,
                "engagement_level": 0.3,
                "question_frequency": 0.2,
                "positive_sentiment": 0.25,
                "specific_inquiries": 0.35,
                "time_investment": 0.15
            }
        }
        
        await self.initialize_model(
            model_params=model_params,
            description="Modelo para predicción de probabilidad de conversión"
        )
    
    async def predict_conversion(self, conversation_id: str, 
                           messages: List[Dict[str, Any]],
                           customer_profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Predice la probabilidad de conversión basada en la conversación actual.
        
        Args:
            conversation_id: ID de la conversación
            messages: Lista de mensajes de la conversación
            customer_profile: Perfil del cliente (opcional)
            
        Returns:
            Predicción de probabilidad de conversión con recomendaciones
        """
        try:
            await self.initialize()
            if not messages:
                return {
                    "probability": 0, 
                    "confidence": 0, 
                    "category": "low",
                    "signals": {},
                    "recommendations": []
                }
            
            # Filtrar mensajes del cliente
            client_messages = [msg for msg in messages if msg.get("role") == "customer"]
            
            # Obtener parámetros del modelo
            model_params = await self.get_model_parameters()
            signal_weights = model_params.get("signal_weights", {})
            thresholds = model_params.get("conversion_thresholds", {"low": 0.3, "medium": 0.6, "high": 0.8})
            
            # Detectar señales de conversión
            signals = await self._detect_conversion_signals(
                client_messages=client_messages,
                all_messages=messages,
                signal_weights=signal_weights
            )
            
            # Calcular probabilidad de conversión
            probability, confidence = await self._calculate_conversion_probability(
                signals=signals,
                customer_profile=customer_profile
            )
            
            # Determinar categoría de conversión
            category = await self._get_conversion_category(
                probability=probability,
                thresholds=thresholds
            )
            
            # Obtener recomendaciones
            recommendations = await self._get_conversion_recommendations(
                conversion_category=category,
                signals=signals,
                customer_profile=customer_profile
            )
            
            # Crear resultado de predicción
            prediction_result = {
                "probability": probability,
                "confidence": confidence,
                "category": category,
                "signals": signals,
                "recommendations": recommendations,
                "timestamp": datetime.now().isoformat()
            }
            
            # Guardar predicción en base de datos
            await self.store_prediction(
                conversation_id=conversation_id,
                prediction_data=prediction_result
            )
            
            return prediction_result
            
        except Exception as e:
            logger.error(f"Error al predecir conversión: {e}")
            return {
                "probability": 0, 
                "confidence": 0, 
                "category": "low",
                "signals": {},
                "recommendations": [],
                "error": str(e)
            }
    
    async def _detect_conversion_signals(self, client_messages: List[Dict[str, Any]], 
                                   all_messages: List[Dict[str, Any]],
                                   signal_weights: Dict[str, float]) -> Dict[str, float]:
        """
        Detecta señales de conversión en los mensajes.
        
        Args:
            client_messages: Lista de mensajes del cliente
            all_messages: Lista de todos los mensajes (cliente y agente)
            signal_weights: Pesos para cada tipo de señal
            
        Returns:
            Diccionario con señales detectadas y sus valores normalizados
        """
        try:
            # Extraer texto de los mensajes
            client_texts = [msg.get("content", "") for msg in client_messages]
            all_texts = [msg.get("content", "") for msg in all_messages]
            
            # Detectar señales de compra (palabras clave relacionadas con intención de compra)
            buying_signals = await detect_keyword_signals(
                texts=client_texts,
                keywords=["comprar", "adquirir", "precio", "costo", "oferta", "descuento", "promoción", "pagar", "tarjeta", "factura"],
                nlp_service=self.nlp_integration_service
            )
            
            # Detectar nivel de engagement (frecuencia de respuestas, longitud, tiempo)
            engagement_level = await detect_engagement_signals(
                messages=all_messages,
                client_role="customer"
            )
            
            # Detectar frecuencia de preguntas (indica interés)
            question_frequency = await detect_question_patterns(
                texts=client_texts
            )
            
            # Detectar sentimiento positivo
            sentiment_signals = await detect_sentiment_signals(
                texts=client_texts,
                nlp_service=self.nlp_integration_service
            )
            positive_sentiment = sentiment_signals.get("positive", 0)
            
            # Detectar consultas específicas (detalles técnicos, especificaciones)
            specific_inquiries = await detect_keyword_signals(
                texts=client_texts,
                keywords=["especificación", "detalle", "característica", "funciona", "comparar", "diferencia", "ventaja"],
                nlp_service=self.nlp_integration_service
            )
            
            # Detectar inversión de tiempo (duración de la conversación)
            time_investment = min(1.0, len(all_messages) / 20)  # Normalizado a máximo 1.0
            
            # Recopilar todas las señales
            signals = {
                "buying_signals": buying_signals,
                "engagement_level": engagement_level,
                "question_frequency": question_frequency,
                "positive_sentiment": positive_sentiment,
                "specific_inquiries": specific_inquiries,
                "time_investment": time_investment
            }
            
            # Normalizar señales
            normalized_signals = normalize_scores(signals)
            
            # Aplicar pesos según importancia de cada señal
            weighted_signals = apply_weights(normalized_signals, signal_weights)
            
            return weighted_signals
            
        except Exception as e:
            logger.error(f"Error al detectar señales de conversión: {e}")
            return {
                "buying_signals": 0,
                "engagement_level": 0,
                "question_frequency": 0,
                "positive_sentiment": 0,
                "specific_inquiries": 0,
                "time_investment": 0
            }
    
    async def _calculate_conversion_probability(self, signals: Dict[str, float],
                                          customer_profile: Optional[Dict[str, Any]] = None) -> Tuple[float, float]:
        """
        Calcula la probabilidad de conversión basada en señales detectadas.
        
        Args:
            signals: Señales detectadas en la conversación
            customer_profile: Perfil del cliente (opcional)
            
        Returns:
            Tupla con probabilidad de conversión y nivel de confianza
        """
        try:
            # Base de cálculo: promedio ponderado de señales
            base_probability = sum(signals.values()) / max(1, len(signals))
            
            # Ajustes basados en perfil del cliente (si está disponible)
            profile_adjustment = 0
            
            if customer_profile:
                # Ajuste por historial de compras previas
                previous_purchases = customer_profile.get("previous_purchases", [])
                if previous_purchases:
                    profile_adjustment += 0.1  # Clientes existentes tienen mayor probabilidad
                
                # Ajuste por segmento del cliente
                segment = customer_profile.get("segment")
                if segment == "premium":
                    profile_adjustment += 0.05
                elif segment == "price_sensitive":
                    profile_adjustment -= 0.05
                
                # Ajuste por interacciones previas
                previous_interactions = customer_profile.get("previous_interactions", 0)
                if previous_interactions > 5:
                    profile_adjustment += 0.05
            
            # Calcular probabilidad final (limitada entre 0 y 1)
            probability = max(0, min(1, base_probability + profile_adjustment))
            
            # Calcular nivel de confianza
            # Más señales con valores consistentes = mayor confianza
            confidence = calculate_confidence(signals)
            
            return probability, confidence
            
        except Exception as e:
            logger.error(f"Error al calcular probabilidad de conversión: {e}")
            return 0, 0
    
    async def _get_conversion_category(self, probability: float, thresholds: Dict[str, float]) -> str:
        """
        Determina la categoría de conversión basada en la probabilidad.
        
        Args:
            probability: Probabilidad de conversión (0-1)
            thresholds: Umbrales para categorías
            
        Returns:
            Categoría de conversión (low, medium, high)
        """
        if probability >= thresholds.get("high", 0.8):
            return "high"
        elif probability >= thresholds.get("medium", 0.6):
            return "medium"
        else:
            return "low"
    
    async def _get_conversion_recommendations(self, conversion_category: str,
                                        signals: Dict[str, float],
                                        customer_profile: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Obtiene recomendaciones para aumentar la probabilidad de conversión.
        
        Args:
            conversion_category: Categoría de conversión (low, medium, high)
            signals: Señales detectadas en la conversación
            customer_profile: Perfil del cliente (opcional)
            
        Returns:
            Lista de recomendaciones con acciones sugeridas
        """
        try:
            # Definir plantillas de recomendaciones por categoría
            recommendation_templates = {
                "low": [
                    {
                        "action": "identify_needs",
                        "description": "Identificar necesidades específicas del cliente",
                        "priority": "high"
                    },
                    {
                        "action": "provide_information",
                        "description": "Proporcionar información relevante sobre el producto/servicio",
                        "priority": "high"
                    },
                    {
                        "action": "build_rapport",
                        "description": "Establecer una conexión personal con el cliente",
                        "priority": "medium"
                    }
                ],
                "medium": [
                    {
                        "action": "address_objections",
                        "description": "Abordar objeciones potenciales",
                        "priority": "high"
                    },
                    {
                        "action": "highlight_benefits",
                        "description": "Destacar beneficios específicos para el cliente",
                        "priority": "high"
                    },
                    {
                        "action": "suggest_next_steps",
                        "description": "Sugerir próximos pasos concretos",
                        "priority": "medium"
                    }
                ],
                "high": [
                    {
                        "action": "close_sale",
                        "description": "Cerrar la venta directamente",
                        "priority": "high"
                    },
                    {
                        "action": "offer_incentive",
                        "description": "Ofrecer incentivo para decisión inmediata",
                        "priority": "medium"
                    },
                    {
                        "action": "schedule_followup",
                        "description": "Programar seguimiento concreto",
                        "priority": "medium"
                    }
                ]
            }
            
            # Definir recomendaciones basadas en señales
            signal_recommendations = {
                "buying_signals": {
                    "threshold": 0.3,
                    "action": "create_urgency",
                    "description": "Crear sentido de urgencia o escasez",
                    "priority": "medium"
                },
                "engagement_level": {
                    "threshold": 0.3,
                    "action": "ask_open_questions",
                    "description": "Formular preguntas abiertas para aumentar participación",
                    "priority": "high"
                },
                "positive_sentiment": {
                    "threshold": 0.3,
                    "action": "address_concerns",
                    "description": "Abordar preocupaciones o frustraciones del cliente",
                    "priority": "high"
                },
                "specific_inquiries": {
                    "threshold": 0.3,
                    "action": "provide_details",
                    "description": "Ofrecer detalles específicos sobre características y beneficios",
                    "priority": "medium"
                }
            }
            
            # Generar recomendaciones basadas en la categoría
            recommendations = recommendation_templates.get(conversion_category, [])
            
            # Añadir recomendaciones basadas en señales
            for signal_name, signal_info in signal_recommendations.items():
                if signals.get(signal_name, 0) < signal_info["threshold"]:
                    recommendations.append({
                        "action": signal_info["action"],
                        "description": signal_info["description"],
                        "priority": signal_info["priority"]
                    })
            
            # Añadir recomendaciones basadas en perfil del cliente
            if customer_profile:
                # Si es cliente existente con compras previas
                previous_purchases = customer_profile.get("previous_purchases", [])
                if previous_purchases:
                    recommendations.append({
                        "action": "reference_history",
                        "description": "Hacer referencia a compras o interacciones previas",
                        "priority": "high"
                    })
                else:  # Si es cliente nuevo
                    recommendations.append({
                        "action": "offer_trial",
                        "description": "Ofrecer prueba o demo del producto/servicio",
                        "priority": "high"
                    })
                
                # Según segmento del cliente
                segment = customer_profile.get("segment")
                if segment == "premium":
                    recommendations.append({
                        "action": "highlight_exclusivity",
                        "description": "Destacar aspectos exclusivos o premium",
                        "priority": "high"
                    })
                elif segment == "price_sensitive":
                    recommendations.append({
                        "action": "emphasize_value",
                        "description": "Enfatizar relación calidad-precio",
                        "priority": "high"
                    })
            
            # Eliminar duplicados
            unique_recommendations = []
            action_set = set()
            
            for rec in recommendations:
                action = rec["action"]
                if action not in action_set:
                    action_set.add(action)
                    unique_recommendations.append(rec)
            
            # Ordenar por prioridad
            priority_order = {"high": 0, "medium": 1, "low": 2}
            unique_recommendations.sort(key=lambda x: priority_order.get(x.get("priority"), 999))
            
            # Limitar a un máximo de 5 recomendaciones
            return unique_recommendations[:5]
            
        except Exception as e:
            logger.error(f"Error al generar recomendaciones de conversión: {e}")
            return [{
                "action": "continue_conversation",
                "description": "Continuar la conversación para obtener más información",
                "priority": "medium"
            }]
    
    async def record_actual_conversion(self, conversation_id: str, 
                                 did_convert: bool,
                                 conversion_details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Registra el resultado real de conversión para mejorar el modelo.
        
        Args:
            conversation_id: ID de la conversación
            did_convert: Indica si el cliente realmente se convirtió
            conversion_details: Detalles adicionales de la conversión (opcional)
            
        Returns:
            Resultado del registro
        """
        try:
            # Crear el objeto de resultado real
            actual_result = {
                "did_convert": did_convert,
                "conversion_details": conversion_details or {},
                "timestamp": datetime.now().isoformat()
            }
            
            # Determinar si la predicción fue correcta se hará en la clase base
            # usando la lógica específica para este tipo de predicción
            result = await self.record_actual_result(
                conversation_id=conversation_id,
                actual_result=actual_result
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error al registrar resultado de conversión: {e}")
            return {}
    
    async def get_conversion_statistics(self, time_period: Optional[int] = None) -> Dict[str, Any]:
        """
        Obtiene estadísticas sobre predicciones de conversión.
        
        Args:
            time_period: Período de tiempo en días (opcional)
            
        Returns:
            Estadísticas de conversión
        """
        try:
            # Obtener estadísticas básicas
            basic_stats = await self.get_statistics(time_period)
            
            # Obtener distribución de conversiones
            query = self.supabase.table("prediction_results").select("*").eq("model_name", self.model_name).eq("status", "completed").execute()
            
            if not query.data:
                return {
                    **basic_stats,
                    "conversion_rate": 0,
                    "category_distribution": {},
                    "total_predictions": 0
                }
            
            # Calcular tasa de conversión real
            total_predictions = len(query.data)
            conversions = 0
            category_counts = {"low": 0, "medium": 0, "high": 0, "very_high": 0}
            
            for prediction in query.data:
                actual_result = json.loads(prediction["result"]) if prediction["result"] else {}
                prediction_data = json.loads(prediction["prediction_data"]) if prediction["prediction_data"] else {}
                
                # Contar conversiones reales
                if actual_result.get("did_convert", False):
                    conversions += 1
                
                # Contar categorías de predicción
                category = prediction_data.get("category", "low")
                if category in category_counts:
                    category_counts[category] += 1
            
            # Calcular tasa de conversión
            conversion_rate = conversions / total_predictions if total_predictions > 0 else 0
            
            # Calcular distribución de categorías
            category_distribution = {}
            for category, count in category_counts.items():
                category_distribution[category] = count / total_predictions if total_predictions > 0 else 0
            
            return {
                **basic_stats,
                "conversion_rate": conversion_rate,
                "category_distribution": category_distribution,
                "total_predictions": total_predictions
            }
            
        except Exception as e:
            logger.error(f"Error al obtener estadísticas de conversión: {e}")
            return {
                "accuracy": {"accuracy": 0, "total_predictions": 0},
                "conversion_rate": 0,
                "category_distribution": {},
                "total_predictions": 0
            }
