-- =====================================================================
-- SCRIPT MAESTRO DE MIGRACIONES - NGX VOICE SALES AGENT
-- =====================================================================
-- Este script ejecuta todas las migraciones en el orden correcto
-- para configurar la base de datos completa del sistema

-- IMPORTANTE: Este script debe ejecutarse en una base de datos Supabase
-- que ya tenga la tabla 'conversations' creada

-- =====================================================================
-- VERIFICACIÓN INICIAL
-- =====================================================================
DO $$
BEGIN
    -- Verificar que existe la tabla conversations
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables 
                   WHERE table_schema = 'public' 
                   AND table_name = 'conversations') THEN
        RAISE EXCEPTION 'La tabla conversations no existe. Por favor, créela primero.';
    END IF;
    
    -- Mensaje de inicio
    RAISE NOTICE 'Iniciando migración completa de NGX Voice Sales Agent...';
END $$;

-- =====================================================================
-- EJECUTAR MIGRACIONES EN ORDEN
-- =====================================================================

-- 1. Actualizar tabla conversations existente
\echo 'Ejecutando 001_core_conversations.sql...'
\i 001_core_conversations.sql

-- 2. Crear tablas de modelos predictivos
\echo 'Ejecutando 003_predictive_models.sql...'
\i 003_predictive_models.sql

-- 3. Crear tablas de inteligencia emocional
\echo 'Ejecutando 004_emotional_intelligence.sql...'
\i 004_emotional_intelligence.sql

-- 4. Crear tablas de optimización de prompts
\echo 'Ejecutando 005_prompt_optimization.sql...'
\i 005_prompt_optimization.sql

-- 5. Crear tablas de gestión de trials
\echo 'Ejecutando 006_trial_management.sql...'
\i 006_trial_management.sql

-- 6. Crear tablas de tracking de ROI
\echo 'Ejecutando 007_roi_tracking.sql...'
\i 007_roi_tracking.sql

-- =====================================================================
-- VERIFICACIÓN FINAL
-- =====================================================================
DO $$
DECLARE
    table_count INTEGER;
    view_count INTEGER;
    function_count INTEGER;
BEGIN
    -- Contar objetos creados
    SELECT COUNT(*) INTO table_count 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_type = 'BASE TABLE';
    
    SELECT COUNT(*) INTO view_count 
    FROM information_schema.views 
    WHERE table_schema = 'public';
    
    SELECT COUNT(*) INTO function_count
    FROM information_schema.routines
    WHERE routine_schema = 'public'
    AND routine_type = 'FUNCTION';
    
    RAISE NOTICE '======================================';
    RAISE NOTICE 'Migración completada exitosamente!';
    RAISE NOTICE 'Tablas creadas: %', table_count;
    RAISE NOTICE 'Vistas creadas: %', view_count;
    RAISE NOTICE 'Funciones creadas: %', function_count;
    RAISE NOTICE '======================================';
END $$;

-- =====================================================================
-- CONFIGURACIÓN DE SEGURIDAD BÁSICA
-- =====================================================================

-- Habilitar Row Level Security en tablas sensibles
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE trial_users ENABLE ROW LEVEL SECURITY;
ALTER TABLE roi_calculations ENABLE ROW LEVEL SECURITY;
ALTER TABLE emotional_analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE personality_analysis ENABLE ROW LEVEL SECURITY;

-- Crear políticas básicas (ajustar según necesidades)
-- Ejemplo: política para conversations
CREATE POLICY "Enable read access for all users" ON conversations
    FOR SELECT USING (true);

CREATE POLICY "Enable insert for authenticated users" ON conversations
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- =====================================================================
-- ÍNDICES ADICIONALES PARA PERFORMANCE
-- =====================================================================

-- Índices compuestos para queries comunes
CREATE INDEX IF NOT EXISTS idx_conversations_user_status 
    ON conversations(user_id, status);

CREATE INDEX IF NOT EXISTS idx_prediction_results_conversation_type 
    ON prediction_results(conversation_id, prediction_type);

CREATE INDEX IF NOT EXISTS idx_emotional_analysis_conversation_timestamp 
    ON emotional_analysis(conversation_id, analyzed_at);

-- =====================================================================
-- JOBS PROGRAMADOS (OPCIONAL)
-- =====================================================================

-- Ejemplo: Job para limpiar datos antiguos
-- CREATE EXTENSION IF NOT EXISTS pg_cron;

-- SELECT cron.schedule(
--     'cleanup-old-conversations',
--     '0 2 * * *', -- 2 AM todos los días
--     $$DELETE FROM conversations 
--       WHERE created_at < NOW() - INTERVAL '90 days' 
--       AND status = 'completed'$$
-- );

-- =====================================================================
-- NOTIFICACIONES
-- =====================================================================
\echo ''
\echo '============================================='
\echo 'MIGRACIÓN COMPLETADA CON ÉXITO'
\echo '============================================='
\echo ''
\echo 'Próximos pasos:'
\echo '1. Revisar las políticas RLS creadas'
\echo '2. Configurar backups automáticos en Supabase'
\echo '3. Ajustar índices según patrones de uso real'
\echo '4. Configurar monitoring de performance'
\echo ''