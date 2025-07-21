#!/usr/bin/env python3
"""
测试文章创建功能
"""

import asyncio
import aiohttp
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"


async def test_article_creation():
    """测试文章创建"""
    async with aiohttp.ClientSession() as session:
        # 1. 先注册用户
        user_data = {
            "username": "testuser_article",
            "email": "test_article@example.com",
            "password": "testpass123",
            "full_name": "Test User Article"
        }
        
        print("1. 注册用户...")
        async with session.post(f"{BASE_URL}/auth/register", json=user_data) as response:
            if response.status == 200:
                result = await response.json()
                access_token = result.get("access_token")
                print("✅ 用户注册成功")
            elif response.status == 409:
                print("⚠️ 用户已存在，尝试登录...")
                login_data = {
                    "username": user_data["username"],
                    "password": user_data["password"]
                }
                async with session.post(f"{BASE_URL}/auth/login", json=login_data) as login_response:
                    if login_response.status == 200:
                        result = await login_response.json()
                        access_token = result.get("access_token")
                        print("✅ 用户登录成功")
                    else:
                        print(f"❌ 用户登录失败: {login_response.status}")
                        return
            else:
                print(f"❌ 用户注册失败: {response.status}")
                return
        
        # 2. 测试创建简单文章
        print("\n2. 测试创建简单文章...")
        article_data = {
            "title": "简单测试文章",
            "content": "这是一个简单的测试文章内容。",
            "summary": "简单测试摘要",
            "status": "published",
            "tags": ["测试"],
            "has_latex": False
        }
        
        headers = {"Authorization": f"Bearer {access_token}"}
        async with session.post(f"{BASE_URL}/articles", json=article_data, headers=headers) as response:
            print(f"状态码: {response.status}")
            print(f"响应头: {dict(response.headers)}")
            
            try:
                result = await response.json()
                print(f"响应内容: {result}")
                if response.status == 200:
                    print("✅ 简单文章创建成功")
                else:
                    print(f"❌ 简单文章创建失败: {result}")
            except Exception as e:
                text_result = await response.text()
                print(f"❌ 解析响应失败: {e}")
                print(f"原始响应: {text_result}")
        
        # 3. 测试创建包含LaTeX的文章
        print("\n3. 测试创建包含LaTeX的文章...")
        latex_article_data = {
            "title": "LaTeX测试文章",
            "content": "# LaTeX测试文章\n\n这是一个包含数学公式的测试文章。\n\n## 行内公式\n\n当 $a \\neq 0$ 时，方程 $ax^2 + bx + c = 0$ 的解为：\n\n## 块级公式\n\n二次方程的求根公式：\n\n$$x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$$",
            "summary": "测试LaTeX功能的文章",
            "status": "published",
            "tags": ["LaTeX", "数学", "测试"],
            "has_latex": True,
            "latex_content": "\\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}"
        }
        
        async with session.post(f"{BASE_URL}/articles", json=latex_article_data, headers=headers) as response:
            print(f"状态码: {response.status}")
            print(f"响应头: {dict(response.headers)}")
            
            try:
                result = await response.json()
                print(f"响应内容: {result}")
                if response.status == 200:
                    print("✅ LaTeX文章创建成功")
                else:
                    print(f"❌ LaTeX文章创建失败: {result}")
            except Exception as e:
                text_result = await response.text()
                print(f"❌ 解析响应失败: {e}")
                print(f"原始响应: {text_result}")


if __name__ == "__main__":
    asyncio.run(test_article_creation()) 