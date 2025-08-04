from datetime import datetime
from decimal import Decimal
from typing import Optional
from enum import Enum
from pydantic import BaseModel


class DonationStatus(str, Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class PaymentMethod(str, Enum):
    ALIPAY = "ALIPAY"
    WECHAT = "WECHAT"
    PAYPAL = "PAYPAL"


class DonationConfigUpdate(BaseModel):
    is_enabled: Optional[bool] = None
    title: Optional[str] = None
    description: Optional[str] = None
    alipay_enabled: Optional[bool] = None
    wechat_enabled: Optional[bool] = None
    paypal_enabled: Optional[bool] = None
    preset_amounts: Optional[str] = None

# app/schemas/donation.py
from pydantic import BaseModel
from typing import Optional

class DonationConfigResponse(BaseModel):
    id: Optional[int]
    is_enabled: bool
    title: str
    description: str
    alipay_enabled: bool
    wechat_enabled: bool
    paypal_enabled: bool
    preset_amounts: str  # 也可以解析为 List[int]，看你后续怎么用

    class Config:
        from_attributes = True  # Pydantic v2 替代 orm_mode


class DonationCreate(BaseModel):
    donor_name: str
    donor_email: Optional[str] = None
    donor_message: Optional[str] = None
    is_anonymous: bool = False
    amount: Decimal
    currency: str = "CNY"
    payment_method: PaymentMethod
    goal_id: Optional[int] = None


class DonationResponse(BaseModel):
    id: int
    donor_name: str
    donor_email: Optional[str] = None
    donor_message: Optional[str] = None
    is_anonymous: bool
    amount: Decimal
    currency: str
    payment_method: PaymentMethod
    payment_status: DonationStatus
    transaction_id: Optional[str] = None
    user_id: Optional[int] = None
    goal_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    paid_at: Optional[datetime] = None
    
    alipay_form_html: Optional[str] = None
    alipay_qr: Optional[str] = None
    wechat_qr: Optional[str] = None
    wechat_prepay_id: Optional[str] = None
    wechat_trade_type: Optional[str] = None
    wechat_error: Optional[str] = None
    paypal_url: Optional[str] = None
    paypal_order_id: Optional[str] = None
    paypal_error: Optional[str] = None

    class Config:
        from_attributes = True


class DonationGoalCreate(BaseModel):
    title: str
    description: str
    target_amount: Decimal
    currency: str = "CNY"
    start_date: datetime
    end_date: Optional[datetime] = None


class DonationGoalUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    target_amount: Optional[Decimal] = None
    currency: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None


class DonationGoalResponse(BaseModel):
    id: int
    title: str
    description: str
    target_amount: Decimal
    current_amount: Decimal
    currency: str
    start_date: datetime
    end_date: Optional[datetime] = None
    is_active: bool
    is_completed: bool
    progress_percentage: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DonationStats(BaseModel):
    total_donations: int
    total_amount: Decimal
    currency: str
    monthly_donations: int
    monthly_amount: Decimal
    active_goals: int
    completed_goals: int

    class Config:
        from_attributes = True