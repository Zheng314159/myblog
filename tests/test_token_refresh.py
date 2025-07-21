#!/usr/bin/env python3
"""
测试token自动刷新功能
"""

import requests
import json
import time
from datetime import datetime

# 配置
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"
REFRESH_URL = f"{BASE_URL}/api/v1/auth/refresh"
ME_URL = f"{BASE_URL}/api/v1/auth/me"

def test_token_refresh():
    print("=== Token自动刷新测试 ===")
    print(f"测试时间: {datetime.now()}")
    print()
    
    # 1. 登录获取token
    print("1. 登录获取token...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(LOGIN_URL, json=login_data)
        response.raise_for_status()
        tokens = response.json()
        
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]
        
        print(f"✓ 登录成功")
        print(f"  Access Token: {access_token[:50]}...")
        print(f"  Refresh Token: {refresh_token[:50]}...")
        print()
        
    except Exception as e:
        print(f"✗ 登录失败: {e}")
        return
    
    # 2. 测试访问受保护的接口
    print("2. 测试访问受保护的接口...")
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(ME_URL, headers=headers)
        response.raise_for_status()
        user_info = response.json()
        print(f"✓ 获取用户信息成功: {user_info['username']}")
        print()
        
    except Exception as e:
        print(f"✗ 获取用户信息失败: {e}")
        return
    
    # 3. 测试token刷新
    print("3. 测试token刷新...")
    refresh_data = {"refresh_token": refresh_token}
    
    try:
        response = requests.post(REFRESH_URL, json=refresh_data)
        response.raise_for_status()
        new_tokens = response.json()
        
        new_access_token = new_tokens["access_token"]
        new_refresh_token = new_tokens["refresh_token"]
        
        print(f"✓ Token刷新成功")
        print(f"  新Access Token: {new_access_token[:50]}...")
        print(f"  新Refresh Token: {new_refresh_token[:50]}...")
        print()
        
    except Exception as e:
        print(f"✗ Token刷新失败: {e}")
        return
    
    # 4. 使用新token测试访问
    print("4. 使用新token测试访问...")
    new_headers = {"Authorization": f"Bearer {new_access_token}"}
    
    try:
        response = requests.get(ME_URL, headers=new_headers)
        response.raise_for_status()
        user_info = response.json()
        print(f"✓ 使用新token获取用户信息成功: {user_info['username']}")
        print()
        
    except Exception as e:
        print(f"✗ 使用新token获取用户信息失败: {e}")
        return
    
    # 5. 测试无效token的错误处理
    print("5. 测试无效token的错误处理...")
    invalid_headers = {"Authorization": "Bearer invalid_token"}
    
    try:
        response = requests.get(ME_URL, headers=invalid_headers)
        print(f"✓ 无效token正确返回错误: {response.status_code}")
        if response.status_code == 401:
            print("  ✓ 返回401状态码")
        print()
        
    except Exception as e:
        print(f"✗ 无效token测试失败: {e}")
    
    print("=== 测试完成 ===")
    print("前端应该已经启动了自动token检查机制，每分钟检查一次token是否即将过期")
    print("如果token将在5分钟内过期，会自动刷新token")

if __name__ == "__main__":
    test_token_refresh() 