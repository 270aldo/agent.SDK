# NGX Sales Agent API

API para el Agente de Ventas NGX con IA conversacional que aprovecha OpenAI para procesamiento de lenguaje natural y ElevenLabs para síntesis de voz. Incluye capacidades avanzadas de análisis de intención, personalización y seguimiento post-conversación.

## Características

### Capacidades Principales
- 🧠 **Procesamiento de Lenguaje Natural**: Utiliza GPT-4 para mantener conversaciones contextuales y naturales.
- 🗣️ **Síntesis de Voz Avanzada**: Integración con ElevenLabs para generar respuestas de voz naturales y expresivas.
- 💾 **Persistencia en Supabase**: Almacenamiento de conversaciones y datos de clientes en PostgreSQL mediante Supabase.
- 🔄 **Arquitectura Asíncrona**: API completamente asíncrona para manejar múltiples conversaciones simultáneas.
- 🚀 **Containerización con Docker**: Facilidad de despliegue y desarrollo mediante contenedores.

### Características Avanzadas
- 🎯 **Análisis de Intención Mejorado**: 
  - Análisis de sentimiento para detectar el tono del usuario
  - Personalización por industria (salud, finanzas, tecnología, educación)
  - Aprendizaje continuo basado en conversaciones previas
- 👤 **Transferencia a Agentes Humanos**: 
  - Detección automática de solicitudes de transferencia
  - Gestión de cola de solicitudes y asignación de agentes
  - Seguimiento del estado de transferencias
- 📅 **Seguimiento Post-Conversación**: 
  - Programación automática de seguimientos basados en intención
  - Generación de emails personalizados según el tipo de seguimiento
  - Gestión de estados y respuestas de seguimiento
- 🎭 **Personalización Dinámica**: 
  - Ajuste del tono y estilo según el perfil del usuario
  - Generación de saludos y despedidas personalizadas
  - Adaptación de la complejidad del mensaje

## Prerrequisitos

- Python 3.10 o superior
- Docker y Docker Compose (opcional, para desarrollo en contenedores)
- Cuenta en OpenAI con API key
- Cuenta en ElevenLabs con API key
- Cuenta en Supabase con proyecto configurado

## Configuración

1. Clona este repositorio:
   ```bash
   git clone <url-del-repositorio>
   cd ngx-sales-agent
   ```

2. Crea un archivo `.env` a partir del ejemplo:
   ```bash
   cp env.example .env
   ```

3. Edita el archivo `.env` con tus claves de API y configuración:
   ```
   # OpenAI
   OPENAI_API_KEY=tu_api_key_de_openai
   
   # ElevenLabs
   ELEVENLABS_API_KEY=tu_api_key_de_elevenlabs
   
   # Supabase
   SUPABASE_URL=tu_url_de_supabase
   SUPABASE_ANON_KEY=tu_clave_anonima_de_supabase
   SUPABASE_SERVICE_ROLE_KEY=tu_clave_de_servicio_de_supabase
   
   # Configuración de la aplicación
   DEBUG=True
   LOG_LEVEL=INFO
   ```

4. Configura las tablas en la base de datos de Supabase ejecutando los scripts SQL:
   ```bash
   # Tablas para el sistema de calificación de leads
   python scripts/run_qualification_migrations.py
   
   # Tablas para el sistema de transferencia a humanos
   python scripts/create_human_transfer_tables.sql
   
   # Tablas para el sistema de seguimiento post-conversación
   python scripts/create_follow_up_tables.sql
   
   # Tablas para el sistema de análisis de intención mejorado
   python scripts/create_intent_analysis_tables.sql
   ```
   
   Alternativamente, puedes ejecutar los scripts SQL directamente en el editor SQL de Supabase.

## Desarrollo Local

### Usando Python directamente

1. Crea un entorno virtual e instala las dependencias:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Ejecuta la aplicación:
   ```bash
   uvicorn src.api.main:app --reload
   ```

### Usando Docker

1. Construye y ejecuta los contenedores:
   ```bash
   docker-compose -f docker/docker-compose.yml up --build
   ```

   Para producción puedes usar la misma imagen pero sin recarga automática y con
   múltiples procesos de trabajo:

   ```bash
   docker build -f docker/Dockerfile -t ngx-agent .
   docker run -p 8000:8000 ngx-agent
   ```

## API Endpoints

La API estará disponible en `http://localhost:8000` con los siguientes endpoints:

- **GET /health**: Verificar que la API está funcionando.
- **POST /conversations/start**: Iniciar una nueva conversación.
- **POST /conversations/{conversation_id}/message**: Enviar un mensaje a una conversación existente.
- **GET /conversations/{conversation_id}/audio**: Obtener el audio de respuesta para el último mensaje del asistente.
- **POST /conversations/{conversation_id}/end**: Finalizar una conversación.
- **GET /conversations/{conversation_id}**: Obtener el estado completo de una conversación.

Para documentación completa de la API, visita `http://localhost:8000/docs` después de iniciar la aplicación.

## Ejemplos de Uso

### Iniciar una conversación

```bash
curl -X 'POST' \
  'http://localhost:8000/conversations/start' \
  -H 'Content-Type: application/json' \
  -d '{
    "customer_data": {
      "name": "Juan Pérez",
      "email": "juan@ejemplo.com",
      "age": 42,
      "gender": "male",
      "occupation": "CEO",
      "goals": {
        "primary": "increase_energy",
        "secondary": ["improve_focus", "stress_management"]
      }
    },
    "program_type": "PRIME"
  }'
```

### Enviar un mensaje

```bash
curl -X 'POST' \
  'http://localhost:8000/conversations/{conversation_id}/message' \
  -H 'Content-Type: application/json' \
  -d '{
    "message": "Me interesa mejorar mi energía durante el día."
  }'
```

## Plan de Mejora

El proyecto tiene planificadas las siguientes mejoras para las próximas versiones:

### Fase 1: Estabilización y Pruebas (2-3 semanas)
- Implementación de manejo de errores robusto
- Creación de suite de pruebas automatizadas
- Optimización de rendimiento de operaciones existentes

### Fase 2: Mejoras en NLP y Análisis (3-4 semanas)
- Integración de procesamiento de lenguaje natural avanzado
- Implementación de embeddings y vectorización
- Mejora del sistema de aprendizaje continuo

### Fase 3: Personalización Avanzada (2-3 semanas)
- Desarrollo de perfiles de usuario dinámicos
- Implementación de ajustes de voz basados en emociones
- Creación de sistema de recomendaciones personalizado

### Fase 4: Capacidades Predictivas (3-4 semanas)
- Implementación de modelos predictivos
- Desarrollo de motor de decisiones
- Creación de sistema de anticipación de objeciones

## Licencia

[MIT](LICENSE) 