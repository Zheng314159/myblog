from datetime import datetime
from typing import TYPE_CHECKING, Optional
from decimal import Decimal
from enum import Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, ForeignKey, func, String, Boolean, Text
from app.core.base import BaseModelMixin

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


class DonationConfig(BaseModelMixin):
    __tablename__ = "donation_config"
    id: Mapped[Optional[int]] = mapped_column(default=None, primary_key=True)
    
    is_enabled: Mapped[bool] = mapped_column(default=True, comment="是否启用捐赠功能")
    title: Mapped[str] = mapped_column(default="支持我们", comment="捐赠页面标题")
    description: Mapped[str] = mapped_column(default="感谢您的支持！", comment="捐赠页面描述")
    
    alipay_enabled: Mapped[bool] = mapped_column(default=True, comment="是否启用支付宝")
    wechat_enabled: Mapped[bool] = mapped_column(default=True, comment="是否启用微信支付")
    paypal_enabled: Mapped[bool] = mapped_column(default=True, comment="是否启用PayPal")
    
    preset_amounts: Mapped[str] = mapped_column(default='[5, 10, 20, 50, 100]', comment="预设捐赠金额，JSON格式")


class DonationRecord(BaseModelMixin):
    __tablename__ = "donation_record"
    id: Mapped[int] = mapped_column(default=None, primary_key=True)
    
    donor_name: Mapped[str] = mapped_column(comment="捐赠者姓名")
    donor_email: Mapped[Optional[str]] = mapped_column(default=None, comment="捐赠者邮箱")
    donor_message: Mapped[Optional[str]] = mapped_column(default=None, comment="捐赠留言")
    is_anonymous: Mapped[bool] = mapped_column(default=False, comment="是否匿名捐赠")
    
    amount: Mapped[Decimal] = mapped_column(comment="捐赠金额")
    currency: Mapped[str] = mapped_column(default="CNY", comment="货币类型")
    payment_method: Mapped[str] = mapped_column(comment="支付方式")
    payment_status: Mapped[str] = mapped_column(default="PENDING", comment="支付状态")
    transaction_id: Mapped[Optional[str]] = mapped_column(default=None, comment="第三方交易ID")
    
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("user.id"), comment="关联用户ID", default=None)
    user: Mapped[Optional["User"]] = relationship(back_populates="donations")
    
    goal_id: Mapped[Optional[int]] = mapped_column(ForeignKey("donation_goal.id"), comment="关联捐赠目标ID", default=None)
    
    paid_at: Mapped[Optional[datetime]] = mapped_column(default=None, comment="支付完成时间")


class DonationGoal(BaseModelMixin):
    __tablename__ = "donation_goal"
    id: Mapped[int] = mapped_column(default=None, primary_key=True)
    
    title: Mapped[str] = mapped_column(comment="目标标题")
    description: Mapped[str] = mapped_column(comment="目标描述")
    target_amount: Mapped[Decimal] = mapped_column(comment="目标金额")
    current_amount: Mapped[Decimal] = mapped_column(default=Decimal('0.00'), comment="当前金额")
    currency: Mapped[str] = mapped_column(default="CNY", comment="货币类型")
    
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    end_date: Mapped[Optional[datetime]] = mapped_column(default=None, comment="结束日期")
    
    is_active: Mapped[bool] = mapped_column(default=True, comment="是否激活")
    is_completed: Mapped[bool] = mapped_column(default=False, comment="是否完成")
