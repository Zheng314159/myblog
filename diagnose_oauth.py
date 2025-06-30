#!/usr/bin/env python3
"""
OAuth 功能诊断脚本
"""

import requests
import json
import time

def test_backend_health():
    """测试后端健康状态"""
    print("=== 后端健康检查 ===")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            print("✅ 后端服务器正常运行")
            return True
        else:
            print(f"❌ 后端服务器异常: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到后端服务器: {e}")
        return False

def test_frontend_proxy():
    """测试前端代理"""
    print("\n=== 前端代理测试 ===")
    try:
        # 测试通过前端代理访问后端API
        response = requests.get("http://localhost:3000/api/v1/oauth/providers", timeout=5)
        print(f"前端代理状态码: {response.status_code}")
        if response.status_code == 200:
            print("✅ 前端代理工作正常")
            data = response.json()
            print(f"OAuth提供商: {[p['display_name'] for p in data.get('providers', [])]}")
            return True
        else:
            print(f"❌ 前端代理异常: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 前端代理测试失败: {e}")
        return False

def test_oauth_endpoints():
    """测试OAuth端点"""
    print("\n=== OAuth端点测试 ===")
    
    # 测试GitHub OAuth
    try:
        response = requests.get("http://localhost:8000/api/v1/oauth/github/login", 
                              allow_redirects=False, timeout=5)
        print(f"GitHub OAuth状态码: {response.status_code}")
        if response.status_code == 302:
            location = response.headers.get('Location', '')
            print(f"✅ GitHub OAuth重定向正常")
            print(f"重定向URL: {location[:100]}...")
            if 'github.com' in location:
                print("✅ GitHub OAuth配置正确")
            else:
                print("⚠️  GitHub OAuth重定向URL可能有问题")
        elif response.status_code == 501:
            print("❌ GitHub OAuth未配置")
        else:
            print(f"❌ GitHub OAuth异常: {response.text}")
    except Exception as e:
        print(f"❌ GitHub OAuth测试失败: {e}")
    
    # 测试Google OAuth
    try:
        response = requests.get("http://localhost:8000/api/v1/oauth/google/login", 
                              allow_redirects=False, timeout=5)
        print(f"Google OAuth状态码: {response.status_code}")
        if response.status_code == 302:
            location = response.headers.get('Location', '')
            print(f"✅ Google OAuth重定向正常")
            print(f"重定向URL: {location[:100]}...")
            if 'google.com' in location:
                print("✅ Google OAuth配置正确")
            else:
                print("⚠️  Google OAuth重定向URL可能有问题")
        elif response.status_code == 501:
            print("❌ Google OAuth未配置")
        else:
            print(f"❌ Google OAuth异常: {response.text}")
    except Exception as e:
        print(f"❌ Google OAuth测试失败: {e}")

def test_frontend_oauth_buttons():
    """测试前端OAuth按钮"""
    print("\n=== 前端OAuth按钮测试 ===")
    
    # 测试通过前端代理的OAuth登录
    for provider in ['github', 'google']:
        try:
            url = f"http://localhost:3000/api/v1/oauth/{provider}/login"
            print(f"测试 {provider.upper()} 登录按钮: {url}")
            
            response = requests.get(url, allow_redirects=False, timeout=5)
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 302:
                location = response.headers.get('Location', '')
                print(f"✅ {provider.upper()} 按钮工作正常")
                print(f"重定向到: {location[:100]}...")
            else:
                print(f"❌ {provider.upper()} 按钮异常: {response.text}")
                
        except Exception as e:
            print(f"❌ {provider.upper()} 按钮测试失败: {e}")

def check_ports():
    """检查端口占用"""
    print("\n=== 端口检查 ===")
    import socket
    
    ports = [3000, 8000]
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            if result == 0:
                print(f"✅ 端口 {port} 正在监听")
            else:
                print(f"❌ 端口 {port} 未监听")
        except Exception as e:
            print(f"❌ 检查端口 {port} 失败: {e}")

def main():
    """主诊断函数"""
    print("🔍 开始OAuth功能诊断...")
    print("=" * 50)
    
    # 检查端口
    check_ports()
    
    # 测试后端健康状态
    backend_ok = test_backend_health()
    
    if backend_ok:
        # 测试OAuth端点
        test_oauth_endpoints()
        
        # 测试前端代理
        frontend_ok = test_frontend_proxy()
        
        if frontend_ok:
            # 测试前端OAuth按钮
            test_frontend_oauth_buttons()
    
    print("\n" + "=" * 50)
    print("📋 诊断总结:")
    print("1. 如果后端健康检查失败，请启动后端服务器: python main.py")
    print("2. 如果前端代理测试失败，请检查vite.config.ts中的代理配置")
    print("3. 如果OAuth端点返回501，请检查.env文件中的OAuth配置")
    print("4. 如果前端按钮测试失败，请检查前端开发服务器是否运行")
    print("\n🔧 访问测试页面: http://localhost:3000/oauth-test")

if __name__ == "__main__":
    main() 