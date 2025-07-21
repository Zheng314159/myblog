#!/usr/bin/env python3
import requests
import json

def check_github_redirect_uri():
    """检查GitHub OAuth重定向URI配置"""
    print("=== GitHub OAuth 重定向URI 检查 ===\n")
    
    try:
        # 检查当前OAuth配置
        response = requests.get('http://localhost:8000/api/v1/config/oauth')
        if response.status_code == 200:
            config = response.json()
            print(f"✅ 当前配置:")
            print(f"  前端URL: {config.get('frontend_url')}")
            print(f"  GitHub启用: {config.get('github_enabled')}")
        else:
            print(f"❌ 无法获取OAuth配置: {response.status_code}")
            return
        
        # 测试GitHub OAuth登录，获取重定向URI
        print("\n=== 测试GitHub OAuth登录 ===")
        response = requests.get('http://localhost:8000/api/v1/oauth/github/login', allow_redirects=False)
        
        if response.status_code == 302:
            location = response.headers.get('Location', '')
            print(f"✅ GitHub OAuth重定向正常")
            print(f"重定向URL: {location}")
            
            # 解析重定向URL中的参数
            if '?' in location:
                base_url = location.split('?')[0]
                params = location.split('?')[1]
                print(f"\n重定向基础URL: {base_url}")
                print(f"参数: {params}")
                
                # 检查client_id
                if 'client_id=' in params:
                    client_id = params.split('client_id=')[1].split('&')[0]
                    print(f"Client ID: {client_id}")
                    
                    if client_id == 'your-github-client-id':
                        print("❌ 还在使用占位符client_id")
                        print("请在.env文件中配置真实的GitHub OAuth应用信息")
                    else:
                        print("✅ Client ID已配置")
                
                # 检查redirect_uri
                if 'redirect_uri=' in params:
                    redirect_uri = params.split('redirect_uri=')[1].split('&')[0]
                    redirect_uri = requests.utils.unquote(redirect_uri)
                    print(f"重定向URI: {redirect_uri}")
                    
                    print("\n=== GitHub OAuth应用配置指南 ===")
                    print("请在GitHub OAuth应用设置中配置以下重定向URI:")
                    print(f"  {redirect_uri}")
                    print("\n配置步骤:")
                    print("1. 登录GitHub")
                    print("2. 进入 Settings > Developer settings > OAuth Apps")
                    print("3. 选择或创建你的OAuth应用")
                    print("4. 在 'Authorization callback URL' 字段中输入:")
                    print(f"   {redirect_uri}")
                    print("5. 保存设置")
                    
            else:
                print("❌ 重定向URL格式异常")
        else:
            print(f"❌ GitHub OAuth异常: {response.status_code}")
            print(f"响应: {response.text}")
            
    except Exception as e:
        print(f"❌ 检查失败: {e}")

if __name__ == "__main__":
    check_github_redirect_uri() 