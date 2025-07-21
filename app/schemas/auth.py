from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.user import OAuthProvider


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: str | None = None
    user_id: int | None = None
    role: str | None = None


class LoginRequest(BaseModel):
    username: str
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    access_token: str


class OAuthAccountInfo(BaseModel):
    provider: OAuthProvider
    provider_username: Optional[str] = None
    created_at: datetime


class OAuthProviderInfo(BaseModel):
    name: str
    display_name: str
    login_url: str


class OAuthAccountsResponse(BaseModel):
    accounts: List[OAuthAccountInfo]


class OAuthProvidersResponse(BaseModel):
    providers: List[OAuthProviderInfo]


class OAuthBindRequest(BaseModel):
    provider: OAuthProvider


class OAuthBindResponse(BaseModel):
    message: str


class OAuthUnbindResponse(BaseModel):
    message: str 