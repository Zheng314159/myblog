import time
import logging
from typing import Callable
from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.core.config import settings
from app.core.redis import redis_manager
from app.core.security import verify_token
from app.core.exceptions import AuthenticationError
from app.models.user import User
from app.core.database import async_session
from sqlalchemy import select

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
ADMIN_PATH = "/admin"

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
        # 静态资源放行：uploads 目录
        if request.url.path.startswith("/uploads/"):
            logger.info(f"Uploads static resource path, skipping auth: {request.url.path}")
            return await call_next(request)
        
        # WebSocket路径白名单，直接放行
        if request.url.path.startswith("/api/v1/ws"):
            logger.info(f"WebSocket path, skipping auth: {request.url.path}")
            return await call_next(request)
        
        # 静态资源放行：图片和视频和多媒体列表
        if request.url.path.startswith("/api/v1/articles/images/") or \
           request.url.path.startswith("/api/v1/articles/videos/") or \
           request.url.path.startswith("/api/v1/articles/pdfs/") or \
           request.url.path == "/api/v1/articles/media/list":
            logger.info(f"Static/media resource path, skipping auth: {request.url.path}")
            return await call_next(request)
        
        # 强制放行所有 /admin 相关请求
        if request.url.path.startswith(ADMIN_PATH):
            logger.info(f"Public path (admin), skipping auth: {request.url.path}")
            return await call_next(request)
        
        # 允许无需认证的公开路径
        public_paths = [
            "/", "/health", "/docs", "/redoc", "/openapi.json", "/favicon.ico",
            "/api/v1/auth/login", "/api/v1/auth/register", "/api/v1/auth/config",
            "/api/v1/auth/refresh", "/api/v1/auth/forgot-password", "/api/v1/auth/reset-password", "/api/v1/auth/send-verification-code",
            "/api/v1/articles", "/api/v1/articles/",  # 允许匿名访问文章列表
            "/api/v1/tags/popular",  # 允许匿名访问热门标签
            "/api/v1/config", "/api/v1/config/",  # 允许匿名访问配置
            "/api/v1/config/statistics",  # 允许匿名访问统计数据
            "/api/v1/notifications",  # 允许匿名访问系统通知（修正路径）
            "/api/v1/donation/config",  # 允许匿名访问捐赠配置
            "/api/v1/donation/public-stats",  # 允许匿名访问公开统计
            "/api/v1/donation/goals",  # 允许匿名访问捐赠目标
            "/api/v1/donation/create",  # 允许匿名访问捐赠创建接口
            "/admin", "/admin/",  # 放行admin后台
            "/jianai", "/jianai/",  # 放行自定义后台路径
            ADMIN_PATH, ADMIN_PATH + "/",
            "/donation/result",  # 允许匿名访问捐赠结果页
        ]
        # 新增：统一去除末尾斜杠进行判断
        normalized_path = request.url.path.rstrip('/') or '/'
        normalized_public_paths = [p.rstrip('/') or '/' for p in public_paths]
        is_public = (
            normalized_path in normalized_public_paths or
            request.url.path.startswith("/admin") or
            request.url.path.startswith("/jianai") or
            request.url.path.startswith(ADMIN_PATH) or
            request.url.path.startswith("/static") or 
            request.url.path.startswith("/statics") or
            request.url.path.startswith("/docs") or 
            request.url.path.startswith("/redoc") or 
            request.url.path.startswith("/api/v1/search/") or
            request.url.path.startswith("/api/v1/oauth/") or
            request.url.path.startswith("/api/v1/config/") or  # 允许配置相关端点
            request.url.path.startswith("/api/v1/donation/") or  # 允许捐赠相关端点
            (
                request.url.path in ["/api/v1/articles", "/api/v1/articles/"] and request.method == "GET"
            ) or
            (
                request.url.path.startswith("/api/v1/tags") and request.method == "GET"
            )
            # 允许匿名访问 /api/v1/articles/{id} 详情页
            or (
                request.url.path.startswith("/api/v1/articles/")
                and request.method == "GET"
                and len(request.url.path.split("/")) == 5
            )
            # 允许匿名访问 /api/v1/articles/{id}/comments 评论列表
            or (
                request.url.path.startswith("/api/v1/articles/")
                and request.url.path.endswith("/comments")
                and request.method == "GET"
                and len(request.url.path.split("/")) == 6
            )
        )
        logger.info(f"Auth check for path: {request.url.path}, normalized: {normalized_path}, is_public: {is_public}")
        logger.info(f"Normalized public paths: {normalized_public_paths}")
        logger.info(f"Path in normalized_public_paths: {normalized_path in normalized_public_paths}")
        
        if is_public:
            logger.info(f"Public path, skipping auth: {request.url.path}")
            return await call_next(request)
        
        # Debug: 打印所有请求头
        logger.info(f"All request headers: {dict(request.headers)}")
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
        async with async_session() as db:
            result = await db.execute(select(User).where(User.username == payload.get("sub")))
            user = result.scalar_one_or_none()
            if not user:
                logger.error(f"User not found for token subject: {payload.get('sub')}")
                raise AuthenticationError("User not found")
            request.state.user = user
            logger.info(f"User authenticated: {user.username} for path: {request.url.path}")
        
        return await call_next(request)


def setup_middleware(app):
    """Setup all middleware"""
    print("[DEBUG] Allowed origins:", settings.allowed_origins)
    
    # Session middleware - 必须最先添加，OAuth功能需要
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.secret_key,  # 使用配置中的secret_key
        max_age=60 * 60 * 24 * 7,  # 7 days
        same_site="lax",
        https_only=False  # 开发环境设为False，生产环境应该设为True
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
    
    # Custom middleware
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(AuthMiddleware) 