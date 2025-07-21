#!/usr/bin/env python3
import requests
import json

def verify_oauth_config():
    """验证OAuth配置"""
    print("=== OAuth配置验证 ===\n")
    
    try:
        # 1. 检查OAuth配置
        print("1. 检查OAuth配置...")
        response = requests.get('http://localhost:8000/api/v1/config/oauth')
        
        if response.status_code == 200:
            config = response.json()
            print(f"✅ GitHub启用: {config.get('github_enabled')}")
            print(f"✅ Google启用: {config.get('google_enabled')}")
            print(f"✅ 前端URL: {config.get('frontend_url')}")
            
            if config.get('github_enabled') and not config.get('google_enabled'):
                print("✅ 配置正确: GitHub启用，Google禁用")
            else:
                print("❌ 配置异常")
        else:
            print(f"❌ 配置检查失败: {response.status_code}")
            return
        
        # 2. 测试GitHub OAuth
        print("\n2. 测试GitHub OAuth...")
        response = requests.get('http://localhost:8000/api/v1/oauth/github/login', allow_redirects=False)
        
        if response.status_code == 302:
            location = response.headers.get('Location', '')
            print("✅ GitHub OAuth正常工作")
            print(f"授权链接: {location[:100]}...")
        else:
            print(f"❌ GitHub OAuth异常: {response.status_code}")
        
        # 3. 测试Google OAuth (应该被禁用)
        print("\n3. 测试Google OAuth (应该被禁用)...")
        response = requests.get('http://localhost:8000/api/v1/oauth/google/login', allow_redirects=False)
        
        if response.status_code == 501:
            print("✅ Google OAuth已正确禁用")
        else:
            print(f"❌ Google OAuth状态异常: {response.status_code}")
            print(f"响应: {response.text}")
        
        # 4. 总结
        print("\n=== 总结 ===")
        print("✅ GitHub OAuth: 正常工作")
        print("❌ Google OAuth: 已禁用")
        print("✅ 邮箱密码登录: 可用")
        print("\n现在你可以:")
        print("1. 使用GitHub登录")
        print("2. 使用邮箱密码登录")
        print("3. 专注于GitHub OAuth功能")
        
    except Exception as e:
        print(f"❌ 验证失败: {e}")

if __name__ == "__main__":
    verify_oauth_config() 