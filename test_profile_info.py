#!/usr/bin/env python3
"""
测试个人信息显示功能
"""

import requests
import json

# 配置
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def test_profile_info():
    """测试个人信息显示功能"""
    print("=== 测试个人信息显示功能 ===")
    
    # 1. 获取配置信息
    print("\n1. 获取邮箱配置...")
    try:
        config_response = requests.get(f"{API_BASE}/auth/config")
        print(f"配置响应状态: {config_response.status_code}")
        
        if config_response.status_code == 200:
            config = config_response.json()
            email_enabled = config.get("email_enabled", False)
            print(f"邮箱验证状态: {email_enabled}")
        else:
            print(f"获取配置失败: {config_response.text}")
            return
            
    except Exception as e:
        print(f"获取配置失败: {e}")
        return
    
    # 2. 测试获取个人信息（无token，应该返回401）
    print("\n2. 测试获取个人信息（无token）...")
    try:
        me_response = requests.get(f"{API_BASE}/auth/me")
        print(f"获取个人信息响应状态: {me_response.status_code}")
        print(f"响应内容: {me_response.text}")
        
    except Exception as e:
        print(f"获取个人信息请求失败: {e}")
    
    # 3. 尝试注册新用户
    print("\n3. 尝试注册新用户...")
    register_data = {
        "username": "testprofile",
        "email": "testprofile@example.com",
        "password": "testpass123",
        "full_name": "测试用户"
    }
    
    try:
        register_response = requests.post(f"{API_BASE}/auth/register", json=register_data)
        print(f"注册响应状态: {register_response.status_code}")
        
        if register_response.status_code == 200:
            register_result = register_response.json()
            access_token = register_result.get("access_token")
            print(f"注册成功，获取到access_token: {access_token[:20]}...")
            
            # 4. 测试获取个人信息（有token）
            print("\n4. 测试获取个人信息（有token）...")
            headers = {"Authorization": f"Bearer {access_token}"}
            
            me_response = requests.get(f"{API_BASE}/auth/me", headers=headers)
            print(f"获取个人信息响应状态: {me_response.status_code}")
            
            if me_response.status_code == 200:
                user_info = me_response.json()
                print("✅ 获取个人信息成功！")
                print(f"用户信息: {json.dumps(user_info, indent=2, ensure_ascii=False)}")
                
                # 验证关键字段
                required_fields = ["id", "username", "email", "role", "is_active"]
                missing_fields = [field for field in required_fields if field not in user_info]
                
                if missing_fields:
                    print(f"❌ 缺少字段: {missing_fields}")
                else:
                    print("✅ 所有必需字段都存在")
                    
            else:
                print(f"❌ 获取个人信息失败: {me_response.text}")
                
        else:
            print(f"注册失败: {register_response.text}")
            
    except Exception as e:
        print(f"注册请求失败: {e}")

if __name__ == "__main__":
    test_profile_info() 