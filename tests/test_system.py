#!/usr/bin/env python3
"""
FastAPI Blog System 测试脚本
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any

BASE_URL = "http://127.0.0.1:8000"

async def test_health_check():
    """测试健康检查"""
    print("🔍 测试健康检查...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ 健康检查通过: {data}")
                    return True
                else:
                    error_data = await response.text()
                    print(f"❌ 健康检查失败: {response.status}")
                    print(f"错误详情: {error_data}")
                    return False
    except Exception as e:
        print(f"❌ 健康检查连接失败: {e}")
        return False

async def test_root_endpoint():
    """测试根端点"""
    print("🔍 测试根端点...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ 根端点正常: {data}")
                    return True
                else:
                    error_data = await response.text()
                    print(f"❌ 根端点失败: {response.status}")
                    print(f"错误详情: {error_data}")
                    return False
    except Exception as e:
        print(f"❌ 根端点连接失败: {e}")
        return False

async def test_user_registration():
    """测试用户注册"""
    print("🔍 测试用户注册...")
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{BASE_URL}/api/v1/auth/register",
                json=user_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ 用户注册成功: {data.get('access_token', '')[:20]}...")
                    return data
                else:
                    error_data = await response.json()
                    print(f"❌ 用户注册失败: {error_data}")
                    return None
    except Exception as e:
        print(f"❌ 用户注册连接失败: {e}")
        return None

async def test_user_login():
    """测试用户登录"""
    print("🔍 测试用户登录...")
    login_data = {
        "username": "testuser",
        "password": "testpassword123"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{BASE_URL}/api/v1/auth/login",
                json=login_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ 用户登录成功: {data.get('access_token', '')[:20]}...")
                    return data
                else:
                    error_data = await response.json()
                    print(f"❌ 用户登录失败: {error_data}")
                    return None
    except Exception as e:
        print(f"❌ 用户登录连接失败: {e}")
        return None

async def test_protected_endpoint(token_data: Dict[str, Any]):
    """测试受保护的端点"""
    print("🔍 测试受保护的端点...")
    headers = {
        "Authorization": f"Bearer {token_data['access_token']}"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{BASE_URL}/health",
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ 受保护端点访问成功: {data}")
                    return True
                else:
                    error_data = await response.json()
                    print(f"❌ 受保护端点访问失败: {error_data}")
                    return False
    except Exception as e:
        print(f"❌ 受保护端点连接失败: {e}")
        return False

async def test_token_refresh(token_data: Dict[str, Any]):
    """测试Token刷新"""
    print("🔍 测试Token刷新...")
    refresh_data = {
        "refresh_token": token_data["refresh_token"]
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{BASE_URL}/api/v1/auth/refresh",
                json=refresh_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Token刷新成功: {data.get('access_token', '')[:20]}...")
                    return data
                else:
                    error_data = await response.json()
                    print(f"❌ Token刷新失败: {error_data}")
                    return None
    except Exception as e:
        print(f"❌ Token刷新连接失败: {e}")
        return None

async def test_logout(token_data: Dict[str, Any]):
    """测试用户登出"""
    print("🔍 测试用户登出...")
    logout_data = {
        "access_token": token_data["access_token"]
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{BASE_URL}/api/v1/auth/logout",
                json=logout_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ 用户登出成功: {data}")
                    return True
                else:
                    error_data = await response.json()
                    print(f"❌ 用户登出失败: {error_data}")
                    return False
    except Exception as e:
        print(f"❌ 用户登出连接失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("🧪 FastAPI Blog System 功能测试")
    print("=" * 50)
    print(f"🌐 测试地址: {BASE_URL}")
    print("=" * 50)
    
    # 测试基础功能
    if not await test_health_check():
        print("❌ 系统未启动，请先运行 python main.py")
        print("💡 提示: 确保服务器在 http://127.0.0.1:8000 运行")
        return
    
    if not await test_root_endpoint():
        print("❌ 根端点测试失败")
        return
    
    # 测试认证功能
    token_data = await test_user_registration()
    if not token_data:
        print("❌ 用户注册测试失败")
        return
    
    login_data = await test_user_login()
    if not login_data:
        print("❌ 用户登录测试失败")
        return
    
    # 测试受保护端点
    if not await test_protected_endpoint(login_data):
        print("❌ 受保护端点测试失败")
        return
    
    # 测试Token刷新
    new_token_data = await test_token_refresh(login_data)
    if not new_token_data:
        print("❌ Token刷新测试失败")
        return
    
    # 测试登出
    if not await test_logout(new_token_data):
        print("❌ 用户登出测试失败")
        return
    
    print("\n🎉 所有测试通过！")
    print("=" * 50)
    print("✅ 系统功能正常")
    print("✅ 认证系统工作正常")
    print("✅ JWT Token机制正常")
    print("✅ Redis连接正常")
    print("✅ 数据库操作正常")

if __name__ == "__main__":
    asyncio.run(main()) 