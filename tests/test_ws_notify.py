import asyncio
import websockets
import json
import httpx

# 配置
WS_URL = "ws://localhost:8000/api/v1/ws"
API_LOGIN_URL = "http://localhost:8000/api/v1/auth/login"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

async def get_admin_token():
    async with httpx.AsyncClient() as client:
        resp = await client.post(API_LOGIN_URL, json={
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD
        })
        resp.raise_for_status()
        data = resp.json()
        return data["access_token"]

async def main():
    token = await get_admin_token()
    print("admin token:", token)
    async with websockets.connect(WS_URL) as ws:
        # 认证
        await ws.send(json.dumps({"token": token}))
        print("已发送认证")
        # 订阅首页频道（可选）
        await ws.send(json.dumps({"type": "subscribe", "data": {"channel": "home"}}))
        print("已发送订阅")
        # 推送一条系统通知到首页频道
        notify = {
            "title": "测试通知",
            "message": "这是一条来自Python脚本的实时通知！",
            "notification_type": "info"
        }
        await ws.send(json.dumps({"type": "broadcast", "data": {"message": {"type": "system_notification", "data": notify}, "channel": "home"}}))
        print("已推送测试通知！")
        await asyncio.sleep(5)
        # 可选：接收服务器返回（注释掉，避免因无返回导致报错）
        # try:
        #     while True:
        #         msg = await asyncio.wait_for(ws.recv(), timeout=5)
        #         print("收到消息:", msg)
        # except asyncio.TimeoutError:
        #     pass

if __name__ == "__main__":
    asyncio.run(main()) 