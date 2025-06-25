import time
import logging
from typing import Callable
from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings
from app.core.redis import redis_manager
from app.core.security import verify_token
from app.core.exceptions import AuthenticationError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Logging middleware for request/response"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url}")
        
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        logger.info(f"Response: {response.status_code} - {process_time:.4f}s")
        
        return response


class AuthMiddleware(BaseHTTPMiddleware):
    """Authentication middleware"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 允许无需认证的公开路径
        public_paths = [
            "/", "/health", "/docs", "/redoc", "/openapi.json", "/favicon.ico",
            "/api/v1/auth/login", "/api/v1/auth/register"
        ]
        if request.url.path in public_paths or request.url.path.startswith("/static") or request.url.path.startswith("/docs") or request.url.path.startswith("/redoc") or request.url.path.startswith("/api/v1/auth/") or request.url.path.startswith("/api/v1/search/"):
            return await call_next(request)
        
        # Get token from header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise AuthenticationError("Missing or invalid authorization header")
        
        token = auth_header.split(" ")[1]
        
        # Check if token is blacklisted
        is_blacklisted = await redis_manager.exists(f"blacklist:{token}")
        if is_blacklisted:
            raise AuthenticationError("Token has been revoked")
        
        # Verify token
        payload = verify_token(token)
        if not payload or payload.get("type") != "access":
            raise AuthenticationError("Invalid or expired token")
        
        # Add user info to request state
        request.state.user = payload
        
        return await call_next(request)


def setup_middleware(app):
    """Setup all middleware"""
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Custom middleware
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(AuthMiddleware) 