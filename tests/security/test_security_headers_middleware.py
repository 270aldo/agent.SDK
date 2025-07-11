"""
Tests for Security Headers Middleware.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.middleware.security_headers import SecurityHeadersMiddleware


def test_security_headers_are_added():
    """Test that security headers are added to responses."""
    app = FastAPI()
    app.add_middleware(SecurityHeadersMiddleware)
    
    @app.get("/test")
    def test_endpoint():
        return {"message": "test"}
    
    client = TestClient(app)
    response = client.get("/test")
    
    # Check required security headers
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("X-XSS-Protection") == "1; mode=block"
    assert response.headers.get("Strict-Transport-Security") == "max-age=31536000; includeSubDomains"
    assert "Content-Security-Policy" in response.headers
    assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert "Permissions-Policy" in response.headers


def test_csp_contains_required_directives():
    """Test that CSP header contains all required directives."""
    app = FastAPI()
    app.add_middleware(SecurityHeadersMiddleware)
    
    @app.get("/test")
    def test_endpoint():
        return {"message": "test"}
    
    client = TestClient(app)
    response = client.get("/test")
    
    csp = response.headers.get("Content-Security-Policy", "")
    
    # Check important CSP directives
    assert "default-src 'self'" in csp
    assert "script-src 'self'" in csp
    assert "style-src 'self'" in csp
    assert "object-src 'none'" in csp
    assert "frame-ancestors 'none'" in csp
    assert "base-uri 'self'" in csp
    assert "form-action 'self'" in csp
    assert "upgrade-insecure-requests" in csp


def test_permissions_policy_contains_required_features():
    """Test that Permissions Policy contains required feature restrictions."""
    app = FastAPI()
    app.add_middleware(SecurityHeadersMiddleware)
    
    @app.get("/test")
    def test_endpoint():
        return {"message": "test"}
    
    client = TestClient(app)
    response = client.get("/test")
    
    permissions = response.headers.get("Permissions-Policy", "")
    
    # Check important feature restrictions
    assert "camera=self" in permissions
    assert "microphone=self" in permissions
    assert "payment=none" in permissions
    assert "usb=none" in permissions