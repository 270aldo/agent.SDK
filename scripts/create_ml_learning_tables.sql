-- =====================================================================
-- SCHEMA DE BASE DE DATOS PARA SISTEMA ML ADAPTATIVO NGX
-- =====================================================================
-- Este script crea todas las tablas necesarias para el sistema de
-- aprendizaje adaptativo que convierte al agente NGX en un organismo vivo.

-- =====================================================================
-- 1. TABLA DE EXPERIMENTOS ML A/B
-- =====================================================================
CREATE TABLE IF NOT EXISTS ml_experiments (
    -- Identificación
    experiment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    experiment_name VARCHAR(255) NOT NULL,
    experiment_type VARCHAR(50) NOT NULL, -- prompt_variant, strategy_test, etc.
    description TEXT,
    hypothesis TEXT,
    
    -- Configuración del experimento
    variants JSONB NOT NULL, -- Array de ExperimentVariant
    target_metric VARCHAR(100) NOT NULL, -- conversion_rate, satisfaction, etc.
    minimum_sample_size INTEGER DEFAULT 100,
    confidence_level FLOAT DEFAULT 0.95,
    
    -- Control del experimento
    status VARCHAR(50) DEFAULT 'planning', -- planning, running, analyzing, completed, etc.
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    auto_deploy_winner BOOLEAN DEFAULT true,
    
    -- Resultados
    results JSONB DEFAULT '{}',
    winning_variant_id UUID,
    confidence_score FLOAT,
    
    -- Metadata
    created_by VARCHAR(255) DEFAULT 'adaptive_learning_system',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Índices y constraints
    CONSTRAINT valid_confidence_level CHECK (confidence_level >= 0.5 AND confidence_level <= 0.99),
    CONSTRAINT valid_confidence_score CHECK (confidence_score IS NULL OR (confidence_score >= 0.0 AND confidence_score <= 1.0))
);

-- Índices para ml_experiments
CREATE INDEX IF NOT EXISTS idx_ml_experiments_status ON ml_experiments(status);
CREATE INDEX IF NOT EXISTS idx_ml_experiments_type ON ml_experiments(experiment_type);
CREATE INDEX IF NOT EXISTS idx_ml_experiments_dates ON ml_experiments(start_date, end_date);
CREATE INDEX IF NOT EXISTS idx_ml_experiments_created_at ON ml_experiments(created_at);

-- =====================================================================
-- 2. TABLA DE OUTCOMES DE CONVERSACIÓN PARA ML
-- =====================================================================
CREATE TABLE IF NOT EXISTS conversation_outcomes (
    -- Identificación
    outcome_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL,
    
    -- Información del cliente
    client_archetype VARCHAR(100),
    client_demographic_data JSONB DEFAULT '{}',
    initial_intent VARCHAR(255),
    
    -- Estrategias y experimentos
    strategies_used JSONB DEFAULT '[]', -- Array de strings
    prompts_used JSONB DEFAULT '[]', -- Array de objetos
    experiment_assignments JSONB DEFAULT '[]', -- Array de experiment_ids
    
    -- Resultado
    outcome VARCHAR(50) NOT NULL, -- converted, lost, follow_up_scheduled, etc.
    
    -- Métricas detalladas
    total_duration_seconds INTEGER,
    user_messages_count INTEGER,
    agent_messages_count INTEGER,
    average_response_time_seconds FLOAT,
    engagement_score FLOAT CHECK (engagement_score >= 0.0 AND engagement_score <= 10.0),
    satisfaction_score FLOAT CHECK (satisfaction_score IS NULL OR (satisfaction_score >= 0.0 AND satisfaction_score <= 10.0)),
    emotional_journey_stability FLOAT CHECK (emotional_journey_stability >= 0.0 AND emotional_journey_stability <= 1.0),
    conversion_probability FLOAT CHECK (conversion_probability >= 0.0 AND conversion_probability <= 1.0),
    
    -- Información de tier y objeciones
    tier_recommended VARCHAR(50),
    final_tier_accepted VARCHAR(50),
    objections_count INTEGER DEFAULT 0,
    objections_resolved_count INTEGER DEFAULT 0,
    questions_asked_by_user INTEGER DEFAULT 0,
    early_adopter_presented BOOLEAN DEFAULT false,
    early_adopter_accepted BOOLEAN DEFAULT false,
    hie_explanation_effectiveness FLOAT CHECK (hie_explanation_effectiveness >= 0.0 AND hie_explanation_effectiveness <= 1.0),
    
    -- Insights para aprendizaje
    success_factors JSONB DEFAULT '[]',
    failure_factors JSONB DEFAULT '[]',
    learning_insights JSONB DEFAULT '{}',
    
    -- Metadata
    recorded_at TIMESTAMP DEFAULT NOW(),
    agent_version VARCHAR(50) DEFAULT 'ngx_v1.0',
    
    -- Foreign key constraint (si existe tabla conversations)
    -- FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

-- Índices para conversation_outcomes
CREATE INDEX IF NOT EXISTS idx_conversation_outcomes_conversation_id ON conversation_outcomes(conversation_id);
CREATE INDEX IF NOT EXISTS idx_conversation_outcomes_outcome ON conversation_outcomes(outcome);
CREATE INDEX IF NOT EXISTS idx_conversation_outcomes_archetype ON conversation_outcomes(client_archetype);
CREATE INDEX IF NOT EXISTS idx_conversation_outcomes_recorded_at ON conversation_outcomes(recorded_at);
CREATE INDEX IF NOT EXISTS idx_conversation_outcomes_conversion_prob ON conversation_outcomes(conversion_probability);
CREATE INDEX IF NOT EXISTS idx_conversation_outcomes_engagement ON conversation_outcomes(engagement_score);

-- =====================================================================
-- 3. TABLA DE MODELOS ENTRENADOS
-- =====================================================================
CREATE TABLE IF NOT EXISTS learned_models (
    -- Identificación
    model_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_type VARCHAR(50) NOT NULL, -- pattern_recognition, conversion_prediction, etc.
    model_name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Datos del modelo
    model_artifacts JSONB NOT NULL, -- weights, parameters, configuration
    training_data_range JSONB NOT NULL, -- {start_date, end_date}
    training_sample_size INTEGER,
    
    -- Performance metrics
    performance_metrics JSONB DEFAULT '{}', -- accuracy, precision, recall, f1, etc.
    cross_validation_score FLOAT,
    confidence_interval JSONB DEFAULT '{}', -- {lower, upper}
    
    -- Deployment info
    deployment_status VARCHAR(50) DEFAULT 'trained', -- trained, testing, deployed, deprecated
    deployment_date TIMESTAMP,
    champion_model BOOLEAN DEFAULT false, -- Es el modelo actual en producción
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(255) DEFAULT 'adaptive_learning_system',
    
    -- Constraints
    CONSTRAINT valid_deployment_status CHECK (deployment_status IN ('trained', 'testing', 'deployed', 'deprecated')),
    CONSTRAINT valid_cross_validation CHECK (cross_validation_score IS NULL OR (cross_validation_score >= 0.0 AND cross_validation_score <= 1.0))
);

-- Índices para learned_models
CREATE INDEX IF NOT EXISTS idx_learned_models_type ON learned_models(model_type);
CREATE INDEX IF NOT EXISTS idx_learned_models_status ON learned_models(deployment_status);
CREATE INDEX IF NOT EXISTS idx_learned_models_champion ON learned_models(champion_model) WHERE champion_model = true;
CREATE INDEX IF NOT EXISTS idx_learned_models_created_at ON learned_models(created_at);

-- =====================================================================
-- 4. TABLA DE PATRONES IDENTIFICADOS
-- =====================================================================
CREATE TABLE IF NOT EXISTS identified_patterns (
    -- Identificación
    pattern_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern_name VARCHAR(255) NOT NULL,
    pattern_type VARCHAR(100) NOT NULL, -- client_behavior, strategy_effectiveness, timing
    
    -- Descripción del patrón
    description TEXT NOT NULL,
    pattern_conditions JSONB NOT NULL,
    pattern_outcomes JSONB NOT NULL,
    
    -- Estadísticas
    confidence_score FLOAT NOT NULL CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    sample_size INTEGER NOT NULL,
    effect_size FLOAT,
    statistical_significance FLOAT,
    
    -- Aplicabilidad
    applicable_archetypes JSONB DEFAULT '[]',
    recommended_actions JSONB DEFAULT '[]',
    implementation_priority VARCHAR(20) DEFAULT 'medium', -- low, medium, high, critical
    
    -- Metadata
    discovered_at TIMESTAMP DEFAULT NOW(),
    last_validated TIMESTAMP DEFAULT NOW(),
    validation_frequency_days INTEGER DEFAULT 7,
    
    -- Constraints
    CONSTRAINT valid_implementation_priority CHECK (implementation_priority IN ('low', 'medium', 'high', 'critical')),
    CONSTRAINT valid_sample_size CHECK (sample_size > 0)
);

-- Índices para identified_patterns
CREATE INDEX IF NOT EXISTS idx_identified_patterns_type ON identified_patterns(pattern_type);
CREATE INDEX IF NOT EXISTS idx_identified_patterns_priority ON identified_patterns(implementation_priority);
CREATE INDEX IF NOT EXISTS idx_identified_patterns_confidence ON identified_patterns(confidence_score);
CREATE INDEX IF NOT EXISTS idx_identified_patterns_discovered_at ON identified_patterns(discovered_at);

-- =====================================================================
-- 5. TABLA DE CONFIGURACIÓN DEL SISTEMA ADAPTATIVO
-- =====================================================================
CREATE TABLE IF NOT EXISTS adaptive_learning_config (
    -- Identificación
    config_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    config_name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    
    -- Configuración de experimentos
    max_concurrent_experiments INTEGER DEFAULT 5,
    minimum_experiment_duration_hours INTEGER DEFAULT 24,
    auto_deploy_threshold FLOAT DEFAULT 0.95,
    
    -- Configuración de aprendizaje
    learning_rate FLOAT DEFAULT 0.01,
    pattern_detection_sensitivity FLOAT DEFAULT 0.05,
    minimum_pattern_sample_size INTEGER DEFAULT 50,
    
    -- Configuración de performance
    model_retraining_frequency_hours INTEGER DEFAULT 24,
    performance_degradation_threshold FLOAT DEFAULT 0.05,
    champion_challenger_ratio FLOAT DEFAULT 0.9,
    
    -- Configuración de seguridad
    fallback_to_baseline_on_error BOOLEAN DEFAULT true,
    max_performance_degradation_allowed FLOAT DEFAULT 0.1,
    automatic_rollback_enabled BOOLEAN DEFAULT true,
    
    -- Metadata
    is_active BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(255) DEFAULT 'system',
    
    -- Constraints
    CONSTRAINT valid_auto_deploy_threshold CHECK (auto_deploy_threshold >= 0.5 AND auto_deploy_threshold <= 1.0),
    CONSTRAINT valid_learning_rate CHECK (learning_rate > 0.0 AND learning_rate <= 1.0),
    CONSTRAINT valid_champion_challenger_ratio CHECK (champion_challenger_ratio >= 0.5 AND champion_challenger_ratio <= 1.0)
);

-- Índice para adaptive_learning_config
CREATE INDEX IF NOT EXISTS idx_adaptive_learning_config_active ON adaptive_learning_config(is_active) WHERE is_active = true;

-- =====================================================================
-- 6. TABLA DE MÉTRICAS EN TIEMPO REAL
-- =====================================================================
CREATE TABLE IF NOT EXISTS ml_metrics_realtime (
    -- Identificación
    metric_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_name VARCHAR(255) NOT NULL,
    metric_type VARCHAR(100) NOT NULL, -- experiment, model, pattern, system
    
    -- Datos de la métrica
    metric_value FLOAT NOT NULL,
    metric_context JSONB DEFAULT '{}', -- contexto adicional
    
    -- Referencias
    experiment_id UUID, -- NULL si no es métrica de experimento
    model_id UUID, -- NULL si no es métrica de modelo
    pattern_id UUID, -- NULL si no es métrica de patrón
    
    -- Metadata
    recorded_at TIMESTAMP DEFAULT NOW(),
    recorded_by VARCHAR(255) DEFAULT 'system',
    
    -- Foreign keys (opcional)
    -- FOREIGN KEY (experiment_id) REFERENCES ml_experiments(experiment_id) ON DELETE CASCADE,
    -- FOREIGN KEY (model_id) REFERENCES learned_models(model_id) ON DELETE CASCADE,
    -- FOREIGN KEY (pattern_id) REFERENCES identified_patterns(pattern_id) ON DELETE CASCADE
);

-- Índices para ml_metrics_realtime
CREATE INDEX IF NOT EXISTS idx_ml_metrics_realtime_name ON ml_metrics_realtime(metric_name);
CREATE INDEX IF NOT EXISTS idx_ml_metrics_realtime_type ON ml_metrics_realtime(metric_type);
CREATE INDEX IF NOT EXISTS idx_ml_metrics_realtime_recorded_at ON ml_metrics_realtime(recorded_at);
CREATE INDEX IF NOT EXISTS idx_ml_metrics_realtime_experiment_id ON ml_metrics_realtime(experiment_id) WHERE experiment_id IS NOT NULL;

-- =====================================================================
-- 7. TRIGGERS PARA UPDATED_AT AUTOMÁTICO
-- =====================================================================

-- Function para actualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger para ml_experiments
CREATE TRIGGER update_ml_experiments_updated_at 
    BEFORE UPDATE ON ml_experiments 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Trigger para adaptive_learning_config
CREATE TRIGGER update_adaptive_learning_config_updated_at 
    BEFORE UPDATE ON adaptive_learning_config 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================================
-- 8. INSERTAR CONFIGURACIÓN INICIAL
-- =====================================================================
INSERT INTO adaptive_learning_config (
    config_name,
    description,
    is_active,
    created_by
) VALUES (
    'default_adaptive_config',
    'Configuración inicial del sistema de aprendizaje adaptativo NGX',
    true,
    'setup_script'
) ON CONFLICT (config_name) DO NOTHING;

-- =====================================================================
-- 9. COMENTARIOS PARA DOCUMENTACIÓN
-- =====================================================================
COMMENT ON TABLE ml_experiments IS 'Experimentos A/B para optimización continua del agente NGX';
COMMENT ON TABLE conversation_outcomes IS 'Resultados detallados de conversaciones para training ML';
COMMENT ON TABLE learned_models IS 'Modelos entrenados listos para deployment';
COMMENT ON TABLE identified_patterns IS 'Patrones de comportamiento identificados automáticamente';
COMMENT ON TABLE adaptive_learning_config IS 'Configuración del sistema de aprendizaje adaptativo';
COMMENT ON TABLE ml_metrics_realtime IS 'Métricas en tiempo real del sistema ML';

-- Comentarios en columnas clave
COMMENT ON COLUMN conversation_outcomes.conversion_probability IS 'Probabilidad de conversión predicha al inicio de la conversación';
COMMENT ON COLUMN conversation_outcomes.hie_explanation_effectiveness IS 'Efectividad de la explicación HIE (0-1)';
COMMENT ON COLUMN learned_models.champion_model IS 'Indica si este es el modelo actualmente en producción';
COMMENT ON COLUMN identified_patterns.statistical_significance IS 'P-value del patrón identificado';

-- =====================================================================
-- 10. VIEWS ÚTILES PARA ANALYTICS
-- =====================================================================

-- View para experimentos activos
CREATE OR REPLACE VIEW active_experiments AS
SELECT 
    experiment_id,
    experiment_name,
    experiment_type,
    status,
    start_date,
    target_metric,
    (SELECT COUNT(*) FROM conversation_outcomes WHERE experiment_assignments::text LIKE '%' || experiment_id::text || '%') as sample_size_current
FROM ml_experiments 
WHERE status IN ('running', 'analyzing');

-- View para performance de modelos
CREATE OR REPLACE VIEW model_performance_summary AS
SELECT 
    model_type,
    COUNT(*) as total_models,
    AVG(cross_validation_score) as avg_cv_score,
    MAX(cross_validation_score) as best_cv_score,
    COUNT(*) FILTER (WHERE champion_model = true) as champion_models
FROM learned_models 
WHERE deployment_status != 'deprecated'
GROUP BY model_type;

-- View para conversión por arquetipo
CREATE OR REPLACE VIEW conversion_by_archetype AS
SELECT 
    client_archetype,
    COUNT(*) as total_conversations,
    COUNT(*) FILTER (WHERE outcome = 'converted') as conversions,
    ROUND(COUNT(*) FILTER (WHERE outcome = 'converted')::numeric / COUNT(*)::numeric * 100, 2) as conversion_rate,
    AVG(engagement_score) as avg_engagement,
    AVG(conversion_probability) as avg_predicted_probability
FROM conversation_outcomes 
WHERE recorded_at >= NOW() - INTERVAL '30 days'
GROUP BY client_archetype
ORDER BY conversion_rate DESC;

-- =====================================================================
-- FINALIZACIÓN
-- =====================================================================
-- Script completado exitosamente
-- El sistema de base de datos está listo para soportar el aprendizaje adaptativo