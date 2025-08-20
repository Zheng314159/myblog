from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from pydantic import BaseModel
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, ForeignKey, func
from app.core.base import BaseModelMixin

if TYPE_CHECKING:
    from .article import Article


class TagBase:
    name: Mapped[str] = mapped_column(unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(default=None, nullable=True)


class Tag(TagBase,BaseModelMixin):
    __tablename__ = "tag"
    id: Mapped[int] = mapped_column(default=None, primary_key=True)
    # relationships
    article_tags: Mapped[List["ArticleTag"]] = relationship(back_populates="tag", cascade="all, delete-orphan", passive_deletes=True)


class ArticleTag(BaseModelMixin):
    """Many-to-many relationship between articles and tags"""
    __tablename__ = "article_tag"
    id: Mapped[int] = mapped_column(default=None, primary_key=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("article.id", ondelete="CASCADE"))
    tag_id: Mapped[int] = mapped_column(ForeignKey("tag.id", ondelete="CASCADE"))
    
    # relationships
    article: Mapped[Optional["Article"]] = relationship(back_populates="tags")
    tag: Mapped[Optional["Tag"]] = relationship(back_populates="article_tags")
