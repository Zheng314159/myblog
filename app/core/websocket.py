import json
import logging
from typing import Dict, List, Set, Optional
from fastapi import WebSocket, WebSocketDisconnect
from app.models.user import User

logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        # 活跃连接: {user_id: WebSocket}
        self.active_connections: Dict[int, WebSocket] = {}
        # 用户订阅: {user_id: Set[channel]}
        self.user_subscriptions: Dict[int, Set[str]] = {}
        # 频道订阅: {channel: Set[user_id]}
        self.channel_subscriptions: Dict[str, Set[int]] = {}
    
    async def connect(self, websocket: WebSocket, user: User):
        """建立WebSocket连接"""
        # await websocket.accept()  # 已在 endpoint 处 accept，这里不再 accept
        self.active_connections[user.id] = websocket
        self.user_subscriptions[user.id] = set()
        logger.info(f"User {user.username} connected via WebSocket")
    
    def disconnect(self, user_id: int):
        """断开WebSocket连接"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        
        # 清理用户订阅
        if user_id in self.user_subscriptions:
            user_channels = self.user_subscriptions[user_id]
            for channel in user_channels:
                if channel in self.channel_subscriptions:
                    self.channel_subscriptions[channel].discard(user_id)
                    if not self.channel_subscriptions[channel]:
                        del self.channel_subscriptions[channel]
            del self.user_subscriptions[user_id]
        
        logger.info(f"User {user_id} disconnected from WebSocket")
    
    def subscribe_to_channel(self, user_id: int, channel: str):
        """用户订阅频道"""
        if user_id not in self.user_subscriptions:
            self.user_subscriptions[user_id] = set()
        
        self.user_subscriptions[user_id].add(channel)
        
        if channel not in self.channel_subscriptions:
            self.channel_subscriptions[channel] = set()
        
        self.channel_subscriptions[channel].add(user_id)
        logger.info(f"User {user_id} subscribed to channel: {channel}")
    
    def unsubscribe_from_channel(self, user_id: int, channel: str):
        """用户取消订阅频道"""
        if user_id in self.user_subscriptions:
            self.user_subscriptions[user_id].discard(channel)
        
        if channel in self.channel_subscriptions:
            self.channel_subscriptions[channel].discard(user_id)
            if not self.channel_subscriptions[channel]:
                del self.channel_subscriptions[channel]
        
        logger.info(f"User {user_id} unsubscribed from channel: {channel}")
    
    async def send_personal_message(self, message: dict, user_id: int):
        """发送个人消息"""
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to send personal message to user {user_id}: {e}")
                self.disconnect(user_id)
    
    async def broadcast_to_channel(self, message: dict, channel: str):
        """向频道广播消息，返回实际推送到的用户数"""
        if channel not in self.channel_subscriptions:
            return 0
        disconnected_users = []
        sent_count = 0
        for user_id in self.channel_subscriptions[channel]:
            if user_id in self.active_connections:
                try:
                    await self.active_connections[user_id].send_text(json.dumps(message))
                    sent_count += 1
                except Exception as e:
                    logger.error(f"Failed to send message to user {user_id} in channel {channel}: {e}")
                    disconnected_users.append(user_id)
            else:
                disconnected_users.append(user_id)
        # 清理断开的连接
        for user_id in disconnected_users:
            self.disconnect(user_id)
        return sent_count
    
    async def broadcast_to_all(self, message: dict):
        """向所有连接广播消息"""
        disconnected_users = []
        for user_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to send broadcast message to user {user_id}: {e}")
                disconnected_users.append(user_id)
        
        # 清理断开的连接
        for user_id in disconnected_users:
            self.disconnect(user_id)
    
    def get_connected_users(self) -> List[int]:
        """获取已连接用户列表"""
        return list(self.active_connections.keys())
    
    def get_channel_subscribers(self, channel: str) -> List[int]:
        """获取频道订阅者列表"""
        return list(self.channel_subscriptions.get(channel, set()))


# 创建全局连接管理器实例
manager = ConnectionManager()


class NotificationService:
    """通知服务"""
    
    @staticmethod
    async def send_comment_notification(
        article_author_id: int,
        commenter_name: str,
        article_title: str,
        comment_content: str
    ):
        """发送评论通知"""
        message = {
            "type": "comment_notification",
            "data": {
                "commenter_name": commenter_name,
                "article_title": article_title,
                "comment_content": comment_content[:100] + "..." if len(comment_content) > 100 else comment_content
            }
        }
        await manager.send_personal_message(message, article_author_id)
    
    @staticmethod
    async def send_article_published_notification(
        author_id: int,
        article_title: str
    ):
        """发送文章发布通知"""
        message = {
            "type": "article_published",
            "data": {
                "article_title": article_title
            }
        }
        await manager.send_personal_message(message, author_id)
    
    @staticmethod
    async def send_system_notification(
        user_id: int,
        title: str,
        message: str,
        notification_type: str = "info"
    ):
        """发送系统通知"""
        notification = {
            "type": "system_notification",
            "data": {
                "title": title,
                "message": message,
                "notification_type": notification_type
            }
        }
        await manager.send_personal_message(notification, user_id)
    
    @staticmethod
    async def broadcast_article_update(
        article_id: int,
        article_title: str,
        action: str
    ):
        """广播文章更新"""
        message = {
            "type": "article_update",
            "data": {
                "article_id": article_id,
                "article_title": article_title,
                "action": action  # created, updated, deleted
            }
        }
        await manager.broadcast_to_channel(message, "articles")
    
    @staticmethod
    async def broadcast_new_comment(
        article_id: int,
        article_title: str,
        commenter_name: str
    ):
        """广播新评论"""
        message = {
            "type": "new_comment",
            "data": {
                "article_id": article_id,
                "article_title": article_title,
                "commenter_name": commenter_name
            }
        }
        await manager.broadcast_to_channel(message, f"article_{article_id}")


# 创建全局通知服务实例
notification_service = NotificationService() 