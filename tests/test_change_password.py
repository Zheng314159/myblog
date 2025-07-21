#!/usr/bin/env python3
"""
测试修改密码功能
"""

import requests
import json
import time

# 配置
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def test_change_password_flow():
    """测试修改密码流程"""
    print("=== 测试修改密码功能 ===")
    
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
    
    # 3. 如果邮箱验证开启，发送验证码
    verification_code = ""
    if email_enabled:
        print("\n3. 发送验证码...")
        headers = {"Authorization": f"Bearer {access_token}"}
        
        try:
            code_response = requests.post(f"{API_BASE}/auth/send-change-password-code", headers=headers)
            print(f"发送验证码响应状态: {code_response.status_code}")
            
            if code_response.status_code == 200:
                print("验证码发送成功")
                verification_code = input("请输入收到的验证码: ").strip()
            else:
                print(f"发送验证码失败: {code_response.text}")
                return
                
        except Exception as e:
            print(f"发送验证码请求失败: {e}")
            return
    
    # 4. 修改密码
    print("\n4. 修改密码...")
    change_password_data = {
        "current_password": "testpass123",
        "new_password": "newpass123"
    }
    
    if email_enabled and verification_code:
        change_password_data["verification_code"] = verification_code
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        change_response = requests.post(f"{API_BASE}/auth/change-password", json=change_password_data, headers=headers)
        print(f"修改密码响应状态: {change_response.status_code}")
        
        if change_response.status_code == 200:
            print("密码修改成功！")
            
            # 5. 测试新密码登录
            print("\n5. 测试新密码登录...")
            new_login_data = {
                "username": "testuser",
                "password": "newpass123"
            }
            
            new_login_response = requests.post(f"{API_BASE}/auth/login", json=new_login_data)
            print(f"新密码登录响应状态: {new_login_response.status_code}")
            
            if new_login_response.status_code == 200:
                print("新密码登录成功！")
                
                # 6. 改回原密码
                print("\n6. 改回原密码...")
                if email_enabled:
                    # 重新发送验证码
                    code_response = requests.post(f"{API_BASE}/auth/send-change-password-code", headers=headers)
                    if code_response.status_code == 200:
                        verification_code = input("请输入新的验证码: ").strip()
                    else:
                        print("无法发送验证码，跳过改回原密码")
                        return
                
                revert_data = {
                    "current_password": "newpass123",
                    "new_password": "testpass123"
                }
                
                if email_enabled and verification_code:
                    revert_data["verification_code"] = verification_code
                
                revert_response = requests.post(f"{API_BASE}/auth/change-password", json=revert_data, headers=headers)
                print(f"改回原密码响应状态: {revert_response.status_code}")
                
                if revert_response.status_code == 200:
                    print("密码已改回原密码")
                else:
                    print(f"改回原密码失败: {revert_response.text}")
            else:
                print(f"新密码登录失败: {new_login_response.text}")
        else:
            print(f"修改密码失败: {change_response.text}")
            
    except Exception as e:
        print(f"修改密码请求失败: {e}")

if __name__ == "__main__":
    test_change_password_flow() 