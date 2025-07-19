from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
import asyncio
import time
import uuid
from datetime import datetime
from contextlib import asynccontextmanager

# Import configuration and security
from src.config import settings, Environment
from src.infrastructure.security import secrets_manager, validate_secrets
from src.utils.structured_logging import StructuredLogger
from src.utils.observability import init_observability

from src.api.middleware.rate_limiter import RateLimiter, get_user_from_request
from src.api.middleware.error_handlers import http_exception_handler, validation_exception_handler, internal_exception_handler
from src.api.middleware.security_headers import SecurityHeadersMiddleware
from src.auth.jwt_functions import decode_token
from .routers import conversation
from .routers import qualification
from .routers import analytics
from .routers import predictive
from .routers import model_training
from .routers import auth

# Configure structured logging from settings
StructuredLogger.setup_logging(
    log_level=settings.log_level,
    log_file=settings.log_file,
    include_stack_info=settings.log_include_stack_info
)

# Get logger for main module
logger = StructuredLogger.get_logger("api.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle.
    
    Handles startup and shutdown events with proper resource management.
    """
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    
    # Validate required secrets
    try:
        secrets_valid = await validate_secrets()
        if not secrets_valid:
            logger.error("Required secrets validation failed")
            if settings.is_production:
                raise RuntimeError("Cannot start in production without required secrets")
            else:
                logger.warning("Running in development mode with missing secrets")
    except Exception as e:
        logger.error(f"Error validating secrets: {e}")
        if settings.is_production:
            raise
    
    # Log safe configuration
    logger.info("Configuration loaded successfully")
    logger.debug(f"Safe config: {settings.dict_safe()}")
    
    # Initialize services
    logger.info("Initializing services...")
    
    # Import here to avoid circular imports
    from src.services.conversation_service import ConversationService
    from src.api.routers import conversation as conv_router
    
    # Create and initialize conversation service
    conversation_service = ConversationService()
    await conversation_service.initialize()
    
    # Inject into router
    conv_router.conversation_service = conversation_service
    
    logger.info("API startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down API...")
    # Add cleanup tasks here (close DB connections, etc.)
    logger.info("API shutdown complete")


# Create FastAPI application with lifespan
app = FastAPI(
    title=settings.app_name,
    description="Elite conversational AI system for sales automation",
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
)

# Initialize observability
init_observability(app)

# Configure CORS from settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=settings.allow_credentials,
    allow_methods=settings.allow_methods,
    allow_headers=settings.allow_headers,
    expose_headers=["X-Request-ID", "X-Rate-Limit-Limit", "X-Rate-Limit-Remaining", "X-Rate-Limit-Reset"]
)

# Configure security headers
app.add_middleware(SecurityHeadersMiddleware)

# Configure rate limiting from settings
if settings.rate_limit_enabled:
    app.add_middleware(
        RateLimiter,
        requests_per_minute=settings.rate_limit_per_minute,
        requests_per_hour=settings.rate_limit_per_hour,
        admin_exempt=True,
        whitelist_ips=settings.rate_limit_whitelist_ips,
        whitelist_paths=["/docs", "/redoc", "/openapi.json", "/health"],
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
    """
    Health check endpoint.
    
    Returns basic health status and application information.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.app_version,
        "environment": settings.environment,
        "services": {
            "api": {"status": "up"},
            "secrets": {"status": "configured" if await validate_secrets() else "missing"}
        }
    } 