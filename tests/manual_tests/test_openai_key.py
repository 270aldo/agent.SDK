#!/usr/bin/env python3
"""
Script para probar la validez de la clave API de OpenAI.
"""

import os
import sys
from dotenv import load_dotenv
import openai
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

def test_openai_key():
    """Probar la validez de la clave API de OpenAI"""
    
    # Obtener la clave API de OpenAI
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        logger.error("No se encontró la clave API de OpenAI en las variables de entorno")
        return False
    
    logger.info(f"Clave API de OpenAI (primeros 10 caracteres): {api_key[:10]}...")
    
    try:
        # Configurar la clave API
        client = openai.OpenAI(api_key=api_key)
        
        # Intentar una solicitud simple
        logger.info("Probando la clave API de OpenAI con una solicitud simple...")
        response = client.models.list()
        
        # Si llegamos aquí, la clave es válida
        logger.info("La clave API de OpenAI es válida")
        logger.info(f"Modelos disponibles: {[model.id for model in response.data[:5]]}")
        return True
    except Exception as e:
        logger.error(f"Error al probar la clave API de OpenAI: {e}")
        return False

if __name__ == "__main__":
    test_openai_key()
