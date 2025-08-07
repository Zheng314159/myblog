from datetime import datetime
import logging

logger = logging.getLogger(__name__)


async def push_all_task_status():
    from app.core.apscheduler.base import scheduler
    from app.core.websocket import manager
    """推送所有定时任务状态到首页频道"""
    try:
        jobs = scheduler.get_job_status().get("jobs", [])
        msg = {
            "type": "task_status",
            "data": {
                "jobs": jobs,
                "updated_at": datetime.now().isoformat()
            }
        }
        await manager.broadcast_to_channel(msg, "home")
        logger.info("已推送所有定时任务状态到首页频道")
    except Exception as e:
        logger.error(f"推送定时任务状态失败: {e}")

def register_jobs():
    return {
        "push_all_task_status":push_all_task_status
    }