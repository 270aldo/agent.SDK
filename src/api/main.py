from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
import os
import time
import uuid
from dotenv import load_dotenv

from src.utils.structured_logging import StructuredLogger

from src.api.middleware.rate_limiter import RateLimiter, get_user_from_request
from src.api.middleware.error_handlers import http_exception_handler, validation_exception_handler, internal_exception_handler
from src.auth.jwt_handler import decode_token
from .routers import conversation
from .routers import qualification
from .routers import analytics
from .routers import predictive
from .routers import model_training
from .routers import auth

# Cargar variables de entorno
load_dotenv()

# Configurar logging estructurado
log_level = os.getenv("LOG_LEVEL", "INFO")
log_file = os.getenv("LOG_FILE", "logs/api.log")
include_stack_info = os.getenv("ENVIRONMENT", "production").lower() != "production"

StructuredLogger.setup_logging(
    log_level=log_level,
    log_file=log_file,
    include_stack_info=include_stack_info
)

# Obtener logger para el módulo principal
logger = StructuredLogger.get_logger("api.main")

# Crear aplicación FastAPI
app = FastAPI(
    title="NGX Sales Agent API",
    description="API para el Agente de Ventas NGX con IA conversacional",
    version="0.1.0",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("ALLOWED_ORIGINS", "*").split(",")],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
    expose_headers=["X-Request-ID", "X-Rate-Limit-Limit", "X-Rate-Limit-Remaining", "X-Rate-Limit-Reset"]
)

# Configurar limitador de tasa
app.add_middleware(
    RateLimiter,
    requests_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", "60")),
    requests_per_hour=int(os.getenv("RATE_LIMIT_PER_HOUR", "1000")),
    admin_exempt=True,
    whitelist_ips=os.getenv("RATE_LIMIT_WHITELIST_IPS", "").split(","),
    whitelist_paths=["/docs", "/redoc", "/openapi.json"],
    get_user_id=get_user_from_request
)

# Middleware para registro de solicitudes y respuestas
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    # Generar ID de solicitud único
    request_id = str(uuid.uuid4())
    
    # Registrar inicio de solicitud
    logger.info(
        f"Solicitud iniciada: {request.method} {request.url.path}",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "query_params": str(request.query_params),
            "client_ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("User-Agent", "unknown")
        }
    )
    
    # Medir tiempo de respuesta
    start_time = time.time()
    
    try:
        # Procesar solicitud
        response = await call_next(request)
        
        # Calcular tiempo de procesamiento
        process_time = time.time() - start_time
        
        # Añadir encabezados de seguridad
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; object-src 'none';"
        
        # Añadir ID de solicitud para seguimiento
        response.headers["X-Request-ID"] = request_id
        
        # Registrar finalización de solicitud
        logger.info(
            f"Solicitud completada: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "status_code": response.status_code,
                "process_time_ms": int(process_time * 1000)
            }
        )
        
        return response
    except Exception as exc:
        # Calcular tiempo hasta el error
        process_time = time.time() - start_time
        
        # Registrar error
        logger.error(
            f"Error en solicitud: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "error": str(exc),
                "error_type": type(exc).__name__,
                "process_time_ms": int(process_time * 1000)
            },
            exc_info=True
        )
        
        # Re-lanzar la excepción para que sea manejada por los manejadores de excepciones
        raise

# Incluir routers
app.include_router(auth.router)  # Incluir primero el router de autenticación
app.include_router(conversation.router)
app.include_router(qualification.router)
app.include_router(analytics.router)
app.include_router(predictive.router)
app.include_router(model_training.router)

# Registrar manejadores de excepciones personalizados
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, internal_exception_handler)

@app.get("/health")
async def health_check():
    """Endpoint para verificar que la API está funcionando."""
    return {"status": "ok", "message": "NGX Sales Agent API está funcionando"}

@app.on_event("startup")
async def startup_event():
    """Evento que se ejecuta al iniciar la aplicación."""
    logger.info("Iniciando aplicación NGX Sales Agent API...")
    
    # Verificar configuración de APIs
    required_env_vars = [
        "OPENAI_API_KEY", 
        "ELEVENLABS_API_KEY", 
        "SUPABASE_URL", 
        "SUPABASE_ANON_KEY",
        "JWT_SECRET"
    ]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.warning(f"Faltan variables de entorno: {', '.join(missing_vars)}")
        
        # Generar advertencia específica para JWT_SECRET
        if "JWT_SECRET" in missing_vars:
            logger.warning("JWT_SECRET no está configurado. Se utilizará una clave predeterminada. " +
                          "Esto es inseguro para entornos de producción.")
    else:
        logger.info("Todas las variables de entorno requeridas están configuradas")

@app.on_event("shutdown")
async def shutdown_event():
    """Evento que se ejecuta al detener la aplicación."""
    logger.info("Deteniendo aplicación NGX Sales Agent API...") 