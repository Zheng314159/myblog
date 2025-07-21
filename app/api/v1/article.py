import os
import uuid
from datetime import datetime
from typing import List, Optional, Annotated
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, BackgroundTasks, Query
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
import re

from app.core.database import get_db
from app.core.exceptions import NotFoundError, AuthorizationError
from app.core.security import get_current_user
from app.core.tasks import add_comment_notification_task
from app.core.latex import latex_renderer
from app.models.user import User, UserRole
from app.models.article import Article, ArticleStatus
from app.models.comment import Comment
from app.models.tag import Tag, ArticleTag
from app.schemas.article import (
    ArticleCreate, ArticleUpdate, ArticleResponse, ArticleListResponse,
    ArticleDetailResponse, CommentCreate, CommentResponse
)
from app.core.config import settings
from app.models.media import MediaFile, MediaType

router = APIRouter(prefix="/articles", tags=["articles"])


# 文件上传相关
UPLOAD_DIR = "uploads"
IMAGES_DIR = os.path.join(UPLOAD_DIR, "images")
ARTICLES_DIR = os.path.join(UPLOAD_DIR, "articles")
LATEX_DIR = os.path.join(UPLOAD_DIR, "latex")
VIDEOS_DIR = os.path.join(UPLOAD_DIR, "videos")
PDFS_DIR = os.path.join(UPLOAD_DIR, "pdfs")

# 确保上传目录存在
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(ARTICLES_DIR, exist_ok=True)
os.makedirs(LATEX_DIR, exist_ok=True)
os.makedirs(VIDEOS_DIR, exist_ok=True)
os.makedirs(PDFS_DIR, exist_ok=True)


def get_file_path(filename: str, directory: str) -> str:
    """生成文件路径"""
    return os.path.join(directory, filename)


@router.post("/upload-image", response_model=dict)
async def upload_image(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    file: UploadFile = File(...)
):
    """上传图片"""
    # 检查文件类型
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400,
            detail="Only image files are allowed"
        )
    
    # 检查文件大小 (5MB)
    if file.size and file.size > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="File size too large. Maximum 5MB allowed"
        )
    
    # 生成唯一文件名
    if not file.filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = get_file_path(unique_filename, IMAGES_DIR)
    
    # 保存文件
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save file: {str(e)}"
        )
    
    # 返回文件URL
    file_url = f"/api/v1/articles/images/{unique_filename}"
    
    # 保存元数据
    db_file = MediaFile(
        filename=unique_filename,
        type=MediaType.image,
        url=file_url,
        size=len(content),
        description=None,
        uploader_id=current_user.id
    )
    db.add(db_file)
    await db.commit()
    
    return {
        "url": file_url,
        "filename": unique_filename,
        "original_name": file.filename,
        "size": len(content)
    }


@router.get("/images/{filename}")
async def get_image(filename: str):
    """获取图片文件"""
    file_path = get_file_path(filename, IMAGES_DIR)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image not found")
    
    return FileResponse(file_path)


@router.get("/latex/{filename}")
async def get_latex_image(filename: str):
    """获取LaTeX渲染的图片文件"""
    file_path = get_file_path(filename, LATEX_DIR)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="LaTeX image not found")
    
    # 检查文件类型
    if filename.endswith('.svg'):
        return FileResponse(file_path, media_type="image/svg+xml")
    else:
        return FileResponse(file_path)


@router.post("/latex/preview")
async def preview_latex(
    latex_content: str = Form(...),
    block_type: str = Form(default="block")
):
    """预览LaTeX内容"""
    # 验证LaTeX语法
    is_valid, message = latex_renderer.validate_latex(latex_content)
    if not is_valid:
        raise HTTPException(status_code=400, detail=message)
    
    # 渲染LaTeX
    image_url = latex_renderer.render_latex_to_image(latex_content, block_type)
    if not image_url:
        raise HTTPException(status_code=500, detail="LaTeX渲染失败")
    
    return {
        "image_url": image_url,
        "latex_content": latex_content,
        "block_type": block_type
    }


@router.post("/latex/validate")
async def validate_latex(latex_content: str = Form(...)):
    """验证LaTeX语法"""
    is_valid, message = latex_renderer.validate_latex(latex_content)
    return {
        "is_valid": is_valid,
        "message": message,
        "latex_content": latex_content
    }


# 评论相关
@router.post("/{article_id}/comments", response_model=CommentResponse)
async def create_comment(
    article_id: int,
    comment_data: CommentCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    background_tasks: BackgroundTasks,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """创建评论"""
    # 检查文章是否存在
    result = await db.execute(
        select(Article).options(selectinload(Article.author)).where(Article.id == article_id)
    )
    article = result.scalar_one_or_none()
    
    if not article:
        raise NotFoundError("Article not found")
    
    # 创建评论
    db_comment = Comment(
        content=comment_data.content,
        author_id=current_user.id,
        article_id=article_id,
        parent_id=comment_data.parent_id
    )
    
    db.add(db_comment)
    await db.commit()
    await db.refresh(db_comment)
    
    # 发送评论通知邮件给文章作者
    if article.author_id != current_user.id and article.author:
        add_comment_notification_task(
            background_tasks,
            article.author.email,
            article.author.username,
            article.title,
            comment_data.content
        )
    
    # 手动组装 CommentResponse，避免 ORM 对象不可序列化
    from app.schemas.article import UserBasicInfo, CommentResponse
    author_info = UserBasicInfo.model_validate(current_user)
    return CommentResponse(
        id=db_comment.id,
        content=db_comment.content,
        author=author_info,
        article_id=db_comment.article_id,
        parent_id=db_comment.parent_id,
        replies=[],
        created_at=db_comment.created_at,
        updated_at=db_comment.updated_at
    )


@router.get("/{article_id}/comments", response_model=List[CommentResponse])
async def get_article_comments(
    article_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = 0,
    limit: int = 50
):
    """获取文章评论"""
    result = await db.execute(
        select(Comment).options(
            selectinload(Comment.author),
            selectinload(Comment.replies)
        ).where(Comment.article_id == article_id)
        .order_by(Comment.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    comments = result.scalars().all()
    
    return [CommentResponse.from_orm(comment) for comment in comments]


@router.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """删除评论"""
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    
    if not comment:
        raise NotFoundError("Comment not found")
    
    # 检查权限
    if comment.author_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise AuthorizationError("You can only delete your own comments")
    
    # 删除评论
    await db.execute(delete(Comment).where(Comment.id == comment_id))
    await db.commit()
    
    return {"message": "Comment deleted successfully"}


@router.post("/", response_model=ArticleResponse)
async def create_article(
    article_data: ArticleCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """创建文章"""
    # 检查是否包含LaTeX内容（用于标记，但不进行服务端渲染）
    has_latex = False
    latex_content = None
    
    # 简单的LaTeX检测
    if article_data.content:
        latex_patterns = [
            r'\$[^$]+\$',  # 行内公式
            r'\$\$[^$]+\$\$',  # 块级公式
            r'\\\([^)]+\\\)',  # 行内公式
            r'\\\[[^\]]+\\\]',  # 块级公式
        ]
        
        for pattern in latex_patterns:
            if re.search(pattern, article_data.content):
                has_latex = True
                break
    
    # 创建文章（直接使用原始内容，不进行LaTeX处理）
    db_article = Article(
        title=article_data.title,
        content=article_data.content,  # 直接使用原始内容
        summary=article_data.summary,
        status=article_data.status,
        author_id=current_user.id,
        has_latex=has_latex,
        latex_content=latex_content
    )
    
    db.add(db_article)
    await db.commit()
    await db.refresh(db_article)
    
    # 处理标签
    if article_data.tags:
        for tag_name in article_data.tags:
            # 查找或创建标签
            result = await db.execute(select(Tag).where(Tag.name == tag_name))
            tag = result.scalar_one_or_none()
            
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
                await db.commit()
                await db.refresh(tag)
            
            # 创建文章标签关联
            article_tag = ArticleTag(article_id=db_article.id, tag_id=tag.id)
            db.add(article_tag)
        
        await db.commit()
    
    # 重新加载文章及其标签
    result = await db.execute(
        select(Article)
        .options(
            selectinload(Article.author),
            selectinload(Article.tags).selectinload(ArticleTag.tag)
        )
        .where(Article.id == db_article.id)
    )
    article_with_relations = result.scalar_one()
    
    # 组装 ArticleResponse 所需的 author/tags 字段
    from app.schemas.article import UserBasicInfo, TagInfo
    author_info = UserBasicInfo.model_validate(article_with_relations.author)
    tag_infos = [TagInfo.model_validate(at.tag) for at in article_with_relations.tags if at.tag is not None]
    
    return ArticleResponse(
        id=article_with_relations.id,
        title=article_with_relations.title,
        summary=article_with_relations.summary,
        status=article_with_relations.status,
        author=author_info,
        tags=tag_infos,
        created_at=article_with_relations.created_at,
        updated_at=article_with_relations.updated_at,
        view_count=getattr(article_with_relations, 'view_count', 0)
    )


@router.get("/", response_model=List[ArticleListResponse])
async def list_articles(
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = 0,
    limit: int = 10,
    status: Optional[ArticleStatus] = None,
    tag: Optional[str] = None,
    search: Optional[str] = None,
    author: Optional[str] = None
):
    """获取文章列表"""
    query = select(Article).options(
        selectinload(Article.author),
        selectinload(Article.tags).selectinload(ArticleTag.tag),
        selectinload(Article.comments)
    )
    
    # 过滤条件
    if status:
        query = query.where(Article.status == status)
    
    if search:
        query = query.where(
            Article.title.contains(search) | 
            Article.content.contains(search)
        )
    
    if tag:
        query = query.join(ArticleTag).join(Tag).where(Tag.name == tag)
    
    if author:
        query = query.join(User).where(User.username == author)
    
    # 排序和分页
    query = query.order_by(Article.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    articles = result.scalars().all()
    
    # 手动构建响应，避免ORM序列化问题
    from app.schemas.article import UserBasicInfo, TagInfo
    article_responses = []
    
    for article in articles:
        author_info = UserBasicInfo.model_validate(article.author)
        tag_infos = [TagInfo.model_validate(at.tag) for at in article.tags if at.tag is not None]
        
        article_response = ArticleListResponse(
            id=article.id,
            title=article.title,
            summary=article.summary,
            status=article.status,
            author=author_info,
            tags=tag_infos,
            created_at=article.created_at,
            updated_at=article.updated_at,
            view_count=getattr(article, 'view_count', 0),
            comment_count=len(article.comments)
        )
        article_responses.append(article_response)
    
    return article_responses


@router.get("/{article_id}", response_model=ArticleDetailResponse)
async def get_article(
    article_id: int,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """获取文章详情"""
    result = await db.execute(
        select(Article).options(
            selectinload(Article.author),
            selectinload(Article.tags).selectinload(ArticleTag.tag),
            selectinload(Article.comments).selectinload(Comment.author)
        ).where(Article.id == article_id)
    )
    article = result.scalar_one_or_none()
    
    if not article:
        raise NotFoundError("Article not found")
    
    # 访问时自增view_count
    article.view_count = (article.view_count or 0) + 1
    await db.commit()
    await db.refresh(article)
    
    # 手动构建响应，避免ORM序列化问题
    from app.schemas.article import UserBasicInfo, TagInfo, CommentBasicInfo
    author_info = UserBasicInfo.model_validate(article.author)
    tag_infos = [TagInfo.model_validate(at.tag) for at in article.tags if at.tag is not None]
    
    # 处理评论
    comment_infos = []
    for comment in article.comments:
        comment_author = UserBasicInfo.model_validate(comment.author)
        comment_info = CommentBasicInfo(
            id=comment.id,
            content=comment.content,
            author=comment_author,
            created_at=comment.created_at,
            parent_id=comment.parent_id
        )
        comment_infos.append(comment_info)
    
    return ArticleDetailResponse(
        id=article.id,
        title=article.title,
        content=article.content,
        summary=article.summary,
        status=article.status,
        author=author_info,
        tags=tag_infos,
        comments=comment_infos,
        created_at=article.created_at,
        updated_at=article.updated_at,
        view_count=getattr(article, 'view_count', 0)
    )


@router.put("/{article_id}", response_model=ArticleResponse)
async def update_article(
    article_id: int,
    article_data: ArticleUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """更新文章"""
    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()
    
    if not article:
        raise NotFoundError("Article not found")
    
    # 检查权限
    if article.author_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise AuthorizationError("You can only update your own articles")
    
    # 只提取 Article 表字段
    update_data = article_data.dict(exclude_unset=True, exclude={"tags"})
    
    if article_data.content is not None:
        # 处理LaTeX内容
        has_latex = False
        latex_content = None
        processed_content = article_data.content
        
        if article_data.has_latex and article_data.latex_content:
            has_latex = True
            latex_content = article_data.latex_content
            # 处理LaTeX内容
            processed_content, latex_blocks = latex_renderer.process_content(article_data.content)
        
        update_data['content'] = processed_content
        update_data['has_latex'] = has_latex
        update_data['latex_content'] = latex_content
    
    # 更新文章
    await db.execute(
        update(Article)
        .where(Article.id == article_id)
        .values(**update_data)
    )
    
    # 更新标签
    if article_data.tags is not None:
        # 删除现有标签关联
        await db.execute(delete(ArticleTag).where(ArticleTag.article_id == article_id))
        
        # 添加新标签
        for tag_name in article_data.tags:
            result = await db.execute(select(Tag).where(Tag.name == tag_name))
            tag = result.scalar_one_or_none()
            
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
                await db.commit()
                await db.refresh(tag)
            
            article_tag = ArticleTag(article_id=article_id, tag_id=tag.id)
            db.add(article_tag)
    
    await db.commit()
    
    # 返回更新后的文章
    result = await db.execute(
        select(Article).options(
            selectinload(Article.author),
            selectinload(Article.tags).selectinload(ArticleTag.tag)
        ).where(Article.id == article_id)
    )
    updated_article = result.scalar_one()
    
    # 手动构建响应，避免ORM序列化问题
    from app.schemas.article import UserBasicInfo, TagInfo
    author_info = UserBasicInfo.model_validate(updated_article.author)
    tag_infos = [TagInfo.model_validate(at.tag) for at in updated_article.tags if at.tag is not None]
    
    return ArticleResponse(
        id=updated_article.id,
        title=updated_article.title,
        summary=updated_article.summary,
        status=updated_article.status,
        author=author_info,
        tags=tag_infos,
        created_at=updated_article.created_at,
        updated_at=updated_article.updated_at,
        view_count=getattr(updated_article, 'view_count', 0)
    )


@router.delete("/{article_id}")
async def delete_article(
    article_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """删除文章"""
    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()
    
    if not article:
        raise NotFoundError("Article not found")
    
    # 检查权限
    if article.author_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise AuthorizationError("You can only delete your own articles")
    
    # 删除文章标签关联
    await db.execute(delete(ArticleTag).where(ArticleTag.article_id == article_id))
    
    # 删除文章
    await db.execute(delete(Article).where(Article.id == article_id))
    await db.commit()
    
    return {"message": "Article deleted successfully"}


@router.post("/upload-video", response_model=dict)
async def upload_video(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    file: UploadFile = File(...)
):
    """上传视频"""
    # 检查文件类型
    if not file.content_type or not file.content_type.startswith('video/'):
        raise HTTPException(
            status_code=400,
            detail="Only video files are allowed"
        )
    # 检查文件大小 (100MB)
    if file.size and file.size > 100 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="File size too large. Maximum 100MB allowed"
        )
    # 生成唯一文件名
    if not file.filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(VIDEOS_DIR, unique_filename)
    # 保存文件
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save file: {str(e)}"
        )
    # 返回文件URL
    file_url = f"/api/v1/articles/videos/{unique_filename}"
    
    # 保存元数据
    db_file = MediaFile(
        filename=unique_filename,
        type=MediaType.video,
        url=file_url,
        size=len(content),
        description=None,
        uploader_id=current_user.id
    )
    db.add(db_file)
    await db.commit()
    
    return {
        "url": file_url,
        "filename": unique_filename,
        "original_name": file.filename,
        "size": len(content)
    }


@router.get("/videos/{filename}")
async def get_video(filename: str):
    """获取视频文件"""
    file_path = os.path.join(VIDEOS_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Video not found")
    return FileResponse(file_path)


@router.post("/upload-pdf", response_model=dict)
async def upload_pdf(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    file: UploadFile = File(...)
):
    """上传 PDF 文档"""
    if not file.content_type or file.content_type != 'application/pdf':
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(PDFS_DIR, unique_filename)
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    file_url = f"/api/v1/articles/pdfs/{unique_filename}"
    
    # 保存元数据
    db_file = MediaFile(
        filename=unique_filename,
        type=MediaType.pdf,
        url=file_url,
        size=len(content),
        description=None,
        uploader_id=current_user.id
    )
    db.add(db_file)
    await db.commit()
    
    return {
        "url": file_url,
        "filename": unique_filename,
        "original_name": file.filename,
        "size": len(content)
    }


@router.get("/pdfs/{filename}")
async def get_pdf(filename: str):
    file_path = os.path.join(PDFS_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="PDF not found")
    return FileResponse(file_path, media_type="application/pdf", filename=filename, content_disposition_type="inline")


@router.get("/media/list", response_model=List[dict])
async def list_media_files(uploader_id: int = Query(None), db: Annotated[AsyncSession, Depends(get_db)] = None):
    from app.models.media import MediaFile
    from sqlalchemy import select
    query = select(MediaFile).options(selectinload(MediaFile.uploader))
    if uploader_id is not None:
        query = query.where(MediaFile.uploader_id == uploader_id)
    result = await db.execute(query)
    files = result.scalars().all()
    media_files = []
    for f in files:
        media_files.append({
            "id": f.id,
            "filename": f.filename,
            "type": f.type,
            "size": f.size,
            "upload_time": f.upload_time.timestamp() if hasattr(f.upload_time, 'timestamp') else f.upload_time,
            "url": f.url,
            "uploader_id": f.uploader_id,
            "uploader_username": f.uploader.username if f.uploader else None,
            "uploader_role": f.uploader.role if f.uploader else None,
        })
    media_files.sort(key=lambda x: x["upload_time"], reverse=True)
    return JSONResponse(content=media_files)


@router.delete("/media/{media_id}", response_model=dict)
async def delete_media_file(
    media_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    media = await db.get(MediaFile, media_id)
    if not media:
        raise HTTPException(status_code=404, detail="文件不存在")
    # 权限校验（只允许本人或管理员删除）
    if media.uploader_id != current_user.id and getattr(current_user, 'role', None) != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="无权限删除")
    # 删除文件本体
    try:
        # 只删除本地文件，url 需转为本地路径
        file_path = None
        if media.type == MediaType.image:
            file_path = os.path.join("uploads", "images", media.filename)
        elif media.type == MediaType.video:
            file_path = os.path.join("uploads", "videos", media.filename)
        elif media.type == MediaType.pdf:
            file_path = os.path.join("uploads", "pdfs", media.filename)
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        pass  # 可记录日志
    await db.delete(media)
    await db.commit()
    return {"message": "删除成功"} 