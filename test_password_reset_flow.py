#!/usr/bin/env python3
"""
测试完整的密码重置流程
"""
import requests
import time
import json
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

BASE_URL = "http://localhost:8000"

def test_forgot_password(email: str):
    """测试忘记密码功能"""
    print(f"=== 测试忘记密码功能 (邮箱: {email}) ===")
    
    url = f"{BASE_URL}/api/v1/auth/forgot-password"
    data = {"email": email}
    
    try:
        response = requests.post(url, json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code == 200:
            print("✅ 忘记密码请求成功")
            return True
        else:
            print("❌ 忘记密码请求失败")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_reset_password_with_invalid_token():
    """测试使用无效token重置密码"""
    print("\n=== 测试使用无效token重置密码 ===")
    
    url = f"{BASE_URL}/api/v1/auth/reset-password"
    data = {
        "token": "invalid_token_for_testing",
        "new_password": "newpassword123"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code == 401:
            print("✅ 无效token测试通过（返回401是预期的）")
            return True
        else:
            print("⚠️  无效token测试响应异常")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_token_verification():
    """测试token验证逻辑"""
    print("\n=== 测试token验证逻辑 ===")
    
    # 这里我们需要一个有效的token来测试
    # 由于token是从邮件中获取的，我们只能测试无效token的情况
    print("💡 要测试有效token，需要：")
    print("1. 发送忘记密码邮件")
    print("2. 从邮件中获取token")
    print("3. 使用该token测试重置密码")
    
    return True

def test_frontend_integration():
    """测试前端集成"""
    print("\n=== 测试前端集成 ===")
    
    try:
        # 测试忘记密码页面
        forgot_url = "http://localhost:3000/forgot-password"
        response = requests.get(forgot_url)
        print(f"忘记密码页面状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 忘记密码页面可访问")
        else:
            print("❌ 忘记密码页面无法访问")
        
        # 测试重置密码页面
        reset_url = "http://localhost:3000/reset-password?token=test_token"
        response = requests.get(reset_url)
        print(f"重置密码页面状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 重置密码页面可访问")
        else:
            print("❌ 重置密码页面无法访问")
            
    except Exception as e:
        print(f"❌ 前端集成测试异常: {e}")

def main():
    """主函数"""
    print("密码重置流程测试")
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
    
    # 获取测试邮箱
    email = input("请输入测试邮箱地址: ").strip()
    if not email:
        print("❌ 邮箱地址不能为空")
        return
    
    # 测试忘记密码功能
    if test_forgot_password(email):
        print(f"\n📧 密码重置邮件已发送到 {email}")
        print("请检查邮箱，获取重置token")
    
    # 测试无效token
    test_reset_password_with_invalid_token()
    
    # 测试token验证逻辑
    test_token_verification()
    
    # 测试前端集成
    test_frontend_integration()
    
    print("\n=== 测试完成 ===")
    print("💡 使用说明:")
    print("1. 检查邮箱，找到密码重置邮件")
    print("2. 点击邮件中的重置链接")
    print("3. 在重置页面输入新密码")
    print("4. 使用新密码登录验证")
    print("\n🔧 如果仍有问题:")
    print("- 检查token是否过期（24小时有效期）")
    print("- 确认邮箱地址正确")
    print("- 检查Redis服务是否正常运行")

if __name__ == "__main__":
    main() 