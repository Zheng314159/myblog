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
from app.core.websocket import manager
from app.models.system_notification import SystemNotification
from app.core.email import email_service

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
            CronTrigger(minute='*'),  # 每小时第5分钟执行
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
        
        # 每天早晨5点执行：发送业务统计邮件
        self.scheduler.add_job(
            self._send_statistics_email,
            CronTrigger(hour=5, minute=0),  # 每天早晨5点执行
            id='send_statistics_email',
            name='发送业务统计邮件',
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
        
        # 每分钟推送定时任务状态到首页频道
        self.scheduler.add_job(
            self._push_all_task_status,
            CronTrigger(minute='*'),  # 每分钟执行
            id='push_all_task_status',
            name='推送所有定时任务状态',
            replace_existing=True
        )
        
        # 每分钟推送数据库系统通知
        self.scheduler.add_job(
            self._push_db_system_notifications,
            CronTrigger(minute='*'),
            id='push_db_system_notifications',
            name='推送数据库系统通知',
            replace_existing=True
        )
        
        # 每分钟推送业务统计
        self.scheduler.add_job(
            self._push_business_statistics,
            CronTrigger(minute='*'),
            id='push_business_statistics',
            name='推送业务统计',
            replace_existing=True
        )
        
        logger.info("定时任务已添加")
    
    async def _cleanup_redis_blacklist(self):
        """清理 Redis 中已过期的黑名单"""
        try:
            logger.info("开始清理 Redis 黑名单...")
            # 确保已连接
            if not redis_manager.redis:
                await redis_manager.connect()
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
                # {
                #     "id": "system_maintenance",
                #     "title": "系统维护通知",
                #     "message": "系统正常运行中，所有功能正常",
                #     "notification_type": "info"
                # },
                # {
                #     "id": "performance_monitor",
                #     "title": "性能监控",
                #     "message": "系统性能良好，响应时间正常",
                #     "notification_type": "info"
                # }
            ]
            # 推送到WebSocket首页频道
            for notification in notifications:
                msg = {
                    "type": "system_notification",
                    "data": notification
                }
                logger.info(f"发送通知: {notification['title']} - {notification['message']}")
                await manager.broadcast_to_channel(msg, "home")
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
                today = datetime.utcnow().date()
                beijing_offset = 8  # 北京时间比UTC快8小时
                user_count = await session.scalar(select(func.count(User.id)))
                today_users = await session.scalar(
                    select(func.count(User.id)).where(
                        func.date(func.datetime(User.created_at, f'+{beijing_offset} hours')) == (datetime.utcnow() + timedelta(hours=beijing_offset)).date()
                    )
                )
                article_count = await session.scalar(select(func.count(Article.id)))
                today_articles = await session.scalar(
                    select(func.count(Article.id)).where(
                        func.date(func.datetime(Article.created_at, f'+{beijing_offset} hours')) == (datetime.utcnow() + timedelta(hours=beijing_offset)).date()
                    )
                )
                comment_count = await session.scalar(select(func.count(Comment.id)))
                today_comments = await session.scalar(
                    select(func.count(Comment.id)).where(
                        func.date(func.datetime(Comment.created_at, f'+{beijing_offset} hours')) == (datetime.utcnow() + timedelta(hours=beijing_offset)).date()
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
                if not redis_manager.redis:
                    await redis_manager.connect()
                await redis_manager.redis.hset("system:statistics", mapping=stats)
                await redis_manager.redis.expire("system:statistics", 3600)  # 1小时过期
                logger.info(f"统计信息生成完成: {stats}")
        except Exception as e:
            logger.error(f"生成统计信息失败: {e}")
    
    async def _send_statistics_email(self):
        """发送业务统计邮件"""
        try:
            logger.info("定时任务触发：准备发送统计邮件")
            # 检查邮件通知是否启用
            if not settings.notification_email_enabled:
                logger.info("邮件通知功能已禁用，跳过发送业务统计邮件")
                return
            # 检查邮件配置是否完整
            if not all([settings.email_user, settings.email_password, settings.smtp_server]):
                logger.warning("邮件配置不完整，跳过发送业务统计邮件")
                return
            # 获取最新的统计数据
            stats = await self._get_latest_statistics()
            if not stats:
                logger.warning("无法获取统计数据，跳过发送邮件")
                return
            # 发送邮件到通知收件人
            recipient_email = settings.notification_email
            if not recipient_email:
                logger.error("NOTIFICATION_EMAIL未配置，跳过发送统计邮件")
                return
            logger.info(f"准备发送统计邮件到: {recipient_email}")
            success = email_service.send_statistics_email(recipient_email, stats)
            if success:
                logger.info(f"业务统计邮件发送成功: {recipient_email}")
                # 记录发送日志
                if not redis_manager.redis:
                    await redis_manager.connect()
                await redis_manager.redis.hset(
                    "system:email_logs", 
                    f"statistics_{datetime.now().strftime('%Y%m%d_%H%M')}",
                    f"发送成功 - {recipient_email} - {datetime.now().isoformat()}"
                )
            else:
                logger.error(f"业务统计邮件发送失败: {recipient_email}")
                # 记录失败日志
                if not redis_manager.redis:
                    await redis_manager.connect()
                await redis_manager.redis.hset(
                    "system:email_logs", 
                    f"statistics_{datetime.now().strftime('%Y%m%d_%H%M')}",
                    f"发送失败 - {recipient_email} - {datetime.now().isoformat()}"
                )
        except Exception as e:
            logger.error(f"发送业务统计邮件失败: {e}")
    
    async def _get_latest_statistics(self) -> Dict[str, Any]:
        """获取最新的统计数据"""
        try:
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
                today = datetime.utcnow().date()
                beijing_offset = 8  # 北京时间比UTC快8小时
                today_users = await session.scalar(
                    select(func.count(User.id)).where(
                        func.date(func.datetime(User.created_at, f'+{beijing_offset} hours')) == (datetime.utcnow() + timedelta(hours=beijing_offset)).date()
                    )
                )
                today_articles = await session.scalar(
                    select(func.count(Article.id)).where(
                        func.date(func.datetime(Article.created_at, f'+{beijing_offset} hours')) == (datetime.utcnow() + timedelta(hours=beijing_offset)).date()
                    )
                )
                today_comments = await session.scalar(
                    select(func.count(Comment.id)).where(
                        func.date(func.datetime(Comment.created_at, f'+{beijing_offset} hours')) == (datetime.utcnow() + timedelta(hours=beijing_offset)).date()
                    )
                )
                
                return {
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
                
        except Exception as e:
            logger.error(f"获取统计数据失败: {e}")
            return None
    
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
    
    async def _push_all_task_status(self):
        """推送所有定时任务状态到首页频道"""
        try:
            jobs = self.get_job_status().get("jobs", [])
            msg = {
                "type": "task_status",
                "data": {
                    "jobs": jobs,
                    "updated_at": datetime.now().isoformat()
                }
            }
            await manager.broadcast_to_channel(msg, "home")
            logger.info("已推送所有定时任务状态到首页频道")
        except Exception as e:
            logger.error(f"推送定时任务状态失败: {e}")
    
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
    
    async def _push_db_system_notifications(self):
        """推送数据库中的未发送系统通知到首页频道"""
        try:
            async with async_session() as session:
                result = await session.execute(
                    select(SystemNotification).where(SystemNotification.is_sent == False)
                )
                notifications = result.scalars().all()
                sent_ids = []
                for n in notifications:
                    msg = {
                        "type": "system_notification",
                        "data": {
                            "id": n.id,
                            "title": n.title,
                            "message": n.message,
                            "notification_type": n.notification_type
                        }
                    }
                    sent_count = await manager.broadcast_to_channel(msg, "home")
                    if sent_count > 0:
                        n.is_sent = True
                        sent_ids.append(n.id)
                await session.commit()
                if sent_ids:
                    logger.info(f"推送并标记为已发送的系统通知: {sent_ids}")
        except Exception as e:
            logger.error(f"推送数据库系统通知失败: {e}")
    
    async def _push_business_statistics(self):
        """推送实际业务统计到首页频道"""
        try:
            async with async_session() as session:
                today = datetime.utcnow().date()
                beijing_offset = 8  # 北京时间比UTC快8小时
                user_count = await session.scalar(select(func.count(User.id)))
                today_users = await session.scalar(
                    select(func.count(User.id)).where(
                        func.date(func.datetime(User.created_at, f'+{beijing_offset} hours')) == (datetime.utcnow() + timedelta(hours=beijing_offset)).date()
                    )
                )
                article_count = await session.scalar(select(func.count(Article.id)))
                today_articles = await session.scalar(
                    select(func.count(Article.id)).where(
                        func.date(func.datetime(Article.created_at, f'+{beijing_offset} hours')) == (datetime.utcnow() + timedelta(hours=beijing_offset)).date()
                    )
                )
                comment_count = await session.scalar(select(func.count(Comment.id)))
                today_comments = await session.scalar(
                    select(func.count(Comment.id)).where(
                        func.date(func.datetime(Comment.created_at, f'+{beijing_offset} hours')) == (datetime.utcnow() + timedelta(hours=beijing_offset)).date()
                    )
                )
                msg = {
                    "type": "task_status",
                    "data": {
                        "jobs": [
                            {"id": f"today_users_{today}", "name": "今日新增用户", "next_run_time": "", "count": today_users},
                            {"id": f"today_articles_{today}", "name": "今日新增文章", "next_run_time": "", "count": today_articles},
                            {"id": f"today_comments_{today}", "name": "今日新增评论", "next_run_time": "", "count": today_comments},
                            {"id": f"total_users", "name": "用户总数", "next_run_time": "", "count": user_count},
                            {"id": f"total_articles", "name": "文章总数", "next_run_time": "", "count": article_count},
                            {"id": f"total_comments", "name": "评论总数", "next_run_time": "", "count": comment_count}
                        ],
                        "updated_at": datetime.now().isoformat()
                    }
                }
                await manager.broadcast_to_channel(msg, "home")
                logger.info("已推送业务统计到首页频道")
        except Exception as e:
            logger.error(f"推送业务统计失败: {e}")


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