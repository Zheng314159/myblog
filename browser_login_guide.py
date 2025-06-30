#!/usr/bin/env python3
"""
浏览器登录问题排查指南
"""

import requests
import webbrowser
import time

BASE_URL = "http://localhost:8000"
ADMIN_PATH = "/jianai"

def check_server_status():
    """检查服务器状态"""
    print("🔍 检查服务器状态...")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ 服务器运行正常")
            return True
        else:
            print(f"❌ 服务器响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到服务器: {e}")
        return False

def open_admin_login():
    """打开管理后台登录页面"""
    print("\n🌐 打开管理后台登录页面...")
    
    login_url = f"{BASE_URL}{ADMIN_PATH}/login"
    print(f"登录页面URL: {login_url}")
    
    try:
        webbrowser.open(login_url)
        print("✅ 已在浏览器中打开登录页面")
        return True
    except Exception as e:
        print(f"❌ 无法打开浏览器: {e}")
        return False

def print_login_instructions():
    """打印登录说明"""
    print("\n" + "=" * 60)
    print("📋 管理后台登录说明")
    print("=" * 60)
    
    print("\n🔐 登录凭据:")
    print("   用户名: admin")
    print("   密码: admin123")
    
    print("\n🌐 登录页面:")
    print(f"   {BASE_URL}{ADMIN_PATH}/login")
    
    print("\n📝 登录步骤:")
    print("   1. 在浏览器中访问上述URL")
    print("   2. 输入用户名: admin")
    print("   3. 输入密码: admin123")
    print("   4. 点击登录按钮")
    print("   5. 应该重定向到管理后台主页")
    
    print("\n🔧 如果登录失败，请尝试:")
    print("   1. 清除浏览器缓存和Cookie")
    print("      - Chrome: Ctrl+Shift+Delete")
    print("      - Firefox: Ctrl+Shift+Delete")
    print("      - Edge: Ctrl+Shift+Delete")
    
    print("\n   2. 使用无痕/隐私模式")
    print("      - Chrome: Ctrl+Shift+N")
    print("      - Firefox: Ctrl+Shift+P")
    print("      - Edge: Ctrl+Shift+N")
    
    print("\n   3. 尝试不同的浏览器")
    print("      - Chrome, Firefox, Edge, Safari")
    
    print("\n   4. 检查浏览器控制台")
    print("      - 按F12打开开发者工具")
    print("      - 查看Console标签页的错误信息")
    
    print("\n   5. 检查网络连接")
    print("      - 确保服务器正在运行")
    print("      - 确保端口8000没有被防火墙阻止")

def test_direct_access():
    """测试直接访问管理后台"""
    print("\n🔍 测试直接访问管理后台...")
    
    try:
        # 测试登录页面
        response = requests.get(f"{BASE_URL}{ADMIN_PATH}/login", timeout=10)
        print(f"登录页面状态码: {response.status_code}")
        
        # 测试管理后台主页
        response = requests.get(f"{BASE_URL}{ADMIN_PATH}/", timeout=10)
        print(f"管理后台主页状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 管理后台页面可以访问")
        elif response.status_code == 302:
            print("✅ 管理后台重定向到登录页面（正常）")
        else:
            print(f"❌ 管理后台访问异常: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 访问测试失败: {e}")

def main():
    """主函数"""
    print("🔧 浏览器登录问题排查指南")
    print("=" * 60)
    
    # 检查服务器状态
    if not check_server_status():
        print("\n❌ 服务器未运行，请先启动服务器")
        return
    
    # 测试直接访问
    test_direct_access()
    
    # 打印登录说明
    print_login_instructions()
    
    # 询问是否打开浏览器
    print("\n" + "=" * 60)
    choice = input("是否要在浏览器中打开登录页面？(y/n): ").lower().strip()
    
    if choice in ['y', 'yes', '是']:
        open_admin_login()
        print("\n💡 提示:")
        print("1. 如果浏览器没有自动打开，请手动访问:")
        print(f"   {BASE_URL}{ADMIN_PATH}/login")
        print("2. 使用上述登录凭据进行测试")
        print("3. 如果仍然失败，请检查浏览器控制台错误")
    else:
        print(f"\n请手动访问: {BASE_URL}{ADMIN_PATH}/login")

if __name__ == "__main__":
    main() 