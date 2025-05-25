-- Esquema para el sistema de seguimiento post-conversación

-- Tabla para almacenar solicitudes de seguimiento
CREATE TABLE IF NOT EXISTS public.follow_up_requests (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    conversation_id UUID NOT NULL,
    follow_up_type TEXT NOT NULL CHECK (follow_up_type IN ('high_intent', 'objection_handling', 'information_request', 'demo_request', 'pricing_request', 'transfer_follow_up')),
    status TEXT NOT NULL CHECK (status IN ('scheduled', 'sent', 'responded', 'completed', 'cancelled')),
    scheduled_date TIMESTAMP WITH TIME ZONE NOT NULL,
    sent_date TIMESTAMP WITH TIME ZONE,
    response_date TIMESTAMP WITH TIME ZONE,
    template_id TEXT,
    custom_message TEXT,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Crear índices para búsquedas comunes
CREATE INDEX IF NOT EXISTS idx_follow_up_requests_user_id ON public.follow_up_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_follow_up_requests_conversation_id ON public.follow_up_requests(conversation_id);
CREATE INDEX IF NOT EXISTS idx_follow_up_requests_status ON public.follow_up_requests(status);
CREATE INDEX IF NOT EXISTS idx_follow_up_requests_scheduled_date ON public.follow_up_requests(scheduled_date);

-- Política RLS para permitir acceso completo al servicio
CREATE POLICY "Service full access for follow_up_requests"
ON public.follow_up_requests
FOR ALL
USING (true)
WITH CHECK (true);

-- Habilitar RLS en la tabla
ALTER TABLE public.follow_up_requests ENABLE ROW LEVEL SECURITY;

-- Tabla para almacenar plantillas de email para seguimiento
CREATE TABLE IF NOT EXISTS public.email_templates (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    template_type TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Política RLS para permitir acceso completo al servicio
CREATE POLICY "Service full access for email_templates"
ON public.email_templates
FOR ALL
USING (true)
WITH CHECK (true);

-- Habilitar RLS en la tabla
ALTER TABLE public.email_templates ENABLE ROW LEVEL SECURITY;
