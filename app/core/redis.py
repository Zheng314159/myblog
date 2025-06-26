from typing import Optional
import redis.asyncio as redis
from app.core.config import settings


class RedisManager:
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
    
    async def connect(self):
        """Connect to Redis"""
        self.redis = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True
        )
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis:
            await self.redis.close()
    
    async def get(self, key: str):
        """Get value from Redis"""
        if not self.redis:
            raise RuntimeError("Redis not connected")
        return await self.redis.get(key)
    
    async def set(self, key: str, value: str, expire: Optional[int] = None):
        """Set value in Redis"""
        if not self.redis:
            raise RuntimeError("Redis not connected")
        await self.redis.set(key, value, ex=expire)
    
    async def delete(self, key: str):
        """Delete key from Redis"""
        if not self.redis:
            raise RuntimeError("Redis not connected")
        await self.redis.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis"""
        if not self.redis:
            raise RuntimeError("Redis not connected")
        return await self.redis.exists(key) > 0


redis_manager = RedisManager() 