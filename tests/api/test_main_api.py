"""
Integration tests for the main API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add the project root to the Python path to allow imports from src
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the FastAPI app instance
# This import might fail if environment variables required by the app at import time are not set.
# For example, if OpenAIEngine or SupabaseClient are initialized at the module level in main.py
# and they require environment variables.
try:
    from src.api.main import app
except ImportError as e:
    # Handle cases where critical env vars might be missing for app setup
    # This is a common issue in test environments if not all .env vars are loaded/available
    # or if services are initialized at import time.
    print(f"Error importing FastAPI app: {e}")
    print("Ensure all necessary environment variables are set or mock services at app startup for tests.")
    app = None # Set app to None so tests can be skipped if import fails


@pytest.fixture(scope="module")
def client():
    """
    Provides a TestClient instance for API testing.
    Skips tests if the app could not be imported.
    """
    if app is None:
        pytest.skip("FastAPI app could not be imported, skipping API tests.")
    
    # In a real-world scenario, you might need to ensure that environment variables
    # are loaded before the app is imported, or that the app's dependencies
    # are mocked during testing if they connect to external services on startup.
    # For example, using pytest-dotenv or by setting them up in a conftest.py.
    
    # For now, we assume that if `app` is not None, it loaded correctly.
    with TestClient(app) as test_client:
        yield test_client

def test_health_check(client: TestClient):
    """
    Tests the /health endpoint.
    """
    response = client.get("/health")
    
    assert response.status_code == 200
    expected_json = {"status": "ok", "message": "NGX Sales Agent API está funcionando"}
    
    # Comparing dictionaries directly is more robust than string comparison of JSON
    assert response.json() == expected_json

# Example of how to run these tests:
# 1. Ensure `pytest`, `httpx`, and `fastapi` are in requirements.txt and installed.
# 2. Navigate to the project root in your terminal.
# 3. Run the command: `pytest`
#
# Notes for running API tests:
# - Environment Variables: The FastAPI application (`src.api.main.app`) might require
#   environment variables to be set to initialize services (like OpenAI, Supabase clients).
#   If these are not set, importing `app` might fail or tests might not behave as expected.
#   Consider using a `.env.test` file and `python-dotenv` (or `pytest-dotenv`) to manage
#   test-specific configurations.
# - Mocking Services: For true integration tests of API endpoints without hitting external
#   services, you would typically mock the service dependencies of your FastAPI app.
#   This can be done using FastAPI's dependency overrides feature.
#   For example, mocking `ConversationService` for endpoints that use it.
#   The /health endpoint is simple and usually doesn't have external dependencies.
# - Database State: If API tests interact with a database, ensure a consistent DB state
#   for each test run (e.g., by using a test database, transactions, or data fixtures).
#   The /health endpoint typically does not interact with the DB.
