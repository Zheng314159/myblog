#!/usr/bin/env python3
"""
重新发送重置密码邮件
"""
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

BASE_URL = "http://localhost:8000"

def resend_reset_email(email: str):
    """重新发送重置密码邮件"""
    print(f"=== 重新发送重置密码邮件到 {email} ===")
    
    url = f"{BASE_URL}/api/v1/auth/forgot-password"
    data = {"email": email}
    
    try:
        response = requests.post(url, json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code == 200:
            print("✅ 重置密码邮件已重新发送")
            print("💡 新的邮件链接将指向前端页面: http://localhost:5173/reset-password?token=...")
            return True
        else:
            print("❌ 发送失败")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def main():
    """主函数"""
    print("重新发送重置密码邮件")
    print("=" * 50)
    
    # 检查服务器是否运行
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        if response.status_code != 200:
            print("❌ 后端服务器未正常运行，请先启动服务器")
            return
    except:
        print("❌ 无法连接到后端服务器，请先启动服务器")
        return
    
    print("✅ 后端服务器连接正常")
    
    # 获取邮箱地址
    email = input("请输入您的邮箱地址: ").strip()
    if not email:
        print("❌ 邮箱地址不能为空")
        return
    
    # 重新发送邮件
    resend_reset_email(email)
    
    print("\n=== 完成 ===")
    print("请检查您的邮箱，新的重置链接将指向前端页面")

if __name__ == "__main__":
    main() 