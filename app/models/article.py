from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum

if TYPE_CHECKING:
    from .user import User
    from .comment import Comment
    from .tag import ArticleTag


class ArticleStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class ArticleBase(SQLModel):
    title: str = Field(index=True)
    content: str
    summary: Optional[str] = None
    status: ArticleStatus = Field(default=ArticleStatus.DRAFT)
    is_featured: bool = Field(default=False)
    # LaTeX支持
    has_latex: bool = Field(default=False, description="是否包含LaTeX内容")
    latex_content: Optional[str] = Field(default=None, description="LaTeX内容")


class Article(ArticleBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    author_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = None
    
    # Relationships
    author: Optional["User"] = Relationship(back_populates="articles")
    comments: List["Comment"] = Relationship(back_populates="article")
    tags: List["ArticleTag"] = Relationship(back_populates="article")


class ArticleCreate(ArticleBase):
    pass


class ArticleUpdate(SQLModel):
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    status: Optional[ArticleStatus] = None
    is_featured: Optional[bool] = None
    has_latex: Optional[bool] = None
    latex_content: Optional[str] = None


class ArticleResponse(ArticleBase):
    id: int
    author_id: int
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None 