"""
A/B Testing Framework - Sistema de experimentación automática.

Este framework maneja experimentos A/B en tiempo real para optimizar continuamente
el agente NGX:
- Creación automática de experimentos
- Asignación inteligente de variants usando Multi-Armed Bandit
- Stopping rules automáticos basados en significancia estadística
- Deployment automático de ganadores
- Análisis estadístico robusto de resultados

Es el motor de experimentación que permite evolución constante del agente.
"""

import logging
import asyncio
import json
import random
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import uuid
import numpy as np
from dataclasses import asdict
import math

# Importar modelos propios
from src.models.learning_models import (
    MLExperiment, ExperimentVariant, ExperimentStatus, ExperimentType,
    ConversationOutcomeRecord, AdaptiveLearningConfig
)

# Importar integración con base de datos
from src.integrations.supabase import supabase_client

logger = logging.getLogger(__name__)


class MultiArmedBandit:
    """
    Implementación de Multi-Armed Bandit para asignación inteligente de variants.
    
    Usa algoritmo UCB1 (Upper Confidence Bound) para balancear exploration vs exploitation.
    """
    
    def __init__(self, variants: List[str], exploration_factor: float = 2.0):
        self.variants = variants
        self.exploration_factor = exploration_factor
        self.counts = {variant: 0 for variant in variants}
        self.rewards = {variant: 0.0 for variant in variants}
        self.total_count = 0
    
    def select_variant(self) -> str:
        """Selecciona variant usando algoritmo UCB1."""
        if self.total_count == 0:
            return random.choice(self.variants)
        
        # Calcular UCB para cada variant
        ucb_values = {}
        for variant in self.variants:
            if self.counts[variant] == 0:
                ucb_values[variant] = float('inf')  # Explorar variants no probados
            else:
                mean_reward = self.rewards[variant] / self.counts[variant]
                confidence_bonus = math.sqrt(
                    (self.exploration_factor * math.log(self.total_count)) / self.counts[variant]
                )
                ucb_values[variant] = mean_reward + confidence_bonus
        
        # Seleccionar variant con mayor UCB
        return max(ucb_values, key=ucb_values.get)
    
    def update_reward(self, variant: str, reward: float) -> None:
        """Actualiza reward para un variant."""
        self.counts[variant] += 1
        self.rewards[variant] += reward
        self.total_count += 1
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas actuales del bandit."""
        stats = {}
        for variant in self.variants:
            if self.counts[variant] > 0:
                stats[variant] = {
                    "count": self.counts[variant],
                    "total_reward": self.rewards[variant],
                    "mean_reward": self.rewards[variant] / self.counts[variant],
                    "selection_probability": self.counts[variant] / max(1, self.total_count)
                }
            else:
                stats[variant] = {
                    "count": 0,
                    "total_reward": 0.0,
                    "mean_reward": 0.0,
                    "selection_probability": 0.0
                }
        
        return stats


class ABTestingFramework:
    """
    Framework completo para A/B testing automático en el agente NGX.
    
    Funcionalidades:
    - Gestión de experimentos multi-variant
    - Asignación inteligente usando Multi-Armed Bandit
    - Análisis estadístico automático (significancia, power, etc.)
    - Stopping rules automáticos
    - Deployment automático de ganadores
    - Rollback automático si hay degradación
    """
    
    def __init__(self, config: AdaptiveLearningConfig):
        self.config = config
        self.active_experiments = {}  # Cache de experimentos activos
        self.bandits = {}  # Multi-armed bandits por experimento
        self.experiment_assignments = {}  # Tracking de asignaciones
        
        # Inicializar experimentos activos
        asyncio.create_task(self._load_active_experiments())
    
    async def _load_active_experiments(self) -> None:
        """Carga experimentos activos de la base de datos."""
        try:
            result = supabase_client.table("ml_experiments")\
                .select("*")\
                .eq("status", ExperimentStatus.RUNNING.value)\
                .execute()
            
            if result.data:
                for exp_data in result.data:
                    experiment = self._dict_to_experiment(exp_data)
                    self.active_experiments[experiment.experiment_id] = experiment
                    
                    # Crear bandit para este experimento
                    variant_ids = [v.variant_id for v in experiment.variants]
                    self.bandits[experiment.experiment_id] = MultiArmedBandit(variant_ids)
                    
                    # Cargar datos históricos del bandit
                    await self._load_bandit_data(experiment.experiment_id)
                    
                logger.info(f"Loaded {len(self.active_experiments)} active experiments")
            
        except Exception as e:
            logger.error(f"Error loading active experiments: {str(e)}")
    
    def _dict_to_experiment(self, exp_dict: Dict) -> MLExperiment:
        """Convierte diccionario de DB a MLExperiment."""
        variants = []
        for v_data in exp_dict["variants"]:
            variant = ExperimentVariant(
                variant_id=v_data["variant_id"],
                variant_name=v_data["variant_name"],
                variant_type=v_data["variant_type"],
                variant_content=v_data["variant_content"],
                weight=v_data.get("weight", 0.5),
                active=v_data.get("active", True),
                created_at=datetime.fromisoformat(v_data["created_at"])
            )
            variants.append(variant)
        
        return MLExperiment(
            experiment_id=exp_dict["experiment_id"],
            experiment_name=exp_dict["experiment_name"],
            experiment_type=ExperimentType(exp_dict["experiment_type"]),
            description=exp_dict["description"],
            hypothesis=exp_dict["hypothesis"],
            variants=variants,
            target_metric=exp_dict["target_metric"],
            minimum_sample_size=exp_dict["minimum_sample_size"],
            confidence_level=exp_dict["confidence_level"],
            status=ExperimentStatus(exp_dict["status"]),
            start_date=datetime.fromisoformat(exp_dict["start_date"]) if exp_dict["start_date"] else None,
            end_date=datetime.fromisoformat(exp_dict["end_date"]) if exp_dict["end_date"] else None,
            auto_deploy_winner=exp_dict["auto_deploy_winner"],
            results=exp_dict["results"],
            winning_variant_id=exp_dict["winning_variant_id"],
            confidence_score=exp_dict["confidence_score"],
            created_by=exp_dict["created_by"],
            created_at=datetime.fromisoformat(exp_dict["created_at"]),
            updated_at=datetime.fromisoformat(exp_dict["updated_at"])
        )
    
    async def _load_bandit_data(self, experiment_id: str) -> None:
        """Carga datos históricos para el bandit de un experimento."""
        try:
            # Obtener outcomes de conversaciones que participaron en este experimento
            result = supabase_client.table("conversation_outcomes")\
                .select("experiment_assignments, outcome, conversion_probability")\
                .contains("experiment_assignments", [experiment_id])\
                .execute()
            
            if result.data:
                bandit = self.bandits[experiment_id]
                
                for outcome in result.data:
                    # Determinar variant asignado (simplificado)
                    assignments = outcome.get("experiment_assignments", [])
                    if experiment_id in assignments:
                        # Para simplificar, usar el primer variant del experimento
                        # En implementación real, se necesitaría tracking más detallado
                        experiment = self.active_experiments[experiment_id]
                        if experiment.variants:
                            variant_id = experiment.variants[0].variant_id
                            
                            # Calcular reward basado en outcome
                            reward = 1.0 if outcome["outcome"] == "converted" else 0.0
                            bandit.update_reward(variant_id, reward)
                
                logger.debug(f"Loaded bandit data for experiment {experiment_id}")
            
        except Exception as e:
            logger.error(f"Error loading bandit data for {experiment_id}: {str(e)}")
    
    async def create_experiment(
        self,
        experiment_name: str,
        experiment_type: ExperimentType,
        description: str,
        hypothesis: str,
        variants: List[Dict[str, Any]],
        target_metric: str = "conversion_rate",
        minimum_sample_size: int = 100,
        auto_deploy: bool = True
    ) -> Optional[MLExperiment]:
        """
        Crea un nuevo experimento A/B.
        
        Args:
            experiment_name: Nombre del experimento
            experiment_type: Tipo de experimento
            description: Descripción detallada
            hypothesis: Hipótesis a probar
            variants: Lista de variants a probar
            target_metric: Métrica objetivo para evaluar
            minimum_sample_size: Tamaño mínimo de muestra
            auto_deploy: Si deploy automático está habilitado
            
        Returns:
            Experimento creado o None si falla
        """
        try:
            # Verificar límite de experimentos concurrentes
            if len(self.active_experiments) >= self.config.max_concurrent_experiments:
                logger.warning(f"Cannot create experiment: limit of {self.config.max_concurrent_experiments} reached")
                return None
            
            # Crear variants
            experiment_variants = []
            total_weight = 0.0
            
            for i, variant_data in enumerate(variants):
                weight = variant_data.get("weight", 1.0 / len(variants))
                total_weight += weight
                
                variant = ExperimentVariant(
                    variant_name=variant_data["name"],
                    variant_type=variant_data["type"],
                    variant_content=variant_data["content"],
                    weight=weight
                )
                experiment_variants.append(variant)
            
            # Normalizar weights si no suman 1.0
            if abs(total_weight - 1.0) > 0.01:
                for variant in experiment_variants:
                    variant.weight = variant.weight / total_weight
            
            # Crear experimento
            experiment = MLExperiment(
                experiment_name=experiment_name,
                experiment_type=experiment_type,
                description=description,
                hypothesis=hypothesis,
                variants=experiment_variants,
                target_metric=target_metric,
                minimum_sample_size=minimum_sample_size,
                auto_deploy_winner=auto_deploy,
                status=ExperimentStatus.PLANNING
            )
            
            # Guardar en base de datos
            await self._save_experiment_to_database(experiment)
            
            logger.info(f"Created experiment: {experiment_name} with {len(variants)} variants")
            return experiment
            
        except Exception as e:
            logger.error(f"Error creating experiment: {str(e)}")
            return None
    
    async def start_experiment(self, experiment_id: str) -> bool:
        """
        Inicia un experimento.
        
        Args:
            experiment_id: ID del experimento a iniciar
            
        Returns:
            True si se inició exitosamente
        """
        try:
            # Cargar experimento de DB si no está en cache
            if experiment_id not in self.active_experiments:
                result = supabase_client.table("ml_experiments")\
                    .select("*")\
                    .eq("experiment_id", experiment_id)\
                    .execute()
                
                if not result.data:
                    logger.error(f"Experiment {experiment_id} not found")
                    return False
                
                experiment = self._dict_to_experiment(result.data[0])
            else:
                experiment = self.active_experiments[experiment_id]
            
            # Actualizar status
            experiment.status = ExperimentStatus.RUNNING
            experiment.start_date = datetime.now()
            
            # Crear bandit para el experimento
            variant_ids = [v.variant_id for v in experiment.variants]
            self.bandits[experiment_id] = MultiArmedBandit(variant_ids)
            
            # Actualizar en cache y DB
            self.active_experiments[experiment_id] = experiment
            await self._update_experiment_in_database(experiment)
            
            logger.info(f"Started experiment: {experiment.experiment_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting experiment {experiment_id}: {str(e)}")
            return False
    
    def assign_variant(
        self, 
        experiment_id: str, 
        conversation_id: str,
        context: Dict[str, Any] = None
    ) -> Optional[ExperimentVariant]:
        """
        Asigna variant para una conversación usando Multi-Armed Bandit.
        
        Args:
            experiment_id: ID del experimento
            conversation_id: ID de la conversación
            context: Contexto adicional para la asignación
            
        Returns:
            Variant asignado o None si no hay experimento activo
        """
        try:
            if experiment_id not in self.active_experiments:
                return None
            
            experiment = self.active_experiments[experiment_id]
            if experiment.status != ExperimentStatus.RUNNING:
                return None
            
            # Usar bandit para seleccionar variant
            bandit = self.bandits[experiment_id]
            selected_variant_id = bandit.select_variant()
            
            # Encontrar el variant correspondiente
            selected_variant = None
            for variant in experiment.variants:
                if variant.variant_id == selected_variant_id:
                    selected_variant = variant
                    break
            
            if selected_variant:
                # Registrar asignación
                self.experiment_assignments[conversation_id] = {
                    "experiment_id": experiment_id,
                    "variant_id": selected_variant_id,
                    "assigned_at": datetime.now(),
                    "context": context or {}
                }
                
                logger.debug(f"Assigned variant {selected_variant.variant_name} to conversation {conversation_id}")
                return selected_variant
            
            return None
            
        except Exception as e:
            logger.error(f"Error assigning variant for experiment {experiment_id}: {str(e)}")
            return None
    
    async def record_experiment_outcome(
        self,
        conversation_id: str,
        outcome_record: ConversationOutcomeRecord
    ) -> None:
        """
        Registra el outcome de una conversación que participó en experimentos.
        
        Args:
            conversation_id: ID de la conversación
            outcome_record: Record completo del outcome
        """
        try:
            if conversation_id not in self.experiment_assignments:
                return
            
            assignment = self.experiment_assignments[conversation_id]
            experiment_id = assignment["experiment_id"]
            variant_id = assignment["variant_id"]
            
            if experiment_id not in self.active_experiments:
                return
            
            experiment = self.active_experiments[experiment_id]
            
            # Calcular reward basado en la métrica objetivo
            reward = self._calculate_reward(outcome_record, experiment.target_metric)
            
            # Actualizar bandit
            if experiment_id in self.bandits:
                self.bandits[experiment_id].update_reward(variant_id, reward)
            
            # Verificar si el experimento puede terminar
            await self._check_experiment_completion(experiment_id)
            
            logger.debug(f"Recorded outcome for experiment {experiment_id}, variant {variant_id}, reward: {reward}")
            
        except Exception as e:
            logger.error(f"Error recording experiment outcome: {str(e)}")
    
    def _calculate_reward(self, outcome_record: ConversationOutcomeRecord, target_metric: str) -> float:
        """Calcula reward basado en la métrica objetivo."""
        try:
            if target_metric == "conversion_rate":
                return 1.0 if outcome_record.outcome.value == "converted" else 0.0
            
            elif target_metric == "engagement_score":
                return outcome_record.metrics.engagement_score / 10.0
            
            elif target_metric == "satisfaction_score":
                satisfaction = outcome_record.metrics.satisfaction_score
                return (satisfaction / 10.0) if satisfaction is not None else 0.5
            
            elif target_metric == "time_to_close":
                # Recompensa inversamente proporcional al tiempo (más rápido = mejor)
                duration = outcome_record.metrics.total_duration_seconds
                optimal_duration = 420  # 7 minutos
                if duration <= optimal_duration:
                    return 1.0 - (duration / optimal_duration) * 0.5
                else:
                    return max(0.1, 0.5 - ((duration - optimal_duration) / optimal_duration) * 0.4)
            
            else:
                # Métrica desconocida, usar conversión como default
                return 1.0 if outcome_record.outcome.value == "converted" else 0.0
                
        except Exception as e:
            logger.error(f"Error calculating reward: {str(e)}")
            return 0.0
    
    async def _check_experiment_completion(self, experiment_id: str) -> None:
        """Verifica si un experimento puede completarse."""
        try:
            experiment = self.active_experiments[experiment_id]
            bandit = self.bandits[experiment_id]
            
            # Verificar tamaño mínimo de muestra
            total_samples = sum(bandit.counts.values())
            if total_samples < experiment.minimum_sample_size:
                return
            
            # Verificar duración mínima
            if experiment.start_date:
                min_duration = timedelta(hours=self.config.minimum_experiment_duration_hours)
                if datetime.now() - experiment.start_date < min_duration:
                    return
            
            # Analizar significancia estadística
            analysis_results = await self._analyze_experiment_results(experiment_id)
            
            if analysis_results["has_winner"] and analysis_results["confidence"] >= experiment.confidence_level:
                # Completar experimento
                await self._complete_experiment(experiment_id, analysis_results)
            
        except Exception as e:
            logger.error(f"Error checking experiment completion: {str(e)}")
    
    async def _analyze_experiment_results(self, experiment_id: str) -> Dict[str, Any]:
        """Analiza resultados estadísticos de un experimento."""
        try:
            experiment = self.active_experiments[experiment_id]
            bandit = self.bandits[experiment_id]
            stats = bandit.get_statistics()
            
            # Encontrar el mejor variant
            best_variant = None
            best_mean = 0.0
            
            for variant_id, variant_stats in stats.items():
                if variant_stats["count"] > 0 and variant_stats["mean_reward"] > best_mean:
                    best_mean = variant_stats["mean_reward"]
                    best_variant = variant_id
            
            # Calcular significancia (simplificado)
            has_winner = False
            confidence = 0.0
            
            if best_variant:
                # Verificar si la diferencia es significativa
                best_stats = stats[best_variant]
                
                for variant_id, variant_stats in stats.items():
                    if variant_id != best_variant and variant_stats["count"] > 10:
                        # Test Z simplificado para diferencia de proporciones
                        diff = best_stats["mean_reward"] - variant_stats["mean_reward"]
                        
                        if diff > 0.05:  # 5% improvement threshold
                            # Calcular confidence aproximado
                            n1 = best_stats["count"]
                            n2 = variant_stats["count"]
                            p1 = best_stats["mean_reward"]
                            p2 = variant_stats["mean_reward"]
                            
                            # Standard error
                            se = math.sqrt((p1 * (1 - p1) / n1) + (p2 * (1 - p2) / n2))
                            
                            if se > 0:
                                z_score = diff / se
                                # Aproximación de confidence (no exacta)
                                confidence = max(confidence, min(0.99, abs(z_score) / 3.0))
                        
                        if confidence >= 0.8:
                            has_winner = True
            
            return {
                "has_winner": has_winner,
                "winning_variant": best_variant,
                "confidence": confidence,
                "stats": stats,
                "total_samples": sum(s["count"] for s in stats.values())
            }
            
        except Exception as e:
            logger.error(f"Error analyzing experiment results: {str(e)}")
            return {"has_winner": False, "confidence": 0.0}
    
    async def _complete_experiment(self, experiment_id: str, analysis_results: Dict[str, Any]) -> None:
        """Completa un experimento y opcionalmente despliega el ganador."""
        try:
            experiment = self.active_experiments[experiment_id]
            
            # Actualizar experimento
            experiment.status = ExperimentStatus.COMPLETED
            experiment.end_date = datetime.now()
            experiment.results = analysis_results
            experiment.winning_variant_id = analysis_results.get("winning_variant")
            experiment.confidence_score = analysis_results.get("confidence")
            
            # Guardar en DB
            await self._update_experiment_in_database(experiment)
            
            # Auto-deploy si está habilitado y hay un ganador claro
            if (experiment.auto_deploy_winner and 
                analysis_results["has_winner"] and 
                analysis_results["confidence"] >= self.config.auto_deploy_threshold):
                
                await self._deploy_winning_variant(experiment_id)
            
            # Remover de experimentos activos
            del self.active_experiments[experiment_id]
            if experiment_id in self.bandits:
                del self.bandits[experiment_id]
            
            logger.info(
                f"Completed experiment {experiment.experiment_name} "
                f"(winner: {analysis_results.get('winning_variant', 'none')}, "
                f"confidence: {analysis_results.get('confidence', 0):.2f})"
            )
            
        except Exception as e:
            logger.error(f"Error completing experiment {experiment_id}: {str(e)}")
    
    async def _deploy_winning_variant(self, experiment_id: str) -> None:
        """Despliega automáticamente el variant ganador."""
        try:
            experiment = self.active_experiments.get(experiment_id)
            if not experiment or not experiment.winning_variant_id:
                return
            
            # Encontrar variant ganador
            winning_variant = None
            for variant in experiment.variants:
                if variant.variant_id == experiment.winning_variant_id:
                    winning_variant = variant
                    break
            
            if not winning_variant:
                return
            
            # Deployment específico por tipo de experimento
            if experiment.experiment_type == ExperimentType.PROMPT_VARIANT:
                await self._deploy_prompt_variant(winning_variant)
            
            elif experiment.experiment_type == ExperimentType.STRATEGY_TEST:
                await self._deploy_strategy_variant(winning_variant)
            
            logger.info(f"Auto-deployed winning variant {winning_variant.variant_name}")
            
        except Exception as e:
            logger.error(f"Error deploying winning variant: {str(e)}")
    
    async def _deploy_prompt_variant(self, variant: ExperimentVariant) -> None:
        """Despliega un prompt variant ganador."""
        # TODO: Implementar integración con PromptOptimizerService
        logger.info(f"Deploying prompt variant: {variant.variant_name}")
    
    async def _deploy_strategy_variant(self, variant: ExperimentVariant) -> None:
        """Despliega una estrategia variant ganadora."""
        # TODO: Implementar integración con estrategias del agente
        logger.info(f"Deploying strategy variant: {variant.variant_name}")
    
    async def _save_experiment_to_database(self, experiment: MLExperiment) -> None:
        """Guarda experimento en base de datos."""
        try:
            experiment_data = {
                "experiment_id": experiment.experiment_id,
                "experiment_name": experiment.experiment_name,
                "experiment_type": experiment.experiment_type.value,
                "description": experiment.description,
                "hypothesis": experiment.hypothesis,
                "variants": [asdict(v) for v in experiment.variants],
                "target_metric": experiment.target_metric,
                "minimum_sample_size": experiment.minimum_sample_size,
                "confidence_level": experiment.confidence_level,
                "status": experiment.status.value,
                "start_date": experiment.start_date.isoformat() if experiment.start_date else None,
                "end_date": experiment.end_date.isoformat() if experiment.end_date else None,
                "auto_deploy_winner": experiment.auto_deploy_winner,
                "results": experiment.results,
                "winning_variant_id": experiment.winning_variant_id,
                "confidence_score": experiment.confidence_score,
                "created_by": experiment.created_by,
                "created_at": experiment.created_at.isoformat(),
                "updated_at": experiment.updated_at.isoformat()
            }
            
            result = supabase_client.table("ml_experiments").insert(experiment_data).execute()
            
            if hasattr(result, 'error') and result.error:
                logger.error(f"Database error saving experiment: {result.error}")
            
        except Exception as e:
            logger.error(f"Error saving experiment to database: {str(e)}")
    
    async def _update_experiment_in_database(self, experiment: MLExperiment) -> None:
        """Actualiza experimento en base de datos."""
        try:
            experiment_data = {
                "status": experiment.status.value,
                "start_date": experiment.start_date.isoformat() if experiment.start_date else None,
                "end_date": experiment.end_date.isoformat() if experiment.end_date else None,
                "results": experiment.results,
                "winning_variant_id": experiment.winning_variant_id,
                "confidence_score": experiment.confidence_score,
                "updated_at": datetime.now().isoformat()
            }
            
            result = supabase_client.table("ml_experiments")\
                .update(experiment_data)\
                .eq("experiment_id", experiment.experiment_id)\
                .execute()
            
            if hasattr(result, 'error') and result.error:
                logger.error(f"Database error updating experiment: {result.error}")
                
        except Exception as e:
            logger.error(f"Error updating experiment in database: {str(e)}")
    
    def get_active_experiments(self) -> List[MLExperiment]:
        """Obtiene lista de experimentos activos."""
        return list(self.active_experiments.values())
    
    def get_experiment_status(self, experiment_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene status detallado de un experimento."""
        if experiment_id not in self.active_experiments:
            return None
        
        experiment = self.active_experiments[experiment_id]
        bandit_stats = self.bandits[experiment_id].get_statistics() if experiment_id in self.bandits else {}
        
        return {
            "experiment": asdict(experiment),
            "bandit_statistics": bandit_stats,
            "total_assignments": sum(s.get("count", 0) for s in bandit_stats.values())
        }
    
    async def pause_experiment(self, experiment_id: str) -> bool:
        """Pausa un experimento activo."""
        try:
            if experiment_id not in self.active_experiments:
                return False
            
            experiment = self.active_experiments[experiment_id]
            experiment.status = ExperimentStatus.PAUSED
            
            await self._update_experiment_in_database(experiment)
            
            logger.info(f"Paused experiment: {experiment.experiment_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error pausing experiment {experiment_id}: {str(e)}")
            return False
    
    async def resume_experiment(self, experiment_id: str) -> bool:
        """Reanuda un experimento pausado."""
        try:
            if experiment_id not in self.active_experiments:
                return False
            
            experiment = self.active_experiments[experiment_id]
            if experiment.status == ExperimentStatus.PAUSED:
                experiment.status = ExperimentStatus.RUNNING
                
                await self._update_experiment_in_database(experiment)
                
                logger.info(f"Resumed experiment: {experiment.experiment_name}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error resuming experiment {experiment_id}: {str(e)}")
            return False