import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlmodel import SQLModel

from app.core.config import settings
from app.core.database import engine, create_db_and_tables
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
setup_middleware(app)


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=settings.debug,
        log_level="info"
    ) 