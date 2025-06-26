#!/usr/bin/env python3
"""
测试邮件功能
"""

import asyncio
import os
from dotenv import load_dotenv
from app.core.email import email_service

# 加载环境变量
load_dotenv()


async def test_email_service():
    """测试邮件服务"""
    print("=== 测试邮件服务 ===")
    
    # 检查邮件配置
    print(f"SMTP服务器: {email_service.smtp_server}")
    print(f"SMTP端口: {email_service.smtp_port}")
    print(f"邮件用户: {email_service.email_user}")
    print(f"邮件功能启用: {email_service.enabled}")
    
    if not email_service.enabled:
        print("邮件功能已禁用，跳过发送测试")
        return
    
    if not all([email_service.smtp_server, email_service.email_user, email_service.email_password]):
        print("邮件配置不完整，跳过发送测试")
        return
    
    # 测试邮件地址（请替换为您的测试邮箱）
    test_email = input("请输入测试邮箱地址: ").strip()
    if not test_email:
        print("未提供测试邮箱，跳过发送测试")
        return
    
    print(f"\n开始发送测试邮件到: {test_email}")
    
    # 测试欢迎邮件
    print("\n1. 测试欢迎邮件...")
    success = email_service.send_welcome_email(test_email, "测试用户")
    if success:
        print("✓ 欢迎邮件发送成功")
    else:
        print("✗ 欢迎邮件发送失败")
    
    # 测试密码重置邮件
    print("\n2. 测试密码重置邮件...")
    reset_token = "test-reset-token-12345"
    success = email_service.send_password_reset_email(test_email, "测试用户", reset_token)
    if success:
        print("✓ 密码重置邮件发送成功")
    else:
        print("✗ 密码重置邮件发送失败")
    
    # 测试评论通知邮件
    print("\n3. 测试评论通知邮件...")
    success = email_service.send_comment_notification_email(
        test_email, "测试用户", "测试文章标题", "这是一条测试评论内容"
    )
    if success:
        print("✓ 评论通知邮件发送成功")
    else:
        print("✗ 评论通知邮件发送失败")
    
    print("\n=== 邮件测试完成 ===")


async def test_background_tasks():
    """测试后台任务"""
    print("\n=== 测试后台任务 ===")
    
    from fastapi import BackgroundTasks
    from app.core.tasks import (
        add_welcome_email_task,
        add_password_reset_email_task,
        add_comment_notification_task
    )
    
    # 创建后台任务
    background_tasks = BackgroundTasks()
    
    # 添加邮件任务
    test_email = "test@example.com"
    add_welcome_email_task(background_tasks, test_email, "测试用户")
    add_password_reset_email_task(background_tasks, test_email, "测试用户", "test-token")
    add_comment_notification_task(
        background_tasks, test_email, "测试用户", "测试文章", "测试评论"
    )
    
    print(f"已添加 {len(background_tasks.tasks)} 个后台任务")
    print("后台任务将在API调用时自动执行")
    
    print("=== 后台任务测试完成 ===")


def main():
    """主函数"""
    print("邮件功能测试工具")
    print("=" * 50)
    
    # 运行测试
    asyncio.run(test_email_service())
    asyncio.run(test_background_tasks())


if __name__ == "__main__":
    main() 