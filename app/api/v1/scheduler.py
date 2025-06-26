from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.core.scheduler import get_scheduler_status, start_scheduler, stop_scheduler
from app.models.user import UserRole

router = APIRouter(prefix="/scheduler", tags=["scheduler"])


@router.get("/status")
async def get_scheduler_status_endpoint(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取定时任务状态（需要管理员权限）"""
    if current_user.get("role") != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    
    return get_scheduler_status()


@router.post("/start")
async def start_scheduler_endpoint(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """启动定时任务调度器（需要管理员权限）"""
    if current_user.get("role") != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    
    try:
        await start_scheduler()
        return {"message": "定时任务调度器启动成功"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"启动定时任务调度器失败: {str(e)}"
        )


@router.post("/stop")
async def stop_scheduler_endpoint(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """停止定时任务调度器（需要管理员权限）"""
    if current_user.get("role") != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    
    try:
        await stop_scheduler()
        return {"message": "定时任务调度器停止成功"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"停止定时任务调度器失败: {str(e)}"
        )


@router.get("/jobs")
async def get_scheduler_jobs(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取所有定时任务列表（需要管理员权限）"""
    if current_user.get("role") != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    
    status_info = get_scheduler_status()
    return {
        "status": status_info["status"],
        "jobs": status_info["jobs"]
    } 