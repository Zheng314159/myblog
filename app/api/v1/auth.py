from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, create_password_reset_token, verify_token
from app.core.redis import redis_manager
from app.core.exceptions import AuthenticationError, ConflictError
from app.core.tasks import add_welcome_email_task, add_password_reset_email_task, add_verification_code_email_task
from app.models.user import User
from app.schemas.user import UserCreate
from app.schemas.auth import Token, LoginRequest, RefreshTokenRequest, LogoutRequest
from fastapi import Depends
from app.api.deps import get_current_user
from app.core.config import settings
from app.core.email import email_service
import random
import string
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["authentication"])

def generate_verification_code(length: int = 6) -> str:
    """生成验证码"""
    return ''.join(random.choices(string.digits, k=length))

class EmailRequest(BaseModel):
    email: str

@router.post("/send-verification-code")
async def send_verification_code(
    email_request: EmailRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """发送邮箱验证码"""
    if not settings.email_enabled:
        raise HTTPException(status_code=400, detail="Email verification is disabled")
    
    email = email_request.email
    
    # 检查邮箱是否已被注册
    result = await db.execute(select(User).where(User.email == email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # 生成验证码
    verification_code = generate_verification_code()
    
    # 存储验证码到Redis（5分钟有效期）
    await redis_manager.set_key(
        f"email_verification:{email}",
        verification_code,
        expire=5 * 60  # 5 minutes
    )
    
    # 发送验证码邮件
    subject = f"{settings.app_name} - 邮箱验证码"
    body = f"""
您好！

您的邮箱验证码是：{verification_code}

此验证码将在5分钟后失效。

如果您没有请求此验证码，请忽略此邮件。

祝好，
{settings.app_name} 团队
    """.strip()
    
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>邮箱验证码</title>
</head>
<body>
    <div style="max-width: 600px; margin: 0 auto; padding: 20px; font-family: Arial, sans-serif;">
        <h2 style="color: #333;">邮箱验证码</h2>
        <p>您好！</p>
        <p>您的邮箱验证码是：</p>
        <div style="background-color: #f8f9fa; padding: 20px; text-align: center; margin: 20px 0; border-radius: 5px;">
            <h1 style="color: #007bff; margin: 0; font-size: 32px; letter-spacing: 5px;">{verification_code}</h1>
        </div>
        <p><strong>注意：</strong>此验证码将在5分钟后失效。</p>
        <p>如果您没有请求此验证码，请忽略此邮件。</p>
        <hr style="margin: 30px 0;">
        <p style="color: #666; font-size: 14px;">
            祝好，<br>
            {settings.app_name} 团队
        </p>
    </div>
</body>
</html>
    """.strip()
    
    success = email_service.send_email(email, subject, body, html_body)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send verification code")
    
    return {"message": "Verification code sent successfully"}

@router.get("/config")
async def get_auth_config():
    """
    获取认证相关配置信息
    """
    # 重新加载配置以确保获取最新的EMAIL_ENABLED状态
    from app.core.config import reload_settings
    reload_settings()
    from app.core.config import settings
    
    return {
        "email_enabled": settings.email_enabled,
        "oauth_enabled": bool(settings.github_client_id or settings.google_client_id)
    }

@router.get("/me")
async def get_me(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: dict = Depends(get_current_user)
):
    """
    获取当前登录用户信息
    """
    print(f"Debug: current_user = {current_user}")
    try:
        # 从数据库获取完整的用户信息
        user_id = current_user.get("user_id") if isinstance(current_user, dict) else current_user.id
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise AuthenticationError("User not found")
        
        user_info = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value if user.role else None,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None
        }
        
        print(f"Debug: returning user_info = {user_info}")
        return user_info
    except Exception as e:
        print(f"Error in /me endpoint: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/register", response_model=Token)
async def register(
    user_data: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    background_tasks: BackgroundTasks
):
    """Register a new user"""
    # Check if user already exists
    result = await db.execute(select(User).where(User.username == user_data.username))
    if result.scalar_one_or_none():
        raise ConflictError("Username already registered")
    
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise ConflictError("Email already registered")
    
    # 如果邮箱验证开启，需要验证验证码
    if settings.email_enabled:
        verification_code = getattr(user_data, 'verification_code', None)
        if not verification_code:
            raise HTTPException(status_code=400, detail="Verification code required when email verification is enabled")
        
        # 验证验证码（这里应该从Redis中获取并验证）
        stored_code = await redis_manager.get_key(f"email_verification:{user_data.email}")
        if not stored_code or stored_code != verification_code:
            raise HTTPException(status_code=400, detail="Invalid verification code")
        
        # 验证成功后删除验证码
        await redis_manager.delete_key(f"email_verification:{user_data.email}")
    
    # Create new user
    hashed_password = get_password_hash(user_data.password or "")
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        role=user_data.role,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    # Create tokens
    access_token = create_access_token(
        data={"sub": db_user.username, "user_id": db_user.id, "role": db_user.role.value}
    )
    refresh_token = create_refresh_token(
        data={"sub": db_user.username, "user_id": db_user.id}
    )
    
    # Store refresh token in Redis
    await redis_manager.set_key(
        f"refresh_token:{db_user.id}:{refresh_token}",
        "valid",
        expire=7 * 24 * 60 * 60  # 7 days
    )
    
    # Add welcome email task to background tasks
    add_welcome_email_task(background_tasks, db_user.email, db_user.username)
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Login user"""
    # Find user by username
    result = await db.execute(select(User).where(User.username == login_data.username))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(login_data.password or "", user.hashed_password or ""):
        print("验证密码时收到登录数据：", login_data)

        raise AuthenticationError("Incorrect username or password")
    
    if not user.is_active:
        raise AuthenticationError("Inactive user")
    
    # 🚫 禁止管理员前端登录
    if user.role.value == "ADMIN":  
        raise AuthenticationError("管理员账号禁止前端登录")
    # Create tokens
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role.value}
    )
    refresh_token = create_refresh_token(
        data={"sub": user.username, "user_id": user.id}
    )
    
    # Store refresh token in Redis
    await redis_manager.set_key(
        f"refresh_token:{user.id}:{refresh_token}",
        "valid",
        expire=7 * 24 * 60 * 60  # 7 days
    )
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Refresh access token (multi-device support)"""
    # Verify refresh token
    payload = verify_token(refresh_data.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise AuthenticationError("Invalid refresh token")
    
    user_id = payload.get("user_id")
    username = payload.get("sub")
    # 多端：校验refresh_token:{user_id}:{refresh_token}
    exists = await redis_manager.exists_key(f"refresh_token:{user_id}:{refresh_data.refresh_token}")
    if not exists:
        raise AuthenticationError("Invalid refresh token")
    # Get user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise AuthenticationError("User not found or inactive")
    # Create new tokens
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role.value}
    )
    new_refresh_token = create_refresh_token(
        data={"sub": user.username, "user_id": user.id}
    )
    # 多端：存储新refresh token，不删除旧的
    await redis_manager.set_key(
        f"refresh_token:{user.id}:{new_refresh_token}",
        "valid",
        expire=7 * 24 * 60 * 60
    )
    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer"
    )


@router.post("/logout")
async def logout(logout_data: LogoutRequest):
    """Logout user and blacklist token"""
    # Add access token to blacklist
    await redis_manager.set_key(
        f"blacklist:{logout_data.access_token}",
        "revoked",
        expire=30 * 60  # 30 minutes (access token lifetime)
    )
    
    return {"message": "Successfully logged out"}


class ForgotPasswordRequest(BaseModel):
    email: str

@router.post("/forgot-password")
async def forgot_password(
    forgot_data: ForgotPasswordRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    background_tasks: BackgroundTasks
):
    """Send password reset email"""
    # Find user by email
    result = await db.execute(select(User).where(User.email == forgot_data.email))
    user = result.scalar_one_or_none()
    
    if not user:
        # Don't reveal if email exists or not for security
        return {"message": "If the email exists, a password reset link has been sent"}
    
    if not user.is_active:
        raise AuthenticationError("Inactive user")
    
    # Generate password reset token
    reset_token = create_password_reset_token(
        data={"sub": user.username, "user_id": user.id},
        expires_delta=timedelta(hours=24)
    )
    
    # Store reset token in Redis
    await redis_manager.set_key(
        f"password_reset:{user.id}",
        reset_token,
        expire=24 * 60 * 60  # 24 hours
    )
    
    # Add password reset email task to background tasks
    add_password_reset_email_task(background_tasks, user.email, user.username, reset_token)
    
    return {"message": "If the email exists, a password reset link has been sent"}


class PasswordResetRequest(BaseModel):
    token: str
    new_password: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
    verification_code: str = ""  # 可选，仅在EMAIL_ENABLED=true时需要

@router.post("/change-password")
async def change_password(
    change_data: ChangePasswordRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: dict = Depends(get_current_user)
):
    """Change password for logged-in user"""
    # Get user from database
    user_id = current_user["user_id"] if isinstance(current_user, dict) else current_user.id
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise AuthenticationError("User not found")
    
    # Verify current password
    if not verify_password(change_data.current_password or "", user.hashed_password or ""):
        raise AuthenticationError("Current password is incorrect")
    
    # Check if email verification is required
    if settings.email_enabled:
        # Email verification is enabled
        if not change_data.verification_code:
            raise AuthenticationError("Verification code is required when email verification is enabled")
        
        # Verify the verification code
        stored_code = await redis_manager.get_key(f"verification_code:{user.email}")
        if not stored_code or stored_code != change_data.verification_code:
            raise AuthenticationError("Invalid or expired verification code")
        
        # Remove the verification code after successful verification
        await redis_manager.delete_key(f"verification_code:{user.email}")
    
    # Update password
    user.hashed_password = get_password_hash(change_data.new_password)
    await db.commit()
    
    return {"message": "Password successfully changed"}


@router.post("/send-change-password-code")
async def send_change_password_code(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: dict = Depends(get_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Send verification code for password change"""
    if not settings.email_enabled:
        return {"message": "Email verification is not enabled", "email_enabled": False}
    
    # Generate verification code
    verification_code = generate_verification_code()
    
    # Store verification code in Redis (5 minutes expiry)
    user_email = current_user["email"] if isinstance(current_user, dict) else current_user.email
    await redis_manager.set_key(
        f"verification_code:{user_email}",
        verification_code,
        expire=5 * 60  # 5 minutes
    )
    
    # Send verification code email
    add_verification_code_email_task(background_tasks, user_email, verification_code)
    
    return {"message": "Verification code sent to your email", "email_enabled": True}


@router.post("/reset-password")
async def reset_password(
    reset_data: PasswordResetRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Reset password using token"""
    # Verify reset token
    payload = verify_token(reset_data.token)
    if not payload or payload.get("type") != "password_reset":
        raise AuthenticationError("Invalid or expired reset token")
    
    user_id = payload.get("user_id")
    
    # Check if reset token exists in Redis
    stored_token = await redis_manager.get_key(f"password_reset:{user_id}")
    if not stored_token or stored_token != reset_data.token:
        raise AuthenticationError("Invalid or expired reset token")
    
    # Get user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise AuthenticationError("User not found or inactive")
    
    # Update password
    user.hashed_password = get_password_hash(reset_data.new_password)
    await db.commit()
    
    # Remove reset token from Redis
    await redis_manager.delete_key(f"password_reset:{user_id}")
    
    return {"message": "Password successfully reset"}

@router.get("/users")
async def list_users(db: Annotated[AsyncSession, Depends(get_db)], role: str = Query(None)):
    query = select(User)
    if role:
        from app.models.user import UserRole
        try:
            role_enum = UserRole(role)
        except ValueError:
            return []
        query = query.where(getattr(User, "role") == role_enum.value)
    result = await db.execute(query)
    users = result.scalars().all()
    return [{"id": u.id, "username": u.username, "role": u.role} for u in users] 