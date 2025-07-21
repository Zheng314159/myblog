import asyncio
from app.core.scheduler import TaskScheduler
import app.models
from app.models.user import User
from app.models.media import MediaFile
from app.models.article import Article, ArticleStatus
from app.models.comment import Comment
from app.models.tag import Tag
from app.models.system_notification import SystemNotification

async def main():
    scheduler = TaskScheduler()
    await scheduler._send_statistics_email()

if __name__ == "__main__":
    asyncio.run(main())