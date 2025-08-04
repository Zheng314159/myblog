from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.base import BaseModelMixin

if TYPE_CHECKING:
    from .article import Article
    from .user import User


class Comment(BaseModelMixin):
    __tablename__ = "comment"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str]

    article_id: Mapped[int] = mapped_column(ForeignKey("article.id"))
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("comment.id"), default=None)
    is_approved: Mapped[bool] = mapped_column(default=True)

    # relationships
    article: Mapped[Optional["Article"]] = relationship(back_populates="comments")
    author: Mapped[Optional["User"]] = relationship(back_populates="comments")
    parent: Mapped[Optional["Comment"]] = relationship(back_populates="replies", remote_side="Comment.id")
    replies: Mapped[List["Comment"]] = relationship(back_populates="parent")