"""Middleware implementations"""

import logging
import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from app.utils.auth import verify_token, extract_token_from_header
from app.utils.errors import UnauthorizedException, ForbiddenException
from app.config import get_config

logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add unique request ID to each request"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        
        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests and responses"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        logger.info(f"Request: {request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
        except Exception as exc:
            duration = time.time() - start_time
            logger.error(f"Request failed: {request.method} {request.url.path} - {exc}")
            raise
        
        duration = time.time() - start_time
        logger.info(f"Response: {request.method} {request.url.path} {response.status_code} ({duration:.2f}s)")
        
        return response


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Verify JWT token in requests"""
    
    EXCLUDED_PATHS = {
        "/",
        "/healthz",
        "/health",
        "/docs",
        "/openapi.json",
        "/redoc",
        "/favicon.ico",
        "/api/auth/login",
        "/api/auth/register",
        "/api/auth/oauth",
        "/api/v1/auth/token",
        "/api/v1/auth/user",
        "/api/v1/auth/login",
        "/api/v1/auth/register",
        "/api/v1/auth/oauth",
    }
    
    EXCLUDED_PREFIXES = (
        "/docs",
        "/static",
    )
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        path = request.url.path
        
        # Skip authentication for excluded paths
        if path in self.EXCLUDED_PATHS:
            return await call_next(request)
        
        # Skip authentication for excluded prefixes
        if path.startswith(self.EXCLUDED_PREFIXES):
            return await call_next(request)
        
        # Extract token from header
        auth_header = request.headers.get("Authorization")
        token = extract_token_from_header(auth_header)
        
        if not token:
            # Return JSON response instead of raising exception
            return Response(
                content='{"success": false, "message": "Missing or invalid authorization header"}',
                status_code=401,
                media_type="application/json"
            )
        
        # Verify token
        token_data = verify_token(token)
        if not token_data:
            return Response(
                content='{"success": false, "message": "Invalid or expired token"}',
                status_code=401,
                media_type="application/json"
            )
        
        # Store token data in request state
        request.state.user_id = token_data.user_id
        request.state.username = token_data.username
        
        return await call_next(request)


class CORSMiddlewareConfig:
    """CORS configuration"""
    
    @staticmethod
    def get_middleware(app):
        """Add CORS middleware to app"""
        config = get_config()
        
        return CORSMiddleware(
            app=app,
            allow_origins=["*"],  # Configure based on environment
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting middleware"""
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests = {}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Check rate limit (simplified - use Redis for production)
        current_time = time.time()
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        # Remove requests older than 1 minute
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if current_time - req_time < 60
        ]
        
        # Check if limit exceeded
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            return Response("Rate limit exceeded", status_code=429)
        
        # Add current request
        self.requests[client_ip].append(current_time)
        
        return await call_next(request)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Handle exceptions and return proper error responses"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except UnauthorizedException as e:
            logger.warning(f"Unauthorized: {e.message}")
            return Response(
                content=f'{{"success": false, "message": "{e.message}"}}',
                status_code=401,
                media_type="application/json"
            )
        except ForbiddenException as e:
            logger.warning(f"Forbidden: {e.message}")
            return Response(
                content=f'{{"success": false, "message": "{e.message}"}}',
                status_code=403,
                media_type="application/json"
            )
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return Response(
                content=f'{{"success": false, "message": "Internal server error", "error": "{str(e)}"}}',
                status_code=500,
                media_type="application/json"
            )
