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

# Constants
ADMIN_PATH = "/admin"
# 顶部添加：
PUBLIC_PATHS = {
    "/", "/health", "/docs", "/redoc", "/openapi.json", "/favicon.ico",
    "/api/v1/auth/login", "/api/v1/auth/register", "/api/v1/auth/config",
    "/api/v1/auth/refresh", "/api/v1/auth/forgot-password", "/api/v1/auth/reset-password",
    "/api/v1/auth/send-verification-code", "/api/v1/notifications", "/api/v1/tags/popular"
}

PREFIX_PATHS = [
    "/uploads/", "/wss/ws", "/static", "/statics",
    "/api/v1/search/", "/api/v1/oauth/", "/api/v1/config/", "/api/v1/donation/",
    "/api/v1/articles/images/", "/api/v1/articles/videos/", "/api/v1/articles/pdfs/", "/api/v1/articles/media/list"
]


class LoggingMiddleware(BaseHTTPMiddleware):
    """Logging middleware for request/response"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        logger.info(f"→ Request: {request.method} {request.url.path}")

        response = await call_next(request)

        process_time = time.time() - start_time
        logger.info(f"← Response: {response.status_code} ({process_time:.3f}s)")
        return response


class AuthMiddleware(BaseHTTPMiddleware):
    """Authentication middleware"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        path = request.url.path
        method = request.method
        def is_public_path(request: Request) -> bool:
            normalized_path = path.rstrip("/") or "/"
            
            # 特殊 GET 请求白名单
            if method == "GET":
                if path in ["/api/v1/articles", "/api/v1/articles/"]:
                    return True
                if path.startswith("/api/v1/articles/") and len(path.split("/")) == 5:
                    return True
                if path.startswith("/api/v1/articles/") and path.endswith("/comments") and len(path.split("/")) == 6:
                    return True
                if path.startswith("/api/v1/tags"):
                    return True

            if normalized_path in PUBLIC_PATHS:
                return True
            if any(path.startswith(prefix) for prefix in PREFIX_PATHS):
                return True
            if path.startswith(ADMIN_PATH):
                return True
            
            return False


        if is_public_path(request):
            try:
                return await call_next(request)
            except Exception as e:
                logger.exception(f"🔥 Unhandled error at path {request.url.path}")
                raise e


        # ----- Authorization -----
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            logger.warning(f"⚠️ Unauthorized access attempt: {path}")
            raise AuthenticationError("Missing or invalid authorization header")

        token = auth_header.removeprefix("Bearer ").strip()
        logger.debug(f"Auth token: {token[:20]}...")

        if len(token) > 2048 or not token.isascii():
            raise AuthenticationError("Malformed token")

        # Check if token is blacklisted
        if await redis_manager.is_blacklisted(token):
            logger.error("🚫 Blacklisted token used.")
            raise AuthenticationError("Token has been revoked")

        # Verify token
        payload = verify_token(token)
        if not payload or payload.get("type") != "access":
            raise AuthenticationError("Invalid or expired token")

        # Attach user to request
        async with async_session() as db:
            result = await db.execute(select(User).where(User.username == payload.get("sub")))
            user = result.scalar_one_or_none()
            if not user:
                raise AuthenticationError("User not found")

            request.state.user = user
            logger.info(f"✅ Authenticated: {user.username}")

        return await call_next(request)


def setup_middleware(app):
    """Register all middleware on app"""
    logger.info("⚙️ Setting up middleware")

    # Session middleware (required for OAuth)
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.secret_key,
        max_age=60 * 60 * 24 * 7,  # 7 days
        same_site="lax",
        https_only=settings.https_only
    )

    # CORS
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
