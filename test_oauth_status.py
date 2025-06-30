#!/usr/bin/env python3
"""
OAuth状态检查脚本 - 不修改数据库
检查GitHub和Google OAuth的配置和网络连接状态
"""

import asyncio
import httpx
import os
from app.core.config import settings

async def test_oauth_health():
    """测试OAuth健康状态"""
    print("=== OAuth 状态检查 ===\n")
    
    # 检查配置
    print("1. 配置检查:")
    print(f"   GitHub Client ID: {'已配置' if settings.github_client_id else '未配置'}")
    print(f"   GitHub Client Secret: {'已配置' if settings.github_client_secret else '未配置'}")
    print(f"   Google Client ID: {'已配置' if settings.google_client_id else '未配置'}")
    print(f"   Google Client Secret: {'已配置' if settings.google_client_secret else '未配置'}")
    print(f"   HTTP Proxy: {settings.http_proxy or '未设置'}")
    print(f"   HTTPS Proxy: {settings.https_proxy or '未设置'}")
    print()
    
    # 检查网络连接
    print("2. 网络连接测试:")
    
    # 测试GitHub
    print("   测试 GitHub API...")
    try:
        proxy = settings.https_proxy or settings.http_proxy
        transport = httpx.AsyncHTTPTransport(proxy=proxy) if proxy else None
        
        async with httpx.AsyncClient(transport=transport, timeout=10.0) as client:
            response = await client.get('https://api.github.com/zen')
            if response.status_code == 200:
                print(f"   ✅ GitHub API 可访问: {response.text}")
            else:
                print(f"   ❌ GitHub API 返回状态码: {response.status_code}")
    except Exception as e:
        print(f"   ❌ GitHub API 连接失败: {str(e)}")
    
    # 测试Google
    print("   测试 Google OAuth...")
    try:
        proxy = settings.https_proxy or settings.http_proxy
        transport = httpx.AsyncHTTPTransport(proxy=proxy) if proxy else None
        
        async with httpx.AsyncClient(transport=transport, timeout=10.0) as client:
            response = await client.get('https://accounts.google.com/.well-known/openid_configuration')
            if response.status_code == 200:
                print("   ✅ Google OAuth 可访问")
            else:
                print(f"   ❌ Google OAuth 返回状态码: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Google OAuth 连接失败: {str(e)}")
    
    print()
    
    # 检查环境变量
    print("3. 环境变量检查:")
    env_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'NO_PROXY']
    for var in env_vars:
        value = os.environ.get(var)
        print(f"   {var}: {value or '未设置'}")
    
    print()
    
    # 建议
    print("4. 建议:")
    if not settings.github_client_id or not settings.github_client_secret:
        print("   - 请配置GitHub OAuth凭据")
    if not settings.google_client_id or not settings.google_client_secret:
        print("   - 请配置Google OAuth凭据")
    if not settings.https_proxy and not settings.http_proxy:
        print("   - 如果无法访问Google服务，请设置代理")
        print("   - 在.env文件中添加: HTTPS_PROXY=http://127.0.0.1:7890")
    else:
        print("   - 代理已配置，应该可以访问Google服务")

if __name__ == "__main__":
    asyncio.run(test_oauth_health()) 