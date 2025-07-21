from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum

if TYPE_CHECKING:
    from .article import Article
    from .comment import Comment
    from .media import MediaFile
    from .donation import DonationRecord


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    MODERATOR = "MODERATOR"
    USER = "USER"


class OAuthProvider(str, Enum):
    GITHUB = "github"
    GOOGLE = "google"


class UserBase(SQLModel):
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    full_name: Optional[str] = None
    role: UserRole = Field(default=UserRole.USER)
    is_active: bool = Field(default=True)


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: Optional[str] = None  # Optional for OAuth users
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # OAuth fields
    oauth_provider: Optional[OAuthProvider] = None
    oauth_id: Optional[str] = None  # External OAuth ID
    oauth_username: Optional[str] = None  # Username from OAuth provider
    avatar_url: Optional[str] = None  # Profile picture URL
    
    # Relationships
    articles: List["Article"] = Relationship(back_populates="author")
    comments: List["Comment"] = Relationship(back_populates="author")
    media_files: List["MediaFile"] = Relationship(back_populates="uploader")
    donations: List["DonationRecord"] = Relationship(back_populates="user")


class UserCreate(UserBase):
    password: Optional[str] = None  # Optional for OAuth users
    verification_code: Optional[str] = None  # Email verification code


class UserUpdate(SQLModel):
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    avatar_url: Optional[str] = None


class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    oauth_provider: Optional[OAuthProvider] = None
    avatar_url: Optional[str] = None


class OAuthAccount(SQLModel, table=True):
    """Separate table for OAuth account bindings"""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    provider: OAuthProvider
    provider_user_id: str = Field(index=True)
    provider_username: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow) 