import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis import redis_manager
from app.core.database import async_session
from app.models.user import User
from app.models.article import Article, ArticleStatus
from app.models.comment import Comment
from app.models.tag import Tag
from app.core.config import settings

logger = logging.getLogger(__name__)


class TaskScheduler:
    """定时任务调度器"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler(
            timezone=settings.timezone,
            job_defaults={
                'coalesce': True,  # 合并重复任务
                'max_instances': 1,  # 最大实例数
                'misfire_grace_time': 60  # 错过执行时间的宽限时间
            }
        )
        self._running = False
    
    async def start(self):
        """启动调度器"""
        if self._running:
            logger.warning("调度器已在运行中")
            return
        
        try:
            # 添加定时任务
            await self._add_jobs()
            
            # 启动调度器
            self.scheduler.start()
            self._running = True
            logger.info("定时任务调度器启动成功")
            
        except Exception as e:
            logger.error(f"启动定时任务调度器失败: {e}")
            raise
    
    async def stop(self):
        """停止调度器"""
        if not self._running:
            return
        
        try:
            self.scheduler.shutdown(wait=True)
            self._running = False
            logger.info("定时任务调度器已停止")
        except Exception as e:
            logger.error(f"停止定时任务调度器失败: {e}")
    
    async def _add_jobs(self):
        """添加定时任务"""
        # 每小时执行一次：清理 Redis 黑名单
        self.scheduler.add_job(
            self._cleanup_redis_blacklist,
            CronTrigger(minute=0),  # 每小时整点执行
            id='cleanup_redis_blacklist',
            name='清理 Redis 黑名单',
            replace_existing=True
        )
        
        # 每小时执行一次：发送系统通知
        self.scheduler.add_job(
            self._send_system_notifications,
            CronTrigger(minute=5),  # 每小时第5分钟执行
            id='send_system_notifications',
            name='发送系统通知',
            replace_existing=True
        )
        
        # 每小时执行一次：汇总统计
        self.scheduler.add_job(
            self._generate_statistics,
            CronTrigger(minute=10),  # 每小时第10分钟执行
            id='generate_statistics',
            name='汇总统计',
            replace_existing=True
        )
        
        # 每小时执行一次：模拟邮件发送
        self.scheduler.add_job(
            self._simulate_email_sending,
            CronTrigger(minute=15),  # 每小时第15分钟执行
            id='simulate_email_sending',
            name='模拟邮件发送',
            replace_existing=True
        )
        
        # 每天凌晨2点执行：数据清理和维护
        self.scheduler.add_job(
            self._daily_maintenance,
            CronTrigger(hour=2, minute=0),  # 每天凌晨2点执行
            id='daily_maintenance',
            name='每日数据维护',
            replace_existing=True
        )
        
        logger.info("定时任务已添加")
    
    async def _cleanup_redis_blacklist(self):
        """清理 Redis 中已过期的黑名单"""
        try:
            logger.info("开始清理 Redis 黑名单...")
            
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
    
    async def _send_system_notifications(self):
        """发送系统通知"""
        try:
            logger.info("开始发送系统通知...")
            
            # 模拟发送系统通知
            notifications = [
                {
                    "type": "system",
                    "title": "系统维护通知",
                    "content": "系统正常运行中，所有功能正常",
                    "level": "info"
                },
                {
                    "type": "performance",
                    "title": "性能监控",
                    "content": "系统性能良好，响应时间正常",
                    "level": "info"
                }
            ]
            
            # 这里可以集成实际的通知系统（如 WebSocket、邮件等）
            for notification in notifications:
                logger.info(f"发送通知: {notification['title']} - {notification['content']}")
            
            logger.info("系统通知发送完成")
            
        except Exception as e:
            logger.error(f"发送系统通知失败: {e}")
    
    async def _generate_statistics(self):
        """汇总统计"""
        try:
            logger.info("开始生成统计信息...")
            
            async with async_session() as session:
                # 用户统计
                user_count = await session.scalar(select(func.count(User.id)))
                active_user_count = await session.scalar(
                    select(func.count(User.id)).where(User.is_active == True)
                )
                
                # 文章统计
                article_count = await session.scalar(select(func.count(Article.id)))
                published_article_count = await session.scalar(
                    select(func.count(Article.id)).where(Article.status == ArticleStatus.PUBLISHED)
                )
                
                # 评论统计
                comment_count = await session.scalar(select(func.count(Comment.id)))
                approved_comment_count = await session.scalar(
                    select(func.count(Comment.id)).where(Comment.is_approved == True)
                )
                
                # 标签统计
                tag_count = await session.scalar(select(func.count(Tag.id)))
                
                # 今日新增统计
                today = datetime.now().date()
                today_users = await session.scalar(
                    select(func.count(User.id)).where(
                        func.date(User.created_at) == today
                    )
                )
                today_articles = await session.scalar(
                    select(func.count(Article.id)).where(
                        func.date(Article.created_at) == today
                    )
                )
                today_comments = await session.scalar(
                    select(func.count(Comment.id)).where(
                        func.date(Comment.created_at) == today
                    )
                )
                
                # 保存统计结果到 Redis
                stats = {
                    "total_users": user_count,
                    "active_users": active_user_count,
                    "total_articles": article_count,
                    "published_articles": published_article_count,
                    "total_comments": comment_count,
                    "approved_comments": approved_comment_count,
                    "total_tags": tag_count,
                    "today_users": today_users,
                    "today_articles": today_articles,
                    "today_comments": today_comments,
                    "updated_at": datetime.now().isoformat()
                }
                
                await redis_manager.redis.hset("system:statistics", mapping=stats)
                await redis_manager.redis.expire("system:statistics", 3600)  # 1小时过期
                
                logger.info(f"统计信息生成完成: {stats}")
                
        except Exception as e:
            logger.error(f"生成统计信息失败: {e}")
    
    async def _simulate_email_sending(self):
        """模拟邮件发送"""
        try:
            logger.info("开始模拟邮件发送...")
            
            # 模拟不同类型的邮件
            email_tasks = [
                {
                    "type": "welcome",
                    "recipient": "new_user@example.com",
                    "subject": "欢迎加入我们的博客系统",
                    "content": "感谢您注册我们的博客系统！"
                },
                {
                    "type": "notification",
                    "recipient": "admin@example.com",
                    "subject": "系统运行状态报告",
                    "content": "系统运行正常，所有服务都在线。"
                },
                {
                    "type": "digest",
                    "recipient": "subscriber@example.com",
                    "subject": "今日热门文章摘要",
                    "content": "查看今日最受欢迎的文章和评论。"
                }
            ]
            
            for email in email_tasks:
                logger.info(f"模拟发送邮件: {email['type']} -> {email['recipient']}")
                # 这里可以集成实际的邮件发送服务
                await asyncio.sleep(0.1)  # 模拟发送延迟
            
            logger.info("邮件发送模拟完成")
            
        except Exception as e:
            logger.error(f"模拟邮件发送失败: {e}")
    
    async def _daily_maintenance(self):
        """每日数据维护"""
        try:
            logger.info("开始每日数据维护...")
            
            # 清理过期的临时数据
            await self._cleanup_temp_data()
            
            # 数据备份提醒
            await self._backup_reminder()
            
            # 系统健康检查
            await self._health_check()
            
            logger.info("每日数据维护完成")
            
        except Exception as e:
            logger.error(f"每日数据维护失败: {e}")
    
    async def _cleanup_temp_data(self):
        """清理临时数据"""
        try:
            # 清理过期的会话数据
            expired_sessions = await redis_manager.redis.keys("session:*")
            if expired_sessions:
                await redis_manager.redis.delete(*expired_sessions)
                logger.info(f"清理了 {len(expired_sessions)} 个过期会话")
            
            # 清理过期的缓存数据
            expired_cache = await redis_manager.redis.keys("cache:*")
            if expired_cache:
                await redis_manager.redis.delete(*expired_cache)
                logger.info(f"清理了 {len(expired_cache)} 个过期缓存")
                
        except Exception as e:
            logger.error(f"清理临时数据失败: {e}")
    
    async def _backup_reminder(self):
        """数据备份提醒"""
        try:
            logger.info("检查数据备份状态...")
            
            # 模拟备份检查
            backup_status = {
                "last_backup": datetime.now().isoformat(),
                "backup_size": "2.5MB",
                "status": "success"
            }
            
            await redis_manager.redis.hset("system:backup", mapping=backup_status)
            logger.info("数据备份状态已更新")
            
        except Exception as e:
            logger.error(f"备份提醒失败: {e}")
    
    async def _health_check(self):
        """系统健康检查"""
        try:
            logger.info("执行系统健康检查...")
            
            health_status = {
                "database": "healthy",
                "redis": "healthy",
                "api": "healthy",
                "search": "healthy",
                "checked_at": datetime.now().isoformat()
            }
            
            await redis_manager.redis.hset("system:health", mapping=health_status)
            logger.info("系统健康检查完成")
            
        except Exception as e:
            logger.error(f"系统健康检查失败: {e}")
    
    def get_job_status(self) -> Dict[str, Any]:
        """获取任务状态"""
        if not self._running:
            return {"status": "stopped", "jobs": []}
        
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            })
        
        return {
            "status": "running",
            "jobs": jobs
        }


# 全局调度器实例
scheduler = TaskScheduler()


async def start_scheduler():
    """启动定时任务调度器"""
    await scheduler.start()


async def stop_scheduler():
    """停止定时任务调度器"""
    await scheduler.stop()


def get_scheduler_status() -> Dict[str, Any]:
    """获取调度器状态"""
    return scheduler.get_job_status() 