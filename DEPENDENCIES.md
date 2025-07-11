# Guía de Dependencias - NGX Voice Sales Agent

## Estructura de Requirements

El proyecto tiene tres archivos de requirements organizados jerárquicamente:

### 1. `requirements.txt` - Dependencias Base
Contiene las dependencias mínimas necesarias para ejecutar la aplicación en producción.

```bash
# Instalar solo dependencias de producción
pip install -r requirements.txt
```

### 2. `requirements-test.txt` - Dependencias de Testing
Incluye requirements.txt + herramientas de testing.

```bash
# Instalar dependencias de producción + testing
pip install -r requirements-test.txt
```

### 3. `requirements-dev.txt` - Entorno de Desarrollo Completo
Incluye requirements-test.txt + herramientas de desarrollo, linting, y observabilidad.

```bash
# Instalar entorno de desarrollo completo
pip install -r requirements-dev.txt
```

## Instalación Recomendada

### Para Desarrollo Local:
```bash
# Activar entorno virtual
source .venv_clean/bin/activate  # macOS/Linux
# o
.venv_clean\Scripts\activate     # Windows

# Instalar todas las dependencias de desarrollo
pip install -r requirements-dev.txt
```

### Para CI/CD Pipeline:
```bash
# Solo testing
pip install -r requirements-test.txt
```

### Para Producción:
```bash
# Solo dependencias core
pip install -r requirements.txt
```

## Notas Importantes

- **langchain**: Mencionado en requirements_simple.txt pero no incluido en la consolidación. Evaluar si es necesario.
- **OpenTelemetry**: Las dependencias de observabilidad son opcionales. La aplicación funciona sin ellas.
- **ElevenLabs**: Versión pinned a 1.17.0 para estabilidad.
- **Pre-commit**: Incluido en requirements-dev.txt para configurar hooks de calidad de código.

## Verificación de Instalación

```bash
# Verificar instalación correcta
python -c "import fastapi; print(f'FastAPI: {fastapi.__version__}')"
python -c "import openai; print(f'OpenAI: {openai.__version__}')"
```