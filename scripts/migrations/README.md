# Migraciones de Base de Datos - NGX Voice Sales Agent

## 📋 Descripción

Este directorio contiene todos los scripts de migración SQL necesarios para configurar la base de datos completa del sistema NGX Voice Sales Agent en Supabase.

## 🗂 Estructura de Archivos

```
migrations/
├── 001_core_conversations.sql      # Actualiza tabla conversations existente
├── 003_predictive_models.sql       # Sistema de modelos predictivos ML
├── 004_emotional_intelligence.sql  # Análisis emocional y personalidad
├── 005_prompt_optimization.sql     # Optimización genética de prompts
├── 006_trial_management.sql        # Gestión de trials y demos
├── 007_roi_tracking.sql            # Cálculo y tracking de ROI
├── run_all_migrations.sql          # Script maestro de ejecución
└── README.md                       # Este archivo
```

## 🚀 Cómo Ejecutar las Migraciones

### Opción 1: Ejecutar Todo de Una Vez (Recomendado)

1. Abre el **Supabase SQL Editor** en tu dashboard
2. Copia y pega el contenido de `run_all_migrations.sql`
3. Ejecuta el script completo

### Opción 2: Ejecutar Migraciones Individuales

Si prefieres ejecutar las migraciones una por una:

1. Ejecuta primero `001_core_conversations.sql`
2. Luego ejecuta en orden:
   - `003_predictive_models.sql`
   - `004_emotional_intelligence.sql`
   - `005_prompt_optimization.sql`
   - `006_trial_management.sql`
   - `007_roi_tracking.sql`

### Opción 3: Usando Línea de Comandos

```bash
# Desde el directorio migrations/
psql -h your-project.supabase.co \
     -U postgres \
     -d postgres \
     -p 5432 \
     -f run_all_migrations.sql
```

## ⚠️ Prerrequisitos

1. **Tabla conversations existente**: El script asume que ya tienes una tabla `conversations` creada
2. **Permisos de administrador**: Necesitas permisos para crear tablas, índices y funciones
3. **PostgreSQL 14+**: Las migraciones usan características modernas de PostgreSQL

## 📊 Tablas Creadas

### Core System
- `conversations` (actualizada con nuevos campos)

### Predictive ML System (003)
- `predictive_models`
- `prediction_results`
- `model_training_data`
- `prediction_feedback`
- `model_training`
- `feedback`
- `predictions`

### Emotional Intelligence (004)
- `emotional_analysis`
- `personality_analysis`
- `conversation_patterns`
- `conversation_pattern_matches`
- `emotional_evolution`

### Prompt Optimization (005)
- `prompt_variants`
- `hie_prompt_optimizations`
- `hie_gene_performance`
- `prompt_experiments`
- `prompt_usage_log`

### Trial Management (006)
- `trial_users`
- `demo_events`
- `demo_sessions`
- `scheduled_touchpoints`
- `trial_events`
- `trial_configuration`

### ROI Tracking (007)
- `roi_calculations`
- `roi_profession_benchmarks`
- `roi_success_stories`
- `roi_value_components`
- `roi_projections`

## 🔒 Seguridad

Las migraciones incluyen:

1. **Row Level Security (RLS)** habilitado en tablas sensibles
2. **Políticas básicas** de acceso (debes personalizarlas)
3. **Índices optimizados** para performance
4. **Validaciones** en campos críticos

## 🔄 Rollback

Si necesitas revertir las migraciones:

```sql
-- Ejecutar con PRECAUCIÓN - esto eliminará todas las tablas
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public;
```

## 📝 Notas Importantes

1. **Backups**: Siempre haz backup antes de ejecutar migraciones
2. **Ambiente**: Prueba primero en desarrollo/staging
3. **RLS**: Revisa y ajusta las políticas RLS según tus necesidades
4. **Índices**: Monitorea y ajusta índices basado en uso real
5. **Datos iniciales**: Las migraciones incluyen algunos datos de ejemplo

## 🔍 Verificación Post-Migración

Después de ejecutar las migraciones, verifica:

```sql
-- Contar tablas creadas
SELECT COUNT(*) FROM information_schema.tables 
WHERE table_schema = 'public' AND table_type = 'BASE TABLE';

-- Verificar vistas
SELECT COUNT(*) FROM information_schema.views 
WHERE table_schema = 'public';

-- Verificar funciones
SELECT COUNT(*) FROM information_schema.routines
WHERE routine_schema = 'public' AND routine_type = 'FUNCTION';
```

## 🤝 Soporte

Si encuentras problemas:

1. Verifica los logs en Supabase Dashboard
2. Revisa que la tabla `conversations` exista
3. Confirma que tienes los permisos necesarios
4. Consulta la documentación de Supabase

## 📅 Historial de Versiones

- **v1.0.0** (2025-01-19): Migración inicial completa
  - Sistema predictivo ML
  - Inteligencia emocional
  - Optimización de prompts
  - Gestión de trials
  - Tracking de ROI