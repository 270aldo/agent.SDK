#!/usr/bin/env python3
"""
Script para iniciar la aplicación NGX Sales Agent API.
"""

import os
import argparse
import subprocess
import logging
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

def run_uvicorn(host="127.0.0.1", port=8000, reload=True):
    """
    Ejecutar el servidor de desarrollo uvicorn.
    
    Args:
        host (str): Host para servir la aplicación
        port (int): Puerto para servir la aplicación
        reload (bool): Si se debe recargar la aplicación al detectar cambios
    """
    cmd = [
        "uvicorn", 
        "src.api.main:app", 
        "--host", host, 
        "--port", str(port)
    ]
    
    if reload:
        cmd.append("--reload")
    
    logger.info(f"Iniciando servidor en http://{host}:{port}")
    subprocess.run(cmd)

def run_docker():
    """
    Ejecutar la aplicación usando Docker Compose.
    """
    cmd = [
        "docker-compose", 
        "-f", "docker/docker-compose.yml", 
        "up", 
        "--build"
    ]
    
    logger.info("Iniciando aplicación con Docker Compose")
    subprocess.run(cmd)

def main():
    """
    Función principal para iniciar la aplicación.
    """
    parser = argparse.ArgumentParser(description="Iniciar NGX Sales Agent API")
    parser.add_argument("--docker", action="store_true", help="Ejecutar con Docker Compose")
    parser.add_argument("--host", default="127.0.0.1", help="Host para el servidor (solo sin Docker)")
    parser.add_argument("--port", type=int, default=8000, help="Puerto para el servidor (solo sin Docker)")
    parser.add_argument("--no-reload", action="store_true", help="Desactivar recarga automática (solo sin Docker)")
    
    args = parser.parse_args()
    
    # Verificar requisitos
    missing = []
    if not os.getenv("OPENAI_API_KEY"):
        missing.append("OPENAI_API_KEY")
    if not os.getenv("ELEVENLABS_API_KEY"):
        missing.append("ELEVENLABS_API_KEY")
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_ANON_KEY"):
        missing.append("SUPABASE_URL y/o SUPABASE_ANON_KEY")
    
    if missing:
        logger.error(f"Faltan las siguientes variables de entorno: {', '.join(missing)}")
        logger.error("Por favor crea un archivo .env basado en env.example")
        return
    
    # Ejecutar la aplicación
    if args.docker:
        run_docker()
    else:
        run_uvicorn(host=args.host, port=args.port, reload=not args.no_reload)

if __name__ == "__main__":
    main() 