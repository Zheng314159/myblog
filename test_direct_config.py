#!/usr/bin/env python3
"""
直接测试配置接口
"""

import requests
import json

def test_config_direct():
    """直接测试配置接口"""
    try:
        print("直接测试 /api/v1/auth/config 接口...")
        
        # 方法1：直接GET请求
        response = requests.get("http://localhost:8000/api/v1/auth/config", timeout=10)
        print(f"方法1 - 状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"方法1 - 响应: {response.json()}")
        else:
            print(f"方法1 - 错误: {response.text}")
            
    except Exception as e:
        print(f"方法1 - 异常: {e}")
    
    try:
        # 方法2：使用curl命令
        import subprocess
        result = subprocess.run(['curl', '-X', 'GET', 'http://localhost:8000/api/v1/auth/config'], 
                              capture_output=True, text=True, timeout=10)
        print(f"方法2 - 状态码: {result.returncode}")
        print(f"方法2 - 输出: {result.stdout}")
        if result.stderr:
            print(f"方法2 - 错误: {result.stderr}")
            
    except Exception as e:
        print(f"方法2 - 异常: {e}")

if __name__ == "__main__":
    test_config_direct() 