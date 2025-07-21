from fastapi import APIRouter, HTTPException, Depends, Query
from app.core.config import settings, reload_settings
from typing import Dict, Any, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db, async_session
from app.models.article import Article, ArticleStatus
from app.models.user import User
from app.models.media import MediaFile, MediaType
from sqlmodel import SQLModel
from fastapi.responses import JSONResponse
from app.models.system_notification import SystemNotification
from sqlalchemy.future import select

router = APIRouter(prefix="/config", tags=["config"])

@router.get("/")
async def get_config() -> Dict[str, Any]:
    """
    获取所有配置信息（敏感信息会被隐藏）
    """
    # 重新加载配置以确保获取最新状态
    reload_settings()
    
    return {
        # 应用设置
        "app_name": settings.app_name,
        "debug": settings.debug,
        "frontend_url": settings.frontend_url,
        
        # 数据库设置
        "database_url": "***hidden***" if settings.database_url else None,
        
        # JWT设置
        "algorithm": settings.algorithm,
        "access_token_expire_minutes": settings.access_token_expire_minutes,
        "refresh_token_expire_days": settings.refresh_token_expire_days,
        
        # Redis设置
        "redis_url": "***hidden***" if settings.redis_url else None,
        
        # 邮箱设置
        "smtp_server": settings.smtp_server,
        "smtp_port": settings.smtp_port,
        "email_user": "***hidden***" if settings.email_user else None,
        "email_from": settings.email_from,
        "email_enabled": settings.email_enabled,
        
        # CORS设置
        "allowed_origins": settings.allowed_origins,
        
        # 调度器设置
        "timezone": settings.timezone,
        
        # OAuth设置
        "github_client_id": "***hidden***" if settings.github_client_id else None,
        "github_client_secret": "***hidden***" if settings.github_client_secret else None,
        "google_client_id": "***hidden***" if settings.google_client_id else None,
        "google_client_secret": "***hidden***" if settings.google_client_secret else None,
        "oauth_base_url": settings.oauth_base_url,
        
        # 代理设置
        "http_proxy": "***hidden***" if settings.http_proxy else None,
        "https_proxy": "***hidden***" if settings.https_proxy else None,
        "no_proxy": settings.no_proxy,
        
        # 功能状态
        "oauth_enabled": bool(settings.github_client_id or settings.google_client_id),
        "github_oauth_enabled": bool(settings.github_client_id and settings.github_client_secret),
        "google_oauth_enabled": bool(settings.google_client_id and settings.google_client_secret),
        "enable_notification_fetch": settings.enable_notification_fetch,
        "enable_notification_push": settings.enable_notification_push,
    }

@router.get("/auth")
async def get_auth_config() -> Dict[str, Any]:
    """
    获取认证相关配置信息（兼容旧版本）
    """
    # 重新加载配置以确保获取最新状态
    reload_settings()
    
    return {
        "email_enabled": settings.email_enabled,
        "oauth_enabled": bool(settings.github_client_id or settings.google_client_id),
        "github_oauth_enabled": bool(settings.github_client_id and settings.github_client_secret),
        "google_oauth_enabled": bool(settings.google_client_id and settings.google_client_secret),
    }

@router.get("/oauth")
async def get_oauth_config() -> Dict[str, Any]:
    """
    获取OAuth相关配置信息
    """
    # 重新加载配置以确保获取最新状态
    reload_settings()
    
    return {
        "github_enabled": bool(settings.github_client_id and settings.github_client_secret),
        "google_enabled": bool(settings.google_client_id and settings.google_client_secret),
        "oauth_base_url": settings.oauth_base_url,
        "frontend_url": settings.frontend_url,
    }

@router.post("/reload")
async def reload_config() -> Dict[str, str]:
    """
    手动重新加载配置
    """
    try:
        reload_settings()
        return {"message": "Configuration reloaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reload configuration: {str(e)}")

@router.get("/health")
async def config_health() -> Dict[str, Any]:
    """
    配置健康检查
    """
    # 重新加载配置以确保获取最新状态
    reload_settings()
    
    return {
        "status": "healthy",
        "config_loaded": True,
        "email_enabled": settings.email_enabled,
        "oauth_enabled": bool(settings.github_client_id or settings.google_client_id),
        "database_configured": bool(settings.database_url),
        "redis_configured": bool(settings.redis_url),
    }

@router.get("/statistics")
async def get_statistics(
    db: AsyncSession = Depends(get_db)
):
    """获取系统统计数据"""
    try:
        # 获取文章总数
        result = await db.execute(select(func.count(Article.id)))
        total_articles = result.scalar() or 0
        
        # 获取已发布文章数
        result = await db.execute(
            select(func.count(Article.id)).where(Article.status == "published")
        )
        published_articles = result.scalar() or 0
        
        # 获取用户总数
        result = await db.execute(select(func.count(User.id)))
        total_users = result.scalar() or 0
        
        # 获取活跃用户数（有发布文章的用户）
        result = await db.execute(
            select(func.count(func.distinct(User.id)))
            .select_from(User)
            .join(Article, User.id == Article.author_id)
            .where(Article.status == "published")
        )
        active_users = result.scalar() or 0
        
        # 获取媒体文件总数
        result = await db.execute(select(func.count(MediaFile.id)))
        total_media = result.scalar() or 0
        
        # 按类型统计媒体文件
        result = await db.execute(
            select(MediaFile.type, func.count(MediaFile.id)).group_by(MediaFile.type)
        )
        media_by_type = {str(row[0]): row[1] for row in result.all()}
        
        # 真实总浏览量：所有已发布文章的view_count之和
        result = await db.execute(
            select(func.sum(Article.view_count)).where(Article.status == "published")
        )
        total_views = result.scalar() or 0
        
        return {
            "total_articles": total_articles,
            "published_articles": published_articles,
            "total_users": total_users,
            "active_users": active_users,
            "total_media": total_media,
            "media_by_type": media_by_type,
            "total_views": total_views
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计数据失败: {str(e)}")

@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "message": "系统运行正常"}

@router.get("/tables", summary="获取所有数据库表名")
def get_all_tables():
    table_names = list(SQLModel.metadata.tables.keys())
    return JSONResponse(content={"tables": table_names})

@router.get("/notifications")
async def get_notifications(limit: int = Query(5, ge=1, le=20)):
    async with async_session() as session:
        result = await session.execute(
            select(SystemNotification)
            .where(SystemNotification.is_sent.is_(True))
            .order_by(SystemNotification.id.desc())
            .limit(limit)
        )
        notifications = result.scalars().all()
        return {"notifications": [n.dict() for n in notifications]} 