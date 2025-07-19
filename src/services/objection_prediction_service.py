"""
Servicio de Predicción de Objeciones para NGX Voice Sales Agent.

Este servicio se encarga de predecir posibles objeciones que un cliente
podría presentar durante una conversación de ventas, permitiendo
anticiparse y preparar respuestas adecuadas.
"""

from typing import Dict, List, Any, Optional, Tuple
import logging
import json
from datetime import datetime

from src.integrations.supabase.resilient_client import ResilientSupabaseClient
from src.services.predictive_model_service import PredictiveModelService
from src.services.nlp_integration_service import NLPIntegrationService
from src.services.base_predictive_service import BasePredictiveService
from src.services.utils.signal_detection import detect_sentiment_signals, detect_keyword_signals, detect_question_patterns
from src.services.utils.scoring import normalize_scores, apply_weights, calculate_confidence, rank_items
from src.services.utils.recommendations import generate_response_suggestions

logger = logging.getLogger(__name__)

class ObjectionPredictionService(BasePredictiveService):
    """
    Servicio para predecir posibles objeciones de clientes durante conversaciones de ventas.
    
    Características principales:
    - Detección temprana de señales de objeción
    - Biblioteca de respuestas a objeciones comunes
    - Integración con análisis de sentimiento y contexto
    - Aprendizaje continuo basado en conversaciones pasadas
    """
    
    def __init__(self, 
                 supabase_client: ResilientSupabaseClient,
                 predictive_model_service: PredictiveModelService,
                 nlp_integration_service: NLPIntegrationService):
        """
        Inicializa el servicio de predicción de objeciones.
        
        Args:
            supabase_client: Cliente de Supabase para persistencia
            predictive_model_service: Servicio base para modelos predictivos
            nlp_integration_service: Servicio de integración NLP
        """
        super().__init__(
            supabase=supabase_client,
            predictive_model_service=predictive_model_service,
            nlp_integration_service=nlp_integration_service,
            model_name="objection_prediction_model",
            model_type="objection"
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
        Inicializa el modelo de predicción de objeciones.
        """
        model_params = {
            "objection_types": [
                "price", "value", "need", "urgency", "authority", 
                "trust", "competition", "features", "implementation", 
                "support", "compatibility"
            ],
            "confidence_threshold": 0.65,
            "context_window": 5,  # Número de mensajes a considerar para contexto
            "signal_weights": {
                "sentiment_negative": 0.3,
                "hesitation_words": 0.2,
                "comparison_phrases": 0.25,
                "price_mentions": 0.4,
                "uncertainty_phrases": 0.3
            }
        }
        
        await self.initialize_model(
            model_params=model_params,
            description="Modelo para predicción de objeciones de clientes"
        )
    
    async def predict_objections(self, conversation_id: str, 
                           messages: List[Dict[str, Any]],
                           customer_profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Predice posibles objeciones basadas en la conversación actual.
        
        Args:
            conversation_id: ID de la conversación
            messages: Lista de mensajes de la conversación
            customer_profile: Perfil del cliente (opcional)
            
        Returns:
            Predicciones de objeciones con niveles de confianza
        """
        try:
            await self.initialize()
            if not messages:
                return {"objections": [], "confidence": 0, "signals": {}}
            
            # Obtener parámetros del modelo
            model = await self.predictive_model_service.get_model(self.model_name)
            if not model or "parameters" not in model:
                logger.error("Modelo de predicción de objeciones no encontrado")
                return {"objections": [], "confidence": 0, "signals": {}}
            
            model_params = json.loads(model["parameters"])
            objection_types = model_params.get("objection_types", [])
            confidence_threshold = model_params.get("confidence_threshold", 0.65)
            context_window = model_params.get("context_window", 5)
            signal_weights = model_params.get("signal_weights", {})
            
            # Limitar a los últimos N mensajes para el análisis
            recent_messages = messages[-context_window:] if len(messages) > context_window else messages
            
            # Extraer texto de los mensajes del cliente
            client_messages = [msg["content"] for msg in recent_messages if msg.get("role") == "user"]
            
            if not client_messages:
                return {"objections": [], "confidence": 0, "signals": {}}
            
            # Analizar señales de objeción en los mensajes
            signals = await self._detect_objection_signals(client_messages, signal_weights)
            
            # Calcular puntuaciones para cada tipo de objeción
            objection_scores = await self._calculate_objection_scores(signals, objection_types, customer_profile)
            
            # Determinar las objeciones más probables
            predicted_objections = []
            for objection_type, score in objection_scores.items():
                if score >= confidence_threshold:
                    predicted_objections.append({
                        "type": objection_type,
                        "confidence": score,
                        "suggested_responses": await self._get_suggested_responses(objection_type)
                    })
            
            # Ordenar por nivel de confianza
            predicted_objections.sort(key=lambda x: x["confidence"], reverse=True)
            
            # Calcular confianza general
            overall_confidence = max(objection_scores.values()) if objection_scores else 0
            
            # Almacenar predicción
            prediction_data = {
                "objection_types": [obj["type"] for obj in predicted_objections],
                "signals": signals
            }
            
            await self.predictive_model_service.store_prediction(
                model_name=self.model_name,
                conversation_id=conversation_id,
                prediction_type="objection",
                prediction_data=prediction_data,
                confidence=overall_confidence
            )
            
            return {
                "objections": predicted_objections,
                "confidence": overall_confidence,
                "signals": signals
            }
            
        except Exception as e:
            logger.error(f"Error al predecir objeciones: {e}")
            return {"objections": [], "confidence": 0, "signals": {}}
    
    async def _detect_objection_signals(self, messages: List[Dict[str, Any]], 
                                  signal_weights: Dict[str, float]) -> Dict[str, float]:
        """
        Detecta señales de posibles objeciones en los mensajes.
        
        Args:
            messages: Lista de mensajes del cliente
            signal_weights: Pesos para diferentes tipos de señales
            
        Returns:
            Diccionario con señales detectadas y sus intensidades
        """
        try:
            # Extraer solo los mensajes del cliente
            client_messages = [msg for msg in messages if msg.get("role") == "user"]
            
            if not client_messages:
                return {}
            
            # Detectar señales de sentimiento
            sentiment_signals = await detect_sentiment_signals(client_messages, self.nlp_service)
            
            # Detectar señales de palabras clave
            keyword_signals = await detect_keyword_signals(client_messages, {
                "hesitation_words": ["pero", "sin embargo", "aunque", "no estoy seguro", "tal vez", "quizás", "demasiado", "caro", "complicado"],
                "comparison_phrases": ["otra opción", "competencia", "alternativa", "mejor oferta", "más barato", "más económico", "comparando"],
                "price_mentions": ["precio", "costo", "tarifa", "pago", "inversión", "descuento", "oferta", "presupuesto", "$", "euros", "pesos"],
                "uncertainty_phrases": ["no estoy convencido", "tengo que pensarlo", "consultarlo", "no estoy seguro", "duda", "preocupa", "problema"]
            })
            
            # Detectar patrones de preguntas
            question_signals = await detect_question_patterns(client_messages)
            
            # Combinar todas las señales
            signals = {**sentiment_signals, **keyword_signals, **question_signals}
            
            # Aplicar pesos a las señales
            weighted_signals = apply_weights(signals, signal_weights)
            
            return weighted_signals
            
        except Exception as e:
            logger.error(f"Error al detectar señales de objeción: {e}")
            return {}
    
    async def _calculate_objection_scores(self, signals: Dict[str, float], 
                                    objection_types: List[str],
                                    customer_profile: Optional[Dict[str, Any]] = None) -> Dict[str, float]:
        """
        Calcula puntuaciones para cada tipo de objeción basado en señales detectadas.
        
        Args:
            signals: Señales detectadas en la conversación
            objection_types: Tipos de objeciones a evaluar
            customer_profile: Perfil del cliente (opcional)
            
        Returns:
            Diccionario con tipos de objeción y sus puntuaciones
        """
        objection_scores = {objection_type: 0.0 for objection_type in objection_types}
        
        # Mapeo de señales a tipos de objeción
        signal_to_objection = {
            "sentiment_negative": ["price", "value", "trust", "features"],
            "hesitation_words": ["need", "urgency", "authority"],
            "comparison_phrases": ["competition", "features", "value"],
            "price_mentions": ["price", "value"],
            "uncertainty_phrases": ["trust", "need", "implementation", "support", "compatibility"]
        }
        
        # Calcular puntuaciones basadas en señales
        for signal, value in signals.items():
            if signal in signal_to_objection:
                for objection_type in signal_to_objection[signal]:
                    if objection_type in objection_scores:
                        objection_scores[objection_type] += value
        
        # Normalizar puntuaciones (0-1)
        max_score = max(objection_scores.values()) if objection_scores.values() else 1.0
        if max_score > 0:
            for objection_type in objection_scores:
                objection_scores[objection_type] /= max_score
        
        # Ajustar basado en perfil del cliente (si está disponible)
        if customer_profile:
            industry = customer_profile.get("industry")
            size = customer_profile.get("company_size")
            
            # Ajustes específicos por industria
            industry_adjustments = {
                "healthcare": {"compliance": 0.2, "security": 0.2},
                "finance": {"security": 0.3, "compliance": 0.3, "price": -0.1},
                "education": {"price": 0.2, "implementation": 0.1},
                "retail": {"features": 0.1, "implementation": 0.1},
                "technology": {"features": 0.2, "compatibility": 0.2}
            }
            
            # Aplicar ajustes por industria
            if industry and industry in industry_adjustments:
                for obj_type, adjustment in industry_adjustments[industry].items():
                    if obj_type in objection_scores:
                        objection_scores[obj_type] += adjustment
                        # Asegurar que esté en rango 0-1
                        objection_scores[obj_type] = max(0, min(1, objection_scores[obj_type]))
        
        return objection_scores
    
    async def _get_suggested_responses(self, objection_type: str) -> List[str]:
        """
        Obtiene respuestas sugeridas para un tipo de objeción.
        
        Args:
            objection_type: Tipo de objeción
            
        Returns:
            Lista de respuestas sugeridas
        """
        # Biblioteca de respuestas a objeciones comunes
        objection_responses = {
            "price": [
                "Entiendo su preocupación por el precio. Nuestro producto ofrece valor a largo plazo porque...",
                "Si analizamos el retorno de inversión, verá que el costo se amortiza en X meses debido a...",
                "Tenemos diferentes opciones de precios que podrían ajustarse mejor a su presupuesto..."
            ],
            "value": [
                "Los beneficios clave que nuestros clientes valoran más incluyen...",
                "A diferencia de otras soluciones, nuestro producto ofrece estas ventajas únicas...",
                "Basado en clientes similares, el valor principal que encontrará es..."
            ],
            "need": [
                "Entiendo que puede no ver la necesidad inmediata. Otros clientes inicialmente pensaron lo mismo hasta que...",
                "Basado en lo que me ha comentado sobre sus objetivos, esto podría ayudarle específicamente con...",
                "¿Le ayudaría si le muestro cómo esto ha resuelto problemas similares para otras empresas?"
            ],
            "urgency": [
                "Comprendo que no sea una prioridad inmediata. ¿Puedo preguntarle cuál es su cronograma para abordar este tema?",
                "Muchos clientes encuentran que retrasar esta decisión puede resultar en costos adicionales como...",
                "Actualmente tenemos una oferta especial que expira pronto, lo que podría ser una buena oportunidad..."
            ],
            "authority": [
                "Entiendo que necesita consultar con otros. ¿Podría ayudarle proporcionando materiales específicos para compartir?",
                "¿Qué información necesitaría la persona que toma la decisión para evaluar esta solución?",
                "¿Podríamos programar una breve demostración con todos los involucrados en la decisión?"
            ],
            "trust": [
                "Entiendo su cautela. Permítame compartir algunos casos de éxito de clientes similares...",
                "Ofrecemos una garantía de satisfacción que elimina el riesgo porque...",
                "¿Le ayudaría hablar directamente con alguno de nuestros clientes actuales?"
            ],
            "competition": [
                "Apreciamos que esté evaluando todas sus opciones. Nuestra diferencia principal es...",
                "En comparación con ese proveedor, nuestras ventajas únicas incluyen...",
                "Algunos clientes que cambiaron de ese proveedor a nosotros lo hicieron porque..."
            ],
            "features": [
                "Además de esa característica, ofrecemos estas funcionalidades que podrían ser valiosas para su caso...",
                "Entiendo que esa característica es importante. Nuestra solución aborda esa necesidad mediante...",
                "Estamos desarrollando mejoras en esa área. Mientras tanto, ofrecemos estas alternativas..."
            ],
            "implementation": [
                "El proceso de implementación típicamente toma X semanas, y nuestro equipo le acompaña en cada paso...",
                "Ofrecemos un plan de implementación estructurado que minimiza las interrupciones...",
                "Nuestro equipo de soporte está disponible durante todo el proceso de implementación para..."
            ],
            "support": [
                "Nuestro soporte incluye X horas de asistencia directa, además de recursos en línea como...",
                "El tiempo promedio de respuesta de nuestro equipo de soporte es de X horas...",
                "Ofrecemos diferentes niveles de soporte, incluyendo opciones premium con tiempos de respuesta garantizados..."
            ],
            "compatibility": [
                "Nuestra solución se integra con las principales plataformas, incluyendo...",
                "Tenemos APIs y conectores específicos para facilitar la integración con...",
                "Nuestro equipo técnico puede realizar una evaluación de compatibilidad para identificar cualquier ajuste necesario..."
            ]
        }
        
        return objection_responses.get(objection_type, ["Lo siento, no tengo respuestas específicas para este tipo de objeción."])
    
    async def record_actual_objection(self, conversation_id: str, 
                                objection_type: str,
                                objection_text: str) -> Dict[str, Any]:
        """
        Registra una objeción real para mejorar el modelo.
        
        Args:
            conversation_id: ID de la conversación
            objection_type: Tipo de objeción detectada
            objection_text: Texto de la objeción
            
        Returns:
            Resultado del registro
        """
        try:
            # Registrar el resultado real
            actual_result = {
                "objection_type": objection_type,
                "objection_text": objection_text,
                "timestamp": datetime.now().isoformat()
            }
            
            result = await self.record_actual_result(
                conversation_id=conversation_id,
                actual_result=actual_result,
                was_correct=None  # Se determinará automáticamente en record_actual_result
            )
            
            # Añadir datos para entrenamiento futuro
            features = {
                "objection_text": objection_text,
                "conversation_id": conversation_id
            }
            
            await self.add_training_data(
                features=features,
                label=objection_type
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error al registrar objeción real: {e}")
            return {}
    
    async def get_objection_statistics(self, time_period: Optional[int] = None) -> Dict[str, Any]:
        """
        Obtiene estadísticas sobre objeciones detectadas.
        
        Args:
            time_period: Período de tiempo en días (opcional)
            
        Returns:
            Estadísticas de objeciones
        """
        try:
            # Obtener estadísticas básicas
            basic_stats = await self.get_statistics(time_period)
            
            # Obtener distribución de tipos de objeciones
            query = self.supabase.table("prediction_results").select("*").eq("model_name", self.model_name).eq("status", "completed").execute()
            
            if not query.data:
                return {
                    **basic_stats,
                    "objection_distribution": {},
                    "total_objections": 0
                }
            
            # Contar tipos de objeciones
            objection_counts = {}
            for prediction in query.data:
                actual_result = json.loads(prediction["result"]) if prediction["result"] else {}
                objection_type = actual_result.get("objection_type")
                
                if objection_type:
                    objection_counts[objection_type] = objection_counts.get(objection_type, 0) + 1
            
            total_objections = sum(objection_counts.values())
            
            # Calcular distribución porcentual
            objection_distribution = {}
            for objection_type, count in objection_counts.items():
                objection_distribution[objection_type] = count / total_objections if total_objections > 0 else 0
            
            return {
                **basic_stats,
                "objection_distribution": objection_distribution,
                "total_objections": total_objections
            }
            
        except Exception as e:
            logger.error(f"Error al obtener estadísticas de objeciones: {e}")
            return {
                "accuracy": {"accuracy": 0, "total_predictions": 0},
                "objection_distribution": {},
                "total_objections": 0
            }
