#!/usr/bin/env python3
"""
快速测试修改密码API
"""

import requests
import json

# 配置
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def test_change_password_api():
    """测试修改密码API"""
    print("=== 快速测试修改密码API ===")
    
    # 1. 登录获取token
    print("\n1. 登录获取token...")
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    
    try:
        login_response = requests.post(f"{API_BASE}/auth/login", json=login_data)
        print(f"登录响应状态: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"登录失败: {login_response.text}")
            return
        
        login_result = login_response.json()
        access_token = login_result.get("access_token")
        print(f"获取到access_token: {access_token[:20]}...")
        
    except Exception as e:
        print(f"登录请求失败: {e}")
        return
    
    # 2. 获取配置信息
    print("\n2. 获取邮箱配置...")
    try:
        config_response = requests.get(f"{API_BASE}/auth/config")
        print(f"配置响应状态: {config_response.status_code}")
        
        if config_response.status_code == 200:
            config = config_response.json()
            email_enabled = config.get("email_enabled", False)
            print(f"邮箱验证状态: {email_enabled}")
        else:
            print(f"获取配置失败: {config_response.text}")
            email_enabled = False
            
    except Exception as e:
        print(f"获取配置失败: {e}")
        email_enabled = False
    
    # 3. 测试发送验证码API（如果邮箱验证开启）
    if email_enabled:
        print("\n3. 测试发送验证码API...")
        headers = {"Authorization": f"Bearer {access_token}"}
        
        try:
            code_response = requests.post(f"{API_BASE}/auth/send-change-password-code", headers=headers)
            print(f"发送验证码响应状态: {code_response.status_code}")
            print(f"响应内容: {code_response.text}")
            
        except Exception as e:
            print(f"发送验证码请求失败: {e}")
    
    # 4. 测试修改密码API（不提供验证码，应该失败）
    print("\n4. 测试修改密码API（无验证码）...")
    change_password_data = {
        "current_password": "testpass123",
        "new_password": "newpass123"
    }
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        change_response = requests.post(f"{API_BASE}/auth/change-password", json=change_password_data, headers=headers)
        print(f"修改密码响应状态: {change_response.status_code}")
        print(f"响应内容: {change_response.text}")
        
    except Exception as e:
        print(f"修改密码请求失败: {e}")

if __name__ == "__main__":
    test_change_password_api() 