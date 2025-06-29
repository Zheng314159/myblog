#!/usr/bin/env python3
"""
测试完整注册流程
"""
import requests
import json
import time

# 服务器地址
BASE_URL = "http://localhost:8000"

def test_complete_register_flow():
    """测试完整的注册流程"""
    print("=== 完整注册流程测试 ===")
    
    # 生成唯一的测试数据
    timestamp = int(time.time())
    username = f"testuser{timestamp}"
    email = f"test{timestamp}@example.com"
    
    print(f"测试用户名: {username}")
    print(f"测试邮箱: {email}")
    
    # 1. 发送验证码
    print("\n1. 发送验证码...")
    url = f"{BASE_URL}/api/v1/auth/send-verification-code"
    data = {"email": email}
    
    try:
        response = requests.post(url, json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code != 200:
            print("❌ 发送验证码失败")
            return False
            
        print("✅ 验证码发送成功")
        
    except Exception as e:
        print(f"❌ 发送验证码请求失败: {e}")
        return False
    
    # 2. 等待用户输入验证码
    print("\n2. 请输入收到的验证码:")
    verification_code = input("验证码: ").strip()
    
    if not verification_code:
        print("❌ 验证码不能为空")
        return False
    
    # 3. 使用验证码注册
    print("\n3. 使用验证码注册...")
    register_data = {
        "username": username,
        "email": email,
        "password": "password123",
        "full_name": "Test User",
        "verification_code": verification_code
    }
    
    url = f"{BASE_URL}/api/v1/auth/register"
    
    try:
        response = requests.post(url, json=register_data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code == 200:
            print("✅ 注册成功！")
            
            # 4. 测试登录
            print("\n4. 测试登录...")
            login_data = {
                "username": username,
                "password": "password123"
            }
            
            login_url = f"{BASE_URL}/api/v1/auth/login"
            login_response = requests.post(login_url, json=login_data)
            
            print(f"登录状态码: {login_response.status_code}")
            print(f"登录响应: {login_response.text}")
            
            if login_response.status_code == 200:
                print("✅ 登录成功！")
                return True
            else:
                print("❌ 登录失败")
                return False
        else:
            print("❌ 注册失败")
            return False
            
    except Exception as e:
        print(f"❌ 注册请求失败: {e}")
        return False

if __name__ == "__main__":
    print("开始测试完整注册流程...")
    test_complete_register_flow()
    print("\n测试完成！") 