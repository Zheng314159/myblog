from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, ForeignKey, func
from enum import Enum
from app.core.base import BaseModelMixin

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


class User(BaseModelMixin):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    full_name: Mapped[Optional[str]] = mapped_column(default=None, nullable=True)
    role: Mapped[UserRole] = mapped_column(default=UserRole.USER)
    is_active: Mapped[bool] = mapped_column(default=True)
    hashed_password: Mapped[Optional[str]] = mapped_column(default=None, nullable=True)

    # OAuth fields
    oauth_provider: Mapped[Optional[OAuthProvider]] = mapped_column(default=None, nullable=True)
    oauth_id: Mapped[Optional[str]] = mapped_column(default=None, nullable=True)
    oauth_username: Mapped[Optional[str]] = mapped_column(default=None, nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(default=None, nullable=True)

    # relationships
    articles: Mapped[List["Article"]] = relationship(back_populates="author")
    comments: Mapped[List["Comment"]] = relationship(back_populates="author")
    media_files: Mapped[List["MediaFile"]] = relationship(back_populates="uploader")
    donations: Mapped[List["DonationRecord"]] = relationship(back_populates="user")

    @property
    def is_admin(self) -> bool:
        """判断是否管理员"""
        return self.role == UserRole.ADMIN


class OAuthAccount(BaseModelMixin):
    __tablename__ = "oauth_account"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    provider: Mapped[OAuthProvider]
    provider_user_id: Mapped[str] = mapped_column(index=True)
    provider_username: Mapped[Optional[str]] = mapped_column(default=None, nullable=True)
    access_token: Mapped[Optional[str]] = mapped_column(default=None, nullable=True)
    refresh_token: Mapped[Optional[str]] = mapped_column(default=None, nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(default=None, nullable=True)
