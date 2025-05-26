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

logger = logging.getLogger(__name__)

class ObjectionPredictionService:
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
        self.supabase = supabase_client
        self.predictive_model_service = predictive_model_service
        self.nlp_service = nlp_integration_service
        self.model_name = "objection_prediction_model"
        self._initialize_model()
        
    async def _initialize_model(self) -> None:
        """
        Inicializa el modelo de predicción de objeciones.
        """
        try:
            # Verificar si el modelo ya existe
            model = await self.predictive_model_service.get_model(self.model_name)
            
            if not model:
                # Crear modelo si no existe
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
                
                await self.predictive_model_service.register_model(
                    model_name=self.model_name,
                    model_type="objection",
                    model_params=model_params,
                    description="Modelo para predicción de objeciones de clientes"
                )
                logger.info(f"Modelo de predicción de objeciones inicializado: {self.model_name}")
            
        except Exception as e:
            logger.error(f"Error al inicializar modelo de predicción de objeciones: {e}")
    
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
    
    async def _detect_objection_signals(self, messages: List[str], 
                                  signal_weights: Dict[str, float]) -> Dict[str, float]:
        """
        Detecta señales de posibles objeciones en los mensajes.
        
        Args:
            messages: Lista de mensajes del cliente
            signal_weights: Pesos para diferentes tipos de señales
            
        Returns:
            Diccionario con señales detectadas y sus intensidades
        """
        signals = {}
        combined_text = " ".join(messages).lower()
        
        # Analizar sentimiento
        for message in messages:
            nlp_analysis = await self.nlp_service.analyze_message(message)
            sentiment = nlp_analysis.get("sentiment", {}).get("score", 0)
            
            # Detectar sentimiento negativo
            if sentiment < -0.2:
                signals["sentiment_negative"] = abs(sentiment)
        
        # Detectar palabras de duda/hesitación
        hesitation_words = ["quizás", "tal vez", "no estoy seguro", "tengo dudas", 
                           "necesito pensar", "no sé si", "me preocupa"]
        hesitation_count = sum(1 for word in hesitation_words if word in combined_text)
        if hesitation_count > 0:
            signals["hesitation_words"] = min(1.0, hesitation_count / 3)
        
        # Detectar frases de comparación
        comparison_phrases = ["mejor que", "comparado con", "a diferencia de", 
                             "más barato", "más caro", "competidor", "alternativa"]
        comparison_count = sum(1 for phrase in comparison_phrases if phrase in combined_text)
        if comparison_count > 0:
            signals["comparison_phrases"] = min(1.0, comparison_count / 2)
        
        # Detectar menciones de precio
        price_phrases = ["precio", "costo", "caro", "barato", "presupuesto", 
                        "inversión", "gasto", "pagar", "euros", "dólares", "pesos"]
        price_count = sum(1 for phrase in price_phrases if phrase in combined_text)
        if price_count > 0:
            signals["price_mentions"] = min(1.0, price_count / 2)
        
        # Detectar frases de incertidumbre
        uncertainty_phrases = ["no estoy convencido", "tendría que consultar", 
                              "no es lo que esperaba", "no cumple", "me falta", 
                              "necesito más información"]
        uncertainty_count = sum(1 for phrase in uncertainty_phrases if phrase in combined_text)
        if uncertainty_count > 0:
            signals["uncertainty_phrases"] = min(1.0, uncertainty_count / 2)
        
        # Aplicar pesos a las señales
        weighted_signals = {}
        for signal, value in signals.items():
            if signal in signal_weights:
                weighted_signals[signal] = value * signal_weights[signal]
            else:
                weighted_signals[signal] = value * 0.1  # Peso por defecto
        
        return weighted_signals
    
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
            # Obtener predicciones previas para esta conversación
            query = self.supabase.table("prediction_results").select("*").eq("conversation_id", conversation_id).eq("model_name", self.model_name).execute()
            
            if not query.data:
                logger.warning(f"No se encontraron predicciones previas para la conversación: {conversation_id}")
                return {}
            
            prediction = query.data[0]
            prediction_id = prediction["id"]
            prediction_data = json.loads(prediction["prediction_data"])
            
            # Verificar si la objeción real coincide con la predicción
            predicted_objections = prediction_data.get("objection_types", [])
            was_correct = objection_type in predicted_objections
            
            # Registrar el resultado real
            actual_result = {
                "objection_type": objection_type,
                "objection_text": objection_text,
                "timestamp": datetime.now().isoformat()
            }
            
            result = await self.predictive_model_service.update_prediction_result(
                prediction_id=prediction_id,
                actual_result=actual_result,
                was_correct=was_correct
            )
            
            # Añadir datos para entrenamiento futuro
            features = {
                "objection_text": objection_text,
                "conversation_id": conversation_id,
                "signals": prediction_data.get("signals", {})
            }
            
            await self.predictive_model_service.add_training_data(
                model_name=self.model_name,
                data_type="objection",
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
            # Obtener precisión del modelo
            accuracy_stats = await self.predictive_model_service.get_model_accuracy(
                model_name=self.model_name,
                time_period=time_period
            )
            
            # Obtener distribución de tipos de objeciones
            query = self.supabase.table("prediction_results").select("*").eq("model_name", self.model_name).eq("status", "completed").execute()
            
            if not query.data:
                return {
                    "accuracy": accuracy_stats,
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
                "accuracy": accuracy_stats,
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
