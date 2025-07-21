#!/usr/bin/env python3
"""
简单认证测试脚本
"""

import asyncio
import aiohttp
import json
from typing import Optional

BASE_URL = "http://127.0.0.1:8000"

class AuthTester:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.session = None
        self.token = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_health(self) -> bool:
        """测试健康检查"""
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ 健康检查通过: {data}")
                    return True
                else:
                    print(f"❌ 健康检查失败: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ 健康检查异常: {e}")
            return False
    
    async def test_register(self, username: str, email: str, password: str) -> bool:
        """测试用户注册"""
        try:
            data = {
                "username": username,
                "email": email,
                "password": password,
                "full_name": f"{username} User"
            }
            
            async with self.session.post(f"{self.base_url}/api/v1/auth/register", json=data) as response:
                if response.status == 201:
                    result = await response.json()
                    print(f"✅ 用户注册成功: {result}")
                    return True
                elif response.status == 409:
                    result = await response.json()
                    print(f"⚠️ 用户已存在: {result}")
                    return True  # 用户已存在也算成功
                else:
                    result = await response.json()
                    print(f"❌ 用户注册失败: {result}")
                    return False
        except Exception as e:
            print(f"❌ 用户注册异常: {e}")
            return False
    
    async def test_login(self, username: str, password: str) -> bool:
        """测试用户登录"""
        try:
            data = {
                "username": username,
                "password": password
            }
            
            async with self.session.post(f"{self.base_url}/api/v1/auth/login", data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    self.token = result.get("access_token")
                    print(f"✅ 用户登录成功: {result.get('token_type')} {self.token[:20]}...")
                    return True
                else:
                    result = await response.json()
                    print(f"❌ 用户登录失败: {result}")
                    return False
        except Exception as e:
            print(f"❌ 用户登录异常: {e}")
            return False
    
    async def test_protected_endpoint(self) -> bool:
        """测试受保护的端点"""
        if not self.token:
            print("❌ 没有访问令牌，跳过受保护端点测试")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            async with self.session.get(f"{self.base_url}/api/v1/auth/me", headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ 受保护端点访问成功: {result}")
                    return True
                else:
                    result = await response.json()
                    print(f"❌ 受保护端点访问失败: {result}")
                    return False
        except Exception as e:
            print(f"❌ 受保护端点访问异常: {e}")
            return False


async def main():
    """主测试函数"""
    print("🔐 认证功能测试\n" + "="*50)
    async with aiohttp.ClientSession() as session:
        # 健康检查
        print("\n🔍 测试健康检查...")
        async with session.get(f"{BASE_URL}/health") as resp:
            data = await resp.json()
            if resp.status == 200 and data.get("status") == "healthy":
                print(f"✅ 健康检查通过: {data}")
            else:
                print(f"❌ 健康检查失败: {data}")
                return

        # 注册测试用户
        print("🔍 测试用户注册...")
        reg_data = {
            "username": "testuser_auth",
            "email": "testauth@example.com",
            "password": "testpass123",
            "full_name": "testuser_auth User"
        }
        try:
            async with session.post(f"{BASE_URL}/api/v1/auth/register", json=reg_data) as resp:
                try:
                    result = await resp.json()
                except Exception:
                    result = await resp.text()
                if resp.status in (200, 201) and isinstance(result, dict) and "access_token" in result:
                    print(f"✅ 用户注册成功: {result}")
                elif resp.status == 409 or (isinstance(result, dict) and result.get("message", "").find("already registered") != -1):
                    print(f"⚠️ 用户已存在: {result}")
                else:
                    print(f"❌ 用户注册失败: {result}")
                    return
        except Exception as e:
            print(f"❌ 用户注册异常: {e}")
            return

        # 登录测试用户
        print("\n🔍 测试用户登录...")
        login_data = {
            "username": "testuser_auth",
            "password": "testpass123"
        }
        try:
            async with session.post(f"{BASE_URL}/api/v1/auth/login", json=login_data) as resp:
                try:
                    result = await resp.json()
                except Exception as e:
                    print(f"❌ 用户登录异常: {e}, url={resp.url}")
                    print("❌ 用户登录失败")
                    return
                if resp.status == 200 and "access_token" in result:
                    print(f"✅ 用户登录成功: {result}")
                else:
                    print(f"❌ 用户登录失败: {result}")
                    return
        except Exception as e:
            print(f"❌ 用户登录异常: {e}")
            return

        # 刷新 token
        print("\n🔍 测试刷新 token...")
        refresh_token = result.get("refresh_token")
        if not refresh_token:
            print("❌ 未获取到 refresh_token，跳过刷新 token 测试")
            return
        try:
            async with session.post(f"{BASE_URL}/api/v1/auth/refresh", json={"refresh_token": refresh_token}) as resp:
                try:
                    result2 = await resp.json()
                except Exception as e:
                    print(f"❌ 刷新 token 异常: {e}, url={resp.url}")
                    print("❌ 刷新 token 失败")
                    return
                if resp.status == 200 and "access_token" in result2:
                    print(f"✅ 刷新 token 成功: {result2}")
                else:
                    print(f"❌ 刷新 token 失败: {result2}")
                    return
        except Exception as e:
            print(f"❌ 刷新 token 异常: {e}")
            return

        # 登出
        print("\n🔍 测试登出...")
        access_token = result.get("access_token")
        if not access_token:
            print("❌ 未获取到 access_token，跳过登出测试")
            return
        try:
            async with session.post(f"{BASE_URL}/api/v1/auth/logout", json={"access_token": access_token}) as resp:
                try:
                    result3 = await resp.json()
                except Exception as e:
                    print(f"❌ 登出异常: {e}, url={resp.url}")
                    print("❌ 登出失败")
                    return
                if resp.status == 200 and result3.get("message"):
                    print(f"✅ 登出成功: {result3}")
                else:
                    print(f"❌ 登出失败: {result3}")
                    return
        except Exception as e:
            print(f"❌ 登出异常: {e}")
            return

        print("\n🎉 所有认证相关测试通过！")


if __name__ == "__main__":
    asyncio.run(main()) 