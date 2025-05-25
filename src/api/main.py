from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
from dotenv import load_dotenv
from .routers import conversation
from .routers import qualification
from .routers import analytics
from .routers import predictive

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Crear aplicación FastAPI
app = FastAPI(
    title="NGX Sales Agent API",
    description="API para el Agente de Ventas NGX con IA conversacional",
    version="0.1.0",
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
app.include_router(analytics.router)
app.include_router(predictive.router)

@app.get("/health")
async def health_check():
    """Endpoint para verificar que la API está funcionando."""
    return {"status": "ok", "message": "NGX Sales Agent API está funcionando"}

@app.on_event("startup")
async def startup_event():
    """Evento que se ejecuta al iniciar la aplicación."""
    logger.info("Iniciando aplicación NGX Sales Agent API...")
    
    # Verificar configuración de APIs
    required_env_vars = ["OPENAI_API_KEY", "ELEVENLABS_API_KEY", "SUPABASE_URL", "SUPABASE_ANON_KEY"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.warning(f"Faltan variables de entorno: {', '.join(missing_vars)}")
    else:
        logger.info("Todas las variables de entorno requeridas están configuradas")

@app.on_event("shutdown")
async def shutdown_event():
    """Evento que se ejecuta al detener la aplicación."""
    logger.info("Deteniendo aplicación NGX Sales Agent API...") 