"""
Conversation Outcome Tracker - Sistema de tracking para aprendizaje ML.

Este servicio rastrea cada conversación en detalle para alimentar el sistema
de aprendizaje adaptativo. Captura:
- Métricas de performance en tiempo real
- Estrategias utilizadas y su efectividad
- Outcomes y factores de éxito/fracaso
- Datos para pattern recognition y optimization

Es el foundation del sistema ML que convierte al agente en organismo vivo.
"""

import logging
import asyncio
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import uuid
from dataclasses import asdict

# Importar modelos
from src.models.learning_models import (
    ConversationOutcomeRecord,
    ConversationMetrics,
    ConversationOutcome,
    ExperimentVariant
)
from src.models.conversation import ConversationState, Message

# Importar integración con base de datos
from src.integrations.supabase import supabase_client

logger = logging.getLogger(__name__)


class ConversationOutcomeTracker:
    """
    Tracker completo de outcomes de conversación para ML adaptativo.
    
    Funcionalidades:
    - Tracking en tiempo real de métricas
    - Identificación automática de estrategias usadas
    - Cálculo de scores de éxito/fracaso
    - Almacenamiento estructurado para ML
    - Detección de patrones de comportamiento
    """
    
    def __init__(self):
        self.tracked_conversations = {}  # Cache de conversaciones activas
        self.metrics_buffer = {}  # Buffer para métricas en tiempo real
        self.strategy_detection_patterns = self._initialize_strategy_patterns()
        
    def _initialize_strategy_patterns(self) -> Dict[str, List[str]]:
        """Inicializa patrones para detectar estrategias usadas."""
        return {
            "consultative_approach": [
                "entiendo", "comprendo", "¿qué opinas?", "cuéntame", 
                "me parece", "en tu caso", "para tu situación"
            ],
            "hie_emphasis": [
                "hybrid intelligence engine", "hie", "11 agentes", 
                "imposible de clonar", "tecnología única"
            ],
            "empathy_techniques": [
                "validación", "comprendo tu", "es normal", "muchos clientes",
                "perfectamente normal", "entiendo tu preocupación"
            ],
            "early_adopter_presentation": [
                "primeros", "exclusivo", "limitado", "pioneer", 
                "innovator", "early adopter"
            ],
            "tier_recommendation": [
                "essential", "pro", "elite", "premium", 
                "recomiendo", "ideal para ti", "perfecto para"
            ],
            "objection_handling": [
                "entiendo tu preocupación", "es una consideración válida",
                "muchos clientes preguntan", "permíteme explicar"
            ],
            "social_proof": [
                "otros clientes", "caso de éxito", "testimonios",
                "resultados similares", "transformación"
            ]
        }
    
    async def start_tracking_conversation(
        self, 
        conversation_id: str,
        initial_client_data: Dict[str, Any],
        experiment_assignments: List[str] = None
    ) -> None:
        """
        Inicia el tracking de una nueva conversación.
        
        Args:
            conversation_id: ID único de la conversación
            initial_client_data: Datos iniciales del cliente
            experiment_assignments: IDs de experimentos asignados
        """
        try:
            tracking_data = {
                "conversation_id": conversation_id,
                "start_time": datetime.now(),
                "client_data": initial_client_data,
                "experiment_assignments": experiment_assignments or [],
                "messages_log": [],
                "strategies_detected": set(),
                "metrics_history": [],
                "real_time_metrics": {
                    "engagement_score": 5.0,
                    "conversion_probability": 0.5,
                    "emotional_stability": 0.7,
                    "response_quality": 0.8
                }
            }
            
            self.tracked_conversations[conversation_id] = tracking_data
            
            logger.info(
                f"Started tracking conversation {conversation_id} "
                f"with {len(experiment_assignments or [])} experiments assigned"
            )
            
        except Exception as e:
            logger.error(f"Error starting conversation tracking: {str(e)}")
    
    async def update_conversation_metrics(
        self,
        conversation_id: str,
        message: Message,
        response_time_seconds: float,
        additional_metrics: Dict[str, Any] = None
    ) -> None:
        """
        Actualiza métricas en tiempo real durante la conversación.
        
        Args:
            conversation_id: ID de la conversación
            message: Mensaje procesado
            response_time_seconds: Tiempo de respuesta del agente
            additional_metrics: Métricas adicionales específicas
        """
        try:
            if conversation_id not in self.tracked_conversations:
                logger.warning(f"Conversation {conversation_id} not being tracked")
                return
            
            tracking_data = self.tracked_conversations[conversation_id]
            current_time = datetime.now()
            
            # Registrar mensaje
            tracking_data["messages_log"].append({
                "message_id": message.id,
                "role": message.role,
                "content": message.content,
                "timestamp": message.timestamp,
                "response_time": response_time_seconds
            })
            
            # Detectar estrategias usadas en este mensaje
            if message.role == "assistant":
                strategies = self._detect_strategies_in_message(message.content)
                tracking_data["strategies_detected"].update(strategies)
            
            # Calcular métricas actualizadas
            updated_metrics = self._calculate_real_time_metrics(
                tracking_data, message, additional_metrics or {}
            )
            tracking_data["real_time_metrics"] = updated_metrics
            
            # Añadir snapshot de métricas
            tracking_data["metrics_history"].append({
                "timestamp": current_time,
                "metrics": updated_metrics.copy(),
                "message_count": len(tracking_data["messages_log"])
            })
            
            # Log para debugging (nivel DEBUG)
            logger.debug(
                f"Updated metrics for {conversation_id}: "
                f"engagement={updated_metrics['engagement_score']:.2f}, "
                f"conversion_prob={updated_metrics['conversion_probability']:.2f}"
            )
            
        except Exception as e:
            logger.error(f"Error updating conversation metrics: {str(e)}")
    
    def _detect_strategies_in_message(self, message_content: str) -> List[str]:
        """Detecta estrategias utilizadas en un mensaje."""
        detected_strategies = []
        message_lower = message_content.lower()
        
        for strategy, patterns in self.strategy_detection_patterns.items():
            if any(pattern in message_lower for pattern in patterns):
                detected_strategies.append(strategy)
        
        return detected_strategies
    
    def _calculate_real_time_metrics(
        self,
        tracking_data: Dict,
        latest_message: Message,
        additional_metrics: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calcula métricas en tiempo real basadas en la conversación actual."""
        try:
            messages = tracking_data["messages_log"]
            user_messages = [m for m in messages if m["role"] == "user"]
            agent_messages = [m for m in messages if m["role"] == "assistant"]
            
            # Calcular engagement score basado en longitud y frecuencia de mensajes
            if user_messages:
                avg_user_message_length = sum(len(m["content"]) for m in user_messages) / len(user_messages)
                engagement_base = min(10.0, avg_user_message_length / 20.0)  # Base score
                
                # Boost por preguntas del usuario
                questions_count = sum(1 for m in user_messages if "?" in m["content"])
                question_boost = min(2.0, questions_count * 0.5)
                
                engagement_score = min(10.0, engagement_base + question_boost)
            else:
                engagement_score = 5.0
            
            # Calcular probabilidad de conversión basada en varios factores
            conversion_factors = []
            
            # Factor 1: Engagement alto
            if engagement_score >= 7.0:
                conversion_factors.append(0.2)
            
            # Factor 2: Uso de estrategias efectivas
            effective_strategies = ["consultative_approach", "hie_emphasis", "empathy_techniques"]
            strategy_score = sum(0.1 for strategy in effective_strategies 
                               if strategy in tracking_data["strategies_detected"])
            conversion_factors.append(strategy_score)
            
            # Factor 3: Longitud de conversación apropiada
            if len(messages) >= 6:  # Conversación sustancial
                conversion_factors.append(0.15)
            
            # Factor 4: Respuestas rápidas del agente
            if agent_messages:
                avg_response_time = sum(m.get("response_time", 3.0) for m in agent_messages) / len(agent_messages)
                if avg_response_time <= 2.0:
                    conversion_factors.append(0.1)
            
            # Factor 5: Métricas adicionales
            if additional_metrics.get("emotional_intelligence_score", 0) > 0.7:
                conversion_factors.append(0.1)
                
            conversion_probability = min(1.0, 0.3 + sum(conversion_factors))
            
            # Calcular estabilidad emocional (simplicado por ahora)
            emotional_stability = additional_metrics.get("emotional_stability", 0.7)
            
            # Calcular calidad de respuesta basada en estrategias usadas
            response_quality = min(1.0, 0.5 + len(tracking_data["strategies_detected"]) * 0.1)
            
            return {
                "engagement_score": round(engagement_score, 2),
                "conversion_probability": round(conversion_probability, 2),
                "emotional_stability": round(emotional_stability, 2),
                "response_quality": round(response_quality, 2)
            }
            
        except Exception as e:
            logger.error(f"Error calculating real-time metrics: {str(e)}")
            return {
                "engagement_score": 5.0,
                "conversion_probability": 0.5,
                "emotional_stability": 0.7,
                "response_quality": 0.7
            }
    
    async def record_conversation_outcome(
        self,
        conversation_id: str,
        final_outcome: str,
        tier_recommended: str,
        tier_accepted: Optional[str] = None,
        satisfaction_score: Optional[float] = None,
        additional_context: Dict[str, Any] = None
    ) -> ConversationOutcomeRecord:
        """
        Registra el outcome final de una conversación para ML.
        
        Args:
            conversation_id: ID de la conversación
            final_outcome: Resultado final (converted, lost, etc.)
            tier_recommended: Tier recomendado por el agente
            tier_accepted: Tier finalmente aceptado por el cliente
            satisfaction_score: Score de satisfacción del cliente
            additional_context: Contexto adicional relevante
            
        Returns:
            ConversationOutcomeRecord creado
        """
        try:
            if conversation_id not in self.tracked_conversations:
                logger.error(f"Cannot record outcome for untracked conversation {conversation_id}")
                return None
            
            tracking_data = self.tracked_conversations[conversation_id]
            end_time = datetime.now()
            duration = (end_time - tracking_data["start_time"]).total_seconds()
            
            # Construir métricas finales
            messages = tracking_data["messages_log"]
            user_messages = [m for m in messages if m["role"] == "user"]
            agent_messages = [m for m in messages if m["role"] == "assistant"]
            
            # Calcular métricas detalladas
            metrics = ConversationMetrics(
                total_duration_seconds=int(duration),
                user_messages_count=len(user_messages),
                agent_messages_count=len(agent_messages),
                average_response_time_seconds=self._calculate_avg_response_time(agent_messages),
                engagement_score=tracking_data["real_time_metrics"]["engagement_score"],
                satisfaction_score=satisfaction_score,
                emotional_journey_stability=tracking_data["real_time_metrics"]["emotional_stability"],
                conversion_probability=tracking_data["real_time_metrics"]["conversion_probability"],
                tier_recommended=tier_recommended,
                final_tier_accepted=tier_accepted,
                objections_count=self._count_objections(user_messages),
                objections_resolved_count=self._count_resolved_objections(tracking_data),
                questions_asked_by_user=sum(1 for m in user_messages if "?" in m["content"]),
                early_adopter_presented="early_adopter_presentation" in tracking_data["strategies_detected"],
                early_adopter_accepted=tier_accepted is not None and additional_context and additional_context.get("early_adopter_accepted", False),
                hie_explanation_effectiveness=self._calculate_hie_effectiveness(tracking_data)
            )
            
            # Identificar factores de éxito/fracaso
            success_factors, failure_factors = self._analyze_success_failure_factors(
                tracking_data, final_outcome, metrics
            )
            
            # Crear record de outcome
            outcome_record = ConversationOutcomeRecord(
                conversation_id=conversation_id,
                client_archetype=self._determine_client_archetype(tracking_data["client_data"]),
                client_demographic_data=tracking_data["client_data"],
                initial_intent=additional_context.get("initial_intent", "information_seeking"),
                strategies_used=list(tracking_data["strategies_detected"]),
                prompts_used=self._extract_prompts_used(agent_messages),
                experiment_assignments=tracking_data["experiment_assignments"],
                outcome=ConversationOutcome(final_outcome),
                metrics=metrics,
                success_factors=success_factors,
                failure_factors=failure_factors,
                learning_insights=self._generate_learning_insights(tracking_data, final_outcome)
            )
            
            # Guardar en base de datos
            await self._save_outcome_to_database(outcome_record)
            
            # Limpiar del cache
            del self.tracked_conversations[conversation_id]
            
            logger.info(
                f"Recorded outcome for conversation {conversation_id}: "
                f"{final_outcome} (engagement: {metrics.engagement_score}, "
                f"conversion_prob: {metrics.conversion_probability})"
            )
            
            return outcome_record
            
        except Exception as e:
            logger.error(f"Error recording conversation outcome: {str(e)}")
            return None
    
    def _calculate_avg_response_time(self, agent_messages: List[Dict]) -> float:
        """Calcula tiempo promedio de respuesta del agente."""
        if not agent_messages:
            return 0.0
        
        response_times = [m.get("response_time", 2.0) for m in agent_messages]
        return sum(response_times) / len(response_times)
    
    def _count_objections(self, user_messages: List[Dict]) -> int:
        """Cuenta objeciones en mensajes del usuario."""
        objection_indicators = [
            "pero", "sin embargo", "no estoy seguro", "es muy caro",
            "no tengo tiempo", "no funciona", "no creo"
        ]
        
        objections = 0
        for message in user_messages:
            content_lower = message["content"].lower()
            if any(indicator in content_lower for indicator in objection_indicators):
                objections += 1
        
        return objections
    
    def _count_resolved_objections(self, tracking_data: Dict) -> int:
        """Cuenta objeciones aparentemente resueltas."""
        # Simplificado: si usamos objection_handling y la conversación continúa
        if "objection_handling" in tracking_data["strategies_detected"]:
            return min(self._count_objections([m for m in tracking_data["messages_log"] if m["role"] == "user"]), 
                      len([m for m in tracking_data["messages_log"] if m["role"] == "assistant"]) // 2)
        return 0
    
    def _calculate_hie_effectiveness(self, tracking_data: Dict) -> float:
        """Calcula efectividad de la explicación HIE."""
        if "hie_emphasis" not in tracking_data["strategies_detected"]:
            return 0.0
        
        # Simplificado: basado en engagement después de mencionar HIE
        hie_mentions = 0
        post_hie_engagement = []
        
        for i, message in enumerate(tracking_data["messages_log"]):
            if message["role"] == "assistant" and any(
                term in message["content"].lower() 
                for term in ["hie", "hybrid intelligence", "11 agentes"]
            ):
                hie_mentions += 1
                # Medir engagement en los próximos mensajes del usuario
                for j in range(i+1, min(i+3, len(tracking_data["messages_log"]))):
                    if tracking_data["messages_log"][j]["role"] == "user":
                        msg_engagement = len(tracking_data["messages_log"][j]["content"]) / 100.0
                        post_hie_engagement.append(min(1.0, msg_engagement))
        
        if not post_hie_engagement:
            return 0.5  # Neutral si no hay datos
        
        return sum(post_hie_engagement) / len(post_hie_engagement)
    
    def _determine_client_archetype(self, client_data: Dict[str, Any]) -> str:
        """Determina arquetipo del cliente basado en datos disponibles."""
        age = client_data.get("age", 35)
        occupation = client_data.get("occupation", "").lower()
        
        if "ceo" in occupation or "director" in occupation or "gerente" in occupation:
            return "executive_performer"
        elif age < 45:
            return "performance_optimizer"
        elif age >= 50:
            return "longevity_seeker"
        else:
            return "health_conscious"
    
    def _extract_prompts_used(self, agent_messages: List[Dict]) -> List[Dict[str, Any]]:
        """Extrae información de prompts usados."""
        prompts = []
        for message in agent_messages:
            # Simplificado: extraer primer párrafo como "prompt usado"
            content = message["content"]
            first_sentence = content.split('.')[0] if '.' in content else content[:100]
            
            prompts.append({
                "timestamp": message["timestamp"],
                "prompt_type": "conversational",
                "content_preview": first_sentence,
                "full_length": len(content)
            })
        
        return prompts
    
    def _analyze_success_failure_factors(
        self, 
        tracking_data: Dict, 
        outcome: str, 
        metrics: ConversationMetrics
    ) -> Tuple[List[str], List[str]]:
        """Analiza factores que contribuyeron al éxito o fracaso."""
        success_factors = []
        failure_factors = []
        
        # Analizar basado en outcome
        if outcome == "converted":
            if metrics.engagement_score >= 7.0:
                success_factors.append("high_engagement_achieved")
            if "consultative_approach" in tracking_data["strategies_detected"]:
                success_factors.append("consultative_selling_used")
            if "hie_emphasis" in tracking_data["strategies_detected"]:
                success_factors.append("hie_differentiation_effective")
            if metrics.objections_resolved_count > 0:
                success_factors.append("objections_handled_well")
                
        elif outcome == "lost":
            if metrics.engagement_score < 4.0:
                failure_factors.append("low_engagement")
            if metrics.objections_count > metrics.objections_resolved_count:
                failure_factors.append("unresolved_objections")
            if metrics.total_duration_seconds < 180:  # < 3 minutos
                failure_factors.append("conversation_too_short")
            if len(tracking_data["strategies_detected"]) < 2:
                failure_factors.append("limited_strategies_used")
        
        return success_factors, failure_factors
    
    def _generate_learning_insights(self, tracking_data: Dict, outcome: str) -> Dict[str, Any]:
        """Genera insights para el sistema de aprendizaje."""
        return {
            "optimal_conversation_length": len(tracking_data["messages_log"]),
            "most_effective_strategy": max(tracking_data["strategies_detected"], 
                                         default="none") if tracking_data["strategies_detected"] else "none",
            "engagement_progression": [h["metrics"]["engagement_score"] 
                                     for h in tracking_data["metrics_history"]],
            "conversion_probability_progression": [h["metrics"]["conversion_probability"] 
                                                 for h in tracking_data["metrics_history"]],
            "key_turning_points": self._identify_turning_points(tracking_data["metrics_history"]),
            "recommended_improvements": self._suggest_improvements(tracking_data, outcome)
        }
    
    def _identify_turning_points(self, metrics_history: List[Dict]) -> List[Dict]:
        """Identifica puntos de inflexión en la conversación."""
        turning_points = []
        
        if len(metrics_history) < 3:
            return turning_points
        
        for i in range(1, len(metrics_history) - 1):
            current = metrics_history[i]["metrics"]["engagement_score"]
            previous = metrics_history[i-1]["metrics"]["engagement_score"]
            next_val = metrics_history[i+1]["metrics"]["engagement_score"]
            
            # Detectar picos o caídas significativas
            if abs(current - previous) > 1.5 or abs(next_val - current) > 1.5:
                turning_points.append({
                    "timestamp": metrics_history[i]["timestamp"],
                    "type": "engagement_change",
                    "magnitude": current - previous,
                    "message_number": metrics_history[i]["message_count"]
                })
        
        return turning_points
    
    def _suggest_improvements(self, tracking_data: Dict, outcome: str) -> List[str]:
        """Sugiere mejoras basadas en el análisis de la conversación."""
        suggestions = []
        
        if outcome != "converted":
            if "consultative_approach" not in tracking_data["strategies_detected"]:
                suggestions.append("use_more_consultative_approach")
            
            if "empathy_techniques" not in tracking_data["strategies_detected"]:
                suggestions.append("incorporate_empathy_techniques")
            
            if len(tracking_data["messages_log"]) < 6:
                suggestions.append("extend_conversation_length")
            
            if "hie_emphasis" not in tracking_data["strategies_detected"]:
                suggestions.append("emphasize_hie_differentiation")
        
        return suggestions
    
    async def _save_outcome_to_database(self, outcome_record: ConversationOutcomeRecord) -> None:
        """Guarda el record de outcome en la base de datos."""
        try:
            # Convertir el record a formato de base de datos
            db_data = {
                "outcome_id": outcome_record.outcome_id,
                "conversation_id": outcome_record.conversation_id,
                "client_archetype": outcome_record.client_archetype,
                "client_demographic_data": outcome_record.client_demographic_data,
                "initial_intent": outcome_record.initial_intent,
                "strategies_used": outcome_record.strategies_used,
                "prompts_used": outcome_record.prompts_used,
                "experiment_assignments": outcome_record.experiment_assignments,
                "outcome": outcome_record.outcome.value,
                
                # Métricas individuales (flat structure para DB)
                "total_duration_seconds": outcome_record.metrics.total_duration_seconds,
                "user_messages_count": outcome_record.metrics.user_messages_count,
                "agent_messages_count": outcome_record.metrics.agent_messages_count,
                "average_response_time_seconds": outcome_record.metrics.average_response_time_seconds,
                "engagement_score": outcome_record.metrics.engagement_score,
                "satisfaction_score": outcome_record.metrics.satisfaction_score,
                "emotional_journey_stability": outcome_record.metrics.emotional_journey_stability,
                "conversion_probability": outcome_record.metrics.conversion_probability,
                "tier_recommended": outcome_record.metrics.tier_recommended,
                "final_tier_accepted": outcome_record.metrics.final_tier_accepted,
                "objections_count": outcome_record.metrics.objections_count,
                "objections_resolved_count": outcome_record.metrics.objections_resolved_count,
                "questions_asked_by_user": outcome_record.metrics.questions_asked_by_user,
                "early_adopter_presented": outcome_record.metrics.early_adopter_presented,
                "early_adopter_accepted": outcome_record.metrics.early_adopter_accepted,
                "hie_explanation_effectiveness": outcome_record.metrics.hie_explanation_effectiveness,
                
                "success_factors": outcome_record.success_factors,
                "failure_factors": outcome_record.failure_factors,
                "learning_insights": outcome_record.learning_insights,
                "recorded_at": outcome_record.recorded_at.isoformat(),
                "agent_version": outcome_record.agent_version
            }
            
            # Insertar en Supabase
            result = supabase_client.table("conversation_outcomes").insert(db_data).execute()
            
            if hasattr(result, 'error') and result.error:
                logger.error(f"Database error saving outcome: {result.error}")
            else:
                logger.debug(f"Successfully saved outcome record for conversation {outcome_record.conversation_id}")
                
        except Exception as e:
            logger.error(f"Error saving outcome to database: {str(e)}")
    
    def get_conversation_summary(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene resumen de una conversación siendo tracked."""
        if conversation_id not in self.tracked_conversations:
            return None
        
        tracking_data = self.tracked_conversations[conversation_id]
        return {
            "conversation_id": conversation_id,
            "duration": (datetime.now() - tracking_data["start_time"]).total_seconds(),
            "message_count": len(tracking_data["messages_log"]),
            "strategies_detected": list(tracking_data["strategies_detected"]),
            "current_metrics": tracking_data["real_time_metrics"],
            "experiment_assignments": tracking_data["experiment_assignments"]
        }