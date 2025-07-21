import asyncio
from datetime import datetime
from app.core.database import async_session
from app.models.user import User, UserRole
from app.models.media import MediaFile  # 显式导入，确保关系注册
from app.core.security import get_password_hash

async def create_admin():
    async with async_session() as session:
        username = 'admin'
        email = 'admin@example.com'
        password = 'admin123'  # 可修改
        hashed_password = get_password_hash(password)
        now = datetime.now()
        user = User(
            username=username,
            email=email,
            full_name='管理员',
            role=UserRole.ADMIN,
            is_active=True,
            hashed_password=hashed_password,
            created_at=now,
            updated_at=now
        )
        session.add(user)
        await session.commit()
        print(f"管理员账号已创建: 用户名={username} 密码={password}")

if __name__ == '__main__':
    asyncio.run(create_admin()) 