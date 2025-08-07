import asyncio
from typing import Any, Dict
import logging
import uuid
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from sqlalchemy import select
from app.models.scheduled_task import ScheduledTask
from app.core.database import async_session
from sqlalchemy.exc import IntegrityError
from app.core.config import settings
from app.core.apscheduler.jobs import task_func_map

logger = logging.getLogger(__name__)

class TaskScheduler:
    # 你之前已有的代码...

    def __init__(self):
        self.scheduler = AsyncIOScheduler(
            timezone=settings.timezone,
            job_defaults={
                'coalesce': True,  # 合并重复任务
                'max_instances': 1,  # 最大实例数
                'misfire_grace_time': 60  # 错过执行时间的宽限时间
            }
        )
        self._running = False
        self._lock = asyncio.Lock()
        self.task_func_map = task_func_map
    
    async def start(self):
        """启动调度器"""
        try:
            async with self._lock:
                if self._running:
                    logger.warning("调度器已运行")
                    return
                await self._ensure_registered_tasks()
                await self._add_jobs()
                self.scheduler.start()
                self._running = True
                logger.info("调度器已启动")
            
        except Exception as e:
            logger.error(f"启动定时任务调度器失败: {e}")
            raise e
        
    async def _add_jobs(self):
        async with async_session() as session:
            result = await session.execute(
                select(ScheduledTask).where(ScheduledTask.is_enabled == True)
            )
            tasks = result.scalars().all()
            for task in tasks:
                if task.func_name not in self.task_func_map:
                    logger.warning(f"任务 [{task.name}] 的 func_name [{task.func_name}] 未注册，跳过")
                    continue
                await self.add_job_from_db(task)

    # 在 scheduler.start() 中补一段
    async def _ensure_registered_tasks(self):
        async with async_session() as session:
            for func_name in task_func_map.keys():
                stmt = select(ScheduledTask).where(ScheduledTask.func_name == func_name)
                result = await session.execute(stmt)
                exists = result.scalar()
                if not exists:
                    new_task = ScheduledTask(
                        id=str(uuid.uuid4()),
                        name=f"{func_name}-示例",
                        func_name=func_name,
                        trigger="interval",
                        trigger_args={"seconds": 60},
                        is_enabled=False  # 默认禁用，手动启用
                    )
                    session.add(new_task)
                    try:
                        await session.commit()
                        logger.info(f"自动注册任务：{func_name}")
                    except IntegrityError:
                        await session.rollback()
                        logger.warning(f"任务 {func_name} 已存在，跳过注册")
    
    async def stop(self):
        """停止调度器"""
        if not self._running:
            return
        
        try:
            self.scheduler.shutdown(wait=True)
            self._running = False
            logger.info("定时任务调度器已停止")
        except Exception as e:
            logger.error(f"停止定时任务调度器失败: {e}")

    def get_job_status(self) -> Dict[str, Any]:
        """获取任务状态"""
        if not self._running:
            return {"status": "stopped", "jobs": []}
        
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            })
        
        return {
            "status": "running",
            "jobs": jobs
        }
    
    def get_job_info(self, job_id: str) -> dict:
        job = self.scheduler.get_job(job_id)
        if not job:
            return {}
        return {
            "id": job.id,
            "name": job.name,
            "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
            "trigger": str(job.trigger),
            "args": job.args,
            "kwargs": job.kwargs,
        }


    async def add_job_from_db(self, task: ScheduledTask):
        """根据数据库的ScheduledTask实例，添加或更新调度任务"""
        try:
            # 先移除同名任务，防止重复
            self.scheduler.remove_job(task.id)
        except Exception:
            pass
        
        # 根据 trigger 类型构造对应触发器
        trigger = None
        if task.trigger == "interval":
            trigger = IntervalTrigger(**task.trigger_args)
        elif task.trigger == "cron":
            trigger = CronTrigger(**task.trigger_args)
        elif task.trigger == "date":
            trigger = DateTrigger(**task.trigger_args)
        else:
            raise ValueError(f"未知触发器类型: {task.trigger}")
        
        # 任务函数映射，根据 func_name 找对应函数
        if task.func_name not in self.task_func_map:
            raise ValueError(f"找不到任务函数: {task.func_name}")
        func = self.task_func_map[task.func_name]

        self.scheduler.add_job(
            func=func,
            trigger=trigger,
            args=task.args or [],
            kwargs=task.kwargs or {},
            id=task.id,
            name=task.name,
            replace_existing=True,
            coalesce=True,
            max_instances=1,
            misfire_grace_time=60,
        )
        if not task.is_enabled:
            self.scheduler.pause_job(task.id)

    async def remove_job(self, job_id: str):
        try:
            self.scheduler.remove_job(job_id)
        except Exception:
            pass
    async def pause_job(self, job_id: str):
        self.scheduler.pause_job(job_id)

    async def resume_job(self, job_id: str):
        self.scheduler.resume_job(job_id)



# 全局调度器实例
scheduler = TaskScheduler()


