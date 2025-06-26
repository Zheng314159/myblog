import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """邮件服务类"""
    
    def __init__(self):
        self.smtp_server = settings.smtp_server
        self.smtp_port = settings.smtp_port
        self.email_user = settings.email_user
        self.email_password = settings.email_password
        self.email_from = settings.email_from or settings.email_user
        self.enabled = settings.email_enabled
    
    def _create_message(self, to_email: str, subject: str, body: str, html_body: Optional[str] = None) -> MIMEMultipart:
        """创建邮件消息"""
        msg = MIMEMultipart('alternative')
        msg['From'] = self.email_from
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # 添加纯文本内容
        text_part = MIMEText(body, 'plain', 'utf-8')
        msg.attach(text_part)
        
        # 如果有HTML内容，也添加
        if html_body:
            html_part = MIMEText(html_body, 'html', 'utf-8')
            msg.attach(html_part)
        
        return msg
    
    def send_email(self, to_email: str, subject: str, body: str, html_body: Optional[str] = None) -> bool:
        """发送邮件"""
        if not self.enabled:
            logger.info(f"邮件功能已禁用，跳过发送邮件到 {to_email}")
            return True
        
        if not all([self.smtp_server, self.email_user, self.email_password]):
            logger.warning("邮件配置不完整，跳过发送邮件")
            return False
        
        try:
            # 创建邮件消息
            msg = self._create_message(to_email, subject, body, html_body)
            
            # 连接SMTP服务器
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # 启用TLS加密
                server.login(self.email_user, self.email_password)
                
                # 发送邮件
                server.send_message(msg)
                
            logger.info(f"邮件发送成功: {to_email} - {subject}")
            return True
            
        except Exception as e:
            logger.error(f"邮件发送失败: {e}")
            return False
    
    def send_welcome_email(self, to_email: str, username: str) -> bool:
        """发送欢迎邮件"""
        subject = f"欢迎加入 {settings.app_name}！"
        
        body = f"""
亲爱的 {username}，

欢迎加入 {settings.app_name}！

感谢您的注册，您的账户已经成功创建。

如果您有任何问题，请随时联系我们。

祝好，
{settings.app_name} 团队
        """.strip()
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>欢迎加入 {settings.app_name}</title>
</head>
<body>
    <div style="max-width: 600px; margin: 0 auto; padding: 20px; font-family: Arial, sans-serif;">
        <h2 style="color: #333;">欢迎加入 {settings.app_name}！</h2>
        <p>亲爱的 <strong>{username}</strong>，</p>
        <p>感谢您的注册，您的账户已经成功创建。</p>
        <p>如果您有任何问题，请随时联系我们。</p>
        <hr style="margin: 30px 0;">
        <p style="color: #666; font-size: 14px;">
            祝好，<br>
            {settings.app_name} 团队
        </p>
    </div>
</body>
</html>
        """.strip()
        
        return self.send_email(to_email, subject, body, html_body)
    
    def send_password_reset_email(self, to_email: str, username: str, reset_token: str) -> bool:
        """发送密码重置邮件"""
        subject = f"{settings.app_name} - 密码重置"
        
        reset_url = f"http://127.0.0.1:8000/reset-password?token={reset_token}"
        
        body = f"""
亲爱的 {username}，

您请求重置密码。请点击以下链接重置您的密码：

{reset_url}

如果您没有请求重置密码，请忽略此邮件。

此链接将在24小时后失效。

祝好，
{settings.app_name} 团队
        """.strip()
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>密码重置</title>
</head>
<body>
    <div style="max-width: 600px; margin: 0 auto; padding: 20px; font-family: Arial, sans-serif;">
        <h2 style="color: #333;">密码重置</h2>
        <p>亲爱的 <strong>{username}</strong>，</p>
        <p>您请求重置密码。请点击以下按钮重置您的密码：</p>
        <p style="text-align: center; margin: 30px 0;">
            <a href="{reset_url}" style="background-color: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">
                重置密码
            </a>
        </p>
        <p>如果您没有请求重置密码，请忽略此邮件。</p>
        <p><strong>注意：</strong>此链接将在24小时后失效。</p>
        <hr style="margin: 30px 0;">
        <p style="color: #666; font-size: 14px;">
            祝好，<br>
            {settings.app_name} 团队
        </p>
    </div>
</body>
</html>
        """.strip()
        
        return self.send_email(to_email, subject, body, html_body)
    
    def send_comment_notification_email(self, to_email: str, username: str, article_title: str, comment_content: str) -> bool:
        """发送评论通知邮件"""
        subject = f"{settings.app_name} - 新评论通知"
        
        body = f"""
亲爱的 {username}，

您的文章 "{article_title}" 收到了新评论：

"{comment_content}"

请登录查看完整评论。

祝好，
{settings.app_name} 团队
        """.strip()
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>新评论通知</title>
</head>
<body>
    <div style="max-width: 600px; margin: 0 auto; padding: 20px; font-family: Arial, sans-serif;">
        <h2 style="color: #333;">新评论通知</h2>
        <p>亲爱的 <strong>{username}</strong>，</p>
        <p>您的文章 <strong>"{article_title}"</strong> 收到了新评论：</p>
        <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #007bff; margin: 20px 0;">
            <p style="margin: 0; font-style: italic;">"{comment_content}"</p>
        </div>
        <p>请登录查看完整评论。</p>
        <hr style="margin: 30px 0;">
        <p style="color: #666; font-size: 14px;">
            祝好，<br>
            {settings.app_name} 团队
        </p>
    </div>
</body>
</html>
        """.strip()
        
        return self.send_email(to_email, subject, body, html_body)


# 创建全局邮件服务实例
email_service = EmailService() 