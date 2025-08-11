import logging
from app.core.websocket import manager

logger = logging.getLogger(__name__)


async def challenge_me():
    """发送系统通知"""
    try:
        logger.info("开始发送系统通知...")
        # 模拟发送系统通知
        notifications = [
            {
                "id": "challenge_me",
                "title": "challenge me",
                "message": "挑战我，请往多媒体频道下载专著",
                "notification_type": "info"
            }
        ]
        # 推送到WebSocket首页频道
        for notification in notifications:
            msg = {
                "type": "fund_challenge",
                "data": notification
            }
            logger.info(f"发送通知: {notification['title']} - {notification['message']}")
            await manager.broadcast_to_channel(msg, "home")
        logger.info("系统通知发送完成")
    except Exception as e:
        logger.error(f"发送系统通知失败: {e}")

def register_jobs():
    return {
        "challenge_me":challenge_me
    }