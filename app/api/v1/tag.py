from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.exceptions import NotFoundError, ConflictError
from app.core.security import get_current_user, require_admin
from app.models.user import User
from app.models.tag import Tag
from app.models.tag import ArticleTag
from app.schemas.tag import TagCreate, TagUpdate, TagResponse, TagWithCountResponse

router = APIRouter(prefix="/tags", tags=["tags"])


@router.post("/", response_model=TagResponse)
async def create_tag(
    tag_data: TagCreate,
    current_user: Annotated[User, Depends(require_admin)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """创建标签（仅管理员）"""
    # 检查标签是否已存在
    result = await db.execute(select(Tag).where(Tag.name == tag_data.name))
    if result.scalar_one_or_none():
        raise ConflictError("Tag already exists")
    
    # 创建标签
    db_tag = Tag(name=tag_data.name, description=tag_data.description)
    db.add(db_tag)
    await db.commit()
    await db.refresh(db_tag)
    
    return TagResponse.from_orm(db_tag)


@router.get("/", response_model=List[TagWithCountResponse])
async def list_tags(
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """获取标签列表（包含文章数量）"""
    # 查询标签及其关联的文章数量
    result = await db.execute(
        select(
            Tag,
            func.count(ArticleTag.article_id).label('article_count')
        )
        .outerjoin(ArticleTag)
        .group_by(Tag.id)
        .order_by(Tag.name)
    )
    
    tags_with_count = result.all()
    
    return [
        TagWithCountResponse(
            id=tag.id,
            name=tag.name,
            description=tag.description,
            article_count=count
        )
        for tag, count in tags_with_count
    ]


@router.get("/popular", response_model=List[TagWithCountResponse])
async def get_popular_tags(
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = 10
):
    """获取热门标签"""
    result = await db.execute(
        select(
            Tag,
            func.count(ArticleTag.article_id).label('article_count')
        )
        .outerjoin(ArticleTag)
        .group_by(Tag.id)
        .order_by(func.count(ArticleTag.article_id).desc())
        .limit(limit)
    )
    
    tags_with_count = result.all()
    
    return [
        TagWithCountResponse(
            id=tag.id,
            name=tag.name,
            description=tag.description,
            article_count=count
        )
        for tag, count in tags_with_count
    ]


@router.get("/{tag_id}", response_model=TagResponse)
async def get_tag(
    tag_id: int,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """获取标签详情"""
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalar_one_or_none()
    
    if not tag:
        raise NotFoundError("Tag not found")
    
    return TagResponse.from_orm(tag)


@router.put("/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: int,
    tag_data: TagUpdate,
    current_user: Annotated[User, Depends(require_admin)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """更新标签（仅管理员）"""
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalar_one_or_none()
    
    if not tag:
        raise NotFoundError("Tag not found")
    
    # 检查新名称是否与其他标签冲突
    if tag_data.name and tag_data.name != tag.name:
        result = await db.execute(select(Tag).where(Tag.name == tag_data.name))
        if result.scalar_one_or_none():
            raise ConflictError("Tag name already exists")
    
    # 更新标签
    update_data = tag_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tag, field, value)
    
    await db.commit()
    await db.refresh(tag)
    
    return TagResponse.from_orm(tag)


@router.delete("/{tag_id}")
async def delete_tag(
    tag_id: int,
    current_user: Annotated[User, Depends(require_admin)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """删除标签（仅管理员）"""
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalar_one_or_none()
    
    if not tag:
        raise NotFoundError("Tag not found")
    
    # 删除标签与文章的关联
    await db.execute(delete(ArticleTag).where(ArticleTag.tag_id == tag_id))
    
    # 删除标签
    await db.execute(delete(Tag).where(Tag.id == tag_id))
    await db.commit()
    
    return {"message": "Tag deleted successfully"} 