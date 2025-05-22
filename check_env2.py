import re

def read_env_file(var_name, default=""):
    """Lee una variable directamente del archivo .env"""
    try:
        with open(".env", "r") as f:
            content = f.read()
            pattern = fr"{var_name}=(.*?)($|\n)"
            match = re.search(pattern, content)
            if match:
                return match.group(1).strip()
    except Exception as e:
        print(f"Error al leer variable {var_name} del archivo .env: {e}")
    return default

# Obtener variables
supabase_url = read_env_file("SUPABASE_URL")
supabase_key = read_env_file("SUPABASE_ANON_KEY")
supabase_service_key = read_env_file("SUPABASE_SERVICE_ROLE_KEY")

# Mostrar valores (solo los primeros 20 caracteres por seguridad)
print(f"SUPABASE_URL: {supabase_url}")
print(f"SUPABASE_ANON_KEY (primeros 20 caracteres): {supabase_key[:20] if supabase_key else 'No definido'}")
print(f"SUPABASE_SERVICE_ROLE_KEY (primeros 20 caracteres): {supabase_service_key[:20] if supabase_service_key else 'No definido'}") 