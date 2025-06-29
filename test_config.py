#!/usr/bin/env python3
"""
配置检查脚本
"""
import os
from dotenv import load_dotenv
from app.core.config import settings

# 加载环境变量
load_dotenv()

print("=== 环境变量检查 ===")
print(f"SMTP_SERVER: {os.getenv('SMTP_SERVER', 'Not set')}")
print(f"SMTP_PORT: {os.getenv('SMTP_PORT', 'Not set')}")
print(f"EMAIL_USER: {os.getenv('EMAIL_USER', 'Not set')}")
print(f"EMAIL_PASSWORD: {'*' * len(os.getenv('EMAIL_PASSWORD', '')) if os.getenv('EMAIL_PASSWORD') else 'Not set'}")
print(f"EMAIL_FROM: {os.getenv('EMAIL_FROM', 'Not set')}")
print(f"EMAIL_ENABLED: {os.getenv('EMAIL_ENABLED', 'Not set')}")

print("\n=== 应用配置检查 ===")
print(f"settings.smtp_server: {settings.smtp_server}")
print(f"settings.smtp_port: {settings.smtp_port}")
print(f"settings.email_user: {settings.email_user}")
print(f"settings.email_password: {'*' * len(settings.email_password) if settings.email_password else 'Not set'}")
print(f"settings.email_from: {settings.email_from}")
print(f"settings.email_enabled: {settings.email_enabled}")

print("\n=== 配置对比 ===")
env_smtp = os.getenv('SMTP_SERVER', '')
app_smtp = settings.smtp_server
print(f"SMTP_SERVER 匹配: {env_smtp == app_smtp}")

env_user = os.getenv('EMAIL_USER', '')
app_user = settings.email_user
print(f"EMAIL_USER 匹配: {env_user == app_user}")

env_enabled = os.getenv('EMAIL_ENABLED', 'false').lower() == 'true'
app_enabled = settings.email_enabled
print(f"EMAIL_ENABLED 匹配: {env_enabled == app_enabled}")

# 测试邮件服务
print("\n=== 邮件服务测试 ===")
from app.core.email import email_service

print(f"email_service.smtp_server: {email_service.smtp_server}")
print(f"email_service.email_user: {email_service.email_user}")
print(f"email_service.enabled: {email_service.enabled}")

# 测试发送邮件
print("\n=== 测试发送邮件 ===")
try:
    success = email_service.send_email(
        "test@example.com",
        "配置测试",
        "这是一封配置测试邮件"
    )
    print(f"发送结果: {success}")
except Exception as e:
    print(f"发送异常: {e}") 