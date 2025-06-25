#!/usr/bin/env python3
"""
Redis 连接测试脚本
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.append(str(Path(__file__).parent))

async def test_redis_connection():
    """测试 Redis 异步连接"""
    try:
        from app.core.redis import redis_manager
        
        print("🔍 测试 Redis 异步连接...")
        
        # 连接 Redis
        await redis_manager.connect()
        print("✅ Redis 连接成功")
        
        # 测试基本操作
        await redis_manager.set("test_key", "test_value", expire=60)
        print("✅ Redis 写入测试成功")
        
        value = await redis_manager.get("test_key")
        print(f"✅ Redis 读取测试成功: {value}")
        
        exists = await redis_manager.exists("test_key")
        print(f"✅ Redis 存在检查成功: {exists}")
        
        await redis_manager.delete("test_key")
        print("✅ Redis 删除测试成功")
        
        # 断开连接
        await redis_manager.disconnect()
        print("✅ Redis 断开连接成功")
        
        return True
        
    except Exception as e:
        print(f"❌ Redis 测试失败: {e}")
        return False

async def test_sync_redis():
    """测试同步 Redis 连接"""
    try:
        import redis
        
        print("🔍 测试 Redis 同步连接...")
        
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✅ Redis 同步连接成功")
        
        # 测试基本操作
        r.set("sync_test_key", "sync_test_value", ex=60)
        print("✅ Redis 同步写入测试成功")
        
        value = r.get("sync_test_key")
        print(f"✅ Redis 同步读取测试成功: {value}")
        
        exists = r.exists("sync_test_key")
        print(f"✅ Redis 同步存在检查成功: {exists}")
        
        r.delete("sync_test_key")
        print("✅ Redis 同步删除测试成功")
        
        return True
        
    except Exception as e:
        print(f"❌ Redis 同步测试失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("🧪 Redis 连接测试")
    print("=" * 40)
    
    # 测试同步连接
    sync_result = await test_sync_redis()
    
    print()
    
    # 测试异步连接
    async_result = await test_redis_connection()
    
    print("\n" + "=" * 40)
    if sync_result and async_result:
        print("🎉 所有 Redis 测试通过！")
        print("✅ 同步 Redis 连接正常")
        print("✅ 异步 Redis 连接正常")
        print("✅ redis[async] 包工作正常")
    else:
        print("❌ 部分 Redis 测试失败")
        if not sync_result:
            print("❌ 同步 Redis 连接失败")
        if not async_result:
            print("❌ 异步 Redis 连接失败")

if __name__ == "__main__":
    asyncio.run(main()) 