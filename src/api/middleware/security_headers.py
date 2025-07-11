"""
Security Headers Middleware for NGX Voice Sales Agent.

This middleware adds security headers to all HTTP responses to protect
against common web vulnerabilities.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses."""

    async def dispatch(self, request: Request, call_next):
        """Add security headers to the response."""
        response = await call_next(request)
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Prevent clickjacking attacks
        response.headers["X-Frame-Options"] = "DENY"
        
        # Enable XSS filter in older browsers
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Force HTTPS
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Content Security Policy
        # Note: Adjust based on your actual needs. This is a restrictive policy.
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net",
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
            "font-src 'self' https://fonts.gstatic.com",
            "img-src 'self' data: https:",
            "connect-src 'self' https://api.openai.com https://api.elevenlabs.io wss:",
            "media-src 'self' https:",
            "object-src 'none'",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'",
            "upgrade-insecure-requests"
        ]
        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)
        
        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions Policy (formerly Feature Policy)
        permissions = [
            "camera=self",
            "microphone=self",
            "geolocation=self",
            "payment=none",
            "usb=none",
            "magnetometer=none",
            "gyroscope=none",
            "accelerometer=none"
        ]
        response.headers["Permissions-Policy"] = ", ".join(permissions)
        
        return response


def add_security_headers(app):
    """Helper function to add security headers middleware to the app."""
    app.add_middleware(SecurityHeadersMiddleware)