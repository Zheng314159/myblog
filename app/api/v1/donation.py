from datetime import datetime, timedelta
from typing import List, Optional
from decimal import Decimal
import json
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from sqlmodel import select, func
from sqlalchemy import and_
from alipay import AliPay

from app.core.database import async_session
from app.core.security import get_current_user, require_admin
from app.models.user import User, UserRole
from app.models.donation import (
    DonationConfig, DonationRecord, DonationGoal,
    DonationStatus, PaymentMethod,
    DonationConfigUpdate, DonationCreate, DonationResponse,
    DonationGoalCreate, DonationGoalUpdate, DonationGoalResponse,
    DonationStats
)
from app.core.email import email_service
from app.core.config import settings
from app.core.exceptions import BlogException
from app.core.wechat_pay import wechat_pay_v3
from app.core.paypal import paypal_pay

router = APIRouter(prefix="/donation", tags=["捐赠"])


# ==================== 捐赠配置管理 ====================

@router.get("/config", response_model=DonationConfig)
async def get_donation_config():
    """获取捐赠配置"""
    async with async_session() as session:
        result = await session.execute(select(DonationConfig).limit(1))
        config = result.scalar_one_or_none()
        
        if not config:
            # 创建默认配置
            config = DonationConfig()
            session.add(config)
            await session.commit()
            await session.refresh(config)
        
        return config


@router.put("/config", response_model=DonationConfig)
async def update_donation_config(
    config_update: DonationConfigUpdate,
    current_user: User = Depends(require_admin)
):
    """更新捐赠配置（仅管理员）"""
    async with async_session() as session:
        result = await session.execute(select(DonationConfig).limit(1))
        config = result.scalar_one_or_none()
        
        if not config:
            config = DonationConfig()
            session.add(config)
        
        # 更新配置
        update_data = config_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(config, field, value)
        
        config.updated_at = datetime.utcnow()
        await session.commit()
        await session.refresh(config)
        
        return config


# ==================== 捐赠记录管理 ====================

@router.post("/create", response_model=DonationResponse)
async def create_donation(
    donation_data: DonationCreate,
    background_tasks: BackgroundTasks,
    request: Request
):
    user = getattr(request.state, "user", None)
    print("进入 create_donation 路由, user:", user)
    """创建捐赠记录"""
    async with async_session() as session:
        # 检查捐赠功能是否启用
        result = await session.execute(select(DonationConfig).limit(1))
        config = result.scalar_one_or_none()
        
        if not config or not config.is_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="捐赠功能未启用"
            )
        
        # 检查支付方式是否启用
        payment_enabled = getattr(config, f"{donation_data.payment_method.lower()}_enabled", False)
        if not payment_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{donation_data.payment_method} 支付方式未启用"
            )
        
        # 创建捐赠记录
        donation = DonationRecord(
            donor_name=donation_data.donor_name,
            donor_email=donation_data.donor_email,
            donor_message=donation_data.donor_message,
            is_anonymous=donation_data.is_anonymous,
            amount=donation_data.amount,
            currency=donation_data.currency,
            payment_method=donation_data.payment_method,
            user_id=user.id if user else None,
            goal_id=getattr(donation_data, 'goal_id', None)
        )
        
        session.add(donation)
        await session.commit()
        await session.refresh(donation)
        
        # 统一定义 donation_dict，避免 UnboundLocalError
        donation_dict = donation.dict() if hasattr(donation, 'dict') else dict(donation)
        
        # 根据支付方式生成支付信息
        if donation_data.payment_method == PaymentMethod.ALIPAY:
            try:
                alipay = AliPay(
                    appid=settings.alipay_app_id,
                    app_notify_url=settings.alipay_notify_url,
                    app_private_key_string=settings.alipay_private_key,
                    alipay_public_key_string=settings.alipay_public_key,
                    sign_type="RSA2",
                    debug=False
                )
                order_string = alipay.api_alipay_trade_page_pay(
                    out_trade_no=str(donation.id),
                    total_amount=str(donation.amount),
                    subject=f"博客捐赠-{donation.donor_name}",
                    return_url=settings.alipay_return_url,
                    notify_url=settings.alipay_notify_url
                )
                # 生成 form 表单 HTML
                params = [tuple(p.split('=', 1)) for p in order_string.split('&')]
                form_html = f'''<form id="alipaysubmit" name="alipaysubmit" action="{settings.alipay_gateway}?charset=utf-8" method="POST">{''.join([f'<input type="hidden" name="{k}" value="{v}" />' for k, v in params])}</form><script>document.forms['alipaysubmit'].submit();</script>'''
                donation_dict["alipay_form_html"] = form_html
                if settings.alipay_qr_base:
                    donation_dict["alipay_qr"] = f"{settings.alipay_qr_base}/{donation.id}.png"
            except Exception as e:
                donation_dict["alipay_error"] = str(e)
                
        elif donation_data.payment_method == PaymentMethod.WECHAT:
            try:
                total_amount = int(float(donation.amount) * 100)
                wechat_result = wechat_pay_v3.create_order(
                    out_trade_no=str(donation.id),
                    total_amount=total_amount,
                    description=f"博客捐赠-{donation.donor_name}",
                    openid=None
                )
                if wechat_result.get("code_url"):
                    donation_dict["wechat_qr"] = wechat_result["code_url"]
                donation_dict["wechat_prepay_id"] = wechat_result.get("prepay_id")
                donation_dict["wechat_trade_type"] = wechat_result.get("trade_type")
            except Exception as e:
                donation_dict["wechat_error"] = str(e)
                
        elif donation_data.payment_method == PaymentMethod.PAYPAL:
            try:
                paypal_result = paypal_pay.create_order(
                    out_trade_no=str(donation.id),
                    total_amount=float(donation.amount),
                    description=f"博客捐赠-{donation.donor_name}"
                )
                if paypal_result.get("success"):
                    donation_dict["paypal_url"] = paypal_result.get("approval_url")
                    donation_dict["paypal_order_id"] = paypal_result.get("order_id")
                else:
                    donation_dict["paypal_error"] = paypal_result.get("error")
            except Exception as e:
                donation_dict["paypal_error"] = str(e)
                
        # 优先累加到 donation.goal_id 指定目标
        goal = None
        if donation.goal_id:
            goal_result = await session.execute(
                select(DonationGoal).where(DonationGoal.id == donation.goal_id)
            )
            goal = goal_result.scalar_one_or_none()
        if not goal:
            goal_result = await session.execute(
                select(DonationGoal)
                .where(DonationGoal.is_completed == False)
                .order_by(DonationGoal.start_date.asc(), DonationGoal.id.asc())
                .limit(1)
            )
            goal = goal_result.scalar_one_or_none()
        if goal:
            goal.current_amount += donation.amount
            if goal.current_amount >= goal.target_amount:
                goal.is_completed = True
        
        return donation_dict


@router.get("/records", response_model=List[DonationResponse])
async def get_donation_records(
    skip: int = 0,
    limit: int = 20,
    status_filter: Optional[DonationStatus] = None,
    current_user: User = Depends(require_admin)
):
    """获取捐赠记录列表（仅管理员）"""
    async with async_session() as session:
        query = select(DonationRecord)
        
        if status_filter:
            query = query.where(DonationRecord.payment_status == status_filter)
        
        query = query.order_by(DonationRecord.created_at.desc())
        query = query.offset(skip).limit(limit)
        
        result = await session.execute(query)
        donations = result.scalars().all()
        
        return donations


@router.get("/records/my", response_model=List[DonationResponse])
async def get_my_donation_records(
    current_user: User = Depends(get_current_user)
):
    """获取我的捐赠记录"""
    async with async_session() as session:
        query = select(DonationRecord).where(DonationRecord.user_id == current_user.id)
        query = query.order_by(DonationRecord.created_at.desc())
        
        result = await session.execute(query)
        donations = result.scalars().all()
        
        return donations


@router.put("/records/{donation_id}/status")
async def update_donation_status(
    donation_id: int,
    status: DonationStatus,
    background_tasks: BackgroundTasks,
    transaction_id: Optional[str] = None,
    current_user: User = Depends(require_admin)
):
    """更新捐赠状态（仅管理员）"""
    async with async_session() as session:
        result = await session.execute(select(DonationRecord).where(DonationRecord.id == donation_id))
        donation = result.scalar_one_or_none()
        
        if not donation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="捐赠记录不存在"
            )
        
        # 更新状态
        donation.payment_status = status
        if transaction_id:
            donation.transaction_id = transaction_id
        
        if status == DonationStatus.SUCCESS:
            donation.paid_at = datetime.utcnow()
            
            # 发送确认邮件
            if donation.donor_email and settings.email_enabled:
                background_tasks.add_task(
                    send_donation_confirmation_email,
                    donation.donor_email,
                    donation.donor_name,
                    donation.amount,
                    donation.currency
                )
            
            # 发送通知邮件给管理员
            if settings.notification_email and settings.notification_email_enabled:
                background_tasks.add_task(
                    send_donation_notification_email,
                    donation.amount,
                    donation.currency,
                    donation.donor_name,
                    donation.donor_message
                )
            
            # 自动累加到最早未完成目标
            goal_result = await session.execute(
                select(DonationGoal)
                .where(DonationGoal.is_completed == False)
                .order_by(DonationGoal.start_date.asc(), DonationGoal.id.asc())
                .limit(1)
            )
            goal = goal_result.scalar_one_or_none()
            if goal:
                goal.current_amount += donation.amount
                if goal.current_amount >= goal.target_amount:
                    goal.is_completed = True
        
        donation.updated_at = datetime.utcnow()
        await session.commit()
        await session.refresh(donation)
        
        return {"message": "状态更新成功"}


# ==================== 捐赠目标管理 ====================

@router.post("/goals", response_model=DonationGoalResponse)
async def create_donation_goal(
    goal_data: DonationGoalCreate,
    current_user: User = Depends(require_admin)
):
    """创建捐赠目标（仅管理员）"""
    async with async_session() as session:
        goal_dict = goal_data.dict()
        if not goal_dict.get("start_date"):
            goal_dict["start_date"] = datetime.utcnow()
        goal = DonationGoal(**goal_dict)
        session.add(goal)
        await session.commit()
        await session.refresh(goal)
        # 计算进度百分比
        goal.progress_percentage = float(goal.current_amount / goal.target_amount * 100)
        return goal


@router.get("/goals", response_model=List[DonationGoalResponse])
async def get_donation_goals(
    active_only: bool = True
):
    """获取捐赠目标列表"""
    async with async_session() as session:
        query = select(DonationGoal)
        if active_only:
            query = query.where(DonationGoal.is_active == True)
        query = query.order_by(DonationGoal.created_at.desc())
        result = await session.execute(query)
        goals = result.scalars().all()
        # 返回 DonationGoalResponse 列表
        goal_responses = []
        for goal in goals:
            progress = float(goal.current_amount / goal.target_amount * 100) if goal.target_amount else 0.0
            goal_responses.append(DonationGoalResponse(
                id=goal.id,
                title=goal.title,
                description=goal.description,
                target_amount=goal.target_amount,
                current_amount=goal.current_amount,
                currency=goal.currency,
                start_date=goal.start_date,
                end_date=goal.end_date,
                is_active=goal.is_active,
                is_completed=goal.is_completed,
                progress_percentage=progress,
                created_at=goal.created_at,
                updated_at=goal.updated_at
            ))
        return goal_responses


@router.put("/goals/{goal_id}", response_model=DonationGoalResponse)
async def update_donation_goal(
    goal_id: int,
    goal_update: DonationGoalUpdate,
    current_user: User = Depends(require_admin)
):
    """更新捐赠目标（仅管理员）"""
    async with async_session() as session:
        result = await session.execute(select(DonationGoal).where(DonationGoal.id == goal_id))
        goal = result.scalar_one_or_none()
        
        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="捐赠目标不存在"
            )
        
        # 更新目标
        update_data = goal_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(goal, field, value)
        
        goal.updated_at = datetime.utcnow()
        await session.commit()
        await session.refresh(goal)
        
        # 计算进度百分比
        goal.progress_percentage = float(goal.current_amount / goal.target_amount * 100)
        
        return goal


@router.delete("/goals/{goal_id}")
async def delete_donation_goal(
    goal_id: int,
    current_user: User = Depends(require_admin)
):
    """删除捐赠目标（仅管理员）"""
    async with async_session() as session:
        result = await session.execute(select(DonationGoal).where(DonationGoal.id == goal_id))
        goal = result.scalar_one_or_none()
        
        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="捐赠目标不存在"
            )
        
        await session.delete(goal)
        await session.commit()
        
        return {"message": "捐赠目标删除成功"}


# ==================== 捐赠统计 ====================

@router.get("/stats", response_model=DonationStats)
async def get_donation_stats(
    current_user: User = Depends(require_admin)
):
    """获取捐赠统计（仅管理员）"""
    async with async_session() as session:
        # 总捐赠统计
        total_result = await session.execute(
            select(
                func.count(DonationRecord.id).label("total_donations"),
                func.sum(DonationRecord.amount).label("total_amount")
            ).where(DonationRecord.payment_status == DonationStatus.SUCCESS)
        )
        total_stats = total_result.first()
        
        # 本月捐赠统计
        start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_result = await session.execute(
            select(
                func.count(DonationRecord.id).label("monthly_donations"),
                func.sum(DonationRecord.amount).label("monthly_amount")
            ).where(
                and_(
                    DonationRecord.payment_status == DonationStatus.SUCCESS,
                    DonationRecord.created_at >= start_of_month
                )
            )
        )
        monthly_stats = monthly_result.first()
        
        # 目标统计
        goals_result = await session.execute(
            select(
                func.count(DonationGoal.id).label("total_goals"),
                func.sum(func.case((DonationGoal.is_completed == True, 1), else_=0)).label("completed_goals")
            ).where(DonationGoal.is_active == True)
        )
        goals_stats = goals_result.first()
        
        return DonationStats(
            total_donations=total_stats.total_donations or 0,
            total_amount=total_stats.total_amount or Decimal('0.00'),
            currency="CNY",
            monthly_donations=monthly_stats.monthly_donations or 0,
            monthly_amount=monthly_stats.monthly_amount or Decimal('0.00'),
            active_goals=goals_stats.total_goals or 0,
            completed_goals=goals_stats.completed_goals or 0
        )


@router.get("/public-stats")
async def get_public_donation_stats():
    """获取公开捐赠统计"""
    async with async_session() as session:
        # 总捐赠统计
        total_result = await session.execute(
            select(
                func.count(DonationRecord.id).label("total_donations"),
                func.sum(DonationRecord.amount).label("total_amount")
            ).where(DonationRecord.payment_status == DonationStatus.SUCCESS)
        )
        total_stats = total_result.first()
        
        # 活跃目标数量
        goals_result = await session.execute(
            select(func.count(DonationGoal.id)).where(DonationGoal.is_active == True)
        )
        active_goals = goals_result.scalar() or 0
        
        return {
            "total_donations": total_stats.total_donations or 0,
            "total_amount": float(total_stats.total_amount or 0),
            "currency": "CNY",
            "active_goals": active_goals
        }


# ==================== 支付回调 ====================

@router.post("/callback/alipay")
async def alipay_callback():
    """支付宝回调处理"""
    # TODO: 实现支付宝回调验证和处理
    return {"message": "支付宝回调处理"}


@router.post("/callback/wechat")
async def wechat_callback(request: Request):
    """微信支付回调处理"""
    try:
        # 获取回调数据
        body = await request.body()
        notify_data = body.decode('utf-8')
        
        # 验证回调
        result = wechat_pay_v3.verify_notify(notify_data)
        
        if result:
            # 更新捐赠记录状态
            out_trade_no = result.get("out_trade_no")
            if out_trade_no:
                async with async_session() as session:
                    donation_result = await session.execute(
                        select(DonationRecord).where(DonationRecord.id == int(out_trade_no))
                    )
                    donation = donation_result.scalar_one_or_none()
                    
                    if donation:
                        donation.payment_status = DonationStatus.SUCCESS
                        donation.transaction_id = result.get("transaction_id")
                        donation.paid_at = datetime.utcnow()
                        donation.updated_at = datetime.utcnow()
                        
                        # 优先累加到 donation.goal_id 指定目标
                        goal = None
                        if donation.goal_id:
                            goal_result = await session.execute(
                                select(DonationGoal).where(DonationGoal.id == donation.goal_id)
                            )
                            goal = goal_result.scalar_one_or_none()
                        if not goal:
                            goal_result = await session.execute(
                                select(DonationGoal)
                                .where(DonationGoal.is_completed == False)
                                .order_by(DonationGoal.start_date.asc(), DonationGoal.id.asc())
                                .limit(1)
                            )
                            goal = goal_result.scalar_one_or_none()
                        if goal:
                            goal.current_amount += donation.amount
                            if goal.current_amount >= goal.target_amount:
                                goal.is_completed = True
                        
                        await session.commit()
                        
                        # 发送确认邮件
                        if donation.donor_email and settings.email_enabled:
                            await send_donation_confirmation_email(
                                donation.donor_email,
                                donation.donor_name,
                                donation.amount,
                                donation.currency
                            )
                        
                        # 发送通知邮件给管理员
                        if settings.notification_email and settings.notification_email_enabled:
                            await send_donation_notification_email(
                                donation.amount,
                                donation.currency,
                                donation.donor_name,
                                donation.donor_message
                            )
        
        return {"code": "SUCCESS", "message": "OK"}
        
    except Exception as e:
        print(f"微信支付回调处理失败: {e}")
        return {"code": "FAIL", "message": str(e)}


@router.post("/callback/paypal")
async def paypal_callback(request: Request):
    """PayPal回调处理"""
    try:
        # 获取回调数据
        body = await request.body()
        data = await request.json()
        
        # 验证回调
        headers = dict(request.headers)
        if paypal_pay.verify_webhook(headers, body.decode('utf-8')):
            # 处理订单捕获
            order_id = data.get("resource", {}).get("id")
            if order_id:
                capture_result = paypal_pay.capture_order(order_id)
                
                if capture_result.get("success"):
                    # 更新捐赠记录状态
                    reference_id = data.get("resource", {}).get("reference_id")
                    if reference_id:
                        async with async_session() as session:
                            donation_result = await session.execute(
                                select(DonationRecord).where(DonationRecord.id == int(reference_id))
                            )
                            donation = donation_result.scalar_one_or_none()
                            
                            if donation:
                                donation.payment_status = DonationStatus.SUCCESS
                                donation.transaction_id = capture_result.get("capture_id")
                                donation.paid_at = datetime.utcnow()
                                donation.updated_at = datetime.utcnow()
                                
                                # 优先累加到 donation.goal_id 指定目标
                                goal = None
                                if donation.goal_id:
                                    goal_result = await session.execute(
                                        select(DonationGoal).where(DonationGoal.id == donation.goal_id)
                                    )
                                    goal = goal_result.scalar_one_or_none()
                                if not goal:
                                    goal_result = await session.execute(
                                        select(DonationGoal)
                                        .where(DonationGoal.is_completed == False)
                                        .order_by(DonationGoal.start_date.asc(), DonationGoal.id.asc())
                                        .limit(1)
                                    )
                                    goal = goal_result.scalar_one_or_none()
                                if goal:
                                    goal.current_amount += donation.amount
                                    if goal.current_amount >= goal.target_amount:
                                        goal.is_completed = True
                                
                                await session.commit()
                                
                                # 发送确认邮件
                                if donation.donor_email and settings.email_enabled:
                                    await send_donation_confirmation_email(
                                        donation.donor_email,
                                        donation.donor_name,
                                        donation.amount,
                                        donation.currency
                                    )
                                
                                # 发送通知邮件给管理员
                                if settings.notification_email and settings.notification_email_enabled:
                                    await send_donation_notification_email(
                                        donation.amount,
                                        donation.currency,
                                        donation.donor_name,
                                        donation.donor_message
                                    )
        
        return {"message": "PayPal回调处理成功"}
        
    except Exception as e:
        print(f"PayPal回调处理失败: {e}")
        return {"error": str(e)}


# ==================== 邮件发送 ====================

async def send_donation_confirmation_email(
    email: str,
    donor_name: str,
    amount: Decimal,
    currency: str
):
    """发送捐赠确认邮件"""
    try:
        subject = "感谢您的捐赠！"
        content = f"""
        <h2>感谢您的捐赠！</h2>
        <p>亲爱的 {donor_name}，</p>
        <p>感谢您对我们博客的支持！您的捐赠已经成功处理。</p>
        <p><strong>捐赠金额：</strong>{amount} {currency}</p>
        <p>您的支持是我们继续前进的动力！</p>
        <p>祝您生活愉快！</p>
        """
        
        await email_service.send_email(email, subject, content)
        
    except Exception as e:
        print(f"发送捐赠确认邮件失败: {e}")


async def send_donation_notification_email(
    amount: Decimal,
    currency: str,
    donor_name: str,
    donor_message: Optional[str] = None
):
    """发送捐赠通知邮件给管理员"""
    try:
        subject = "收到新的捐赠！"
        content = f"""
        <h2>收到新的捐赠！</h2>
        <p><strong>捐赠者：</strong>{donor_name}</p>
        <p><strong>金额：</strong>{amount} {currency}</p>
        {f'<p><strong>留言：</strong>{donor_message}</p>' if donor_message else ''}
        <p>感谢您的关注！</p>
        """
        
        await email_service.send_email(settings.notification_email, subject, content)
        
    except Exception as e:
        print(f"发送捐赠通知邮件失败: {e}")


@router.get("/payment_methods", tags=["donation"])
async def get_payment_methods():
    async with async_session() as session:
        result = await session.execute(select(DonationConfig).limit(1))
        config = result.scalar_one_or_none()
        methods = []
        if config and getattr(config, 'alipay_enabled', False):
            methods.append({"type": "alipay", "name": "支付宝"})
        if config and getattr(config, 'wechat_enabled', False):
            methods.append({"type": "wechatpayv3", "name": "微信支付"})
        if config and getattr(config, 'paypal_enabled', False):
            methods.append({"type": "paypal", "name": "PayPal"})
        return {"methods": methods}


@router.post("/alipay/notify", tags=["donation"])
async def alipay_notify(request: Request):
    data = dict(await request.form())
    sign = data.pop("sign", None)
    # TODO: 使用alipay-sdk-python进行签名校验
    # if not alipay.verify(data, sign):
    #     return "fail"
    if data.get("trade_status") == "TRADE_SUCCESS":
        out_trade_no = data.get("out_trade_no")
        async with async_session() as session:
            result = await session.execute(select(DonationRecord).where(DonationRecord.transaction_id == out_trade_no))
            record = result.scalar_one_or_none()
            if record and record.payment_status != "PAID":
                record.payment_status = "PAID"
                record.paid_at = data.get("gmt_payment")
                await session.commit()
        return "success"
    return "fail"


@router.post("/wechat/notify", tags=["donation"])
async def wechat_notify(request: Request):
    import xmltodict
    xml_data = await request.body()
    data = xmltodict.parse(xml_data)["xml"]
    # TODO: 校验微信签名
    # if not check_wechat_sign(data, key=settings.WECHAT_API_V3_KEY):
    #     return xml_response("FAIL", "签名失败")
    if data.get("return_code") == "SUCCESS" and data.get("result_code") == "SUCCESS":
        out_trade_no = data.get("out_trade_no")
        async with async_session() as session:
            result = await session.execute(select(DonationRecord).where(DonationRecord.transaction_id == out_trade_no))
            record = result.scalar_one_or_none()
            if record and record.payment_status != "PAID":
                record.payment_status = "PAID"
                record.paid_at = data.get("time_end")
                await session.commit()
        return "<xml><return_code><![CDATA[SUCCESS]]></return_code><return_msg><![CDATA[OK]]></return_msg></xml>"
    return "<xml><return_code><![CDATA[FAIL]]></return_code><return_msg><![CDATA[支付失败]]></return_msg></xml>"


@router.post("/paypal/notify", tags=["donation"])
async def paypal_notify(request: Request):
    data = await request.json()
    # TODO: 校验PayPal签名
    event_type = data.get("event_type")
    status = data.get("resource", {}).get("status")
    invoice_id = data.get("resource", {}).get("invoice_id")
    if event_type == "PAYMENT.CAPTURE.COMPLETED" and status == "COMPLETED":
        async with async_session() as session:
            result = await session.execute(select(DonationRecord).where(DonationRecord.transaction_id == invoice_id))
            record = result.scalar_one_or_none()
            if record and record.payment_status != "PAID":
                record.payment_status = "PAID"
                record.paid_at = data.get("resource", {}).get("update_time")
                await session.commit()
        return {"status": "success"}
    return {"status": "fail"} 