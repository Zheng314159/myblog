#!/usr/bin/env python3
"""
解决管理后台缓存和连接问题
"""

import requests
import webbrowser
import time

BASE_URL = "http://localhost:8000"
ADMIN_PATH = "/jianai"

def check_server_health():
    """检查服务器健康状态"""
    print("🔍 检查服务器健康状态...")
    
    try:
        # 检查基础健康端点
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ 服务器健康检查通过")
            return True
        else:
            print(f"❌ 服务器健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到服务器: {e}")
        return False

def test_admin_endpoints():
    """测试管理后台各个端点"""
    print("\n🔍 测试管理后台端点...")
    
    endpoints = [
        f"{ADMIN_PATH}/login",
        f"{ADMIN_PATH}/",
        f"{ADMIN_PATH}/user/list",
        f"{ADMIN_PATH}/article/list"
    ]
    
    session = requests.Session()
    
    for endpoint in endpoints:
        try:
            print(f"   测试: {endpoint}")
            response = session.get(f"{BASE_URL}{endpoint}", timeout=10)
            print(f"     状态码: {response.status_code}")
            
            if response.status_code == 200:
                print("     ✅ 端点可访问")
            elif response.status_code == 302:
                print("     ⚠️ 重定向（可能需要登录）")
            else:
                print(f"     ❌ 端点访问失败")
                
        except Exception as e:
            print(f"     ❌ 请求失败: {e}")

def clear_browser_cache_instructions():
    """提供清除浏览器缓存的详细说明"""
    print("\n" + "=" * 60)
    print("🧹 清除浏览器缓存详细说明")
    print("=" * 60)
    
    print("\n🌐 Chrome浏览器:")
    print("   1. 按 Ctrl+Shift+Delete")
    print("   2. 时间范围选择: '所有时间'")
    print("   3. 勾选: 'Cookie及其他网站数据'")
    print("   4. 勾选: '缓存的图片和文件'")
    print("   5. 点击: '清除数据'")
    
    print("\n🦊 Firefox浏览器:")
    print("   1. 按 Ctrl+Shift+Delete")
    print("   2. 时间范围选择: '所有'")
    print("   3. 勾选: 'Cookie'")
    print("   4. 勾选: '缓存'")
    print("   5. 点击: '立即清除'")
    
    print("\n🔵 Edge浏览器:")
    print("   1. 按 Ctrl+Shift+Delete")
    print("   2. 时间范围选择: '所有时间'")
    print("   3. 勾选: 'Cookie和网站数据'")
    print("   4. 勾选: '缓存的图片和文件'")
    print("   5. 点击: '立即清除'")
    
    print("\n🍎 Safari浏览器:")
    print("   1. 菜单 -> 开发 -> 清空缓存")
    print("   2. 或者: 菜单 -> 偏好设置 -> 隐私 -> 管理网站数据")

def open_admin_with_cache_busting():
    """使用缓存破坏技术打开管理后台"""
    print("\n🌐 使用缓存破坏技术打开管理后台...")
    
    # 添加时间戳参数来破坏缓存
    timestamp = int(time.time())
    login_url = f"{BASE_URL}{ADMIN_PATH}/login?t={timestamp}"
    
    print(f"登录页面URL: {login_url}")
    
    try:
        webbrowser.open(login_url)
        print("✅ 已在浏览器中打开登录页面（带缓存破坏）")
        return True
    except Exception as e:
        print(f"❌ 无法打开浏览器: {e}")
        return False

def test_direct_access():
    """测试直接访问管理后台"""
    print("\n🔍 测试直接访问管理后台...")
    
    session = requests.Session()
    
    try:
        # 直接访问管理后台主页
        response = session.get(f"{BASE_URL}{ADMIN_PATH}/", timeout=10)
        print(f"直接访问状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 可以直接访问管理后台")
            return True
        elif response.status_code == 302:
            location = response.headers.get('Location', '')
            print(f"⚠️ 重定向到: {location}")
            if 'login' in location:
                print("✅ 正确重定向到登录页面")
                return True
        else:
            print(f"❌ 访问失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 直接访问失败: {e}")
        return False

def provide_troubleshooting_steps():
    """提供故障排除步骤"""
    print("\n" + "=" * 60)
    print("🔧 故障排除步骤")
    print("=" * 60)
    
    print("\n1️⃣ 重启服务器:")
    print("   - 停止当前服务器 (Ctrl+C)")
    print("   - 重新启动: python main.py")
    
    print("\n2️⃣ 清除浏览器缓存:")
    print("   - 按照上述说明清除缓存")
    print("   - 或者使用无痕/隐私模式")
    
    print("\n3️⃣ 尝试不同的浏览器:")
    print("   - Chrome, Firefox, Edge, Safari")
    
    print("\n4️⃣ 检查防火墙设置:")
    print("   - 确保端口8000没有被阻止")
    print("   - 检查Windows防火墙设置")
    
    print("\n5️⃣ 检查网络连接:")
    print("   - 确保localhost可以访问")
    print("   - 尝试ping localhost")
    
    print("\n6️⃣ 使用不同的URL:")
    print(f"   - http://127.0.0.1:8000{ADMIN_PATH}/login")
    print(f"   - http://localhost:8000{ADMIN_PATH}/login")

def main():
    """主函数"""
    print("🔧 管理后台缓存问题解决工具")
    print("=" * 50)
    
    # 检查服务器健康状态
    if not check_server_health():
        print("❌ 服务器可能未运行，请先启动服务器")
        return
    
    # 测试管理后台端点
    test_admin_endpoints()
    
    # 测试直接访问
    test_direct_access()
    
    # 提供清除缓存说明
    clear_browser_cache_instructions()
    
    # 提供故障排除步骤
    provide_troubleshooting_steps()
    
    # 询问是否打开浏览器
    print("\n" + "=" * 60)
    choice = input("是否要在浏览器中打开登录页面（带缓存破坏）？(y/n): ").lower().strip()
    
    if choice in ['y', 'yes', '是', 'Y']:
        if open_admin_with_cache_busting():
            print("\n✅ 已打开浏览器，请尝试登录")
            print("💡 如果仍有问题，请按照上述故障排除步骤操作")
        else:
            print("\n❌ 无法打开浏览器，请手动访问")
    else:
        print("\n💡 请手动访问登录页面")
    
    print("\n🎉 祝您使用愉快！")

if __name__ == "__main__":
    main() 