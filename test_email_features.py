#!/usr/bin/env python3
"""
测试邮箱相关功能
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_auth_config():
    """测试获取认证配置"""
    print("=== 测试获取认证配置 ===")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/auth/config")
        if response.status_code == 200:
            config = response.json()
            print(f"✓ 获取配置成功: {config}")
            return config
        else:
            print(f"✗ 获取配置失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"✗ 获取配置异常: {e}")
        return None

def test_send_verification_code(email):
    """测试发送验证码"""
    print(f"\n=== 测试发送验证码到 {email} ===")
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/send-verification-code",
            json={"email": email}
        )
        if response.status_code == 200:
            print("✓ 验证码发送成功")
            return True
        else:
            error = response.json()
            print(f"✗ 验证码发送失败: {error}")
            return False
    except Exception as e:
        print(f"✗ 验证码发送异常: {e}")
        return False

def test_forgot_password(email):
    """测试找回密码"""
    print(f"\n=== 测试找回密码 {email} ===")
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/forgot-password",
            json={"email": email}
        )
        if response.status_code == 200:
            result = response.json()
            print(f"✓ 找回密码邮件发送成功: {result}")
            return True
        else:
            error = response.json()
            print(f"✗ 找回密码失败: {error}")
            return False
    except Exception as e:
        print(f"✗ 找回密码异常: {e}")
        return False

def main():
    """主函数"""
    print("邮箱功能测试")
    print("=" * 50)
    
    # 测试获取配置
    config = test_auth_config()
    if not config:
        print("无法获取配置，测试终止")
        return
    
    email_enabled = config.get("email_enabled", False)
    print(f"\n邮箱功能状态: {'启用' if email_enabled else '禁用'}")
    
    if not email_enabled:
        print("邮箱功能已禁用，跳过邮箱相关测试")
        return
    
    # 获取测试邮箱
    test_email = input("\n请输入测试邮箱地址: ").strip()
    if not test_email:
        print("未提供测试邮箱，跳过邮箱测试")
        return
    
    # 测试发送验证码
    test_send_verification_code(test_email)
    
    # 测试找回密码
    test_forgot_password(test_email)
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    main() 