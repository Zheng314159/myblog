from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class SystemNotification(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    message: str
    notification_type: str = "info"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_sent: bool = False
    admin_id: Optional[int] = None 