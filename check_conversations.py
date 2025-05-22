import os
import sys
import json
import uuid
from dotenv import load_dotenv

# Asegurar que el directorio raíz está en el path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Cargar variables de entorno
load_dotenv()

from src.integrations.supabase import supabase_client

def check_conversations_structure():
    """Verificar la estructura de la tabla conversations con valores válidos."""
    client = supabase_client.get_client(admin=True)
    
    # Generar IDs únicos para evitar colisiones
    conversation_id = str(uuid.uuid4())
    customer_id = str(uuid.uuid4())
    
    # Intentar insertar un registro con valor válido para program_type
    test_conversation = {
        "conversation_id": conversation_id,
        "customer_id": customer_id,
        "program_type": "PRIME",  # Valor válido según la restricción
        "phase": "initial_contact",
        "messages": []
    }
    
    print(f"Intentando insertar un registro de prueba en la tabla 'conversations' con ID: {conversation_id}")
    try:
        response = client.table("conversations").insert(test_conversation).execute()
        print(f"Inserción exitosa: {response.data}")
        
        # Consultar el registro insertado
        print("Consultando el registro insertado")
        response = client.table("conversations").select("*").eq("conversation_id", conversation_id).execute()
        if response.data:
            print("Columnas de la tabla 'conversations':")
            print(json.dumps(list(response.data[0].keys()), indent=2))
        else:
            print("No se pudo recuperar el registro insertado")
            
    except Exception as e:
        print(f"Error al insertar registro de prueba: {e}")
        
if __name__ == "__main__":
    check_conversations_structure() 