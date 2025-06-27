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
            "/api/v1/auth/login", "/api/v1/auth/register",
            "/api/v1/articles", "/api/v1/articles/",  # 允许匿名访问文章列表
            "/api/v1/tags/popular",  # 允许匿名访问热门标签
        ]
        
        # 检查是否是公开路径
        is_public = (
            request.url.path in public_paths or 
            request.url.path.startswith("/static") or 
            request.url.path.startswith("/docs") or 
            request.url.path.startswith("/redoc") or 
            request.url.path.startswith("/api/v1/search/") or
            request.url.path.startswith("/api/v1/oauth/") or
            request.url.path.startswith("/api/v1/articles/") or  # 允许所有文章相关接口匿名访问
            request.url.path.startswith("/api/v1/tags/")  # 允许所有标签相关接口匿名访问
        )
        
        logger.info(f"Auth check for path: {request.url.path}, is_public: {is_public}")
        
        if is_public:
            logger.info(f"Public path, skipping auth: {request.url.path}")
            return await call_next(request)
        
        # 对于需要认证的路径，检查Authorization头
        auth_header = request.headers.get("Authorization")
        logger.info(f"Auth header: {auth_header}")
        
        if not auth_header or not auth_header.startswith("Bearer "):
            logger.error(f"Missing or invalid authorization header for path: {request.url.path}")
            raise AuthenticationError("Missing or invalid authorization header")
        
        token = auth_header.split(" ")[1]
        logger.info(f"Token extracted: {token[:20]}...")
        
        # Check if token is blacklisted
        is_blacklisted = await redis_manager.exists(f"blacklist:{token}")
        if is_blacklisted:
            logger.error(f"Token is blacklisted for path: {request.url.path}")
            raise AuthenticationError("Token has been revoked")
        
        # Verify token
        payload = verify_token(token)
        logger.info(f"Token verification result: {payload}")
        
        if not payload or payload.get("type") != "access":
            logger.error(f"Invalid or expired token for path: {request.url.path}")
            raise AuthenticationError("Invalid or expired token")
        
        # Add user info to request state
        request.state.user = payload
        logger.info(f"User authenticated: {payload.get('sub')} for path: {request.url.path}")
        
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