from typing import Optional
import redis.asyncio as redis
from app.core.config import settings


class RedisManager:
    '''
    黑名单存储规则：
        blacklist:user:<user_id>
        blacklist:ip:<ip>
        blacklist:device:<device_id>
        blacklist:token:<jti>

    普通业务存储：
        直接用 set_key/get_key/del_key 管理
        例如：
            refresh_token:<user_id>:<token>
            session:<session_id>
    '''
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
    
    async def connect(self):
        """连接 Redis"""
        if not self.redis:
            self.redis = redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
    
    async def disconnect(self):
        """断开 Redis 连接"""
        if self.redis:
            await self.redis.close()
            self.redis = None
    
    # ======================
    # 黑名单管理
    # ======================
    async def add_blacklist(self, category: str, value: str, ttl: int):
        """添加到黑名单"""
        if not self.redis:
            raise RuntimeError("Redis not connected")
        key = f"blacklist:{category}:{value}"
        await self.redis.set(key, 1, ex=ttl)

    async def exists_blacklist(self, category: str, value: str) -> bool:
        """检查是否在黑名单"""
        if not self.redis:
            raise RuntimeError("Redis not connected")
        key = f"blacklist:{category}:{value}"
        return await self.redis.exists(key) > 0

    async def remove_blacklist(self, category: str, value: str):
        """移除黑名单"""
        if not self.redis:
            raise RuntimeError("Redis not connected")
        key = f"blacklist:{category}:{value}"
        await self.redis.delete(key)

    async def is_token_blacklisted(self, token: str) -> bool:
        """检查 token 是否在黑名单"""
        if not self.redis:
            await self.connect()
        return await self.exists_blacklist("token", token)
    
    # ======================
    # 通用 Key-Value 管理
    # ======================
    async def set_key(self, key: str, value: str, expire: int|None = None):
        """存普通业务数据"""
        if not self.redis:
            raise RuntimeError("Redis not connected")
        await self.redis.set(key, value, ex=expire)

    async def get_key(self, key: str):
        """取普通业务数据"""
        if not self.redis:
            raise RuntimeError("Redis not connected")
        return await self.redis.get(key)

    async def exists_key(self, key: str):
        """取普通业务数据"""
        if not self.redis:
            raise RuntimeError("Redis not connected")
        return await self.redis.exists(key) > 0
    
    async def delete_key(self, key: str):
        """删普通业务数据"""
        if not self.redis:
            raise RuntimeError("Redis not connected")
        await self.redis.delete(key)


# 实例化
redis_manager = RedisManager()
