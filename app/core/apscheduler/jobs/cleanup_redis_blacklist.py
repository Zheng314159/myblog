import logging

logger = logging.getLogger(__name__)


async def cleanup_redis_blacklist():
    from app.core.redis import redis_manager    
    """清理 Redis 中已过期的黑名单"""
    try:
        logger.info("开始清理 Redis 黑名单...")
        # 确保已连接
        if not redis_manager.redis:
            await redis_manager.connect()
        assert redis_manager.redis is not None, "Redis连接未建立"
        # 获取所有黑名单键
        blacklist_keys = await redis_manager.redis.keys("blacklist:*")
        if not blacklist_keys:
            logger.info("没有找到黑名单记录")
            return
        cleaned_count = 0
        for key in blacklist_keys:
            # 检查是否过期
            ttl = await redis_manager.redis.ttl(key)
            if ttl <= 0:
                await redis_manager.redis.delete(key)
                cleaned_count += 1
        logger.info(f"Redis 黑名单清理完成，清理了 {cleaned_count} 个过期记录")
    except Exception as e:
        logger.error(f"清理 Redis 黑名单失败: {e}")

def register_jobs():
    return {
        "cleanup_redis_blacklist":cleanup_redis_blacklist
    }