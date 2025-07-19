#!/usr/bin/env python3
"""
Script para verificar la existencia de las tablas de análisis de intención en Supabase.
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

def test_intent_tables():
    """Verificar la existencia de las tablas de análisis de intención en Supabase"""
    
    # Usar directamente las claves proporcionadas
    url = "https://phjhufqvakdgzsomjobs.supabase.co"
    anon_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBoamh1ZnF2YWtkZ3pzb21qb2JzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDgxMjkyODEsImV4cCI6MjA2MzcwNTI4MX0.AUCqqqEx3xDQyLjtBgCW_o52T_SvioNCvdLnmzgbAXs"
    service_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBoamh1ZnF2YWtkZ3pzb21qb2JzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0ODEyOTI4MSwiZXhwIjoyMDYzNzA1MjgxfQ.sW1oVUg2_9pFFa9NwlD2uj_JfVOokLlAToGsufQQn_U"
    
    logger.info(f"URL: {url}")
    logger.info(f"ANON_KEY (primeros 10 caracteres): {anon_key[:10]}...")
    
    try:
        # Conectar con clave de servicio para tener permisos completos
        logger.info("Conectando a Supabase con clave de servicio...")
        client = create_client(url, service_key)
        
        # Verificar tabla intent_models
        logger.info("Verificando tabla intent_models...")
        response = client.table("intent_models").select("count").execute()
        logger.info(f"Tabla intent_models verificada. Respuesta: {response}")
        
        # Verificar tabla intent_analysis_results
        logger.info("Verificando tabla intent_analysis_results...")
        response = client.table("intent_analysis_results").select("count").execute()
        logger.info(f"Tabla intent_analysis_results verificada. Respuesta: {response}")
        
        # Verificar tabla intent_training_data
        logger.info("Verificando tabla intent_training_data...")
        response = client.table("intent_training_data").select("count").execute()
        logger.info(f"Tabla intent_training_data verificada. Respuesta: {response}")
        
        logger.info("¡Todas las tablas de análisis de intención existen en Supabase!")
        return True
        
    except Exception as e:
        logger.error(f"Error al verificar tablas: {e}")
        return False

if __name__ == "__main__":
    test_intent_tables()
