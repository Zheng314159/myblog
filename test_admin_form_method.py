#!/usr/bin/env python3
"""
测试管理后台表单方法
"""

import requests
from bs4 import BeautifulSoup

BASE_URL = "http://localhost:8000"
ADMIN_PATH = "/jianai"

def check_form_method():
    """检查登录表单的方法"""
    print("🔍 检查登录表单方法...")
    
    try:
        response = requests.get(f"{BASE_URL}{ADMIN_PATH}/login", timeout=10)
        print(f"登录页面状态码: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找登录表单
            form = soup.find('form')
            if form:
                print(f"✅ 找到表单")
                print(f"   表单action: {form.get('action', 'N/A')}")
                print(f"   表单method: {form.get('method', 'N/A')}")
                print(f"   表单enctype: {form.get('enctype', 'N/A')}")
                
                # 检查输入字段
                username_input = form.find('input', {'name': 'username'})
                password_input = form.find('input', {'name': 'password'})
                
                if username_input:
                    print(f"✅ 找到用户名输入框: {username_input.get('type', 'N/A')}")
                else:
                    print("❌ 未找到用户名输入框")
                    
                if password_input:
                    print(f"✅ 找到密码输入框: {password_input.get('type', 'N/A')}")
                else:
                    print("❌ 未找到密码输入框")
                
                # 检查提交按钮
                submit_button = form.find('input', {'type': 'submit'}) or form.find('button', {'type': 'submit'})
                if submit_button:
                    print(f"✅ 找到提交按钮: {submit_button.get('value', 'N/A')}")
                else:
                    print("❌ 未找到提交按钮")
                
                # 如果表单方法不是POST，这就是问题所在
                if form.get('method', '').lower() != 'post':
                    print("\n❌ 问题发现：表单方法不是POST！")
                    print("   这会导致表单提交失败")
                    return False
                else:
                    print("\n✅ 表单方法正确（POST）")
                    return True
            else:
                print("❌ 未找到表单")
                return False
        else:
            print(f"❌ 无法获取登录页面: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 检查表单方法失败: {e}")
        return False

def test_form_submission_with_get():
    """测试使用GET方法提交表单（模拟错误情况）"""
    print("\n🔍 测试GET方法表单提交...")
    
    session = requests.Session()
    
    # 使用GET方法提交表单数据
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = session.get(
        f"{BASE_URL}{ADMIN_PATH}/login",
        params=login_data,
        allow_redirects=False,
        timeout=10
    )
    
    print(f"GET提交响应状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)}")
    
    if response.status_code == 302:
        print("⚠️ GET提交也有重定向，这可能不是问题")
        return True
    else:
        print("❌ GET提交没有重定向")
        return False

def test_form_submission_with_post():
    """测试使用POST方法提交表单（正确情况）"""
    print("\n🔍 测试POST方法表单提交...")
    
    session = requests.Session()
    
    # 使用POST方法提交表单数据
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
    
    print(f"POST提交响应状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)}")
    
    if response.status_code == 302:
        print("✅ POST提交有重定向，这是正确的")
        return True
    else:
        print("❌ POST提交没有重定向")
        return False

def main():
    """主函数"""
    print("🔧 管理后台表单方法测试")
    print("=" * 50)
    
    # 检查表单方法
    form_ok = check_form_method()
    
    # 测试不同提交方法
    get_ok = test_form_submission_with_get()
    post_ok = test_form_submission_with_post()
    
    print("\n" + "=" * 50)
    print("📊 测试结果总结:")
    print(f"   表单方法检查: {'✅ 通过' if form_ok else '❌ 失败'}")
    print(f"   GET提交测试: {'✅ 通过' if get_ok else '❌ 失败'}")
    print(f"   POST提交测试: {'✅ 通过' if post_ok else '❌ 失败'}")
    
    if not form_ok:
        print("\n💡 解决方案:")
        print("1. 检查sqladmin版本，可能需要升级")
        print("2. 检查是否有自定义模板覆盖了默认登录页面")
        print("3. 检查浏览器开发者工具中的表单提交情况")
        print("4. 尝试清除浏览器缓存和Cookie")

if __name__ == "__main__":
    main() 