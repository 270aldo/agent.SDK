import os
import sys
import json
from dotenv import load_dotenv

# Asegurar que el directorio raíz está en el path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Cargar variables de entorno
load_dotenv()

from src.integrations.supabase import supabase_client

def check_table_columns():
    """Verificar las columnas de las tablas en Supabase."""
    client = supabase_client.get_client(admin=True)
    
    # Consultar las columnas de la tabla conversations
    try:
        # información de columnas desde information_schema
        query = """
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_schema = 'public' AND table_name = 'conversations'
        ORDER BY ordinal_position
        """
        
        # Obtener el cliente de la API de postgrest
        conversations_columns = []
        
        # Consulta para ver si se puede ejecutar SQL directamente
        try:
            # Intentar insertar un registro de prueba
            test_conversation = {
                "conversation_id": "00000000-0000-0000-0000-000000000000",
                "customer_id": "00000000-0000-0000-0000-000000000000",
                "program_type": "TEST",
                "phase": "test"
            }
            
            print("Intentando insertar un registro de prueba en la tabla 'conversations'")
            response = client.table("conversations").insert(test_conversation).execute()
            print(f"Inserción exitosa: {response.data}")
            
            # Consultar el registro insertado
            print("Consultando el registro insertado")
            response = client.table("conversations").select("*").eq("conversation_id", "00000000-0000-0000-0000-000000000000").execute()
            if response.data:
                print("Columnas de la tabla 'conversations':")
                print(json.dumps(list(response.data[0].keys()), indent=2))
            else:
                print("No se pudo recuperar el registro insertado")
            
        except Exception as e:
            print(f"Error al insertar registro de prueba: {e}")
            
            # Intentar con el otro posible nombre de campo
            try:
                test_conversation = {
                    "id": "00000000-0000-0000-0000-000000000000",
                    "customer_id": "00000000-0000-0000-0000-000000000000",
                    "program_type": "TEST",
                    "phase": "test"
                }
                
                print("Intentando insertar un registro de prueba con 'id' en lugar de 'conversation_id'")
                response = client.table("conversations").insert(test_conversation).execute()
                print(f"Inserción exitosa: {response.data}")
                
                # Consultar el registro insertado
                print("Consultando el registro insertado")
                response = client.table("conversations").select("*").eq("id", "00000000-0000-0000-0000-000000000000").execute()
                if response.data:
                    print("Columnas de la tabla 'conversations':")
                    print(json.dumps(list(response.data[0].keys()), indent=2))
                else:
                    print("No se pudo recuperar el registro insertado")
            except Exception as e2:
                print(f"Error al insertar registro de prueba con 'id': {e2}")
    
    except Exception as e:
        print(f"Error al consultar las columnas de la tabla 'conversations': {e}")
    
    # Hacer lo mismo para la tabla customers
    try:
        # Intentar insertar un registro de prueba
        test_customer = {
            "id": "00000000-0000-0000-0000-000000000000",
            "name": "Test Customer",
            "email": "test@example.com",
            "age": 30
        }
        
        print("\nIntentando insertar un registro de prueba en la tabla 'customers'")
        response = client.table("customers").insert(test_customer).execute()
        print(f"Inserción exitosa: {response.data}")
        
        # Consultar el registro insertado
        print("Consultando el registro insertado")
        response = client.table("customers").select("*").eq("id", "00000000-0000-0000-0000-000000000000").execute()
        if response.data:
            print("Columnas de la tabla 'customers':")
            print(json.dumps(list(response.data[0].keys()), indent=2))
        else:
            print("No se pudo recuperar el registro insertado")
    except Exception as e:
        print(f"Error al insertar registro de prueba en customers: {e}")

if __name__ == "__main__":
    check_table_columns() 