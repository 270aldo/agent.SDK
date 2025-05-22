import os
import sys
import json
from dotenv import load_dotenv

# Asegurar que el directorio raíz está en el path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Cargar variables de entorno
load_dotenv()

from src.integrations.supabase import supabase_client

def check_table_structure():
    """Verificar la estructura de las tablas en Supabase."""
    client = supabase_client.get_client(admin=True)
    
    # Consulta para obtener información sobre la tabla conversations
    try:
        response = client.table("conversations").select("*").limit(0).execute()
        print("Estructura de la tabla 'conversations':")
        if response.data:
            # Si hay datos, imprimimos las claves del primer registro
            print(json.dumps(list(response.data[0].keys()), indent=2))
        else:
            print("No hay datos en la tabla, pero la tabla existe")
    except Exception as e:
        print(f"Error al consultar la tabla 'conversations': {e}")
    
    # Consulta para obtener información sobre la tabla customers
    try:
        response = client.table("customers").select("*").limit(0).execute()
        print("\nEstructura de la tabla 'customers':")
        if response.data:
            # Si hay datos, imprimimos las claves del primer registro
            print(json.dumps(list(response.data[0].keys()), indent=2))
        else:
            print("No hay datos en la tabla, pero la tabla existe")
    except Exception as e:
        print(f"Error al consultar la tabla 'customers': {e}")

if __name__ == "__main__":
    check_table_structure() 