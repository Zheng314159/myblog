import logging
from sqlalchemy import func, select
from app.core.websocket import manager
from app.core.database import async_session
from app.models.system_notification import SystemNotification

logger = logging.getLogger(__name__)


async def push_db_system_notifications():
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

def register_jobs():
    return {
        "push_db_system_notifications":push_db_system_notifications
    }