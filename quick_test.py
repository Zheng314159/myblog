#!/usr/bin/env python3
import requests

# 测试忘记密码功能
email = "goldzheng8@gmail.com"
url = "http://localhost:8000/api/v1/auth/forgot-password"
data = {"email": email}

try:
    response = requests.post(url, json=data)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.text}")
    
    if response.status_code == 200:
        print("✅ 忘记密码请求成功")
        print(f"📧 密码重置邮件已发送到 {email}")
        print("请检查邮箱，获取重置token")
    else:
        print("❌ 忘记密码请求失败")
        
except Exception as e:
    print(f"❌ 请求异常: {e}") 