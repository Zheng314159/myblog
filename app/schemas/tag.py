from typing import Optional
from pydantic import BaseModel, Field


class TagCreate(BaseModel):
    """创建标签请求模型"""
    name: str = Field(..., min_length=1, max_length=50, description="标签名称")
    description: Optional[str] = Field(None, max_length=200, description="标签描述")


class TagUpdate(BaseModel):
    """更新标签请求模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="标签名称")
    description: Optional[str] = Field(None, max_length=200, description="标签描述")


class TagResponse(BaseModel):
    """标签响应模型"""
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class TagWithCountResponse(BaseModel):
    """带文章数量的标签响应模型"""
    id: int
    name: str
    description: Optional[str] = None
    article_count: int = 0

    class Config:
        from_attributes = True 