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
            raise RuntimeError("Redis not connected")
        return await self.exists_blacklist("token", token)
    
    # ======================
    # 安全增强功能
    # ======================

    async def ttl_blacklist(self, category: str, value: str) -> int:
        """获取黑名单剩余 TTL（秒），不存在返回 -2"""
        if not self.redis:
            raise RuntimeError("Redis not connected")
        key = f"blacklist:{category}:{value}"
        return await self.redis.ttl(key)

    async def refresh_blacklist(self, category: str, value: str, ttl: int):
        """刷新黑名单 TTL"""
        if not self.redis:
            raise RuntimeError("Redis not connected")
        key = f"blacklist:{category}:{value}"
        if await self.redis.exists(key):
            await self.redis.expire(key, ttl)

    async def batch_add_blacklist(self, category: str, values: list[str], ttl: int):
        """批量添加到黑名单"""
        if not self.redis:
            raise RuntimeError("Redis not connected")
        pipe = self.redis.pipeline()
        for v in values:
            pipe.set(f"blacklist:{category}:{v}", 1, ex=ttl)
        await pipe.execute()

    async def batch_remove_blacklist(self, category: str, values: list[str]):
        """批量移除黑名单"""
        if not self.redis:
            raise RuntimeError("Redis not connected")
        keys = [f"blacklist:{category}:{v}" for v in values]
        if keys:
            await self.redis.delete(*keys)

    # ======================
    # 登录安全 / 反暴力破解
    # ======================
    async def incr_failed_login(self, ip: str, limit: int = 5, window: int = 300) -> bool:
        """
        登录失败计数器（基于 IP 防暴力破解）
        :param ip: 用户 IP
        :param limit: 允许失败次数
        :param window: 统计窗口时间（秒）
        :return: 是否超过限制
        """
        if not self.redis:
            raise RuntimeError("Redis not connected")
        key = f"login:fail:{ip}"
        count = await self.redis.incr(key)
        if count == 1:  # 第一次失败时设置 TTL
            await self.redis.expire(key, window)
        return count > limit

    async def reset_failed_login(self, ip: str):
        """重置 IP 的失败计数"""
        if not self.redis:
            raise RuntimeError("Redis not connected")
        key = f"login:fail:{ip}"
        await self.redis.delete(key)

    async def is_ip_blocked(self, ip: str) -> bool:
        """检查 IP 是否在黑名单"""
        return await self.exists_blacklist("ip", ip)

    async def block_ip(self, ip: str, ttl: int = 600):
        """封禁 IP 一段时间"""
        await self.add_blacklist("ip", ip, ttl)

    async def block_device(self, device_id: str, ttl: int = 600):
        """封禁设备"""
        await self.add_blacklist("device", device_id, ttl)
    
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
    async def ttl(self, key: str) -> int:
        """
        获取 key 剩余过期时间（秒）
        - 返回 -2：key 不存在
        - 返回 -1：key 存在但无过期时间
        - 返回 >=0：剩余秒数
        """
        if not self.redis:
            raise RuntimeError("Redis not connected")
        return await self.redis.ttl(key)


# 实例化
redis_manager = RedisManager()
