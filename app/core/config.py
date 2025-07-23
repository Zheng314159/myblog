from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import os
from dotenv import load_dotenv

# 获取 env_file 优先级（不论是否在容器中，都定义它）
ENV_FILE = os.getenv("ENV_FILE", ".env")

# 如果不是在容器中运行，自动加载 dotenv 文件（仅本地）
if not os.getenv("IN_DOCKER", "").lower() == "true":
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=Path(ENV_FILE), override=True)

class Settings(BaseSettings):
    # Database
    https_only: bool = Field(default=False, alias="HTTPS_ONLY")  # 是否强制使用 HTTPS
    database_url: str = "sqlite+aiosqlite:///./blog.db"
    environment: str = Field(default="development", alias="ENVIRONMENT") # 环境变量，默认为 development，可通过 .env 文件覆盖
    python_io_encoding: str = Field(default="utf-8", alias="PYTHONIOENCODING")  # 确保 Python IO 编码为 UTF-8
    # JWT Settings
    secret_key: str = "your-super-secret-key-change-this-in-production-123456789"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 默认 1 天，可通过 .env 配置覆盖
    refresh_token_expire_days: int = 7
    
    # Redis Settings
    redis_url: str = "redis://localhost:6379/0"
    
    # Email Settings
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    email_user: str = ""
    email_password: str = ""
    email_from: str = ""
    notification_email: Optional[str] = Field(default=None, alias="NOTIFICATION_EMAIL")
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
    oauth_base_url: str = Field(default="http://localhost:8000", alias="OAUTH_BASE_URL")
    
    # Proxy Settings (for accessing blocked services)
    http_proxy: Optional[str] = None
    https_proxy: Optional[str] = None
    no_proxy: Optional[str] = None
    

    # Scheduler/Notification dynamic config
    scheduler_cleanup_redis_enabled: bool = Field(default=True, alias="SCHEDULER_CLEANUP_REDIS_ENABLED")
    scheduler_cleanup_redis_cron: str = Field(default="0 * * * *", alias="SCHEDULER_CLEANUP_REDIS_CRON")
    scheduler_system_notification_enabled: bool = Field(default=True, alias="SCHEDULER_SYSTEM_NOTIFICATION_ENABLED")
    scheduler_system_notification_cron: str = Field(default="5 * * * *", alias="SCHEDULER_SYSTEM_NOTIFICATION_CRON")
    notification_websocket_enabled: bool = Field(default=True, alias="NOTIFICATION_WEBSOCKET_ENABLED")
    notification_email_enabled: bool = Field(default=False, alias="NOTIFICATION_EMAIL_ENABLED")
    enable_notification_fetch: bool = Field(default=True, alias="ENABLE_NOTIFICATION_FETCH")
    enable_notification_push: bool = Field(default=True, alias="ENABLE_NOTIFICATION_PUSH")
    
    # 支付宝配置
    alipay_app_id: str = Field(default="", alias="ALIPAY_APP_ID")
    alipay_app_private_key_path: str = Field(default="keys/app_private_key.pem", alias="ALIPAY_APP_PRIVATE_KEY_PATH")
    alipay_public_key_path: str = Field(default="keys/alipay_public_key.pem", alias="ALIPAY_PUBLIC_KEY_PATH")
    alipay_notify_url: str = Field(default="", alias="ALIPAY_NOTIFY_URL")
    alipay_return_url: str = Field(default="", alias="ALIPAY_RETURN_URL")
    alipay_gateway: str = Field(default="", alias="ALIPAY_GATEWAY")
    alipay_qr_base: str = Field(default="", alias="ALIPAY_QR_BASE")
    # 微信支付V3配置
    wechat_appid: str = Field(default="", alias="WECHAT_APPID")
    wechat_mchid: str = Field(default="", alias="WECHAT_MCHID")
    wechat_api_v3_key: str = Field(default="", alias="WECHAT_API_V3_KEY")
    wechat_private_key_path: str = Field(default="", alias="WECHAT_PRIVATE_KEY_PATH")
    wechat_cert_serial_no: str = Field(default="", alias="WECHAT_CERT_SERIAL_NO")
    wechat_notify_url: str = Field(default="", alias="WECHAT_NOTIFY_URL")
    wechat_platform_cert_path: str = Field(default="", alias="WECHAT_PLATFORM_CERT_PATH")
    wechat_pay_type: str = Field(default="native", alias="WECHAT_PAY_TYPE")
    wechat_qr_base: str = Field(default="", alias="WECHAT_QR_BASE")
    # PayPal配置
    paypal_client_id: str = Field(default="", alias="PAYPAL_CLIENT_ID")
    paypal_client_secret: str = Field(default="", alias="PAYPAL_CLIENT_SECRET")
    paypal_api_base: str = Field(default="https://api-m.sandbox.paypal.com", alias="PAYPAL_API_BASE")
    paypal_return_url: str = Field(default="", alias="PAYPAL_RETURN_URL")
    paypal_cancel_url: str = Field(default="", alias="PAYPAL_CANCEL_URL")
    paypal_currency: str = Field(default="USD", alias="PAYPAL_CURRENCY")
    paypal_qr_base: str = Field(default="", alias="PAYPAL_QR_BASE")
    
    @property
    def is_postgres(self) -> bool:
        return self.database_url.startswith("postgresql")
    
    @property
    def alipay_private_key(self):
        """读取支付宝私钥内容"""
        if self.alipay_app_private_key_path and os.path.exists(self.alipay_app_private_key_path):
            with open(self.alipay_app_private_key_path, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    @property
    def alipay_public_key(self):
        """读取支付宝公钥内容"""
        if self.alipay_public_key_path and os.path.exists(self.alipay_public_key_path):
            with open(self.alipay_public_key_path, "r", encoding="utf-8") as f:
                return f.read()
        return ""
    
    @property
    def wechat_private_key(self):
        """读取微信支付私钥内容"""
        if self.wechat_private_key_path and os.path.exists(self.wechat_private_key_path):
            with open(self.wechat_private_key_path, "r", encoding="utf-8") as f:
                return f.read()
        return ""
    
    @property
    def wechat_platform_cert(self):
        """读取微信支付平台证书内容"""
        if self.wechat_platform_cert_path and os.path.exists(self.wechat_platform_cert_path):
            with open(self.wechat_platform_cert_path, "r", encoding="utf-8") as f:
                return f.read()
        return ""
    
    class Config:
        validate_by_name = True  # 允许用字段名或别名赋值
        env_file = ENV_FILE
        env_file_encoding = "utf-8"
        case_sensitive = False

    # model_config = SettingsConfigDict(
    #     env_file=f".env.{os.getenv('ENVIRONMENT', 'development')}",
    #     env_file = os.getenv("ENV_FILE", ".env"),
    #     env_file_encoding="utf-8",
    #     case_sensitive = False
    # )    
    
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