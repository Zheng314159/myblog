#!/usr/bin/env python3
"""
测试缓存头
"""

import requests

def test_cache_headers():
    """测试缓存头"""
    print("🔍 测试缓存头...")
    
    try:
        # 测试登录页面
        response = requests.get('http://localhost:8000/jianai/login', timeout=10)
        
        print(f"登录页面状态码: {response.status_code}")
        print(f"Cache-Control: {response.headers.get('Cache-Control', 'Not set')}")
        print(f"Pragma: {response.headers.get('Pragma', 'Not set')}")
        print(f"Expires: {response.headers.get('Expires', 'Not set')}")
        
        if 'no-cache' not in response.headers.get('Cache-Control', ''):
            print("✅ 登录页面可以被缓存")
        else:
            print("❌ 登录页面仍然不缓存")
        
        # 测试管理后台主页
        print("\n测试管理后台主页...")
        response = requests.get('http://localhost:8000/jianai/', timeout=10)
        
        print(f"管理后台状态码: {response.status_code}")
        print(f"Cache-Control: {response.headers.get('Cache-Control', 'Not set')}")
        print(f"Pragma: {response.headers.get('Pragma', 'Not set')}")
        print(f"Expires: {response.headers.get('Expires', 'Not set')}")
        
        if 'no-cache' in response.headers.get('Cache-Control', ''):
            print("✅ 管理后台主页不缓存（正确）")
        else:
            print("❌ 管理后台主页可以被缓存（可能有问题）")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_cache_headers() 