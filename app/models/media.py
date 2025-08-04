from typing import Optional, TYPE_CHECKING
from enum import Enum
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, ForeignKey, func
from app.core.base import BaseModelMixin

if TYPE_CHECKING:
    from .user import User

class MediaType(str, Enum):
    image = "image"
    video = "video"
    pdf = "pdf"

class MediaFile(BaseModelMixin):
    __tablename__ = "media_file"
    id: Mapped[int] = mapped_column(default=None, primary_key=True)
    filename: Mapped[str] =mapped_column()
    type: Mapped[MediaType] =mapped_column()
    url: Mapped[str] =mapped_column()
    size: Mapped[int] =mapped_column()
    upload_time: Mapped[datetime] = mapped_column( DateTime(timezone=True),nullable=False,server_default=func.now())
    description: Mapped[Optional[str]] =mapped_column()
    uploader_id: Mapped[Optional[int]] = mapped_column(ForeignKey("user.id"),default=None)
    uploader: Mapped[Optional["User"]] = relationship(back_populates="media_files")
    # 可选：定义关系
    # uploader: Optional["User"] = relationship(back_populates="media_files") 