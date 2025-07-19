"""
Servicio de Motor de Decisiones para NGX Voice Sales Agent.

Este servicio se encarga de optimizar el flujo de conversación,
crear árboles de decisión dinámicos, adaptar respuestas en tiempo real
y priorizar objetivos durante interacciones con clientes.
"""

from typing import Dict, List, Any, Optional, Tuple, Set
import logging
import json
import uuid
import asyncio
from datetime import datetime
import random

from src.integrations.supabase.resilient_client import ResilientSupabaseClient
from src.services.base_predictive_service import BasePredictiveService
from src.services.predictive_model_service import PredictiveModelService
from src.services.nlp_integration_service import NLPIntegrationService
from src.services.objection_prediction_service import ObjectionPredictionService
from src.services.needs_prediction_service import NeedsPredictionService
from src.services.conversion_prediction_service import ConversionPredictionService

logger = logging.getLogger(__name__)

class DecisionEngineService(BasePredictiveService):
    """
    Servicio para optimizar el flujo de conversación y toma de decisiones.
    
    Características principales:
    - Optimización de flujo de conversación
    - Árboles de decisión dinámicos
    - Adaptación en tiempo real
    - Priorización de objetivos
    """
    
    def __init__(self, 
                 supabase: ResilientSupabaseClient,
                 predictive_model_service: PredictiveModelService,
                 nlp_integration_service: NLPIntegrationService,
                 objection_prediction_service: ObjectionPredictionService,
                 needs_prediction_service: NeedsPredictionService,
                 conversion_prediction_service: ConversionPredictionService):
        """
        Inicializa el servicio de motor de decisiones.
        
        Args:
            supabase: Cliente de Supabase para persistencia
            predictive_model_service: Servicio base para modelos predictivos
            nlp_integration_service: Servicio de integración NLP
            objection_prediction_service: Servicio de predicción de objeciones
            needs_prediction_service: Servicio de predicción de necesidades
            conversion_prediction_service: Servicio de predicción de conversión
        """
        super().__init__(
            supabase=supabase,
            predictive_model_service=predictive_model_service,
            nlp_integration_service=nlp_integration_service,
            model_name="decision_engine_model",
            model_type="decision_engine"
        )
        self.objection_service = objection_prediction_service
        self.needs_service = needs_prediction_service
        self.conversion_service = conversion_prediction_service
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
        Inicializa el modelo del motor de decisiones.
        """
        model_params = {
            "objective_weights": {
                "need_satisfaction": 0.35,
                "objection_handling": 0.25,
                "conversion_progress": 0.4
            },
            "exploration_rate": 0.2,  # Tasa de exploración para nuevas rutas
            "adaptation_threshold": 0.3,  # Umbral para adaptación de estrategia
            "max_tree_depth": 5,  # Profundidad máxima de árboles de decisión
            "min_confidence": 0.6,  # Confianza mínima para tomar decisiones
            "context_window": 15  # Número de mensajes a considerar para contexto
        }
        
        await self.initialize_model(
            model_params=model_params,
            description="Modelo para motor de decisiones y optimización de flujo"
        )
    
    async def optimize_conversation_flow(self, conversation_id: str, 
                                   messages: List[Dict[str, Any]],
                                   customer_profile: Optional[Dict[str, Any]] = None,
                                   current_objectives: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Optimiza el flujo de conversación basado en predicciones y objetivos.
        
        Args:
            conversation_id: ID de la conversación
            messages: Lista de mensajes de la conversación
            customer_profile: Perfil del cliente (opcional)
            current_objectives: Objetivos actuales con pesos (opcional)
            
        Returns:
            Estrategia optimizada con acciones recomendadas
        """
        try:
            await self.initialize()
            if not messages:
                return {
                    "next_actions": [],
                    "confidence": 0,
                    "decision_tree": {}
                }
            
            # Obtener parámetros del modelo
            model_params = await self.get_model_parameters()
            min_confidence = model_params.get("min_confidence", 0.6)
            
            # Obtener objetivos predeterminados si no se proporcionan
            objective_weights = current_objectives or model_params.get("objective_weights", {
                "need_satisfaction": 0.35,
                "objection_handling": 0.25,
                "conversion_progress": 0.4
            })
            
            # Obtener predicciones de otros servicios en paralelo para mejorar rendimiento
            objection_task = self.objection_service.predict_objections(
                conversation_id=conversation_id,
                messages=messages,
                customer_profile=customer_profile
            )
            
            needs_task = self.needs_service.predict_needs(
                conversation_id=conversation_id,
                messages=messages,
                customer_profile=customer_profile
            )
            
            conversion_task = self.conversion_service.predict_conversion(
                conversation_id=conversation_id,
                messages=messages,
                customer_profile=customer_profile
            )
            
            # Esperar a que todas las predicciones se completen
            objection_prediction, needs_prediction, conversion_prediction = await asyncio.gather(
                objection_task, needs_task, conversion_task
            )
            
            # Generar árbol de decisión
            decision_tree = await self._generate_decision_tree(
                objection_prediction=objection_prediction,
                needs_prediction=needs_prediction,
                conversion_prediction=conversion_prediction,
                objective_weights=objective_weights,
                customer_profile=customer_profile
            )
            
            # Determinar próximas acciones
            next_actions = await self._determine_next_actions(
                decision_tree=decision_tree,
                objective_weights=objective_weights,
                min_confidence=min_confidence
            )
            
            # Calcular confianza general
            confidence = sum([action.get("confidence", 0) for action in next_actions]) / max(1, len(next_actions))
            
            # Crear resultado de optimización
            optimization_result = {
                "next_actions": next_actions,
                "confidence": confidence,
                "decision_tree": decision_tree,
                "timestamp": datetime.now().isoformat()
            }
            
            # Guardar predicción en base de datos usando la clase base
            await self.store_prediction(
                conversation_id=conversation_id,
                prediction_type="flow_optimization",
                prediction_data=optimization_result,
                confidence=confidence
            )
            
            return optimization_result
            
        except Exception as e:
            logger.error(f"Error al optimizar flujo de conversación: {e}")
            return {
                "next_actions": [],
                "confidence": 0,
                "decision_tree": {},
                "error": str(e)
            }
    
    async def _generate_decision_tree(self, 
                                objection_prediction: Dict[str, Any],
                                needs_prediction: Dict[str, Any],
                                conversion_prediction: Dict[str, Any],
                                objective_weights: Dict[str, float],
                                customer_profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Genera un árbol de decisión dinámico basado en predicciones.
        
        Args:
            objection_prediction: Predicción de objeciones
            needs_prediction: Predicción de necesidades
            conversion_prediction: Predicción de conversión
            objective_weights: Pesos de objetivos
            customer_profile: Perfil del cliente (opcional)
            
        Returns:
            Árbol de decisión con rutas y puntuaciones
        """
        # Crear nodo raíz
        root_node = {
            "id": str(uuid.uuid4()),
            "type": "root",
            "description": "Punto de inicio de decisión",
            "children": []
        }
        
        # Extraer predicciones principales
        objections = objection_prediction.get("objections", [])
        needs = needs_prediction.get("needs", [])
        conversion_category = conversion_prediction.get("category", "low")
        conversion_recommendations = conversion_prediction.get("recommendations", [])
        
        # 1. Rama para manejo de objeciones (si hay objeciones con alta confianza)
        if objections and objections[0].get("confidence", 0) > 0.7:
            top_objection = objections[0]
            objection_node = {
                "id": str(uuid.uuid4()),
                "type": "objection_handling",
                "description": f"Manejar objeción: {top_objection.get('type', 'desconocida')}",
                "confidence": top_objection.get("confidence", 0),
                "data": top_objection,
                "children": []
            }
            
            # Añadir respuestas sugeridas como nodos hijos
            for i, response in enumerate(top_objection.get("suggested_responses", [])):
                response_node = {
                    "id": str(uuid.uuid4()),
                    "type": "response",
                    "description": f"Respuesta {i+1}",
                    "content": response,
                    "score": 0.9 - (i * 0.1)  # Puntuar respuestas en orden decreciente
                }
                objection_node["children"].append(response_node)
            
            root_node["children"].append(objection_node)
        
        # 2. Rama para satisfacción de necesidades
        if needs:
            for need in needs[:2]:  # Considerar las 2 necesidades principales
                need_node = {
                    "id": str(uuid.uuid4()),
                    "type": "need_satisfaction",
                    "description": f"Satisfacer necesidad: {need.get('category', 'desconocida')}",
                    "confidence": need.get("confidence", 0),
                    "data": need,
                    "children": []
                }
                
                # Añadir acciones sugeridas como nodos hijos
                for i, action in enumerate(need.get("suggested_actions", [])[:3]):
                    action_node = {
                        "id": str(uuid.uuid4()),
                        "type": "action",
                        "description": action.get("action", ""),
                        "action_type": action.get("type", ""),
                        "priority": action.get("priority", "medium"),
                        "score": 0.9 - (i * 0.15)  # Puntuar acciones en orden decreciente
                    }
                    need_node["children"].append(action_node)
                
                root_node["children"].append(need_node)
        
        # 3. Rama para progresión de conversión
        conversion_node = {
            "id": str(uuid.uuid4()),
            "type": "conversion_progression",
            "description": f"Progresión de conversión: {conversion_category}",
            "confidence": conversion_prediction.get("confidence", 0),
            "data": {
                "probability": conversion_prediction.get("probability", 0),
                "category": conversion_category
            },
            "children": []
        }
        
        # Añadir recomendaciones de conversión como nodos hijos
        for i, recommendation in enumerate(conversion_recommendations[:3]):
            recommendation_node = {
                "id": str(uuid.uuid4()),
                "type": "recommendation",
                "description": recommendation.get("action", ""),
                "recommendation_type": recommendation.get("type", ""),
                "priority": recommendation.get("priority", "medium"),
                "score": 0.9 - (i * 0.15)  # Puntuar recomendaciones en orden decreciente
            }
            conversion_node["children"].append(recommendation_node)
        
        root_node["children"].append(conversion_node)
        
        # 4. Añadir nodo de exploración (para descubrir nuevas rutas)
        exploration_node = {
            "id": str(uuid.uuid4()),
            "type": "exploration",
            "description": "Explorar nuevas direcciones de conversación",
            "confidence": 0.6,
            "children": []
        }
        
        # Añadir algunas acciones exploratorias
        exploration_actions = [
            "Preguntar sobre objetivos a largo plazo",
            "Indagar sobre experiencias previas con soluciones similares",
            "Explorar nuevos casos de uso potenciales",
            "Preguntar sobre otros stakeholders involucrados en la decisión"
        ]
        
        for i, action in enumerate(exploration_actions):
            action_node = {
                "id": str(uuid.uuid4()),
                "type": "exploration_action",
                "description": action,
                "score": 0.7 - (i * 0.1)
            }
            exploration_node["children"].append(action_node)
        
        root_node["children"].append(exploration_node)
        
        # Calcular puntuaciones para cada rama basado en objetivos
        self._score_decision_tree(root_node, objective_weights)
        
        return root_node
    
    def _score_decision_tree(self, node: Dict[str, Any], objective_weights: Dict[str, float]) -> float:
        """
        Asigna puntuaciones a los nodos del árbol de decisión.
        
        Args:
            node: Nodo a puntuar
            objective_weights: Pesos de objetivos
            
        Returns:
            Puntuación del nodo
        """
        # Puntuación base según tipo de nodo
        base_score = 0.5
        
        # Ajustar puntuación según tipo y objetivos
        if node["type"] == "objection_handling":
            base_score = objective_weights.get("objection_handling", 0.25) * node.get("confidence", 0.5)
        elif node["type"] == "need_satisfaction":
            base_score = objective_weights.get("need_satisfaction", 0.35) * node.get("confidence", 0.5)
        elif node["type"] == "conversion_progression":
            # Ajustar según categoría de conversión
            conversion_category = node.get("data", {}).get("category", "low")
            category_multiplier = {
                "low": 0.6,
                "medium": 0.8,
                "high": 1.0,
                "very_high": 1.2
            }
            base_score = objective_weights.get("conversion_progress", 0.4) * node.get("confidence", 0.5) * category_multiplier.get(conversion_category, 0.8)
        elif node["type"] == "exploration":
            # Puntuación de exploración es fija pero baja
            base_score = 0.3
        
        # Recursivamente puntuar hijos
        if "children" in node and node["children"]:
            child_scores = []
            
            for child in node["children"]:
                # Para nodos hoja, usar score existente o asignar uno
                if "children" not in child or not child["children"]:
                    if "score" not in child:
                        child["score"] = 0.5
                    child_scores.append(child["score"])
                else:
                    # Para nodos internos, calcular recursivamente
                    child_score = self._score_decision_tree(child, objective_weights)
                    child["score"] = child_score
                    child_scores.append(child_score)
            
            # La puntuación del nodo es su base más el promedio de sus mejores hijos
            if child_scores:
                child_scores.sort(reverse=True)
                top_children = child_scores[:min(2, len(child_scores))]
                avg_top_children = sum(top_children) / len(top_children) if top_children else 0
                node["score"] = (base_score * 0.7) + (avg_top_children * 0.3)
            else:
                node["score"] = base_score
        else:
            node["score"] = base_score
        
        return node["score"]
    
    async def _determine_next_actions(self, decision_tree: Dict[str, Any],
                                objective_weights: Dict[str, float],
                                min_confidence: float) -> List[Dict[str, Any]]:
        """
        Determina las próximas acciones óptimas basadas en el árbol de decisión.
        
        Args:
            decision_tree: Árbol de decisión generado
            objective_weights: Pesos de objetivos
            min_confidence: Confianza mínima para tomar decisiones
            
        Returns:
            Lista de acciones recomendadas
        """
        try:
            # Extraer todos los nodos de acción del árbol
            action_nodes = await self._extract_action_nodes(decision_tree)
            
            if not action_nodes:
                return []
            
            # Filtrar acciones por confianza mínima
            filtered_actions = [node for node in action_nodes if node.get("confidence", 0) >= min_confidence]
            
            if not filtered_actions:
                # Si no hay acciones con confianza suficiente, tomar las mejores 3
                sorted_actions = sorted(action_nodes, key=lambda x: x.get("score", 0), reverse=True)
                filtered_actions = sorted_actions[:3]
                
                # Si aún así no hay acciones, añadir acciones de exploración
                if not filtered_actions:
                    exploration_actions = [
                        {
                            "type": "exploration",
                            "action": "explore_needs",
                            "description": "Preguntar sobre objetivos específicos del cliente",
                            "priority": "high",
                            "confidence": 0.7,
                            "score": 0.7,
                            "related_to": {"objective": "need_satisfaction"}
                        },
                        {
                            "type": "exploration",
                            "action": "explore_decision_process",
                            "description": "Indagar sobre el proceso de toma de decisiones",
                            "priority": "medium",
                            "confidence": 0.6,
                            "score": 0.6,
                            "related_to": {"objective": "conversion_progress"}
                        },
                        {
                            "type": "exploration",
                            "action": "explore_challenges",
                            "description": "Explorar desafíos actuales que enfrenta el cliente",
                            "priority": "medium",
                            "confidence": 0.6,
                            "score": 0.6,
                            "related_to": {"objective": "objection_handling"}
                        }
                    ]
                    return exploration_actions
            
            # Ordenar por puntuación
            sorted_actions = sorted(filtered_actions, key=lambda x: x.get("score", 0), reverse=True)
            
            # Limitar a las 5 mejores acciones
            top_actions = sorted_actions[:5]
            
            # Preparar resultado
            result = []
            for action in top_actions:
                result.append({
                    "type": action.get("type", ""),
                    "action": action.get("action", ""),
                    "description": action.get("description", ""),
                    "priority": action.get("priority", "medium"),
                    "confidence": action.get("confidence", 0),
                    "score": action.get("score", 0),
                    "related_to": action.get("related_to", {})
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error al determinar próximas acciones: {e}")
            return []
            
            random_action = random.choice(exploration_actions)
            
            next_actions.append({
                "id": str(uuid.uuid4()),
                "type": "exploration_action",
                "action_category": "exploration",
                "description": random_action,
                "content": random_action,
                "score": 0.5,
                "priority": "medium"
            })
        
        return next_actions, confidence
    
    async def _extract_action_nodes(self, node: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extrae todos los nodos de acción de un árbol de decisión.
        
        Args:
            node: Nodo raíz o subnodo del árbol
            
        Returns:
            Lista de nodos de acción
        """
        try:
            action_nodes = []
            
            # Si el nodo actual es un nodo de acción, añadirlo
            if node.get("type") in ["action", "response", "recommendation", "exploration"]:
                action_nodes.append(node)
            
            # Procesar nodos hijos recursivamente
            children = node.get("children", [])
            for child in children:
                child_nodes = await self._extract_action_nodes(child)
                action_nodes.extend(child_nodes)
            
            return action_nodes
        except Exception as e:
            logger.error(f"Error al extraer nodos de acción: {e}")
            return []
    
    async def adapt_strategy_realtime(self, conversation_id: str, 
                                  messages: List[Dict[str, Any]],
                                  feedback: Dict[str, Any],
                                  customer_profile: Optional[Dict[str, Any]] = None,
                                  current_objectives: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Adapta la estrategia en tiempo real basándose en feedback del usuario.
        
        Args:
            conversation_id: ID de la conversación
            messages: Lista de mensajes de la conversación
            feedback: Feedback del usuario sobre la conversación
            customer_profile: Perfil del cliente (opcional)
            current_objectives: Objetivos actuales (opcional)
            
        Returns:
            Estrategia adaptada con nuevos objetivos y acciones recomendadas
        """
        try:
            if not messages or not feedback:
                return {
                    "adjusted_objectives": current_objectives or {},
                    "next_actions": []
                }
            
            # Extraer información del feedback
            feedback_type = feedback.get("type", "")
            feedback_value = feedback.get("value", 0)
            feedback_details = feedback.get("details", {})
            
            # Inicializar objetivos si no se proporcionan
            if not current_objectives:
                current_objectives = {
                    "conversion": 0.5,
                    "satisfaction": 0.3,
                    "efficiency": 0.2
                }
            
            # Ajustar objetivos basados en feedback
            adjusted_objectives = current_objectives.copy()
            
            if feedback_type == "satisfaction":
                # Si el cliente está insatisfecho, aumentar prioridad de satisfacción
                if feedback_value < 0.5:
                    adjusted_objectives["satisfaction"] = min(1.0, adjusted_objectives.get("satisfaction", 0) + 0.2)
                    adjusted_objectives["conversion"] = max(0.1, adjusted_objectives.get("conversion", 0) - 0.1)
                
            elif feedback_type == "objection":
                # Si hay objeciones, enfocarse en abordarlas
                objection_type = feedback_details.get("objection_type", "")
                
                # Obtener predicción de objeciones
                objection_prediction = await self.objection_service.predict_objections(
                    conversation_id=conversation_id,
                    messages=messages,
                    customer_profile=customer_profile
                )
                
                # Buscar estrategias para la objeción específica
                objections = objection_prediction.get("objections", [])
                target_objection = None
                
                for obj in objections:
                    if obj.get("type") == objection_type:
                        target_objection = obj
                        break
                
                # Ajustar objetivos para enfocarse en resolver la objeción
                if target_objection:
                    adjusted_objectives["objection_handling"] = 0.4
                    adjusted_objectives["conversion"] = max(0.1, adjusted_objectives.get("conversion", 0) - 0.2)
                    adjusted_objectives["efficiency"] = max(0.1, adjusted_objectives.get("efficiency", 0) - 0.1)
            
            elif feedback_type == "interest":
                # Si muestra interés en un producto/servicio específico
                interest_category = feedback_details.get("category", "")
                interest_level = feedback_value
                
                if interest_level > 0.7:
                    # Alto interés, aumentar enfoque en conversión
                    adjusted_objectives["conversion"] = min(1.0, adjusted_objectives.get("conversion", 0) + 0.2)
                    adjusted_objectives["efficiency"] = max(0.1, adjusted_objectives.get("efficiency", 0) - 0.1)
            
            # Normalizar objetivos para que sumen 1.0
            total = sum(adjusted_objectives.values())
            if total > 0:
                for key in adjusted_objectives:
                    adjusted_objectives[key] = adjusted_objectives[key] / total
            
            # Obtener nueva estrategia con objetivos ajustados
            new_strategy = await self.optimize_conversation_flow(
                conversation_id=conversation_id,
                messages=messages,
                customer_profile=customer_profile,
                current_objectives=adjusted_objectives
            )
            
            # Registrar adaptación de estrategia usando la clase base
            adaptation_data = {
                "conversation_id": conversation_id,
                "feedback": feedback,
                "previous_objectives": current_objectives,
                "adjusted_objectives": adjusted_objectives,
                "next_actions": new_strategy.get("next_actions", []),
                "timestamp": datetime.now().isoformat()
            }
            
            # Usar el método de la clase base para almacenar la predicción
            await self.store_prediction(
                conversation_id=conversation_id,
                prediction_type="strategy_adaptation",
                prediction_data=adaptation_data,
                confidence=0.7  # Confianza moderada en la adaptación
            )
            
            # Registrar el feedback para análisis posterior y mejora del modelo
            await self.log_feedback(
                conversation_id=conversation_id,
                feedback_data={
                    "type": feedback_type,
                    "value": feedback_value,
                    "details": feedback_details,
                    "resulting_adaptation": adjusted_objectives
                }
            )
            
            return {
                "adjusted_objectives": adjusted_objectives,
                "next_actions": new_strategy.get("next_actions", [])
            }
            
        except Exception as e:
            logger.error(f"Error al adaptar estrategia en tiempo real: {e}")
            return {
                "adjusted_objectives": current_objectives or {},
                "next_actions": []
            }
    
    async def log_feedback(self, conversation_id: str, feedback_data: Dict[str, Any]) -> None:
        """
        Registra el feedback del usuario para análisis posterior y mejora del modelo.
        
        Args:
            conversation_id: ID de la conversación
            feedback_data: Datos del feedback recibido
        """
        try:
            # Enriquecer los datos de feedback con información adicional
            enriched_feedback = {
                **feedback_data,
                "timestamp": datetime.now().isoformat(),
                "model_name": self.model_name,
                "model_version": self.model_version
            }
            
            # Almacenar el feedback en la base de datos usando el cliente de Supabase
            await self.supabase.from_("feedback_logs")\
                .insert({
                    "conversation_id": conversation_id,
                    "model_name": self.model_name,
                    "feedback_type": feedback_data.get("type", "unknown"),
                    "feedback_value": feedback_data.get("value", 0),
                    "feedback_details": feedback_data.get("details", {}),
                    "resulting_adaptation": feedback_data.get("resulting_adaptation", {}),
                    "created_at": enriched_feedback["timestamp"]
                })\
                .execute()
            
            # Registrar el feedback en los logs para análisis
            logger.info(f"Feedback registrado para conversación {conversation_id}: {feedback_data}")
            
            # Actualizar métricas de feedback para el modelo
            await self._update_feedback_metrics(conversation_id, feedback_data)
            
        except Exception as e:
            logger.error(f"Error al registrar feedback: {e}")
    
    async def _update_feedback_metrics(self, conversation_id: str, feedback_data: Dict[str, Any]) -> None:
        """
        Actualiza las métricas internas basadas en el feedback recibido.
        
        Args:
            conversation_id: ID de la conversación
            feedback_data: Datos del feedback recibido
        """
        try:
            # Obtener métricas actuales del modelo
            model_metrics = await self.get_model_metrics()
            
            # Actualizar métricas según el tipo de feedback
            feedback_type = feedback_data.get("type", "")
            feedback_value = feedback_data.get("value", 0)
            
            if feedback_type == "satisfaction":
                # Actualizar promedio de satisfacción
                current_avg = model_metrics.get("avg_satisfaction", 0)
                current_count = model_metrics.get("satisfaction_count", 0)
                
                new_count = current_count + 1
                new_avg = ((current_avg * current_count) + feedback_value) / new_count
                
                model_metrics["avg_satisfaction"] = new_avg
                model_metrics["satisfaction_count"] = new_count
                
            elif feedback_type == "objection":
                # Incrementar contador de objeciones por tipo
                objection_type = feedback_data.get("details", {}).get("objection_type", "unknown")
                objection_counts = model_metrics.get("objection_counts", {})
                
                objection_counts[objection_type] = objection_counts.get(objection_type, 0) + 1
                model_metrics["objection_counts"] = objection_counts
            
            # Guardar métricas actualizadas
            await self._save_model_metrics(model_metrics)
            
        except Exception as e:
            logger.error(f"Error al actualizar métricas de feedback: {e}")
    
    async def _save_model_metrics(self, model_metrics: Dict[str, Any]) -> None:
        """
        Guarda las métricas actualizadas del modelo en la base de datos.
        
        Args:
            model_metrics: Métricas actualizadas del modelo
        """
        try:
            # Preparar datos para guardar
            metrics_data = {
                "model_name": self.model_name,
                "model_version": self.model_version,
                "metrics": model_metrics,
                "updated_at": datetime.now().isoformat()
            }
            
            # Verificar si ya existen métricas para este modelo
            result = await self.supabase_client.from_("model_metrics")\
                .select("*")\
                .eq("model_name", self.model_name)\
                .eq("model_version", self.model_version)\
                .execute()
            
            existing_metrics = result.data if hasattr(result, 'data') else []
            
            if existing_metrics:
                # Actualizar métricas existentes
                await self.supabase_client.from_("model_metrics")\
                    .update({"metrics": model_metrics, "updated_at": metrics_data["updated_at"]})\
                    .eq("model_name", self.model_name)\
                    .eq("model_version", self.model_version)\
                    .execute()
            else:
                # Insertar nuevas métricas
                await self.supabase_client.from_("model_metrics")\
                    .insert(metrics_data)\
                    .execute()
            
            logger.info(f"Métricas guardadas para modelo {self.model_name} v{self.model_version}")
            
        except Exception as e:
            logger.error(f"Error al guardar métricas del modelo: {e}")
    
    async def get_model_metrics(self) -> Dict[str, Any]:
        """
        Obtiene las métricas actuales del modelo desde la base de datos.
        
        Returns:
            Métricas actuales del modelo
        """
        try:
            # Obtener métricas de la base de datos
            result = await self.supabase_client.from_("model_metrics")\
                .select("*")\
                .eq("model_name", self.model_name)\
                .eq("model_version", self.model_version)\
                .execute()
            
            metrics_data = result.data[0] if hasattr(result, 'data') and result.data else {}
            
            if metrics_data and "metrics" in metrics_data:
                return metrics_data["metrics"]
            else:
                # Devolver métricas iniciales si no hay datos
                return {
                    "avg_satisfaction": 0,
                    "satisfaction_count": 0,
                    "objection_counts": {},
                    "conversion_rate": 0,
                    "conversion_count": 0,
                    "total_predictions": 0
                }
            
        except Exception as e:
            logger.error(f"Error al obtener métricas del modelo: {e}")
            return {}
    
    async def prioritize_objectives(self, conversation_id: str,
                               messages: List[Dict[str, Any]],
                               customer_profile: Optional[Dict[str, Any]] = None) -> Dict[str, float]:
        """
        Prioriza los objetivos del modelo según el contexto de la conversación.
        
        Args:
            conversation_id: ID de la conversación
            messages: Lista de mensajes de la conversación
            customer_profile: Perfil del cliente (opcional)
            
        Returns:
            Diccionario con objetivos priorizados y sus pesos
        """
        try:
            # Obtener parámetros del modelo usando el método de la clase base
            model_params = await self.get_model_parameters()
            if not model_params:
                default_weights = {
                    "conversion": 0.4,
                    "need_satisfaction": 0.35,
                    "objection_handling": 0.25
                }
                return default_weights
            default_weights = model_params.get("objective_weights", {
                "need_satisfaction": 0.35,
                "objection_handling": 0.25,
                "conversion_progress": 0.4
            })
            
            # Si no hay mensajes, usar pesos predeterminados
            if not messages:
                return default_weights
            
            # Obtener predicciones para evaluar prioridades
            objection_prediction = await self.objection_service.predict_objections(
                conversation_id, messages, customer_profile
            )
            
            needs_prediction = await self.needs_service.predict_needs(
                conversation_id, messages, customer_profile
            )
            
            conversion_prediction = await self.conversion_service.predict_conversion(
                conversation_id, messages, customer_profile
            )
            
            # Inicializar con pesos predeterminados
            objective_weights = default_weights.copy()
            
            # Ajustar basado en predicciones
            # 1. Si hay objeciones fuertes, aumentar peso de manejo de objeciones
            objections = objection_prediction.get("objections", [])
            if objections and objections[0].get("confidence", 0) > 0.7:
                objective_weights["objection_handling"] = min(0.6, objective_weights["objection_handling"] + 0.2)
            
            # 2. Si hay necesidades claras, aumentar peso de satisfacción de necesidades
            needs = needs_prediction.get("needs", [])
            if needs and needs[0].get("confidence", 0) > 0.7:
                objective_weights["need_satisfaction"] = min(0.6, objective_weights["need_satisfaction"] + 0.15)
            
            # 3. Ajustar según etapa de conversión
            conversion_category = conversion_prediction.get("category", "low")
            if conversion_category in ["high", "very_high"]:
                objective_weights["conversion_progress"] = min(0.7, objective_weights["conversion_progress"] + 0.2)
            elif conversion_category == "medium":
                # En etapa media, equilibrar entre necesidades y conversión
                objective_weights["need_satisfaction"] = min(0.5, objective_weights["need_satisfaction"] + 0.1)
                objective_weights["conversion_progress"] = min(0.5, objective_weights["conversion_progress"] + 0.1)
            
            # Normalizar pesos para que sumen 1
            total_weight = sum(objective_weights.values())
            if total_weight > 0:
                for key in objective_weights:
                    objective_weights[key] /= total_weight
            
            # Almacenar priorización usando el método de la clase base
            await self.store_prediction(
                conversation_id=conversation_id,
                prediction_type="objectives_prioritization",
                prediction_data={
                    "objectives": objective_weights,
                    "conversation_stage": self._determine_conversation_stage(messages),
                    "objection_probability": objection_prediction.get("probability", 0),
                    "conversion_probability": conversion_prediction.get("probability", 0),
                    "unsatisfied_needs_count": len([need for need in needs if need.get("satisfaction_level", 0) <= 0.6]),
                    "timestamp": datetime.now().isoformat()
                },
                confidence=0.8
            )
            
            return objective_weights
            
        except Exception as e:
            logger.error(f"Error al priorizar objetivos: {e}")
            return {
                "conversion": 0.4,
                "need_satisfaction": 0.35,
                "objection_handling": 0.25
            }
    
    async def evaluate_conversation_path(self, conversation_id: str,
                                    messages: List[Dict[str, Any]],
                                    path_actions: List[Dict[str, Any]],
                                    customer_profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Evalúa la efectividad de una ruta de conversación específica.
        
        Args:
            conversation_id: ID de la conversación
            messages: Lista de mensajes de la conversación
            path_actions: Acciones tomadas en la ruta de conversación
            customer_profile: Perfil del cliente (opcional)
            
        Returns:
            Evaluación de la ruta con métricas y recomendaciones
        """
        try:
            if not messages or not path_actions:
                return {
                    "effectiveness": 0,
                    "metrics": {},
                    "recommendations": []
                }
            
            # Obtener predicciones actuales en paralelo para mejorar rendimiento
            objection_task = self.objection_service.predict_objections(
                conversation_id=conversation_id,
                messages=messages,
                customer_profile=customer_profile
            )
            
            needs_task = self.needs_service.predict_needs(
                conversation_id=conversation_id,
                messages=messages,
                customer_profile=customer_profile
            )
            
            conversion_task = self.conversion_service.predict_conversion(
                conversation_id=conversation_id,
                messages=messages,
                customer_profile=customer_profile
            )
            
            # Esperar a que todas las predicciones se completen
            objection_prediction, needs_prediction, conversion_prediction = await asyncio.gather(
                objection_task, needs_task, conversion_task
            )
            
            # Calcular métricas de efectividad
            metrics = {}
            
            # 1. Reducción de objeciones
            objection_probability = objection_prediction.get("probability", 0)
            metrics["objection_reduction"] = 1 - objection_probability
            
            # 2. Satisfacción de necesidades
            needs = needs_prediction.get("needs", [])
            satisfied_needs = [need for need in needs if need.get("satisfaction_level", 0) > 0.6]
            needs_satisfaction = len(satisfied_needs) / max(1, len(needs))
            metrics["needs_satisfaction"] = needs_satisfaction
            
            # 3. Progreso de conversión
            conversion_probability = conversion_prediction.get("probability", 0)
            metrics["conversion_progress"] = conversion_probability
            
            # 4. Alineación con acciones recomendadas
            recommended_actions = set()
            for action in path_actions:
                action_id = action.get("id", "")
                action_type = action.get("type", "")
                if action_id or action_type:
                    recommended_actions.add(f"{action_type}:{action_id}")
            
            # Obtener acciones que se deberían haber tomado según predicciones actuales
            current_strategy = await self.optimize_conversation_flow(
                conversation_id=conversation_id,
                messages=messages,
                customer_profile=customer_profile
            )
            
            optimal_actions = set()
            for action in current_strategy.get("next_actions", []):
                action_id = action.get("id", "")
                action_type = action.get("type", "")
                if action_id or action_type:
                    optimal_actions.add(f"{action_type}:{action_id}")
            
            # Calcular alineación como intersección de conjuntos
            if optimal_actions:
                alignment = len(recommended_actions.intersection(optimal_actions)) / len(optimal_actions)
            else:
                alignment = 0
            
            metrics["action_alignment"] = alignment
            
            # Calcular efectividad general como promedio ponderado
            effectiveness = (
                metrics["objection_reduction"] * 0.25 +
                metrics["needs_satisfaction"] * 0.35 +
                metrics["conversion_progress"] * 0.3 +
                metrics["action_alignment"] * 0.1
            )
            
            # Generar recomendaciones para mejorar la ruta
            recommendations = []
            
            # Si hay baja reducción de objeciones
            if metrics["objection_reduction"] < 0.5:
                objections = objection_prediction.get("objections", [])
                for objection in objections[:2]:  # Tomar las 2 principales objeciones
                    recommendations.append({
                        "type": "objection_handling",
                        "description": f"Abordar objeción: {objection.get('description', '')}",
                        "priority": "high"
                    })
            
            # Si hay baja satisfacción de necesidades
            if metrics["needs_satisfaction"] < 0.5:
                unsatisfied_needs = [need for need in needs if need.get("satisfaction_level", 0) <= 0.6]
                for need in unsatisfied_needs[:2]:  # Tomar las 2 principales necesidades insatisfechas
                    recommendations.append({
                        "type": "need_satisfaction",
                        "description": f"Satisfacer necesidad: {need.get('description', '')}",
                        "priority": "high"
                    })
            
            # Si hay bajo progreso de conversión
            if metrics["conversion_progress"] < 0.4:
                conversion_recommendations = conversion_prediction.get("recommendations", [])
                for rec in conversion_recommendations[:2]:  # Tomar las 2 principales recomendaciones
                    recommendations.append({
                        "type": "conversion_progression",
                        "description": rec.get("description", ""),
                        "priority": "medium"
                    })
            
            # Si hay baja alineación de acciones
            if metrics["action_alignment"] < 0.5:
                recommendations.append({
                    "type": "action_alignment",
                    "description": "Seguir más de cerca las acciones recomendadas por el motor de decisiones",
                    "priority": "medium"
                })
            
            # Guardar evaluación usando la clase base
            evaluation_data = {
                "conversation_id": conversation_id,
                "path_actions": path_actions,
                "metrics": metrics,
                "effectiveness": effectiveness,
                "recommendations": recommendations,
                "timestamp": datetime.now().isoformat()
            }
            
            await self.store_prediction(
                conversation_id=conversation_id,
                prediction_type="path_evaluation",
                prediction_data=evaluation_data,
                confidence=0.8  # Alta confianza en la evaluación de la ruta
            )
            
            return {
                "effectiveness": effectiveness,
                "metrics": metrics,
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"Error al evaluar ruta de conversación: {e}")
            return {
                "effectiveness": 0,
                "metrics": {},
                "recommendations": []
            }
    
    def _determine_conversation_stage(self, messages: List[Dict[str, Any]]) -> str:
        """
        Determina la etapa actual de la conversación basado en los mensajes.
        
        Args:
            messages: Lista de mensajes de la conversación
            
        Returns:
            Etapa de la conversación ("initial", "middle", "closing")
        """
        if not messages:
            return "initial"
        
        # Determinar etapa basado en cantidad de mensajes
        message_count = len(messages)
        
        if message_count <= 5:
            return "initial"  # Etapa inicial (saludo, presentación)
        elif message_count <= 15:
            return "middle"   # Etapa media (exploración de necesidades, manejo de objeciones)
        else:
            # Analizar contenido de últimos mensajes para detectar si estamos en etapa de cierre
            recent_messages = messages[-5:]  # Últimos 5 mensajes
            closing_keywords = [
                "comprar", "adquirir", "contratar", "precio", "costo", "pagar", "tarjeta",
                "factura", "descuento", "oferta", "promocion", "cerrar", "finalizar", "decidir"
            ]
            
            # Contar menciones de palabras clave de cierre
            closing_mentions = 0
            for msg in recent_messages:
                content = msg.get("content", "").lower()
                for keyword in closing_keywords:
                    if keyword in content:
                        closing_mentions += 1
            
            # Si hay suficientes menciones de palabras clave de cierre, considerar etapa de cierre
            if closing_mentions >= 2:
                return "closing"
            else:
                return "middle"
    
    async def get_decision_statistics(self, time_period: Optional[int] = None) -> Dict[str, Any]:
        """
        Obtiene estadísticas sobre decisiones tomadas por el motor.
        
        Args:
            time_period: Período de tiempo en días (opcional)
            
        Returns:
            Estadísticas de decisiones
        """
        try:
            # Obtener estadísticas básicas usando la clase base
            basic_stats = await self.get_statistics(time_period)
            
            # Obtener todas las predicciones de decisión
            query = await self.supabase_client.from_("prediction_results")\
                .select("*")\
                .eq("model_name", self.model_name)\
                .execute()
            
            if not hasattr(query, 'data') or not query.data:
                return {
                    **basic_stats,
                    "decision_types": {},
                    "adaptation_rate": 0,
                    "effectiveness": 0,
                    "total_decisions": 0
                }
            
            # Contar tipos de decisiones
            decision_types = {}
            adaptations = 0
            effectiveness_sum = 0
            effectiveness_count = 0
            
            for prediction in query.data:
                prediction_type = prediction.get("prediction_type", "")
                decision_types[prediction_type] = decision_types.get(prediction_type, 0) + 1
                
                # Contar adaptaciones
                if prediction_type == "strategy_adaptation":
                    adaptations += 1
                
                # Sumar efectividad de rutas evaluadas
                if prediction_type == "path_evaluation":
                    prediction_data = json.loads(prediction.get("prediction_data", "{}"))
                    effectiveness = prediction_data.get("effectiveness", 0)
                    effectiveness_sum += effectiveness
                    effectiveness_count += 1
            
            total_decisions = len(query.data)
            
            # Calcular tasa de adaptación
            adaptation_rate = adaptations / total_decisions if total_decisions > 0 else 0
            
            # Calcular efectividad promedio
            avg_effectiveness = effectiveness_sum / effectiveness_count if effectiveness_count > 0 else 0
            
            return {
                **basic_stats,
                "decision_types": decision_types,
                "adaptation_rate": adaptation_rate,
                "effectiveness": avg_effectiveness,
                "total_decisions": total_decisions
            }
            
        except Exception as e:
            logger.error(f"Error al obtener estadísticas de decisiones: {e}")
            return {
                "accuracy": {"accuracy": 0, "total_predictions": 0},
                "decision_types": {},
                "adaptation_rate": 0,
                "effectiveness": 0,
                "total_decisions": 0
            }
