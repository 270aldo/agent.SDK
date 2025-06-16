import pytest
from unittest.mock import patch
import os

from src.utils.observability import _create_resource


@pytest.fixture
def mock_env_vars():
    """Configura variables de entorno para pruebas"""
    with patch.dict(os.environ, {
        "SERVICE_NAME": "test-service",
        "SERVICE_VERSION": "1.0.0",
        "ENVIRONMENT": "test"
    }):
        yield


def test_create_resource(mock_env_vars):
    """Test para la creación del recurso de OpenTelemetry"""
    # Ejecutar la función que queremos probar
    resource = _create_resource()
    
    # Verificar que el recurso contiene los atributos esperados
    attributes = resource.attributes
    assert attributes.get("service.name") == "test-service"
    assert attributes.get("service.version") == "1.0.0"
    assert attributes.get("deployment.environment") == "test"
