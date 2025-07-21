#!/usr/bin/env python3
import requests
import time

def test_google_oauth_callback():
    """测试Google OAuth回调处理"""
    print("=== Google OAuth 回调测试 ===\n")
    
    try:
        # 1. 获取Google OAuth登录链接
        print("1. 获取Google OAuth登录链接...")
        response = requests.get('http://localhost:8000/api/v1/oauth/google/login', allow_redirects=False)
        
        if response.status_code != 302:
            print(f"❌ Google OAuth登录失败: {response.status_code}")
            return
            
        location = response.headers.get('Location', '')
        print("✅ Google OAuth登录链接生成成功")
        print(f"授权链接: {location}")
        
        # 2. 模拟回调测试
        print("\n2. 测试回调端点...")
        
        # 测试无效的回调参数
        test_callback_url = "http://localhost:8000/api/v1/oauth/google/callback?error=access_denied&state=test"
        response = requests.get(test_callback_url, allow_redirects=False)
        
        print(f"回调测试状态码: {response.status_code}")
        
        if response.status_code == 302:
            redirect_location = response.headers.get('Location', '')
            print(f"✅ 回调重定向正常")
            print(f"重定向到: {redirect_location}")
            
            if 'error' in redirect_location:
                print("✅ 错误处理正常")
            else:
                print("✅ 回调处理正常")
                
        elif response.status_code == 500:
            print("❌ 回调处理出现服务器错误")
            print("可能的原因:")
            print("1. Google OpenID配置URL无法访问")
            print("2. 网络连接问题")
            print("3. Google OAuth应用配置错误")
            
        else:
            print(f"回调响应: {response.text}")
            
        # 3. 检查网络连接
        print("\n3. 检查Google服务连接...")
        try:
            # 测试Google OpenID配置URL
            openid_url = "https://accounts.google.com/.well-known/openid_configuration"
            response = requests.get(openid_url, timeout=10)
            
            if response.status_code == 200:
                print("✅ Google OpenID配置URL可访问")
                config = response.json()
                print(f"授权端点: {config.get('authorization_endpoint', 'N/A')}")
                print(f"令牌端点: {config.get('token_endpoint', 'N/A')}")
            else:
                print(f"❌ Google OpenID配置URL访问失败: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print("❌ Google OpenID配置URL连接超时")
            print("建议使用代理或VPN")
        except requests.exceptions.ConnectionError:
            print("❌ Google OpenID配置URL连接失败")
            print("建议使用代理或VPN")
        except Exception as e:
            print(f"❌ Google服务连接异常: {e}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_google_oauth_callback() 