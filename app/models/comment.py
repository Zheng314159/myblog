from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .article import Article
    from .user import User


class CommentBase(SQLModel):
    content: str


class Comment(CommentBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    article_id: int = Field(foreign_key="article.id")
    author_id: int = Field(foreign_key="user.id")
    parent_id: Optional[int] = Field(default=None, foreign_key="comment.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_approved: bool = Field(default=True)
    
    # Relationships
    article: Optional["Article"] = Relationship(back_populates="comments")
    author: Optional["User"] = Relationship(back_populates="comments")
    parent: Optional["Comment"] = Relationship(back_populates="replies", sa_relationship_kwargs={"remote_side": "Comment.id"})
    replies: List["Comment"] = Relationship(back_populates="parent")


class CommentCreate(CommentBase):
    parent_id: Optional[int] = None


class CommentUpdate(SQLModel):
    content: Optional[str] = None
    is_approved: Optional[bool] = None


class CommentResponse(CommentBase):
    id: int
    article_id: int
    author_id: int
    parent_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    is_approved: bool 