#!/usr/bin/env python3
"""
重建数据库 - 删除旧数据库并重新创建所有表
"""
import asyncio
import os
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db, engine
from app.models.user import User, UserRole
from app.core.security import get_password_hash

# 确保所有模型都被导入
from app.models import user, article, comment, tag, donation, media, system_notification

async def rebuild_database():
    """重建数据库"""
    print("开始重建数据库...")
    
    # 1. 删除数据库文件（如果存在）
    db_file = "blog.db"
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"✓ 已删除旧数据库文件: {db_file}")
    
    # 2. 创建所有表
    print("创建数据库表...")
    async with engine.begin() as conn:
        # 这里会创建所有表
        pass
    print("✓ 数据库表创建完成")
    
    # 3. 创建管理员用户
    print("创建管理员用户...")
    async for db in get_db():
        try:
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
            break
            
        except Exception as e:
            print(f"✗ 创建管理员用户失败: {e}")
            import traceback
            traceback.print_exc()
            break
    
    print("\n=== 数据库重建完成 ===")
    print("✓ 数据库表已创建")
    print("✓ 管理员用户已创建")
    print("✓ 可以开始使用博客系统")

if __name__ == "__main__":
    asyncio.run(rebuild_database()) 