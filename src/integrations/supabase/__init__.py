# Este archivo permite que el directorio sea tratado como un paquete de Python
from .client import SupabaseClient, supabase_client

__all__ = ["SupabaseClient", "supabase_client"] 