import requests

BASE_URL = "http://localhost:8000"
email = input("请输入测试邮箱: ").strip()

# 1. 发送验证码
resp = requests.post(f"{BASE_URL}/api/v1/auth/send-verification-code", json={"email": email})
print("验证码发送响应:", resp.status_code, resp.text)
code = input("请输入你收到的验证码: ").strip()

# 2. 注册
data = {
    "username": "testuser2",
    "email": email,
    "password": "123456",
    "full_name": "测试用户2",
    "verification_code": code
}
resp = requests.post(f"{BASE_URL}/api/v1/auth/register", json=data)
print("注册响应:", resp.status_code, resp.text)