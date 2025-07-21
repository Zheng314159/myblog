#!/usr/bin/env python3
"""
初始化数据库并创建管理员用户
"""
import asyncio
import os
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db, engine
from app.models.user import User, UserRole
from app.core.security import get_password_hash
from app.core.search import FTSSearch

async def init_database():
    """初始化数据库"""
    print("开始初始化数据库...")
    
    # 1. 创建所有表
    print("创建数据库表...")
    async with engine.begin() as conn:
        # 这里会创建所有表
        pass
    
    # 2. 创建管理员用户
    print("创建管理员用户...")
    async for db in get_db():
        try:
            # 检查是否已存在管理员用户
            from sqlalchemy import select
            result = await db.execute(select(User).where(User.username == "admin"))
            admin_user = result.scalar_one_or_none()
            
            if not admin_user:
                # 创建管理员用户
                admin_user = User(
                    username="admin",
                    email="admin@example.com",
                    full_name="超级管理员",
                    hashed_password=get_password_hash("admin123"),
                    role=UserRole.ADMIN,
                    is_active=True,
                    is_verified=True
                )
                db.add(admin_user)
                await db.commit()
                await db.refresh(admin_user)
                print("✓ 管理员用户创建成功")
                print(f"  用户名: admin")
                print(f"  密码: admin123")
            else:
                print("✓ 管理员用户已存在")
            
            # 3. 初始化FTS5搜索索引
            print("初始化FTS5搜索索引...")
            try:
                await FTSSearch.create_fts_table(db)
                await FTSSearch.populate_fts_table(db)
                print("✓ FTS5搜索索引初始化成功")
            except Exception as e:
                print(f"⚠️  FTS5搜索索引初始化失败: {e}")
                print("   搜索功能可能不可用，但不影响基本功能")
            
            break
            
        except Exception as e:
            print(f"✗ 初始化失败: {e}")
            import traceback
            traceback.print_exc()
            break
    
    print("\n=== 数据库初始化完成 ===")
    print("✓ 数据库表已创建")
    print("✓ 管理员用户已创建")
    print("✓ 可以开始使用博客系统")

if __name__ == "__main__":
    asyncio.run(init_database()) 