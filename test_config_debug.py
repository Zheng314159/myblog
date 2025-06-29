#!/usr/bin/env python3
"""
测试配置加载和动态切换
"""
import os
import sys
import asyncio
from dotenv import load_dotenv

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings

def test_config_loading():
    """测试配置加载"""
    print("=== 配置加载测试 ===")
    print(f"EMAIL_ENABLED: {settings.email_enabled}")
    print(f"SMTP_SERVER: {settings.smtp_server}")
    print(f"EMAIL_USER: {settings.email_user}")
    print(f"EMAIL_FROM: {settings.email_from}")
    
    # 检查环境变量
    print("\n=== 环境变量检查 ===")
    print(f"EMAIL_ENABLED (env): {os.getenv('EMAIL_ENABLED')}")
    print(f"SMTP_SERVER (env): {os.getenv('SMTP_SERVER')}")
    print(f"EMAIL_USER (env): {os.getenv('EMAIL_USER')}")
    
    # 检查.env文件是否存在
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    print(f"\n.env文件存在: {os.path.exists(env_file)}")
    
    if os.path.exists(env_file):
        print("=== .env文件内容 ===")
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
            print(content)

def test_dynamic_config():
    """测试动态配置切换"""
    print("\n=== 动态配置测试 ===")
    
    # 测试不同的EMAIL_ENABLED值
    test_values = ['true', 'false', 'True', 'False', '1', '0']
    
    for value in test_values:
        # 临时设置环境变量
        os.environ['EMAIL_ENABLED'] = value
        print(f"设置 EMAIL_ENABLED={value}")
        
        # 重新加载配置
        from app.core.config import Settings
        temp_settings = Settings()
        print(f"  结果: {temp_settings.email_enabled} (类型: {type(temp_settings.email_enabled)})")

async def test_auth_config_endpoint():
    """测试认证配置端点"""
    print("\n=== 认证配置端点测试 ===")
    
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/api/v1/auth/config")
            print(f"状态码: {response.status_code}")
            print(f"响应: {response.json()}")
    except Exception as e:
        print(f"请求失败: {e}")

if __name__ == "__main__":
    # 加载环境变量
    load_dotenv()
    
    test_config_loading()
    test_dynamic_config()
    
    # 测试API端点
    asyncio.run(test_auth_config_endpoint()) 