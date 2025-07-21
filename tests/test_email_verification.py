#!/usr/bin/env python3
"""
测试邮箱验证码功能
"""
import requests
import json

# 服务器地址
BASE_URL = "http://localhost:8000"

def test_send_verification_code():
    """测试发送验证码"""
    print("=== 测试发送邮箱验证码 ===")
    
    # 测试数据
    test_email = "test@example.com"
    
    # 发送验证码请求
    url = f"{BASE_URL}/api/v1/auth/send-verification-code"
    data = {"email": test_email}
    
    try:
        response = requests.post(url, json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code == 200:
            print("✅ 验证码发送成功")
        else:
            print("❌ 验证码发送失败")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")

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
            print(f"邮箱功能启用: {config.get('email_enabled', False)}")
            print(f"OAuth功能启用: {config.get('oauth_enabled', False)}")
        else:
            print("❌ 获取配置失败")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")

if __name__ == "__main__":
    print("开始测试邮箱验证码功能...")
    
    # 测试获取配置
    test_auth_config()
    
    # 测试发送验证码
    test_send_verification_code()
    
    print("\n测试完成！") 