"""Interfaz base para repositorios de persistencia.

Proporciona métodos CRUD asíncronos que pueden ser implementados para distintos
back-ends (Supabase, DynamoDB, Postgres, etc.).
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union


class BaseRepo(ABC):
    """Interfaz CRUD mínima."""

    @abstractmethod
    async def insert(self, table: str, data: Dict[str, Any]) -> Any:
        ...

    @abstractmethod
    async def select(self, table: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        ...

    @abstractmethod
    async def update(self, table: str, data: Dict[str, Any], filters: Dict[str, Any]) -> Any:
        ...

    @abstractmethod
    async def delete(self, table: str, filters: Dict[str, Any]) -> Any:
        ...

    # Métodos auxiliares opcionales
    async def upsert(self, table: str, data: Dict[str, Any], conflict_columns: Union[str, List[str]]):
        raise NotImplementedError
