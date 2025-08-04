from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CommentBase(BaseModel):
    content: str


class CommentCreate(CommentBase):
    parent_id: Optional[int] = None
    article_id: int
    author_id: int


class CommentUpdate(BaseModel):
    content: Optional[str] = None
    is_approved: Optional[bool] = None


class CommentResponse(CommentBase):
    id: int
    article_id: int
    author_id: int
    parent_id: Optional[int]
    is_approved: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
