#!/usr/bin/env python3
"""
检查数据库中的管理员用户角色
"""

import sqlite3
import asyncio
from app.core.database import async_session
from app.models.user import User
from sqlalchemy import select

def check_sqlite_users():
    """直接检查SQLite数据库中的用户"""
    print("🔍 直接检查SQLite数据库中的用户...")
    
    try:
        conn = sqlite3.connect('blog.db')
        cursor = conn.cursor()
        
        # 查看user表结构
        cursor.execute("PRAGMA table_info(user)")
        columns = cursor.fetchall()
        print("📋 user表结构:")
        for col in columns:
            print(f"   {col[1]} ({col[2]})")
        
        # 查看所有用户
        cursor.execute("SELECT id, username, email, role, is_active, created_at FROM user")
        users = cursor.fetchall()
        
        print(f"\n👥 数据库中的用户 ({len(users)}个):")
        for user in users:
            print(f"   ID: {user[0]}, 用户名: {user[1]}, 邮箱: {user[2]}, 角色: '{user[3]}', 激活: {user[4]}, 创建时间: {user[5]}")
        
        # 检查admin用户
        admin_users = [u for u in users if u[1] == 'admin']
        if admin_users:
            admin = admin_users[0]
            print(f"\n🔑 admin用户详情:")
            print(f"   ID: {admin[0]}")
            print(f"   用户名: {admin[1]}")
            print(f"   邮箱: {admin[2]}")
            print(f"   角色: '{admin[3]}' (类型: {type(admin[3])})")
            print(f"   激活状态: {admin[4]}")
            print(f"   创建时间: {admin[5]}")
            
            # 检查角色是否正确
            if admin[3] == 'admin':
                print("✅ admin用户角色正确 (小写)")
            elif admin[3] == 'ADMIN':
                print("❌ admin用户角色错误 (大写，需要改为小写)")
            elif admin[3] == 'Admin':
                print("❌ admin用户角色错误 (首字母大写，需要改为小写)")
            else:
                print(f"❌ admin用户角色异常: '{admin[3]}'")
        else:
            print("❌ 未找到admin用户")
        
        conn.close()
        return users
        
    except Exception as e:
        print(f"❌ 检查SQLite数据库失败: {e}")
        return None

async def check_async_users():
    """通过SQLModel检查用户"""
    print("\n🔍 通过SQLModel检查用户...")
    
    try:
        async with async_session() as session:
            result = await session.execute(select(User))
            users = result.scalars().all()
            
            print(f"👥 SQLModel查询到的用户 ({len(users)}个):")
            for user in users:
                print(f"   ID: {user.id}, 用户名: {user.username}, 邮箱: {user.email}, 角色: {user.role}, 激活: {user.is_active}")
            
            # 检查admin用户
            admin_user = next((u for u in users if u.username == 'admin'), None)
            if admin_user:
                print(f"\n🔑 admin用户详情 (SQLModel):")
                print(f"   ID: {admin_user.id}")
                print(f"   用户名: {admin_user.username}")
                print(f"   邮箱: {admin_user.email}")
                print(f"   角色: {admin_user.role} (类型: {type(admin_user.role)})")
                print(f"   角色值: {admin_user.role.value if hasattr(admin_user.role, 'value') else 'N/A'}")
                print(f"   激活状态: {admin_user.is_active}")
                
                # 检查角色是否正确
                if hasattr(admin_user.role, 'value'):
                    role_value = admin_user.role.value
                    if role_value == 'admin':
                        print("✅ admin用户角色正确 (小写)")
                    elif role_value == 'ADMIN':
                        print("❌ admin用户角色错误 (大写，需要改为小写)")
                    elif role_value == 'Admin':
                        print("❌ admin用户角色错误 (首字母大写，需要改为小写)")
                    else:
                        print(f"❌ admin用户角色异常: '{role_value}'")
                else:
                    print(f"❌ 无法获取角色值")
            
            return users
            
    except Exception as e:
        print(f"❌ SQLModel查询失败: {e}")
        return None

def fix_admin_role():
    """修复admin用户角色为小写"""
    print("\n🔧 修复admin用户角色...")
    
    try:
        conn = sqlite3.connect('blog.db')
        cursor = conn.cursor()
        
        # 检查当前admin用户角色
        cursor.execute("SELECT role FROM user WHERE username = 'admin'")
        result = cursor.fetchone()
        
        if result:
            current_role = result[0]
            print(f"   当前admin角色: '{current_role}'")
            
            if current_role != 'admin':
                # 更新为小写admin
                cursor.execute("UPDATE user SET role = 'admin' WHERE username = 'admin'")
                conn.commit()
                print("✅ 已将admin用户角色更新为小写")
                
                # 验证更新
                cursor.execute("SELECT role FROM user WHERE username = 'admin'")
                new_role = cursor.fetchone()[0]
                print(f"   更新后admin角色: '{new_role}'")
            else:
                print("✅ admin用户角色已经是小写，无需修改")
        else:
            print("❌ 未找到admin用户")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 修复admin角色失败: {e}")

def main():
    """主函数"""
    print("🔧 检查管理员用户角色")
    print("=" * 50)
    
    # 检查数据库中的用户
    sqlite_users = check_sqlite_users()
    
    # 通过SQLModel检查用户
    asyncio.run(check_async_users())
    
    # 询问是否修复角色
    if sqlite_users:
        admin_users = [u for u in sqlite_users if u[1] == 'admin']
        if admin_users and admin_users[0][3] != 'admin':
            print("\n" + "=" * 50)
            print("💡 发现admin用户角色不是小写，是否要修复？")
            print("   这将把admin用户的角色从大写改为小写")
            
            # 自动修复
            fix_admin_role()
    
    print("\n" + "=" * 50)
    print("📋 检查完成")
    print("💡 如果admin用户角色不是小写'admin'，管理后台登录会失败")

if __name__ == "__main__":
    main() 