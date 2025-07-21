from datetime import datetime
from typing import Optional, List, TYPE_CHECKING, Any
from sqlmodel import SQLModel, Field, Relationship, Text
from enum import Enum
from sqlalchemy import Column, Index
from sqlalchemy.dialects.postgresql import TSVECTOR
from app.core.config import settings    

if TYPE_CHECKING:
    from .user import User
    from .comment import Comment
    from .tag import ArticleTag
    
# IS_POSTGRES = settings.is_postgres
if settings.is_postgres:
    from app.models.fts_pg import tsv_zh_column, tsv_en_column, tsv_zh_index, tsv_en_index
else:
    tsv_zh_column = Column("tsv_zh", Text, nullable=True)
    tsv_en_column = Column("tsv_en", Text, nullable=True)
    tsv_zh_index = None
    tsv_en_index = None

class ArticleStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class ArticleBase(SQLModel):
    title: str = Field(index=True)
    content: str
    summary: str|None = None
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
    view_count: int = Field(default=0, description="浏览量")

    # ✅ 永远声明字段，避免 Alembic 忽略字段变化
    tsv_zh: Optional[str] = Field(default=None, sa_column=tsv_zh_column)
    tsv_en: Optional[str] = Field(default=None, sa_column=tsv_en_column)

    __table_args__ = tuple(filter(None, (tsv_zh_index, tsv_en_index)))
    # print(f"🧪 IS_POSTGRES={settings.is_postgres}, DB={settings.database_url}")

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