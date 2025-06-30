#!/usr/bin/env python3
import requests
import json
import urllib.parse

def check_google_oauth():
    """检查Google OAuth配置和问题"""
    print("=== Google OAuth 详细检查 ===\n")
    
    try:
        # 1. 检查OAuth配置
        print("1. 检查OAuth配置...")
        response = requests.get('http://localhost:8000/api/v1/config/oauth')
        if response.status_code == 200:
            config = response.json()
            print(f"✅ Google启用: {config.get('google_enabled')}")
            print(f"✅ 前端URL: {config.get('frontend_url')}")
        else:
            print(f"❌ 配置检查失败: {response.status_code}")
            return
        
        # 2. 测试Google OAuth登录
        print("\n2. 测试Google OAuth登录...")
        response = requests.get('http://localhost:8000/api/v1/oauth/google/login', allow_redirects=False)
        
        print(f"Google OAuth状态码: {response.status_code}")
        
        if response.status_code == 302:
            location = response.headers.get('Location', '')
            print("✅ Google OAuth重定向正常")
            print(f"重定向URL: {location}")
            
            # 解析重定向URL
            if '?' in location:
                base_url = location.split('?')[0]
                params = location.split('?')[1]
                print(f"\n重定向基础URL: {base_url}")
                
                # 解析参数
                param_dict = {}
                for param in params.split('&'):
                    if '=' in param:
                        key, value = param.split('=', 1)
                        param_dict[key] = urllib.parse.unquote(value)
                
                print("\n重定向参数:")
                for key, value in param_dict.items():
                    print(f"  {key}: {value}")
                
                # 检查client_id
                client_id = param_dict.get('client_id', '')
                if client_id:
                    if 'your-google-client-id' in client_id:
                        print("\n❌ 还在使用占位符client_id")
                        print("请在.env文件中配置真实的Google OAuth应用信息")
                    else:
                        print(f"\n✅ Client ID已配置: {client_id[:20]}...")
                
                # 检查redirect_uri
                redirect_uri = param_dict.get('redirect_uri', '')
                if redirect_uri:
                    print(f"\n✅ 重定向URI: {redirect_uri}")
                    
                    print("\n=== Google OAuth应用配置指南 ===")
                    print("请在Google Cloud Console中配置以下重定向URI:")
                    print(f"  {redirect_uri}")
                    print("\n配置步骤:")
                    print("1. 登录Google Cloud Console")
                    print("2. 选择你的项目")
                    print("3. 进入 APIs & Services > Credentials")
                    print("4. 编辑你的OAuth 2.0 Client ID")
                    print("5. 在 'Authorized redirect URIs' 中添加:")
                    print(f"   {redirect_uri}")
                    print("6. 保存设置")
                
                print(f"\n🔗 Google授权链接:")
                print(f"{location}")
                
            else:
                print("❌ 重定向URL格式异常")
                
        elif response.status_code == 500:
            print("❌ Google OAuth服务器错误")
            print("可能的原因:")
            print("1. Google OAuth应用未正确配置")
            print("2. 网络连接问题（可能需要代理）")
            print("3. Google OpenID配置URL无法访问")
            
            # 尝试获取错误详情
            try:
                error_response = requests.get('http://localhost:8000/api/v1/oauth/google/login')
                print(f"错误详情: {error_response.text}")
            except:
                pass
                
        else:
            print(f"❌ Google OAuth异常: {response.status_code}")
            print(f"响应: {response.text}")
            
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        print("\n可能的问题:")
        print("1. 服务器未运行")
        print("2. 网络连接问题")
        print("3. Google OAuth配置错误")

if __name__ == "__main__":
    check_google_oauth() 