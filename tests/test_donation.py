#!/usr/bin/env python3
"""
测试捐赠功能
"""
import asyncio
import sys
import os

# 添加项目路径
sys.path.append(os.path.abspath('.'))

from app.core.database import async_session
from app.models.donation import DonationConfig, DonationRecord, DonationGoal
from app.models.user import User, UserRole
from app.models.article import Article
from app.models.comment import Comment
from app.models.tag import Tag, ArticleTag
from app.models.media import MediaFile
from app.models.system_notification import SystemNotification
from sqlmodel import select
from decimal import Decimal
from datetime import datetime, timedelta

async def test_donation():
    """测试捐赠功能"""
    print("=== 测试捐赠功能 ===")
    
    async with async_session() as session:
        # 1. 检查捐赠配置
        print("\n1. 检查捐赠配置...")
        result = await session.execute(select(DonationConfig).limit(1))
        config = result.scalar_one_or_none()
        
        if config:
            print(f"✅ 捐赠配置存在")
            print(f"   - 标题: {config.title}")
            print(f"   - 启用状态: {config.is_enabled}")
            print(f"   - 支付宝: {config.alipay_enabled}")
            print(f"   - 微信: {config.wechat_enabled}")
            print(f"   - PayPal: {config.paypal_enabled}")
            print(f"   - 预设金额: {config.preset_amounts}")
        else:
            print("❌ 捐赠配置不存在")
            return
        
        # 2. 创建测试用户（如果不存在）
        print("\n2. 检查测试用户...")
        result = await session.execute(select(User).where(User.username == "testuser"))
        user = result.scalar_one_or_none()
        
        if not user:
            print("创建测试用户...")
            user = User(
                username="testuser",
                email="test@example.com",
                full_name="测试用户",
                role=UserRole.USER,
                is_active=True
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            print(f"✅ 创建测试用户: {user.username}")
        else:
            print(f"✅ 测试用户已存在: {user.username}")
        
        # 3. 创建测试捐赠目标
        print("\n3. 创建测试捐赠目标...")
        goal = DonationGoal(
            title="服务器升级",
            description="为博客系统升级服务器配置，提升性能和稳定性",
            target_amount=Decimal('1000.00'),
            current_amount=Decimal('250.00'),
            currency="CNY",
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=30),
            is_active=True,
            is_completed=False
        )
        session.add(goal)
        await session.commit()
        await session.refresh(goal)
        print(f"✅ 创建捐赠目标: {goal.title}")
        print(f"   - 目标金额: ¥{goal.target_amount}")
        print(f"   - 当前金额: ¥{goal.current_amount}")
        print(f"   - 进度: {float(goal.current_amount / goal.target_amount * 100):.1f}%")
        
        # 4. 创建测试捐赠记录
        print("\n4. 创建测试捐赠记录...")
        donation = DonationRecord(
            donor_name="张三",
            donor_email="zhangsan@example.com",
            donor_message="支持你们，继续加油！",
            is_anonymous=False,
            amount=Decimal('50.00'),
            currency="CNY",
            payment_method="ALIPAY",
            payment_status="SUCCESS",
            transaction_id="TEST_123456",
            user_id=user.id,
            paid_at=datetime.utcnow()
        )
        session.add(donation)
        await session.commit()
        await session.refresh(donation)
        print(f"✅ 创建捐赠记录")
        print(f"   - 捐赠者: {donation.donor_name}")
        print(f"   - 金额: ¥{donation.amount}")
        print(f"   - 支付方式: {donation.payment_method}")
        print(f"   - 状态: {donation.payment_status}")
        
        # 5. 更新统计信息
        print("\n5. 更新统计信息...")
        config.total_donations += 1
        config.total_amount += donation.amount
        config.updated_at = datetime.utcnow()
        await session.commit()
        print(f"✅ 更新统计信息")
        print(f"   - 总捐赠次数: {config.total_donations}")
        print(f"   - 总捐赠金额: ¥{config.total_amount}")
        
        # 6. 查询捐赠记录
        print("\n6. 查询捐赠记录...")
        result = await session.execute(select(DonationRecord))
        donations = result.scalars().all()
        print(f"✅ 共有 {len(donations)} 条捐赠记录")
        
        for i, d in enumerate(donations, 1):
            print(f"   {i}. {d.donor_name} - ¥{d.amount} - {d.payment_method} - {d.payment_status}")
        
        # 7. 查询捐赠目标
        print("\n7. 查询捐赠目标...")
        result = await session.execute(select(DonationGoal))
        goals = result.scalars().all()
        print(f"✅ 共有 {len(goals)} 个捐赠目标")
        
        for i, g in enumerate(goals, 1):
            progress = float(g.current_amount / g.target_amount * 100)
            status = "已完成" if g.is_completed else "进行中"
            print(f"   {i}. {g.title} - ¥{g.current_amount}/{g.target_amount} ({progress:.1f}%) - {status}")
        
        print("\n=== 测试完成 ===")
        print("🎉 捐赠功能测试成功！")
        print("\n现在可以：")
        print("1. 访问 http://localhost:8000/docs 查看API文档")
        print("2. 访问 http://localhost:8000/admin 管理捐赠")
        print("3. 启动前端访问捐赠页面")

if __name__ == "__main__":
    asyncio.run(test_donation()) 