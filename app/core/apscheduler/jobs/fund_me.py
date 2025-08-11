import logging
from app.core.websocket import manager

logger = logging.getLogger(__name__)


async def fund_me():
    """发送系统通知"""
    try:
        logger.info("开始发送系统通知...")
        # 模拟发送系统通知
        notifications = [
            {
                "id": "fund_me",
                "title": "fund me",
                "message": "资助我，让我更好推动科学进步",
                "notification_type": "info"
            }
        ]
        # 推送到WebSocket首页频道
        for notification in notifications:
            msg = {
                "type": "fund_me",
                "data": notification
            }
            logger.info(f"发送通知: {notification['title']} - {notification['message']}")
            await manager.broadcast_to_channel(msg, "home")
        logger.info("系统通知发送完成")
    except Exception as e:
        logger.error(f"发送系统通知失败: {e}")

def register_jobs():
    return {
        "fund_me":fund_me
    }