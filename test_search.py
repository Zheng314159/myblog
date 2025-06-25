import asyncio
import aiohttp
import json
import time
from aiohttp import ClientTimeout

BASE_URL = "http://127.0.0.1:8000/api/v1"

# 设置超时时间
TIMEOUT = ClientTimeout(total=30, connect=10)

async def test_search_features():
    """测试搜索功能"""
    connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
    async with aiohttp.ClientSession(connector=connector, timeout=TIMEOUT) as session:
        print("🔍 测试全文搜索功能")
        print("=" * 50)
        
        # 1. 初始化搜索索引
        print("📝 初始化搜索索引...")
        try:
            async with session.post(f"{BASE_URL}/search/init") as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ 搜索索引初始化成功: {result}")
                else:
                    print(f"❌ 搜索索引初始化失败: {response.status}")
                    return
        except Exception as e:
            print(f"❌ 初始化搜索索引时出错: {e}")
            return
        
        # 2. 获取搜索统计信息
        print("\n📊 获取搜索统计信息...")
        try:
            async with session.get(f"{BASE_URL}/search/stats") as response:
                if response.status == 200:
                    stats = await response.json()
                    print(f"✅ 搜索统计: {stats}")
                else:
                    print(f"❌ 获取统计信息失败: {response.status}")
        except Exception as e:
            print(f"❌ 获取统计信息时出错: {e}")
        
        # 3. 测试全文搜索
        print("\n🔎 测试全文搜索...")
        search_queries = [
            "测试",
            "技术",
            "博客",
            "FastAPI",
            "LaTeX",
            "数学公式"
        ]
        
        for query in search_queries:
            print(f"\n搜索关键词: '{query}'")
            try:
                async with session.get(f"{BASE_URL}/search/?q={query}&limit=5") as response:
                    if response.status == 200:
                        results = await response.json()
                        print(f"✅ 找到 {len(results)} 篇文章")
                        for i, article in enumerate(results[:3], 1):
                            print(f"  {i}. {article['title']} (ID: {article['id']})")
                    else:
                        print(f"❌ 搜索失败: {response.status}")
            except Exception as e:
                print(f"❌ 搜索 '{query}' 时出错: {e}")
        
        # 4. 测试搜索建议
        print("\n💡 测试搜索建议...")
        suggestion_queries = ["测试", "技术", "Fast"]
        
        for query in suggestion_queries:
            print(f"\n获取建议: '{query}'")
            try:
                async with session.get(f"{BASE_URL}/search/suggestions?q={query}&limit=3") as response:
                    if response.status == 200:
                        suggestions = await response.json()
                        print(f"✅ 建议: {suggestions['suggestions']}")
                    else:
                        print(f"❌ 获取建议失败: {response.status}")
            except Exception as e:
                print(f"❌ 获取建议时出错: {e}")
        
        # 5. 测试热门搜索
        print("\n🔥 测试热门搜索...")
        try:
            async with session.get(f"{BASE_URL}/search/popular?limit=5") as response:
                if response.status == 200:
                    popular = await response.json()
                    print(f"✅ 热门搜索词: {popular['popular_searches']}")
                else:
                    print(f"❌ 获取热门搜索失败: {response.status}")
        except Exception as e:
            print(f"❌ 获取热门搜索时出错: {e}")
        
        # 6. 测试高级搜索（带状态过滤）
        print("\n🎯 测试高级搜索（仅已发布文章）...")
        try:
            async with session.get(f"{BASE_URL}/search/?q=测试&status=published&limit=3") as response:
                if response.status == 200:
                    results = await response.json()
                    print(f"✅ 已发布文章搜索结果: {len(results)} 篇")
                    for i, article in enumerate(results, 1):
                        print(f"  {i}. {article['title']} (状态: {article['status']})")
                else:
                    print(f"❌ 高级搜索失败: {response.status}")
        except Exception as e:
            print(f"❌ 高级搜索时出错: {e}")
        
        # 7. 测试分页
        print("\n📄 测试搜索分页...")
        try:
            async with session.get(f"{BASE_URL}/search/?q=测试&skip=0&limit=2") as response:
                if response.status == 200:
                    page1 = await response.json()
                    print(f"✅ 第1页: {len(page1)} 篇文章")
        except Exception as e:
            print(f"❌ 获取第1页时出错: {e}")
        
        try:
            async with session.get(f"{BASE_URL}/search/?q=测试&skip=2&limit=2") as response:
                if response.status == 200:
                    page2 = await response.json()
                    print(f"✅ 第2页: {len(page2)} 篇文章")
        except Exception as e:
            print(f"❌ 获取第2页时出错: {e}")
        
        print("\n" + "=" * 50)
        print("🎉 搜索功能测试完成！")


async def test_search_performance():
    """测试搜索性能"""
    connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
    async with aiohttp.ClientSession(connector=connector, timeout=TIMEOUT) as session:
        print("\n⚡ 测试搜索性能")
        print("=" * 30)
        
        # 测试搜索响应时间
        queries = ["测试", "技术", "博客", "FastAPI"]
        
        for query in queries:
            start_time = time.time()
            try:
                async with session.get(f"{BASE_URL}/search/?q={query}&limit=10") as response:
                    if response.status == 200:
                        results = await response.json()
                        end_time = time.time()
                        response_time = (end_time - start_time) * 1000  # 毫秒
                        print(f"✅ '{query}' 搜索耗时: {response_time:.2f}ms, 结果: {len(results)} 篇")
                    else:
                        print(f"❌ '{query}' 搜索失败: {response.status}")
            except Exception as e:
                print(f"❌ '{query}' 搜索时出错: {e}")


if __name__ == "__main__":
    # 在 Windows 系统上使用 ProactorEventLoop
    if hasattr(asyncio, 'WindowsProactorEventLoopPolicy'):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    try:
        asyncio.run(test_search_features())
        asyncio.run(test_search_performance())
    except KeyboardInterrupt:
        print("\n⚠️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}") 