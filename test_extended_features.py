#!/usr/bin/env python3
"""
测试扩展功能：文章管理、文件上传、评论系统、WebSocket
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000/api/v1"


class ExtendedFeaturesTester:
    def __init__(self):
        self.session = None
        self.access_token = None
        self.refresh_token = None
        self.test_user = {
            "username": "testuser_extended",
            "email": "test_extended@example.com",
            "password": "testpass123",
            "full_name": "Test User Extended"
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
            self.refresh_token = response.get("refresh_token")
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
            self.refresh_token = response.get("refresh_token")
            print("✅ 用户登录成功")
            return True
        else:
            print(f"❌ 用户登录失败: {status} - {response}")
            return False
    
    async def test_tag_management(self):
        """测试标签管理"""
        print("🏷️ 测试标签管理...")
        
        # 获取标签列表
        response, status = await self.make_request("GET", "/tags")
        if status == 200:
            print(f"✅ 获取标签列表成功，共 {len(response)} 个标签")
        else:
            print(f"❌ 获取标签列表失败: {status}")
        
        # 获取热门标签
        response, status = await self.make_request("GET", "/tags/popular")
        if status == 200:
            print(f"✅ 获取热门标签成功，共 {len(response)} 个标签")
        else:
            print(f"❌ 获取热门标签失败: {status}")
    
    async def test_article_management(self):
        """测试文章管理"""
        print("📝 测试文章管理...")
        
        # 创建文章
        article_data = {
            "title": "测试文章标题",
            "content": "# 测试文章\n\n这是一个测试文章的内容，支持 **Markdown** 格式。\n\n## 功能特性\n\n- 富文本编辑\n- 文件上传\n- 评论系统\n- 实时通知",
            "summary": "这是一个测试文章的摘要",
            "status": "published",
            "tags": ["测试", "技术", "博客"]
        }
        
        response, status = await self.make_request("POST", "/articles", article_data)
        if status == 200:
            article_id = response.get("id")
            print(f"✅ 创建文章成功，ID: {article_id}")
            
            # 获取文章详情
            response, status = await self.make_request("GET", f"/articles/{article_id}")
            if status == 200:
                print("✅ 获取文章详情成功")
            else:
                print(f"❌ 获取文章详情失败: {status}")
            
            # 更新文章
            update_data = {
                "title": "更新后的测试文章标题",
                "content": "# 更新后的测试文章\n\n内容已更新！",
                "tags": ["测试", "技术", "博客", "更新"]
            }
            
            response, status = await self.make_request("PUT", f"/articles/{article_id}", update_data)
            if status == 200:
                print("✅ 更新文章成功")
            else:
                print(f"❌ 更新文章失败: {status}")
            
            return article_id
        else:
            print(f"❌ 创建文章失败: {status} - {response}")
            return None
    
    async def test_comment_system(self, article_id):
        """测试评论系统"""
        if not article_id:
            print("⚠️ 跳过评论测试，文章ID无效")
            return
        
        print("💬 测试评论系统...")
        
        # 创建评论
        comment_data = {
            "content": "这是一条测试评论！",
            "parent_id": None
        }
        
        response, status = await self.make_request("POST", f"/articles/{article_id}/comments", comment_data)
        if status == 200:
            comment_id = response.get("id")
            print(f"✅ 创建评论成功，ID: {comment_id}")
            
            # 获取文章评论
            response, status = await self.make_request("GET", f"/articles/{article_id}/comments")
            if status == 200:
                print(f"✅ 获取文章评论成功，共 {len(response)} 条评论")
            else:
                print(f"❌ 获取文章评论失败: {status}")
            
            # 创建回复评论
            reply_data = {
                "content": "这是对第一条评论的回复！",
                "parent_id": comment_id
            }
            
            response, status = await self.make_request("POST", f"/articles/{article_id}/comments", reply_data)
            if status == 200:
                print("✅ 创建回复评论成功")
            else:
                print(f"❌ 创建回复评论失败: {status}")
            
            return comment_id
        else:
            print(f"❌ 创建评论失败: {status} - {response}")
            return None
    
    async def test_file_upload(self):
        """测试文件上传"""
        print("📁 测试文件上传...")
        
        # 创建测试图片文件 (简单的PNG文件)
        test_image_path = "test_image.png"
        # 创建一个最小的PNG文件
        png_header = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x07tIME\x07\xe5\x06\x19\x10\x1d\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xf5\xd7\xd4\xc4\x00\x00\x00\x00IEND\xaeB`\x82'
        
        with open(test_image_path, "wb") as f:
            f.write(png_header)
        
        try:
            # 模拟文件上传
            url = f"{BASE_URL}/articles/upload-image"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            with open(test_image_path, "rb") as f:
                data = aiohttp.FormData()
                data.add_field('file', f, filename='test_image.png', content_type='image/png')
                
                async with self.session.post(url, data=data, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        print(f"✅ 文件上传成功: {result.get('filename')}")
                    else:
                        print(f"❌ 文件上传失败: {response.status}")
        except Exception as e:
            print(f"❌ 文件上传测试失败: {e}")
        finally:
            # 清理测试文件
            if os.path.exists(test_image_path):
                os.remove(test_image_path)
    
    async def test_websocket_status(self):
        """测试WebSocket状态"""
        print("🔌 测试WebSocket状态...")
        response, status = await self.make_request("GET", "/ws/status")
        if status == 200:
            print(f"✅ WebSocket状态检查成功")
            print(f"   连接用户数: {response.get('connected_users_count', 0)}")
            print(f"   活跃频道数: {len(response.get('active_channels', []))}")
        else:
            print(f"❌ WebSocket状态检查失败: {status}")
    
    async def test_article_listing(self):
        """测试文章列表"""
        print("📋 测试文章列表...")
        
        # 获取文章列表
        response, status = await self.make_request("GET", "/articles")
        if status == 200:
            print(f"✅ 获取文章列表成功，共 {len(response)} 篇文章")
        else:
            print(f"❌ 获取文章列表失败: {status}")
        
        # 测试搜索功能
        response, status = await self.make_request("GET", "/articles?search=测试")
        if status == 200:
            print(f"✅ 文章搜索成功，找到 {len(response)} 篇文章")
        else:
            print(f"❌ 文章搜索失败: {status}")
        
        # 测试标签过滤
        response, status = await self.make_request("GET", "/articles?tag=测试")
        if status == 200:
            print(f"✅ 标签过滤成功，找到 {len(response)} 篇文章")
        else:
            print(f"❌ 标签过滤失败: {status}")
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("🧪 扩展功能测试开始")
        print("=" * 50)
        
        # 健康检查
        if not await self.test_health_check():
            print("❌ 系统未启动，请先启动服务器")
            return
        
        # 用户认证
        if not await self.test_user_registration():
            print("❌ 用户认证失败，停止测试")
            return
        
        # 标签管理
        await self.test_tag_management()
        
        # 文章管理
        article_id = await self.test_article_management()
        
        # 评论系统
        await self.test_comment_system(article_id)
        
        # 文件上传
        await self.test_file_upload()
        
        # WebSocket状态
        await self.test_websocket_status()
        
        # 文章列表
        await self.test_article_listing()
        
        print("=" * 50)
        print("🎉 扩展功能测试完成！")


async def main():
    """主函数"""
    async with ExtendedFeaturesTester() as tester:
        await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main()) 