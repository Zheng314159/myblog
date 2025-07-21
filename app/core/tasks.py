import asyncio
import logging
from typing import Optional
from fastapi import BackgroundTasks
from app.core.email import email_service
from app.models.user import User
from app.models.article import Article
from app.models.comment import Comment

logger = logging.getLogger(__name__)


class TaskService:
    """异步任务服务"""
    
    @staticmethod
    async def send_welcome_email_task(email: str, username: str):
        """发送欢迎邮件的异步任务"""
        try:
            logger.info(f"开始发送欢迎邮件给 {username} ({email})")
            
            # 模拟异步处理时间
            await asyncio.sleep(1)
            
            # 发送欢迎邮件
            success = email_service.send_welcome_email(email, username)
            
            if success:
                logger.info(f"欢迎邮件发送成功: {email}")
            else:
                logger.error(f"欢迎邮件发送失败: {email}")
                
        except Exception as e:
            logger.error(f"发送欢迎邮件时发生错误: {e}")
    
    @staticmethod
    async def send_password_reset_email_task(email: str, username: str, reset_token: str):
        """发送密码重置邮件的异步任务"""
        try:
            logger.info(f"开始发送密码重置邮件给 {username} ({email})")
            
            # 模拟异步处理时间
            await asyncio.sleep(1)
            
            # 发送密码重置邮件
            success = email_service.send_password_reset_email(email, username, reset_token)
            
            if success:
                logger.info(f"密码重置邮件发送成功: {email}")
            else:
                logger.error(f"密码重置邮件发送失败: {email}")
                
        except Exception as e:
            logger.error(f"发送密码重置邮件时发生错误: {e}")
    
    @staticmethod
    async def send_comment_notification_task(
        author_email: str, 
        author_username: str, 
        article_title: str, 
        comment_content: str
    ):
        """发送评论通知邮件的异步任务"""
        try:
            logger.info(f"开始发送评论通知邮件给 {author_username} ({author_email})")
            
            # 模拟异步处理时间
            await asyncio.sleep(1)
            
            # 发送评论通知邮件
            success = email_service.send_comment_notification_email(
                author_email, author_username, article_title, comment_content
            )
            
            if success:
                logger.info(f"评论通知邮件发送成功: {author_email}")
            else:
                logger.error(f"评论通知邮件发送失败: {author_email}")
                
        except Exception as e:
            logger.error(f"发送评论通知邮件时发生错误: {e}")
    
    @staticmethod
    async def send_verification_code_email_task(email: str, verification_code: str):
        """发送验证码邮件的异步任务"""
        try:
            logger.info(f"开始发送验证码邮件给 {email}")
            
            # 模拟异步处理时间
            await asyncio.sleep(1)
            
            # 发送验证码邮件
            success = email_service.send_verification_code_email(email, verification_code)
            
            if success:
                logger.info(f"验证码邮件发送成功: {email}")
            else:
                logger.error(f"验证码邮件发送失败: {email}")
                
        except Exception as e:
            logger.error(f"发送验证码邮件时发生错误: {e}")
    
    @staticmethod
    async def process_user_registration_task(user: User):
        """处理用户注册的异步任务"""
        try:
            logger.info(f"开始处理用户注册任务: {user.username}")
            
            # 模拟异步处理时间
            await asyncio.sleep(2)
            
            # 发送欢迎邮件
            await TaskService.send_welcome_email_task(user.email, user.username)
            
            # 这里可以添加其他注册后的处理逻辑
            # 比如：创建用户配置文件、发送欢迎消息等
            
            logger.info(f"用户注册任务处理完成: {user.username}")
            
        except Exception as e:
            logger.error(f"处理用户注册任务时发生错误: {e}")
    
    @staticmethod
    async def process_comment_creation_task(comment: Comment, article: Article):
        """处理评论创建的异步任务"""
        try:
            logger.info(f"开始处理评论创建任务: 文章 {article.title}")
            
            # 模拟异步处理时间
            await asyncio.sleep(1)
            
            # 如果评论不是作者自己发的，发送通知邮件给文章作者
            if comment.author_id != article.author_id:
                # 这里需要获取文章作者信息，暂时跳过
                logger.info(f"评论创建任务处理完成: 文章 {article.title}")
            
        except Exception as e:
            logger.error(f"处理评论创建任务时发生错误: {e}")


# 创建全局任务服务实例
task_service = TaskService()


def add_welcome_email_task(background_tasks: BackgroundTasks, email: str, username: str):
    """添加发送欢迎邮件的后台任务"""
    background_tasks.add_task(TaskService.send_welcome_email_task, email, username)


def add_password_reset_email_task(background_tasks: BackgroundTasks, email: str, username: str, reset_token: str):
    """添加发送密码重置邮件的后台任务"""
    background_tasks.add_task(TaskService.send_password_reset_email_task, email, username, reset_token)


def add_verification_code_email_task(background_tasks: BackgroundTasks, email: str, verification_code: str):
    """添加发送验证码邮件的后台任务"""
    background_tasks.add_task(TaskService.send_verification_code_email_task, email, verification_code)


def add_comment_notification_task(
    background_tasks: BackgroundTasks, 
    author_email: str, 
    author_username: str, 
    article_title: str, 
    comment_content: str
):
    """添加发送评论通知邮件的后台任务"""
    background_tasks.add_task(
        TaskService.send_comment_notification_task, 
        author_email, author_username, article_title, comment_content
    )


def add_user_registration_task(background_tasks: BackgroundTasks, user: User):
    """添加用户注册处理的后台任务"""
    background_tasks.add_task(TaskService.process_user_registration_task, user)


def add_comment_creation_task(background_tasks: BackgroundTasks, comment: Comment, article: Article):
    """添加评论创建处理的后台任务"""
    background_tasks.add_task(TaskService.process_comment_creation_task, comment, article) 