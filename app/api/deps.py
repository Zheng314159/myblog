from typing import Annotated, Optional
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import verify_token
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.models.user import UserRole


async def get_current_user(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> dict:
    """Get current user from request state"""
    if not hasattr(request.state, 'user'):
        raise AuthenticationError("User not authenticated")
    return request.state.user


async def get_current_active_user(
    current_user: Annotated[dict, Depends(get_current_user)]
) -> dict:
    """Get current active user"""
    if not current_user.get("is_active", True):
        raise AuthenticationError("Inactive user")
    return current_user


def require_role(required_role: UserRole):
    """Dependency to require specific role"""
    async def role_checker(
        current_user: Annotated[dict, Depends(get_current_active_user)]
    ) -> dict:
        user_role = current_user.get("role")
        if user_role != required_role.value and user_role != UserRole.ADMIN.value:
            raise AuthorizationError(f"Requires {required_role.value} role")
        return current_user
    return role_checker


def require_admin():
    """Dependency to require admin role"""
    return require_role(UserRole.ADMIN)


def require_moderator():
    """Dependency to require moderator role"""
    return require_role(UserRole.MODERATOR) 