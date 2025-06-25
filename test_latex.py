#!/usr/bin/env python3
"""
测试LaTeX功能
"""

import asyncio
import aiohttp
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000/api/v1"


class LatexTester:
    def __init__(self):
        self.session = None
        self.access_token = None
        self.test_user = {
            "username": "testuser_latex",
            "email": "test_latex@example.com",
            "password": "testpass123",
            "full_name": "Test User LaTeX"
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def make_request(self, method, endpoint, data=None, headers=None):
        """发送HTTP请求"""
        url = f"{BASE_URL}{endpoint}"
        request_headers = {
            "Content-Type": "application/json"
        }
        if self.access_token:
            request_headers["Authorization"] = f"Bearer {self.access_token}"
        if headers:
            request_headers.update(headers)
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url, headers=request_headers) as response:
                    return await response.json(), response.status
            elif method.upper() == "POST":
                async with self.session.post(url, json=data, headers=request_headers) as response:
                    return await response.json(), response.status
            elif method.upper() == "PUT":
                async with self.session.put(url, json=data, headers=request_headers) as response:
                    return await response.json(), response.status
            elif method.upper() == "DELETE":
                async with self.session.delete(url, headers=request_headers) as response:
                    return await response.json(), response.status
        except Exception as e:
            print(f"请求失败: {e}")
            return None, 500
    
    async def make_form_request(self, method, endpoint, data=None):
        """发送表单请求"""
        url = f"{BASE_URL}{endpoint}"
        request_headers = {}
        if self.access_token:
            request_headers["Authorization"] = f"Bearer {self.access_token}"
        
        try:
            if method.upper() == "POST":
                async with self.session.post(url, data=data, headers=request_headers) as response:
                    return await response.json(), response.status
        except Exception as e:
            print(f"请求失败: {e}")
            return None, 500
    
    async def test_health_check(self):
        """测试健康检查"""
        print("🔍 测试健康检查...")
        url = "http://127.0.0.1:8000/health"
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ 健康检查通过")
                    return True
                else:
                    print(f"❌ 健康检查失败: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ 系统未启动，请先启动服务器")
            return False
    
    async def test_user_registration(self):
        """测试用户注册"""
        print("👤 测试用户注册...")
        response, status = await self.make_request("POST", "/auth/register", self.test_user)
        if status == 200:
            self.access_token = response.get("access_token")
            print("✅ 用户注册成功")
            return True
        elif status == 409:
            print("⚠️ 用户已存在，尝试登录...")
            return await self.test_user_login()
        else:
            print(f"❌ 用户注册失败: {status} - {response}")
            return False
    
    async def test_user_login(self):
        """测试用户登录"""
        print("🔐 测试用户登录...")
        login_data = {
            "username": self.test_user["username"],
            "password": self.test_user["password"]
        }
        response, status = await self.make_request("POST", "/auth/login", login_data)
        if status == 200:
            self.access_token = response.get("access_token")
            print("✅ 用户登录成功")
            return True
        else:
            print(f"❌ 用户登录失败: {status} - {response}")
            return False
    
    async def test_latex_validation(self):
        """测试LaTeX语法验证"""
        print("🔍 测试LaTeX语法验证...")
        
        # 测试有效的LaTeX
        valid_latex = "\\frac{a}{b} = \\frac{c}{d}"
        data = {"latex_content": valid_latex}
        response, status = await self.make_form_request("POST", "/articles/latex/validate", data)
        if status == 200:
            print("✅ LaTeX语法验证成功")
            print(f"   验证结果: {response}")
        else:
            print(f"❌ LaTeX语法验证失败: {status}")
        
        # 测试无效的LaTeX
        invalid_latex = "\\frac{a}{b} = \\frac{c}{d"  # 缺少闭合括号
        data = {"latex_content": invalid_latex}
        response, status = await self.make_form_request("POST", "/articles/latex/validate", data)
        if status == 200:
            print("✅ 无效LaTeX检测成功")
            print(f"   验证结果: {response}")
        else:
            print(f"❌ 无效LaTeX检测失败: {status}")
    
    async def test_latex_preview(self):
        """测试LaTeX预览"""
        print("👁️ 测试LaTeX预览...")
        
        # 测试行内公式
        inline_latex = "\\alpha + \\beta = \\gamma"
        data = {"latex_content": inline_latex, "block_type": "inline"}
        response, status = await self.make_form_request("POST", "/articles/latex/preview", data)
        if status == 200:
            print("✅ 行内LaTeX预览成功")
            print(f"   预览结果: {response}")
        else:
            print(f"❌ 行内LaTeX预览失败: {status}")
        
        # 测试块级公式
        block_latex = "\\int_{0}^{\\infty} e^{-x} dx = 1"
        data = {"latex_content": block_latex, "block_type": "block"}
        response, status = await self.make_form_request("POST", "/articles/latex/preview", data)
        if status == 200:
            print("✅ 块级LaTeX预览成功")
            print(f"   预览结果: {response}")
        else:
            print(f"❌ 块级LaTeX预览失败: {status}")
    
    async def test_article_with_latex(self):
        """测试包含LaTeX的文章"""
        print("📝 测试包含LaTeX的文章...")
        
        article_data = {
            "title": "LaTeX测试文章",
            "content": """# LaTeX测试文章

这是一个包含数学公式的测试文章。

## 行内公式

当 $a \\neq 0$ 时，方程 $ax^2 + bx + c = 0$ 的解为：

## 块级公式

二次方程的求根公式：

$$x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$$

## 积分公式

定积分：

$$\\int_{0}^{\\infty} e^{-x} dx = 1$$

## 矩阵

$$\\begin{pmatrix}
a & b \\\\
c & d
\\end{pmatrix}$$

## 化学公式

$$\\ce{H2O + CO2 -> H2CO3}$$
""",
            "summary": "测试LaTeX功能的文章",
            "status": "published",
            "tags": ["LaTeX", "数学", "测试"],
            "has_latex": True,
            "latex_content": "\\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}"
        }
        
        response, status = await self.make_request("POST", "/articles", article_data)
        if status == 200:
            article_id = response.get("id")
            print(f"✅ 创建包含LaTeX的文章成功，ID: {article_id}")
            
            # 获取文章详情
            response, status = await self.make_request("GET", f"/articles/{article_id}")
            if status == 200:
                print("✅ 获取文章详情成功")
                print(f"   文章标题: {response.get('title')}")
                print(f"   包含LaTeX: {response.get('has_latex')}")
            else:
                print(f"❌ 获取文章详情失败: {status}")
            
            return article_id
        else:
            print(f"❌ 创建包含LaTeX的文章失败: {status} - {response}")
            return None
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("🧪 LaTeX功能测试开始")
        print("=" * 50)
        
        # 健康检查
        if not await self.test_health_check():
            print("❌ 系统未启动，请先启动服务器")
            return
        
        # 用户认证
        if not await self.test_user_registration():
            print("❌ 用户认证失败")
            return
        
        print()
        
        # LaTeX功能测试
        await self.test_latex_validation()
        print()
        
        await self.test_latex_preview()
        print()
        
        await self.test_article_with_latex()
        print()
        
        print("=" * 50)
        print("🎉 LaTeX功能测试完成！")


async def main():
    """主函数"""
    async with LatexTester() as tester:
        await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main()) 