#!/usr/bin/env python3
import requests

def check_oauth_config():
    try:
        # 检查OAuth配置
        response = requests.get('http://localhost:8000/api/v1/config/oauth')
        print(f"OAuth配置状态码: {response.status_code}")
        
        if response.status_code == 200:
            config = response.json()
            print("✅ OAuth配置:")
            print(f"  GitHub启用: {config.get('github_enabled')}")
            print(f"  Google启用: {config.get('google_enabled')}")
            print(f"  前端URL: {config.get('frontend_url')}")
        else:
            print(f"❌ 获取OAuth配置失败: {response.text}")
            
        # 检查GitHub OAuth登录端点
        print("\n=== 测试GitHub OAuth登录 ===")
        response = requests.get('http://localhost:8000/api/v1/oauth/github/login', allow_redirects=False)
        print(f"GitHub OAuth状态码: {response.status_code}")
        
        if response.status_code == 302:
            location = response.headers.get('Location', '')
            print(f"✅ GitHub OAuth重定向正常")
            print(f"重定向URL: {location[:100]}...")
            
            if 'your-github-client-id' in location:
                print("❌ 还在使用占位符client_id，需要配置真实的GitHub OAuth应用")
            elif 'github.com' in location:
                print("✅ GitHub OAuth配置正确")
        else:
            print(f"❌ GitHub OAuth异常: {response.text}")
            
    except Exception as e:
        print(f"❌ 检查失败: {e}")

if __name__ == "__main__":
    check_oauth_config() 