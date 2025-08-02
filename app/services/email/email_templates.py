from app.services.email.tasks import send_email
from app.services.email.service import EmailService
from app.core.config import settings

email_service = EmailService()


def send_welcome_email(to_email: str, username: str) -> bool:
    subject = f"欢迎加入 {settings.app_name}！"
    context={}
    context['username'] = username
    context['app_name'] = settings.app_name

    try:
        email_service.send_async_or_queue(to_email, subject, "welcome.txt", "welcome.html",context)
    except Exception as e:
        return False
    return True
def send_password_reset_email(to_email: str, username: str, reset_token: str) -> bool:
    subject = f"{settings.app_name} 密码重置请求"
    reset_url = f"{settings.frontend_url}/reset-password?token={reset_token}"
    context = {
        'username': username,
        'reset_url': reset_url,
        'app_name': settings.app_name
    }
    try:
        email_service.send_async_or_queue(to_email, subject, "password_reset.txt", "password_reset.html",context)
    except Exception as e:
        return False
    return True

def send_comment_notification_email(to_email: str, username: str, article_title: str, comment_content: str) -> bool:
    subject = f"新评论通知 - {article_title}"
    context = {
        'username': username,
        'article_title': article_title,
        'comment_content': comment_content,
        'app_name': settings.app_name
    }
    try:
        email_service.send_async_or_queue(to_email, subject, "comment_notification.txt", "comment_notification.html",context)
    except Exception as e:
        return False
    return True

def send_verification_code_email(to_email: str, verification_code: str) -> bool:
    subject = f"{settings.app_name}-验证码"
    context = {
        'verification_code': verification_code,
        'app_name': settings.app_name
    }
    try:
        email_service.send_async_or_queue(to_email, subject, "verification_code.txt", "verification_code.html",context)
    except Exception as e:
        return False
    return True

def send_statistics_email(to_email: str, statistics_data: dict) -> bool:
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

        context = {
            'total_users': total_users,
            'active_users': active_users,
            'total_articles': total_articles,
            'published_articles': published_articles,
            'total_comments': total_comments,
            'approved_comments': approved_comments,
            'total_tags': total_tags,
            'today_users': today_users,

            'today_articles': today_articles,
            'today_comments': today_comments,
            'updated_at': updated_at,
            'app_name': settings.app_name
        }
        try:
            email_service.send_async_or_queue(to_email, subject, "statistics_report.txt", "statistics_report.html",context)
        except Exception as e:
            return False
        return True