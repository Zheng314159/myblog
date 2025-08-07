from app.core.apscheduler.base import scheduler

async def start_scheduler():
    await scheduler.start()

async def stop_scheduler():
    await scheduler.stop()

def get_scheduler_status():
    return scheduler.get_job_status()
