#!/usr/bin/env python3
"""
测试修复后的管理后台登录
"""

import requests

BASE_URL = "http://localhost:8000"
ADMIN_PATH = "/jianai"

def test_admin_login():
    """测试管理后台登录"""
    print("🔍 测试管理后台登录...")
    
    session = requests.Session()
    
    # 1. 获取登录页面
    print("1. 获取登录页面...")
    response = session.get(f"{BASE_URL}{ADMIN_PATH}/login", timeout=10)
    print(f"   状态码: {response.status_code}")
    
    if response.status_code != 200:
        print("❌ 无法获取登录页面")
        return False
    
    # 2. 提交登录表单
    print("\n2. 提交登录表单...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = session.post(
        f"{BASE_URL}{ADMIN_PATH}/login",
        data=login_data,
        allow_redirects=False,
        timeout=10
    )
    
    print(f"   登录响应状态码: {response.status_code}")
    print(f"   响应头: {dict(response.headers)}")
    print(f"   Cookie: {dict(session.cookies)}")
    
    if response.status_code == 302:
        location = response.headers.get('Location', '')
        print(f"   重定向到: {location}")
        
        # 3. 跟随重定向
        print("\n3. 跟随重定向...")
        response = session.get(location, timeout=10)
        print(f"   重定向后状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 登录成功，可以访问管理后台")
            
            # 检查页面内容
            if "博客管理系统" in response.text or "用户管理" in response.text:
                print("✅ 确认进入管理后台页面")
                return True
            else:
                print("⚠️ 页面内容可能不是管理后台")
                return False
        else:
            print("❌ 重定向后无法访问管理后台")
            return False
    else:
        print("❌ 登录失败，没有重定向")
        return False

def test_admin_dashboard():
    """测试直接访问管理后台"""
    print("\n🔍 测试直接访问管理后台...")
    
    session = requests.Session()
    
    # 直接访问管理后台主页
    response = session.get(f"{BASE_URL}{ADMIN_PATH}/", timeout=10)
    print(f"   状态码: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ 可以直接访问管理后台")
        return True
    elif response.status_code == 302:
        location = response.headers.get('Location', '')
        print(f"   重定向到: {location}")
        if 'login' in location:
            print("✅ 正确重定向到登录页面（未登录状态）")
            return True
        else:
            print("❌ 重定向到未知页面")
            return False
    else:
        print("❌ 访问管理后台失败")
        return False

def main():
    """主函数"""
    print("🔧 测试修复后的管理后台登录")
    print("=" * 50)
    
    # 测试直接访问
    dashboard_ok = test_admin_dashboard()
    
    # 测试登录
    login_ok = test_admin_login()
    
    print("\n" + "=" * 50)
    print("📊 测试结果总结:")
    print(f"   管理后台访问: {'✅ 通过' if dashboard_ok else '❌ 失败'}")
    print(f"   登录功能: {'✅ 通过' if login_ok else '❌ 失败'}")
    
    if login_ok:
        print("\n🎉 管理后台登录修复成功！")
        print("💡 现在可以在浏览器中正常登录管理后台了")
        print(f"   登录地址: {BASE_URL}{ADMIN_PATH}/login")
        print("   用户名: admin")
        print("   密码: admin123")
    else:
        print("\n❌ 管理后台登录仍有问题，需要进一步排查")

if __name__ == "__main__":
    main() 