-- =====================================================================
-- MIGRACIÓN 005: SISTEMA DE OPTIMIZACIÓN DE PROMPTS
-- =====================================================================
-- Este script crea las tablas para el sistema genético de optimización
-- de prompts con enfoque HIE (Human Intelligence Enhancement)

-- =====================================================================
-- 1. TABLA DE VARIANTES DE PROMPTS
-- =====================================================================
CREATE TABLE IF NOT EXISTS prompt_variants (
    -- Identificación
    variant_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    variant_name VARCHAR(255) NOT NULL,
    prompt_type VARCHAR(100) NOT NULL, -- greeting, objection_handling, closing, hie_explanation, etc.
    
    -- Contenido del prompt
    prompt_template TEXT NOT NULL,
    template_variables JSONB DEFAULT '[]', -- Variables que se pueden insertar
    
    -- Configuración genética
    genetic_code JSONB NOT NULL DEFAULT '{}', -- Genes del prompt para algoritmo genético
    parent_variants JSONB DEFAULT '[]', -- IDs de prompts padres si fue generado
    generation INTEGER DEFAULT 1,
    mutation_rate FLOAT DEFAULT 0.1 CHECK (mutation_rate >= 0.0 AND mutation_rate <= 1.0),
    
    -- Performance metrics
    usage_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    success_rate FLOAT GENERATED ALWAYS AS (
        CASE WHEN usage_count > 0 THEN success_count::FLOAT / usage_count::FLOAT ELSE 0 END
    ) STORED,
    avg_engagement_score FLOAT CHECK (avg_engagement_score >= 0.0 AND avg_engagement_score <= 10.0),
    avg_conversion_impact FLOAT CHECK (avg_conversion_impact >= -1.0 AND avg_conversion_impact <= 1.0),
    
    -- A/B Testing
    is_control BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    test_group VARCHAR(50), -- A, B, C, etc.
    confidence_score FLOAT CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    
    -- Contexto de aplicación
    target_archetype VARCHAR(100), -- all, analytical, emotional, etc.
    target_tier VARCHAR(50), -- all, essential, pro, elite, prime, longevity
    target_industry VARCHAR(100), -- all, fitness, health, wellness
    context_conditions JSONB DEFAULT '{}', -- Condiciones específicas de uso
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(255) DEFAULT 'prompt_optimizer',
    approved_by VARCHAR(255),
    approval_date TIMESTAMP
);

-- Índices para prompt_variants
CREATE INDEX IF NOT EXISTS idx_prompt_variants_type ON prompt_variants(prompt_type);
CREATE INDEX IF NOT EXISTS idx_prompt_variants_active ON prompt_variants(is_active);
CREATE INDEX IF NOT EXISTS idx_prompt_variants_success_rate ON prompt_variants(success_rate);
CREATE INDEX IF NOT EXISTS idx_prompt_variants_archetype ON prompt_variants(target_archetype);
CREATE INDEX IF NOT EXISTS idx_prompt_variants_tier ON prompt_variants(target_tier);
CREATE INDEX IF NOT EXISTS idx_prompt_variants_generation ON prompt_variants(generation);

-- =====================================================================
-- 2. TABLA DE OPTIMIZACIONES HIE DE PROMPTS
-- =====================================================================
CREATE TABLE IF NOT EXISTS hie_prompt_optimizations (
    -- Identificación
    optimization_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    variant_id UUID NOT NULL,
    
    -- Optimización HIE específica
    hie_focus VARCHAR(100) NOT NULL, -- energy, focus, stress_reduction, cognitive_enhancement
    hie_keywords JSONB NOT NULL DEFAULT '[]',
    scientific_backing JSONB DEFAULT '{}', -- Referencias a estudios
    
    -- Elementos HIE del prompt
    benefit_emphasis JSONB NOT NULL, -- Cómo se enfatizan los beneficios HIE
    social_proof_elements JSONB DEFAULT '[]', -- Testimonios, casos de éxito
    urgency_elements JSONB DEFAULT '[]', -- Elementos de urgencia/escasez
    
    -- Performance HIE específico
    hie_conversion_rate FLOAT CHECK (hie_conversion_rate >= 0.0 AND hie_conversion_rate <= 1.0),
    hie_engagement_score FLOAT CHECK (hie_engagement_score >= 0.0 AND hie_engagement_score <= 10.0),
    belief_shift_score FLOAT CHECK (belief_shift_score >= 0.0 AND belief_shift_score <= 10.0),
    
    -- Análisis de efectividad
    most_effective_elements JSONB DEFAULT '[]',
    least_effective_elements JSONB DEFAULT '[]',
    improvement_suggestions JSONB DEFAULT '[]',
    
    -- Control de calidad
    medical_claims_verified BOOLEAN DEFAULT false,
    compliance_checked BOOLEAN DEFAULT false,
    ethical_review_passed BOOLEAN DEFAULT false,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    last_tested TIMESTAMP,
    optimization_version INTEGER DEFAULT 1,
    
    -- Foreign key
    FOREIGN KEY (variant_id) REFERENCES prompt_variants(variant_id) ON DELETE CASCADE
);

-- Índices para hie_prompt_optimizations
CREATE INDEX IF NOT EXISTS idx_hie_optimizations_variant ON hie_prompt_optimizations(variant_id);
CREATE INDEX IF NOT EXISTS idx_hie_optimizations_focus ON hie_prompt_optimizations(hie_focus);
CREATE INDEX IF NOT EXISTS idx_hie_optimizations_conversion ON hie_prompt_optimizations(hie_conversion_rate);

-- =====================================================================
-- 3. TABLA DE PERFORMANCE DE GENES
-- =====================================================================
CREATE TABLE IF NOT EXISTS hie_gene_performance (
    -- Identificación
    gene_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    gene_name VARCHAR(100) NOT NULL UNIQUE,
    gene_type VARCHAR(50) NOT NULL, -- tone, structure, persuasion, hie_element
    
    -- Definición del gen
    gene_value JSONB NOT NULL,
    gene_description TEXT,
    
    -- Performance metrics
    total_usage INTEGER DEFAULT 0,
    successful_usage INTEGER DEFAULT 0,
    avg_impact_score FLOAT CHECK (avg_impact_score >= -1.0 AND avg_impact_score <= 1.0),
    
    -- Análisis por contexto
    performance_by_archetype JSONB DEFAULT '{}',
    performance_by_tier JSONB DEFAULT '{}',
    performance_by_objection JSONB DEFAULT '{}',
    
    -- Combinaciones exitosas
    successful_combinations JSONB DEFAULT '[]', -- Otros genes con los que funciona bien
    unsuccessful_combinations JSONB DEFAULT '[]', -- Genes con los que no funciona
    
    -- Estado
    is_active BOOLEAN DEFAULT true,
    requires_review BOOLEAN DEFAULT false,
    
    -- Metadata
    discovered_at TIMESTAMP DEFAULT NOW(),
    last_updated TIMESTAMP DEFAULT NOW()
);

-- Índices para hie_gene_performance
CREATE INDEX IF NOT EXISTS idx_gene_performance_name ON hie_gene_performance(gene_name);
CREATE INDEX IF NOT EXISTS idx_gene_performance_type ON hie_gene_performance(gene_type);
CREATE INDEX IF NOT EXISTS idx_gene_performance_active ON hie_gene_performance(is_active);
CREATE INDEX IF NOT EXISTS idx_gene_performance_impact ON hie_gene_performance(avg_impact_score);

-- =====================================================================
-- 4. TABLA DE EXPERIMENTOS DE PROMPTS
-- =====================================================================
CREATE TABLE IF NOT EXISTS prompt_experiments (
    -- Identificación
    experiment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    experiment_name VARCHAR(255) NOT NULL,
    
    -- Configuración del experimento
    variant_ids JSONB NOT NULL, -- Array de variant_ids participando
    control_variant_id UUID,
    hypothesis TEXT NOT NULL,
    success_criteria JSONB NOT NULL,
    
    -- Estado del experimento
    status VARCHAR(50) DEFAULT 'planning', -- planning, running, analyzing, completed
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    
    -- Resultados
    total_conversations INTEGER DEFAULT 0,
    results_by_variant JSONB DEFAULT '{}',
    winning_variant_id UUID,
    statistical_significance FLOAT CHECK (statistical_significance >= 0.0 AND statistical_significance <= 1.0),
    
    -- Configuración estadística
    minimum_sample_size INTEGER DEFAULT 100,
    confidence_level FLOAT DEFAULT 0.95,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(255) DEFAULT 'system',
    notes TEXT
);

-- Índices para prompt_experiments
CREATE INDEX IF NOT EXISTS idx_prompt_experiments_status ON prompt_experiments(status);
CREATE INDEX IF NOT EXISTS idx_prompt_experiments_dates ON prompt_experiments(start_date, end_date);

-- =====================================================================
-- 5. TABLA DE USO DE PROMPTS
-- =====================================================================
CREATE TABLE IF NOT EXISTS prompt_usage_log (
    -- Identificación
    usage_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    variant_id UUID NOT NULL,
    conversation_id UUID NOT NULL,
    
    -- Contexto de uso
    used_at TIMESTAMP DEFAULT NOW(),
    prompt_position VARCHAR(50), -- greeting, middle, closing
    conversation_stage VARCHAR(100), -- discovery, objection_handling, closing
    
    -- Variables utilizadas
    template_values JSONB DEFAULT '{}',
    rendered_prompt TEXT,
    
    -- Resultado inmediato
    user_response TEXT,
    response_sentiment FLOAT CHECK (response_sentiment >= -1.0 AND response_sentiment <= 1.0),
    response_length INTEGER,
    response_time_seconds INTEGER,
    
    -- Impacto
    engagement_delta FLOAT, -- Cambio en engagement después del prompt
    conversion_impact FLOAT CHECK (conversion_impact >= -1.0 AND conversion_impact <= 1.0),
    led_to_conversion BOOLEAN,
    
    -- Foreign key
    FOREIGN KEY (variant_id) REFERENCES prompt_variants(variant_id) ON DELETE CASCADE
);

-- Índices para prompt_usage_log
CREATE INDEX IF NOT EXISTS idx_prompt_usage_variant ON prompt_usage_log(variant_id);
CREATE INDEX IF NOT EXISTS idx_prompt_usage_conversation ON prompt_usage_log(conversation_id);
CREATE INDEX IF NOT EXISTS idx_prompt_usage_timestamp ON prompt_usage_log(used_at);
CREATE INDEX IF NOT EXISTS idx_prompt_usage_conversion ON prompt_usage_log(led_to_conversion);

-- =====================================================================
-- 6. TRIGGERS Y FUNCIONES
-- =====================================================================

-- Trigger para actualizar updated_at en prompt_variants
CREATE OR REPLACE FUNCTION update_prompt_variant_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_prompt_variant_timestamp_trigger
BEFORE UPDATE ON prompt_variants
FOR EACH ROW EXECUTE FUNCTION update_prompt_variant_timestamp();

-- Función para calcular fitness score de un prompt
CREATE OR REPLACE FUNCTION calculate_prompt_fitness(
    variant_id UUID
) RETURNS FLOAT AS $$
DECLARE
    fitness FLOAT := 0;
    variant RECORD;
BEGIN
    SELECT * INTO variant FROM prompt_variants WHERE prompt_variants.variant_id = $1;
    
    IF FOUND THEN
        -- Fórmula de fitness: combina success rate, engagement y conversion impact
        fitness := (
            COALESCE(variant.success_rate, 0) * 0.4 +
            COALESCE(variant.avg_engagement_score / 10.0, 0) * 0.3 +
            COALESCE((variant.avg_conversion_impact + 1) / 2, 0.5) * 0.3
        );
    END IF;
    
    RETURN fitness;
END;
$$ LANGUAGE plpgsql;

-- =====================================================================
-- 7. VISTAS ANALÍTICAS
-- =====================================================================

-- Vista de mejores prompts por tipo
CREATE OR REPLACE VIEW top_performing_prompts AS
SELECT 
    pv.variant_id,
    pv.variant_name,
    pv.prompt_type,
    pv.generation,
    pv.usage_count,
    pv.success_rate,
    pv.avg_engagement_score,
    pv.avg_conversion_impact,
    calculate_prompt_fitness(pv.variant_id) as fitness_score
FROM prompt_variants pv
WHERE pv.is_active = true AND pv.usage_count >= 10
ORDER BY calculate_prompt_fitness(pv.variant_id) DESC;

-- Vista de evolución genética
CREATE OR REPLACE VIEW genetic_evolution_view AS
SELECT 
    generation,
    COUNT(*) as variant_count,
    AVG(success_rate) as avg_success_rate,
    AVG(avg_engagement_score) as avg_engagement,
    MAX(success_rate) as best_success_rate,
    AVG(usage_count) as avg_usage
FROM prompt_variants
WHERE is_active = true
GROUP BY generation
ORDER BY generation;

-- =====================================================================
-- 8. DATOS INICIALES - GENES HIE
-- =====================================================================

-- Insertar genes iniciales para optimización HIE
INSERT INTO hie_gene_performance (gene_name, gene_type, gene_value, gene_description) VALUES
('scientific_credibility', 'hie_element', 
 '{"template": "Basado en {study_count} estudios científicos con {participant_count} participantes"}',
 'Enfatiza credibilidad científica con números específicos'),
 
('roi_emphasis', 'persuasion',
 '{"template": "ROI promedio de {roi_percentage}% en {time_period}"}',
 'Enfatiza retorno de inversión específico'),
 
('urgency_scarcity', 'persuasion',
 '{"template": "Solo {spots_left} lugares disponibles este mes"}',
 'Crea urgencia con escasez real'),
 
('social_proof_specific', 'hie_element',
 '{"template": "{client_name}, {client_profession} en {client_company}: \"{testimonial}\""}',
 'Testimonios específicos con datos verificables'),
 
('empathetic_understanding', 'tone',
 '{"markers": ["entiendo", "comprendo", "tiene sentido", "es natural"]}',
 'Tono empático que genera confianza'),
 
('consultative_approach', 'structure',
 '{"flow": ["pregunta", "escucha", "valida", "sugiere"]}',
 'Estructura consultiva no agresiva')
ON CONFLICT (gene_name) DO NOTHING;

-- =====================================================================
-- 9. PLANTILLAS DE PROMPTS INICIALES
-- =====================================================================

-- Insertar variantes de prompts iniciales
INSERT INTO prompt_variants (variant_name, prompt_type, prompt_template, genetic_code, target_archetype) VALUES
('hie_greeting_analytical', 'greeting',
 'Hola {name}, veo que estás interesado en optimizar tu rendimiento. Basándome en más de 50 estudios científicos y 10,000+ horas de datos biométricos, el sistema HIE puede ayudarte a lograr resultados medibles. ¿Qué aspecto específico de tu rendimiento te gustaría mejorar?',
 '{"genes": ["scientific_credibility", "consultative_approach"]}',
 'analytical'),
 
('hie_objection_price_roi', 'objection_handling',
 'Entiendo perfectamente tu preocupación sobre la inversión. De hecho, es una pregunta inteligente. Nuestros clientes, profesionales como tú, reportan un ROI promedio del 847% en los primeros 6 meses. ¿Te gustaría ver cómo calculamos este retorno específicamente para tu caso?',
 '{"genes": ["empathetic_understanding", "roi_emphasis", "consultative_approach"]}',
 'all'),
 
('hie_closing_early_adopter', 'closing',
 'Me encanta tu visión {name}. Eres exactamente el tipo de profesional innovador que estamos buscando. Tenemos solo {spots_left} lugares en nuestro programa Early Adopter este mes, con beneficios exclusivos. ¿Te gustaría asegurar tu lugar ahora?',
 '{"genes": ["urgency_scarcity", "social_proof_specific"]}',
 'all')
ON CONFLICT DO NOTHING;

-- =====================================================================
-- COMENTARIOS DE DOCUMENTACIÓN
-- =====================================================================
COMMENT ON TABLE prompt_variants IS 'Variantes de prompts para optimización genética';
COMMENT ON TABLE hie_prompt_optimizations IS 'Optimizaciones específicas HIE para prompts';
COMMENT ON TABLE hie_gene_performance IS 'Performance de genes individuales en algoritmo genético';
COMMENT ON TABLE prompt_experiments IS 'Experimentos A/B para optimización de prompts';
COMMENT ON TABLE prompt_usage_log IS 'Log detallado de uso de cada prompt';

-- =====================================================================
-- Script completado exitosamente
-- =====================================================================