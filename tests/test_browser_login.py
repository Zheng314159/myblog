#!/usr/bin/env python3
"""
模拟浏览器登录行为测试
"""

import requests
import json

BASE_URL = "http://localhost:8000"
ADMIN_PATH = "/jianai"

def test_browser_login_simulation():
    """模拟浏览器登录行为"""
    print("🌐 模拟浏览器登录行为测试")
    print("=" * 50)
    
    # 创建会话对象，模拟浏览器行为
    session = requests.Session()
    
    # 1. 访问登录页面
    print("1. 访问登录页面...")
    try:
        response = session.get(f"{BASE_URL}{ADMIN_PATH}/login", timeout=10)
        print(f"   状态码: {response.status_code}")
        print(f"   Cookie: {dict(session.cookies)}")
        
        if response.status_code != 200:
            print("❌ 无法访问登录页面")
            return False
            
    except Exception as e:
        print(f"❌ 访问登录页面失败: {e}")
        return False
    
    # 2. 提交登录表单
    print("\n2. 提交登录表单...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
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
            print(f"   页面标题: {response.text[:200]}...")
            
            if response.status_code == 200:
                print("✅ 登录成功，可以访问管理后台")
                return True
            else:
                print("❌ 重定向后无法访问管理后台")
                return False
        else:
            print("❌ 登录失败")
            return False
            
    except Exception as e:
        print(f"❌ 登录请求失败: {e}")
        return False

def test_different_browsers():
    """测试不同浏览器的User-Agent"""
    print("\n🔍 测试不同浏览器User-Agent...")
    
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59 Safari/537.36"
    ]
    
    for i, user_agent in enumerate(user_agents, 1):
        print(f"\n测试浏览器 {i}:")
        session = requests.Session()
        session.headers.update({'User-Agent': user_agent})
        
        try:
            # 访问登录页面
            response = session.get(f"{BASE_URL}{ADMIN_PATH}/login", timeout=10)
            print(f"   登录页面状态码: {response.status_code}")
            
            # 提交登录
            login_data = {"username": "admin", "password": "admin123"}
            response = session.post(
                f"{BASE_URL}{ADMIN_PATH}/login",
                data=login_data,
                allow_redirects=False,
                timeout=10
            )
            
            print(f"   登录状态码: {response.status_code}")
            
            if response.status_code == 302:
                print("   ✅ 登录成功")
            else:
                print("   ❌ 登录失败")
                
        except Exception as e:
            print(f"   ❌ 测试失败: {e}")

def test_cookie_handling():
    """测试Cookie处理"""
    print("\n🍪 测试Cookie处理...")
    
    session = requests.Session()
    
    # 清除所有Cookie
    session.cookies.clear()
    print("1. 清除Cookie")
    
    # 访问登录页面
    response = session.get(f"{BASE_URL}{ADMIN_PATH}/login", timeout=10)
    print(f"2. 访问登录页面，Cookie: {dict(session.cookies)}")
    
    # 提交登录
    login_data = {"username": "admin", "password": "admin123"}
    response = session.post(
        f"{BASE_URL}{ADMIN_PATH}/login",
        data=login_data,
        allow_redirects=False,
        timeout=10
    )
    
    print(f"3. 登录后Cookie: {dict(session.cookies)}")
    
    if response.status_code == 302:
        # 跟随重定向
        location = response.headers.get('Location', '')
        response = session.get(location, timeout=10)
        print(f"4. 重定向后状态码: {response.status_code}")
        print(f"5. 最终Cookie: {dict(session.cookies)}")
        
        if response.status_code == 200:
            print("✅ Cookie处理正常")
            return True
        else:
            print("❌ Cookie处理异常")
            return False
    else:
        print("❌ 登录失败")
        return False

def main():
    """主函数"""
    print("🔧 浏览器登录行为测试")
    print("=" * 60)
    
    # 测试基本浏览器登录
    if test_browser_login_simulation():
        print("\n✅ 基本浏览器登录测试通过")
    else:
        print("\n❌ 基本浏览器登录测试失败")
    
    # 测试不同浏览器
    test_different_browsers()
    
    # 测试Cookie处理
    if test_cookie_handling():
        print("\n✅ Cookie处理测试通过")
    else:
        print("\n❌ Cookie处理测试失败")
    
    print("\n" + "=" * 60)
    print("💡 如果浏览器登录仍然失败，请尝试:")
    print("1. 清除浏览器缓存和Cookie")
    print("2. 使用无痕/隐私模式")
    print("3. 尝试不同的浏览器")
    print("4. 检查浏览器控制台错误")
    print("5. 确认服务器正在运行")

if __name__ == "__main__":
    main() 