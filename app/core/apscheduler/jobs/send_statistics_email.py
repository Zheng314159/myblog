from datetime import datetime
import logging
from typing import Any, Dict
from zoneinfo import ZoneInfo
from sqlalchemy import func, select
from app.core.email import email_service
from app.core.config import settings
from app.core.database import async_session
from app.core.redis import redis_manager
from app.models.article import Article, ArticleStatus
from app.models.comment import Comment
from app.models.tag import Tag
from app.models.user import User

logger = logging.getLogger(__name__)


async def send_statistics_email():
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
        stats = await get_latest_statistics()
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
            assert redis_manager.redis is not None, "Redis连接未建立"
            redis_manager.redis.hset(
                "system:email_logs", 
                f"statistics_{datetime.now().strftime('%Y%m%d_%H%M')}",
                f"发送成功 - {recipient_email} - {datetime.now().isoformat()}"
            )
        else:
            logger.error(f"业务统计邮件发送失败: {recipient_email}")
            # 记录失败日志
            if not redis_manager.redis:
                await redis_manager.connect()
            assert redis_manager.redis is not None, "Redis连接未建立"
            redis_manager.redis.hset(
                "system:email_logs", 
                f"statistics_{datetime.now().strftime('%Y%m%d_%H%M')}",
                f"发送失败 - {recipient_email} - {datetime.now().isoformat()}"
            )
    except Exception as e:
        logger.error(f"发送业务统计邮件失败: {e}")

async def get_latest_statistics() -> Dict[str, Any]:
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
                    func.date(func.datetime(User.created_at, f'+{beijing_offset} hours')) == datetime.now(ZoneInfo("Asia/Shanghai")).date()
                )
            )
            today_articles = await session.scalar(
                select(func.count(Article.id)).where(
                    func.date(func.datetime(Article.created_at, f'+{beijing_offset} hours')) == datetime.now(ZoneInfo("Asia/Shanghai")).date()
                )
            )
            today_comments = await session.scalar(
                select(func.count(Comment.id)).where(
                    func.date(func.datetime(Comment.created_at, f'+{beijing_offset} hours')) == datetime.now(ZoneInfo("Asia/Shanghai")).date()
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
        return {
            "total_users": 0,
            "active_users": 0,
            "total_articles": 0,
            "published_articles": 0,
            "total_comments": 0,
            "approved_comments": 0,
            "total_tags": 0,
            "today_users": 0,
            "today_articles": 0,
            "today_comments": 0,
            "updated_at": datetime.now().isoformat()
        }
    
def register_jobs():
    return {
        "send_statistics_email":send_statistics_email
    }