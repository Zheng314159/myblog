from datetime import datetime
from typing import Optional, List, TYPE_CHECKING, Any
from pydantic import BaseModel
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum
from sqlalchemy import Column, DateTime, ForeignKey, Index, Text, func
from sqlalchemy.dialects.postgresql import TSVECTOR
from app.core.config import settings
from app.core.base import BaseModelMixin
from app.models.fts import get_fts_columns 

if TYPE_CHECKING:
    from .user import User
    from .comment import Comment
    from .tag import ArticleTag
    
# IS_POSTGRES = settings.is_postgres
fts = get_fts_columns(settings.is_postgres)

class ArticleStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class ArticleBase:
    title: Mapped[str] = mapped_column(index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str|None] = mapped_column(Text, nullable=True, comment="文章摘要")
    status: Mapped[ArticleStatus] = mapped_column(default=ArticleStatus.DRAFT)
    is_featured: Mapped[bool] = mapped_column(default=False)
    # LaTeX支持
    has_latex: Mapped[bool] = mapped_column(default=False, comment="是否包含LaTeX内容")
    latex_content: Mapped[Optional[str]] = mapped_column(default=None,nullable=True, comment="LaTeX内容")


class Article(ArticleBase, BaseModelMixin):
    __tablename__ = "article"
    id: Mapped[int] = mapped_column(default=None, primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    published_at: Mapped[Optional[datetime]] = mapped_column(default=None, nullable=True, comment="发布时间")
    view_count: Mapped[int] = mapped_column(default=0, comment="浏览量")

    # ✅ 永远声明字段，避免 Alembic 忽略字段变化
    # Full-text search columns (手动注入 Column 类型)
    tsv_zh = fts["tsv_zh"]
    tsv_en = fts["tsv_en"]

    __table_args__ = tuple(fts["indexes"])  # 添加 GIN 索引（仅 PostgreSQL 下有效）
    # print(f"🧪 IS_POSTGRES={settings.is_postgres}, DB={settings.database_url}")

    # relationships
    author: Mapped[Optional["User"]] = relationship(back_populates="articles")
    comments: Mapped[List["Comment"]] = relationship(back_populates="article")
    tags: Mapped[List["ArticleTag"]] = relationship(back_populates="article")


