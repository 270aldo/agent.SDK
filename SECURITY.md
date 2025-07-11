# Guía de Seguridad - NGX Voice Sales Agent

## Manejo de Variables de Entorno

### ✅ Mejores Prácticas Implementadas

1. **No hay archivos .env en el control de versiones**
   - El archivo `.gitignore` incluye patrones para excluir todos los archivos `.env*`
   - Solo `env.example` está permitido en el repositorio

2. **Archivo env.example disponible**
   - Proporciona una plantilla con todas las variables requeridas
   - No contiene valores reales, solo placeholders

### 🔒 Configuración de Variables de Entorno

#### Para Desarrollo Local:
1. Copiar `env.example` a `.env`:
   ```bash
   cp env.example .env
   ```

2. Editar `.env` con valores reales:
   ```bash
   # NUNCA commitear este archivo
   nano .env
   ```

#### Para CI/CD:
Usar secretos del pipeline en lugar de archivos:

**GitHub Actions:**
```yaml
env:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  ELEVENLABS_API_KEY: ${{ secrets.ELEVENLABS_API_KEY }}
  SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
  SUPABASE_ANON_KEY: ${{ secrets.SUPABASE_ANON_KEY }}
  JWT_SECRET: ${{ secrets.JWT_SECRET }}
```

**GitLab CI:**
```yaml
variables:
  OPENAI_API_KEY: $OPENAI_API_KEY
  ELEVENLABS_API_KEY: $ELEVENLABS_API_KEY
  # etc...
```

#### Para Producción:
Usar servicios de gestión de secretos:

- **AWS**: AWS Secrets Manager o Parameter Store
- **Azure**: Azure Key Vault
- **Google Cloud**: Secret Manager
- **Kubernetes**: Kubernetes Secrets
- **Docker**: Docker Secrets (Swarm mode)

### 🛡️ Headers de Seguridad

Los headers de seguridad deben configurarse en el middleware de FastAPI:

```python
# src/api/middleware/security_headers.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';"
        
        return response
```

### 🔐 Checklist de Seguridad

- [ ] **Variables de Entorno**
  - [ ] Archivo `.env` creado localmente (no en Git)
  - [ ] Todos los secretos configurados en CI/CD
  - [ ] Sin valores hardcodeados en el código

- [ ] **JWT Configuration**
  - [ ] JWT_SECRET configurado (sin default)
  - [ ] JWT_ALGORITHM = "HS256"
  - [ ] JWT_ACCESS_TOKEN_EXPIRE_MINUTES configurado

- [ ] **CORS Configuration**
  - [ ] ALLOWED_ORIGINS configurado específicamente
  - [ ] Sin wildcard "*" en producción

- [ ] **Rate Limiting**
  - [ ] RATE_LIMIT_PER_MINUTE configurado
  - [ ] RATE_LIMIT_PER_HOUR configurado

- [ ] **API Keys**
  - [ ] Todas las API keys en variables de entorno
  - [ ] Rotación regular de keys
  - [ ] Diferentes keys para dev/staging/prod

### 📝 Validación

Para validar la configuración de seguridad:

```bash
# Verificar que no hay archivos .env en Git
git ls-files | grep -E "\.env"

# Ejecutar tests de seguridad
pytest tests/security/ -v

# Verificar headers de seguridad
curl -I http://localhost:8000/health
```

### 🚨 Respuesta a Incidentes

Si se expone accidentalmente un secreto:

1. **Rotar inmediatamente** el secreto expuesto
2. **Revisar logs** para detectar uso no autorizado
3. **Notificar** al equipo de seguridad
4. **Actualizar** todos los servicios con el nuevo secreto
5. **Documentar** el incidente y las lecciones aprendidas

### 🔧 Herramientas Recomendadas

- **git-secrets**: Previene commits de secretos
- **truffleHog**: Escanea el historial de Git
- **detect-secrets**: Pre-commit hook para secretos
- **vault**: Gestión centralizada de secretos