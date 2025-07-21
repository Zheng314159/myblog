import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from app.core.config import settings, reload_settings

logger = logging.getLogger(__name__)


class EmailService:
    """邮件服务类"""
    
    def __init__(self):
        self._reload_config()
    
    def _reload_config(self):
        """重新加载配置"""
        # 重新加载全局配置
        reload_settings()
        from app.core.config import settings
        
        self.smtp_server = settings.smtp_server
        self.smtp_port = settings.smtp_port
        self.email_user = settings.email_user
        self.email_password = settings.email_password
        self.email_from = settings.email_from or settings.email_user
        self.enabled = settings.email_enabled
        
        logger.info(f"邮件服务配置已重新加载: enabled={self.enabled}")
    
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
        # 每次发送前重新加载配置，确保获取最新的EMAIL_ENABLED状态
        self._reload_config()
        
        if not self.enabled:
            logger.info(f"邮件功能已禁用，跳过发送邮件到 {to_email}")
            return True
        
        if not all([self.smtp_server, self.email_user, self.email_password]):
            logger.warning("邮件配置不完整，跳过发送邮件")
            return False
        
        try:
            # 创建邮件消息
            msg = self._create_message(to_email, subject, body, html_body)
            
            logger.info(f"开始发送邮件到 {to_email}")
            logger.info(f"SMTP服务器: {self.smtp_server}:{self.smtp_port}")
            
            # 连接SMTP服务器，添加超时参数
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
                logger.info("SMTP连接建立成功")
                
                # 启用TLS加密
                logger.info("启用TLS加密...")
                server.starttls()
                logger.info("TLS加密启用成功")
                
                # 登录
                logger.info("开始登录...")
                server.login(self.email_user, self.email_password)
                logger.info("登录成功")
                
                # 发送邮件
                logger.info("开始发送邮件...")
                try:
                    server.send_message(msg)
                    logger.info("邮件发送完成")
                except smtplib.SMTPResponseException as e:
                    # QQ邮箱有时会返回错误码但实际发送成功
                    if e.smtp_code == 250:
                        logger.info("邮件发送成功（QQ邮箱返回250状态码）")
                    else:
                        logger.error(f"SMTP响应错误: {e}")
                        return False
                except Exception as e:
                    # 检查是否是QQ邮箱的特殊情况
                    if "(-1, b'\\x00\\x00\\x00')" in str(e):
                        logger.info("QQ邮箱发送成功（忽略特殊错误码）")
                    else:
                        logger.error(f"发送邮件时发生异常: {e}")
                        return False
                
            logger.info(f"邮件发送成功: {to_email} - {subject}")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP认证失败: {e}")
            return False
        except smtplib.SMTPConnectError as e:
            logger.error(f"SMTP连接失败: {e}")
            return False
        except smtplib.SMTPException as e:
            # 检查是否是QQ邮箱的特殊情况
            if "(-1, b'\\x00\\x00\\x00')" in str(e):
                logger.info("QQ邮箱发送成功（忽略特殊错误码）")
                return True
            else:
                logger.error(f"SMTP错误: {e}")
                return False
        except Exception as e:
            logger.error(f"邮件发送失败: {e}")
            import traceback
            logger.error(f"详细错误信息: {traceback.format_exc()}")
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
        
        # 使用配置中的前端URL
        reset_url = f"{settings.frontend_url}/reset-password?token={reset_token}"
        
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
    
    def send_verification_code_email(self, to_email: str, verification_code: str) -> bool:
        """发送验证码邮件"""
        subject = f"{settings.app_name} - 验证码"
        
        body = f"""
您好，

您的验证码是：{verification_code}

此验证码将在5分钟后失效。

如果您没有请求此验证码，请忽略此邮件。

祝好，
{settings.app_name} 团队
        """.strip()
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>验证码</title>
</head>
<body>
    <div style="max-width: 600px; margin: 0 auto; padding: 20px; font-family: Arial, sans-serif;">
        <h2 style="color: #333;">验证码</h2>
        <p>您好，</p>
        <p>您的验证码是：</p>
        <div style="background-color: #f8f9fa; padding: 20px; text-align: center; margin: 20px 0; border-radius: 5px;">
            <h1 style="color: #007bff; font-size: 32px; margin: 0; letter-spacing: 5px;">{verification_code}</h1>
        </div>
        <p><strong>注意：</strong>此验证码将在5分钟后失效。</p>
        <p>如果您没有请求此验证码，请忽略此邮件。</p>
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

    def send_statistics_email(self, to_email: str, statistics_data: dict) -> bool:
        """发送业务统计数据邮件"""
        subject = f"{settings.app_name} - 业务统计数据报告"
        
        # 格式化统计数据
        total_users = statistics_data.get('total_users', 0)
        active_users = statistics_data.get('active_users', 0)
        total_articles = statistics_data.get('total_articles', 0)
        published_articles = statistics_data.get('published_articles', 0)
        total_comments = statistics_data.get('total_comments', 0)
        approved_comments = statistics_data.get('approved_comments', 0)
        total_tags = statistics_data.get('total_tags', 0)
        today_users = statistics_data.get('today_users', 0)
        today_articles = statistics_data.get('today_articles', 0)
        today_comments = statistics_data.get('today_comments', 0)
        updated_at = statistics_data.get('updated_at', '')
        
        body = f"""
业务统计数据报告

生成时间: {updated_at}

总体统计:
- 用户总数: {total_users}
- 活跃用户: {active_users}
- 文章总数: {total_articles}
- 已发布文章: {published_articles}
- 评论总数: {total_comments}
- 已审核评论: {approved_comments}
- 标签总数: {total_tags}

今日新增:
- 新增用户: {today_users}
- 新增文章: {today_articles}
- 新增评论: {today_comments}

此报告由系统自动生成，如有疑问请联系管理员。

祝好，
{settings.app_name} 团队
        """.strip()
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>业务统计数据报告</title>
    <style>
        .stat-card {{
            background-color: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #007bff;
        }}
        .stat-number {{
            font-size: 24px;
            font-weight: bold;
            color: #007bff;
        }}
        .stat-label {{
            color: #666;
            font-size: 14px;
        }}
        .section-title {{
            color: #333;
            border-bottom: 2px solid #007bff;
            padding-bottom: 5px;
            margin: 20px 0 15px 0;
        }}
    </style>
</head>
<body>
    <div style="max-width: 700px; margin: 0 auto; padding: 20px; font-family: Arial, sans-serif;">
        <h2 style="color: #333; text-align: center;">业务统计数据报告</h2>
        <p style="text-align: center; color: #666; margin-bottom: 30px;">生成时间: {updated_at}</p>
        
        <h3 class="section-title">总体统计</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
            <div class="stat-card">
                <div class="stat-number">{total_users}</div>
                <div class="stat-label">用户总数</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{active_users}</div>
                <div class="stat-label">活跃用户</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{total_articles}</div>
                <div class="stat-label">文章总数</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{published_articles}</div>
                <div class="stat-label">已发布文章</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{total_comments}</div>
                <div class="stat-label">评论总数</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{approved_comments}</div>
                <div class="stat-label">已审核评论</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{total_tags}</div>
                <div class="stat-label">标签总数</div>
            </div>
        </div>
        
        <h3 class="section-title">今日新增</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
            <div class="stat-card">
                <div class="stat-number">{today_users}</div>
                <div class="stat-label">新增用户</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{today_articles}</div>
                <div class="stat-label">新增文章</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{today_comments}</div>
                <div class="stat-label">新增评论</div>
            </div>
        </div>
        
        <hr style="margin: 30px 0;">
        <p style="color: #666; font-size: 14px; text-align: center;">
            此报告由系统自动生成，如有疑问请联系管理员。<br>
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