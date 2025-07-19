-- =====================================================================
-- MIGRACIÓN 003: SISTEMA DE MODELOS PREDICTIVOS
-- =====================================================================
-- Este script crea todas las tablas necesarias para el sistema de
-- predicción y modelos ML del agente NGX

-- =====================================================================
-- 1. TABLA DE MODELOS PREDICTIVOS
-- =====================================================================
CREATE TABLE IF NOT EXISTS predictive_models (
    -- Identificación
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    model_type VARCHAR(100) NOT NULL, -- objection_prediction, needs_prediction, conversion_prediction, etc.
    version VARCHAR(50) NOT NULL,
    description TEXT,
    
    -- Configuración del modelo
    model_config JSONB NOT NULL DEFAULT '{}',
    feature_names JSONB NOT NULL DEFAULT '[]',
    hyperparameters JSONB DEFAULT '{}',
    
    -- Métricas de performance
    accuracy FLOAT CHECK (accuracy >= 0.0 AND accuracy <= 1.0),
    precision_score FLOAT CHECK (precision_score >= 0.0 AND precision_score <= 1.0),
    recall_score FLOAT CHECK (recall_score >= 0.0 AND recall_score <= 1.0),
    f1_score FLOAT CHECK (f1_score >= 0.0 AND f1_score <= 1.0),
    
    -- Estado del modelo
    status VARCHAR(50) DEFAULT 'training', -- training, active, deprecated, failed
    is_active BOOLEAN DEFAULT false,
    training_date TIMESTAMP,
    last_used TIMESTAMP,
    
    -- Datos de entrenamiento
    training_samples INTEGER,
    validation_samples INTEGER,
    test_samples INTEGER,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(255) DEFAULT 'system'
);

-- Índices para predictive_models
CREATE INDEX IF NOT EXISTS idx_predictive_models_name ON predictive_models(name);
CREATE INDEX IF NOT EXISTS idx_predictive_models_type ON predictive_models(model_type);
CREATE INDEX IF NOT EXISTS idx_predictive_models_status ON predictive_models(status);
CREATE INDEX IF NOT EXISTS idx_predictive_models_active ON predictive_models(is_active) WHERE is_active = true;

-- =====================================================================
-- 2. TABLA DE RESULTADOS DE PREDICCIONES
-- =====================================================================
CREATE TABLE IF NOT EXISTS prediction_results (
    -- Identificación
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_name VARCHAR(255) NOT NULL,
    conversation_id UUID NOT NULL,
    
    -- Tipo y resultado de predicción
    prediction_type VARCHAR(100) NOT NULL, -- objection, needs, conversion, decision
    prediction_value JSONB NOT NULL,
    confidence_score FLOAT NOT NULL CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    
    -- Contexto de la predicción
    input_features JSONB NOT NULL,
    feature_importance JSONB DEFAULT '{}',
    
    -- Estado y timing
    status VARCHAR(50) DEFAULT 'pending', -- pending, completed, failed
    prediction_timestamp TIMESTAMP DEFAULT NOW(),
    processing_time_ms INTEGER,
    
    -- Resultado real (para aprendizaje)
    actual_outcome JSONB,
    outcome_recorded_at TIMESTAMP,
    prediction_accuracy FLOAT CHECK (prediction_accuracy >= 0.0 AND prediction_accuracy <= 1.0),
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    model_version VARCHAR(50),
    
    -- Foreign keys
    FOREIGN KEY (model_name) REFERENCES predictive_models(name) ON DELETE CASCADE
);

-- Índices para prediction_results
CREATE INDEX IF NOT EXISTS idx_prediction_results_model ON prediction_results(model_name);
CREATE INDEX IF NOT EXISTS idx_prediction_results_conversation ON prediction_results(conversation_id);
CREATE INDEX IF NOT EXISTS idx_prediction_results_type ON prediction_results(prediction_type);
CREATE INDEX IF NOT EXISTS idx_prediction_results_status ON prediction_results(status);
CREATE INDEX IF NOT EXISTS idx_prediction_results_timestamp ON prediction_results(prediction_timestamp);
CREATE INDEX IF NOT EXISTS idx_prediction_results_confidence ON prediction_results(confidence_score);

-- =====================================================================
-- 3. TABLA DE DATOS DE ENTRENAMIENTO
-- =====================================================================
CREATE TABLE IF NOT EXISTS model_training_data (
    -- Identificación
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_name VARCHAR(255) NOT NULL,
    
    -- Datos de entrada y salida
    input_data JSONB NOT NULL,
    target_value JSONB NOT NULL,
    
    -- Metadata del dato
    data_source VARCHAR(100), -- conversation, manual, synthetic
    conversation_id UUID,
    quality_score FLOAT DEFAULT 1.0 CHECK (quality_score >= 0.0 AND quality_score <= 1.0),
    
    -- Control de uso
    used_in_training BOOLEAN DEFAULT false,
    training_date TIMESTAMP,
    validation_set BOOLEAN DEFAULT false,
    test_set BOOLEAN DEFAULT false,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(255) DEFAULT 'system',
    
    -- Foreign keys
    FOREIGN KEY (model_name) REFERENCES predictive_models(name) ON DELETE CASCADE
);

-- Índices para model_training_data
CREATE INDEX IF NOT EXISTS idx_model_training_data_model ON model_training_data(model_name);
CREATE INDEX IF NOT EXISTS idx_model_training_data_used ON model_training_data(used_in_training);
CREATE INDEX IF NOT EXISTS idx_model_training_data_created ON model_training_data(created_at);
CREATE INDEX IF NOT EXISTS idx_model_training_data_conversation ON model_training_data(conversation_id);

-- =====================================================================
-- 4. TABLA DE RETROALIMENTACIÓN DE PREDICCIONES
-- =====================================================================
CREATE TABLE IF NOT EXISTS prediction_feedback (
    -- Identificación
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prediction_id UUID NOT NULL,
    
    -- Retroalimentación
    feedback_type VARCHAR(50) NOT NULL, -- accuracy, relevance, usefulness
    feedback_value JSONB NOT NULL,
    feedback_score FLOAT CHECK (feedback_score >= -1.0 AND feedback_score <= 1.0),
    
    -- Contexto
    user_id UUID,
    agent_id VARCHAR(255),
    comments TEXT,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    processed BOOLEAN DEFAULT false,
    processed_at TIMESTAMP,
    
    -- Foreign keys
    FOREIGN KEY (prediction_id) REFERENCES prediction_results(id) ON DELETE CASCADE
);

-- Índices para prediction_feedback
CREATE INDEX IF NOT EXISTS idx_prediction_feedback_prediction ON prediction_feedback(prediction_id);
CREATE INDEX IF NOT EXISTS idx_prediction_feedback_type ON prediction_feedback(feedback_type);
CREATE INDEX IF NOT EXISTS idx_prediction_feedback_processed ON prediction_feedback(processed);
CREATE INDEX IF NOT EXISTS idx_prediction_feedback_created ON prediction_feedback(created_at);

-- =====================================================================
-- 5. TABLA DE SESIONES DE ENTRENAMIENTO
-- =====================================================================
CREATE TABLE IF NOT EXISTS model_training (
    -- Identificación
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_name VARCHAR(255) NOT NULL,
    
    -- Configuración del entrenamiento
    training_config JSONB NOT NULL,
    hyperparameters JSONB NOT NULL,
    feature_engineering JSONB DEFAULT '{}',
    
    -- Estado y progreso
    status VARCHAR(50) DEFAULT 'pending', -- pending, in_progress, completed, failed
    progress FLOAT DEFAULT 0.0 CHECK (progress >= 0.0 AND progress <= 1.0),
    current_epoch INTEGER DEFAULT 0,
    total_epochs INTEGER,
    
    -- Métricas de entrenamiento
    training_loss FLOAT,
    validation_loss FLOAT,
    training_metrics JSONB DEFAULT '{}',
    validation_metrics JSONB DEFAULT '{}',
    
    -- Timing
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds INTEGER,
    
    -- Resultados
    final_model_path TEXT,
    model_size_mb FLOAT,
    improvement_percentage FLOAT,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(255) DEFAULT 'system',
    notes TEXT,
    
    -- Foreign keys
    FOREIGN KEY (model_name) REFERENCES predictive_models(name) ON DELETE CASCADE
);

-- Índices para model_training
CREATE INDEX IF NOT EXISTS idx_model_training_model ON model_training(model_name);
CREATE INDEX IF NOT EXISTS idx_model_training_status ON model_training(status);
CREATE INDEX IF NOT EXISTS idx_model_training_created ON model_training(created_at);

-- =====================================================================
-- 6. TABLA DE FEEDBACK GENERAL (SIMPLIFICADA)
-- =====================================================================
CREATE TABLE IF NOT EXISTS feedback (
    -- Identificación
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Contexto
    model_name VARCHAR(255),
    conversation_id UUID,
    prediction_id UUID,
    
    -- Feedback
    feedback_type VARCHAR(100) NOT NULL,
    feedback_value JSONB NOT NULL,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    user_id UUID,
    session_id VARCHAR(255)
);

-- Índices para feedback
CREATE INDEX IF NOT EXISTS idx_feedback_model ON feedback(model_name);
CREATE INDEX IF NOT EXISTS idx_feedback_conversation ON feedback(conversation_id);
CREATE INDEX IF NOT EXISTS idx_feedback_created ON feedback(created_at);

-- =====================================================================
-- 7. TABLA DE PREDICCIONES HISTÓRICAS
-- =====================================================================
CREATE TABLE IF NOT EXISTS predictions (
    -- Identificación
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Contexto
    model_name VARCHAR(255) NOT NULL,
    conversation_id UUID,
    user_id UUID,
    
    -- Predicción
    prediction_type VARCHAR(100) NOT NULL,
    prediction_data JSONB NOT NULL,
    confidence FLOAT CHECK (confidence >= 0.0 AND confidence <= 1.0),
    
    -- Resultado
    actual_outcome JSONB,
    accuracy FLOAT CHECK (accuracy >= 0.0 AND accuracy <= 1.0),
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    model_version VARCHAR(50)
);

-- Índices para predictions
CREATE INDEX IF NOT EXISTS idx_predictions_model ON predictions(model_name);
CREATE INDEX IF NOT EXISTS idx_predictions_conversation ON predictions(conversation_id);
CREATE INDEX IF NOT EXISTS idx_predictions_created ON predictions(created_at);

-- =====================================================================
-- 8. TRIGGERS PARA UPDATED_AT
-- =====================================================================
CREATE OR REPLACE FUNCTION update_predictive_models_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_predictive_models_updated_at_trigger
BEFORE UPDATE ON predictive_models
FOR EACH ROW EXECUTE FUNCTION update_predictive_models_updated_at();

-- =====================================================================
-- 9. VISTAS ÚTILES
-- =====================================================================

-- Vista de performance de modelos
CREATE OR REPLACE VIEW model_performance_view AS
SELECT 
    pm.name,
    pm.model_type,
    pm.version,
    pm.accuracy,
    pm.f1_score,
    pm.is_active,
    COUNT(DISTINCT pr.id) as total_predictions,
    AVG(pr.confidence_score) as avg_confidence,
    COUNT(DISTINCT pr.id) FILTER (WHERE pr.actual_outcome IS NOT NULL) as predictions_with_outcome,
    AVG(pr.prediction_accuracy) FILTER (WHERE pr.prediction_accuracy IS NOT NULL) as real_accuracy
FROM predictive_models pm
LEFT JOIN prediction_results pr ON pm.name = pr.model_name
GROUP BY pm.name, pm.model_type, pm.version, pm.accuracy, pm.f1_score, pm.is_active;

-- Vista de actividad de entrenamiento
CREATE OR REPLACE VIEW training_activity_view AS
SELECT 
    mt.model_name,
    COUNT(*) as training_sessions,
    COUNT(*) FILTER (WHERE status = 'completed') as successful_trainings,
    COUNT(*) FILTER (WHERE status = 'failed') as failed_trainings,
    AVG(duration_seconds) FILTER (WHERE status = 'completed') as avg_training_time_seconds,
    MAX(completed_at) as last_training_date,
    AVG(improvement_percentage) FILTER (WHERE improvement_percentage IS NOT NULL) as avg_improvement
FROM model_training mt
GROUP BY mt.model_name;

-- =====================================================================
-- 10. DATOS INICIALES
-- =====================================================================

-- Insertar modelos predictivos iniciales
INSERT INTO predictive_models (name, model_type, version, description, status, is_active) VALUES
('objection_predictor_v1', 'objection_prediction', '1.0.0', 'Predice tipos de objeciones basado en contexto de conversación', 'active', true),
('needs_analyzer_v1', 'needs_prediction', '1.0.0', 'Analiza y predice necesidades del cliente', 'active', true),
('conversion_predictor_v1', 'conversion_prediction', '1.0.0', 'Predice probabilidad de conversión en tiempo real', 'active', true),
('decision_engine_v1', 'decision_engine', '1.0.0', 'Motor de decisiones para estrategias de conversación', 'active', true)
ON CONFLICT (name) DO NOTHING;

-- =====================================================================
-- COMENTARIOS PARA DOCUMENTACIÓN
-- =====================================================================
COMMENT ON TABLE predictive_models IS 'Modelos ML para predicciones en tiempo real';
COMMENT ON TABLE prediction_results IS 'Resultados de todas las predicciones realizadas';
COMMENT ON TABLE model_training_data IS 'Datos utilizados para entrenar modelos';
COMMENT ON TABLE prediction_feedback IS 'Retroalimentación sobre calidad de predicciones';
COMMENT ON TABLE model_training IS 'Registro de sesiones de entrenamiento de modelos';

-- =====================================================================
-- Script completado exitosamente
-- =====================================================================