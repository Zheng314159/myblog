#!/usr/bin/env python3
import requests
import os
import json

def fix_google_oauth_network():
    """修复Google OAuth网络问题"""
    print("=== Google OAuth 网络问题修复 ===\n")
    
    # 1. 检查当前代理配置
    print("1. 当前代理配置...")
    http_proxy = os.environ.get('HTTP_PROXY') or os.environ.get('http_proxy')
    https_proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
    
    print(f"HTTP_PROXY: {http_proxy}")
    print(f"HTTPS_PROXY: {https_proxy}")
    
    # 2. 测试代理连接
    print("\n2. 测试代理连接...")
    proxies = {}
    if http_proxy:
        proxies['http'] = http_proxy
    if https_proxy:
        proxies['https'] = https_proxy
    
    # 测试基本网络连接
    test_urls = [
        "https://www.google.com",
        "https://accounts.google.com",
        "https://accounts.google.com/.well-known/openid_configuration"
    ]
    
    for url in test_urls:
        try:
            print(f"\n测试: {url}")
            response = requests.get(url, proxies=proxies, timeout=10)
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ 连接成功")
                if "openid_configuration" in url:
                    config = response.json()
                    if 'jwks_uri' in config:
                        print("✅ jwks_uri 存在")
                    else:
                        print("❌ jwks_uri 缺失")
            else:
                print(f"❌ 连接失败: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print("❌ 连接超时")
        except requests.exceptions.ConnectionError:
            print("❌ 连接错误")
        except Exception as e:
            print(f"❌ 异常: {e}")
    
    # 3. 提供解决方案
    print("\n=== 解决方案 ===")
    
    if not http_proxy and not https_proxy:
        print("1. 配置代理:")
        print("   在.env文件中添加:")
        print("   HTTP_PROXY=http://127.0.0.1:1080")
        print("   HTTPS_PROXY=http://127.0.0.1:1080")
        print("   或使用你的代理地址")
    else:
        print("1. 代理已配置，但可能有问题:")
        print("   - 检查代理服务是否正常运行")
        print("   - 尝试不同的代理端口")
        print("   - 确认代理支持HTTPS")
    
    print("\n2. 替代方案:")
    print("   - 使用VPN服务")
    print("   - 使用其他代理服务")
    print("   - 临时禁用Google OAuth，只使用GitHub OAuth")
    
    print("\n3. 临时解决方案:")
    print("   如果无法解决网络问题，可以:")
    print("   - 只启用GitHub OAuth")
    print("   - 使用邮箱密码登录")
    print("   - 等待网络环境改善")
    
    # 4. 检查是否可以禁用Google OAuth
    print("\n4. 检查OAuth配置...")
    try:
        response = requests.get('http://localhost:8000/api/v1/config/oauth')
        if response.status_code == 200:
            config = response.json()
            print(f"GitHub启用: {config.get('github_enabled')}")
            print(f"Google启用: {config.get('google_enabled')}")
            
            if config.get('github_enabled'):
                print("✅ GitHub OAuth可用，可以作为主要登录方式")
            else:
                print("❌ GitHub OAuth未启用")
                
    except Exception as e:
        print(f"❌ 配置检查失败: {e}")

if __name__ == "__main__":
    fix_google_oauth_network() 