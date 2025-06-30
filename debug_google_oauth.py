#!/usr/bin/env python3
"""
调试Google OAuth问题
"""

import asyncio
import httpx
import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings

async def debug_google_oauth():
    """调试Google OAuth配置"""
    print("🔍 调试Google OAuth配置")
    print("="*50)
    
    # 检查配置
    print(f"Google Client ID: {settings.google_client_id[:10] if settings.google_client_id else 'None'}...")
    print(f"Google Client Secret: {'已设置' if settings.google_client_secret else '未设置'}")
    
    # 测试Google登录端点
    print("\n📡 测试Google登录端点...")
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get("http://localhost:8000/api/v1/oauth/google/login", follow_redirects=False)
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 500:
                print("❌ 服务器内部错误")
                # 尝试获取错误详情
                try:
                    error_response = await client.get("http://localhost:8000/api/v1/oauth/google/login")
                    print(f"错误响应: {error_response.text[:200]}...")
                except Exception as e:
                    print(f"获取错误详情失败: {e}")
            elif response.status_code == 302:
                redirect_url = response.headers.get('location', '')
                print(f"✅ 重定向成功")
                print(f"重定向URL: {redirect_url[:100]}...")
            else:
                print(f"⚠️ 意外状态码: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 连接失败: {e}")
    
    # 测试OAuth提供商端点
    print("\n📡 测试OAuth提供商端点...")
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get("http://localhost:8000/api/v1/oauth/providers")
            print(f"状态码: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"可用提供商: {data}")
            else:
                print(f"响应内容: {response.text[:200]}...")
        except Exception as e:
            print(f"❌ 提供商端点测试失败: {e}")

if __name__ == "__main__":
    asyncio.run(debug_google_oauth()) 