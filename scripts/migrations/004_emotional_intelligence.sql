-- =====================================================================
-- MIGRACIÓN 004: SISTEMA DE INTELIGENCIA EMOCIONAL
-- =====================================================================
-- Este script crea las tablas para análisis emocional, personalidad
-- y patrones de comportamiento del agente NGX

-- =====================================================================
-- 1. TABLA DE ANÁLISIS EMOCIONAL
-- =====================================================================
CREATE TABLE IF NOT EXISTS emotional_analysis (
    -- Identificación
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL,
    message_id UUID,
    
    -- Análisis emocional principal
    primary_emotion VARCHAR(50) NOT NULL, -- joy, sadness, anger, fear, surprise, disgust, neutral
    emotion_confidence FLOAT NOT NULL CHECK (emotion_confidence >= 0.0 AND emotion_confidence <= 1.0),
    emotion_intensity FLOAT NOT NULL CHECK (emotion_intensity >= 0.0 AND emotion_intensity <= 1.0),
    
    -- Análisis detallado
    emotion_scores JSONB NOT NULL DEFAULT '{}', -- Scores para cada emoción
    sentiment_score FLOAT CHECK (sentiment_score >= -1.0 AND sentiment_score <= 1.0),
    sentiment_magnitude FLOAT CHECK (sentiment_magnitude >= 0.0),
    
    -- Indicadores adicionales
    stress_level FLOAT CHECK (stress_level >= 0.0 AND stress_level <= 1.0),
    engagement_level FLOAT CHECK (engagement_level >= 0.0 AND engagement_level <= 1.0),
    trust_level FLOAT CHECK (trust_level >= 0.0 AND trust_level <= 1.0),
    
    -- Análisis contextual
    emotional_triggers JSONB DEFAULT '[]', -- Palabras o frases que triggerean emociones
    emotional_shift BOOLEAN DEFAULT false, -- Si hubo un cambio emocional significativo
    shift_direction VARCHAR(20), -- positive, negative, neutral
    
    -- Respuesta adaptativa
    recommended_tone VARCHAR(50), -- empathetic, professional, enthusiastic, calm
    recommended_approach JSONB DEFAULT '{}', -- Estrategias recomendadas
    
    -- Metadata
    analyzed_at TIMESTAMP DEFAULT NOW(),
    analyzer_version VARCHAR(50) DEFAULT 'emotional_intelligence_v1',
    processing_time_ms INTEGER,
    
    -- Índices únicos para evitar duplicados
    UNIQUE(conversation_id, message_id)
);

-- Índices para emotional_analysis
CREATE INDEX IF NOT EXISTS idx_emotional_analysis_conversation ON emotional_analysis(conversation_id);
CREATE INDEX IF NOT EXISTS idx_emotional_analysis_emotion ON emotional_analysis(primary_emotion);
CREATE INDEX IF NOT EXISTS idx_emotional_analysis_analyzed_at ON emotional_analysis(analyzed_at);
CREATE INDEX IF NOT EXISTS idx_emotional_analysis_stress ON emotional_analysis(stress_level);
CREATE INDEX IF NOT EXISTS idx_emotional_analysis_engagement ON emotional_analysis(engagement_level);

-- =====================================================================
-- 2. TABLA DE ANÁLISIS DE PERSONALIDAD
-- =====================================================================
CREATE TABLE IF NOT EXISTS personality_analysis (
    -- Identificación
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL,
    user_id UUID,
    
    -- Modelo Big Five (OCEAN)
    openness FLOAT CHECK (openness >= 0.0 AND openness <= 1.0),
    conscientiousness FLOAT CHECK (conscientiousness >= 0.0 AND conscientiousness <= 1.0),
    extraversion FLOAT CHECK (extraversion >= 0.0 AND extraversion <= 1.0),
    agreeableness FLOAT CHECK (agreeableness >= 0.0 AND agreeableness <= 1.0),
    neuroticism FLOAT CHECK (neuroticism >= 0.0 AND neuroticism <= 1.0),
    
    -- Estilos de comunicación
    communication_style VARCHAR(50), -- direct, analytical, expressive, amiable
    learning_style VARCHAR(50), -- visual, auditory, kinesthetic, reading
    decision_style VARCHAR(50), -- rational, intuitive, dependent, avoidant
    
    -- Motivadores principales
    primary_motivators JSONB DEFAULT '[]', -- achievement, affiliation, power, security
    pain_points JSONB DEFAULT '[]',
    values JSONB DEFAULT '[]',
    
    -- Preferencias detectadas
    preferred_pace VARCHAR(20), -- fast, moderate, slow
    detail_orientation VARCHAR(20), -- high, medium, low
    risk_tolerance VARCHAR(20), -- high, medium, low
    
    -- Análisis de comportamiento
    behavioral_patterns JSONB DEFAULT '{}',
    conversation_dynamics JSONB DEFAULT '{}',
    
    -- Confianza del análisis
    analysis_confidence FLOAT CHECK (analysis_confidence >= 0.0 AND analysis_confidence <= 1.0),
    data_points_analyzed INTEGER,
    
    -- Metadata
    analyzed_at TIMESTAMP DEFAULT NOW(),
    last_updated TIMESTAMP DEFAULT NOW(),
    analyzer_version VARCHAR(50) DEFAULT 'personality_analyzer_v1'
);

-- Índices para personality_analysis
CREATE INDEX IF NOT EXISTS idx_personality_analysis_conversation ON personality_analysis(conversation_id);
CREATE INDEX IF NOT EXISTS idx_personality_analysis_user ON personality_analysis(user_id);
CREATE INDEX IF NOT EXISTS idx_personality_analysis_style ON personality_analysis(communication_style);
CREATE INDEX IF NOT EXISTS idx_personality_analysis_analyzed_at ON personality_analysis(analyzed_at);

-- =====================================================================
-- 3. TABLA DE PATRONES DE CONVERSACIÓN
-- =====================================================================
CREATE TABLE IF NOT EXISTS conversation_patterns (
    -- Identificación
    pattern_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern_name VARCHAR(255) NOT NULL,
    pattern_category VARCHAR(100) NOT NULL, -- behavioral, linguistic, emotional, conversion
    
    -- Definición del patrón
    pattern_definition JSONB NOT NULL,
    pattern_conditions JSONB NOT NULL,
    pattern_indicators JSONB NOT NULL DEFAULT '[]',
    
    -- Estadísticas del patrón
    occurrence_count INTEGER DEFAULT 0,
    success_rate FLOAT CHECK (success_rate >= 0.0 AND success_rate <= 1.0),
    confidence_score FLOAT CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    
    -- Aplicabilidad
    applicable_contexts JSONB DEFAULT '[]', -- Contextos donde aplica el patrón
    applicable_personalities JSONB DEFAULT '[]', -- Tipos de personalidad
    applicable_emotions JSONB DEFAULT '[]', -- Estados emocionales
    
    -- Impacto y recomendaciones
    impact_on_conversion FLOAT CHECK (impact_on_conversion >= -1.0 AND impact_on_conversion <= 1.0),
    recommended_responses JSONB DEFAULT '[]',
    avoid_responses JSONB DEFAULT '[]',
    
    -- Evolución del patrón
    first_detected TIMESTAMP DEFAULT NOW(),
    last_detected TIMESTAMP DEFAULT NOW(),
    evolution_trend VARCHAR(20), -- increasing, stable, decreasing
    
    -- Control de calidad
    is_active BOOLEAN DEFAULT true,
    requires_review BOOLEAN DEFAULT false,
    review_notes TEXT,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(255) DEFAULT 'pattern_recognition_engine'
);

-- Índices para conversation_patterns
CREATE INDEX IF NOT EXISTS idx_conversation_patterns_name ON conversation_patterns(pattern_name);
CREATE INDEX IF NOT EXISTS idx_conversation_patterns_category ON conversation_patterns(pattern_category);
CREATE INDEX IF NOT EXISTS idx_conversation_patterns_active ON conversation_patterns(is_active);
CREATE INDEX IF NOT EXISTS idx_conversation_patterns_confidence ON conversation_patterns(confidence_score);
CREATE INDEX IF NOT EXISTS idx_conversation_patterns_impact ON conversation_patterns(impact_on_conversion);

-- =====================================================================
-- 4. TABLA DE MAPEO CONVERSACIÓN-PATRÓN
-- =====================================================================
CREATE TABLE IF NOT EXISTS conversation_pattern_matches (
    -- Identificación
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL,
    pattern_id UUID NOT NULL,
    
    -- Detalles del match
    match_confidence FLOAT NOT NULL CHECK (match_confidence >= 0.0 AND match_confidence <= 1.0),
    match_details JSONB DEFAULT '{}',
    triggered_at TIMESTAMP DEFAULT NOW(),
    
    -- Impacto
    impact_on_conversation VARCHAR(50), -- positive, negative, neutral
    response_effectiveness FLOAT CHECK (response_effectiveness >= 0.0 AND response_effectiveness <= 1.0),
    
    -- Foreign keys
    FOREIGN KEY (pattern_id) REFERENCES conversation_patterns(pattern_id) ON DELETE CASCADE,
    
    -- Evitar duplicados
    UNIQUE(conversation_id, pattern_id, triggered_at)
);

-- Índices para conversation_pattern_matches
CREATE INDEX IF NOT EXISTS idx_pattern_matches_conversation ON conversation_pattern_matches(conversation_id);
CREATE INDEX IF NOT EXISTS idx_pattern_matches_pattern ON conversation_pattern_matches(pattern_id);
CREATE INDEX IF NOT EXISTS idx_pattern_matches_triggered ON conversation_pattern_matches(triggered_at);

-- =====================================================================
-- 5. TABLA DE EVOLUCIÓN EMOCIONAL
-- =====================================================================
CREATE TABLE IF NOT EXISTS emotional_evolution (
    -- Identificación
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL,
    
    -- Timeline emocional
    emotional_timeline JSONB NOT NULL DEFAULT '[]', -- Array de estados emocionales con timestamps
    
    -- Métricas de evolución
    initial_emotion VARCHAR(50),
    final_emotion VARCHAR(50),
    peak_positive_emotion VARCHAR(50),
    peak_negative_emotion VARCHAR(50),
    
    -- Análisis de volatilidad
    emotional_volatility FLOAT CHECK (emotional_volatility >= 0.0 AND emotional_volatility <= 1.0),
    stability_score FLOAT CHECK (stability_score >= 0.0 AND stability_score <= 1.0),
    
    -- Puntos de inflexión
    turning_points JSONB DEFAULT '[]', -- Momentos clave de cambio emocional
    critical_moments JSONB DEFAULT '[]', -- Momentos que requirieron intervención
    
    -- Resumen
    overall_sentiment VARCHAR(20), -- positive, negative, neutral, mixed
    emotional_journey_quality FLOAT CHECK (emotional_journey_quality >= 0.0 AND emotional_journey_quality <= 1.0),
    
    -- Metadata
    analyzed_at TIMESTAMP DEFAULT NOW(),
    
    -- Único por conversación
    UNIQUE(conversation_id)
);

-- Índices para emotional_evolution
CREATE INDEX IF NOT EXISTS idx_emotional_evolution_conversation ON emotional_evolution(conversation_id);
CREATE INDEX IF NOT EXISTS idx_emotional_evolution_sentiment ON emotional_evolution(overall_sentiment);
CREATE INDEX IF NOT EXISTS idx_emotional_evolution_quality ON emotional_evolution(emotional_journey_quality);

-- =====================================================================
-- 6. TRIGGERS PARA ACTUALIZACIÓN AUTOMÁTICA
-- =====================================================================

-- Trigger para actualizar personality_analysis.last_updated
CREATE OR REPLACE FUNCTION update_personality_analysis_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_updated = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_personality_analysis_timestamp_trigger
BEFORE UPDATE ON personality_analysis
FOR EACH ROW EXECUTE FUNCTION update_personality_analysis_timestamp();

-- Trigger para actualizar conversation_patterns.updated_at
CREATE OR REPLACE FUNCTION update_conversation_patterns_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    NEW.occurrence_count = NEW.occurrence_count + 1;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_conversation_patterns_timestamp_trigger
BEFORE UPDATE ON conversation_patterns
FOR EACH ROW EXECUTE FUNCTION update_conversation_patterns_timestamp();

-- =====================================================================
-- 7. VISTAS ANALÍTICAS
-- =====================================================================

-- Vista de resumen emocional por conversación
CREATE OR REPLACE VIEW emotional_summary_view AS
SELECT 
    ea.conversation_id,
    COUNT(*) as total_analyses,
    AVG(ea.emotion_confidence) as avg_confidence,
    AVG(ea.sentiment_score) as avg_sentiment,
    AVG(ea.stress_level) as avg_stress,
    AVG(ea.engagement_level) as avg_engagement,
    AVG(ea.trust_level) as avg_trust,
    MODE() WITHIN GROUP (ORDER BY ea.primary_emotion) as dominant_emotion,
    COUNT(DISTINCT ea.primary_emotion) as emotion_variety
FROM emotional_analysis ea
GROUP BY ea.conversation_id;

-- Vista de patrones más efectivos
CREATE OR REPLACE VIEW effective_patterns_view AS
SELECT 
    cp.pattern_name,
    cp.pattern_category,
    cp.occurrence_count,
    cp.success_rate,
    cp.impact_on_conversion,
    COUNT(DISTINCT cpm.conversation_id) as conversations_affected,
    AVG(cpm.response_effectiveness) as avg_effectiveness
FROM conversation_patterns cp
JOIN conversation_pattern_matches cpm ON cp.pattern_id = cpm.pattern_id
WHERE cp.is_active = true
GROUP BY cp.pattern_id, cp.pattern_name, cp.pattern_category, 
         cp.occurrence_count, cp.success_rate, cp.impact_on_conversion
ORDER BY cp.impact_on_conversion DESC, cp.success_rate DESC;

-- =====================================================================
-- 8. FUNCIONES ÚTILES
-- =====================================================================

-- Función para calcular distancia emocional entre dos estados
CREATE OR REPLACE FUNCTION calculate_emotional_distance(
    emotion1 JSONB,
    emotion2 JSONB
) RETURNS FLOAT AS $$
DECLARE
    distance FLOAT := 0;
    key TEXT;
BEGIN
    FOR key IN SELECT jsonb_object_keys(emotion1)
    LOOP
        distance := distance + POWER(
            COALESCE((emotion1->key)::float, 0) - 
            COALESCE((emotion2->key)::float, 0), 2
        );
    END LOOP;
    RETURN SQRT(distance);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- =====================================================================
-- 9. DATOS INICIALES
-- =====================================================================

-- Insertar patrones comunes iniciales
INSERT INTO conversation_patterns (pattern_name, pattern_category, pattern_definition, pattern_conditions, confidence_score) VALUES
('price_objection_pattern', 'behavioral', 
 '{"description": "Cliente menciona precio como objeción principal"}', 
 '{"keywords": ["caro", "precio", "costo", "presupuesto"], "min_occurrences": 1}', 
 0.85),
('high_engagement_pattern', 'behavioral',
 '{"description": "Cliente hace múltiples preguntas y muestra interés activo"}',
 '{"min_questions": 3, "response_time": "fast", "sentiment": "positive"}',
 0.90),
('trust_building_needed', 'emotional',
 '{"description": "Cliente muestra escepticismo y necesita construcción de confianza"}',
 '{"trust_level": "low", "keywords": ["no sé", "dudoso", "seguro?"], "sentiment": "neutral_negative"}',
 0.80)
ON CONFLICT DO NOTHING;

-- =====================================================================
-- COMENTARIOS DE DOCUMENTACIÓN
-- =====================================================================
COMMENT ON TABLE emotional_analysis IS 'Análisis emocional detallado de cada mensaje en conversaciones';
COMMENT ON TABLE personality_analysis IS 'Perfil de personalidad construido durante la conversación';
COMMENT ON TABLE conversation_patterns IS 'Patrones de comportamiento identificados en conversaciones';
COMMENT ON TABLE emotional_evolution IS 'Evolución emocional a lo largo de cada conversación';

-- =====================================================================
-- Script completado exitosamente
-- =====================================================================