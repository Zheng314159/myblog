import json
import logging
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from app.core.websocket import manager, notification_service
from app.core.security import get_current_user_ws
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websocket"])


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket连接端点"""
    try:
        # 接受连接
        await websocket.accept()
        
        # 等待认证消息
        auth_message = await websocket.receive_text()
        auth_data = json.loads(auth_message)
        
        # 验证用户
        user = await get_current_user_ws(auth_data.get("token"))
        if not user:
            await websocket.close(code=4001, reason="Authentication failed")
            return
        
        # 建立连接
        await manager.connect(websocket, user)
        
        # 发送连接成功消息
        await websocket.send_text(json.dumps({
            "type": "connection_established",
            "data": {
                "user_id": user.id,
                "username": user.username,
                "message": "WebSocket connection established"
            }
        }))
        
        # 处理消息
        while True:
            try:
                message = await websocket.receive_text()
                data = json.loads(message)
                
                await handle_websocket_message(user, data)
                
            except WebSocketDisconnect:
                manager.disconnect(user.id)
                break
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "data": {"message": "Internal server error"}
                }))
    
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.close(code=4000, reason="Internal error")
        except:
            pass


async def handle_websocket_message(user: User, data: dict):
    """处理WebSocket消息"""
    message_type = data.get("type")
    
    if message_type == "subscribe":
        # 订阅频道
        channel = data.get("data", {}).get("channel")
        if channel:
            manager.subscribe_to_channel(user.id, channel)
            await manager.send_personal_message({
                "type": "subscription_success",
                "data": {"channel": channel}
            }, user.id)
    
    elif message_type == "unsubscribe":
        # 取消订阅频道
        channel = data.get("data", {}).get("channel")
        if channel:
            manager.unsubscribe_from_channel(user.id, channel)
            await manager.send_personal_message({
                "type": "unsubscription_success",
                "data": {"channel": channel}
            }, user.id)
    
    elif message_type == "ping":
        # 心跳检测
        await manager.send_personal_message({
            "type": "pong",
            "data": {"timestamp": data.get("data", {}).get("timestamp")}
        }, user.id)
    
    elif message_type == "get_subscriptions":
        # 获取用户订阅列表
        subscriptions = list(manager.user_subscriptions.get(user.id, set()))
        await manager.send_personal_message({
            "type": "subscriptions_list",
            "data": {"subscriptions": subscriptions}
        }, user.id)
    
    else:
        # 未知消息类型
        await manager.send_personal_message({
            "type": "error",
            "data": {"message": f"Unknown message type: {message_type}"}
        }, user.id)


@router.get("/ws/status")
async def websocket_status():
    """获取WebSocket连接状态"""
    connected_users = manager.get_connected_users()
    channels = list(manager.channel_subscriptions.keys())
    
    return {
        "connected_users_count": len(connected_users),
        "connected_users": connected_users,
        "active_channels": channels,
        "channel_subscriptions": {
            channel: manager.get_channel_subscribers(channel)
            for channel in channels
        }
    }


@router.post("/ws/broadcast")
async def broadcast_message(
    message: dict,
    channel: Optional[str] = None,
    current_user: User = Depends(get_current_user_ws)
):
    """广播消息（管理员功能）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    if channel:
        await manager.broadcast_to_channel(message, channel)
    else:
        await manager.broadcast_to_all(message)
    
    return {"message": "Broadcast sent successfully"} 