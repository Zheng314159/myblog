#!/usr/bin/env python3
"""
简单数据库初始化
"""
import asyncio
import os
from sqlmodel import SQLModel
from app.core.database import engine, async_session
from app.models.user import User, UserRole
from app.core.security import get_password_hash

# 导入所有模型以确保它们被注册
from app.models import user, article, comment, tag, donation, media, system_notification

async def init_db():
    """初始化数据库"""
    print("开始初始化数据库...")
    
    # 删除旧数据库文件
    db_file = "blog.db"
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"✓ 已删除旧数据库文件: {db_file}")
    
    # 创建所有表
    print("创建数据库表...")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    print("✓ 数据库表创建完成")
    
    # 创建管理员用户
    print("创建管理员用户...")
    async with async_session() as session:
        admin_user = User(
            username="admin",
            email="admin@example.com",
            full_name="超级管理员",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True
        )
        session.add(admin_user)
        await session.commit()
        await session.refresh(admin_user)
        print("✓ 管理员用户创建成功")
        print(f"  用户名: admin")
        print(f"  密码: admin123")
    
    print("\n=== 数据库初始化完成 ===")
    print("✓ 数据库表已创建")
    print("✓ 管理员用户已创建")
    print("✓ 可以开始使用博客系统")

if __name__ == "__main__":
    asyncio.run(init_db()) 