#!/usr/bin/env python3
"""
测试EMAIL_ENABLED=false时的修改密码功能
"""

import requests
import json

# 配置
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def test_change_password_no_email():
    """测试EMAIL_ENABLED=false时的修改密码功能"""
    print("=== 测试EMAIL_ENABLED=false时的修改密码功能 ===")
    
    # 1. 登录获取token
    print("\n1. 登录获取token...")
    login_data = {
        "username": "admin",
        "password": "admin123"
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
    
    # 3. 测试修改密码API（不提供验证码）
    print("\n3. 测试修改密码API（无验证码）...")
    change_password_data = {
        "current_password": "testpass123",
        "new_password": "newpass123"
    }
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        change_response = requests.post(f"{API_BASE}/auth/change-password", json=change_password_data, headers=headers)
        print(f"修改密码响应状态: {change_response.status_code}")
        print(f"响应内容: {change_response.text}")
        
        if change_response.status_code == 200:
            print("✅ 修改密码成功！")
            
            # 4. 测试新密码登录
            print("\n4. 测试新密码登录...")
            new_login_data = {
                "username": "testuser",
                "password": "newpass123"
            }
            
            new_login_response = requests.post(f"{API_BASE}/auth/login", json=new_login_data)
            print(f"新密码登录响应状态: {new_login_response.status_code}")
            
            if new_login_response.status_code == 200:
                print("✅ 新密码登录成功！")
                
                # 5. 改回原密码
                print("\n5. 改回原密码...")
                new_token = new_login_response.json().get("access_token")
                revert_headers = {"Authorization": f"Bearer {new_token}"}
                
                revert_data = {
                    "current_password": "newpass123",
                    "new_password": "testpass123"
                }
                
                revert_response = requests.post(f"{API_BASE}/auth/change-password", json=revert_data, headers=revert_headers)
                print(f"改回原密码响应状态: {revert_response.status_code}")
                
                if revert_response.status_code == 200:
                    print("✅ 密码已改回原密码")
                else:
                    print(f"❌ 改回原密码失败: {revert_response.text}")
            else:
                print(f"❌ 新密码登录失败: {new_login_response.text}")
        else:
            print(f"❌ 修改密码失败: {change_response.text}")
            
    except Exception as e:
        print(f"❌ 修改密码请求失败: {e}")

if __name__ == "__main__":
    test_change_password_no_email() 