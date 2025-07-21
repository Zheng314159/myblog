#!/usr/bin/env python3
"""
测试管理后台删除功能
"""

import requests
import json
import sqlite3

def test_admin_login():
    """测试管理员登录"""
    print("🔐 测试管理员登录...")
    
    try:
        response = requests.post(
            "http://localhost:8000/admin/login",
            data={
                "username": "admin",
                "password": "admin123"
            },
            allow_redirects=False
        )
        
        print(f"登录响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 302:  # 重定向到管理后台
            print("✅ 登录成功，重定向到管理后台")
            return response.cookies
        else:
            print(f"❌ 登录失败: {response.text[:200]}")
            return None
            
    except Exception as e:
        print(f"❌ 登录请求失败: {e}")
        return None

def check_database():
    """检查数据库中的用户"""
    print("\n🔍 检查数据库中的用户...")
    
    try:
        conn = sqlite3.connect('blog.db')
        cursor = conn.cursor()
        
        # 检查所有用户
        cursor.execute("SELECT id, username, role, is_active FROM user")
        users = cursor.fetchall()
        
        print(f"总用户数: {len(users)}")
        for user in users:
            user_id, username, role, is_active = user
            print(f"  - ID: {user_id}, 用户名: {username}, 角色: {role}, 状态: {is_active}")
        
        # 检查管理员用户
        cursor.execute("SELECT id, username, role FROM user WHERE role = 'ADMIN'")
        admin_users = cursor.fetchall()
        print(f"\n管理员用户数: {len(admin_users)}")
        for user in admin_users:
            print(f"  - ID: {user[0]}, 用户名: {user[1]}, 角色: {user[2]}")
        
        conn.close()
        return users, admin_users
        
    except Exception as e:
        print(f"❌ 数据库检查失败: {e}")
        return [], []

def test_admin_pages(cookies):
    """测试管理后台页面"""
    print("\n🔍 测试管理后台页面...")
    
    try:
        # 测试用户列表页面
        response = requests.get(
            "http://localhost:8000/admin/user/list",
            cookies=cookies
        )
        print(f"用户列表页面状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 用户列表页面可访问")
            # 检查页面内容是否包含删除按钮
            if "delete" in response.text.lower():
                print("✅ 页面包含删除相关内容")
            else:
                print("❌ 页面不包含删除相关内容")
        else:
            print(f"❌ 用户列表页面不可访问: {response.text[:100]}")
            
    except Exception as e:
        print(f"❌ 管理后台页面测试失败: {e}")

def test_delete_endpoints(cookies):
    """测试删除端点"""
    print("\n🔍 测试删除端点...")
    
    try:
        # 测试用户删除端点
        response = requests.post(
            "http://localhost:8000/admin/user/delete",
            cookies=cookies,
            data={"pks": [999]}  # 测试删除不存在的用户
        )
        print(f"用户删除端点状态码: {response.status_code}")
        print(f"响应内容: {response.text[:200]}")
        
        # 测试文章删除端点
        response = requests.post(
            "http://localhost:8000/admin/article/delete",
            cookies=cookies,
            data={"pks": [999]}  # 测试删除不存在的文章
        )
        print(f"文章删除端点状态码: {response.status_code}")
        print(f"响应内容: {response.text[:200]}")
        
    except Exception as e:
        print(f"❌ 删除端点测试失败: {e}")

def check_admin_config():
    """检查管理后台配置"""
    print("\n🔍 检查管理后台配置...")
    
    try:
        # 检查main.py中的管理后台配置
        with open('main.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 检查can_delete设置
        if 'can_delete = True' in content:
            print("✅ 管理后台配置了can_delete = True")
        else:
            print("❌ 管理后台未配置can_delete = True")
            
        # 检查delete_model方法
        if 'delete_model' in content:
            print("✅ 管理后台配置了delete_model方法")
        else:
            print("❌ 管理后台未配置delete_model方法")
            
        # 检查SessionMiddleware
        if 'SessionMiddleware' in content:
            print("✅ 配置了SessionMiddleware")
        else:
            print("❌ 未配置SessionMiddleware")
            
    except Exception as e:
        print(f"❌ 配置文件检查失败: {e}")

if __name__ == "__main__":
    print("🔧 管理后台删除功能测试")
    print("=" * 50)
    
    # 检查数据库
    users, admin_users = check_database()
    
    # 检查配置
    check_admin_config()
    
    # 测试登录
    cookies = test_admin_login()
    
    if cookies:
        # 测试删除端点
        test_delete_endpoints(cookies)
        
        # 测试管理后台页面
        test_admin_pages(cookies)
    
    print("\n" + "=" * 50)
    print("测试完成") 