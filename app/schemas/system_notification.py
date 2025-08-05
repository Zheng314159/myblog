# app/schemas/notification.py
from pydantic import BaseModel
from datetime import datetime

class SystemNotificationOut(BaseModel):
    id: int
    title: str
    message: str
    is_sent: bool
    created_at: datetime
    notification_type: str
    admin_id: int

    class Config:
        from_attributes = True  # 必须加这一行，才能从 ORM 实例读取字段
