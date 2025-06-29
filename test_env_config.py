#!/usr/bin/env python3
"""
检查环境配置
"""
import os
from dotenv import load_dotenv
from app.core.config import settings

# 加载环境变量
load_dotenv()

print("=== 环境变量检查 ===")
print(f"EMAIL_ENABLED: {os.getenv('EMAIL_ENABLED', 'Not set')}")
print(f"SMTP_SERVER: {os.getenv('SMTP_SERVER', 'Not set')}")
print(f"SMTP_PORT: {os.getenv('SMTP_PORT', 'Not set')}")
print(f"EMAIL_USER: {os.getenv('EMAIL_USER', 'Not set')}")
print(f"EMAIL_FROM: {os.getenv('EMAIL_FROM', 'Not set')}")

# 检查是否有.env文件
env_file_exists = os.path.exists('.env')
print(f"\n.env文件存在: {env_file_exists}")

# 检查env.example文件
example_file_exists = os.path.exists('env.example')
print(f"env.example文件存在: {example_file_exists}")

if example_file_exists:
    print("\n=== env.example内容 ===")
    with open('env.example', 'r', encoding='utf-8') as f:
        content = f.read()
        print(content)

print("\n=== 配置对象检查 ===")
print(f"settings.email_enabled: {settings.email_enabled}")
print(f"settings.email_enabled 类型: {type(settings.email_enabled)}")

print("\n=== 所有环境变量 ===")
for key, value in os.environ.items():
    if 'EMAIL' in key.upper():
        print(f"{key}: {value}")

print("\n=== 设置环境变量 ===")
os.environ['EMAIL_ENABLED'] = 'false'
print(f"设置后 EMAIL_ENABLED: {os.getenv('EMAIL_ENABLED')}")

# 重新创建配置对象
from app.core.config import Settings
new_settings = Settings()
print(f"新配置对象 email_enabled: {new_settings.email_enabled}") 