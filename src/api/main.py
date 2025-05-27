from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import logging
# Removed os and load_dotenv imports

from src.config import settings # Importar la configuración centralizada
from .routers import conversation
from .routers import qualification

# Configurar logging using settings
logging.basicConfig(
    level=settings.LOG_LEVEL.upper(), # Use settings.LOG_LEVEL
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Crear aplicación FastAPI
app = FastAPI(
    title="NGX Sales Agent API",
    description="API para el Agente de Ventas NGX con IA conversacional",
    version="0.1.0", # Consider updating version if significant changes
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, limitar a orígenes específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(conversation.router)
app.include_router(qualification.router)

@app.get("/health")
async def health_check():
    """Endpoint para verificar que la API está funcionando."""
    return {"status": "ok", "message": "NGX Sales Agent API está funcionando"}

@app.on_event("startup")
async def startup_event():
    """Evento que se ejecuta al iniciar la aplicación."""
    logger.info("Iniciando aplicación NGX Sales Agent API...")
    
    # Pydantic maneja la validación de variables de entorno al instanciar `settings`.
    # Si falta alguna variable crítica definida en AppSettings, la aplicación
    # no se iniciará correctamente debido a un error de validación de Pydantic.
    logger.info("Application settings loaded and validated by Pydantic.")

    if settings.DEBUG:
        logger.debug("--- Debug Mode: Loaded Settings Overview ---")
        logger.debug(f"Supabase URL: {settings.SUPABASE_URL}")
        logger.debug(f"Log Level: {settings.LOG_LEVEL}")
        # No loguear API keys completas, incluso en debug. Pydantic ya las cargó.
        logger.debug(f"OpenAI API Key Loaded: {'Yes' if settings.OPENAI_API_KEY else 'No'}")
        logger.debug(f"ElevenLabs API Key Loaded: {'Yes' if settings.ELEVENLABS_API_KEY else 'No'}")
        logger.debug(f"Supabase Anon Key Loaded: {'Yes' if settings.SUPABASE_ANON_KEY else 'No'}")
        logger.debug(f"Supabase Service Role Key Loaded: {'Yes' if settings.SUPABASE_SERVICE_ROLE_KEY else 'No'}")
        logger.debug("-------------------------------------------")
        
@app.on_event("shutdown")
async def shutdown_event():
    """Evento que se ejecuta al detener la aplicación."""
    logger.info("Deteniendo aplicación NGX Sales Agent API...") 