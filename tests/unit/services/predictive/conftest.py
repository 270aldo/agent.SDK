"""
Configuración para pruebas de servicios predictivos.

Este módulo configura el entorno de pruebas para los servicios predictivos,
incluyendo la configuración para pruebas asíncronas.
"""

import pytest
import asyncio

# Configuración para pruebas asíncronas
@pytest.fixture
def event_loop():
    """Crear un nuevo event loop para cada prueba."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
