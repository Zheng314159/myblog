#!/usr/bin/env python3
"""
最终功能验证测试脚本
"""

import asyncio
import aiohttp
import json
import time
from typing import Optional

BASE_URL = "http://127.0.0.1:8000"
TIMEOUT = aiohttp.ClientTimeout(total=10)

async def test_all_features():
    """测试所有功能"""
    connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
    async with aiohttp.ClientSession(connector=connector, timeout=TIMEOUT) as session:
        print("🧪 最终功能验证测试")
        print("=" * 50)
        
        # 1. 测试健康检查
        print("🔍 测试健康检查...")
        try:
            async with session.get(f"{BASE_URL}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ 健康检查通过: {data}")
                else:
                    print(f"❌ 健康检查失败: {response.status}")
                    return
        except Exception as e:
            print(f"❌ 健康检查异常: {e}")
            return
        
        # 1.5 自动注册测试账号
        register_data = {
            "username": "admin_scheduler",
            "email": "admin_scheduler@example.com",
            "password": "adminpass123",
            "full_name": "Scheduler Admin",
            "role": "admin"
        }
        try:
            async with session.post(f"{BASE_URL}/api/v1/auth/register", json=register_data) as response:
                if response.status == 201 or response.status == 200:
                    print("✅ 测试账号注册成功")
                elif response.status == 409:
                    print("ℹ️ 测试账号已存在，继续测试")
                else:
                    print(f"❌ 测试账号注册失败: {response.status}")
                    result = await response.json()
                    print(f"错误详情: {result}")
                    return
        except Exception as e:
            print(f"❌ 测试账号注册异常: {e}")
            return
        
        # 2. 测试用户登录
        print("\n🔐 测试用户登录...")
        login_data = {
            "username": "admin_scheduler",
            "password": "adminpass123"
        }
        
        try:
            async with session.post(f"{BASE_URL}/api/v1/auth/login", json=login_data) as response:
                if response.status == 200:
                    result = await response.json()
                    token = result.get("access_token")
                    headers = {"Authorization": f"Bearer {token}"}
                    print(f"✅ 登录成功: {result.get('token_type')} {token[:20]}...")
                else:
                    print(f"❌ 登录失败: {response.status}")
                    result = await response.json()
                    print(f"错误详情: {result}")
                    return
        except Exception as e:
            print(f"❌ 登录异常: {e}")
            return
        
        # 3. 测试调度器功能
        print("\n⏰ 测试调度器功能...")
        try:
            async with session.get(f"{BASE_URL}/api/v1/scheduler/status", headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ 调度器状态: {result.get('status')}")
                    print(f"📋 任务数量: {result.get('job_count')}")
                else:
                    print(f"❌ 获取调度器状态失败: {response.status}")
        except Exception as e:
            print(f"❌ 调度器状态检查异常: {e}")
        
        # 4. 测试搜索功能
        print("\n🔍 测试搜索功能...")
        try:
            async with session.get(f"{BASE_URL}/api/v1/search/?q=测试", headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ 搜索功能正常: 找到 {len(result)} 篇文章")
                else:
                    print(f"❌ 搜索功能失败: {response.status}")
        except Exception as e:
            print(f"❌ 搜索功能异常: {e}")
        
        # 5. 测试文章列表
        print("\n📝 测试文章列表...")
        try:
            async with session.get(f"{BASE_URL}/api/v1/articles/", headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ 文章列表正常: 共 {len(result)} 篇文章")
                else:
                    print(f"❌ 文章列表失败: {response.status}")
        except Exception as e:
            print(f"❌ 文章列表异常: {e}")
        
        # 6. 测试标签功能
        print("\n🏷️ 测试标签功能...")
        try:
            async with session.get(f"{BASE_URL}/api/v1/tags/", headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ 标签功能正常: 共 {len(result)} 个标签")
                else:
                    print(f"❌ 标签功能失败: {response.status}")
        except Exception as e:
            print(f"❌ 标签功能异常: {e}")
        
        # 7. 测试评论功能
        print("\n💬 测试评论功能...")
        try:
            async with session.get(f"{BASE_URL}/api/v1/articles/1/comments", headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ 评论功能正常: 文章1有 {len(result)} 条评论")
                else:
                    print(f"❌ 评论功能失败: {response.status}")
        except Exception as e:
            print(f"❌ 评论功能异常: {e}")
        
        print("\n🎉 所有功能测试完成！")
        print("=" * 50)

if __name__ == "__main__":
    asyncio.run(test_all_features()) 