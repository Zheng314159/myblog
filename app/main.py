# 在所有导入前加载dotenv
import traceback
from dotenv import load_dotenv
load_dotenv()

# 设置代理环境变量（如果.env中有配置）
import os
if os.getenv('HTTP_PROXY') is not None:
    os.environ['HTTP_PROXY'] = str(os.getenv('HTTP_PROXY'))
if os.getenv('HTTPS_PROXY') is not None:
    os.environ['HTTPS_PROXY'] = str(os.getenv('HTTPS_PROXY'))
if os.getenv('NO_PROXY') is not None:
    os.environ['NO_PROXY'] = str(os.getenv('NO_PROXY'))

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlmodel import SQLModel
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import engine, create_db_and_tables, async_session
from app.core.redis import redis_manager
from app.core.middleware import setup_middleware
from app.core.exceptions import BlogException
from app.core.scheduler import start_scheduler, stop_scheduler
from app.core.oauth import oauth
from app.api.v1.auth import router as auth_router
from app.api.v1.article import router as article_router
from app.api.v1.tag import router as tag_router
from app.api.v1.websocket import router as websocket_router
from app.api.v1.search import router as search_router
from app.api.v1.scheduler import router as scheduler_router
from app.api.v1.oauth import router as oauth_router
from app.api.v1.config import router as config_router
from app.api.v1.donation import router as donation_router
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.responses import RedirectResponse
from sqlalchemy import select, delete
from app.models.user import User, OAuthAccount
from app.models.article import Article
from app.models.tag import Tag, ArticleTag
from app.models.comment import Comment
from app.core.security import verify_password
from app.models.user import UserRole
from app.models.media import MediaFile
from app.models.system_notification import SystemNotification
from app.models.donation import DonationConfig, DonationRecord, DonationGoal
import sqladmin
ADMIN_PATH = "/admin"  # 后台路径恢复为/admin，保证SQLAdmin静态资源和JS事件正常


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("Starting up...")
    
    # Connect to Redis
    await redis_manager.connect()
    print("Connected to Redis")
    # 简单的健康检查
    try:
        pong = await redis_manager.redis.ping()
        print(f"Redis ping response: {pong}")  # 应该打印 True
    except Exception as e:
        print(f"Redis health check failed: {e}")
    # Create database tables
    await create_db_and_tables()
    print("Database tables created")
    
    # Initialize OAuth
    # oauth.init_app(app)  # Temporarily disabled due to linter issues
    print("OAuth initialization skipped")
    
    # Start scheduler
    await start_scheduler()
    print("Scheduler started")
    
    # Create management backend
    admin = Admin(
        app, 
        engine, 
        authentication_backend=AdminAuth(secret_key=settings.secret_key), 
        base_url=ADMIN_PATH,
        title="博客管理系统",
        logo_url="https://preview.tabler.io/static/logo-white.svg"
    )

    class UserAdmin(ModelView, model=User):
        column_list = ["id", "username", "email", "role", "is_active", "created_at"]
        form_columns = ["username", "email", "full_name", "role", "is_active", "oauth_provider", "oauth_id", "oauth_username", "avatar_url"]
        can_create = True
        can_edit = True
        can_delete = True
        can_view_details = True
        name = "用户管理"
        name_plural = "用户"
        form_include_pk = False
        form_widget_args = {
            "hashed_password": {"readonly": True}
        }
        
        async def delete_model(self, request: Request, pks: list) -> bool:
            print(f"delete_model called: {pks}")
            """自定义删除方法，防止删除管理员用户"""
            async with async_session() as session:
                try:
                    # 检查是否要删除管理员用户
                    for pk in pks:
                        result = await session.execute(select(User).where(User.id == pk))
                        user = result.scalar_one_or_none()
                        if user and user.role == "ADMIN":
                            print(f"不能删除管理员用户: {user.username}")
                            return False
                    
                    for pk in pks:
                        # 删除用户相关的评论
                        await session.execute(delete(Comment).where(Comment.author_id == pk))
                        
                        # 删除用户的所有文章（包括文章标签关联）
                        article_result = await session.execute(select(Article).where(Article.author_id == pk))
                        user_articles = article_result.scalars().all()
                        
                        for article in user_articles:
                            # 删除文章相关的评论
                            await session.execute(delete(Comment).where(Comment.article_id == article.id))
                            # 删除文章标签关联
                            await session.execute(delete(ArticleTag).where(ArticleTag.article_id == article.id))
                        
                        # 删除用户的所有文章
                        await session.execute(delete(Article).where(Article.author_id == pk))
                    
                    # 删除用户
                    for pk in pks:
                        await session.execute(delete(User).where(User.id == pk))
                    
                    await session.commit()
                    return True
                except Exception as e:
                    await session.rollback()
                    print(f"删除用户失败: {e}")
                    return False

    class ArticleAdmin(ModelView, model=Article):
        column_list = ["id", "title", "author_id", "status", "view_count", "created_at"]
        form_columns = ["title", "content", "summary", "status", "author_id", "is_featured", "has_latex", "latex_content", "view_count"]
        can_create = True
        can_edit = True
        can_delete = True
        can_view_details = True
        name = "文章管理"
        name_plural = "文章"
        form_include_pk = False
        
        async def delete_model(self, request: Request, pks: list) -> bool:
            print(f"delete_model called: {pks}")
            """自定义删除方法，允许管理员删除所有文章"""
            async with async_session() as session:
                try:
                    for pk in pks:
                        # 删除文章相关的评论（包括子评论）
                        await session.execute(delete(Comment).where(Comment.article_id == pk))
                        
                        # 删除文章标签关联
                        await session.execute(delete(ArticleTag).where(ArticleTag.article_id == pk))
                    
                    # 删除文章
                    for pk in pks:
                        await session.execute(delete(Article).where(Article.id == pk))
                    
                    await session.commit()
                    return True
                except Exception as e:
                    await session.rollback()
                    print(f"删除文章失败: {e}")
                    return False

    class TagAdmin(ModelView, model=Tag):
        column_list = ["id", "name", "description", "created_at"]
        form_columns = ["name", "description"]
        can_create = True
        can_edit = True
        can_delete = True
        can_view_details = True
        name = "标签管理"
        name_plural = "标签"
        form_include_pk = False

    class ArticleTagAdmin(ModelView, model=ArticleTag):
        column_list = ["id", "article_id", "tag_id"]
        can_create = True
        can_edit = True
        can_delete = True
        can_view_details = True
        name = "文章标签关联"
        name_plural = "文章标签关联"
        form_include_pk = False
        form_excluded_columns = []

    class CommentAdmin(ModelView, model=Comment):
        column_list = ["id", "article_id", "author_id", "content", "created_at", "is_approved"]
        form_columns = ["article_id", "author_id", "content", "parent_id", "is_approved"]
        can_create = True
        can_edit = True
        can_delete = True
        can_view_details = True
        name = "评论管理"
        name_plural = "评论"
        form_include_pk = False
        
        async def delete_model(self, request: Request, pks: list) -> bool:
            print(f"delete_model called: {pks}")
            """自定义删除方法，删除评论时也删除子评论"""
            async with async_session() as session:
                try:
                    for pk in pks:
                        # 删除子评论
                        await session.execute(delete(Comment).where(Comment.parent_id == pk))
                        
                        # 删除评论本身
                        await session.execute(delete(Comment).where(Comment.id == pk))
                    
                    await session.commit()
                    return True
                except Exception as e:
                    await session.rollback()
                    print(f"删除评论失败: {e}")
                    return False

    class MediaFileAdmin(ModelView, model=MediaFile):
        column_list = ["id", "filename", "type", "url", "size", "upload_time", "description", "uploader_id", "uploader"]
        column_formatters = {
            "uploader": lambda m, p: m.uploader.username if m.uploader else ""
        }
        can_create = True
        can_edit = True
        can_delete = True
        can_view_details = True
        name = "多媒体文件"
        name_plural = "多媒体文件"

    class OAuthAccountAdmin(ModelView, model=OAuthAccount):
        column_list = ["id", "user_id", "provider", "provider_user_id", "provider_username", "created_at", "updated_at"]
        form_columns = ["user_id", "provider", "provider_user_id", "provider_username", "provider_email", "provider_avatar_url"]
        can_create = True
        can_edit = True
        can_delete = True
        can_view_details = True
        name = "OAuth账号绑定"
        name_plural = "OAuth账号绑定"
        form_include_pk = False

    class SystemNotificationAdmin(ModelView, model=SystemNotification):
        column_list = ["id", "title", "message", "notification_type", "created_at", "is_sent", "admin_id"]
        form_columns = ["title", "message", "notification_type", "is_sent", "admin_id"]
        can_create = True
        can_edit = True
        can_delete = True
        can_view_details = True
        name = "系统通知"
        name_plural = "系统通知"
        form_include_pk = False

        async def is_accessible(self, request):
            # 只有管理员能访问
            user_id = request.session.get("user_id")
            if not user_id:
                return False
            async with async_session() as session:
                user = await session.get(User, user_id)
                return user and user.role == UserRole.ADMIN

        async def insert_model(self, request, data):
            # 自动填充 admin_id 字段
            user_id = request.session.get("user_id")
            if user_id:
                data["admin_id"] = user_id
            return await super().insert_model(request, data)

    class DonationConfigAdmin(ModelView, model=DonationConfig):
        column_list = [
            "id", "is_enabled", "title", "description", "alipay_enabled", "wechat_enabled", "paypal_enabled", "preset_amounts", "created_at", "updated_at"
        ]
        form_columns = [
            "is_enabled", "title", "description", "alipay_enabled", "wechat_enabled", "paypal_enabled", "preset_amounts"
        ]
        can_create = True
        can_edit = True
        can_delete = True
        can_view_details = True
        name = "捐赠配置"
        name_plural = "捐赠配置"
        form_include_pk = False

    class DonationRecordAdmin(ModelView, model=DonationRecord):
        column_list = [
            "id", "donor_name", "donor_email", "donor_message", "is_anonymous", "amount", "currency", "payment_method", "payment_status", "transaction_id", "user_id", "goal_id", "created_at", "updated_at", "paid_at"
        ]
        form_columns = [
            "donor_name", "donor_email", "donor_message", "is_anonymous", "amount", "currency", "payment_method", "payment_status", "transaction_id", "user_id", "goal_id", "paid_at"
        ]
        can_create = True
        can_edit = True
        can_delete = True
        can_view_details = True
        name = "捐赠记录"
        name_plural = "捐赠记录"
        form_include_pk = False

    class DonationGoalAdmin(ModelView, model=DonationGoal):
        column_list = ["id", "title", "description", "target_amount", "current_amount", "currency", "start_date", "end_date", "is_active", "is_completed", "created_at", "updated_at"]
        form_columns = ["title", "description", "target_amount", "current_amount", "currency", "start_date", "end_date", "is_active"]
        can_create = True
        can_edit = True
        can_delete = True
        can_view_details = True
        name = "捐赠目标"
        name_plural = "捐赠目标"
        form_include_pk = False

    admin.add_view(UserAdmin)
    admin.add_view(OAuthAccountAdmin)
    admin.add_view(ArticleAdmin)
    admin.add_view(TagAdmin)
    admin.add_view(ArticleTagAdmin)
    admin.add_view(CommentAdmin)
    admin.add_view(MediaFileAdmin)
    admin.add_view(SystemNotificationAdmin)
    admin.add_view(DonationConfigAdmin)
    admin.add_view(DonationRecordAdmin)
    admin.add_view(DonationGoalAdmin)
    
    yield
    
    # Shutdown
    print("Shutting down...")
    
    # Stop scheduler
    await stop_scheduler()
    print("Scheduler stopped")
    
    # Disconnect from Redis
    await redis_manager.disconnect()
    print("Disconnected from Redis")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="A complete FastAPI blog system with JWT authentication, articles, comments, and tags",
    version="1.0.0",
    debug=settings.debug,
    lifespan=lifespan
)

# 挂载 uploads 静态资源目录
import os
app.mount("/uploads", StaticFiles(directory=os.path.abspath("uploads")), name="uploads")

# 找到 sqladmin 的 static 路径
# sqladmin_static_dir = os.path.join(os.path.dirname(sqladmin.__file__), "static")

# 手动挂载 static，路径必须是 /admin/statics 才能匹配模板引用的资源路径
app.mount("/admin/statics", StaticFiles(directory="app/static/sqladmin"), name="sqladmin-static")

# Setup middleware
setup_middleware(app)  # 恢复中间件


# Exception handlers
@app.exception_handler(BlogException)
async def blog_exception_handler(request: Request, exc: BlogException):
    """Handle custom blog exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code
        },
        headers=exc.headers
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    return JSONResponse(
        status_code=422,
        content={
            "error": True,
            "message": "Validation error",
            "details": exc.errors(),
            "status_code": 422
        }
    )


@app.exception_handler(ValidationError)
async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
    """Handle Pydantic validation errors"""
    return JSONResponse(
        status_code=422,
        content={
            "error": True,
            "message": "Validation error",
            "details": exc.errors(),
            "status_code": 422
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    print("🔥 全局异常:", traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal server error",
            "status_code": 500
        }
    )



# Include routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(article_router, prefix="/api/v1")
app.include_router(tag_router, prefix="/api/v1")
app.include_router(websocket_router, prefix="/wss")
app.include_router(search_router, prefix="/api/v1")
app.include_router(scheduler_router, prefix="/api/v1")
app.include_router(oauth_router, prefix="/api/v1")
app.include_router(config_router, prefix="/api/v1")
app.include_router(donation_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to FastAPI Blog System",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Service is running"
    }


class AdminAuth(AuthenticationBackend):
    async def authenticate(self, request: Request):
        if request.session.get("user_id"):
            async with async_session() as session:
                user = await session.get(User, request.session["user_id"])
                if user and user.role == UserRole.ADMIN:
                    return True
        return False

    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = str(form.get("username") or "")
        password = str(form.get("password") or "")
        
        async with async_session() as session:
            result = await session.execute(select(User).where(User.username == username))
            user = result.scalar_one_or_none()
            
            if (
                user and user.role == UserRole.ADMIN and user.is_active
                and user.hashed_password
                and verify_password(password, user.hashed_password)
            ):
                request.session["user_id"] = user.id
                return True
        return False

    async def logout(self, request: Request) -> None:
        request.session.pop("user_id", None)

# class CSPMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request: Request, call_next):
#         response: Response = await call_next(request)

#         if request.url.path.startswith(ADMIN_PATH):
#             response.headers["Content-Security-Policy"] = (
#                 "default-src 'self' data: 'unsafe-inline' 'unsafe-eval'; "
#                 "style-src 'self' 'unsafe-inline' https: http:; "
#                 "script-src 'self' 'unsafe-inline' 'unsafe-eval' https: http:; "
#                 "img-src 'self' data: blob:; "
#                 "font-src 'self' data:;"
#             )

#         return response

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

# app.add_middleware(CSPMiddleware)
app.add_middleware(NoCacheAdminMiddleware)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=settings.debug,
        log_level="info"
    ) 