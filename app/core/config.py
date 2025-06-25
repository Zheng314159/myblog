from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Database
    database_url: str = Field(default="sqlite+aiosqlite:///./blog.db", env="DATABASE_URL")
    
    # JWT Settings
    secret_key: str = Field(env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # Redis Settings
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    
    # Email Settings
    smtp_server: str = Field(default="smtp.gmail.com", env="SMTP_SERVER")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    email_user: str = Field(default="", env="EMAIL_USER")
    email_password: str = Field(default="", env="EMAIL_PASSWORD")
    email_from: str = Field(default="", env="EMAIL_FROM")
    email_enabled: bool = Field(default=False, env="EMAIL_ENABLED")
    
    # CORS Settings
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        env="ALLOWED_ORIGINS"
    )
    
    # App Settings
    app_name: str = Field(default="FastAPI Blog System", env="APP_NAME")
    debug: bool = Field(default=True, env="DEBUG")
    
    # Scheduler Settings
    timezone: str = Field(default="Asia/Shanghai", env="TIMEZONE")
    
    # OAuth Settings
    # GitHub OAuth
    github_client_id: str = Field(default="", env="GITHUB_CLIENT_ID")
    github_client_secret: str = Field(default="", env="GITHUB_CLIENT_SECRET")
    
    # Google OAuth
    google_client_id: str = Field(default="", env="GOOGLE_CLIENT_ID")
    google_client_secret: str = Field(default="", env="GOOGLE_CLIENT_SECRET")
    
    # OAuth Base URL
    oauth_base_url: str = Field(default="http://localhost:8000", env="OAUTH_BASE_URL")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings() 