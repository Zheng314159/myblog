from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, verify_token
from app.core.redis import redis_manager
from app.core.exceptions import AuthenticationError, ConflictError
from app.models.user import User, UserCreate
from app.schemas.auth import Token, LoginRequest, RefreshTokenRequest, LogoutRequest

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=Token)
async def register(
    user_data: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Register a new user"""
    # Check if user already exists
    result = await db.execute(select(User).where(User.username == user_data.username))
    if result.scalar_one_or_none():
        raise ConflictError("Username already registered")
    
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise ConflictError("Email already registered")
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
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
    await redis_manager.set(
        f"refresh_token:{db_user.id}",
        refresh_token,
        expire=7 * 24 * 60 * 60  # 7 days
    )
    
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
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise AuthenticationError("Incorrect username or password")
    
    if not user.is_active:
        raise AuthenticationError("Inactive user")
    
    # Create tokens
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role.value}
    )
    refresh_token = create_refresh_token(
        data={"sub": user.username, "user_id": user.id}
    )
    
    # Store refresh token in Redis
    await redis_manager.set(
        f"refresh_token:{user.id}",
        refresh_token,
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
    """Refresh access token"""
    # Verify refresh token
    payload = verify_token(refresh_data.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise AuthenticationError("Invalid refresh token")
    
    user_id = payload.get("user_id")
    username = payload.get("sub")
    
    # Check if refresh token exists in Redis
    stored_token = await redis_manager.get(f"refresh_token:{user_id}")
    if not stored_token or stored_token != refresh_data.refresh_token:
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
    
    # Update refresh token in Redis
    await redis_manager.set(
        f"refresh_token:{user.id}",
        new_refresh_token,
        expire=7 * 24 * 60 * 60  # 7 days
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
    await redis_manager.set(
        f"blacklist:{logout_data.access_token}",
        "revoked",
        expire=30 * 60  # 30 minutes (access token lifetime)
    )
    
    return {"message": "Successfully logged out"} 