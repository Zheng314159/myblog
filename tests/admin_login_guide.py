#!/usr/bin/env python3
"""
管理后台登录指南
"""

import webbrowser
import time

BASE_URL = "http://localhost:8000"
ADMIN_PATH = "/jianai"

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
    
    print("\n📊 可用的管理员账户:")
    print("   - admin / admin123")
    print("   - admin1 / admin123")
    print("   - admin2 / admin123")
    print("   - admin_sql / admin123")
    
    print("\n🎯 管理后台功能:")
    print("   - 用户管理")
    print("   - 文章管理")
    print("   - 标签管理")
    print("   - 评论管理")

def main():
    """主函数"""
    print("🔧 管理后台登录指南")
    print("=" * 50)
    
    # 打印登录说明
    print_login_instructions()
    
    # 询问是否打开浏览器
    print("\n" + "=" * 60)
    choice = input("是否要在浏览器中打开登录页面？(y/n): ").lower().strip()
    
    if choice in ['y', 'yes', '是', 'Y']:
        if open_admin_login():
            print("\n✅ 已打开浏览器，请按照上述说明进行登录")
        else:
            print("\n❌ 无法打开浏览器，请手动访问登录页面")
    else:
        print("\n💡 请手动在浏览器中访问登录页面")
    
    print("\n🎉 祝您使用愉快！")

if __name__ == "__main__":
    main() 