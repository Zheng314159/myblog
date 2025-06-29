#!/usr/bin/env python3
import requests

try:
    response = requests.get("http://localhost:8000/api/v1/auth/config")
    print(f"状态码: {response.status_code}")
    print(f"配置: {response.json()}")
except Exception as e:
    print(f"错误: {e}") 