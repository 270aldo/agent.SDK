#!/usr/bin/env python3
"""
Demo para mostrar cómo utilizar la API del Agente de Ventas NGX.
Este script muestra cómo iniciar una conversación, enviar mensajes y finalizar una conversación.
"""

import os
import sys
import asyncio
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List
import requests

# Obtener la ruta del directorio raíz del proyecto
ROOT_DIR = Path(__file__).parent.parent.absolute()
# Añadir el directorio raíz al PYTHONPATH
sys.path.insert(0, str(ROOT_DIR))

from src.models.conversation import CustomerData

# URLs para los endpoints (local)
BASE_URL = "http://localhost:8000"
HEALTH_ENDPOINT = f"{BASE_URL}/health"
START_CONVERSATION_ENDPOINT = f"{BASE_URL}/conversations/start"
SEND_MESSAGE_ENDPOINT = f"{BASE_URL}/conversations/{{}}/message"
END_CONVERSATION_ENDPOINT = f"{BASE_URL}/conversations/{{}}/end"
GET_AUDIO_ENDPOINT = f"{BASE_URL}/conversations/{{}}/audio"

def check_api_status() -> bool:
    """
    Verificar si la API está en funcionamiento.
    
    Returns:
        bool: True si la API está funcionando, False si no
    """
    try:
        response = requests.get(HEALTH_ENDPOINT)
        if response.status_code == 200:
            print("✅ API en funcionamiento")
            return True
        else:
            print(f"❌ API no disponible. Código: {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"❌ Error al conectar con la API: {e}")
        return False

def start_conversation(
    customer_name: str,
    customer_email: str, 
    program_type: str = "PRIME"
) -> Dict[str, Any]:
    """
    Iniciar una nueva conversación.
    
    Args:
        customer_name (str): Nombre del cliente
        customer_email (str): Email del cliente
        program_type (str): Tipo de programa ("PRIME" o "LONGEVITY")
        
    Returns:
        Dict[str, Any]: Respuesta de la API
    """
    # Datos de prueba para el cliente
    customer_data = {
        "name": customer_name,
        "email": customer_email,
        "age": 42,
        "gender": "male",
        "occupation": "CEO",
        "goals": {
            "primary": "aumentar energía y rendimiento",
            "secondary": ["mejorar concentración", "gestionar estrés"]
        }
    }
    
    # Datos para la solicitud
    request_data = {
        "customer_data": customer_data,
        "program_type": program_type
    }
    
    # Enviar solicitud
    response = requests.post(
        START_CONVERSATION_ENDPOINT,
        json=request_data
    )
    
    # Procesar respuesta
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Conversación iniciada: {data['conversation_id']}")
        print(f"🤖 Mensaje inicial: {data['message']}")
        return data
    else:
        print(f"❌ Error al iniciar conversación: {response.status_code}")
        print(response.text)
        return {}

def send_message(conversation_id: str, message: str) -> Dict[str, Any]:
    """
    Enviar un mensaje a una conversación existente.
    
    Args:
        conversation_id (str): ID de la conversación
        message (str): Mensaje a enviar
        
    Returns:
        Dict[str, Any]: Respuesta de la API
    """
    # URL para enviar mensaje
    endpoint = SEND_MESSAGE_ENDPOINT.format(conversation_id)
    
    # Datos para la solicitud
    request_data = {
        "message": message
    }
    
    # Enviar solicitud
    response = requests.post(
        endpoint,
        json=request_data
    )
    
    # Procesar respuesta
    if response.status_code == 200:
        data = response.json()
        print(f"🤖 Respuesta: {data['message']}")
        return data
    else:
        print(f"❌ Error al enviar mensaje: {response.status_code}")
        print(response.text)
        return {}

def end_conversation(conversation_id: str) -> Dict[str, Any]:
    """
    Finalizar una conversación.
    
    Args:
        conversation_id (str): ID de la conversación
        
    Returns:
        Dict[str, Any]: Respuesta de la API
    """
    # URL para finalizar conversación
    endpoint = END_CONVERSATION_ENDPOINT.format(conversation_id)
    
    # Enviar solicitud
    response = requests.post(endpoint)
    
    # Procesar respuesta
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Conversación finalizada")
        print(f"🤖 Mensaje final: {data['message']}")
        return data
    else:
        print(f"❌ Error al finalizar conversación: {response.status_code}")
        print(response.text)
        return {}

def get_audio(conversation_id: str, save_to: str = None) -> bool:
    """
    Obtener el audio de la última respuesta del agente.
    
    Args:
        conversation_id (str): ID de la conversación
        save_to (str, optional): Ruta donde guardar el archivo de audio
        
    Returns:
        bool: True si se descargó correctamente, False si no
    """
    # URL para obtener audio
    endpoint = GET_AUDIO_ENDPOINT.format(conversation_id)
    
    # Enviar solicitud
    response = requests.get(endpoint)
    
    # Procesar respuesta
    if response.status_code == 200:
        # Generar nombre de archivo si no se proporcionó
        if not save_to:
            save_to = f"response_{conversation_id[:8]}.mp3"
        
        # Guardar archivo
        with open(save_to, "wb") as f:
            f.write(response.content)
        
        print(f"✅ Audio guardado en: {save_to}")
        return True
    else:
        print(f"❌ Error al obtener audio: {response.status_code}")
        print(response.text)
        return False

def simulate_basic_conversation():
    """Simular una conversación básica usando la API."""
    # Verificar estado de la API
    if not check_api_status():
        print("Asegúrate de que la API esté en funcionamiento con 'python run.py'")
        return
    
    # Iniciar conversación
    print("\n1. Iniciando conversación...")
    response = start_conversation(
        customer_name="Carlos Pérez",
        customer_email="carlos.perez@example.com",
        program_type="PRIME"
    )
    
    if not response:
        return
    
    conversation_id = response["conversation_id"]
    
    # Simular algunos mensajes
    print("\n2. Enviando mensajes...")
    messages = [
        "Me interesa mejorar mi energía durante el día, especialmente en las tardes.",
        "¿Cuánto cuesta el programa? Es un factor importante para mí.",
        "Entiendo, ¿qué resultados puedo esperar en las primeras semanas?",
        "Me parece bien, ¿cómo empezamos?"
    ]
    
    for i, message in enumerate(messages):
        print(f"\nMensaje {i+1}: '{message}'")
        response = send_message(conversation_id, message)
        
        # Descargar audio de la respuesta (solo para el último mensaje)
        if i == len(messages) - 1:
            print("\n3. Descargando audio de la última respuesta...")
            get_audio(conversation_id, f"respuesta_{i+1}.mp3")
    
    # Finalizar conversación
    print("\n4. Finalizando conversación...")
    end_conversation(conversation_id)

def main():
    """Función principal."""
    parser = argparse.ArgumentParser(description="Demo del API del Agente de Ventas NGX")
    parser.add_argument("--host", default="localhost", help="Host de la API")
    parser.add_argument("--port", type=int, default=8000, help="Puerto de la API")
    
    args = parser.parse_args()
    
    # Actualizar URL base
    global BASE_URL, HEALTH_ENDPOINT, START_CONVERSATION_ENDPOINT, SEND_MESSAGE_ENDPOINT, END_CONVERSATION_ENDPOINT, GET_AUDIO_ENDPOINT
    BASE_URL = f"http://{args.host}:{args.port}"
    HEALTH_ENDPOINT = f"{BASE_URL}/health"
    START_CONVERSATION_ENDPOINT = f"{BASE_URL}/conversations/start"
    SEND_MESSAGE_ENDPOINT = f"{BASE_URL}/conversations/{{}}/message"
    END_CONVERSATION_ENDPOINT = f"{BASE_URL}/conversations/{{}}/end"
    GET_AUDIO_ENDPOINT = f"{BASE_URL}/conversations/{{}}/audio"
    
    # Ejecutar simulación
    simulate_basic_conversation()

if __name__ == "__main__":
    main() 