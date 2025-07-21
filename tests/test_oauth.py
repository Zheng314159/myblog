#!/usr/bin/env python3
"""
OAuth测试脚本 - 测试Google和GitHub OAuth功能
"""

import asyncio
import httpx
import json
import os
import sys
from typing import Dict, Any, Optional
from urllib.parse import urlencode, parse_qs, urlparse

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User, OAuthProvider, OAuthAccount
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class OAuthTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        self.session = httpx.AsyncClient(timeout=30.0)
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.aclose()
    
    def print_separator(self, title: str):
        """打印分隔符"""
        print("\n" + "="*60)
        print(f" {title} ")
        print("="*60)
    
    def print_success(self, message: str):
        """打印成功消息"""
        print(f"✅ {message}")
    
    def print_error(self, message: str):
        """打印错误消息"""
        print(f"❌ {message}")
    
    def print_info(self, message: str):
        """打印信息消息"""
        print(f"ℹ️  {message}")
    
    def print_warning(self, message: str):
        """打印警告消息"""
        print(f"⚠️  {message}")
    
    async def test_config(self):
        """测试OAuth配置"""
        self.print_separator("OAuth配置测试")
        
        # 检查GitHub配置
        if settings.github_client_id and settings.github_client_secret:
            self.print_success("GitHub OAuth已配置")
            self.print_info(f"GitHub Client ID: {settings.github_client_id[:10]}...")
        else:
            self.print_error("GitHub OAuth未配置")
            self.print_info("请在.env文件中设置GITHUB_CLIENT_ID和GITHUB_CLIENT_SECRET")
        
        # 检查Google配置
        if settings.google_client_id and settings.google_client_secret:
            self.print_success("Google OAuth已配置")
            self.print_info(f"Google Client ID: {settings.google_client_id[:10]}...")
        else:
            self.print_error("Google OAuth未配置")
            self.print_info("请在.env文件中设置GOOGLE_CLIENT_ID和GOOGLE_CLIENT_SECRET")
        
        # 检查基础URL配置
        self.print_info(f"OAuth Base URL: {settings.oauth_base_url}")
        self.print_info(f"Frontend URL: {settings.frontend_url}")
    
    async def test_oauth_endpoints(self):
        """测试OAuth端点"""
        self.print_separator("OAuth端点测试")
        
        endpoints = [
            ("/api/v1/oauth/github/login", "GitHub登录端点"),
            ("/api/v1/oauth/github/callback", "GitHub回调端点"),
            ("/api/v1/oauth/google/login", "Google登录端点"),
            ("/api/v1/oauth/google/callback", "Google回调端点"),
            ("/api/v1/oauth/providers", "可用提供商端点"),
        ]
        
        for endpoint, description in endpoints:
            try:
                response = await self.session.get(f"{self.base_url}{endpoint}")
                if response.status_code in [200, 302, 307, 308]:
                    self.print_success(f"{description} - 可访问 (状态码: {response.status_code})")
                else:
                    self.print_warning(f"{description} - 返回状态码: {response.status_code}")
            except Exception as e:
                self.print_error(f"{description} - 连接失败: {str(e)}")
    
    async def test_oauth_login_urls(self):
        """测试OAuth登录URL"""
        self.print_separator("OAuth登录URL测试")
        
        # 测试GitHub登录URL
        try:
            response = await self.session.get(f"{self.base_url}/api/v1/oauth/github/login", follow_redirects=False)
            if response.status_code == 302:
                redirect_url = response.headers.get('location', '')
                if 'github.com' in redirect_url:
                    self.print_success("GitHub登录URL正确重定向到GitHub")
                    self.print_info(f"重定向URL: {redirect_url[:100]}...")
                else:
                    self.print_warning(f"GitHub重定向URL可能有问题: {redirect_url}")
            else:
                self.print_warning(f"GitHub登录端点返回状态码: {response.status_code}")
        except Exception as e:
            self.print_error(f"GitHub登录URL测试失败: {str(e)}")
        
        # 测试Google登录URL
        try:
            response = await self.session.get(f"{self.base_url}/api/v1/oauth/google/login", follow_redirects=False)
            if response.status_code == 302:
                redirect_url = response.headers.get('location', '')
                if 'accounts.google.com' in redirect_url:
                    self.print_success("Google登录URL正确重定向到Google")
                    self.print_info(f"重定向URL: {redirect_url[:100]}...")
                else:
                    self.print_warning(f"Google重定向URL可能有问题: {redirect_url}")
            else:
                self.print_warning(f"Google登录端点返回状态码: {response.status_code}")
        except Exception as e:
            self.print_error(f"Google登录URL测试失败: {str(e)}")
    
    async def test_oauth_providers_endpoint(self):
        """测试OAuth提供商端点"""
        self.print_separator("OAuth提供商端点测试")
        
        try:
            response = await self.session.get(f"{self.base_url}/api/v1/oauth/providers")
            if response.status_code == 200:
                data = response.json()
                self.print_success("OAuth提供商端点返回成功")
                self.print_info(f"可用提供商: {data}")
            else:
                self.print_warning(f"OAuth提供商端点返回状态码: {response.status_code}")
        except Exception as e:
            self.print_error(f"OAuth提供商端点测试失败: {str(e)}")
    
    async def test_database_oauth_models(self):
        """测试数据库OAuth模型"""
        self.print_separator("数据库OAuth模型测试")
        
        try:
            async for db in get_db():
                # 测试查询OAuth账户
                result = await db.execute(select(OAuthAccount))
                oauth_accounts = result.scalars().all()
                self.print_success(f"数据库连接成功，找到 {len(oauth_accounts)} 个OAuth账户")
                
                # 显示现有的OAuth账户
                if oauth_accounts:
                    self.print_info("现有的OAuth账户:")
                    for account in oauth_accounts:
                        self.print_info(f"  - 用户ID: {account.user_id}, 提供商: {account.provider}, 提供商用户ID: {account.provider_user_id}")
                else:
                    self.print_info("暂无OAuth账户")
                break
        except Exception as e:
            self.print_error(f"数据库OAuth模型测试失败: {str(e)}")
    
    async def test_oauth_service_methods(self):
        """测试OAuth服务方法"""
        self.print_separator("OAuth服务方法测试")
        
        try:
            from app.core.oauth import OAuthService
            
            # 测试方法存在性
            methods = [
                'get_github_user_info',
                'get_google_user_info', 
                'find_or_create_oauth_user',
                'create_oauth_tokens',
                'bind_oauth_account',
                'unbind_oauth_account',
                'get_user_oauth_accounts'
            ]
            
            for method_name in methods:
                if hasattr(OAuthService, method_name):
                    self.print_success(f"OAuth服务方法 {method_name} 存在")
                else:
                    self.print_error(f"OAuth服务方法 {method_name} 不存在")
                    
        except ImportError as e:
            self.print_error(f"无法导入OAuth服务: {str(e)}")
        except Exception as e:
            self.print_error(f"OAuth服务方法测试失败: {str(e)}")
    
    async def test_oauth_flow_simulation(self):
        """模拟OAuth流程测试"""
        self.print_separator("OAuth流程模拟测试")
        
        # 模拟GitHub OAuth流程
        self.print_info("模拟GitHub OAuth流程:")
        
        # 1. 检查登录URL
        try:
            response = await self.session.get(f"{self.base_url}/api/v1/oauth/github/login", follow_redirects=False)
            if response.status_code == 302:
                github_auth_url = response.headers.get('location', '')
                self.print_success("GitHub授权URL生成成功")
                
                # 解析URL参数
                parsed_url = urlparse(github_auth_url)
                query_params = parse_qs(parsed_url.query)
                
                required_params = ['client_id', 'redirect_uri', 'scope']
                for param in required_params:
                    if param in query_params:
                        self.print_success(f"GitHub授权URL包含必要参数: {param}")
                    else:
                        self.print_error(f"GitHub授权URL缺少必要参数: {param}")
            else:
                self.print_error(f"GitHub登录端点返回错误状态码: {response.status_code}")
        except Exception as e:
            self.print_error(f"GitHub OAuth流程模拟失败: {str(e)}")
        
        # 模拟Google OAuth流程
        self.print_info("模拟Google OAuth流程:")
        
        try:
            response = await self.session.get(f"{self.base_url}/api/v1/oauth/google/login", follow_redirects=False)
            if response.status_code == 302:
                google_auth_url = response.headers.get('location', '')
                self.print_success("Google授权URL生成成功")
                
                # 解析URL参数
                parsed_url = urlparse(google_auth_url)
                query_params = parse_qs(parsed_url.query)
                
                required_params = ['client_id', 'redirect_uri', 'scope']
                for param in required_params:
                    if param in query_params:
                        self.print_success(f"Google授权URL包含必要参数: {param}")
                    else:
                        self.print_error(f"Google授权URL缺少必要参数: {param}")
            else:
                self.print_error(f"Google登录端点返回错误状态码: {response.status_code}")
        except Exception as e:
            self.print_error(f"Google OAuth流程模拟失败: {str(e)}")
    
    async def test_oauth_error_handling(self):
        """测试OAuth错误处理"""
        self.print_separator("OAuth错误处理测试")
        
        # 测试无效的回调
        try:
            response = await self.session.get(f"{self.base_url}/api/v1/oauth/github/callback?error=access_denied")
            if response.status_code == 400:
                self.print_success("GitHub OAuth错误处理正常")
            else:
                self.print_warning(f"GitHub OAuth错误处理返回状态码: {response.status_code}")
        except Exception as e:
            self.print_error(f"GitHub OAuth错误处理测试失败: {str(e)}")
        
        try:
            response = await self.session.get(f"{self.base_url}/api/v1/oauth/google/callback?error=access_denied")
            if response.status_code == 400:
                self.print_success("Google OAuth错误处理正常")
            else:
                self.print_warning(f"Google OAuth错误处理返回状态码: {response.status_code}")
        except Exception as e:
            self.print_error(f"Google OAuth错误处理测试失败: {str(e)}")
    
    async def run_all_tests(self):
        """运行所有测试"""
        self.print_separator("开始OAuth测试")
        
        # 检查服务器是否运行
        try:
            response = await self.session.get(f"{self.base_url}/docs")
            if response.status_code == 200:
                self.print_success("FastAPI服务器正在运行")
            else:
                self.print_warning(f"FastAPI服务器返回状态码: {response.status_code}")
        except Exception as e:
            self.print_error(f"无法连接到FastAPI服务器: {str(e)}")
            self.print_info("请确保服务器正在运行: python main.py")
            return
        
        # 运行所有测试
        await self.test_config()
        await self.test_oauth_endpoints()
        await self.test_oauth_login_urls()
        await self.test_oauth_providers_endpoint()
        await self.test_database_oauth_models()
        await self.test_oauth_service_methods()
        await self.test_oauth_flow_simulation()
        await self.test_oauth_error_handling()
        
        self.print_separator("OAuth测试完成")
        self.print_info("测试完成！请检查上述结果以了解OAuth配置状态。")


async def main():
    """主函数"""
    print("🚀 OAuth测试工具")
    print("测试Google和GitHub OAuth功能")
    
    async with OAuthTester() as tester:
        await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
