import asyncio
import aiohttp
import json
import time
from aiohttp import ClientTimeout

BASE_URL = "http://127.0.0.1:8000"
TIMEOUT = aiohttp.ClientTimeout(total=10)


async def test_scheduler_features():
    """测试定时任务功能"""
    connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
    async with aiohttp.ClientSession(connector=connector, timeout=TIMEOUT) as session:
        print("⏰ 测试定时任务功能")
        print("=" * 50)
        
        # 测试注册管理员用户
        print("🔐 注册管理员账户...")
        register_data = {
            "username": "admin_scheduler",
            "email": "admin_scheduler@example.com",
            "password": "adminpass123",
            "full_name": "Scheduler Admin",
            "role": "admin"
        }
        
        async with session.post(f"{BASE_URL}/api/v1/auth/register", json=register_data) as response:
            if response.status == 201:
                result = await response.json()
                print(f"✅ 注册成功: {result.get('message')}")
            elif response.status == 409:
                print("ℹ️ 用户已存在，继续测试")
            else:
                print(f"❌ 注册失败: {response.status}")
                result = await response.json()
                print(f"错误详情: {result}")
        
        # 测试登录
        print("🔐 登录管理员账户...")
        login_data = {
            "username": "admin_scheduler",
            "password": "adminpass123"
        }
        
        try:
            async with session.post(f"{BASE_URL}/api/v1/auth/login", json=login_data) as response:
                if response.status == 200:
                    result = await response.json()
                    token = result.get("access_token")
                    print(f"✅ 登录成功: {result.get('token_type')} {token[:20]}...")
                    headers = {"Authorization": f"Bearer {token}"}
                else:
                    print(f"❌ 登录失败: {response.status}")
                    result = await response.json()
                    print(f"错误详情: {result}")
                    return
        except Exception as e:
            print(f"❌ 登录请求失败: {e}")
            return
        
        # 2. 获取调度器状态
        print("\n📊 获取调度器状态...")
        try:
            async with session.get(f"{BASE_URL}/api/v1/scheduler/status", headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ 调度器状态: {result['status']}")
                    print(f"📋 任务数量: {len(result['jobs'])}")
                    
                    for job in result['jobs']:
                        print(f"   - {job['name']}: {job['trigger']}")
                        if job['next_run_time']:
                            print(f"     下次执行: {job['next_run_time']}")
                else:
                    print(f"❌ 获取状态失败: {response.status}")
        except Exception as e:
            print(f"❌ 获取状态请求失败: {e}")
        
        # 3. 获取任务列表
        print("\n📋 获取任务列表...")
        try:
            async with session.get(f"{BASE_URL}/api/v1/scheduler/jobs", headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ 任务列表获取成功")
                    print(f"📊 调度器状态: {result['status']}")
                    print(f"🔢 任务总数: {len(result['jobs'])}")
                    
                    for i, job in enumerate(result['jobs'], 1):
                        print(f"\n   {i}. {job['name']} (ID: {job['id']})")
                        print(f"      触发器: {job['trigger']}")
                        if job['next_run_time']:
                            print(f"      下次执行: {job['next_run_time']}")
                else:
                    print(f"❌ 获取任务列表失败: {response.status}")
        except Exception as e:
            print(f"❌ 获取任务列表请求失败: {e}")
        
        # 4. 测试停止调度器
        print("\n⏹️ 测试停止调度器...")
        try:
            async with session.post(f"{BASE_URL}/api/v1/scheduler/stop", headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ {result['message']}")
                else:
                    print(f"❌ 停止调度器失败: {response.status}")
        except Exception as e:
            print(f"❌ 停止调度器请求失败: {e}")
        
        # 5. 测试启动调度器
        print("\n▶️ 测试启动调度器...")
        try:
            async with session.post(f"{BASE_URL}/api/v1/scheduler/start", headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ {result['message']}")
                else:
                    print(f"❌ 启动调度器失败: {response.status}")
        except Exception as e:
            print(f"❌ 启动调度器请求失败: {e}")
        
        # 6. 验证调度器状态
        print("\n🔍 验证调度器状态...")
        try:
            async with session.get(f"{BASE_URL}/api/v1/scheduler/status", headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ 调度器状态: {result['status']}")
                    if result['status'] == 'running':
                        print("🎉 调度器运行正常！")
                    else:
                        print("⚠️ 调度器未运行")
                else:
                    print(f"❌ 验证状态失败: {response.status}")
        except Exception as e:
            print(f"❌ 验证状态请求失败: {e}")
        
        print("\n" + "=" * 50)
        print("✅ 定时任务功能测试完成")


async def test_scheduler_performance():
    """测试定时任务性能"""
    connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
    async with aiohttp.ClientSession(connector=connector, timeout=TIMEOUT) as session:
        print("\n⚡ 测试定时任务性能")
        print("=" * 50)
        
        # 登录获取 token
        login_data = {"username": "admin", "password": "admin123"}
        try:
            async with session.post(f"{BASE_URL}/api/v1/auth/login", json=login_data) as response:
                if response.status == 200:
                    result = await response.json()
                    token = result.get("access_token")
                else:
                    print("❌ 登录失败，跳过性能测试")
                    return
        except Exception as e:
            print(f"❌ 登录失败: {e}")
            return
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # 测试 API 响应时间
        endpoints = [
            ("/api/v1/scheduler/status", "GET"),
            ("/api/v1/scheduler/jobs", "GET"),
        ]
        
        for endpoint, method in endpoints:
            print(f"\n🔍 测试 {method} {endpoint}")
            
            times = []
            for i in range(5):
                start_time = time.time()
                try:
                    if method == "GET":
                        async with session.get(f"{BASE_URL}{endpoint}", headers=headers) as response:
                            await response.json()
                    elif method == "POST":
                        async with session.post(f"{BASE_URL}{endpoint}", headers=headers) as response:
                            await response.json()
                    
                    end_time = time.time()
                    response_time = (end_time - start_time) * 1000
                    times.append(response_time)
                    
                    if response.status == 200:
                        print(f"   ✅ 第 {i+1} 次: {response_time:.2f}ms")
                    else:
                        print(f"   ❌ 第 {i+1} 次: {response.status} - {response_time:.2f}ms")
                        
                except Exception as e:
                    print(f"   ❌ 第 {i+1} 次: 请求失败 - {e}")
            
            if times:
                avg_time = sum(times) / len(times)
                min_time = min(times)
                max_time = max(times)
                print(f"   📊 平均: {avg_time:.2f}ms, 最小: {min_time:.2f}ms, 最大: {max_time:.2f}ms")


if __name__ == "__main__":
    print("🚀 开始测试定时任务功能...")
    
    # 测试基本功能
    asyncio.run(test_scheduler_features())
    
    # 测试性能
    asyncio.run(test_scheduler_performance())
    
    print("\n🎉 所有测试完成！") 