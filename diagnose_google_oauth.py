#!/usr/bin/env python3
import requests
import json
import os

def diagnose_google_oauth():
    """诊断Google OAuth jwks_uri问题"""
    print("=== Google OAuth jwks_uri 问题诊断 ===\n")
    
    # 1. 检查代理设置
    print("1. 检查代理设置...")
    http_proxy = os.environ.get('HTTP_PROXY') or os.environ.get('http_proxy')
    https_proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
    
    print(f"HTTP_PROXY: {http_proxy}")
    print(f"HTTPS_PROXY: {https_proxy}")
    
    proxies = {}
    if http_proxy:
        proxies['http'] = http_proxy
    if https_proxy:
        proxies['https'] = https_proxy
    
    # 2. 测试Google OpenID配置
    print("\n2. 测试Google OpenID配置...")
    openid_url = "https://accounts.google.com/.well-known/openid_configuration"
    
    try:
        response = requests.get(openid_url, proxies=proxies, timeout=15)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            config = response.json()
            print("✅ Google OpenID配置获取成功")
            
            # 检查关键字段
            required_fields = ['authorization_endpoint', 'token_endpoint', 'jwks_uri', 'userinfo_endpoint']
            for field in required_fields:
                if field in config:
                    print(f"✅ {field}: {config[field]}")
                else:
                    print(f"❌ 缺少 {field}")
                    
            # 特别检查jwks_uri
            jwks_uri = config.get('jwks_uri')
            if jwks_uri:
                print(f"\n✅ jwks_uri: {jwks_uri}")
                
                # 测试jwks_uri是否可访问
                try:
                    jwks_response = requests.get(jwks_uri, proxies=proxies, timeout=10)
                    if jwks_response.status_code == 200:
                        print("✅ jwks_uri 可访问")
                    else:
                        print(f"❌ jwks_uri 访问失败: {jwks_response.status_code}")
                except Exception as e:
                    print(f"❌ jwks_uri 访问异常: {e}")
            else:
                print("❌ 缺少 jwks_uri")
                
        else:
            print(f"❌ Google OpenID配置获取失败: {response.status_code}")
            print(f"响应: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Google OpenID配置连接超时")
        print("建议使用代理或VPN")
    except requests.exceptions.ConnectionError:
        print("❌ Google OpenID配置连接失败")
        print("建议使用代理或VPN")
    except Exception as e:
        print(f"❌ Google OpenID配置异常: {e}")
    
    # 3. 检查本地OAuth配置
    print("\n3. 检查本地OAuth配置...")
    try:
        response = requests.get('http://localhost:8000/api/v1/config/oauth')
        if response.status_code == 200:
            config = response.json()
            print(f"✅ Google启用: {config.get('google_enabled')}")
            print(f"✅ 前端URL: {config.get('frontend_url')}")
        else:
            print(f"❌ 本地OAuth配置获取失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 本地OAuth配置检查失败: {e}")
    
    # 4. 提供解决方案
    print("\n=== 解决方案 ===")
    print("1. 网络连接问题:")
    print("   - 配置代理环境变量:")
    print("     set HTTP_PROXY=http://your-proxy:port")
    print("     set HTTPS_PROXY=http://your-proxy:port")
    print("   - 或在.env文件中添加:")
    print("     HTTP_PROXY=http://your-proxy:port")
    print("     HTTPS_PROXY=http://your-proxy:port")
    print("\n2. 重启服务器以应用代理设置")
    print("\n3. 使用VPN服务")
    print("\n4. 检查防火墙设置")

if __name__ == "__main__":
    diagnose_google_oauth() 