-- =====================================================================
-- MIGRACIÓN 001: ACTUALIZACIÓN DE TABLA CONVERSATIONS
-- =====================================================================
-- Este script actualiza la tabla conversations existente para asegurar
-- que tenga todas las columnas necesarias para el sistema completo

-- IMPORTANTE: Primero ejecuta este query para ver la estructura actual:
-- SELECT column_name, data_type, is_nullable, column_default 
-- FROM information_schema.columns 
-- WHERE table_name = 'conversations' 
-- ORDER BY ordinal_position;

-- Verificar y agregar columnas faltantes si no existen
DO $$ 
BEGIN
    -- Agregar columna platform_context si no existe
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'conversations' 
                   AND column_name = 'platform_context') THEN
        ALTER TABLE conversations 
        ADD COLUMN platform_context JSONB DEFAULT '{}';
    END IF;

    -- Agregar columna ml_tracking_enabled si no existe
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'conversations' 
                   AND column_name = 'ml_tracking_enabled') THEN
        ALTER TABLE conversations 
        ADD COLUMN ml_tracking_enabled BOOLEAN DEFAULT true;
    END IF;

    -- Agregar columna tier_detected si no existe
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'conversations' 
                   AND column_name = 'tier_detected') THEN
        ALTER TABLE conversations 
        ADD COLUMN tier_detected VARCHAR(50);
    END IF;

    -- Agregar columna tier_confidence si no existe
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'conversations' 
                   AND column_name = 'tier_confidence') THEN
        ALTER TABLE conversations 
        ADD COLUMN tier_confidence FLOAT CHECK (tier_confidence >= 0.0 AND tier_confidence <= 1.0);
    END IF;

    -- Agregar columna emotional_journey si no existe
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'conversations' 
                   AND column_name = 'emotional_journey') THEN
        ALTER TABLE conversations 
        ADD COLUMN emotional_journey JSONB DEFAULT '[]';
    END IF;

    -- Agregar columna experiment_assignments si no existe
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'conversations' 
                   AND column_name = 'experiment_assignments') THEN
        ALTER TABLE conversations 
        ADD COLUMN experiment_assignments JSONB DEFAULT '[]';
    END IF;

    -- Agregar columna agent_version si no existe
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'conversations' 
                   AND column_name = 'agent_version') THEN
        ALTER TABLE conversations 
        ADD COLUMN agent_version VARCHAR(50) DEFAULT 'ngx_v1.0';
    END IF;

    -- Agregar columna total_duration_seconds si no existe
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'conversations' 
                   AND column_name = 'total_duration_seconds') THEN
        ALTER TABLE conversations 
        ADD COLUMN total_duration_seconds INTEGER;
    END IF;

    -- Agregar columna message_count si no existe
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'conversations' 
                   AND column_name = 'message_count') THEN
        ALTER TABLE conversations 
        ADD COLUMN message_count INTEGER DEFAULT 0;
    END IF;

    -- Agregar columna last_message_at si no existe
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'conversations' 
                   AND column_name = 'last_message_at') THEN
        ALTER TABLE conversations 
        ADD COLUMN last_message_at TIMESTAMP;
    END IF;
END $$;

-- Crear índices si no existen (verificando primero que las columnas existan)
DO $$
BEGIN
    -- Índice para conversation_id si existe la columna
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name = 'conversations' AND column_name = 'conversation_id') THEN
        CREATE INDEX IF NOT EXISTS idx_conversations_conversation_id ON conversations(conversation_id);
    END IF;
    
    -- Índice para user_id si existe la columna
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name = 'conversations' AND column_name = 'user_id') THEN
        CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
    END IF;
    
    -- Índice para status si existe la columna
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name = 'conversations' AND column_name = 'status') THEN
        CREATE INDEX IF NOT EXISTS idx_conversations_status ON conversations(status);
    END IF;
    
    -- Índice para created_at si existe la columna
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name = 'conversations' AND column_name = 'created_at') THEN
        CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at);
    END IF;
    
    -- Índice para tier_detected si existe la columna
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name = 'conversations' AND column_name = 'tier_detected') THEN
        CREATE INDEX IF NOT EXISTS idx_conversations_tier_detected ON conversations(tier_detected);
    END IF;
    
    -- Índice para ml_tracking_enabled si existe la columna
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name = 'conversations' AND column_name = 'ml_tracking_enabled') THEN
        CREATE INDEX IF NOT EXISTS idx_conversations_ml_tracking ON conversations(ml_tracking_enabled) WHERE ml_tracking_enabled = true;
    END IF;
END $$;

-- Agregar comentarios para documentación (solo si las columnas existen)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'conversations' AND column_name = 'platform_context') THEN
        COMMENT ON COLUMN conversations.platform_context IS 'Contexto de la plataforma de origen (web, mobile, API)';
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'conversations' AND column_name = 'ml_tracking_enabled') THEN
        COMMENT ON COLUMN conversations.ml_tracking_enabled IS 'Si el tracking ML está habilitado para esta conversación';
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'conversations' AND column_name = 'tier_detected') THEN
        COMMENT ON COLUMN conversations.tier_detected IS 'Tier detectado automáticamente (Essential, Pro, Elite, PRIME, LONGEVITY)';
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'conversations' AND column_name = 'tier_confidence') THEN
        COMMENT ON COLUMN conversations.tier_confidence IS 'Confianza en la detección del tier (0-1)';
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'conversations' AND column_name = 'emotional_journey') THEN
        COMMENT ON COLUMN conversations.emotional_journey IS 'Array de estados emocionales durante la conversación';
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'conversations' AND column_name = 'experiment_assignments') THEN
        COMMENT ON COLUMN conversations.experiment_assignments IS 'IDs de experimentos A/B asignados a esta conversación';
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'conversations' AND column_name = 'agent_version') THEN
        COMMENT ON COLUMN conversations.agent_version IS 'Versión del agente utilizada';
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'conversations' AND column_name = 'total_duration_seconds') THEN
        COMMENT ON COLUMN conversations.total_duration_seconds IS 'Duración total de la conversación en segundos';
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'conversations' AND column_name = 'message_count') THEN
        COMMENT ON COLUMN conversations.message_count IS 'Número total de mensajes en la conversación';
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'conversations' AND column_name = 'last_message_at') THEN
        COMMENT ON COLUMN conversations.last_message_at IS 'Timestamp del último mensaje';
    END IF;
END $$;

-- Trigger para actualizar last_message_at automáticamente
CREATE OR REPLACE FUNCTION update_conversation_last_message()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_message_at = NOW();
    NEW.message_count = COALESCE(NEW.message_count, 0) + 1;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Solo crear el trigger si no existe
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_conversation_last_message_trigger') THEN
        CREATE TRIGGER update_conversation_last_message_trigger
        BEFORE UPDATE ON conversations
        FOR EACH ROW
        WHEN (OLD.messages IS DISTINCT FROM NEW.messages)
        EXECUTE FUNCTION update_conversation_last_message();
    END IF;
END $$;

-- =====================================================================
-- VERIFICACIÓN FINAL
-- =====================================================================
-- Query para verificar que todas las columnas están presentes
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'conversations'
ORDER BY ordinal_position;