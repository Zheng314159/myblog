from datetime import datetime
import logging
from zoneinfo import ZoneInfo
from sqlalchemy import func, select
from app.core.websocket import manager
from app.core.database import async_session
from app.models.article import Article
from app.models.comment import Comment
from app.models.user import User

logger = logging.getLogger(__name__)


async def push_business_statistics():
    """推送实际业务统计到首页频道"""
    try:
        async with async_session() as session:
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

def register_jobs():
    return {
        "push_business_statistics":push_business_statistics
    }