import json
from app.core.celery_config import celery_app
from app.services.email.service import EmailService
import asyncio

@celery_app.task(bind=True, name="app.services.email.tasks.send_email", max_retries=3, default_retry_delay=10)
def send_email(
    self,
    to_email: str,
    subject: str,
    body_text: str,
    html_template: str|None,
    context_json: str,
    attachments: list[str],
):
    from app.services.email.service import EmailService
    from pathlib import Path
    context = json.loads(context_json)
    paths = [Path(p) for p in attachments]
    try:
        EmailService().send(to_email, subject, body_text, html_template, context, paths)
    except Exception as e:
        raise self.retry(exc=e)

