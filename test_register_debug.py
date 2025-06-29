#!/usr/bin/env python3
"""
注册功能调试脚本
"""
import requests
import json

# 服务器地址
BASE_URL = "http://localhost:8000"

def test_send_verification_code():
    """测试发送验证码"""
    print("=== 测试发送验证码 ===")
    
    email = "test@example.com"
    url = f"{BASE_URL}/api/v1/auth/send-verification-code"
    data = {"email": email}
    
    try:
        response = requests.post(url, json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code == 200:
            print("✅ 验证码发送成功")
            return True
        else:
            print("❌ 验证码发送失败")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def test_register_with_verification():
    """测试带验证码的注册"""
    print("\n=== 测试带验证码的注册 ===")
    
    # 注册数据
    register_data = {
        "username": "testuser123",
        "email": "test@example.com",
        "password": "password123",
        "full_name": "Test User",
        "verification_code": "123456"  # 模拟验证码
    }
    
    url = f"{BASE_URL}/api/v1/auth/register"
    
    try:
        response = requests.post(url, json=register_data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code == 200:
            print("✅ 注册成功")
            return True
        else:
            print("❌ 注册失败")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def test_register_without_verification():
    """测试不带验证码的注册（应该失败）"""
    print("\n=== 测试不带验证码的注册（应该失败）===")
    
    # 注册数据
    register_data = {
        "username": "testuser456",
        "email": "test456@example.com",
        "password": "password123",
        "full_name": "Test User 456"
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

def test_auth_config():
    """测试获取认证配置"""
    print("\n=== 测试获取认证配置 ===")
    
    url = f"{BASE_URL}/api/v1/auth/config"
    
    try:
        response = requests.get(url)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code == 200:
            config = response.json()
            print(f"邮箱功能启用: {config.get('email_enabled')}")
            return config.get('email_enabled', False)
        else:
            print("❌ 获取配置失败")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

if __name__ == "__main__":
    print("开始测试注册功能...")
    
    # 测试配置
    email_enabled = test_auth_config()
    
    if email_enabled:
        print("\n邮箱验证已启用，测试完整流程...")
        
        # 测试发送验证码
        if test_send_verification_code():
            # 测试带验证码的注册
            test_register_with_verification()
        
        # 测试不带验证码的注册
        test_register_without_verification()
    else:
        print("\n邮箱验证未启用，测试简单注册...")
        test_register_without_verification()
    
    print("\n测试完成！") 