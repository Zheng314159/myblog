#!/usr/bin/env python3
"""
简单认证测试脚本
"""

import asyncio
import aiohttp
import json
from typing import Optional


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
    print("🔐 认证功能测试")
    print("=" * 50)
    
    async with AuthTester() as tester:
        # 测试健康检查
        print("\n🔍 测试健康检查...")
        if not await tester.test_health():
            print("❌ 健康检查失败，停止测试")
            return
        
        # 测试用户注册
        print("\n🔍 测试用户注册...")
        test_username = "testuser_auth"
        test_email = "testauth@example.com"
        test_password = "testpass123"
        
        if not await tester.test_register(test_username, test_email, test_password):
            print("❌ 用户注册失败")
            return
        
        # 测试用户登录
        print("\n🔍 测试用户登录...")
        if not await tester.test_login(test_username, test_password):
            print("❌ 用户登录失败")
            return
        
        # 测试受保护的端点
        print("\n🔍 测试受保护的端点...")
        await tester.test_protected_endpoint()
    
    print("\n🎉 认证测试完成！")


if __name__ == "__main__":
    asyncio.run(main()) 