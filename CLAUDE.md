# NGX Voice Sales Agent - Contexto de Desarrollo

## Resumen del Proyecto

NGX Voice Sales Agent es un sistema avanzado de agentes conversacionales para ventas que integra IA, procesamiento de voz y análisis predictivo. El objetivo principal es crear una plataforma multi-canal que pueda integrarse en diferentes puntos de contacto como lead magnets, páginas educativas, landing pages, y aplicaciones móviles.

## Estado Actual del Proyecto

### Arquitectura Existente
- **Backend**: FastAPI con Python 3.10+
- **Base de Datos**: Supabase (PostgreSQL)
- **IA/NLP**: OpenAI GPT-4, Agents SDK
- **Síntesis de Voz**: ElevenLabs
- **Contenedorización**: Docker + Docker Compose
- **Testing**: Pytest con cobertura del 72%

### Componentes Implementados ✅
- Sistema de conversación base con múltiples servicios NLP
- Análisis de intención avanzado y personalización
- Modelos predictivos (objeciones, necesidades)
- Sistema de seguridad con JWT y rate limiting
- Transferencia a agentes humanos
- Seguimiento post-conversación
- API REST completa con documentación

### Problemas Críticos Identificados ⚠️
1. **Dependencias frágiles**: Importaciones con try/except que pueden fallar silenciosamente
2. **Gestión de errores deficiente**: 7 archivos usan `except: pass`
3. **Configuración incompleta**: Variables de entorno faltantes
4. **Código de debugging**: 8 archivos usan `print()` en lugar de logging
5. **Arquitectura monolítica**: Dificulta escalabilidad multi-plataforma

## Objetivo del Desarrollo Actual

### Meta Principal
Transformar el sistema actual en una plataforma de integración multi-canal que pueda desplegarse como:

1. **App Central (Hub)**: Gestión, analytics y configuración
2. **SDK Web**: Widgets para sitios web, lead magnets, landing pages
3. **SDK Móvil**: Aplicaciones nativas iOS/Android
4. **API Gateway**: Integraciones directas con terceros

### Arquitectura Objetivo

```
┌─────────────────────────────────────────────────────────────┐
│                    NGX VOICE AGENT HUB                     │
│                  (Aplicación Central)                      │
├─────────────────────────────────────────────────────────────┤
│  • Core Agent Engine                                       │
│  • Conversation Management                                 │
│  • Analytics & Reporting                                   │
│  • Admin Dashboard                                         │
│  • API Gateway                                             │
└─────────────────────┬───────────────────────────────────────┘
                      │
              ┌───────┼───────┐
              ▼       ▼       ▼
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │   Web SDK   │ │Mobile SDK   │ │  API Only   │
    │             │ │             │ │             │
    │ • JS Widget │ │ • iOS       │ │ • Direct    │
    │ • React Lib │ │ • Android   │ │   API calls │
    │ • Vue Comp  │ │ • React     │ │ • Webhooks  │
    │             │ │   Native    │ │             │
    └─────────────┘ └─────────────┘ └─────────────┘
```

## Puntos de Integración Objetivo

### 1. Lead Magnets Premium
- Widget discreto que se activa post-descarga
- Contexto educativo/nurturing
- Calificación suave de interés
- Transición a demo personalizada

### 2. Páginas Educativas/Blog
- Widget contextual basado en contenido
- Triggers inteligentes (scroll, tiempo, exit-intent)
- Modo consultor experto
- Analytics de engagement

### 3. Landing Pages de Conversión
- Integración fullscreen o overlay
- Modo ventas de alta intención
- A/B testing integrado
- Personalización de marca

### 4. Aplicaciones Móviles
- SDK nativo optimizado
- Notificaciones push
- Integración con llamadas telefónicas
- Experiencia offline limitada

## Plan de Desarrollo Aprobado

### Fase 1: Refactoring del Core (2-3 semanas) 🔧
**Prioridad**: CRÍTICA
- Corregir gestión de dependencias frágiles
- Implementar manejo de errores robusto
- Centralizar configuración por plataforma
- Crear factory patterns para agentes
- Eliminar código de debugging

### Fase 2: Desarrollo de SDKs (4-5 semanas) 📱
**Prioridad**: ALTA
- SDK JavaScript/TypeScript para web
- Librería de componentes React
- SDK React Native para móvil
- Documentación y ejemplos de integración

### Fase 3: Apps Nativas y PWA (6-8 semanas) 🚀
**Prioridad**: MEDIA
- PWA para dashboard administrativo
- Apps nativas optimizadas
- Sistema de notificaciones
- Optimización de performance

### Fase 4: Integración y Optimización (4-6 semanas) ⚡
**Prioridad**: MEDIA
- A/B testing framework
- Analytics avanzados
- Optimizaciones de performance
- Preparación para producción

## Estructura de Archivos Clave

### Core Services
- `src/services/conversation_service.py` - Servicio principal de conversación
- `src/agents/unified_agent.py` - Agente unificado con detección dinámica
- `src/api/main.py` - Aplicación FastAPI principal
- `src/models/conversation.py` - Modelos de datos de conversación

### APIs y Routers
- `src/api/routers/conversation.py` - Endpoints de conversación
- `src/api/routers/predictive.py` - Servicios predictivos
- `src/api/routers/analytics.py` - Analytics y reportes
- `src/api/middleware/` - Rate limiting y manejo de errores

### Servicios Especializados
- `src/services/predictive_model_service.py` - Modelos predictivos base
- `src/services/enhanced_intent_analysis_service.py` - Análisis de intención
- `src/services/human_transfer_service.py` - Transferencia a humanos
- `src/services/personalization_service.py` - Personalización

### Testing y Configuración
- `tests/` - Suite de pruebas con pytest
- `docker/` - Configuración de contenedores
- `requirements.txt` - Dependencias Python
- `env.example` - Variables de entorno ejemplo

## Configuración de Desarrollo

### Variables de Entorno Requeridas
```env
# APIs de Terceros
OPENAI_API_KEY=your_openai_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key

# Base de Datos
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# Autenticación
JWT_SECRET=your_jwt_secret_key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# Aplicación
DEBUG=True
LOG_LEVEL=INFO
ENVIRONMENT=development
```

### Comandos Comunes
```bash
# Desarrollo local
python run.py --host 0.0.0.0 --port 8000

# Con Docker
docker-compose -f docker/docker-compose.yml up --build

# Testing
pytest tests/ -v --cov=src

# Linting y formato
flake8 src/
black src/
```

## Estándares de Desarrollo

### Patrones de Código
- **Dependency Injection**: Usar factory patterns para servicios
- **Error Handling**: Nunca usar `except: pass`, siempre log errors
- **Logging**: Usar `logging` en lugar de `print()`
- **Type Hints**: Obligatorio en todas las funciones públicas
- **Documentación**: Docstrings en formato Google

### Estructura de Commits
```
feat: nueva funcionalidad
fix: corrección de bugs
refactor: refactorización de código
test: añadir/modificar tests
docs: actualizar documentación
style: cambios de formato/estilo
perf: mejoras de performance
```

## Métricas de Éxito

### Técnicas
- **Cobertura de Tests**: Objetivo 90%+
- **Performance**: <200ms respuesta promedio
- **Disponibilidad**: 99.9% uptime
- **Escalabilidad**: 10,000 conversaciones concurrentes

### Negocio
- **Conversión**: Lead magnet → Conversación: 15%+
- **Calificación**: Conversación → Lead calificado: 60%+
- **Ventas**: Lead calificado → Venta: 25%+
- **Satisfacción**: NPS > 70

## Estado Actual - Fase 1 COMPLETADA ✅

### Refactoring del Core (FINALIZADO)
- ✅ **Dependencias frágiles eliminadas** - AgentFactory implementado
- ✅ **PlatformContext system** - Soporte multi-canal funcional
- ✅ **ConfigManager creado** - Configuraciones por plataforma
- ✅ **Gestión de errores mejorada** - Logging estructurado
- ✅ **Código limpio** - Eliminadas importaciones frágiles

### Próximo Paso - Fase 2: Desarrollo de SDKs

**IMPORTANTE**: Iniciar nueva conversación para Fase 2 con contexto limpio.

#### Tareas Fase 2 (Próxima conversación):
1. **Web SDK (JavaScript/TypeScript)** 
   - Widget core con configuración por plataforma
   - Sistema de eventos y callbacks
   - Integración con API refactorizada
   
2. **React Component Library**
   - Componente `<NGXVoiceAgent />`
   - Hooks personalizados (`useNGXVoice`)
   - Provider de contexto
   
3. **Ejemplos de Integración**
   - Lead magnet demo
   - Landing page integration
   - Blog widget example
   
4. **Mobile SDK Foundation**
   - React Native wrapper
   - Native bridges preparación

## Notas Importantes

- **No crear archivos nuevos** sin justificación clara
- **Priorizar edición** de archivos existentes cuando sea posible
- **Mantener compatibilidad** con API actual durante refactoring
- **Documentar todos los cambios** importantes
- **Testing obligatorio** para nuevas funcionalidades

## Contexto de Negocio

NGX es una empresa de fitness y bienestar que ofrece programas personalizados (PRIME y LONGEVITY). El agente de voz debe:

- Calificar leads según edad y objetivos de fitness
- Personalizar conversaciones por industria (salud, finanzas, tech)
- Detectar intención de compra y objeciones
- Facilitar transferencia a agentes humanos cuando sea necesario
- Generar seguimientos automatizados post-conversación

El objetivo final es crear un embudo de ventas automatizado que genere leads calificados de alta conversión a través de múltiples canales digitales.