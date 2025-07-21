#!/usr/bin/env python3
"""
简单测试配置接口
"""

import requests
import json

def test_config():
    """测试配置接口"""
    try:
        print("测试 /api/v1/auth/config 接口...")
        response = requests.get("http://localhost:8000/api/v1/auth/config")
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应数据: {data}")
        else:
            print(f"错误响应: {response.text}")
            
    except Exception as e:
        print(f"请求异常: {e}")

if __name__ == "__main__":
    test_config() 