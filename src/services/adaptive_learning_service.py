"""
Adaptive Learning Service - Motor principal del sistema ML adaptativo.

Este es el cerebro del sistema que convierte al agente NGX en un organismo vivo:
- Analiza patrones de comportamiento y éxito
- Optimiza estrategias automáticamente
- Maneja experimentos A/B en tiempo real
- Entrena y actualiza modelos continuamente
- Toma decisiones de deployment automático

Es el core del sistema que hace al agente exponencialmente mejor con cada conversación.
"""

import logging
import asyncio
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import uuid
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
from dataclasses import asdict

# Importar modelos propios
from src.models.learning_models import (
    MLExperiment, ExperimentStatus, ExperimentType,
    ConversationOutcomeRecord, LearnedModel, ModelType,
    IdentifiedPattern, AdaptiveLearningConfig
)

# Importar servicios relacionados
from src.services.conversation_outcome_tracker import ConversationOutcomeTracker
from src.integrations.supabase import supabase_client

logger = logging.getLogger(__name__)


class AdaptiveLearningService:
    """
    Motor de aprendizaje adaptativo que evoluciona el agente NGX continuamente.
    
    Funcionalidades principales:
    - Pattern Recognition: Identifica patrones de éxito automáticamente
    - Model Training: Entrena modelos predictivos continuamente  
    - Strategy Optimization: Optimiza estrategias basado en resultados
    - Experiment Management: Maneja A/B testing automático
    - Auto-deployment: Despliega mejoras automáticamente
    """
    
    def __init__(self, outcome_tracker: ConversationOutcomeTracker):
        self.outcome_tracker = outcome_tracker
        self.config = self._load_configuration()
        self.active_models = {}  # Cache de modelos activos
        self.pattern_cache = {}  # Cache de patrones identificados
        self.learning_history = []  # Historial de aprendizajes
        
        # Inicializar modelos base
        asyncio.create_task(self._initialize_base_models())
        
    def _load_configuration(self) -> AdaptiveLearningConfig:
        """Carga configuración del sistema de aprendizaje."""
        try:
            # Intentar cargar de base de datos
            result = supabase_client.table("adaptive_learning_config")\
                .select("*")\
                .eq("is_active", True)\
                .execute()
            
            if result.data:
                config_data = result.data[0]
                return AdaptiveLearningConfig(
                    max_concurrent_experiments=config_data.get("max_concurrent_experiments", 5),
                    minimum_experiment_duration_hours=config_data.get("minimum_experiment_duration_hours", 24),
                    auto_deploy_threshold=config_data.get("auto_deploy_threshold", 0.95),
                    learning_rate=config_data.get("learning_rate", 0.01),
                    pattern_detection_sensitivity=config_data.get("pattern_detection_sensitivity", 0.05),
                    minimum_pattern_sample_size=config_data.get("minimum_pattern_sample_size", 50)
                )
            else:
                logger.warning("No active configuration found, using defaults")
                return AdaptiveLearningConfig()
                
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            return AdaptiveLearningConfig()
    
    async def _initialize_base_models(self) -> None:
        """Inicializa modelos base del sistema."""
        try:
            # Cargar modelos existentes de la base de datos
            result = supabase_client.table("learned_models")\
                .select("*")\
                .eq("champion_model", True)\
                .execute()
            
            if result.data:
                for model_data in result.data:
                    model_type = model_data["model_type"]
                    try:
                        # Cargar artifacts del modelo
                        artifacts = model_data["model_artifacts"]
                        if "sklearn_model_path" in artifacts:
                            sklearn_model = joblib.load(artifacts["sklearn_model_path"])
                            self.active_models[model_type] = {
                                "model": sklearn_model,
                                "metadata": model_data,
                                "last_updated": datetime.fromisoformat(model_data["created_at"])
                            }
                            logger.info(f"Loaded champion model for {model_type}")
                    except Exception as e:
                        logger.error(f"Error loading model {model_type}: {str(e)}")
            
            # Si no hay modelos champion, crear modelos base
            if not self.active_models:
                await self._create_base_models()
                
        except Exception as e:
            logger.error(f"Error initializing base models: {str(e)}")
            await self._create_base_models()
    
    async def _create_base_models(self) -> None:
        """Crea modelos base iniciales."""
        try:
            logger.info("Creating base models for adaptive learning")
            
            # Modelo básico de predicción de conversión
            conversion_model = LogisticRegression(random_state=42)
            
            # Modelo básico de clasificación de arquetipos
            archetype_model = RandomForestClassifier(n_estimators=100, random_state=42)
            
            self.active_models = {
                ModelType.CONVERSION_PREDICTION.value: {
                    "model": conversion_model,
                    "metadata": {"type": "baseline", "version": "1.0"},
                    "last_updated": datetime.now()
                },
                ModelType.ARCHETYPE_CLASSIFIER.value: {
                    "model": archetype_model,
                    "metadata": {"type": "baseline", "version": "1.0"},
                    "last_updated": datetime.now()
                }
            }
            
            logger.info("Base models created successfully")
            
        except Exception as e:
            logger.error(f"Error creating base models: {str(e)}")
    
    async def analyze_conversation_patterns(
        self, 
        lookback_days: int = 30,
        minimum_sample_size: int = None
    ) -> List[IdentifiedPattern]:
        """
        Analiza patrones en conversaciones recientes.
        
        Args:
            lookback_days: Días hacia atrás para analizar
            minimum_sample_size: Tamaño mínimo de muestra para patterns
            
        Returns:
            Lista de patrones identificados
        """
        try:
            min_sample = minimum_sample_size or self.config.minimum_pattern_sample_size
            cutoff_date = datetime.now() - timedelta(days=lookback_days)
            
            # Obtener datos de conversaciones recientes
            result = supabase_client.table("conversation_outcomes")\
                .select("*")\
                .gte("recorded_at", cutoff_date.isoformat())\
                .execute()
            
            if not result.data or len(result.data) < min_sample:
                logger.warning(f"Insufficient data for pattern analysis: {len(result.data) if result.data else 0} samples")
                return []
            
            # Convertir a DataFrame para análisis
            df = pd.DataFrame(result.data)
            patterns = []
            
            # Patrón 1: Estrategias más efectivas por arquetipo
            archetype_patterns = await self._analyze_archetype_strategy_patterns(df)
            patterns.extend(archetype_patterns)
            
            # Patrón 2: Timing óptimo para mencionar HIE
            hie_timing_patterns = await self._analyze_hie_timing_patterns(df)
            patterns.extend(hie_timing_patterns)
            
            # Patrón 3: Factores de conversión
            conversion_patterns = await self._analyze_conversion_factor_patterns(df)
            patterns.extend(conversion_patterns)
            
            # Patrón 4: Objeciones más comunes y resoluciones
            objection_patterns = await self._analyze_objection_patterns(df)
            patterns.extend(objection_patterns)
            
            # Guardar patrones en base de datos
            for pattern in patterns:
                await self._save_pattern_to_database(pattern)
            
            logger.info(f"Identified {len(patterns)} patterns from {len(df)} conversations")
            return patterns
            
        except Exception as e:
            logger.error(f"Error analyzing conversation patterns: {str(e)}")
            return []
    
    async def _analyze_archetype_strategy_patterns(self, df: pd.DataFrame) -> List[IdentifiedPattern]:
        """Analiza qué estrategias funcionan mejor para cada arquetipo."""
        patterns = []
        
        try:
            # Agrupar por arquetipo
            archetype_groups = df.groupby('client_archetype')
            
            for archetype, group in archetype_groups:
                if len(group) < 20:  # Mínimo para análisis estadístico
                    continue
                
                # Analizar efectividad de estrategias
                strategy_effectiveness = {}
                
                for _, row in group.iterrows():
                    outcome = row['outcome']
                    strategies = row.get('strategies_used', [])
                    
                    if isinstance(strategies, str):
                        try:
                            strategies = json.loads(strategies)
                        except:
                            strategies = []
                    
                    success = 1 if outcome == 'converted' else 0
                    
                    for strategy in strategies:
                        if strategy not in strategy_effectiveness:
                            strategy_effectiveness[strategy] = {'successes': 0, 'total': 0}
                        
                        strategy_effectiveness[strategy]['total'] += 1
                        strategy_effectiveness[strategy]['successes'] += success
                
                # Identificar estrategias con alta efectividad
                for strategy, stats in strategy_effectiveness.items():
                    if stats['total'] >= 10:  # Mínimo para confiabilidad
                        success_rate = stats['successes'] / stats['total']
                        
                        if success_rate >= 0.7:  # 70%+ success rate
                            pattern = IdentifiedPattern(
                                pattern_name=f"effective_strategy_{strategy}_for_{archetype}",
                                pattern_type="strategy_effectiveness",
                                description=f"Strategy '{strategy}' is highly effective for {archetype} clients",
                                pattern_conditions={
                                    "client_archetype": archetype,
                                    "required_strategy": strategy
                                },
                                pattern_outcomes={
                                    "success_rate": success_rate,
                                    "sample_size": stats['total']
                                },
                                confidence_score=min(0.95, success_rate + 0.1),
                                sample_size=stats['total'],
                                effect_size=success_rate - 0.5,  # vs baseline 50%
                                statistical_significance=self._calculate_p_value(stats['successes'], stats['total']),
                                applicable_archetypes=[archetype],
                                recommended_actions=[f"prioritize_{strategy}_for_{archetype}"],
                                implementation_priority="high" if success_rate >= 0.8 else "medium"
                            )
                            patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error analyzing archetype strategy patterns: {str(e)}")
            return []
    
    async def _analyze_hie_timing_patterns(self, df: pd.DataFrame) -> List[IdentifiedPattern]:
        """Analiza el timing óptimo para mencionar HIE."""
        patterns = []
        
        try:
            # Filtrar conversaciones donde se mencionó HIE
            hie_conversations = df[df['hie_explanation_effectiveness'] > 0]
            
            if len(hie_conversations) < 20:
                return patterns
            
            # Analizar correlación entre timing de HIE y efectividad
            high_effectiveness = hie_conversations[hie_conversations['hie_explanation_effectiveness'] >= 0.7]
            low_effectiveness = hie_conversations[hie_conversations['hie_explanation_effectiveness'] < 0.5]
            
            if len(high_effectiveness) >= 10 and len(low_effectiveness) >= 10:
                # Comparar duración promedio hasta mención de HIE (simplificado)
                high_avg_duration = high_effectiveness['total_duration_seconds'].mean()
                low_avg_duration = low_effectiveness['total_duration_seconds'].mean()
                
                if abs(high_avg_duration - low_avg_duration) > 60:  # Diferencia significativa
                    optimal_timing = "early" if high_avg_duration < low_avg_duration else "late"
                    
                    pattern = IdentifiedPattern(
                        pattern_name=f"optimal_hie_timing_{optimal_timing}",
                        pattern_type="timing_optimization",
                        description=f"HIE explanation is more effective when presented {optimal_timing} in conversation",
                        pattern_conditions={
                            "strategy": "hie_emphasis",
                            "optimal_timing": optimal_timing,
                            "duration_threshold": high_avg_duration
                        },
                        pattern_outcomes={
                            "high_effectiveness_avg": high_effectiveness['hie_explanation_effectiveness'].mean(),
                            "low_effectiveness_avg": low_effectiveness['hie_explanation_effectiveness'].mean()
                        },
                        confidence_score=0.75,
                        sample_size=len(hie_conversations),
                        effect_size=abs(high_effectiveness['hie_explanation_effectiveness'].mean() - 
                                       low_effectiveness['hie_explanation_effectiveness'].mean()),
                        statistical_significance=0.05,  # Placeholder
                        applicable_archetypes=["all"],
                        recommended_actions=[f"present_hie_{optimal_timing}_in_conversation"],
                        implementation_priority="medium"
                    )
                    patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error analyzing HIE timing patterns: {str(e)}")
            return []
    
    async def _analyze_conversion_factor_patterns(self, df: pd.DataFrame) -> List[IdentifiedPattern]:
        """Analiza factores que más influyen en la conversión."""
        patterns = []
        
        try:
            # Separar conversiones exitosas vs no exitosas
            converted = df[df['outcome'] == 'converted']
            not_converted = df[df['outcome'].isin(['lost', 'abandoned'])]
            
            if len(converted) < 10 or len(not_converted) < 10:
                return patterns
            
            # Analizar diferencias en métricas clave
            metrics_to_analyze = [
                'engagement_score', 'total_duration_seconds', 
                'user_messages_count', 'questions_asked_by_user'
            ]
            
            for metric in metrics_to_analyze:
                if metric in df.columns:
                    converted_avg = converted[metric].mean()
                    not_converted_avg = not_converted[metric].mean()
                    
                    # Calcular diferencia significativa
                    difference_pct = abs(converted_avg - not_converted_avg) / max(converted_avg, not_converted_avg)
                    
                    if difference_pct > 0.2:  # 20%+ difference
                        direction = "higher" if converted_avg > not_converted_avg else "lower"
                        
                        pattern = IdentifiedPattern(
                            pattern_name=f"conversion_factor_{metric}_{direction}",
                            pattern_type="conversion_optimization",
                            description=f"Converted clients have {direction} {metric.replace('_', ' ')}",
                            pattern_conditions={
                                "metric": metric,
                                "optimal_direction": direction,
                                "threshold": converted_avg
                            },
                            pattern_outcomes={
                                "converted_average": converted_avg,
                                "not_converted_average": not_converted_avg,
                                "difference_percentage": difference_pct
                            },
                            confidence_score=min(0.9, 0.5 + difference_pct),
                            sample_size=len(df),
                            effect_size=difference_pct,
                            statistical_significance=0.05,  # Placeholder
                            applicable_archetypes=["all"],
                            recommended_actions=[f"optimize_for_{direction}_{metric}"],
                            implementation_priority="high" if difference_pct > 0.3 else "medium"
                        )
                        patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error analyzing conversion factor patterns: {str(e)}")
            return []
    
    async def _analyze_objection_patterns(self, df: pd.DataFrame) -> List[IdentifiedPattern]:
        """Analiza patrones de objeciones y su resolución."""
        patterns = []
        
        try:
            # Filtrar conversaciones con objeciones
            with_objections = df[df['objections_count'] > 0]
            
            if len(with_objections) < 20:
                return patterns
            
            # Analizar tasa de resolución de objeciones
            resolved_rate = with_objections[with_objections['objections_resolved_count'] > 0]
            
            if len(resolved_rate) >= 10:
                # Calcular tasa de conversión con objeciones resueltas vs no resueltas
                resolved_conversion_rate = len(resolved_rate[resolved_rate['outcome'] == 'converted']) / len(resolved_rate)
                
                unresolved = with_objections[with_objections['objections_resolved_count'] == 0]
                if len(unresolved) > 0:
                    unresolved_conversion_rate = len(unresolved[unresolved['outcome'] == 'converted']) / len(unresolved)
                    
                    if resolved_conversion_rate > unresolved_conversion_rate + 0.1:  # 10%+ improvement
                        pattern = IdentifiedPattern(
                            pattern_name="objection_resolution_effectiveness",
                            pattern_type="objection_handling",
                            description="Resolving objections significantly improves conversion rates",
                            pattern_conditions={
                                "has_objections": True,
                                "objections_resolved": True
                            },
                            pattern_outcomes={
                                "resolved_conversion_rate": resolved_conversion_rate,
                                "unresolved_conversion_rate": unresolved_conversion_rate,
                                "improvement": resolved_conversion_rate - unresolved_conversion_rate
                            },
                            confidence_score=0.85,
                            sample_size=len(with_objections),
                            effect_size=resolved_conversion_rate - unresolved_conversion_rate,
                            statistical_significance=0.05,
                            applicable_archetypes=["all"],
                            recommended_actions=["prioritize_objection_resolution"],
                            implementation_priority="high"
                        )
                        patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error analyzing objection patterns: {str(e)}")
            return []
    
    def _calculate_p_value(self, successes: int, total: int, expected_rate: float = 0.5) -> float:
        """Calcula p-value simplificado para significancia estadística."""
        try:
            from scipy.stats import binom_test
            return binom_test(successes, total, expected_rate)
        except ImportError:
            # Fallback sin scipy
            observed_rate = successes / total
            return abs(observed_rate - expected_rate)
    
    async def train_conversion_prediction_model(self, lookback_days: int = 60) -> Optional[LearnedModel]:
        """
        Entrena modelo de predicción de conversión con datos recientes.
        
        Args:
            lookback_days: Días de datos para entrenamiento
            
        Returns:
            Modelo entrenado o None si falla
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=lookback_days)
            
            # Obtener datos de entrenamiento
            result = supabase_client.table("conversation_outcomes")\
                .select("*")\
                .gte("recorded_at", cutoff_date.isoformat())\
                .execute()
            
            if not result.data or len(result.data) < 100:
                logger.warning(f"Insufficient data for model training: {len(result.data) if result.data else 0}")
                return None
            
            # Preparar datos
            df = pd.DataFrame(result.data)
            
            # Features para el modelo
            feature_columns = [
                'engagement_score', 'total_duration_seconds', 'user_messages_count',
                'questions_asked_by_user', 'objections_count', 'hie_explanation_effectiveness'
            ]
            
            # Crear features adicionales
            df['has_early_adopter'] = df['early_adopter_presented'].astype(int)
            df['objection_resolution_rate'] = df['objections_resolved_count'] / (df['objections_count'] + 1)
            
            feature_columns.extend(['has_early_adopter', 'objection_resolution_rate'])
            
            # Preparar X y y
            X = df[feature_columns].fillna(0)
            y = (df['outcome'] == 'converted').astype(int)
            
            # Split train/test
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Entrenar modelo
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            
            # Evaluar performance
            y_pred = model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred)
            recall = recall_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred)
            
            # Cross-validation
            cv_scores = cross_val_score(model, X, y, cv=5)
            cv_mean = cv_scores.mean()
            
            # Crear LearnedModel
            model_artifacts = {
                "feature_columns": feature_columns,
                "model_type": "RandomForestClassifier",
                "sklearn_model_path": f"/tmp/conversion_model_{datetime.now().strftime('%Y%m%d_%H%M%S')}.joblib"
            }
            
            # Guardar modelo
            joblib.dump(model, model_artifacts["sklearn_model_path"])
            
            learned_model = LearnedModel(
                model_type=ModelType.CONVERSION_PREDICTION,
                model_name=f"conversion_predictor_{datetime.now().strftime('%Y%m%d')}",
                description=f"Random Forest model trained on {len(df)} conversations",
                model_artifacts=model_artifacts,
                training_data_range={
                    "start_date": cutoff_date,
                    "end_date": datetime.now()
                },
                training_sample_size=len(df),
                performance_metrics={
                    "accuracy": accuracy,
                    "precision": precision,
                    "recall": recall,
                    "f1_score": f1,
                    "cv_mean": cv_mean
                },
                cross_validation_score=cv_mean,
                confidence_interval={"lower": cv_scores.min(), "upper": cv_scores.max()}
            )
            
            # Guardar en base de datos
            await self._save_model_to_database(learned_model)
            
            # Actualizar modelo activo si es mejor
            current_model = self.active_models.get(ModelType.CONVERSION_PREDICTION.value)
            if not current_model or cv_mean > current_model["metadata"].get("cv_score", 0):
                self.active_models[ModelType.CONVERSION_PREDICTION.value] = {
                    "model": model,
                    "metadata": asdict(learned_model),
                    "last_updated": datetime.now()
                }
                logger.info(f"Updated active conversion prediction model (CV score: {cv_mean:.3f})")
            
            return learned_model
            
        except Exception as e:
            logger.error(f"Error training conversion prediction model: {str(e)}")
            return None
    
    async def _save_pattern_to_database(self, pattern: IdentifiedPattern) -> None:
        """Guarda patrón identificado en base de datos."""
        try:
            pattern_data = {
                "pattern_id": pattern.pattern_id,
                "pattern_name": pattern.pattern_name,
                "pattern_type": pattern.pattern_type,
                "description": pattern.description,
                "pattern_conditions": pattern.pattern_conditions,
                "pattern_outcomes": pattern.pattern_outcomes,
                "confidence_score": pattern.confidence_score,
                "sample_size": pattern.sample_size,
                "effect_size": pattern.effect_size,
                "statistical_significance": pattern.statistical_significance,
                "applicable_archetypes": pattern.applicable_archetypes,
                "recommended_actions": pattern.recommended_actions,
                "implementation_priority": pattern.implementation_priority,
                "discovered_at": pattern.discovered_at.isoformat(),
                "last_validated": pattern.last_validated.isoformat(),
                "validation_frequency_days": pattern.validation_frequency_days
            }
            
            result = supabase_client.table("identified_patterns").insert(pattern_data).execute()
            
            if hasattr(result, 'error') and result.error:
                logger.error(f"Database error saving pattern: {result.error}")
            else:
                logger.debug(f"Successfully saved pattern: {pattern.pattern_name}")
                
        except Exception as e:
            logger.error(f"Error saving pattern to database: {str(e)}")
    
    async def _save_model_to_database(self, model: LearnedModel) -> None:
        """Guarda modelo aprendido en base de datos."""
        try:
            model_data = {
                "model_id": model.model_id,
                "model_type": model.model_type.value,
                "model_name": model.model_name,
                "description": model.description,
                "model_artifacts": model.model_artifacts,
                "training_data_range": model.training_data_range,
                "training_sample_size": model.training_sample_size,
                "performance_metrics": model.performance_metrics,
                "cross_validation_score": model.cross_validation_score,
                "confidence_interval": model.confidence_interval,
                "deployment_status": model.deployment_status,
                "deployment_date": model.deployment_date.isoformat() if model.deployment_date else None,
                "champion_model": model.champion_model,
                "created_at": model.created_at.isoformat(),
                "created_by": model.created_by
            }
            
            result = supabase_client.table("learned_models").insert(model_data).execute()
            
            if hasattr(result, 'error') and result.error:
                logger.error(f"Database error saving model: {result.error}")
            else:
                logger.debug(f"Successfully saved model: {model.model_name}")
                
        except Exception as e:
            logger.error(f"Error saving model to database: {str(e)}")
    
    async def predict_conversation_success(
        self, 
        conversation_metrics: Dict[str, Any]
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Predice probabilidad de éxito de una conversación en curso.
        
        Args:
            conversation_metrics: Métricas actuales de la conversación
            
        Returns:
            Tupla (probabilidad, explicación)
        """
        try:
            model_info = self.active_models.get(ModelType.CONVERSION_PREDICTION.value)
            
            if not model_info:
                # Fallback: predicción basada en reglas simples
                return self._rule_based_prediction(conversation_metrics)
            
            model = model_info["model"]
            feature_columns = model_info["metadata"]["model_artifacts"]["feature_columns"]
            
            # Preparar features
            features = []
            for col in feature_columns:
                if col in conversation_metrics:
                    features.append(conversation_metrics[col])
                else:
                    features.append(0)  # Default value
            
            # Predicción
            features_array = np.array(features).reshape(1, -1)
            probability = model.predict_proba(features_array)[0][1]  # Probabilidad de clase positiva
            
            # Explicación basada en feature importance
            if hasattr(model, 'feature_importances_'):
                feature_importance = list(zip(feature_columns, model.feature_importances_))
                feature_importance.sort(key=lambda x: x[1], reverse=True)
                
                explanation = {
                    "prediction_confidence": "high" if probability > 0.7 or probability < 0.3 else "medium",
                    "key_factors": feature_importance[:3],
                    "model_version": model_info["metadata"].get("model_name", "unknown")
                }
            else:
                explanation = {"prediction_confidence": "medium", "model_version": "fallback"}
            
            return float(probability), explanation
            
        except Exception as e:
            logger.error(f"Error predicting conversation success: {str(e)}")
            return self._rule_based_prediction(conversation_metrics)
    
    def _rule_based_prediction(self, metrics: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """Predicción basada en reglas cuando no hay modelo ML."""
        try:
            score = 0.5  # Base score
            factors = []
            
            # Factor 1: Engagement
            engagement = metrics.get("engagement_score", 5.0)
            if engagement >= 7.0:
                score += 0.2
                factors.append("high_engagement")
            elif engagement <= 3.0:
                score -= 0.2
                factors.append("low_engagement")
            
            # Factor 2: Duration
            duration = metrics.get("total_duration_seconds", 300)
            if duration >= 420:  # 7+ minutes
                score += 0.15
                factors.append("adequate_duration")
            elif duration <= 180:  # < 3 minutes
                score -= 0.15
                factors.append("short_duration")
            
            # Factor 3: User questions
            questions = metrics.get("questions_asked_by_user", 0)
            if questions >= 2:
                score += 0.1
                factors.append("user_engagement")
            
            # Factor 4: HIE effectiveness
            hie_effectiveness = metrics.get("hie_explanation_effectiveness", 0)
            if hie_effectiveness >= 0.7:
                score += 0.1
                factors.append("effective_hie_explanation")
            
            score = max(0.0, min(1.0, score))
            
            explanation = {
                "prediction_confidence": "low",
                "key_factors": factors,
                "model_version": "rule_based_fallback"
            }
            
            return score, explanation
            
        except Exception as e:
            logger.error(f"Error in rule-based prediction: {str(e)}")
            return 0.5, {"prediction_confidence": "very_low", "error": str(e)}
    
    async def get_strategy_recommendations(
        self, 
        client_archetype: str,
        current_metrics: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Obtiene recomendaciones de estrategia basadas en patrones aprendidos.
        
        Args:
            client_archetype: Arquetipo del cliente
            current_metrics: Métricas actuales de la conversación
            
        Returns:
            Lista de recomendaciones de estrategia
        """
        try:
            recommendations = []
            
            # Buscar patrones relevantes en cache
            relevant_patterns = [
                pattern for pattern in self.pattern_cache.values()
                if client_archetype in pattern.applicable_archetypes or "all" in pattern.applicable_archetypes
            ]
            
            # Si no hay patrones en cache, cargar de base de datos
            if not relevant_patterns:
                result = supabase_client.table("identified_patterns")\
                    .select("*")\
                    .contains("applicable_archetypes", [client_archetype])\
                    .or_("applicable_archetypes.cs.{\"all\"}")\
                    .eq("implementation_priority", "high")\
                    .execute()
                
                if result.data:
                    relevant_patterns = [self._dict_to_pattern(p) for p in result.data]
            
            # Generar recomendaciones basadas en patrones
            for pattern in relevant_patterns[:5]:  # Top 5 patterns
                if pattern.pattern_type == "strategy_effectiveness":
                    recommendations.append({
                        "strategy": pattern.recommended_actions[0] if pattern.recommended_actions else "unknown",
                        "confidence": pattern.confidence_score,
                        "reason": pattern.description,
                        "priority": pattern.implementation_priority,
                        "expected_improvement": pattern.effect_size
                    })
                
                elif pattern.pattern_type == "timing_optimization":
                    recommendations.append({
                        "strategy": "timing_adjustment",
                        "confidence": pattern.confidence_score,
                        "reason": pattern.description,
                        "priority": pattern.implementation_priority,
                        "timing_recommendation": pattern.pattern_conditions.get("optimal_timing")
                    })
            
            # Añadir recomendaciones basadas en métricas actuales
            if current_metrics.get("engagement_score", 5.0) < 5.0:
                recommendations.append({
                    "strategy": "increase_engagement",
                    "confidence": 0.8,
                    "reason": "Current engagement is below average",
                    "priority": "high",
                    "suggested_actions": ["ask_open_questions", "show_empathy", "personalize_response"]
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting strategy recommendations: {str(e)}")
            return []
    
    def _dict_to_pattern(self, pattern_dict: Dict) -> IdentifiedPattern:
        """Convierte diccionario de base de datos a IdentifiedPattern."""
        return IdentifiedPattern(
            pattern_id=pattern_dict["pattern_id"],
            pattern_name=pattern_dict["pattern_name"],
            pattern_type=pattern_dict["pattern_type"],
            description=pattern_dict["description"],
            pattern_conditions=pattern_dict["pattern_conditions"],
            pattern_outcomes=pattern_dict["pattern_outcomes"],
            confidence_score=pattern_dict["confidence_score"],
            sample_size=pattern_dict["sample_size"],
            effect_size=pattern_dict["effect_size"],
            statistical_significance=pattern_dict["statistical_significance"],
            applicable_archetypes=pattern_dict["applicable_archetypes"],
            recommended_actions=pattern_dict["recommended_actions"],
            implementation_priority=pattern_dict["implementation_priority"],
            discovered_at=datetime.fromisoformat(pattern_dict["discovered_at"]),
            last_validated=datetime.fromisoformat(pattern_dict["last_validated"]),
            validation_frequency_days=pattern_dict["validation_frequency_days"]
        )
    
    async def run_continuous_learning_cycle(self) -> None:
        """Ejecuta ciclo continuo de aprendizaje del sistema."""
        try:
            logger.info("Starting continuous learning cycle")
            
            # 1. Analizar patrones recientes
            patterns = await self.analyze_conversation_patterns(lookback_days=7)
            logger.info(f"Identified {len(patterns)} new patterns")
            
            # 2. Reentrenar modelos si hay suficientes datos nuevos
            new_model = await self.train_conversion_prediction_model(lookback_days=30)
            if new_model:
                logger.info(f"Trained new model with CV score: {new_model.cross_validation_score:.3f}")
            
            # 3. Actualizar cache de patrones
            self.pattern_cache = {p.pattern_id: p for p in patterns}
            
            # 4. Log learning progress
            self.learning_history.append({
                "timestamp": datetime.now(),
                "patterns_identified": len(patterns),
                "model_updated": new_model is not None,
                "active_models": list(self.active_models.keys())
            })
            
            logger.info("Continuous learning cycle completed successfully")
            
        except Exception as e:
            logger.error(f"Error in continuous learning cycle: {str(e)}")
    
    def get_learning_summary(self) -> Dict[str, Any]:
        """Obtiene resumen del estado del sistema de aprendizaje."""
        return {
            "active_models": list(self.active_models.keys()),
            "patterns_in_cache": len(self.pattern_cache),
            "learning_history_length": len(self.learning_history),
            "last_learning_cycle": self.learning_history[-1] if self.learning_history else None,
            "configuration": asdict(self.config)
        }