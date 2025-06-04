#!/usr/bin/env python3
import pytest
pytest.skip("manual script", allow_module_level=True)
"""
Script para probar la conexión a Supabase directamente.
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

def test_connection():
    """Probar conexión a Supabase con las credenciales del .env"""
    
    # Usar directamente las claves proporcionadas
    url = "https://phjhufqvakdgzsomjobs.supabase.co"
    anon_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBoamh1ZnF2YWtkZ3pzb21qb2JzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDgxMjkyODEsImV4cCI6MjA2MzcwNTI4MX0.AUCqqqEx3xDQyLjtBgCW_o52T_SvioNCvdLnmzgbAXs"
    service_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBoamh1ZnF2YWtkZ3pzb21qb2JzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0ODEyOTI4MSwiZXhwIjoyMDYzNzA1MjgxfQ.sW1oVUg2_9pFFa9NwlD2uj_JfVOokLlAToGsufQQn_U"
    
    logger.info(f"URL: {url}")
    logger.info(f"ANON_KEY (primeros 10 caracteres): {anon_key[:10]}...")
    logger.info(f"SERVICE_KEY (primeros 10 caracteres): {service_key[:10]}...")
    
    try:
        # Probar con clave anónima
        logger.info("Probando conexión con clave anónima...")
        client = create_client(url, anon_key)
        response = client.table("conversations").select("*").limit(1).execute()
        logger.info(f"Conexión exitosa con clave anónima. Respuesta: {response}")
    except Exception as e:
        logger.error(f"Error al conectar con clave anónima: {e}")
    
    try:
        # Probar con clave de servicio
        logger.info("Probando conexión con clave de servicio...")
        admin_client = create_client(url, service_key)
        response = admin_client.table("conversations").select("*").limit(1).execute()
        logger.info(f"Conexión exitosa con clave de servicio. Respuesta: {response}")
    except Exception as e:
        logger.error(f"Error al conectar con clave de servicio: {e}")

if __name__ == "__main__":
    test_connection()
