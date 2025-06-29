#!/usr/bin/env python3
"""
邮件功能调试脚本
"""
import requests
import json
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 服务器地址
BASE_URL = "http://localhost:8000"

def test_email_config():
    """测试邮箱配置"""
    print("=== 邮箱配置检查 ===")
    
    # 从环境变量获取配置
    smtp_server = os.getenv("SMTP_SERVER", "")
    smtp_port = os.getenv("SMTP_PORT", "")
    email_user = os.getenv("EMAIL_USER", "")
    email_password = os.getenv("EMAIL_PASSWORD", "")
    email_from = os.getenv("EMAIL_FROM", "")
    email_enabled = os.getenv("EMAIL_ENABLED", "")
    
    print(f"SMTP_SERVER: {smtp_server}")
    print(f"SMTP_PORT: {smtp_port}")
    print(f"EMAIL_USER: {email_user}")
    print(f"EMAIL_PASSWORD: {'*' * len(email_password) if email_password else 'None'}")
    print(f"EMAIL_FROM: {email_from}")
    print(f"EMAIL_ENABLED: {email_enabled}")
    
    return {
        "smtp_server": smtp_server,
        "smtp_port": smtp_port,
        "email_user": email_user,
        "email_password": email_password,
        "email_from": email_from,
        "email_enabled": email_enabled
    }

def test_auth_config():
    """测试获取认证配置"""
    print("\n=== 测试获取认证配置 ===")
    
    url = f"{BASE_URL}/api/v1/auth/config"
    
    try:
        response = requests.get(url)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code == 200:
            config = response.json()
            print(f"邮箱功能启用: {config.get('email_enabled', False)}")
            print(f"OAuth功能启用: {config.get('oauth_enabled', False)}")
            return config
        else:
            print("❌ 获取配置失败")
            return None
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None

def test_send_verification_code():
    """测试发送验证码"""
    print("\n=== 测试发送邮箱验证码 ===")
    
    # 测试数据
    test_email = "test@example.com"
    
    # 发送验证码请求
    url = f"{BASE_URL}/api/v1/auth/send-verification-code"
    data = {"email": test_email}
    
    try:
        print(f"请求URL: {url}")
        print(f"请求数据: {data}")
        
        response = requests.post(url, json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print(f"响应: {response.text}")
        
        if response.status_code == 200:
            print("✅ 验证码发送成功")
            return True
        else:
            print("❌ 验证码发送失败")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def test_direct_smtp():
    """直接测试SMTP连接"""
    print("\n=== 直接测试SMTP连接 ===")
    
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    # 获取配置
    config = test_email_config()
    
    if not all([config["smtp_server"], config["email_user"], config["email_password"]]):
        print("❌ 配置不完整")
        return False
    
    try:
        print(f"连接到 {config['smtp_server']}:{config['smtp_port']}...")
        
        # 创建SMTP连接
        server = smtplib.SMTP(config["smtp_server"], int(config["smtp_port"]), timeout=10)
        server.starttls()
        
        print("登录...")
        server.login(config["email_user"], config["email_password"])
        
        print("✅ SMTP连接成功")
        
        # 创建测试邮件
        msg = MIMEMultipart('alternative')
        msg['From'] = config["email_from"] or config["email_user"]
        msg['To'] = "test@example.com"
        msg['Subject'] = "测试邮件"
        
        text_body = "这是一封测试邮件"
        text_part = MIMEText(text_body, 'plain', 'utf-8')
        msg.attach(text_part)
        
        print("发送测试邮件...")
        server.send_message(msg)
        
        print("✅ 测试邮件发送成功")
        server.quit()
        return True
        
    except Exception as e:
        print(f"❌ SMTP测试失败: {e}")
        return False

if __name__ == "__main__":
    print("邮件功能调试工具")
    print("=" * 50)
    
    # 检查配置
    config = test_email_config()
    
    # 测试认证配置
    auth_config = test_auth_config()
    
    # 直接测试SMTP
    smtp_success = test_direct_smtp()
    
    # 测试API
    api_success = test_send_verification_code()
    
    print("\n=== 调试总结 ===")
    print(f"配置完整: {all([config['smtp_server'], config['email_user'], config['email_password']])}")
    print(f"邮箱启用: {config['email_enabled'] == 'true'}")
    print(f"SMTP连接: {'✅' if smtp_success else '❌'}")
    print(f"API发送: {'✅' if api_success else '❌'}")
    
    if smtp_success and not api_success:
        print("\n🔍 问题分析: SMTP连接正常但API失败，可能是应用配置问题")
    elif not smtp_success:
        print("\n🔍 问题分析: SMTP连接失败，请检查邮箱配置")
    else:
        print("\n✅ 所有测试通过") 