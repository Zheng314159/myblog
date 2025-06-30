from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field
import os
from dotenv import load_dotenv


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite+aiosqlite:///./blog.db"
    
    # JWT Settings
    secret_key: str = "your-super-secret-key-change-this-in-production-123456789"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # Redis Settings
    redis_url: str = "redis://localhost:6379/0"
    
    # Email Settings
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    email_user: str = ""
    email_password: str = ""
    email_from: str = ""
    email_enabled: bool = False
    
    # CORS Settings
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]
    
    # Frontend Settings
    frontend_url: str = "http://localhost:3000"
    
    # App Settings
    app_name: str = "FastAPI Blog System"
    debug: bool = True
    
    # Scheduler Settings
    timezone: str = "Asia/Shanghai"
    
    # OAuth Settings
    # GitHub OAuth
    github_client_id: str = ""
    github_client_secret: str = ""
    
    # Google OAuth
    google_client_id: str = ""
    google_client_secret: str = ""
    
    # OAuth Base URL
    oauth_base_url: str = "http://localhost:8000"
    
    # Proxy Settings (for accessing blocked services)
    http_proxy: Optional[str] = None
    https_proxy: Optional[str] = None
    no_proxy: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @classmethod
    def reload(cls):
        """重新加载环境变量和配置"""
        # 重新加载.env文件
        load_dotenv(override=True)
        
        # 清除可能的缓存
        if hasattr(cls, '_instance'):
            delattr(cls, '_instance')
        
        # 返回新的配置实例
        return cls()


# 创建全局配置实例
settings = Settings()

def reload_settings():
    """重新加载全局配置"""
    global settings
    settings = Settings.reload()
    return settings 