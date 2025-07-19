"""
Learning Models - Modelos de datos para sistema ML adaptativo.

Este módulo define todos los modelos necesarios para el sistema de aprendizaje:
- Experimentos A/B y variants
- Outcomes de conversación y métricas
- Modelos entrenados y performance
- Patrones identificados y insights
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional, Literal, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import uuid


class ExperimentType(Enum):
    """Tipos de experimentos ML soportados."""
    PROMPT_VARIANT = "prompt_variant"
    STRATEGY_TEST = "strategy_test"
    FLOW_OPTIMIZATION = "flow_optimization"
    ARCHETYPE_DETECTION = "archetype_detection"
    TIMING_OPTIMIZATION = "timing_optimization"


class ExperimentStatus(Enum):
    """Estados de un experimento."""
    PLANNING = "planning"
    RUNNING = "running"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class ConversationOutcome(Enum):
    """Resultados posibles de una conversación."""
    CONVERTED = "converted"
    LOST = "lost"
    FOLLOW_UP_SCHEDULED = "follow_up_scheduled"
    TRANSFERRED_TO_HUMAN = "transferred_to_human"
    ABANDONED = "abandoned"
    IN_PROGRESS = "in_progress"


class ModelType(Enum):
    """Tipos de modelos ML."""
    PATTERN_RECOGNITION = "pattern_recognition"
    CONVERSION_PREDICTION = "conversion_prediction"
    ARCHETYPE_CLASSIFIER = "archetype_classifier"
    PROMPT_OPTIMIZER = "prompt_optimizer"
    STRATEGY_RECOMMENDER = "strategy_recommender"


class ExperimentVariant(BaseModel):
    """Variante de un experimento A/B."""
    variant_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    variant_name: str
    variant_type: str  # "prompt", "strategy", "flow"
    variant_content: Dict[str, Any]
    weight: float = Field(default=0.5, ge=0.0, le=1.0)
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)


class MLExperiment(BaseModel):
    """Experimento de Machine Learning A/B."""
    experiment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    experiment_name: str
    experiment_type: ExperimentType
    description: str
    hypothesis: str
    
    # Configuración del experimento
    variants: List[ExperimentVariant]
    target_metric: str  # "conversion_rate", "satisfaction", "time_to_close"
    minimum_sample_size: int = 100
    confidence_level: float = 0.95
    
    # Control del experimento
    status: ExperimentStatus = ExperimentStatus.PLANNING
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    auto_deploy_winner: bool = True
    
    # Resultados
    results: Dict[str, Any] = Field(default_factory=dict)
    winning_variant_id: Optional[str] = None
    confidence_score: Optional[float] = None
    
    # Metadata
    created_by: str = "adaptive_learning_system"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    @validator('variants')
    def validate_variants(cls, v):
        if len(v) < 2:
            raise ValueError("Experimento debe tener al menos 2 variantes")
        
        total_weight = sum(variant.weight for variant in v)
        if abs(total_weight - 1.0) > 0.01:
            raise ValueError("Peso total de variantes debe sumar 1.0")
        
        return v


class ConversationMetrics(BaseModel):
    """Métricas detalladas de una conversación."""
    # Métricas de duración y flujo
    total_duration_seconds: int
    user_messages_count: int
    agent_messages_count: int
    average_response_time_seconds: float
    
    # Métricas de engagement
    engagement_score: float = Field(ge=0.0, le=10.0)
    satisfaction_score: Optional[float] = Field(default=None, ge=0.0, le=10.0)
    emotional_journey_stability: float = Field(ge=0.0, le=1.0)
    
    # Métricas de conversión
    conversion_probability: float = Field(ge=0.0, le=1.0)
    tier_recommended: str
    final_tier_accepted: Optional[str] = None
    objections_count: int = 0
    objections_resolved_count: int = 0
    
    # Métricas de efectividad
    questions_asked_by_user: int = 0
    early_adopter_presented: bool = False
    early_adopter_accepted: bool = False
    hie_explanation_effectiveness: float = Field(ge=0.0, le=1.0)


class ConversationOutcomeRecord(BaseModel):
    """Registro completo del outcome de una conversación para ML."""
    outcome_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str
    
    # Información del cliente
    client_archetype: str
    client_demographic_data: Dict[str, Any]
    initial_intent: str
    
    # Estrategias usadas
    strategies_used: List[str]
    prompts_used: List[Dict[str, Any]]
    experiment_assignments: List[str] = Field(default_factory=list)
    
    # Resultado y métricas
    outcome: ConversationOutcome
    metrics: ConversationMetrics
    
    # Insights para aprendizaje
    success_factors: List[str] = Field(default_factory=list)
    failure_factors: List[str] = Field(default_factory=list)
    learning_insights: Dict[str, Any] = Field(default_factory=dict)
    
    # Metadata
    recorded_at: datetime = Field(default_factory=datetime.now)
    agent_version: str = "ngx_v1.0"
    
    def calculate_success_score(self) -> float:
        """Calcula score de éxito basado en outcome y métricas."""
        base_scores = {
            ConversationOutcome.CONVERTED: 1.0,
            ConversationOutcome.FOLLOW_UP_SCHEDULED: 0.7,
            ConversationOutcome.TRANSFERRED_TO_HUMAN: 0.5,
            ConversationOutcome.LOST: 0.1,
            ConversationOutcome.ABANDONED: 0.0,
            ConversationOutcome.IN_PROGRESS: 0.3
        }
        
        base_score = base_scores.get(self.outcome, 0.0)
        
        # Ajustar por métricas de calidad
        quality_bonus = (
            self.metrics.engagement_score / 10.0 * 0.2 +
            self.metrics.conversion_probability * 0.1 +
            (self.metrics.satisfaction_score or 5.0) / 10.0 * 0.1
        )
        
        return min(1.0, base_score + quality_bonus)


class LearnedModel(BaseModel):
    """Modelo entrenado y listo para deployment."""
    model_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    model_type: ModelType
    model_name: str
    description: str
    
    # Datos del modelo
    model_artifacts: Dict[str, Any]  # Weights, parameters, etc.
    training_data_range: Dict[str, datetime]
    training_sample_size: int
    
    # Performance metrics
    performance_metrics: Dict[str, float]
    cross_validation_score: float
    confidence_interval: Dict[str, float]
    
    # Deployment info
    deployment_status: Literal["trained", "testing", "deployed", "deprecated"] = "trained"
    deployment_date: Optional[datetime] = None
    champion_model: bool = False  # Es el modelo actual en producción
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    created_by: str = "adaptive_learning_system"
    
    def is_better_than(self, other_model: 'LearnedModel', metric: str = "accuracy") -> bool:
        """Compara este modelo con otro basado en métrica específica."""
        if metric not in self.performance_metrics or metric not in other_model.performance_metrics:
            return False
        
        return self.performance_metrics[metric] > other_model.performance_metrics[metric]


class IdentifiedPattern(BaseModel):
    """Patrón identificado por el sistema de aprendizaje."""
    pattern_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    pattern_name: str
    pattern_type: str  # "client_behavior", "strategy_effectiveness", "timing"
    
    # Descripción del patrón
    description: str
    pattern_conditions: Dict[str, Any]
    pattern_outcomes: Dict[str, Any]
    
    # Estadísticas
    confidence_score: float = Field(ge=0.0, le=1.0)
    sample_size: int
    effect_size: float
    statistical_significance: float
    
    # Aplicabilidad
    applicable_archetypes: List[str]
    recommended_actions: List[str]
    implementation_priority: Literal["low", "medium", "high", "critical"] = "medium"
    
    # Metadata
    discovered_at: datetime = Field(default_factory=datetime.now)
    last_validated: datetime = Field(default_factory=datetime.now)
    validation_frequency_days: int = 7


class AdaptiveLearningConfig(BaseModel):
    """Configuración del sistema de aprendizaje adaptativo."""
    # Configuración de experimentos
    max_concurrent_experiments: int = 5
    minimum_experiment_duration_hours: int = 24
    auto_deploy_threshold: float = 0.95  # Confianza para auto-deploy
    
    # Configuración de aprendizaje
    learning_rate: float = 0.01
    pattern_detection_sensitivity: float = 0.05
    minimum_pattern_sample_size: int = 50
    
    # Configuración de performance
    model_retraining_frequency_hours: int = 24
    performance_degradation_threshold: float = 0.05
    champion_challenger_ratio: float = 0.9  # 90% champion, 10% challenger
    
    # Configuración de seguridad
    fallback_to_baseline_on_error: bool = True
    max_performance_degradation_allowed: float = 0.1
    automatic_rollback_enabled: bool = True
    
    def update_config(self, **kwargs) -> 'AdaptiveLearningConfig':
        """Actualiza configuración con nuevos valores."""
        current_dict = self.dict()
        current_dict.update(kwargs)
        return AdaptiveLearningConfig(**current_dict)


# Alias para facilidad de uso
Experiment = MLExperiment
OutcomeRecord = ConversationOutcomeRecord
Pattern = IdentifiedPattern
Model = LearnedModel
Config = AdaptiveLearningConfig