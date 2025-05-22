# NGX Sales Agent API

API para el Agente de Ventas NGX con IA conversacional que aprovecha OpenAI para procesamiento de lenguaje natural y ElevenLabs para síntesis de voz.

## Características

- 🧠 **Procesamiento de Lenguaje Natural**: Utiliza GPT-4 para mantener conversaciones contextuales y naturales.
- 🗣️ **Síntesis de Voz Avanzada**: Integración con ElevenLabs para generar respuestas de voz naturales y expresivas.
- 💾 **Persistencia en Supabase**: Almacenamiento de conversaciones y datos de clientes en PostgreSQL mediante Supabase.
- 🔄 **Arquitectura Asíncrona**: API completamente asíncrona para manejar múltiples conversaciones simultáneas.
- 🚀 **Containerización con Docker**: Facilidad de despliegue y desarrollo mediante contenedores.

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

4. Configura la base de datos en Supabase:
   ```bash
   python scripts/setup_db.py
   ```

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

## Licencia

[MIT](LICENSE) 