import time
import logging
from typing import Callable
from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.core.config import settings
from app.core.redis import RedisManager, redis_manager
from app.core.security import verify_token
from app.core.exceptions import AuthenticationError
from app.models.user import User
from app.core.database import async_session
from app.core.config import settings
from sqlalchemy import select

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
ADMIN_PATH = settings.admin_path
# 顶部添加：
PUBLIC_PATHS = {
    "/", "/health", "/docs", "/redoc", "/openapi.json", "/favicon.ico",
    "/set-flash","/show","/admin/somepage",
    "/api/v1/auth/login", "/api/v1/auth/register", "/api/v1/auth/config",
    "/api/v1/auth/refresh", "/api/v1/auth/forgot-password", "/api/v1/auth/reset-password",
    "/api/v1/auth/send-verification-code", "/api/v1/notifications", "/api/v1/tags/popular"
}

PREFIX_PATHS = [
    "/uploads/", "/wss/ws", "/static", "/statics",
    "/api/v1/search/", "/api/v1/oauth/", "/api/v1/config/", "/api/v1/donation/","/api/v1/admin/",
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
        if await redis_manager.is_token_blacklisted(token):
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

class CSPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)

        if request.url.path.startswith(ADMIN_PATH):
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "style-src 'self'; "
                # "script-src 'self' ; "
                "script-src 'self' 'unsafe-inline'; "
                "img-src 'self' blob:; "
                "font-src 'self'; "
                "connect-src 'self'; "
                "form-action 'self' http://localhost http://127.0.0.1; "
                "frame-ancestors 'none'; "
                "object-src 'none'; "
                "base-uri 'self'; "
                "media-src 'none'; "
                "frame-src 'none'; "

            )

        return response

class NoCacheAdminMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        # 允许登录页面被缓存，其他管理后台页面不缓存
        if request.url.path.startswith(ADMIN_PATH) and not request.url.path.endswith('/login'):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
            
            # 如果是HTML响应，添加JavaScript错误处理
            if "text/html" in response.headers.get("content-type", ""):
                if hasattr(response, 'body'):
                    try:
                        content = response.body.decode('utf-8')
                        # 简化的JavaScript错误处理
                        error_handler = """
                        <script>
                        // 立即阻止所有null元素错误
                        (function() {
                            // 重写console.error来隐藏错误
                            var originalError = console.error;
                            console.error = function() {
                                var args = Array.prototype.slice.call(arguments);
                                var message = args.join(' ');
                                if (message.includes('Cannot read properties of null')) {
                                    console.warn('Suppressed null element error:', message);
                                    return;
                                }
                                return originalError.apply(console, args);
                            };
                            
                            // 全局错误处理
                            window.addEventListener('error', function(e) {
                                if (e.message && e.message.includes('Cannot read properties of null')) {
                                    console.warn('Blocked null element error:', e.message);
                                    e.preventDefault();
                                    e.stopPropagation();
                                    return false;
                                }
                            });
                            
                            // 处理Bootstrap特定的错误
                            if (typeof $ !== 'undefined') {
                                $(document).ready(function() {
                                    // 延迟处理，确保DOM完全加载
                                    setTimeout(function() {
                                        // 安全地处理所有表单元素
                                        $(document).on('change click', 'input, select, textarea', function(e) {
                                            if (!this) {
                                                console.warn('Preventing event on null element');
                                                e.preventDefault();
                                                e.stopPropagation();
                                                return false;
                                            }
                                        });
                                    }, 100);
                                });
                            }
                        })();
                        </script>
                        """
                        content = content.replace('</head>', error_handler + '</head>')
                        response.body = content.encode('utf-8')
                    except Exception as e:
                        print(f"Error processing response: {e}")
        return response


class HTTPSURLMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        url = request.url
        if (
            url.scheme == "http"
            and request.headers.get("x-forwarded-proto") == "https"
            and url.path.startswith(ADMIN_PATH)
        ):
            request.state.url = url.replace(scheme="https")
            request.state.base_url = request.state.url.replace(path="/")
        else:
            request.state.url = url
            request.state.base_url = request.base_url

        response = await call_next(request)
        return response

# 打印请求协议的调试中间件
class PrintSchemeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        print(f"[DEBUG] {request.url.path} scheme: {request.url.scheme}, x-forwarded-proto: {request.headers.get('x-forwarded-proto')}")
        return await call_next(request)

# app.add_middleware(PrintSchemeMiddleware)
class FlashMessageMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if "text/html" in response.headers.get("content-type", ""):
            # 只在 HTML 页面请求时才读取 & 清除 flash
            messages = request.session.pop("flash_messages", None)
            request.state.flash_messages = messages
        return response

class SecurityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, redis_manager: RedisManager, ip_whitelist=None, ip_blacklist=None, rate_limit: int = 100, rate_window: int = 60):
        """
        :param redis_manager: Redis 管理实例
        :param ip_whitelist: 允许的 IP 列表（可选）
        :param ip_blacklist: 禁止的 IP 列表（可选）
        :param rate_limit: 窗口内允许的最大请求数
        :param rate_window: 窗口大小（秒）
        """
        super().__init__(app)
        self.redis_manager = redis_manager
        self.ip_whitelist = set(ip_whitelist or [])
        self.ip_blacklist = set(ip_blacklist or [])
        self.rate_limit = rate_limit
        self.rate_window = rate_window
        self.route_limits = {
            "/admin/login": (5, 60),            # 登录接口，每分钟5次
            "/send-verification-code": (10, 60),  # 注册/验证码接口
            "/api/": (250, 60),                 # 普通 API 接口
            "/": (300, 60),                      # 首页/静态资源
        }

    async def dispatch(self, request: Request, call_next):
        # ========== 获取客户端 IP ==========
        client_ip: str = "unknown"

        if request.client and request.client.host:
            client_ip = request.client.host
        else:
            # 安全地获取 X-Forwarded-For
            x_forwarded_for = request.headers.get("x-forwarded-for", "")
            if x_forwarded_for:
                client_ip = x_forwarded_for.split(",")[0].strip()

        # 查找匹配的限流策略
        path = request.url.path
        limit, window = self.rate_limit, self.rate_window
        for prefix, (l, w) in self.route_limits.items():
            if path.startswith(prefix):
                limit, window = l, w
                break
        # 1. IP 黑白名单检查
        if self.ip_whitelist and client_ip not in self.ip_whitelist:
            return JSONResponse({"detail": "Your IP is not allowed"}, status_code=403)

        if client_ip in self.ip_blacklist:
            return JSONResponse({"detail": "Your IP is blacklisted"}, status_code=403)

        if await self.redis_manager.exists_blacklist("ip", client_ip):
            return JSONResponse({"detail": "Your IP is in blacklist"}, status_code=403)

        # 2. Token 黑名单检查
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            if await self.redis_manager.is_token_blacklisted(token):
                return JSONResponse({"detail": "Token is blacklisted"}, status_code=401)

        # 3. 设备限制
        device_id = request.headers.get("X-Device-ID")
        if device_id and await self.redis_manager.exists_blacklist("device", device_id):
            return JSONResponse({"detail": "This device is blocked"}, status_code=403)

        # 4. 请求速率限制 (Rate Limit)
        rate_key = f"rate:{client_ip}"
        if self.redis_manager.redis is None:
            raise RuntimeError("Redis not connected")
        current = await self.redis_manager.redis.incr(rate_key)

        if current == 1:
            # 第一次请求，设置过期时间
            await self.redis_manager.redis.expire(rate_key, window)

        if current > limit:
            return JSONResponse(
                {"detail": f"Too many requests, limit {limit}/{window}s"},
                status_code=429,
            )

        # 5. 通过检查，继续处理请求
        response = await call_next(request)
        return response

# class FlashMessageMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request: Request, call_next):
#         # 先从session弹出消息，赋值给request.state
#         flash_messages = request.session.pop("flash_messages", None)
#         if flash_messages is None:
#             flash_messages = []
#         request.state.flash_messages = flash_messages
#         response = await call_next(request)
#         return response
    
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
    app.add_middleware(
        SecurityMiddleware,
        redis_manager=redis_manager,
        ip_whitelist=[],       # 可选，限制访问 IP
        ip_blacklist=[],       # 可选，黑名单
        rate_limit=250,         # 每窗口最多 50 个请求
        rate_window=60,        # 窗口 60 秒
    )

    # Custom middleware
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(AuthMiddleware)
    # app.add_middleware(FlashMessageMiddleware)
    app.add_middleware(CSPMiddleware)
    app.add_middleware(NoCacheAdminMiddleware)
    app.add_middleware(HTTPSURLMiddleware)
