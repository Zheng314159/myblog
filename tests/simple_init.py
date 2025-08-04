#!/usr/bin/env python3
"""
简单数据库初始化
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import asyncio
import os
from app.core.base import BaseModelMixin
from app.core.database import engine, async_session
from app.models.user import User, UserRole
from app.core.security import get_password_hash

# 导入所有模型以确保它们被注册
from app.models import __all_models__

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
        await conn.run_sync(BaseModelMixin.metadata.create_all)
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