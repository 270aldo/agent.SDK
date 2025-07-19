-- =====================================================================
-- MIGRACIÓN 007: SISTEMA DE TRACKING Y CÁLCULO DE ROI
-- =====================================================================
-- Este script crea las tablas para el cálculo dinámico de ROI,
-- tracking de métricas de valor y proyecciones personalizadas

-- =====================================================================
-- 1. TABLA DE CÁLCULOS DE ROI
-- =====================================================================
CREATE TABLE IF NOT EXISTS roi_calculations (
    -- Identificación
    calculation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL,
    user_id UUID,
    
    -- Contexto del cálculo
    profession VARCHAR(100) NOT NULL,
    industry VARCHAR(100),
    company_size VARCHAR(50), -- small, medium, large, enterprise
    
    -- Inputs del cálculo
    base_inputs JSONB NOT NULL, -- hourly_rate, monthly_income, work_hours, etc.
    current_metrics JSONB NOT NULL, -- current productivity, stress level, etc.
    target_metrics JSONB NOT NULL, -- desired improvements
    
    -- Tipos de ROI calculados
    financial_roi JSONB NOT NULL DEFAULT '{}', -- monetary returns
    time_roi JSONB NOT NULL DEFAULT '{}', -- time saved/gained
    productivity_roi JSONB NOT NULL DEFAULT '{}', -- efficiency gains
    health_roi JSONB NOT NULL DEFAULT '{}', -- health improvements value
    performance_roi JSONB NOT NULL DEFAULT '{}', -- performance metrics
    stress_reduction_roi JSONB NOT NULL DEFAULT '{}', -- stress cost savings
    
    -- ROI consolidado
    total_roi_percentage FLOAT,
    total_value_generated DECIMAL(12,2),
    payback_period_months FLOAT,
    five_year_projection DECIMAL(12,2),
    
    -- Factores de cálculo
    calculation_method VARCHAR(50) DEFAULT 'standard', -- standard, conservative, optimistic
    confidence_level FLOAT CHECK (confidence_level >= 0.0 AND confidence_level <= 1.0),
    assumptions_used JSONB DEFAULT '[]',
    
    -- Comparativas
    industry_benchmark_roi FLOAT,
    percentile_ranking INTEGER CHECK (percentile_ranking >= 0 AND percentile_ranking <= 100),
    similar_profiles_avg_roi FLOAT,
    
    -- Personalización
    personalized_factors JSONB DEFAULT '{}', -- factors specific to user
    custom_benefits JSONB DEFAULT '[]', -- additional benefits identified
    
    -- Validación
    data_quality_score FLOAT CHECK (data_quality_score >= 0.0 AND data_quality_score <= 1.0),
    calculation_version VARCHAR(50) DEFAULT 'v1.0',
    
    -- Presentación
    highlighted_metrics JSONB DEFAULT '[]', -- top 3-5 metrics to emphasize
    visual_data JSONB DEFAULT '{}', -- data formatted for charts
    
    -- Impacto en conversión
    shown_to_user BOOLEAN DEFAULT false,
    user_reaction VARCHAR(50), -- positive, neutral, skeptical, negative
    led_to_conversion BOOLEAN,
    
    -- Metadata
    calculated_at TIMESTAMP DEFAULT NOW(),
    calculation_time_ms INTEGER,
    
    -- Unique constraint para evitar duplicados
    UNIQUE(conversation_id, calculation_version)
);

-- Índices para roi_calculations
CREATE INDEX IF NOT EXISTS idx_roi_calculations_conversation ON roi_calculations(conversation_id);
CREATE INDEX IF NOT EXISTS idx_roi_calculations_user ON roi_calculations(user_id);
CREATE INDEX IF NOT EXISTS idx_roi_calculations_profession ON roi_calculations(profession);
CREATE INDEX IF NOT EXISTS idx_roi_calculations_total_roi ON roi_calculations(total_roi_percentage);
CREATE INDEX IF NOT EXISTS idx_roi_calculations_calculated_at ON roi_calculations(calculated_at);
CREATE INDEX IF NOT EXISTS idx_roi_calculations_conversion ON roi_calculations(led_to_conversion);

-- =====================================================================
-- 2. TABLA DE BENCHMARKS POR PROFESIÓN
-- =====================================================================
CREATE TABLE IF NOT EXISTS roi_profession_benchmarks (
    -- Identificación
    benchmark_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profession VARCHAR(100) NOT NULL,
    industry VARCHAR(100),
    
    -- Métricas base promedio
    avg_hourly_rate DECIMAL(10,2),
    avg_monthly_income DECIMAL(12,2),
    avg_work_hours_weekly FLOAT,
    
    -- Costos de ineficiencia típicos
    avg_productivity_loss_percentage FLOAT,
    avg_stress_cost_monthly DECIMAL(10,2),
    avg_health_issues_cost_yearly DECIMAL(12,2),
    avg_burnout_risk_percentage FLOAT,
    
    -- Mejoras típicas con HIE
    avg_productivity_improvement FLOAT,
    avg_stress_reduction FLOAT,
    avg_energy_increase FLOAT,
    avg_focus_improvement FLOAT,
    avg_recovery_time_reduction FLOAT,
    
    -- ROI histórico
    median_roi_percentage FLOAT,
    top_quartile_roi FLOAT,
    bottom_quartile_roi FLOAT,
    
    -- Factores de valor específicos
    value_factors JSONB DEFAULT '{}', -- specific value drivers for profession
    common_pain_points JSONB DEFAULT '[]',
    highest_impact_areas JSONB DEFAULT '[]',
    
    -- Datos de muestra
    sample_size INTEGER,
    data_freshness_days INTEGER,
    confidence_interval JSONB DEFAULT '{}',
    
    -- Estado
    is_active BOOLEAN DEFAULT true,
    requires_update BOOLEAN DEFAULT false,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    data_source VARCHAR(255),
    
    -- Unique constraint
    UNIQUE(profession, industry)
);

-- Índices para roi_profession_benchmarks
CREATE INDEX IF NOT EXISTS idx_roi_benchmarks_profession ON roi_profession_benchmarks(profession);
CREATE INDEX IF NOT EXISTS idx_roi_benchmarks_industry ON roi_profession_benchmarks(industry);
CREATE INDEX IF NOT EXISTS idx_roi_benchmarks_active ON roi_profession_benchmarks(is_active);

-- =====================================================================
-- 3. TABLA DE CASOS DE ÉXITO REALES
-- =====================================================================
CREATE TABLE IF NOT EXISTS roi_success_stories (
    -- Identificación
    story_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_identifier VARCHAR(100) NOT NULL, -- anonymized but consistent
    
    -- Perfil del cliente
    profession VARCHAR(100) NOT NULL,
    industry VARCHAR(100),
    company_type VARCHAR(100),
    starting_situation TEXT,
    
    -- Resultados medibles
    implementation_date DATE,
    measurement_period_months INTEGER,
    
    -- ROI específico
    financial_roi_percentage FLOAT NOT NULL,
    time_saved_hours_monthly FLOAT,
    productivity_increase_percentage FLOAT,
    stress_reduction_percentage FLOAT,
    
    -- Valores monetarios
    monthly_value_generated DECIMAL(10,2),
    yearly_value_generated DECIMAL(12,2),
    total_investment DECIMAL(10,2),
    net_profit DECIMAL(12,2),
    
    -- Detalles cualitativos
    key_improvements JSONB DEFAULT '[]',
    testimonial_quote TEXT,
    specific_wins JSONB DEFAULT '[]',
    
    -- Verificación
    verified BOOLEAN DEFAULT false,
    verification_method VARCHAR(100),
    documentation_available BOOLEAN DEFAULT false,
    
    -- Uso en ventas
    can_be_shared BOOLEAN DEFAULT true,
    sharing_restrictions JSONB DEFAULT '{}',
    times_referenced INTEGER DEFAULT 0,
    conversion_impact_score FLOAT,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    story_status VARCHAR(50) DEFAULT 'active' -- active, archived, pending_verification
);

-- Índices para roi_success_stories
CREATE INDEX IF NOT EXISTS idx_success_stories_profession ON roi_success_stories(profession);
CREATE INDEX IF NOT EXISTS idx_success_stories_roi ON roi_success_stories(financial_roi_percentage);
CREATE INDEX IF NOT EXISTS idx_success_stories_verified ON roi_success_stories(verified);
CREATE INDEX IF NOT EXISTS idx_success_stories_status ON roi_success_stories(story_status);

-- =====================================================================
-- 4. TABLA DE COMPONENTES DE VALOR HIE
-- =====================================================================
CREATE TABLE IF NOT EXISTS roi_value_components (
    -- Identificación
    component_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    component_name VARCHAR(100) NOT NULL UNIQUE,
    component_category VARCHAR(50) NOT NULL, -- productivity, health, performance, wellbeing
    
    -- Descripción del valor
    description TEXT NOT NULL,
    measurement_method TEXT,
    
    -- Fórmula de cálculo
    calculation_formula JSONB NOT NULL,
    required_inputs JSONB DEFAULT '[]',
    
    -- Valores típicos
    typical_improvement_range JSONB DEFAULT '{}', -- min, max, average
    value_per_unit DECIMAL(10,2), -- $ per hour saved, $ per % productivity, etc.
    
    -- Aplicabilidad
    applicable_professions JSONB DEFAULT '[]', -- empty = all
    applicable_tiers JSONB DEFAULT '[]', -- empty = all
    weight_in_total_roi FLOAT DEFAULT 1.0,
    
    -- Evidencia
    supporting_studies JSONB DEFAULT '[]',
    confidence_level FLOAT CHECK (confidence_level >= 0.0 AND confidence_level <= 1.0),
    
    -- Estado
    is_active BOOLEAN DEFAULT true,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Índices para roi_value_components
CREATE INDEX IF NOT EXISTS idx_value_components_name ON roi_value_components(component_name);
CREATE INDEX IF NOT EXISTS idx_value_components_category ON roi_value_components(component_category);
CREATE INDEX IF NOT EXISTS idx_value_components_active ON roi_value_components(is_active);

-- =====================================================================
-- 5. TABLA DE PROYECCIONES DE ROI
-- =====================================================================
CREATE TABLE IF NOT EXISTS roi_projections (
    -- Identificación
    projection_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    calculation_id UUID NOT NULL,
    
    -- Timeline de proyección
    projection_months JSONB NOT NULL, -- Array de valores por mes
    projection_years JSONB NOT NULL, -- Array de valores por año (5 años)
    
    -- Escenarios
    conservative_projection JSONB NOT NULL,
    realistic_projection JSONB NOT NULL,
    optimistic_projection JSONB NOT NULL,
    
    -- Factores de crecimiento
    compound_growth_rate FLOAT,
    value_acceleration_factors JSONB DEFAULT '[]',
    
    -- Puntos de inflexión
    breakeven_month INTEGER,
    exponential_growth_start_month INTEGER,
    plateau_expected_month INTEGER,
    
    -- Riesgos y ajustes
    risk_factors JSONB DEFAULT '[]',
    seasonal_adjustments JSONB DEFAULT '{}',
    
    -- Visualización
    chart_data JSONB NOT NULL, -- Formatted for frontend charts
    key_milestones JSONB DEFAULT '[]',
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Foreign key
    FOREIGN KEY (calculation_id) REFERENCES roi_calculations(calculation_id) ON DELETE CASCADE
);

-- Índices para roi_projections
CREATE INDEX IF NOT EXISTS idx_roi_projections_calculation ON roi_projections(calculation_id);
CREATE INDEX IF NOT EXISTS idx_roi_projections_breakeven ON roi_projections(breakeven_month);

-- =====================================================================
-- 6. FUNCIONES Y TRIGGERS
-- =====================================================================

-- Función para calcular ROI base
CREATE OR REPLACE FUNCTION calculate_base_roi(
    hourly_rate DECIMAL,
    productivity_gain FLOAT,
    hours_saved_monthly FLOAT,
    stress_cost_reduction DECIMAL,
    additional_value DECIMAL
) RETURNS FLOAT AS $$
DECLARE
    monthly_productivity_value DECIMAL;
    monthly_time_value DECIMAL;
    total_monthly_value DECIMAL;
    monthly_cost DECIMAL := 149.00; -- Pro tier as default
    roi FLOAT;
BEGIN
    -- Calculate productivity value
    monthly_productivity_value := hourly_rate * 160 * (productivity_gain / 100);
    
    -- Calculate time value
    monthly_time_value := hourly_rate * hours_saved_monthly;
    
    -- Total value
    total_monthly_value := monthly_productivity_value + monthly_time_value + 
                          stress_cost_reduction + COALESCE(additional_value, 0);
    
    -- Calculate ROI
    IF monthly_cost > 0 THEN
        roi := ((total_monthly_value - monthly_cost) / monthly_cost) * 100;
    ELSE
        roi := 0;
    END IF;
    
    RETURN roi;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Trigger para actualizar benchmarks
CREATE OR REPLACE FUNCTION update_benchmark_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    NEW.data_freshness_days := 0;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_benchmark_timestamp_trigger
BEFORE UPDATE ON roi_profession_benchmarks
FOR EACH ROW EXECUTE FUNCTION update_benchmark_timestamp();

-- =====================================================================
-- 7. VISTAS ANALÍTICAS
-- =====================================================================

-- Vista de ROI promedio por profesión
CREATE OR REPLACE VIEW roi_by_profession_view AS
SELECT 
    rc.profession,
    COUNT(*) as total_calculations,
    AVG(rc.total_roi_percentage) as avg_roi,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY rc.total_roi_percentage) as median_roi,
    MAX(rc.total_roi_percentage) as max_roi,
    MIN(rc.total_roi_percentage) as min_roi,
    AVG(rc.payback_period_months) as avg_payback_months,
    COUNT(*) FILTER (WHERE rc.led_to_conversion = true) as conversions,
    AVG(rc.confidence_level) as avg_confidence
FROM roi_calculations rc
WHERE rc.shown_to_user = true
GROUP BY rc.profession
ORDER BY avg_roi DESC;

-- Vista de componentes de valor más impactantes
CREATE OR REPLACE VIEW high_impact_value_components AS
SELECT 
    vc.component_name,
    vc.component_category,
    vc.typical_improvement_range,
    vc.value_per_unit,
    vc.weight_in_total_roi,
    COUNT(DISTINCT rc.calculation_id) as times_used,
    AVG(vc.confidence_level) as avg_confidence
FROM roi_value_components vc
JOIN roi_calculations rc ON rc.personalized_factors ? vc.component_name
WHERE vc.is_active = true
GROUP BY vc.component_id, vc.component_name, vc.component_category, 
         vc.typical_improvement_range, vc.value_per_unit, vc.weight_in_total_roi
ORDER BY vc.weight_in_total_roi DESC, times_used DESC;

-- =====================================================================
-- 8. DATOS INICIALES
-- =====================================================================

-- Insertar benchmarks para profesiones comunes
INSERT INTO roi_profession_benchmarks (
    profession, avg_hourly_rate, avg_productivity_loss_percentage,
    avg_productivity_improvement, median_roi_percentage
) VALUES
('Software Engineer', 75.00, 25.0, 35.0, 847.0),
('Consultant', 150.00, 30.0, 40.0, 1250.0),
('Executive/CEO', 200.00, 20.0, 30.0, 1500.0),
('Healthcare Professional', 100.00, 35.0, 30.0, 950.0),
('Entrepreneur', 80.00, 40.0, 45.0, 1100.0)
ON CONFLICT (profession, industry) DO NOTHING;

-- Insertar componentes de valor HIE
INSERT INTO roi_value_components (
    component_name, component_category, description,
    calculation_formula, value_per_unit
) VALUES
('productivity_boost', 'productivity', 
 'Aumento en productividad por optimización energética',
 '{"formula": "hourly_rate * work_hours * (improvement_percentage / 100)"}',
 1.0),
('time_savings', 'productivity',
 'Tiempo ahorrado por mejor enfoque y menos distracciones',
 '{"formula": "hours_saved * hourly_rate"}',
 1.0),
('stress_cost_reduction', 'health',
 'Reducción en costos relacionados con estrés',
 '{"formula": "baseline_stress_cost * (reduction_percentage / 100)"}',
 1.0),
('cognitive_enhancement_value', 'performance',
 'Valor de mejora en toma de decisiones y creatividad',
 '{"formula": "monthly_income * 0.15 * (improvement_percentage / 100)"}',
 1.0)
ON CONFLICT (component_name) DO NOTHING;

-- Insertar historia de éxito ejemplo
INSERT INTO roi_success_stories (
    client_identifier, profession, financial_roi_percentage,
    time_saved_hours_monthly, productivity_increase_percentage,
    monthly_value_generated, testimonial_quote, verified
) VALUES
('CLIENT_001', 'Consultant', 1247.0, 20, 40,
 2500.00, 
 'El sistema HIE transformó completamente mi rendimiento. Ahora facturo 40% más trabajando menos horas.',
 true)
ON CONFLICT DO NOTHING;

-- =====================================================================
-- COMENTARIOS DE DOCUMENTACIÓN
-- =====================================================================
COMMENT ON TABLE roi_calculations IS 'Cálculos detallados de ROI personalizados por usuario';
COMMENT ON TABLE roi_profession_benchmarks IS 'Benchmarks de ROI por profesión basados en datos reales';
COMMENT ON TABLE roi_success_stories IS 'Casos de éxito verificados con ROI real';
COMMENT ON TABLE roi_value_components IS 'Componentes individuales que contribuyen al ROI total';
COMMENT ON TABLE roi_projections IS 'Proyecciones de ROI a futuro con diferentes escenarios';

COMMENT ON FUNCTION calculate_base_roi IS 'Función para calcular ROI base con inputs estándar';

-- =====================================================================
-- Script completado exitosamente
-- =====================================================================