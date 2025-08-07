from datetime import datetime
import logging
from zoneinfo import ZoneInfo

from sqlalchemy import func, select

from app.core.database import async_session
from app.core.redis import redis_manager
from app.models.article import Article, ArticleStatus
from app.models.comment import Comment
from app.models.tag import Tag
from app.models.user import User

logger = logging.getLogger(__name__)


async def generate_statistics():
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
                    func.date(func.datetime(User.created_at, f'+{beijing_offset} hours')) == datetime.now(ZoneInfo("Asia/Shanghai")).date()
                )
            )
            article_count = await session.scalar(select(func.count(Article.id)))
            today_articles = await session.scalar(
                select(func.count(Article.id)).where(
                    func.date(func.datetime(Article.created_at, f'+{beijing_offset} hours')) == datetime.now(ZoneInfo("Asia/Shanghai")).date()
                )
            )
            comment_count = await session.scalar(select(func.count(Comment.id)))
            today_comments = await session.scalar(
                select(func.count(Comment.id)).where(
                    func.date(func.datetime(Comment.created_at, f'+{beijing_offset} hours')) == datetime.now(ZoneInfo("Asia/Shanghai")).date()
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
            assert redis_manager.redis is not None, "Redis连接未建立"
            redis_manager.redis.hset("system:statistics", mapping=stats)
            await redis_manager.redis.expire("system:statistics", 3600)  # 1小时过期
            logger.info(f"统计信息生成完成: {stats}")
    except Exception as e:
        logger.error(f"生成统计信息失败: {e}")

def register_jobs():
    return {
        "generate_statistics": generate_statistics
    }