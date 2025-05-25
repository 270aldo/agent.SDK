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
from datetime import datetime
import random

from src.integrations.supabase.resilient_client import ResilientSupabaseClient
from src.services.predictive_model_service import PredictiveModelService
from src.services.objection_prediction_service import ObjectionPredictionService
from src.services.needs_prediction_service import NeedsPredictionService
from src.services.conversion_prediction_service import ConversionPredictionService

logger = logging.getLogger(__name__)

class DecisionEngineService:
    """
    Servicio para optimizar el flujo de conversación y toma de decisiones.
    
    Características principales:
    - Optimización de flujo de conversación
    - Árboles de decisión dinámicos
    - Adaptación en tiempo real
    - Priorización de objetivos
    """
    
    def __init__(self, 
                 supabase_client: ResilientSupabaseClient,
                 predictive_model_service: PredictiveModelService,
                 objection_prediction_service: ObjectionPredictionService,
                 needs_prediction_service: NeedsPredictionService,
                 conversion_prediction_service: ConversionPredictionService):
        """
        Inicializa el servicio de motor de decisiones.
        
        Args:
            supabase_client: Cliente de Supabase para persistencia
            predictive_model_service: Servicio base para modelos predictivos
            objection_prediction_service: Servicio de predicción de objeciones
            needs_prediction_service: Servicio de predicción de necesidades
            conversion_prediction_service: Servicio de predicción de conversión
        """
        self.supabase = supabase_client
        self.predictive_model_service = predictive_model_service
        self.objection_service = objection_prediction_service
        self.needs_service = needs_prediction_service
        self.conversion_service = conversion_prediction_service
        self.model_name = "decision_engine_model"
        self._initialize_model()
        
    async def _initialize_model(self) -> None:
        """
        Inicializa el modelo del motor de decisiones.
        """
        try:
            # Verificar si el modelo ya existe
            model = await self.predictive_model_service.get_model(self.model_name)
            
            if not model:
                # Crear modelo si no existe
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
                
                await self.predictive_model_service.register_model(
                    model_name=self.model_name,
                    model_type="decision_engine",
                    model_params=model_params,
                    description="Modelo para motor de decisiones y optimización de flujo"
                )
                logger.info(f"Modelo de motor de decisiones inicializado: {self.model_name}")
            
        except Exception as e:
            logger.error(f"Error al inicializar modelo de motor de decisiones: {e}")
    
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
            Recomendaciones de flujo optimizado
        """
        try:
            if not messages:
                return {
                    "next_actions": [],
                    "decision_tree": {},
                    "objectives": {},
                    "confidence": 0
                }
            
            # Obtener parámetros del modelo
            model = await self.predictive_model_service.get_model(self.model_name)
            if not model or "parameters" not in model:
                logger.error("Modelo de motor de decisiones no encontrado")
                return {
                    "next_actions": [],
                    "decision_tree": {},
                    "objectives": {},
                    "confidence": 0
                }
            
            model_params = json.loads(model["parameters"])
            default_objective_weights = model_params.get("objective_weights", {})
            min_confidence = model_params.get("min_confidence", 0.6)
            context_window = model_params.get("context_window", 15)
            
            # Usar objetivos proporcionados o los predeterminados
            objective_weights = current_objectives or default_objective_weights
            
            # Limitar a los últimos N mensajes para el análisis
            recent_messages = messages[-context_window:] if len(messages) > context_window else messages
            
            # Obtener predicciones de los diferentes modelos
            objection_prediction = await self.objection_service.predict_objections(
                conversation_id, recent_messages, customer_profile
            )
            
            needs_prediction = await self.needs_service.predict_needs(
                conversation_id, recent_messages, customer_profile
            )
            
            conversion_prediction = await self.conversion_service.predict_conversion(
                conversation_id, recent_messages, customer_profile
            )
            
            # Generar árbol de decisión
            decision_tree = await self._generate_decision_tree(
                objection_prediction,
                needs_prediction,
                conversion_prediction,
                objective_weights,
                customer_profile
            )
            
            # Determinar próximas acciones óptimas
            next_actions, confidence = await self._determine_next_actions(
                decision_tree,
                objective_weights,
                min_confidence
            )
            
            # Almacenar decisión
            decision_data = {
                "decision_tree": decision_tree,
                "next_actions": next_actions,
                "objectives": objective_weights,
                "confidence": confidence
            }
            
            await self.predictive_model_service.store_prediction(
                model_name=self.model_name,
                conversation_id=conversation_id,
                prediction_type="decision",
                prediction_data=decision_data,
                confidence=confidence
            )
            
            return {
                "next_actions": next_actions,
                "decision_tree": decision_tree,
                "objectives": objective_weights,
                "confidence": confidence
            }
            
        except Exception as e:
            logger.error(f"Error al optimizar flujo de conversación: {e}")
            return {
                "next_actions": [],
                "decision_tree": {},
                "objectives": {},
                "confidence": 0
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
                                min_confidence: float) -> Tuple[List[Dict[str, Any]], float]:
        """
        Determina las próximas acciones óptimas basadas en el árbol de decisión.
        
        Args:
            decision_tree: Árbol de decisión generado
            objective_weights: Pesos de objetivos
            min_confidence: Confianza mínima para tomar decisiones
            
        Returns:
            Tupla con lista de acciones recomendadas y nivel de confianza
        """
        next_actions = []
        
        # Extraer todos los nodos de acción del árbol
        action_nodes = self._extract_action_nodes(decision_tree)
        
        # Ordenar por puntuación
        action_nodes.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        # Seleccionar las mejores acciones (máximo 3)
        top_actions = action_nodes[:3]
        
        # Convertir nodos a formato de acción
        for node in top_actions:
            action = {
                "id": node.get("id", str(uuid.uuid4())),
                "type": node.get("type", ""),
                "description": node.get("description", ""),
                "content": node.get("content", node.get("description", "")),
                "score": node.get("score", 0),
                "priority": node.get("priority", "medium")
            }
            
            # Añadir datos específicos según tipo
            if node.get("type") == "response":
                action["action_category"] = "objection_response"
            elif node.get("type") == "action":
                action["action_category"] = "need_satisfaction"
                action["action_type"] = node.get("action_type", "")
            elif node.get("type") == "recommendation":
                action["action_category"] = "conversion_progression"
                action["recommendation_type"] = node.get("recommendation_type", "")
            elif node.get("type") == "exploration_action":
                action["action_category"] = "exploration"
            
            next_actions.append(action)
        
        # Calcular confianza general como promedio ponderado de puntuaciones
        confidence = sum(action.get("score", 0) for action in next_actions) / len(next_actions) if next_actions else 0
        
        # Si la confianza es muy baja, añadir una acción de exploración
        if confidence < min_confidence and not any(a.get("action_category") == "exploration" for a in next_actions):
            exploration_actions = [
                "Preguntar sobre objetivos específicos del cliente",
                "Indagar sobre el proceso de toma de decisiones",
                "Explorar desafíos actuales que enfrenta el cliente",
                "Preguntar sobre experiencias previas con soluciones similares"
            ]
            
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
    
    def _extract_action_nodes(self, node: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extrae todos los nodos de acción de un árbol de decisión.
        
        Args:
            node: Nodo raíz o subnodo del árbol
            
        Returns:
            Lista de nodos de acción
        """
        action_nodes = []
        action_types = {"response", "action", "recommendation", "exploration_action"}
        
        # Si el nodo actual es un nodo de acción, añadirlo
        if node.get("type") in action_types:
            action_nodes.append(node)
        
        # Recursivamente procesar hijos
        if "children" in node and node["children"]:
            for child in node["children"]:
                action_nodes.extend(self._extract_action_nodes(child))
        
        return action_nodes
    
    async def adapt_strategy_realtime(self, conversation_id: str,
                                messages: List[Dict[str, Any]],
                                current_strategy: Dict[str, Any],
                                feedback: Optional[Dict[str, Any]] = None,
                                customer_profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Adapta la estrategia de conversación en tiempo real basado en feedback y nuevos mensajes.
        
        Args:
            conversation_id: ID de la conversación
            messages: Lista de mensajes de la conversación
            current_strategy: Estrategia actual (árbol de decisión y acciones)
            feedback: Feedback sobre acciones previas (opcional)
            customer_profile: Perfil del cliente (opcional)
            
        Returns:
            Estrategia adaptada con nuevas acciones recomendadas
        """
        try:
            if not messages or not current_strategy:
                return await self.optimize_conversation_flow(conversation_id, messages, customer_profile)
            
            # Obtener parámetros del modelo
            model = await self.predictive_model_service.get_model(self.model_name)
            if not model or "parameters" not in model:
                logger.error("Modelo de motor de decisiones no encontrado")
                return current_strategy
            
            model_params = json.loads(model["parameters"])
            adaptation_threshold = model_params.get("adaptation_threshold", 0.3)
            exploration_rate = model_params.get("exploration_rate", 0.2)
            
            # Evaluar necesidad de adaptación basado en feedback
            adaptation_needed = False
            objective_weights = current_strategy.get("objectives", {})
            
            if feedback:
                # Si hay feedback negativo, se necesita adaptación
                if feedback.get("success", True) == False:
                    adaptation_needed = True
                    
                    # Ajustar pesos de objetivos basado en feedback
                    feedback_type = feedback.get("type", "")
                    if feedback_type == "objection_not_addressed":
                        objective_weights["objection_handling"] = min(1.0, objective_weights.get("objection_handling", 0.25) + 0.15)
                    elif feedback_type == "need_not_satisfied":
                        objective_weights["need_satisfaction"] = min(1.0, objective_weights.get("need_satisfaction", 0.35) + 0.15)
                    elif feedback_type == "conversion_stalled":
                        objective_weights["conversion_progress"] = min(1.0, objective_weights.get("conversion_progress", 0.4) + 0.15)
                    
                    # Normalizar pesos
                    total_weight = sum(objective_weights.values())
                    if total_weight > 0:
                        for key in objective_weights:
                            objective_weights[key] /= total_weight
            
            # Verificar si las últimas acciones tuvieron éxito
            next_actions = current_strategy.get("next_actions", [])
            if next_actions:
                # Si la confianza es baja, considerar adaptación
                avg_score = sum(action.get("score", 0) for action in next_actions) / len(next_actions)
                if avg_score < adaptation_threshold:
                    adaptation_needed = True
            
            # Si no se necesita adaptación, mantener estrategia actual
            if not adaptation_needed:
                return current_strategy
            
            # Generar nueva estrategia con pesos ajustados
            new_strategy = await self.optimize_conversation_flow(
                conversation_id, 
                messages, 
                customer_profile,
                objective_weights
            )
            
            # Aumentar tasa de exploración para descubrir nuevas rutas
            decision_tree = new_strategy.get("decision_tree", {})
            exploration_nodes = [node for node in self._extract_action_nodes(decision_tree) 
                               if node.get("type") == "exploration_action"]
            
            for node in exploration_nodes:
                node["score"] = min(1.0, node.get("score", 0.5) + exploration_rate)
            
            # Recalcular próximas acciones
            next_actions, confidence = await self._determine_next_actions(
                decision_tree,
                objective_weights,
                model_params.get("min_confidence", 0.6)
            )
            
            new_strategy["next_actions"] = next_actions
            new_strategy["confidence"] = confidence
            new_strategy["adapted"] = True
            
            # Almacenar estrategia adaptada
            adaptation_data = {
                "original_strategy": current_strategy,
                "adapted_strategy": new_strategy,
                "feedback": feedback,
                "adaptation_reason": "feedback_based" if feedback else "performance_based"
            }
            
            await self.predictive_model_service.store_prediction(
                model_name=self.model_name,
                conversation_id=conversation_id,
                prediction_type="strategy_adaptation",
                prediction_data=adaptation_data,
                confidence=confidence
            )
            
            return new_strategy
            
        except Exception as e:
            logger.error(f"Error al adaptar estrategia en tiempo real: {e}")
            return current_strategy
    
    async def prioritize_objectives(self, conversation_id: str,
                              messages: List[Dict[str, Any]],
                              customer_profile: Optional[Dict[str, Any]] = None) -> Dict[str, float]:
        """
        Prioriza objetivos de conversación basado en el contexto actual.
        
        Args:
            conversation_id: ID de la conversación
            messages: Lista de mensajes de la conversación
            customer_profile: Perfil del cliente (opcional)
            
        Returns:
            Diccionario con objetivos priorizados y sus pesos
        """
        try:
            # Obtener parámetros del modelo
            model = await self.predictive_model_service.get_model(self.model_name)
            if not model or "parameters" not in model:
                logger.error("Modelo de motor de decisiones no encontrado")
                return {}
            
            model_params = json.loads(model["parameters"])
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
            
            # Almacenar priorización
            prioritization_data = {
                "objective_weights": objective_weights,
                "objection_confidence": objection_prediction.get("confidence", 0),
                "needs_confidence": needs_prediction.get("confidence", 0),
                "conversion_category": conversion_category
            }
            
            await self.predictive_model_service.store_prediction(
                model_name=self.model_name,
                conversation_id=conversation_id,
                prediction_type="objective_prioritization",
                prediction_data=prioritization_data,
                confidence=max(objection_prediction.get("confidence", 0),
                              needs_prediction.get("confidence", 0),
                              conversion_prediction.get("confidence", 0))
            )
            
            return objective_weights
            
        except Exception as e:
            logger.error(f"Error al priorizar objetivos: {e}")
            return default_weights
    
    async def evaluate_conversation_path(self, conversation_id: str,
                                    messages: List[Dict[str, Any]],
                                    path_actions: List[Dict[str, Any]],
                                    customer_profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Evalúa la efectividad de una ruta de conversación específica.
        
        Args:
            conversation_id: ID de la conversación
            messages: Lista de mensajes de la conversación
            path_actions: Acciones tomadas en la ruta a evaluar
            customer_profile: Perfil del cliente (opcional)
            
        Returns:
            Evaluación de la ruta con métricas de efectividad
        """
        try:
            if not messages or not path_actions:
                return {
                    "effectiveness": 0,
                    "metrics": {},
                    "recommendations": []
                }
            
            # Obtener predicciones actuales
            conversion_prediction = await self.conversion_service.predict_conversion(
                conversation_id, messages, customer_profile
            )
            
            # Métricas a evaluar
            metrics = {
                "conversion_probability": conversion_prediction.get("probability", 0),
                "objections_addressed": 0,
                "needs_satisfied": 0,
                "engagement_level": 0
            }
            
            # Evaluar manejo de objeciones
            objection_types_addressed = set()
            for action in path_actions:
                if action.get("action_category") == "objection_response":
                    objection_types_addressed.add(action.get("objection_type", ""))
            
            # Obtener todas las objeciones detectadas
            objection_prediction = await self.objection_service.predict_objections(
                conversation_id, messages, customer_profile
            )
            
            objection_types_detected = set(obj.get("type", "") for obj in objection_prediction.get("objections", []))
            
            # Calcular proporción de objeciones abordadas
            if objection_types_detected:
                metrics["objections_addressed"] = len(objection_types_addressed.intersection(objection_types_detected)) / len(objection_types_detected)
            else:
                metrics["objections_addressed"] = 1.0  # No había objeciones que abordar
            
            # Evaluar satisfacción de necesidades
            need_categories_addressed = set()
            for action in path_actions:
                if action.get("action_category") == "need_satisfaction":
                    need_categories_addressed.add(action.get("need_category", ""))
            
            # Obtener todas las necesidades detectadas
            needs_prediction = await self.needs_service.predict_needs(
                conversation_id, messages, customer_profile
            )
            
            need_categories_detected = set(need.get("category", "") for need in needs_prediction.get("needs", []))
            
            # Calcular proporción de necesidades satisfechas
            if need_categories_detected:
                metrics["needs_satisfied"] = len(need_categories_addressed.intersection(need_categories_detected)) / len(need_categories_detected)
            else:
                metrics["needs_satisfied"] = 1.0  # No había necesidades que satisfacer
            
            # Evaluar nivel de engagement
            # Contar mensajes del cliente después de cada acción del agente
            client_messages = [msg for msg in messages if msg.get("role") == "user"]
            agent_messages = [msg for msg in messages if msg.get("role") == "assistant"]
            
            if agent_messages:
                # Calcular promedio de longitud de respuestas del cliente
                avg_client_length = sum(len(msg.get("content", "")) for msg in client_messages) / len(client_messages) if client_messages else 0
                
                # Normalizar (considerando 100 caracteres como buena longitud)
                normalized_length = min(1.0, avg_client_length / 100)
                
                # Proporción de mensajes cliente/agente (idealmente cercano a 1)
                message_ratio = min(1.0, len(client_messages) / len(agent_messages))
                
                metrics["engagement_level"] = (normalized_length + message_ratio) / 2
            else:
                metrics["engagement_level"] = 0
            
            # Calcular efectividad general como promedio ponderado de métricas
            effectiveness = (
                metrics["conversion_probability"] * 0.4 +
                metrics["objections_addressed"] * 0.25 +
                metrics["needs_satisfied"] * 0.25 +
                metrics["engagement_level"] * 0.1
            )
            
            # Generar recomendaciones para mejorar la ruta
            recommendations = []
            
            if metrics["objections_addressed"] < 0.7:
                recommendations.append({
                    "type": "objection_handling",
                    "description": "Mejorar el abordaje de objeciones detectadas",
                    "priority": "high"
                })
            
            if metrics["needs_satisfied"] < 0.7:
                recommendations.append({
                    "type": "need_satisfaction",
                    "description": "Profundizar en la satisfacción de necesidades identificadas",
                    "priority": "high"
                })
            
            if metrics["engagement_level"] < 0.5:
                recommendations.append({
                    "type": "engagement",
                    "description": "Mejorar el nivel de engagement con preguntas más relevantes",
                    "priority": "medium"
                })
            
            if metrics["conversion_probability"] < 0.4:
                recommendations.append({
                    "type": "conversion",
                    "description": "Implementar acciones específicas para avanzar en el proceso de conversión",
                    "priority": "high"
                })
            
            # Almacenar evaluación
            evaluation_data = {
                "path_actions": path_actions,
                "metrics": metrics,
                "effectiveness": effectiveness,
                "recommendations": recommendations
            }
            
            await self.predictive_model_service.store_prediction(
                model_name=self.model_name,
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
    
    async def get_decision_statistics(self, time_period: Optional[int] = None) -> Dict[str, Any]:
        """
        Obtiene estadísticas sobre decisiones tomadas por el motor.
        
        Args:
            time_period: Período de tiempo en días (opcional)
            
        Returns:
            Estadísticas de decisiones
        """
        try:
            # Obtener precisión del modelo
            accuracy_stats = await self.predictive_model_service.get_model_accuracy(
                model_name=self.model_name,
                time_period=time_period
            )
            
            # Obtener todas las predicciones de decisión
            query = self.supabase.table("prediction_results").select("*").eq("model_name", self.model_name).execute()
            
            if not query.data:
                return {
                    "accuracy": accuracy_stats,
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
                "accuracy": accuracy_stats,
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
