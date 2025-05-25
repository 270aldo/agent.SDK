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

logger = logging.getLogger(__name__)

class ConversionPredictionService:
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
        self.supabase = supabase_client
        self.predictive_model_service = predictive_model_service
        self.nlp_service = nlp_integration_service
        self.model_name = "conversion_prediction_model"
        self._initialize_model()
        
    async def _initialize_model(self) -> None:
        """
        Inicializa el modelo de predicción de conversión.
        """
        try:
            # Verificar si el modelo ya existe
            model = await self.predictive_model_service.get_model(self.model_name)
            
            if not model:
                # Crear modelo si no existe
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
                
                await self.predictive_model_service.register_model(
                    model_name=self.model_name,
                    model_type="conversion",
                    model_params=model_params,
                    description="Modelo para predicción de probabilidad de conversión"
                )
                logger.info(f"Modelo de predicción de conversión inicializado: {self.model_name}")
            
        except Exception as e:
            logger.error(f"Error al inicializar modelo de predicción de conversión: {e}")
    
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
            if not messages:
                return {
                    "probability": 0, 
                    "confidence": 0, 
                    "category": "low", 
                    "signals": {},
                    "recommendations": []
                }
            
            # Obtener parámetros del modelo
            model = await self.predictive_model_service.get_model(self.model_name)
            if not model or "parameters" not in model:
                logger.error("Modelo de predicción de conversión no encontrado")
                return {
                    "probability": 0, 
                    "confidence": 0, 
                    "category": "low", 
                    "signals": {},
                    "recommendations": []
                }
            
            model_params = json.loads(model["parameters"])
            conversion_thresholds = model_params.get("conversion_thresholds", {"low": 0.3, "medium": 0.6, "high": 0.8})
            confidence_threshold = model_params.get("confidence_threshold", 0.65)
            context_window = model_params.get("context_window", 10)
            signal_weights = model_params.get("signal_weights", {})
            
            # Limitar a los últimos N mensajes para el análisis
            recent_messages = messages[-context_window:] if len(messages) > context_window else messages
            
            # Extraer texto de los mensajes del cliente
            client_messages = [msg for msg in recent_messages if msg.get("role") == "user"]
            
            if not client_messages:
                return {
                    "probability": 0, 
                    "confidence": 0, 
                    "category": "low", 
                    "signals": {},
                    "recommendations": []
                }
            
            # Detectar señales de conversión
            signals = await self._detect_conversion_signals(client_messages, recent_messages, signal_weights)
            
            # Calcular probabilidad de conversión
            conversion_probability, confidence = await self._calculate_conversion_probability(
                signals, 
                customer_profile
            )
            
            # Determinar categoría de conversión
            conversion_category = self._get_conversion_category(conversion_probability, conversion_thresholds)
            
            # Obtener recomendaciones para aumentar conversión
            recommendations = await self._get_conversion_recommendations(
                conversion_category, 
                signals, 
                customer_profile
            )
            
            # Almacenar predicción
            prediction_data = {
                "probability": conversion_probability,
                "category": conversion_category,
                "signals": signals
            }
            
            await self.predictive_model_service.store_prediction(
                model_name=self.model_name,
                conversation_id=conversation_id,
                prediction_type="conversion",
                prediction_data=prediction_data,
                confidence=confidence
            )
            
            return {
                "probability": conversion_probability,
                "confidence": confidence,
                "category": conversion_category,
                "signals": signals,
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"Error al predecir conversión: {e}")
            return {
                "probability": 0, 
                "confidence": 0, 
                "category": "low", 
                "signals": {},
                "recommendations": []
            }
    
    async def _detect_conversion_signals(self, client_messages: List[Dict[str, Any]], 
                                   all_messages: List[Dict[str, Any]],
                                   signal_weights: Dict[str, float]) -> Dict[str, float]:
        """
        Detecta señales de conversión en los mensajes.
        
        Args:
            client_messages: Lista de mensajes del cliente
            all_messages: Lista de todos los mensajes (cliente y agente)
            signal_weights: Pesos para diferentes tipos de señales
            
        Returns:
            Diccionario con señales detectadas y sus intensidades
        """
        signals = {}
        
        # Extraer contenido de mensajes del cliente
        client_texts = [msg.get("content", "") for msg in client_messages]
        combined_text = " ".join(client_texts).lower()
        
        # 1. Detectar señales de compra
        buying_signal_phrases = [
            "cuándo podría", "cómo puedo comprar", "me interesa", "quiero adquirir",
            "precio final", "descuento", "oferta", "disponibilidad", "stock",
            "formas de pago", "plazos", "contrato", "términos", "condiciones",
            "cuándo podríamos empezar", "siguiente paso", "demo", "prueba"
        ]
        
        buying_signal_count = sum(1 for phrase in buying_signal_phrases if phrase in combined_text)
        if buying_signal_count > 0:
            signals["buying_signals"] = min(1.0, buying_signal_count / 3)
        
        # 2. Medir nivel de engagement
        # Calcular proporción de mensajes del cliente vs total
        engagement_ratio = len(client_messages) / len(all_messages) if all_messages else 0
        # Calcular longitud promedio de mensajes del cliente
        avg_message_length = sum(len(msg.get("content", "")) for msg in client_messages) / len(client_messages) if client_messages else 0
        
        # Normalizar longitud de mensaje (considerando que 50 caracteres es un mensaje corto)
        normalized_length = min(1.0, avg_message_length / 100)
        
        # Combinar métricas de engagement
        engagement_score = (engagement_ratio + normalized_length) / 2
        if engagement_score > 0.3:  # Umbral mínimo de engagement
            signals["engagement_level"] = engagement_score
        
        # 3. Analizar frecuencia de preguntas
        question_indicators = ["?", "cómo", "qué", "cuándo", "dónde", "por qué", "cuánto", "cuál"]
        question_count = sum(1 for msg in client_texts if any(indicator in msg.lower() for indicator in question_indicators))
        
        if question_count > 0:
            # Normalizar por número de mensajes
            normalized_question_freq = question_count / len(client_messages) if client_messages else 0
            signals["question_frequency"] = normalized_question_freq
        
        # 4. Analizar sentimiento positivo
        positive_sentiment_score = 0
        sentiment_count = 0
        
        for message in client_texts:
            nlp_analysis = await self.nlp_service.analyze_message(message)
            sentiment = nlp_analysis.get("sentiment", {}).get("score", 0)
            
            # Considerar solo sentimiento positivo
            if sentiment > 0:
                positive_sentiment_score += sentiment
                sentiment_count += 1
        
        if sentiment_count > 0:
            avg_positive_sentiment = positive_sentiment_score / sentiment_count
            signals["positive_sentiment"] = avg_positive_sentiment
        
        # 5. Detectar consultas específicas
        specific_inquiry_phrases = [
            "especificaciones", "características", "funcionalidades", "detalles técnicos",
            "compatibilidad", "integración", "implementación", "requisitos",
            "garantía", "soporte", "mantenimiento", "capacitación",
            "personalización", "configuración", "opciones"
        ]
        
        specific_inquiry_count = sum(1 for phrase in specific_inquiry_phrases if phrase in combined_text)
        if specific_inquiry_count > 0:
            signals["specific_inquiries"] = min(1.0, specific_inquiry_count / 3)
        
        # 6. Evaluar inversión de tiempo
        # Calcular duración aproximada de la conversación basada en número de mensajes
        conversation_duration = len(all_messages) * 0.5  # Asumiendo 30 segundos por mensaje en promedio
        
        # Normalizar duración (considerando que 10 minutos es una conversación significativa)
        normalized_duration = min(1.0, conversation_duration / 20)
        
        if normalized_duration > 0.2:  # Umbral mínimo de inversión de tiempo
            signals["time_investment"] = normalized_duration
        
        # Aplicar pesos a las señales
        weighted_signals = {}
        for signal, value in signals.items():
            if signal in signal_weights:
                weighted_signals[signal] = value * signal_weights[signal]
            else:
                weighted_signals[signal] = value * 0.1  # Peso por defecto
        
        return weighted_signals
    
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
        # Si no hay señales, la probabilidad es baja
        if not signals:
            return 0.1, 0.5
        
        # Calcular puntuación base sumando todas las señales ponderadas
        base_score = sum(signals.values())
        
        # Normalizar a un rango 0-1
        normalized_score = min(1.0, base_score / 1.5)  # 1.5 como valor máximo esperado
        
        # Ajustar basado en perfil del cliente (si está disponible)
        adjusted_score = normalized_score
        profile_factor = 1.0
        
        if customer_profile:
            # Factores de ajuste basados en perfil
            profile_adjustments = []
            
            # 1. Ajuste por historial de compras previas
            previous_purchases = customer_profile.get("previous_purchases", [])
            if previous_purchases:
                purchase_factor = min(1.3, 1 + (len(previous_purchases) * 0.1))
                profile_adjustments.append(purchase_factor)
            
            # 2. Ajuste por tiempo como cliente
            customer_since = customer_profile.get("customer_since")
            if customer_since:
                try:
                    # Calcular años como cliente
                    customer_date = datetime.fromisoformat(customer_since)
                    years_as_customer = (datetime.now() - customer_date).days / 365
                    
                    loyalty_factor = min(1.2, 1 + (years_as_customer * 0.05))
                    profile_adjustments.append(loyalty_factor)
                except:
                    pass
            
            # 3. Ajuste por segmento de cliente
            segment = customer_profile.get("segment")
            segment_factors = {
                "premium": 1.3,
                "standard": 1.1,
                "basic": 0.9
            }
            
            if segment and segment in segment_factors:
                profile_adjustments.append(segment_factors[segment])
            
            # Calcular factor de perfil promedio
            if profile_adjustments:
                profile_factor = sum(profile_adjustments) / len(profile_adjustments)
            
            # Aplicar ajuste de perfil
            adjusted_score = min(1.0, normalized_score * profile_factor)
        
        # Calcular nivel de confianza basado en cantidad y diversidad de señales
        signal_count = len(signals)
        signal_diversity = signal_count / 6  # 6 es el número máximo de tipos de señales
        
        confidence = 0.5 + (signal_diversity * 0.5)  # Rango 0.5-1.0
        
        return adjusted_score, confidence
    
    def _get_conversion_category(self, probability: float, thresholds: Dict[str, float]) -> str:
        """
        Determina la categoría de conversión basada en la probabilidad.
        
        Args:
            probability: Probabilidad de conversión (0-1)
            thresholds: Umbrales para categorías
            
        Returns:
            Categoría de conversión (low, medium, high)
        """
        if probability < thresholds.get("low", 0.3):
            return "low"
        elif probability < thresholds.get("medium", 0.6):
            return "medium"
        elif probability < thresholds.get("high", 0.8):
            return "high"
        else:
            return "very_high"
    
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
        # Biblioteca de recomendaciones por categoría de conversión
        category_recommendations = {
            "low": [
                {
                    "type": "engagement",
                    "action": "Hacer preguntas abiertas para identificar necesidades",
                    "priority": "high"
                },
                {
                    "type": "value",
                    "action": "Presentar casos de éxito relevantes para el sector",
                    "priority": "high"
                },
                {
                    "type": "education",
                    "action": "Compartir información educativa sobre el problema que resuelve el producto",
                    "priority": "medium"
                },
                {
                    "type": "relationship",
                    "action": "Establecer puntos de contacto periódicos para seguimiento",
                    "priority": "medium"
                }
            ],
            "medium": [
                {
                    "type": "objection",
                    "action": "Abordar proactivamente posibles objeciones",
                    "priority": "high"
                },
                {
                    "type": "demonstration",
                    "action": "Ofrecer una demostración personalizada del producto",
                    "priority": "high"
                },
                {
                    "type": "incentive",
                    "action": "Presentar opciones de prueba o período inicial con descuento",
                    "priority": "medium"
                },
                {
                    "type": "urgency",
                    "action": "Destacar beneficios de implementación temprana",
                    "priority": "medium"
                }
            ],
            "high": [
                {
                    "type": "closing",
                    "action": "Proponer próximos pasos concretos para avanzar",
                    "priority": "high"
                },
                {
                    "type": "customization",
                    "action": "Presentar plan de implementación personalizado",
                    "priority": "high"
                },
                {
                    "type": "reassurance",
                    "action": "Reforzar garantías y soporte post-venta",
                    "priority": "medium"
                },
                {
                    "type": "relationship",
                    "action": "Asignar un gestor de cuenta dedicado",
                    "priority": "medium"
                }
            ],
            "very_high": [
                {
                    "type": "closing",
                    "action": "Preparar documentación para formalizar acuerdo",
                    "priority": "high"
                },
                {
                    "type": "upsell",
                    "action": "Presentar opciones premium o complementarias",
                    "priority": "high"
                },
                {
                    "type": "onboarding",
                    "action": "Detallar proceso de onboarding y cronograma",
                    "priority": "medium"
                },
                {
                    "type": "relationship",
                    "action": "Programar reunión con equipo de implementación",
                    "priority": "medium"
                }
            ]
        }
        
        # Obtener recomendaciones base según categoría
        recommendations = category_recommendations.get(conversion_category, [])
        
        # Recomendaciones adicionales basadas en señales débiles
        weak_signals = []
        for signal, value in signals.items():
            if value < 0.3:  # Umbral para considerar una señal débil
                weak_signals.append(signal)
        
        # Añadir recomendaciones específicas para fortalecer señales débiles
        signal_recommendations = {
            "buying_signals": {
                "type": "trial",
                "action": "Ofrecer una prueba gratuita o demostración del producto",
                "priority": "high"
            },
            "engagement_level": {
                "type": "engagement",
                "action": "Hacer preguntas más específicas sobre sus necesidades",
                "priority": "high"
            },
            "question_frequency": {
                "type": "education",
                "action": "Compartir más información sobre características clave",
                "priority": "medium"
            },
            "positive_sentiment": {
                "type": "emotional",
                "action": "Enfatizar beneficios emocionales del producto/servicio",
                "priority": "medium"
            },
            "specific_inquiries": {
                "type": "details",
                "action": "Proporcionar especificaciones técnicas detalladas",
                "priority": "high"
            },
            "time_investment": {
                "type": "value",
                "action": "Resumir puntos clave y valor principal de la oferta",
                "priority": "medium"
            }
        }
        
        # Añadir recomendaciones para señales débiles
        for signal in weak_signals:
            if signal in signal_recommendations:
                recommendations.append(signal_recommendations[signal])
        
        # Personalizar recomendaciones según perfil del cliente (si está disponible)
        if customer_profile:
            industry = customer_profile.get("industry")
            
            # Recomendaciones específicas por industria
            industry_recommendations = {
                "healthcare": {
                    "type": "compliance",
                    "action": "Destacar cumplimiento normativo y seguridad de datos",
                    "priority": "high"
                },
                "finance": {
                    "type": "security",
                    "action": "Enfatizar medidas de seguridad y protección de datos",
                    "priority": "high"
                },
                "education": {
                    "type": "scalability",
                    "action": "Presentar opciones de escalabilidad para diferentes niveles educativos",
                    "priority": "medium"
                },
                "retail": {
                    "type": "integration",
                    "action": "Destacar integración con sistemas de punto de venta",
                    "priority": "high"
                },
                "technology": {
                    "type": "api",
                    "action": "Compartir documentación técnica y capacidades de API",
                    "priority": "high"
                }
            }
            
            # Añadir recomendación específica por industria
            if industry and industry in industry_recommendations:
                recommendations.append(industry_recommendations[industry])
        
        # Eliminar duplicados y limitar a 5 recomendaciones
        unique_recommendations = []
        recommendation_types = set()
        
        for rec in recommendations:
            if rec["type"] not in recommendation_types:
                unique_recommendations.append(rec)
                recommendation_types.add(rec["type"])
                
                if len(unique_recommendations) >= 5:
                    break
        
        # Ordenar por prioridad
        priority_values = {"high": 3, "medium": 2, "low": 1}
        unique_recommendations.sort(key=lambda x: priority_values.get(x.get("priority"), 0), reverse=True)
        
        return unique_recommendations
    
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
            # Obtener predicciones previas para esta conversación
            query = self.supabase.table("prediction_results").select("*").eq("conversation_id", conversation_id).eq("model_name", self.model_name).execute()
            
            if not query.data:
                logger.warning(f"No se encontraron predicciones previas para la conversación: {conversation_id}")
                return {}
            
            prediction = query.data[0]
            prediction_id = prediction["id"]
            prediction_data = json.loads(prediction["prediction_data"])
            
            # Verificar si la predicción fue correcta
            predicted_probability = prediction_data.get("probability", 0)
            predicted_category = prediction_data.get("category", "low")
            
            # Una predicción se considera correcta si:
            # - Predijo alta probabilidad (>0.6) y el cliente se convirtió
            # - Predijo baja probabilidad (<0.4) y el cliente no se convirtió
            was_correct = (predicted_probability > 0.6 and did_convert) or (predicted_probability < 0.4 and not did_convert)
            
            # Registrar el resultado real
            actual_result = {
                "did_convert": did_convert,
                "conversion_details": conversion_details or {},
                "timestamp": datetime.now().isoformat()
            }
            
            result = await self.predictive_model_service.update_prediction_result(
                prediction_id=prediction_id,
                actual_result=actual_result,
                was_correct=was_correct
            )
            
            # Añadir datos para entrenamiento futuro
            features = {
                "conversation_id": conversation_id,
                "signals": prediction_data.get("signals", {}),
                "predicted_probability": predicted_probability,
                "predicted_category": predicted_category
            }
            
            await self.predictive_model_service.add_training_data(
                model_name=self.model_name,
                data_type="conversion",
                features=features,
                label=1 if did_convert else 0
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
            # Obtener precisión del modelo
            accuracy_stats = await self.predictive_model_service.get_model_accuracy(
                model_name=self.model_name,
                time_period=time_period
            )
            
            # Obtener distribución de conversiones
            query = self.supabase.table("prediction_results").select("*").eq("model_name", self.model_name).eq("status", "completed").execute()
            
            if not query.data:
                return {
                    "accuracy": accuracy_stats,
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
                "accuracy": accuracy_stats,
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
