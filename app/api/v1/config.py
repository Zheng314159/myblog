from fastapi import APIRouter, HTTPException
from app.core.config import settings, reload_settings
from typing import Dict, Any

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