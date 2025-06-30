#!/usr/bin/env python3
import requests
import time

def test_google_oauth_fixed():
    """测试修复后的Google OAuth"""
    print("=== Google OAuth 修复测试 ===\n")
    
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
        
        if response.status_code == 302:
            location = response.headers.get('Location', '')
            print("✅ Google OAuth重定向正常")
            
            # 解析重定向URI
            if 'redirect_uri=' in location:
                redirect_uri = location.split('redirect_uri=')[1].split('&')[0]
                import urllib.parse
                redirect_uri = urllib.parse.unquote(redirect_uri)
                print(f"✅ 重定向URI: {redirect_uri}")
                
                print("\n=== Google OAuth应用配置确认 ===")
                print("请确保Google Cloud Console中的重定向URI为:")
                print(f"  {redirect_uri}")
                print("\n如果仍然有问题，请检查:")
                print("1. 回调地址是否完全匹配（包括大小写）")
                print("2. 是否有多余的斜杠或参数")
                print("3. 应用设置是否已保存")
                
                print(f"\n🔗 Google授权链接:")
                print(f"{location}")
                
            else:
                print("❌ 无法解析重定向URI")
        else:
            print(f"❌ Google OAuth异常: {response.status_code}")
            print(f"响应: {response.text}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_google_oauth_fixed() 