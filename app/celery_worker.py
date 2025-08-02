from app.core.celery_config import celery_app

# Required so celery discovers tasks
import app.services.email.tasks

if __name__ == "__main__":
    celery_app.start()
