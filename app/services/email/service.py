import logging
import asyncio
from typing import Any, Optional, Sequence
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from pathlib import Path
import json
import aiosmtplib

from app.services.email.jinja import render_template, template_dir
from app.core.config import reload_settings, settings

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self._reload_config()

    def _reload_config(self):
        reload_settings()
        from app.core.config import settings  # 热更新
        self.smtp_server = settings.smtp_server
        self.smtp_port = settings.smtp_port
        self.email_user = settings.email_user
        self.email_password = settings.email_password
        self.email_from = settings.email_from or settings.email_user
        self.enabled = settings.email_enabled
        self.smtp_tls = settings.smtp_tls

    def _create_message(
        self,
        to_email: str,
        subject: str,
        body_text: str,
        html_template: Optional[str] = None,
        context: Optional[dict[str, Any]] = None,
        attachments: Optional[Sequence[Path]] = None,
    ) -> MIMEMultipart:
        msg = MIMEMultipart("mixed")
        msg["Subject"] = subject
        msg["To"] = to_email
        msg["From"] = self.email_from

        context = context or {}

        # 文本内容
        if body_text.endswith(".txt"):
            text_template_path = template_dir / body_text
            if not text_template_path.exists():
                raise FileNotFoundError(f"Text template not found: {text_template_path}")
            body_text_rendered = render_template(body_text, context)
        else:
            body_text_rendered = body_text

        text_part = MIMEText(body_text_rendered, "plain", "utf-8")
        msg.attach(text_part)

        # HTML 内容（注意 XSS 转义需在模板中使用 {{ var | e }}）
        if html_template:
            html_body = render_template(html_template, context)
            html_part = MIMEText(html_body, "html", "utf-8")
            msg.attach(html_part)

        # 附件
        if attachments:
            for path in attachments:
                if not path.exists():
                    logger.warning(f"附件文件不存在: {path}")
                    continue
                with path.open("rb") as f:
                    part = MIMEApplication(f.read(), Name=path.name)
                    part.add_header("Content-Disposition", "attachment", filename=path.name)
                    msg.attach(part)

        return msg

    async def send_async(
        self,
        to_email: str,
        subject: str,
        body_text: str,
        html_template: Optional[str] = None,
        context: Optional[dict[str, Any]] = None,
        attachments: Optional[Sequence[Path]] = None,
    ) -> None:
        self._reload_config()

        if not self.enabled:
            logger.info(f"邮件服务关闭，跳过发送：{to_email}")
            return

        if not all([self.smtp_server, self.email_user, self.email_password]):
            logger.warning("邮件配置缺失，发送中止")
            return

        context = context or {}
        msg = self._create_message(to_email, subject, body_text, html_template, context, attachments)

        try:
            logger.info(f"发送邮件到 {to_email} 开始连接 SMTP...")
            await aiosmtplib.send(
                msg,
                hostname=self.smtp_server,
                port=self.smtp_port,
                start_tls=self.smtp_tls,
                username=self.email_user,
                password=self.email_password,
                timeout=10
            )
            logger.info(f"发送成功：{subject} -> {to_email}")
        except Exception as e:
            logger.exception(f"发送邮件失败: {e}")

    def send(
        self,
        to_email: str,
        subject: str,
        body_text: str,
        html_template: Optional[str] = None,
        context: Optional[dict[str, Any]] = None,
        attachments: Optional[Sequence[Path]] = None,
    ) -> None:
        """兼容 Celery 的同步发送方式"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 嵌套运行情况，不建议在 sync 环境中直接用 send
                logger.warning("事件循环已在运行，send 方法应改用 send_async")
                return
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        loop.run_until_complete(
            self.send_async(to_email, subject, body_text, html_template, context, attachments)
        )

    @staticmethod
    def send_async_or_queue(
        to_email: str,
        subject: str,
        body_text: str,
        html_template: Optional[str] = None,
        context: Optional[dict[str, Any]] = None,
        attachments: Optional[Sequence[Path]] = None,  # 注意 Celery 不支持直接传 Path
    ) -> None:
        if settings.use_celery:
            from app.services.email.tasks import send_email
            send_email.delay(
                to_email,
                subject,
                body_text,
                html_template,
                json.dumps(context or {}, ensure_ascii=False),  # 序列化为 JSON
                [str(p) for p in attachments] if attachments else []  # 传字符串路径
            )
        else:
            asyncio.create_task(
                EmailService().send_async(to_email, subject, body_text, html_template, context, attachments)
            )
