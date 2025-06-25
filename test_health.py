#!/usr/bin/env python3
"""
健康检查测试脚本
"""

import asyncio
import aiohttp

async def test_health():
    """测试健康检查端点"""
    url = "http://127.0.0.1:8000/health"
    
    print(f"🔍 测试健康检查: {url}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                print(f"状态码: {response.status}")
                print(f"响应头: {dict(response.headers)}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ 健康检查成功: {data}")
                    return True
                else:
                    text = await response.text()
                    print(f"❌ 健康检查失败: {text}")
                    return False
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False

async def test_root():
    """测试根端点"""
    url = "http://127.0.0.1:8000/"
    
    print(f"\n🔍 测试根端点: {url}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                print(f"状态码: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ 根端点成功: {data}")
                    return True
                else:
                    text = await response.text()
                    print(f"❌ 根端点失败: {text}")
                    return False
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False

async def main():
    """主函数"""
    print("🧪 端点测试")
    print("=" * 40)
    
    health_result = await test_health()
    root_result = await test_root()
    
    print("\n" + "=" * 40)
    if health_result and root_result:
        print("🎉 所有端点测试通过！")
    else:
        print("❌ 部分端点测试失败")
        if not health_result:
            print("❌ 健康检查失败")
        if not root_result:
            print("❌ 根端点失败")

if __name__ == "__main__":
    asyncio.run(main()) 