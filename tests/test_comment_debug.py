import asyncio
import aiohttp
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"

async def test_comment_debug():
    """调试评论API"""
    async with aiohttp.ClientSession() as session:
        # 先注册用户
        register_data = {
            "username": "debuguser",
            "email": "debuguser@example.com",
            "password": "testpass123"
        }
        
        async with session.post(f"{BASE_URL}/auth/register", json=register_data) as response:
            if response.status == 200:
                print("✅ 用户注册成功")
            elif response.status == 409:
                print("⚠️ 用户已存在，继续登录")
            else:
                print(f"❌ 用户注册失败: {response.status}")
        
        # 登录获取token
        login_data = {
            "username": "debuguser",
            "password": "testpass123"
        }
        
        async with session.post(f"{BASE_URL}/auth/login", json=login_data) as response:
            if response.status == 200:
                result = await response.json()
                access_token = result.get("access_token")
                print(f"✅ 登录成功，token: {access_token[:20]}...")
            else:
                print(f"❌ 登录失败: {response.status}")
                return
        
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # 创建文章
        article_data = {
            "title": "调试文章",
            "content": "这是用于调试的文章",
            "summary": "调试用",
            "status": "published",
            "tags": ["调试"]
        }
        
        async with session.post(f"{BASE_URL}/articles", json=article_data, headers=headers) as response:
            if response.status == 200:
                result = await response.json()
                article_id = result.get("id")
                print(f"✅ 创建文章成功，ID: {article_id}")
            else:
                print(f"❌ 创建文章失败: {response.status}")
                return
        
        # 创建评论
        comment_data = {
            "content": "调试评论",
            "parent_id": None
        }
        
        print(f"正在创建评论，文章ID: {article_id}")
        async with session.post(f"{BASE_URL}/articles/{article_id}/comments", json=comment_data, headers=headers) as response:
            print(f"评论API响应状态: {response.status}")
            print(f"响应头: {dict(response.headers)}")
            
            try:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ 创建评论成功: {result}")
                else:
                    text = await response.text()
                    print(f"❌ 创建评论失败: {response.status}")
                    print(f"响应内容: {text}")
            except Exception as e:
                print(f"❌ 解析响应失败: {e}")
                text = await response.text()
                print(f"原始响应: {text}")

if __name__ == "__main__":
    asyncio.run(test_comment_debug()) 