import asyncio
import aiohttp
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"

async def test_update_article():
    """测试更新文章API"""
    async with aiohttp.ClientSession() as session:
        # 先注册用户
        register_data = {
            "username": "testuser2",
            "email": "testuser2@example.com",
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
            "username": "testuser2",
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
            "title": "测试更新文章",
            "content": "这是原始内容",
            "summary": "原始摘要",
            "status": "published",
            "tags": ["测试"]
        }
        
        async with session.post(f"{BASE_URL}/articles", json=article_data, headers=headers) as response:
            if response.status == 200:
                result = await response.json()
                article_id = result.get("id")
                print(f"✅ 创建文章成功，ID: {article_id}")
            else:
                print(f"❌ 创建文章失败: {response.status}")
                return
        
        # 更新文章
        update_data = {
            "title": "更新后的标题",
            "content": "更新后的内容",
            "tags": ["测试", "更新"]
        }
        
        async with session.put(f"{BASE_URL}/articles/{article_id}", json=update_data, headers=headers) as response:
            print(f"更新文章响应状态: {response.status}")
            print(f"响应头: {dict(response.headers)}")
            
            if response.status == 200:
                result = await response.json()
                print(f"✅ 更新文章成功: {result.get('title')}")
            else:
                try:
                    error_text = await response.text()
                    print(f"❌ 更新文章失败: {response.status} - {error_text}")
                except:
                    print(f"❌ 更新文章失败: {response.status}")

if __name__ == "__main__":
    asyncio.run(test_update_article()) 