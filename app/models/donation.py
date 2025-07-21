from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum
from decimal import Decimal

if TYPE_CHECKING:
    from .user import User


class DonationStatus(str, Enum):
    PENDING = "PENDING"      # 待处理
    SUCCESS = "SUCCESS"      # 成功
    FAILED = "FAILED"        # 失败
    CANCELLED = "CANCELLED"  # 已取消


class PaymentMethod(str, Enum):
    ALIPAY = "ALIPAY"        # 支付宝
    WECHAT = "WECHAT"        # 微信支付
    PAYPAL = "PAYPAL"        # PayPal


class DonationConfig(SQLModel, table=True):
    """捐赠配置表"""
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # 基本配置
    is_enabled: bool = Field(default=True, description="是否启用捐赠功能")
    title: str = Field(default="支持我们", description="捐赠页面标题")
    description: str = Field(default="感谢您的支持！", description="捐赠页面描述")
    
    # 支付方式配置
    alipay_enabled: bool = Field(default=True, description="是否启用支付宝")
    wechat_enabled: bool = Field(default=True, description="是否启用微信支付")
    paypal_enabled: bool = Field(default=True, description="是否启用PayPal")
    
    # 预设金额
    preset_amounts: str = Field(default="[5, 10, 20, 50, 100]", description="预设捐赠金额，JSON格式")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class DonationRecord(SQLModel, table=True):
    """捐赠记录表"""
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # 捐赠者信息
    donor_name: str = Field(description="捐赠者姓名")
    donor_email: Optional[str] = Field(default=None, description="捐赠者邮箱")
    donor_message: Optional[str] = Field(default=None, description="捐赠留言")
    is_anonymous: bool = Field(default=False, description="是否匿名捐赠")
    
    # 捐赠信息
    amount: Decimal = Field(description="捐赠金额")
    currency: str = Field(default="CNY", description="货币类型")
    payment_method: str = Field(description="支付方式")
    payment_status: str = Field(default="PENDING", description="支付状态")
    transaction_id: Optional[str] = Field(default=None, description="第三方交易ID")
    
    # 关联用户（可选）
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", description="关联用户ID")
    user: Optional["User"] = Relationship(back_populates="donations")
    
    # 关联目标（可选）
    goal_id: Optional[int] = Field(default=None, foreign_key="donationgoal.id", description="关联捐赠目标ID")
    
    # 时间信息
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    paid_at: Optional[datetime] = Field(default=None, description="支付完成时间")


class DonationGoal(SQLModel, table=True):
    """捐赠目标表"""
    id: Optional[int] = Field(default=None, primary_key=True)
    
    title: str = Field(description="目标标题")
    description: str = Field(description="目标描述")
    target_amount: Decimal = Field(description="目标金额")
    current_amount: Decimal = Field(default=Decimal('0.00'), description="当前金额")
    currency: str = Field(default="CNY", description="货币类型")
    
    start_date: datetime = Field(default_factory=datetime.utcnow, description="开始日期")
    end_date: Optional[datetime] = Field(default=None, description="结束日期")
    
    is_active: bool = Field(default=True, description="是否激活")
    is_completed: bool = Field(default=False, description="是否完成")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Schema 定义
class DonationConfigUpdate(SQLModel):
    is_enabled: Optional[bool] = None
    title: Optional[str] = None
    description: Optional[str] = None
    alipay_enabled: Optional[bool] = None
    wechat_enabled: Optional[bool] = None
    paypal_enabled: Optional[bool] = None
    preset_amounts: Optional[str] = None


class DonationCreate(SQLModel):
    donor_name: str
    donor_email: Optional[str] = None
    donor_message: Optional[str] = None
    is_anonymous: bool = False
    amount: Decimal
    currency: str = "CNY"
    payment_method: PaymentMethod
    goal_id: Optional[int] = None


class DonationResponse(SQLModel):
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
    created_at: datetime
    updated_at: datetime
    paid_at: Optional[datetime] = None
    # 支付相关信息
    alipay_form_html: Optional[str] = None
    alipay_qr: Optional[str] = None
    wechat_qr: Optional[str] = None
    wechat_prepay_id: Optional[str] = None
    wechat_trade_type: Optional[str] = None
    wechat_error: Optional[str] = None
    paypal_url: Optional[str] = None
    paypal_order_id: Optional[str] = None
    paypal_error: Optional[str] = None


class DonationGoalCreate(SQLModel):
    title: str
    description: str
    target_amount: Decimal
    currency: str = "CNY"
    start_date: datetime
    end_date: Optional[datetime] = None


class DonationGoalUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    target_amount: Optional[Decimal] = None
    currency: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None


class DonationGoalResponse(SQLModel):
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


class DonationStats(SQLModel):
    total_donations: int
    total_amount: Decimal
    currency: str
    monthly_donations: int
    monthly_amount: Decimal
    active_goals: int
    completed_goals: int 