import logging
from app.core.websocket import manager

logger = logging.getLogger(__name__)


async def send_system_notifications():
    """发送系统通知"""
    try:
        logger.info("开始发送系统通知...")
        # 模拟发送系统通知
        notifications = [
            {
                "id": "system_maintenance",
                "title": "系统维护通知",
                "message": "系统正常运行中，所有功能正常",
                "notification_type": "info"
            },
            {
                "id": "performance_monitor",
                "title": "性能监控",
                "message": "系统性能良好，响应时间正常",
                "notification_type": "info"
            }
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

def register_jobs():
    return {
        "send_system_notifications":send_system_notifications
    }