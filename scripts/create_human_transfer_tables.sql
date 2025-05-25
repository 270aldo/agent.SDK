-- Esquema para el sistema de transferencia a agentes humanos

-- Tabla para almacenar solicitudes de transferencia a agentes humanos
CREATE TABLE IF NOT EXISTS public.human_transfer_requests (
    id UUID PRIMARY KEY,
    conversation_id UUID NOT NULL,
    user_id UUID NOT NULL,
    agent_id UUID,
    reason TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('requested', 'pending', 'accepted', 'rejected', 'completed', 'timed_out')),
    requested_at TIMESTAMP WITH TIME ZONE NOT NULL,
    accepted_at TIMESTAMP WITH TIME ZONE,
    rejected_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Crear índices para búsquedas comunes
CREATE INDEX IF NOT EXISTS idx_human_transfer_requests_conversation_id ON public.human_transfer_requests(conversation_id);
CREATE INDEX IF NOT EXISTS idx_human_transfer_requests_user_id ON public.human_transfer_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_human_transfer_requests_agent_id ON public.human_transfer_requests(agent_id);
CREATE INDEX IF NOT EXISTS idx_human_transfer_requests_status ON public.human_transfer_requests(status);

-- Política RLS para permitir acceso completo al servicio
CREATE POLICY "Service full access for human_transfer_requests"
ON public.human_transfer_requests
FOR ALL
USING (true)
WITH CHECK (true);

-- Habilitar RLS en la tabla
ALTER TABLE public.human_transfer_requests ENABLE ROW LEVEL SECURITY;

-- Tabla para gestionar la disponibilidad de agentes humanos
CREATE TABLE IF NOT EXISTS public.human_agents (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL CHECK (status IN ('available', 'busy', 'offline')),
    specialization TEXT,
    max_concurrent_chats INTEGER NOT NULL DEFAULT 3,
    current_chats INTEGER NOT NULL DEFAULT 0,
    last_activity TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Crear índices para búsquedas comunes
CREATE INDEX IF NOT EXISTS idx_human_agents_status ON public.human_agents(status);
CREATE INDEX IF NOT EXISTS idx_human_agents_specialization ON public.human_agents(specialization);

-- Política RLS para permitir acceso completo al servicio
CREATE POLICY "Service full access for human_agents"
ON public.human_agents
FOR ALL
USING (true)
WITH CHECK (true);

-- Habilitar RLS en la tabla
ALTER TABLE public.human_agents ENABLE ROW LEVEL SECURITY;
