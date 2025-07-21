#!/usr/bin/env python3
import requests
import os
import json

def test_google_with_proxy():
    """测试Google OAuth的代理配置"""
    print("=== Google OAuth 代理配置测试 ===\n")
    
    # 1. 检查当前代理设置
    print("1. 检查当前代理设置...")
    http_proxy = os.environ.get('HTTP_PROXY') or os.environ.get('http_proxy')
    https_proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
    
    print(f"HTTP_PROXY: {http_proxy}")
    print(f"HTTPS_PROXY: {https_proxy}")
    
    if not http_proxy and not https_proxy:
        print("❌ 未配置代理")
        print("建议配置代理以访问Google服务")
    else:
        print("✅ 代理已配置")
    
    # 2. 测试Google服务连接
    print("\n2. 测试Google服务连接...")
    
    proxies = {}
    if http_proxy:
        proxies['http'] = http_proxy
    if https_proxy:
        proxies['https'] = https_proxy
    
    try:
        # 测试Google OpenID配置
        openid_url = "https://accounts.google.com/.well-known/openid_configuration"
        response = requests.get(openid_url, proxies=proxies, timeout=10)
        
        if response.status_code == 200:
            print("✅ Google OpenID配置URL可访问")
            config = response.json()
            print(f"授权端点: {config.get('authorization_endpoint', 'N/A')}")
            print(f"令牌端点: {config.get('token_endpoint', 'N/A')}")
        else:
            print(f"❌ Google OpenID配置URL访问失败: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("❌ Google OpenID配置URL连接超时")
        print("请检查代理配置或网络连接")
    except requests.exceptions.ConnectionError:
        print("❌ Google OpenID配置URL连接失败")
        print("请检查代理配置或网络连接")
    except Exception as e:
        print(f"❌ Google服务连接异常: {e}")
    
    # 3. 测试Google OAuth登录
    print("\n3. 测试Google OAuth登录...")
    try:
        response = requests.get('http://localhost:8000/api/v1/oauth/google/login', allow_redirects=False)
        
        if response.status_code == 302:
            location = response.headers.get('Location', '')
            print("✅ Google OAuth登录链接生成成功")
            print(f"授权链接: {location}")
            
            # 检查是否包含正确的参数
            if 'client_id=' in location and 'redirect_uri=' in location:
                print("✅ OAuth参数配置正确")
            else:
                print("❌ OAuth参数配置异常")
        else:
            print(f"❌ Google OAuth登录失败: {response.status_code}")
            print(f"响应: {response.text}")
            
    except Exception as e:
        print(f"❌ Google OAuth测试失败: {e}")
    
    # 4. 提供解决方案
    print("\n=== 解决方案 ===")
    if not http_proxy and not https_proxy:
        print("1. 配置代理环境变量:")
        print("   set HTTP_PROXY=http://your-proxy:port")
        print("   set HTTPS_PROXY=http://your-proxy:port")
        print("   或者在.env文件中添加:")
        print("   HTTP_PROXY=http://your-proxy:port")
        print("   HTTPS_PROXY=http://your-proxy:port")
        print("\n2. 重启服务器以应用代理设置")
        print("\n3. 或者使用VPN服务")
    else:
        print("代理已配置，请检查代理服务是否正常工作")

if __name__ == "__main__":
    test_google_with_proxy() 