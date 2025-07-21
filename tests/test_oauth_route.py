#!/usr/bin/env python3
import requests

def test_oauth_routes():
    """测试OAuth路由"""
    base_url = "http://localhost:8000"
    
    # 测试GitHub OAuth登录
    print("=== 测试GitHub OAuth登录 ===")
    try:
        response = requests.get(f"{base_url}/api/v1/oauth/github/login", allow_redirects=False)
        print(f"状态码: {response.status_code}")
        if response.status_code == 302:
            print(f"重定向URL: {response.headers.get('Location', 'N/A')}")
        elif response.status_code == 501:
            print("GitHub OAuth未配置")
        else:
            print(f"响应内容: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 测试OAuth提供商列表
    print("\n=== 测试OAuth提供商列表 ===")
    try:
        response = requests.get(f"{base_url}/api/v1/oauth/providers")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("可用的OAuth提供商:")
            for provider in data.get('providers', []):
                print(f"  - {provider['display_name']}: {provider['login_url']}")
        else:
            print(f"响应内容: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")

if __name__ == "__main__":
    test_oauth_routes() 