from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .article import Article


class TagBase(SQLModel):
    name: str = Field(unique=True, index=True)
    description: Optional[str] = None


class Tag(TagBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    article_tags: List["ArticleTag"] = Relationship(back_populates="tag")


class TagCreate(TagBase):
    pass


class TagUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None


class TagResponse(TagBase):
    id: int
    created_at: datetime


class ArticleTag(SQLModel, table=True):
    """Many-to-many relationship between articles and tags"""
    id: Optional[int] = Field(default=None, primary_key=True)
    article_id: int = Field(foreign_key="article.id")
    tag_id: int = Field(foreign_key="tag.id")
    
    # Relationships
    article: Optional["Article"] = Relationship(back_populates="tags")
    tag: Optional["Tag"] = Relationship(back_populates="article_tags") 