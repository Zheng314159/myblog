# 在所有导入前加载dotenv
from dotenv import load_dotenv
load_dotenv()

# 设置代理环境变量（如果.env中有配置）
import os
if os.getenv('HTTP_PROXY'):
    os.environ['HTTP_PROXY'] = os.getenv('HTTP_PROXY')
if os.getenv('HTTPS_PROXY'):
    os.environ['HTTPS_PROXY'] = os.getenv('HTTPS_PROXY')
if os.getenv('NO_PROXY'):
    os.environ['NO_PROXY'] = os.getenv('NO_PROXY')

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlmodel import SQLModel
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

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
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.responses import RedirectResponse
from sqlalchemy import select, delete
from app.models.user import User
from app.models.article import Article
from app.models.tag import Tag, ArticleTag
from app.models.comment import Comment
from app.core.security import verify_password
from app.models.user import UserRole

ADMIN_PATH = "/jianai"  # 可自定义后台路径


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("Starting up...")
    
    # Connect to Redis
    await redis_manager.connect()
    print("Connected to Redis")
    
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
        authentication_backend=AdminAuth(secret_key="your-random-secret-key"), 
        base_url=ADMIN_PATH,
        title="博客管理系统",
        logo_url="https://preview.tabler.io/static/logo-white.svg"
    )

    class UserAdmin(ModelView, model=User):
        column_list = ["id", "username", "email", "role", "is_active", "created_at"]
        form_excluded_columns = ["hashed_password"]
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
            """自定义删除方法，防止删除管理员用户"""
            async with async_session() as session:
                try:
                    # 检查是否要删除管理员用户
                    for pk in pks:
                        result = await session.execute(select(User).where(User.id == pk))
                        user = result.scalar_one_or_none()
                        if user and user.role == "admin":
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
        column_list = ["id", "title", "author_id", "status", "created_at"]
        can_create = True
        can_edit = True
        can_delete = True
        can_view_details = True
        name = "文章管理"
        name_plural = "文章"
        form_include_pk = False
        form_excluded_columns = ["created_at", "updated_at", "published_at"]
        
        async def delete_model(self, request: Request, pks: list) -> bool:
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
        can_create = True
        can_edit = True
        can_delete = True
        can_view_details = True
        name = "标签管理"
        name_plural = "标签"
        form_include_pk = False
        form_excluded_columns = ["created_at"]

    class CommentAdmin(ModelView, model=Comment):
        column_list = ["id", "article_id", "author_id", "content", "created_at", "is_approved"]
        can_create = True
        can_edit = True
        can_delete = True
        can_view_details = True
        name = "评论管理"
        name_plural = "评论"
        form_include_pk = False
        form_excluded_columns = ["created_at", "updated_at"]
        
        async def delete_model(self, request: Request, pks: list) -> bool:
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

    admin.add_view(UserAdmin)
    admin.add_view(ArticleAdmin)
    admin.add_view(TagAdmin)
    admin.add_view(CommentAdmin)
    
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
app.include_router(websocket_router, prefix="/api/v1")
app.include_router(search_router, prefix="/api/v1")
app.include_router(scheduler_router, prefix="/api/v1")
app.include_router(oauth_router, prefix="/api/v1")
app.include_router(config_router, prefix="/api/v1")


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