# Guía de Configuración de Entornos de Trabajo

## Introducción

Este documento proporciona instrucciones detalladas para configurar los entornos de desarrollo, pruebas y producción para el proyecto NGX Voice Sales Agent. Seguir estos pasos garantizará una configuración consistente y evitará problemas comunes relacionados con dependencias y configuraciones.

## Requisitos Previos

- Python 3.9+ instalado
- pip o uv (recomendado) para gestión de paquetes
- Git para control de versiones
- Acceso a la cuenta de Supabase del proyecto
- Credenciales para servicios externos (OpenAI, ElevenLabs)

## Configuración del Entorno de Desarrollo

### 1. Clonar el Repositorio

```bash
git clone [URL_DEL_REPOSITORIO]
cd Agentes\ SKD_voz/
```

### 2. Crear y Activar Entorno Virtual

```bash
# Usando venv (recomendado para desarrollo)
python -m venv .venv
source .venv/bin/activate  # En macOS/Linux
# o
.venv\Scripts\activate     # En Windows
```

### 3. Instalar Dependencias

```bash
# Usando pip
pip install -r requirements.txt

# O usando uv (más rápido)
uv pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```
# Configuración de Base de Datos
SUPABASE_URL=https://[TU_ID_PROYECTO].supabase.co
SUPABASE_KEY=[TU_CLAVE_ANON]
SUPABASE_SERVICE_KEY=[TU_CLAVE_SERVICIO]

# Configuración de Seguridad
JWT_SECRET=[CLAVE_SECRETA_JWT]
LOG_LEVEL=INFO
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
ALLOWED_ORIGINS=http://localhost:3000,https://tu-dominio.com

# Servicios Externos
OPENAI_API_KEY=[TU_CLAVE_API_OPENAI]
ELEVENLABS_API_KEY=[TU_CLAVE_API_ELEVENLABS]
```

### 5. Inicializar la Base de Datos

Para crear las tablas necesarias en tu entorno local:

```bash
# Ejecutar script de migración
python scripts/init_database.py
```

## Configuración del Entorno de Pruebas

### 1. Crear Entorno Virtual para Pruebas

Es recomendable mantener un entorno separado para pruebas para evitar conflictos de dependencias:

```bash
python -m venv .venv_test
source .venv_test/bin/activate  # En macOS/Linux
# o
.venv_test\Scripts\activate     # En Windows
```

### 2. Instalar Dependencias de Prueba

```bash
# Instalar dependencias específicas para pruebas
pip install -r requirements_test.txt
```

### 3. Configurar Variables de Entorno para Pruebas

Crea un archivo `.env.test` con configuraciones específicas para pruebas:

```
# Usar base de datos de prueba
SUPABASE_URL=https://[TU_ID_PROYECTO_TEST].supabase.co
SUPABASE_KEY=[TU_CLAVE_ANON_TEST]
SUPABASE_SERVICE_KEY=[TU_CLAVE_SERVICIO_TEST]

# Configuración de Seguridad
JWT_SECRET=test_secret_key
LOG_LEVEL=DEBUG
RATE_LIMIT_PER_MINUTE=1000  # Valor alto para facilitar pruebas
RATE_LIMIT_PER_HOUR=10000   # Valor alto para facilitar pruebas
ALLOWED_ORIGINS=http://localhost:3000

# Modo de prueba para servicios externos
TEST_MODE=True
```

### 4. Ejecutar Script de Configuración de Pruebas

```bash
# Configurar entorno de pruebas
bash setup_test_env.sh
```

## Configuración del Entorno de Producción

### 1. Configurar Variables de Entorno para Producción

En el servidor de producción, configura las siguientes variables de entorno:

```
# Configuración de Base de Datos
SUPABASE_URL=https://[TU_ID_PROYECTO_PROD].supabase.co
SUPABASE_KEY=[TU_CLAVE_ANON_PROD]
SUPABASE_SERVICE_KEY=[TU_CLAVE_SERVICIO_PROD]

# Configuración de Seguridad
JWT_SECRET=[CLAVE_SECRETA_JWT_PROD]  # Usar una clave fuerte y única
LOG_LEVEL=WARNING  # Menos verboso en producción
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
ALLOWED_ORIGINS=https://tu-dominio-produccion.com

# Servicios Externos
OPENAI_API_KEY=[TU_CLAVE_API_OPENAI_PROD]
ELEVENLABS_API_KEY=[TU_CLAVE_API_ELEVENLABS_PROD]

# Configuración de Producción
ENVIRONMENT=production
DEBUG=False
```

### 2. Despliegue en Producción

```bash
# Ejemplo de despliegue con uvicorn
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Solución de Problemas Comunes

### 1. Problemas de Compatibilidad de Dependencias

Si encuentras errores relacionados con versiones incompatibles:

```bash
# Reinstalar con versiones específicas
pip install fastapi==0.95.1 starlette==0.26.1 httpx==0.23.3
```

### 2. Errores de Tablas Inexistentes

Si aparecen errores como `relation "public.predictive_models" does not exist`:

```bash
# Ejecutar script de inicialización de tablas
python scripts/init_database.py --force
```

### 3. Problemas con el TestClient

Si encuentras errores al usar el TestClient de FastAPI:

```bash
# Usar el cliente compatible personalizado
# Ver ejemplos en tests/security/security_test_config.py
```

## Verificación de la Configuración

Para verificar que tu entorno está correctamente configurado:

```bash
# Verificar conexión a Supabase
python -c "from src.config.database import get_supabase_client; print(get_supabase_client().table('users').select('*', count='exact').execute())"

# Verificar configuración de seguridad
python -c "from src.config.settings import get_settings; print(get_settings().dict())"
```

## Comandos Útiles para el Desarrollo

### Ejecutar la Aplicación en Modo Desarrollo

```bash
uvicorn src.api.main:app --reload --port 8000
```

### Ejecutar Pruebas

```bash
# Ejecutar todas las pruebas
pytest

# Ejecutar pruebas específicas
pytest tests/security/test_security_headers_only.py

# Ejecutar pruebas con cobertura
pytest --cov=src tests/
```

### Verificar Estilo de Código

```bash
# Verificar estilo con flake8
flake8 src tests

# Formatear código con black
black src tests
```

## Próximos Pasos

1. Completar las pruebas de seguridad restantes
2. Finalizar la implementación de los servicios predictivos pendientes
3. Crear scripts de migración para la creación de tablas
4. Desarrollar endpoints de API para exponer las capacidades predictivas
5. Iniciar integración con el Portal Web

## Notas Adicionales

- Mantén actualizado el archivo `requirements.txt` cuando añadas nuevas dependencias
- Documenta cualquier cambio en la estructura de la base de datos
- Realiza pruebas exhaustivas antes de desplegar en producción
- Monitorea el rendimiento y los logs en producción para detectar problemas temprano
