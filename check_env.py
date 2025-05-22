import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Obtener variables
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_ANON_KEY")
supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Mostrar valores (solo los primeros 20 caracteres por seguridad)
print(f"SUPABASE_URL: {supabase_url}")
print(f"SUPABASE_ANON_KEY (primeros 20 caracteres): {supabase_key[:20] if supabase_key else 'No definido'}")
print(f"SUPABASE_SERVICE_ROLE_KEY (primeros 20 caracteres): {supabase_service_key[:20] if supabase_service_key else 'No definido'}") 