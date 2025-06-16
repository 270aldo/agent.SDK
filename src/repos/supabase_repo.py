"""Implementación de BaseRepo usando Supabase.

Envuelve ResilientSupabaseClient para exponer una interfaz desacoplada que pueda
mockearse fácilmente en tests.
"""
from typing import Any, Dict, List, Optional

from src.integrations.supabase.resilient_client import ResilientSupabaseClient
from .base_repo import BaseRepo


class SupabaseRepo(BaseRepo):
    """Repo concreto para Supabase."""

    def __init__(self, client: Optional[ResilientSupabaseClient] = None):
        self._client = client or ResilientSupabaseClient()

    async def insert(self, table: str, data: Dict[str, Any]) -> Any:
        return self._client.table(table).insert(data).execute()

    async def select(self, table: str, filters: Optional[Dict[str, Any]] = None):
        query = self._client.table(table).select("*")
        if filters:
            for k, v in filters.items():
                query = query.eq(k, v)
        result = query.execute()
        return result.data if hasattr(result, "data") else []

    async def update(self, table: str, data: Dict[str, Any], filters: Dict[str, Any]):
        query = self._client.table(table).update(data)
        for k, v in filters.items():
            query = query.eq(k, v)
        return query.execute()

    async def delete(self, table: str, filters: Dict[str, Any]):
        query = self._client.table(table).delete()
        for k, v in filters.items():
            query = query.eq(k, v)
        return query.execute()
