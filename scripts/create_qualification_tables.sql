-- Esquema para el sistema de cualificación de leads y gestión de sesiones del agente de voz

-- Tabla para almacenar resultados de cualificación de leads
CREATE TABLE IF NOT EXISTS public.lead_qualifications (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    score INTEGER NOT NULL,
    qualified BOOLEAN NOT NULL,
    score_breakdown JSONB NOT NULL DEFAULT '{}'::JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Crear índice para búsqueda por user_id
CREATE INDEX IF NOT EXISTS idx_lead_qualifications_user_id ON public.lead_qualifications(user_id);

-- Tabla para registrar sesiones del agente de voz
CREATE TABLE IF NOT EXISTS public.voice_agent_sessions (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    conversation_id UUID NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE,
    max_duration_seconds INTEGER NOT NULL,
    intent_detection_timeout INTEGER NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('active', 'completed', 'timeout', 'abandoned')),
    end_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Crear índices para búsquedas comunes
CREATE INDEX IF NOT EXISTS idx_voice_agent_sessions_user_id ON public.voice_agent_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_voice_agent_sessions_conversation_id ON public.voice_agent_sessions(conversation_id);
CREATE INDEX IF NOT EXISTS idx_voice_agent_sessions_status ON public.voice_agent_sessions(status);

-- Política RLS para permitir acceso completo al servicio
CREATE POLICY "Service full access for lead_qualifications"
ON public.lead_qualifications
FOR ALL
USING (true)
WITH CHECK (true);

-- Política RLS para permitir acceso completo al servicio
CREATE POLICY "Service full access for voice_agent_sessions"
ON public.voice_agent_sessions
FOR ALL
USING (true)
WITH CHECK (true);

-- Habilitar RLS en las tablas
ALTER TABLE public.lead_qualifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.voice_agent_sessions ENABLE ROW LEVEL SECURITY;
