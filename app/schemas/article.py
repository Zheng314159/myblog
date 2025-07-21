from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum

from app.models.article import ArticleStatus
from app.models.user import UserRole


class ArticleCreate(BaseModel):
    """创建文章请求模型"""
    title: str = Field(..., min_length=1, max_length=200, description="文章标题")
    content: str = Field(..., min_length=1, description="文章内容（Markdown格式）")
    summary: Optional[str] = Field(None, max_length=500, description="文章摘要")
    status: ArticleStatus = Field(default=ArticleStatus.DRAFT, description="文章状态")
    tags: Optional[List[str]] = Field(default=[], description="文章标签")
    has_latex: bool = Field(default=False, description="是否包含LaTeX内容")
    latex_content: Optional[str] = Field(None, description="LaTeX内容")


class ArticleUpdate(BaseModel):
    """更新文章请求模型"""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="文章标题")
    content: Optional[str] = Field(None, min_length=1, description="文章内容（Markdown格式）")
    summary: Optional[str] = Field(None, max_length=500, description="文章摘要")
    status: Optional[ArticleStatus] = Field(None, description="文章状态")
    tags: Optional[List[str]] = Field(None, description="文章标签")
    has_latex: Optional[bool] = Field(None, description="是否包含LaTeX内容")
    latex_content: Optional[str] = Field(None, description="LaTeX内容")


class UserBasicInfo(BaseModel):
    """用户基本信息"""
    id: int
    username: str
    full_name: Optional[str] = None
    role: UserRole

    class Config:
        from_attributes = True


class TagInfo(BaseModel):
    """标签信息"""
    id: int
    name: str

    class Config:
        from_attributes = True


class CommentBasicInfo(BaseModel):
    """评论基本信息"""
    id: int
    content: str
    author: UserBasicInfo
    created_at: datetime
    parent_id: Optional[int] = None

    class Config:
        from_attributes = True


class ArticleResponse(BaseModel):
    """文章响应模型"""
    id: int
    title: str
    summary: Optional[str] = None
    status: ArticleStatus
    author: UserBasicInfo
    tags: List[TagInfo] = []
    created_at: datetime
    updated_at: datetime
    view_count: int = 0

    class Config:
        from_attributes = True


class ArticleListResponse(BaseModel):
    """文章列表响应模型"""
    id: int
    title: str
    summary: Optional[str] = None
    status: ArticleStatus
    author: UserBasicInfo
    tags: List[TagInfo] = []
    created_at: datetime
    updated_at: datetime
    view_count: int = 0
    comment_count: int = 0

    class Config:
        from_attributes = True


class ArticleDetailResponse(BaseModel):
    """文章详情响应模型"""
    id: int
    title: str
    content: str
    summary: Optional[str] = None
    status: ArticleStatus
    author: UserBasicInfo
    tags: List[TagInfo] = []
    comments: List[CommentBasicInfo] = []
    created_at: datetime
    updated_at: datetime
    view_count: int = 0

    class Config:
        from_attributes = True


class CommentCreate(BaseModel):
    """创建评论请求模型"""
    content: str = Field(..., min_length=1, max_length=1000, description="评论内容")
    parent_id: Optional[int] = Field(None, description="父评论ID（用于回复）")


class CommentResponse(BaseModel):
    """评论响应模型"""
    id: int
    content: str
    author: UserBasicInfo
    article_id: int
    parent_id: Optional[int] = None
    replies: List['CommentResponse'] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 解决循环引用
CommentResponse.model_rebuild() 