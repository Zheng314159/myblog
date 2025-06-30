import httpx
from typing import Optional, Dict, Any
from authlib.integrations.starlette_client import OAuth
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.config import settings
from app.models.user import User, OAuthProvider, OAuthAccount
from app.core.security import create_access_token, create_refresh_token
from app.core.redis import redis_manager
import os


# OAuth configuration - 直接使用settings而不是Starlette Config
oauth = OAuth()

# GitHub OAuth
if settings.github_client_id and settings.github_client_secret:
    oauth.register(
        name='github',
        client_id=settings.github_client_id,
        client_secret=settings.github_client_secret,
        access_token_url='https://github.com/login/oauth/access_token',
        access_token_params=None,
        authorize_url='https://github.com/login/oauth/authorize',
        authorize_params=None,
        api_base_url='https://api.github.com/',
        client_kwargs={'scope': 'user:email'},
    )

# Google OAuth
if settings.google_client_id and settings.google_client_secret:
    oauth.register(
        name='google',
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        access_token_url='https://oauth2.googleapis.com/token',
        access_token_params=None,
        authorize_url='https://accounts.google.com/o/oauth2/auth',
        authorize_params=None,
        api_base_url='https://www.googleapis.com/oauth2/v1/',
        client_kwargs={'scope': 'openid email profile'},
    )


def get_proxy_config():
    """获取代理配置"""
    # 使用settings中的代理配置
    if settings.https_proxy:
        return settings.https_proxy
    elif settings.http_proxy:
        return settings.http_proxy
    return None


class OAuthService:
    """OAuth authentication service"""
    
    @staticmethod
    async def get_github_user_info(token: str) -> Optional[Dict[str, Any]]:
        """Get GitHub user information from access token"""
        proxy = get_proxy_config()
        transport = httpx.AsyncHTTPTransport(proxy=proxy) if proxy else None
        
        async with httpx.AsyncClient(transport=transport, timeout=30.0) as client:
            headers = {'Authorization': f'token {token}'}
            response = await client.get('https://api.github.com/user', headers=headers)
            if response.status_code == 200:
                user_data = response.json()
                
                # Get user emails
                emails_response = await client.get('https://api.github.com/user/emails', headers=headers)
                if emails_response.status_code == 200:
                    emails = emails_response.json()
                    primary_email = next((email['email'] for email in emails if email['primary']), None)
                    user_data['email'] = primary_email
                
                return user_data
        return None
    
    @staticmethod
    async def get_google_user_info(token: str) -> Optional[Dict[str, Any]]:
        """Get Google user information from access token"""
        proxy = get_proxy_config()
        transport = httpx.AsyncHTTPTransport(proxy=proxy) if proxy else None
        
        async with httpx.AsyncClient(transport=transport, timeout=30.0) as client:
            headers = {'Authorization': f'Bearer {token}'}
            response = await client.get('https://www.googleapis.com/oauth2/v2/userinfo', headers=headers)
            if response.status_code == 200:
                return response.json()
        return None
    
    @staticmethod
    async def find_or_create_oauth_user(
        db: AsyncSession,
        provider: OAuthProvider,
        provider_user_id: str,
        user_info: Dict[str, Any]
    ) -> User:
        """Find existing OAuth user or create new one"""
        
        # First, try to find existing OAuth account
        result = await db.execute(
            select(OAuthAccount).where(
                OAuthAccount.provider == provider,
                OAuthAccount.provider_user_id == provider_user_id
            )
        )
        oauth_account = result.scalar_one_or_none()
        
        if oauth_account:
            # OAuth account exists, get the user
            result = await db.execute(select(User).where(User.id == oauth_account.user_id))
            user = result.scalar_one_or_none()
            if user:
                return user
        
        # Check if user exists by email
        email = user_info.get('email')
        if email:
            result = await db.execute(select(User).where(User.email == email))
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                # User exists, create OAuth account binding
                oauth_account = OAuthAccount(
                    user_id=existing_user.id,
                    provider=provider,
                    provider_user_id=provider_user_id,
                    provider_username=user_info.get('login') or user_info.get('name'),
                )
                db.add(oauth_account)
                await db.commit()
                return existing_user
        
        # Create new user
        username = user_info.get('login') or user_info.get('name') or f"{provider}_{provider_user_id}"
        full_name = user_info.get('name') or user_info.get('full_name')
        avatar_url = user_info.get('avatar_url') or user_info.get('picture')
        
        # Ensure username is unique
        base_username = username
        counter = 1
        while True:
            result = await db.execute(select(User).where(User.username == username))
            if not result.scalar_one_or_none():
                break
            username = f"{base_username}_{counter}"
            counter += 1
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            full_name=full_name,
            oauth_provider=provider,
            oauth_id=provider_user_id,
            oauth_username=user_info.get('login') or user_info.get('name'),
            avatar_url=avatar_url,
            hashed_password=None  # OAuth users don't have passwords
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        # Create OAuth account record
        oauth_account = OAuthAccount(
            user_id=new_user.id,
            provider=provider,
            provider_user_id=provider_user_id,
            provider_username=user_info.get('login') or user_info.get('name'),
        )
        db.add(oauth_account)
        await db.commit()
        
        return new_user
    
    @staticmethod
    async def create_oauth_tokens(user: User) -> Dict[str, str]:
        """Create JWT tokens for OAuth user"""
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
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    
    @staticmethod
    async def bind_oauth_account(
        db: AsyncSession,
        user_id: int,
        provider: OAuthProvider,
        provider_user_id: str,
        user_info: Dict[str, Any]
    ) -> bool:
        """Bind OAuth account to existing user"""
        
        # Check if OAuth account already exists
        result = await db.execute(
            select(OAuthAccount).where(
                OAuthAccount.provider == provider,
                OAuthAccount.provider_user_id == provider_user_id
            )
        )
        if result.scalar_one_or_none():
            return False  # Already bound to another account
        
        # Check if user already has this OAuth provider
        result = await db.execute(
            select(OAuthAccount).where(
                OAuthAccount.user_id == user_id,
                OAuthAccount.provider == provider
            )
        )
        if result.scalar_one_or_none():
            return False  # User already has this provider
        
        # Create OAuth account binding
        oauth_account = OAuthAccount(
            user_id=user_id,
            provider=provider,
            provider_user_id=provider_user_id,
            provider_username=user_info.get('login') or user_info.get('name'),
        )
        
        db.add(oauth_account)
        await db.commit()
        return True
    
    @staticmethod
    async def unbind_oauth_account(
        db: AsyncSession,
        user_id: int,
        provider: OAuthProvider
    ) -> bool:
        """Unbind OAuth account from user"""
        result = await db.execute(
            select(OAuthAccount).where(
                OAuthAccount.user_id == user_id,
                OAuthAccount.provider == provider
            )
        )
        oauth_account = result.scalar_one_or_none()
        
        if not oauth_account:
            return False
        
        # Check if user has password (can't unbind if no other auth method)
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if user and not user.hashed_password:
            # Check if user has other OAuth accounts
            result = await db.execute(
                select(OAuthAccount).where(OAuthAccount.user_id == user_id)
            )
            other_accounts = result.scalars().all()
            
            if len(other_accounts) <= 1:
                return False  # Can't unbind last auth method
        
        await db.delete(oauth_account)
        await db.commit()
        return True
    
    @staticmethod
    async def get_user_oauth_accounts(
        db: AsyncSession,
        user_id: int
    ) -> list[OAuthAccount]:
        """Get all OAuth accounts for a user"""
        result = await db.execute(
            select(OAuthAccount).where(OAuthAccount.user_id == user_id)
        )
        return result.scalars().all() 