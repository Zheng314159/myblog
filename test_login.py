#!/usr/bin/env python3
"""
测试登录功能
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_login(username, password):
    """测试登录"""
    print(f"测试登录: {username}")
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={
                "username": username,
                "password": password
            }
        )
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"登录成功: {data}")
            return data
        else:
            print(f"登录失败: {response.text}")
            return None
    except Exception as e:
        print(f"登录异常: {e}")
        return None

def test_register(username, email, password, full_name=""):
    """测试注册"""
    print(f"测试注册: {username}")
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/register",
            json={
                "username": username,
                "email": email,
                "password": password,
                "full_name": full_name
            }
        )
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"注册成功: {data}")
            return data
        else:
            print(f"注册失败: {response.text}")
            return None
    except Exception as e:
        print(f"注册异常: {e}")
        return None

def main():
    """主函数"""
    print("登录功能测试")
    print("=" * 50)
    
    # 测试注册新用户
    print("\n1. 测试注册新用户")
    register_result = test_register("testuser", "test@example.com", "123456", "测试用户")
    
    if register_result:
        print("\n2. 测试登录新注册的用户")
        login_result = test_login("testuser", "123456")
        
        if login_result:
            print("\n3. 测试错误密码")
            test_login("testuser", "wrongpassword")
    
    print("\n4. 测试不存在的用户")
    test_login("nonexistent", "123456")

if __name__ == "__main__":
    main() 