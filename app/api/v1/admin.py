import random
import string
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import User
from app.core.config import settings
from app.core.redis import redis_manager
from app.core.email import email_service
from app.core.database import get_db

router = APIRouter(prefix = "/admin",tags=["authentication"])


def generate_verification_code(length: int = 6) -> str:
    """生成验证码"""
    return ''.join(random.choices(string.digits, k=length))

class UsernameRequest(BaseModel):
    username: str

@router.post("/send-admin-verification-code")
async def send_verification_code(
    req: UsernameRequest,
    db: AsyncSession = Depends(get_db)
):
    """发送邮箱验证码（根据用户名查询邮箱，不在前端暴露邮箱）"""
    if not settings.email_enabled:
        raise HTTPException(status_code=400, detail="Email verification is disabled")

    username = req.username.strip()
    print(f"🐱‍🏍🐱‍🏍{username}")
    # 查找用户
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user or not user.email:
        raise HTTPException(status_code=400, detail="User not found or email not bound")

    email = user.email

    # 防止频繁请求（冷却机制，60秒内不允许重复发送）
    key = f"email_verification:{username}"
    ttl = await redis_manager.ttl(key)
    if ttl and ttl > 240:  # 还剩 4 分钟以上，就拒绝发送
        raise HTTPException(status_code=429, detail="请勿频繁请求验证码")

    # 生成验证码
    verification_code = generate_verification_code()

    # 存储验证码到 Redis
    await redis_manager.set_key(
        key,
        verification_code,
        expire=5 * 60  # 5分钟有效
    )

    # 构造邮件内容
    subject = f"{settings.app_name} - 管理后台登录验证码"
    body = f"您好 {username}，您的后台登录验证码是 {verification_code}，5分钟内有效。"
    html_body = f"""
    <div style="font-family: Arial, sans-serif;">
        <p>您好 <b>{username}</b>，</p>
        <p>您的后台登录验证码是：</p>
        <h2 style="color:#007bff;">{verification_code}</h2>
        <p>此验证码 5 分钟内有效，请尽快使用。</p>
        <p>如果不是您本人操作，请忽略。</p>
    </div>
    """

    success = email_service.send_email(email, subject, body, html_body)
    if not success:
        # 邮件发送失败时删除 Redis key
        await redis_manager.delete_key(key)
        raise HTTPException(status_code=500, detail="Failed to send verification code")

    return {"message": "Verification code sent successfully"}