from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, ForeignKey, func
from app.core.base import BaseModelMixin

class SystemNotification(BaseModelMixin):
    __tablename__ = "system_notification"
    id: Mapped[int] = mapped_column(default=None, primary_key=True)
    title: Mapped[str] =mapped_column()
    message: Mapped[str] =mapped_column()
    notification_type: Mapped[str] = mapped_column(default="info")
    is_sent: Mapped[bool] = mapped_column(default=False, comment="是否已发送")
    admin_id: Mapped[Optional[int]] = mapped_column(ForeignKey("user.id"),default=None)