#!/usr/bin/env python3
"""
简单的邮箱测试脚本
用于测试邮箱配置和发送功能
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_email_config():
    """测试邮箱配置"""
    print("=== 邮箱配置测试 ===")
    
    # 从环境变量获取配置
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    email_user = os.getenv("EMAIL_USER", "")
    email_password = os.getenv("EMAIL_PASSWORD", "")
    email_from = os.getenv("EMAIL_FROM", email_user)
    email_enabled = os.getenv("EMAIL_ENABLED", "false").lower() == "true"
    
    print(f"SMTP服务器: {smtp_server}")
    print(f"SMTP端口: {smtp_port}")
    print(f"邮箱用户: {email_user}")
    print(f"发件人: {email_from}")
    print(f"邮箱功能启用: {email_enabled}")
    
    if not email_enabled:
        print("⚠️  邮箱功能已禁用，请在 .env 文件中设置 EMAIL_ENABLED=true")
        return False
    
    if not email_user or not email_password:
        print("⚠️  邮箱配置不完整，请检查 EMAIL_USER 和 EMAIL_PASSWORD")
        return False
    
    return True

def suggest_email_config():
    """建议邮箱配置"""
    print("\n=== 邮箱配置建议 ===")
    print("由于网络原因，建议使用国内邮箱服务商：")
    print()
    print("1. QQ邮箱配置：")
    print("   SMTP_SERVER=smtp.qq.com")
    print("   SMTP_PORT=587")
    print("   EMAIL_USER=你的QQ邮箱@qq.com")
    print("   EMAIL_PASSWORD=授权码（不是QQ密码）")
    print()
    print("2. 163邮箱配置：")
    print("   SMTP_SERVER=smtp.163.com")
    print("   SMTP_PORT=587")
    print("   EMAIL_USER=你的163邮箱@163.com")
    print("   EMAIL_PASSWORD=授权码（不是163密码）")
    print()
    print("3. 126邮箱配置：")
    print("   SMTP_SERVER=smtp.126.com")
    print("   SMTP_PORT=587")
    print("   EMAIL_USER=你的126邮箱@126.com")
    print("   EMAIL_PASSWORD=授权码（不是126密码）")
    print()
    print("4. 新浪邮箱配置：")
    print("   SMTP_SERVER=smtp.sina.com")
    print("   SMTP_PORT=587")
    print("   EMAIL_USER=你的新浪邮箱@sina.com")
    print("   EMAIL_PASSWORD=授权码（不是新浪密码）")
    print()
    print("获取授权码步骤：")
    print("- QQ邮箱：设置 → 账户 → POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务")
    print("- 163邮箱：设置 → POP3/SMTP/IMAP")
    print("- 126邮箱：设置 → POP3/SMTP/IMAP")
    print("- 新浪邮箱：设置 → POP3/SMTP/IMAP")

def test_smtp_connection(smtp_server, smtp_port, email_user, email_password):
    """测试SMTP连接"""
    print(f"\n=== 测试SMTP连接 ===")
    print(f"正在连接到 {smtp_server}:{smtp_port}...")
    
    try:
        # 创建SMTP连接
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
        server.starttls()  # 启用TLS加密
        
        # 登录
        print("正在登录...")
        server.login(email_user, email_password)
        
        print("✓ SMTP连接和登录成功")
        server.quit()
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("✗ SMTP认证失败，请检查邮箱和密码")
        print("提示：请确保使用的是授权码而不是邮箱密码")
        return False
    except smtplib.SMTPConnectError:
        print("✗ 无法连接到SMTP服务器，请检查服务器地址和端口")
        print("提示：可能是网络问题或服务器地址错误")
        return False
    except smtplib.SMTPException as e:
        print(f"✗ SMTP错误: {e}")
        return False
    except Exception as e:
        print(f"✗ 连接失败: {e}")
        if "10060" in str(e) or "timeout" in str(e).lower():
            print("提示：连接超时，可能是网络问题或服务器不可达")
            print("建议：尝试使用国内邮箱服务商（QQ、163、126等）")
        return False

def send_test_email(smtp_server, smtp_port, email_user, email_password, email_from, to_email):
    """发送测试邮件"""
    print(f"\n=== 发送测试邮件 ===")
    print(f"发送到: {to_email}")
    
    try:
        # 创建邮件消息
        msg = MIMEMultipart('alternative')
        msg['From'] = email_from
        msg['To'] = to_email
        msg['Subject'] = "测试邮件 - FastAPI Blog System"
        
        # 纯文本内容
        text_body = """
这是一封测试邮件，用于验证邮箱功能是否正常工作。

如果您收到这封邮件，说明邮箱配置正确，可以正常发送邮件。

祝好，
FastAPI Blog System 团队
        """.strip()
        
        # HTML内容
        html_body = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>测试邮件</title>
</head>
<body>
    <div style="max-width: 600px; margin: 0 auto; padding: 20px; font-family: Arial, sans-serif;">
        <h2 style="color: #333;">测试邮件</h2>
        <p>这是一封测试邮件，用于验证邮箱功能是否正常工作。</p>
        <p>如果您收到这封邮件，说明邮箱配置正确，可以正常发送邮件。</p>
        <hr style="margin: 30px 0;">
        <p style="color: #666; font-size: 14px;">
            祝好，<br>
            FastAPI Blog System 团队
        </p>
    </div>
</body>
</html>
        """.strip()
        
        # 添加内容
        text_part = MIMEText(text_body, 'plain', 'utf-8')
        html_part = MIMEText(html_body, 'html', 'utf-8')
        msg.attach(text_part)
        msg.attach(html_part)
        
        # 发送邮件
        with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
            server.starttls()
            server.login(email_user, email_password)
            server.send_message(msg)
        
        print("✓ 测试邮件发送成功")
        return True
        
    except Exception as e:
        print(f"✗ 发送测试邮件失败: {e}")
        return False

def main():
    """主函数"""
    print("邮箱功能测试工具")
    print("=" * 50)
    
    # 测试配置
    if not test_email_config():
        print("\n请先配置邮箱设置：")
        print("1. 编辑 .env 文件")
        print("2. 设置正确的邮箱配置")
        print("3. 确保 EMAIL_ENABLED=true")
        suggest_email_config()
        return
    
    # 获取配置
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    email_user = os.getenv("EMAIL_USER", "")
    email_password = os.getenv("EMAIL_PASSWORD", "")
    email_from = os.getenv("EMAIL_FROM", email_user)
    
    # 测试SMTP连接
    if not test_smtp_connection(smtp_server, smtp_port, email_user, email_password):
        print("\n连接失败，请检查配置或尝试其他邮箱服务商")
        suggest_email_config()
        return
    
    # 获取测试邮箱
    test_email = input("\n请输入测试邮箱地址: ").strip()
    if not test_email:
        print("未提供测试邮箱，跳过发送测试")
        return
    
    # 发送测试邮件
    send_test_email(smtp_server, smtp_port, email_user, email_password, email_from, test_email)
    
    print("\n=== 测试完成 ===")
    print("如果测试成功，您可以在注册用户和修改密码功能中使用邮箱功能")

if __name__ == "__main__":
    main() 