-- Esquema para el sistema mejorado de análisis de intención de compra

-- Tabla para almacenar modelos de intención por industria
CREATE TABLE IF NOT EXISTS public.intent_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    industry TEXT NOT NULL,
    intent_keywords JSONB NOT NULL,
    rejection_keywords JSONB NOT NULL,
    keyword_weights JSONB NOT NULL,
    sentiment_weights JSONB NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Crear índice para búsquedas por industria
CREATE INDEX IF NOT EXISTS idx_intent_models_industry ON public.intent_models(industry);

-- Tabla para almacenar datos de análisis de intención por conversación
CREATE TABLE IF NOT EXISTS public.intent_analysis_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL,
    user_id UUID NOT NULL,
    purchase_intent_probability NUMERIC(4,3) NOT NULL,
    has_purchase_intent BOOLEAN NOT NULL,
    has_rejection BOOLEAN NOT NULL,
    intent_indicators JSONB,
    rejection_indicators JSONB,
    sentiment_score NUMERIC(4,3),
    engagement_score NUMERIC(4,3),
    industry TEXT NOT NULL,
    model_id UUID REFERENCES public.intent_models(id),
    conversion_result BOOLEAN,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Crear índices para búsquedas comunes
CREATE INDEX IF NOT EXISTS idx_intent_analysis_conversation_id ON public.intent_analysis_results(conversation_id);
CREATE INDEX IF NOT EXISTS idx_intent_analysis_user_id ON public.intent_analysis_results(user_id);
CREATE INDEX IF NOT EXISTS idx_intent_analysis_industry ON public.intent_analysis_results(industry);

-- Tabla para almacenar datos de entrenamiento para el aprendizaje continuo
CREATE TABLE IF NOT EXISTS public.intent_training_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL,
    user_message TEXT NOT NULL,
    intent_label TEXT NOT NULL CHECK (intent_label IN ('high_intent', 'medium_intent', 'low_intent', 'rejection')),
    industry TEXT NOT NULL,
    keywords_detected JSONB,
    sentiment_score NUMERIC(4,3),
    conversion_result BOOLEAN,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Crear índices para búsquedas comunes
CREATE INDEX IF NOT EXISTS idx_intent_training_conversation_id ON public.intent_training_data(conversation_id);
CREATE INDEX IF NOT EXISTS idx_intent_training_intent_label ON public.intent_training_data(intent_label);
CREATE INDEX IF NOT EXISTS idx_intent_training_industry ON public.intent_training_data(industry);

-- Política RLS para permitir acceso completo al servicio
CREATE POLICY "Service full access for intent_models"
ON public.intent_models
USING (true)
WITH CHECK (true);

CREATE POLICY "Service full access for intent_analysis_results"
ON public.intent_analysis_results
USING (true)
WITH CHECK (true);

CREATE POLICY "Service full access for intent_training_data"
ON public.intent_training_data
USING (true)
WITH CHECK (true);

-- Habilitar RLS en las tablas
ALTER TABLE public.intent_models ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.intent_analysis_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.intent_training_data ENABLE ROW LEVEL SECURITY;
