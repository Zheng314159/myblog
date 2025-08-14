import os
from pathlib import Path
import uuid
from datetime import datetime
from typing import List, Optional, Annotated
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, BackgroundTasks, Query
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
import re

from app.core.database import get_db
from app.core.exceptions import NotFoundError, AuthorizationError
from app.core.security import get_current_user
from app.core.tasks import add_comment_notification_task
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

# =========================
# 路径常量
# =========================
BASE_DIR = Path(__file__).resolve().parents[3]  # 往上 3 层
UPLOAD_DIR = BASE_DIR / "uploads"
PUBLIC_DIR = BASE_DIR / "frontend" / "public"

TYPE_DIRS = {
    "image": "images",
    "video": "videos",
    "pdf": "pdfs",
}

# 确保目录存在
for base_dir in (UPLOAD_DIR, PUBLIC_DIR):
    for sub_dir in TYPE_DIRS.values():
        (base_dir / sub_dir).mkdir(parents=True, exist_ok=True)



def get_save_path(current_user: User, file_type: str, filename: str):
    if current_user.role == "ADMIN":
        base_dir = PUBLIC_DIR
        base_url = "/public"
    else:
        base_dir = UPLOAD_DIR
        base_url = "/uploads"

    if file_type not in TYPE_DIRS:
        raise ValueError(f"Unsupported file type: {file_type}")

    sub_dir = TYPE_DIRS[file_type]
    save_dir = base_dir / sub_dir
    file_url = f"{base_url}/{sub_dir}/{filename}"
    return save_dir, file_url

async def save_upload_file(file: UploadFile, save_dir: Path, filename: str) -> bytes:
    save_dir.mkdir(parents=True, exist_ok=True)
    file_path = save_dir / filename
    content = await file.read()
    file_path.write_bytes(content)
    return content


async def handle_upload(
    current_user: User,
    db: AsyncSession,
    file: UploadFile,
    file_type: str,
    max_size: int,
    allowed_mime_prefix: str
):
    """通用上传处理逻辑"""
    # 类型检查
    if not file.content_type or not file.content_type.startswith(allowed_mime_prefix):
        raise HTTPException(status_code=400, detail=f"Only {file_type} files are allowed")

    # 大小检查
    if file.size and file.size > max_size:
        raise HTTPException(status_code=400, detail=f"File size too large. Maximum {max_size // (1024*1024)}MB allowed")

    # 文件名检查
    if not file.filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    # 生成唯一文件名
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{ext}"

    # 路径 & 保存
    save_dir, file_url = get_save_path(current_user, file_type, filename)
    content = await save_upload_file(file, save_dir, filename)

    # 存数据库
    db_file = MediaFile(
        filename=filename,
        type=MediaType[file_type],
        url=file_url,
        size=len(content),
        description=None,
        uploader_id=current_user.id
    )
    db.add(db_file)
    await db.commit()

    return {
        "url": file_url,
        "filename": filename,
        "original_name": file.filename,
        "size": len(content)
    }


# =========================
# 上传接口
# =========================
@router.post("/upload-image", response_model=dict)
async def upload_image(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    file: UploadFile = File(...)
):
    return await handle_upload(
        current_user=current_user,
        db=db,
        file=file,
        file_type="image",
        max_size=5 * 1024 * 1024,  # 5MB
        allowed_mime_prefix="image/"
    )


@router.post("/upload-video", response_model=dict)
async def upload_video(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    file: UploadFile = File(...)
):
    return await handle_upload(
        current_user=current_user,
        db=db,
        file=file,
        file_type="video",
        max_size=100 * 1024 * 1024,  # 100MB
        allowed_mime_prefix="video/"
    )


@router.post("/upload-pdf", response_model=dict)
async def upload_pdf(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    file: UploadFile = File(...)
):
    return await handle_upload(
        current_user=current_user,
        db=db,
        file=file,
        file_type="pdf",
        max_size=20 * 1024 * 1024,  # 可以自己调
        allowed_mime_prefix="application/pdf"
    )
# 文件上传相关
from fastapi import Query
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy import select

@router.get("/media/{file_type}/{filename}")
async def get_media(
    file_type: MediaType,
    filename: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    preview: bool = Query(True)
):
    """
    通用文件获取接口
    file_type: image / video / pdf / latex 等（枚举类型）
    filename: 文件名
    preview: 对 PDF 是否预览（true）或下载（false）
    """
    # 从数据库查找文件元数据
    result = await db.execute(
        select(MediaFile).where(
            MediaFile.filename == filename,
            MediaFile.type == file_type
        )
    )
    media = result.scalar_one_or_none()
    if not media:
        raise HTTPException(status_code=404, detail="File not found")

    # 通过 URL 得到本地路径
    local_path = media.url.lstrip("/")
    if not os.path.exists(local_path):
        raise HTTPException(status_code=404, detail="File missing on disk")

    # PDF 特殊处理（流式传输 + 下载/预览切换）
    if file_type == MediaType.pdf:
        try:
            file = open(local_path, "rb")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to open PDF: {str(e)}")

        def file_iterator():
            try:
                while chunk := file.read(8192):
                    yield chunk
            finally:
                file.close()

        response = StreamingResponse(file_iterator(), media_type="application/pdf")
        if not preview:
            response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    # 其他类型直接用 FileResponse 返回
    return FileResponse(local_path)

@router.get("/images/{filename}")
async def get_image_compat(filename: str, db: Annotated[AsyncSession, Depends(get_db)]):
    return await get_media(MediaType.image, filename,  db,True)

@router.get("/videos/{filename}")
async def get_video_compat(filename: str, db: Annotated[AsyncSession, Depends(get_db)]):
    return await get_media(MediaType.video, filename,  db,True)

@router.get("/pdfs/{filename}")
async def get_pdf_compat(filename: str, db: Annotated[AsyncSession, Depends(get_db)],preview: bool = Query(True)):
    return await get_media(MediaType.pdf, filename,  db,preview)








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


@router.delete("/{article_id}/comments/{comment_id}")
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
    if comment.author_id != current_user.id:
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

@router.get("/media/list", response_model=List[dict])
async def list_media_files(db: Annotated[AsyncSession, Depends(get_db)],uploader_id: int = Query(None)):
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