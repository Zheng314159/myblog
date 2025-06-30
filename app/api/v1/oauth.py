from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.oauth import oauth, OAuthService, get_proxy_config
from app.core.exceptions import AuthenticationError, ConflictError
from app.models.user import User, OAuthProvider, OAuthAccount
from app.schemas.auth import Token
from app.api.deps import get_current_user
from app.core.config import settings
import httpx

router = APIRouter(prefix="/oauth", tags=["oauth"])


@router.get("/health/google")
async def check_google_oauth_health():
    """Check Google OAuth network connectivity"""
    try:
        proxy = get_proxy_config()
        transport = httpx.AsyncHTTPTransport(proxy=proxy) if proxy else None
        
        async with httpx.AsyncClient(transport=transport, timeout=10.0) as client:
            # Test Google's OpenID configuration endpoint
            response = await client.get('https://accounts.google.com/.well-known/openid_configuration')
            if response.status_code == 200:
                return {
                    "provider": "google",
                    "status": "available",
                    "message": "Google OAuth is accessible"
                }
            else:
                return {
                    "provider": "google",
                    "status": "unavailable",
                    "message": f"Google OAuth returned status {response.status_code}"
                }
    except Exception as e:
        return {
            "provider": "google",
            "status": "unavailable",
            "message": f"Google OAuth network error: {str(e)}"
        }


@router.get("/health/github")
async def check_github_oauth_health():
    """Check GitHub OAuth network connectivity"""
    try:
        proxy = get_proxy_config()
        transport = httpx.AsyncHTTPTransport(proxy=proxy) if proxy else None
        
        async with httpx.AsyncClient(transport=transport, timeout=10.0) as client:
            # Test GitHub's API endpoint
            response = await client.get('https://api.github.com/zen')
            if response.status_code == 200:
                return {
                    "provider": "github",
                    "status": "available",
                    "message": "GitHub OAuth is accessible"
                }
            else:
                return {
                    "provider": "github",
                    "status": "unavailable",
                    "message": f"GitHub OAuth returned status {response.status_code}"
                }
    except Exception as e:
        return {
            "provider": "github",
            "status": "unavailable",
            "message": f"GitHub OAuth network error: {str(e)}"
        }


@router.get("/github/login")
async def github_login(request: Request):
    """Initiate GitHub OAuth login"""
    if not hasattr(oauth, 'github') or not oauth.github:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="GitHub OAuth not configured"
        )
    
    redirect_uri = f"{request.base_url}api/v1/oauth/github/callback"
    return await oauth.github.authorize_redirect(request, redirect_uri)


@router.get("/github/callback")
async def github_callback(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Handle GitHub OAuth callback"""
    if not hasattr(oauth, 'github') or not oauth.github:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="GitHub OAuth not configured"
        )
    
    try:
        token = await oauth.github.authorize_access_token(request)
        user_info = await OAuthService.get_github_user_info(token['access_token'])
        
        if not user_info:
            raise AuthenticationError("Failed to get user information from GitHub")
        
        # Find or create user
        user = await OAuthService.find_or_create_oauth_user(
            db=db,
            provider=OAuthProvider.GITHUB,
            provider_user_id=str(user_info['id']),
            user_info=user_info
        )
        
        # Create JWT tokens
        tokens = await OAuthService.create_oauth_tokens(user)
        
        # Redirect to frontend with tokens
        frontend_url = settings.frontend_url or "http://localhost:3000"
        return RedirectResponse(
            url=f"{frontend_url}/oauth/callback?access_token={tokens['access_token']}&refresh_token={tokens['refresh_token']}&token_type={tokens['token_type']}"
        )
        
    except Exception as e:
        raise AuthenticationError(f"GitHub OAuth failed: {str(e)}")


@router.get("/google/login")
async def google_login(request: Request):
    """Initiate Google OAuth login"""
    if not hasattr(oauth, 'google') or not oauth.google:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth not configured"
        )
    
    redirect_uri = f"{request.base_url}api/v1/oauth/google/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Handle Google OAuth callback"""
    if not hasattr(oauth, 'google') or not oauth.google:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth not configured"
        )
    
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = await OAuthService.get_google_user_info(token['access_token'])
        
        if not user_info:
            raise AuthenticationError("Failed to get user information from Google")
        
        # Find or create user
        user = await OAuthService.find_or_create_oauth_user(
            db=db,
            provider=OAuthProvider.GOOGLE,
            provider_user_id=user_info['id'],
            user_info=user_info
        )
        
        # Create JWT tokens
        tokens = await OAuthService.create_oauth_tokens(user)
        
        # Redirect to frontend with tokens
        frontend_url = settings.frontend_url or "http://localhost:3000"
        return RedirectResponse(
            url=f"{frontend_url}/oauth/callback?access_token={tokens['access_token']}&refresh_token={tokens['refresh_token']}&token_type={tokens['token_type']}"
        )
        
    except Exception as e:
        raise AuthenticationError(f"Google OAuth failed: {str(e)}")


@router.post("/bind/{provider}")
async def bind_oauth_account(
    provider: OAuthProvider,
    request: Request,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Bind OAuth account to existing user"""
    user_id = current_user.get("user_id")
    
    # Get OAuth client
    oauth_client = getattr(oauth, provider.value, None)
    if not oauth_client:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=f"{provider.value} OAuth not configured"
        )
    
    try:
        token = await oauth_client.authorize_access_token(request)
        
        if provider == OAuthProvider.GITHUB:
            user_info = await OAuthService.get_github_user_info(token['access_token'])
        elif provider == OAuthProvider.GOOGLE:
            user_info = await OAuthService.get_google_user_info(token['access_token'])
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported provider: {provider}"
            )
        
        if not user_info:
            raise AuthenticationError(f"Failed to get user information from {provider.value}")
        
        # Bind OAuth account
        success = await OAuthService.bind_oauth_account(
            db=db,
            user_id=user_id,
            provider=provider,
            provider_user_id=str(user_info.get('id')),
            user_info=user_info
        )
        
        if not success:
            raise ConflictError(f"Failed to bind {provider.value} account")
        
        return {"message": f"Successfully bound {provider.value} account"}
        
    except Exception as e:
        raise AuthenticationError(f"{provider.value} OAuth binding failed: {str(e)}")


@router.delete("/unbind/{provider}")
async def unbind_oauth_account(
    provider: OAuthProvider,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Unbind OAuth account from user"""
    user_id = current_user.get("user_id")
    
    success = await OAuthService.unbind_oauth_account(
        db=db,
        user_id=user_id,
        provider=provider
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to unbind {provider.value} account. Make sure you have another authentication method."
        )
    
    return {"message": f"Successfully unbound {provider.value} account"}


@router.get("/accounts")
async def get_oauth_accounts(
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Get user's OAuth accounts"""
    user_id = current_user.get("user_id")
    
    accounts = await OAuthService.get_user_oauth_accounts(db=db, user_id=user_id)
    
    return {
        "accounts": [
            {
                "provider": account.provider,
                "provider_username": account.provider_username,
                "created_at": account.created_at
            }
            for account in accounts
        ]
    }


@router.get("/providers")
async def get_available_providers():
    """Get available OAuth providers with network status"""
    providers = []
    
    # Check GitHub
    if hasattr(oauth, 'github') and oauth.github:
        github_health = await check_github_oauth_health()
        providers.append({
            "name": "github",
            "display_name": "GitHub",
            "login_url": "/api/v1/oauth/github/login",
            "status": github_health["status"],
            "message": github_health["message"]
        })
    
    # Check Google
    if hasattr(oauth, 'google') and oauth.google:
        google_health = await check_google_oauth_health()
        providers.append({
            "name": "google",
            "display_name": "Google",
            "login_url": "/api/v1/oauth/google/login",
            "status": google_health["status"],
            "message": google_health["message"]
        })
    
    return {"providers": providers} 