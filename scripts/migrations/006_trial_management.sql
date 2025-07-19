-- =====================================================================
-- MIGRACIÓN 006: SISTEMA DE GESTIÓN DE TRIALS Y DEMOS
-- =====================================================================
-- Este script crea las tablas para el sistema de demos en vivo,
-- trials pagados y gestión de conversión de usuarios

-- =====================================================================
-- 1. TABLA DE USUARIOS DE TRIAL
-- =====================================================================
CREATE TABLE IF NOT EXISTS trial_users (
    -- Identificación
    trial_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    conversation_id UUID,
    
    -- Información del trial
    trial_tier VARCHAR(50) NOT NULL, -- essential, pro, elite, premium
    trial_type VARCHAR(50) NOT NULL, -- free_trial, paid_trial, demo_access
    trial_price DECIMAL(10,2) DEFAULT 0.00,
    
    -- Duración del trial
    trial_start_date TIMESTAMP NOT NULL DEFAULT NOW(),
    trial_end_date TIMESTAMP NOT NULL,
    trial_duration_days INTEGER GENERATED ALWAYS AS (
        EXTRACT(DAY FROM trial_end_date - trial_start_date)
    ) STORED,
    
    -- Estado del trial
    status VARCHAR(50) DEFAULT 'active', -- active, expired, converted, cancelled
    activation_method VARCHAR(50), -- immediate, email_confirmation, manual
    activated_at TIMESTAMP,
    
    -- Datos de conversión
    converted_to_paid BOOLEAN DEFAULT false,
    conversion_date TIMESTAMP,
    converted_tier VARCHAR(50),
    conversion_value DECIMAL(10,2),
    
    -- Engagement metrics
    login_count INTEGER DEFAULT 0,
    last_login_at TIMESTAMP,
    features_used JSONB DEFAULT '[]',
    engagement_score FLOAT CHECK (engagement_score >= 0.0 AND engagement_score <= 10.0),
    
    -- Milestones alcanzados
    milestones_completed JSONB DEFAULT '[]',
    onboarding_completed BOOLEAN DEFAULT false,
    onboarding_completion_time_minutes INTEGER,
    
    -- Comunicación
    emails_sent INTEGER DEFAULT 0,
    emails_opened INTEGER DEFAULT 0,
    touchpoints_completed JSONB DEFAULT '[]',
    
    -- Razones de cancelación/no conversión
    cancellation_reason VARCHAR(255),
    cancellation_feedback TEXT,
    exit_survey_completed BOOLEAN DEFAULT false,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    source VARCHAR(100), -- organic, paid_ad, referral, sales_call
    referral_code VARCHAR(50),
    utm_source VARCHAR(100),
    utm_medium VARCHAR(100),
    utm_campaign VARCHAR(100)
);

-- Índices para trial_users
CREATE INDEX IF NOT EXISTS idx_trial_users_user ON trial_users(user_id);
CREATE INDEX IF NOT EXISTS idx_trial_users_status ON trial_users(status);
CREATE INDEX IF NOT EXISTS idx_trial_users_dates ON trial_users(trial_start_date, trial_end_date);
CREATE INDEX IF NOT EXISTS idx_trial_users_converted ON trial_users(converted_to_paid);
CREATE INDEX IF NOT EXISTS idx_trial_users_tier ON trial_users(trial_tier);
CREATE INDEX IF NOT EXISTS idx_trial_users_engagement ON trial_users(engagement_score);

-- =====================================================================
-- 2. TABLA DE EVENTOS DE DEMO
-- =====================================================================
CREATE TABLE IF NOT EXISTS demo_events (
    -- Identificación
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL,
    conversation_id UUID,
    user_id UUID,
    
    -- Información del evento
    event_type VARCHAR(100) NOT NULL, -- demo_started, feature_shown, interaction, demo_completed
    event_name VARCHAR(255) NOT NULL,
    event_category VARCHAR(100), -- hie_showcase, roi_calculation, feature_demo, testimonial
    
    -- Detalles del evento
    event_data JSONB NOT NULL DEFAULT '{}',
    duration_seconds INTEGER,
    
    -- Contexto de la demo
    demo_type VARCHAR(50) NOT NULL, -- energy_boost, focus_enhancement, stress_reduction, cognitive
    profession VARCHAR(100),
    customization_level VARCHAR(20), -- generic, personalized, highly_personalized
    
    -- Interacción y engagement
    user_interaction BOOLEAN DEFAULT false,
    interaction_type VARCHAR(50), -- click, hover, question, response
    interaction_quality FLOAT CHECK (interaction_quality >= 0.0 AND interaction_quality <= 1.0),
    
    -- Impacto
    engagement_impact FLOAT CHECK (engagement_impact >= -1.0 AND engagement_impact <= 1.0),
    conversion_impact FLOAT CHECK (conversion_impact >= -1.0 AND conversion_impact <= 1.0),
    belief_shift_indicator FLOAT CHECK (belief_shift_indicator >= 0.0 AND belief_shift_indicator <= 1.0),
    
    -- Metadata
    timestamp TIMESTAMP DEFAULT NOW(),
    device_type VARCHAR(50),
    browser VARCHAR(50),
    
    -- Índice compuesto para sesión
    UNIQUE(session_id, event_type, timestamp)
);

-- Índices para demo_events
CREATE INDEX IF NOT EXISTS idx_demo_events_session ON demo_events(session_id);
CREATE INDEX IF NOT EXISTS idx_demo_events_user ON demo_events(user_id);
CREATE INDEX IF NOT EXISTS idx_demo_events_type ON demo_events(event_type);
CREATE INDEX IF NOT EXISTS idx_demo_events_timestamp ON demo_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_demo_events_demo_type ON demo_events(demo_type);
CREATE INDEX IF NOT EXISTS idx_demo_events_conversion_impact ON demo_events(conversion_impact);

-- =====================================================================
-- 3. TABLA DE SESIONES DE DEMO
-- =====================================================================
CREATE TABLE IF NOT EXISTS demo_sessions (
    -- Identificación
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL,
    user_id UUID,
    
    -- Configuración de la demo
    demo_type VARCHAR(50) NOT NULL,
    demo_mode VARCHAR(50) NOT NULL, -- interactive, passive, guided
    personalization_data JSONB DEFAULT '{}',
    
    -- Timing
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    total_duration_seconds INTEGER,
    
    -- Métricas de la sesión
    total_events INTEGER DEFAULT 0,
    interaction_count INTEGER DEFAULT 0,
    features_demonstrated JSONB DEFAULT '[]',
    key_points_covered JSONB DEFAULT '[]',
    
    -- Resultados
    completion_rate FLOAT CHECK (completion_rate >= 0.0 AND completion_rate <= 1.0),
    engagement_score FLOAT CHECK (engagement_score >= 0.0 AND engagement_score <= 10.0),
    effectiveness_score FLOAT CHECK (effectiveness_score >= 0.0 AND effectiveness_score <= 10.0),
    
    -- Conversión
    led_to_trial BOOLEAN DEFAULT false,
    led_to_purchase BOOLEAN DEFAULT false,
    post_demo_action VARCHAR(100), -- started_trial, scheduled_call, requested_info, no_action
    
    -- Feedback
    user_feedback_score INTEGER CHECK (user_feedback_score >= 1 AND user_feedback_score <= 10),
    user_feedback_text TEXT,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    demo_version VARCHAR(50) DEFAULT 'v1.0'
);

-- Índices para demo_sessions
CREATE INDEX IF NOT EXISTS idx_demo_sessions_conversation ON demo_sessions(conversation_id);
CREATE INDEX IF NOT EXISTS idx_demo_sessions_user ON demo_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_demo_sessions_completed ON demo_sessions(completed_at);
CREATE INDEX IF NOT EXISTS idx_demo_sessions_effectiveness ON demo_sessions(effectiveness_score);

-- =====================================================================
-- 4. TABLA DE TOUCHPOINTS PROGRAMADOS
-- =====================================================================
CREATE TABLE IF NOT EXISTS scheduled_touchpoints (
    -- Identificación
    touchpoint_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trial_id UUID NOT NULL,
    user_id UUID NOT NULL,
    
    -- Configuración del touchpoint
    touchpoint_type VARCHAR(100) NOT NULL, -- welcome, feature_highlight, milestone, renewal_reminder
    touchpoint_day INTEGER NOT NULL, -- Día del trial cuando debe ocurrir
    
    -- Contenido
    channel VARCHAR(50) NOT NULL, -- email, in_app, sms, push
    template_id VARCHAR(100),
    personalization_data JSONB DEFAULT '{}',
    
    -- Programación
    scheduled_for TIMESTAMP NOT NULL,
    
    -- Estado
    status VARCHAR(50) DEFAULT 'pending', -- pending, sent, delivered, failed, cancelled
    sent_at TIMESTAMP,
    delivered_at TIMESTAMP,
    opened_at TIMESTAMP,
    clicked_at TIMESTAMP,
    
    -- Respuesta
    user_action VARCHAR(100), -- clicked, replied, ignored, unsubscribed
    action_timestamp TIMESTAMP,
    
    -- Efectividad
    engagement_impact FLOAT CHECK (engagement_impact >= -1.0 AND engagement_impact <= 1.0),
    conversion_impact FLOAT CHECK (conversion_impact >= -1.0 AND conversion_impact <= 1.0),
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    retry_count INTEGER DEFAULT 0,
    error_message TEXT,
    
    -- Foreign key
    FOREIGN KEY (trial_id) REFERENCES trial_users(trial_id) ON DELETE CASCADE
);

-- Índices para scheduled_touchpoints
CREATE INDEX IF NOT EXISTS idx_touchpoints_trial ON scheduled_touchpoints(trial_id);
CREATE INDEX IF NOT EXISTS idx_touchpoints_user ON scheduled_touchpoints(user_id);
CREATE INDEX IF NOT EXISTS idx_touchpoints_scheduled ON scheduled_touchpoints(scheduled_for);
CREATE INDEX IF NOT EXISTS idx_touchpoints_status ON scheduled_touchpoints(status);
CREATE INDEX IF NOT EXISTS idx_touchpoints_type ON scheduled_touchpoints(touchpoint_type);

-- =====================================================================
-- 5. TABLA DE EVENTOS DE TRIAL
-- =====================================================================
CREATE TABLE IF NOT EXISTS trial_events (
    -- Identificación
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trial_id UUID NOT NULL,
    user_id UUID NOT NULL,
    
    -- Información del evento
    event_type VARCHAR(100) NOT NULL, -- login, feature_used, milestone_reached, upgrade_clicked
    event_name VARCHAR(255) NOT NULL,
    event_category VARCHAR(100),
    
    -- Detalles
    event_data JSONB DEFAULT '{}',
    session_id VARCHAR(255),
    
    -- Impacto
    engagement_value FLOAT DEFAULT 1.0,
    conversion_signal FLOAT CHECK (conversion_signal >= 0.0 AND conversion_signal <= 1.0),
    
    -- Metadata
    timestamp TIMESTAMP DEFAULT NOW(),
    ip_address INET,
    user_agent TEXT,
    
    -- Foreign key
    FOREIGN KEY (trial_id) REFERENCES trial_users(trial_id) ON DELETE CASCADE
);

-- Índices para trial_events
CREATE INDEX IF NOT EXISTS idx_trial_events_trial ON trial_events(trial_id);
CREATE INDEX IF NOT EXISTS idx_trial_events_user ON trial_events(user_id);
CREATE INDEX IF NOT EXISTS idx_trial_events_type ON trial_events(event_type);
CREATE INDEX IF NOT EXISTS idx_trial_events_timestamp ON trial_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_trial_events_category ON trial_events(event_category);

-- =====================================================================
-- 6. TABLA DE CONFIGURACIÓN DE TRIALS
-- =====================================================================
CREATE TABLE IF NOT EXISTS trial_configuration (
    -- Identificación
    config_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tier VARCHAR(50) NOT NULL UNIQUE, -- essential, pro, elite, premium
    
    -- Configuración del trial
    trial_duration_days INTEGER NOT NULL DEFAULT 14,
    trial_price DECIMAL(10,2) DEFAULT 0.00,
    
    -- Features incluidas
    included_features JSONB NOT NULL DEFAULT '[]',
    feature_limits JSONB DEFAULT '{}',
    
    -- Milestones y gamificación
    milestone_definitions JSONB NOT NULL DEFAULT '[]',
    reward_system JSONB DEFAULT '{}',
    
    -- Estrategia de conversión
    touchpoint_schedule JSONB NOT NULL DEFAULT '[]', -- Array de touchpoints por día
    conversion_triggers JSONB DEFAULT '[]', -- Eventos que triggerean ofertas
    
    -- Ofertas de conversión
    standard_offer JSONB DEFAULT '{}',
    early_bird_offer JSONB DEFAULT '{}',
    last_chance_offer JSONB DEFAULT '{}',
    
    -- Configuración de comunicación
    email_templates JSONB DEFAULT '{}',
    in_app_messages JSONB DEFAULT '{}',
    
    -- Estado
    is_active BOOLEAN DEFAULT true,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(255) DEFAULT 'system'
);

-- =====================================================================
-- 7. TRIGGERS Y FUNCIONES
-- =====================================================================

-- Trigger para actualizar updated_at en trial_users
CREATE OR REPLACE FUNCTION update_trial_users_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    -- Actualizar engagement score basado en actividad
    IF NEW.login_count > OLD.login_count THEN
        NEW.engagement_score = LEAST(10.0, COALESCE(NEW.engagement_score, 0) + 0.5);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_trial_users_timestamp_trigger
BEFORE UPDATE ON trial_users
FOR EACH ROW EXECUTE FUNCTION update_trial_users_timestamp();

-- Función para calcular probabilidad de conversión
CREATE OR REPLACE FUNCTION calculate_trial_conversion_probability(
    trial_id UUID
) RETURNS FLOAT AS $$
DECLARE
    probability FLOAT := 0.0;
    trial_data RECORD;
    engagement_weight FLOAT := 0.3;
    milestone_weight FLOAT := 0.3;
    usage_weight FLOAT := 0.4;
BEGIN
    SELECT * INTO trial_data FROM trial_users WHERE trial_users.trial_id = $1;
    
    IF FOUND THEN
        probability := (
            COALESCE(trial_data.engagement_score / 10.0, 0) * engagement_weight +
            COALESCE(jsonb_array_length(trial_data.milestones_completed)::FLOAT / 10.0, 0) * milestone_weight +
            LEAST(trial_data.login_count::FLOAT / 20.0, 1.0) * usage_weight
        );
    END IF;
    
    RETURN LEAST(probability, 1.0);
END;
$$ LANGUAGE plpgsql;

-- =====================================================================
-- 8. VISTAS ANALÍTICAS
-- =====================================================================

-- Vista de performance de trials por tier
CREATE OR REPLACE VIEW trial_performance_by_tier AS
SELECT 
    trial_tier,
    COUNT(*) as total_trials,
    COUNT(*) FILTER (WHERE converted_to_paid = true) as conversions,
    ROUND(COUNT(*) FILTER (WHERE converted_to_paid = true)::NUMERIC / 
          NULLIF(COUNT(*)::NUMERIC, 0) * 100, 2) as conversion_rate,
    AVG(engagement_score) as avg_engagement,
    AVG(EXTRACT(DAY FROM conversion_date - trial_start_date)) 
        FILTER (WHERE converted_to_paid = true) as avg_days_to_conversion,
    AVG(conversion_value) FILTER (WHERE converted_to_paid = true) as avg_conversion_value
FROM trial_users
GROUP BY trial_tier
ORDER BY conversion_rate DESC;

-- Vista de efectividad de demos
CREATE OR REPLACE VIEW demo_effectiveness AS
SELECT 
    ds.demo_type,
    COUNT(DISTINCT ds.session_id) as total_sessions,
    AVG(ds.completion_rate) as avg_completion_rate,
    AVG(ds.engagement_score) as avg_engagement,
    AVG(ds.effectiveness_score) as avg_effectiveness,
    COUNT(*) FILTER (WHERE ds.led_to_trial = true) as trials_started,
    COUNT(*) FILTER (WHERE ds.led_to_purchase = true) as direct_purchases,
    ROUND(COUNT(*) FILTER (WHERE ds.led_to_trial = true)::NUMERIC / 
          NULLIF(COUNT(*)::NUMERIC, 0) * 100, 2) as trial_conversion_rate
FROM demo_sessions ds
WHERE ds.completed_at IS NOT NULL
GROUP BY ds.demo_type
ORDER BY avg_effectiveness DESC;

-- Vista de touchpoints más efectivos
CREATE OR REPLACE VIEW effective_touchpoints AS
SELECT 
    touchpoint_type,
    touchpoint_day,
    COUNT(*) as total_sent,
    COUNT(*) FILTER (WHERE status = 'delivered') as delivered,
    COUNT(*) FILTER (WHERE opened_at IS NOT NULL) as opened,
    COUNT(*) FILTER (WHERE clicked_at IS NOT NULL) as clicked,
    AVG(engagement_impact) as avg_engagement_impact,
    AVG(conversion_impact) as avg_conversion_impact
FROM scheduled_touchpoints
WHERE status != 'pending'
GROUP BY touchpoint_type, touchpoint_day
ORDER BY avg_conversion_impact DESC NULLS LAST;

-- =====================================================================
-- 9. DATOS INICIALES
-- =====================================================================

-- Configuración inicial de trials
INSERT INTO trial_configuration (tier, trial_duration_days, trial_price, included_features, touchpoint_schedule) VALUES
('essential', 14, 0.00, 
 '["basic_tracking", "weekly_insights", "community_access"]',
 '[{"day": 1, "type": "welcome"}, {"day": 3, "type": "feature_highlight"}, {"day": 7, "type": "milestone"}, {"day": 12, "type": "renewal_reminder"}]'),
 
('pro', 14, 0.00,
 '["advanced_tracking", "daily_insights", "personalized_recommendations", "priority_support"]',
 '[{"day": 1, "type": "welcome"}, {"day": 2, "type": "onboarding"}, {"day": 5, "type": "feature_highlight"}, {"day": 10, "type": "success_story"}, {"day": 13, "type": "special_offer"}]'),
 
('elite', 14, 29.00,
 '["full_tracking", "real_time_insights", "ai_coach", "1on1_sessions", "custom_programs"]',
 '[{"day": 1, "type": "vip_welcome"}, {"day": 3, "type": "personal_coach_intro"}, {"day": 7, "type": "progress_review"}, {"day": 10, "type": "exclusive_content"}, {"day": 13, "type": "conversion_call"}]')
ON CONFLICT (tier) DO NOTHING;

-- =====================================================================
-- COMENTARIOS DE DOCUMENTACIÓN
-- =====================================================================
COMMENT ON TABLE trial_users IS 'Gestión completa de usuarios en período de trial';
COMMENT ON TABLE demo_events IS 'Eventos detallados durante demos interactivas';
COMMENT ON TABLE demo_sessions IS 'Sesiones completas de demostración con métricas';
COMMENT ON TABLE scheduled_touchpoints IS 'Comunicaciones programadas durante el trial';
COMMENT ON TABLE trial_events IS 'Todos los eventos de usuario durante el trial';
COMMENT ON TABLE trial_configuration IS 'Configuración por tier de trial';

-- =====================================================================
-- Script completado exitosamente
-- =====================================================================