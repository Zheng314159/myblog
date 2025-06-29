#!/usr/bin/env python3
import requests

def test_profile():
    try:
        # 测试配置接口
        print("测试配置接口...")
        response = requests.get("http://localhost:8000/api/v1/auth/config")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            config = response.json()
            print(f"配置: {config}")
        
        # 测试获取个人信息（无token）
        print("\n测试获取个人信息（无token）...")
        response = requests.get("http://localhost:8000/api/v1/auth/me")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    test_profile() 