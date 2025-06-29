#!/usr/bin/env python3
"""
真实注册流程测试脚本
"""
import requests
import json

# 服务器地址
BASE_URL = "http://localhost:8000"

def test_real_register_flow():
    """测试真实的注册流程"""
    print("=== 真实注册流程测试 ===")
    
    # 测试邮箱
    email = "testregister@example.com"
    username = "testregister"
    
    # 1. 发送验证码
    print("1. 发送验证码...")
    url = f"{BASE_URL}/api/v1/auth/send-verification-code"
    data = {"email": email}
    
    try:
        response = requests.post(url, json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code != 200:
            print("❌ 发送验证码失败")
            return False
            
        print("✅ 验证码发送成功，请检查邮箱")
        
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
        "full_name": "Test Register User",
        "verification_code": verification_code
    }
    
    url = f"{BASE_URL}/api/v1/auth/register"
    
    try:
        response = requests.post(url, json=register_data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code == 200:
            print("✅ 注册成功！")
            return True
        else:
            print("❌ 注册失败")
            return False
            
    except Exception as e:
        print(f"❌ 注册请求失败: {e}")
        return False

def test_register_without_verification():
    """测试不带验证码的注册（应该失败）"""
    print("\n=== 测试不带验证码的注册（应该失败）===")
    
    register_data = {
        "username": "testuser789",
        "email": "test789@example.com",
        "password": "password123",
        "full_name": "Test User 789"
        # 没有验证码
    }
    
    url = f"{BASE_URL}/api/v1/auth/register"
    
    try:
        response = requests.post(url, json=register_data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code == 400:
            print("✅ 正确拒绝没有验证码的注册")
            return True
        else:
            print("❌ 应该拒绝没有验证码的注册")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

if __name__ == "__main__":
    print("开始测试真实注册流程...")
    
    # 测试真实注册流程
    test_real_register_flow()
    
    # 测试不带验证码的注册
    test_register_without_verification()
    
    print("\n测试完成！") 