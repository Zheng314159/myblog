#!/usr/bin/env python3
"""
修复数据库中的管理员角色，使其与UserRole枚举匹配
"""

import sqlite3
import asyncio
from app.core.database import async_session
from app.models.user import User, UserRole
from sqlalchemy import select, update

def fix_database_roles():
    """修复数据库中的角色值"""
    print("🔧 修复数据库中的角色值...")
    
    try:
        conn = sqlite3.connect('blog.db')
        cursor = conn.cursor()
        
        # 查看当前所有角色
        cursor.execute("SELECT username, role FROM user")
        users = cursor.fetchall()
        
        print("📋 修复前的用户角色:")
        for user in users:
            print(f"   {user[0]}: '{user[1]}'")
        
        # 修复角色映射
        role_mapping = {
            'ADMIN': 'admin',
            'MODERATOR': 'moderator', 
            'USER': 'user'
        }
        
        # 更新所有用户的角色
        for old_role, new_role in role_mapping.items():
            cursor.execute(
                "UPDATE user SET role = ? WHERE role = ?",
                (new_role, old_role)
            )
            affected = cursor.rowcount
            if affected > 0:
                print(f"✅ 将 {affected} 个用户的角色从 '{old_role}' 更新为 '{new_role}'")
        
        conn.commit()
        
        # 查看修复后的角色
        cursor.execute("SELECT username, role FROM user")
        users_after = cursor.fetchall()
        
        print("\n📋 修复后的用户角色:")
        for user in users_after:
            print(f"   {user[0]}: '{user[1]}'")
        
        conn.close()
        print("\n✅ 数据库角色修复完成")
        
    except Exception as e:
        print(f"❌ 修复数据库角色失败: {e}")

async def test_admin_login():
    """测试管理员登录"""
    print("\n🔍 测试管理员登录...")
    
    try:
        async with async_session() as session:
            # 查找admin用户
            result = await session.execute(select(User).where(User.username == "admin"))
            user = result.scalar_one_or_none()
            
            if user:
                print(f"✅ 找到admin用户: {user.username}")
                print(f"   角色: {user.role} (类型: {type(user.role)})")
                print(f"   激活状态: {user.is_active}")
                
                # 检查角色是否正确
                if user.role == UserRole.ADMIN:
                    print("✅ admin用户角色正确")
                    return True
                else:
                    print(f"❌ admin用户角色错误: {user.role}")
                    return False
            else:
                print("❌ 未找到admin用户")
                return False
                
    except Exception as e:
        print(f"❌ 测试管理员登录失败: {e}")
        return False

def main():
    """主函数"""
    print("🔧 修复管理员角色问题")
    print("=" * 50)
    
    # 修复数据库角色
    fix_database_roles()
    
    # 测试管理员登录
    asyncio.run(test_admin_login())
    
    print("\n" + "=" * 50)
    print("📋 修复完成")
    print("💡 现在可以尝试登录管理后台了")
    print("   用户名: admin")
    print("   密码: admin123")

if __name__ == "__main__":
    main() 