from datetime import datetime, timedelta
from typing import Optional, Union, Annotated
import logging
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.database import get_db, async_session
from app.models.user import User, UserRole

# Configure logging
logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire, "type": "access"})
    logger.info(f"Creating access token with data: {to_encode}")
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    logger.info(f"Access token created: {encoded_jwt[:20]}...")
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    logger.info(f"Creating refresh token with data: {to_encode}")
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    logger.info(f"Refresh token created: {encoded_jwt[:20]}...")
    return encoded_jwt


def create_password_reset_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create password reset token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)  # 24 hours default
    
    to_encode.update({"exp": expire, "type": "password_reset"})
    logger.info(f"Creating password reset token with data: {to_encode}")
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    logger.info(f"Password reset token created: {encoded_jwt[:20]}...")
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Verify and decode token"""
    try:
        logger.info(f"Verifying token: {token[:20]}...")
        logger.info(f"Using secret key: {settings.secret_key[:20]}...")
        logger.info(f"Using algorithm: {settings.algorithm}")
        
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        logger.info(f"Token verification successful: {payload}")
        return payload
    except JWTError as e:
        logger.error(f"Token verification failed: {e}")
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current user from token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = verify_token(credentials.credentials)
        if payload is None:
            raise credentials_exception
        
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        token_type = payload.get("type")
        if token_type != "access":
            raise credentials_exception
        
    except JWTError:
        raise credentials_exception
    
    result = await db.execute(select(User).where(getattr(User, "username") == username))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_user_ws(token: str) -> Optional[User]:
    """Get current user from token for WebSocket connections"""
    try:
        payload = verify_token(token)
        if payload is None:
            return None
        username: str = payload.get("sub")
        if username is None:
            return None
        token_type = payload.get("type")
        if token_type != "access":
            return None
        # 查数据库获取用户
        async with async_session() as db:
            result = await db.execute(select(User).where(User.username == username))
            user = result.scalar_one_or_none()
            return user
    except JWTError:
        return None


async def require_admin(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    """Require admin role"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def require_moderator(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    """Require moderator or admin role"""
    if current_user.role not in [UserRole.MODERATOR, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Moderator access required"
        )
    return current_user 