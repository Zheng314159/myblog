from datetime import datetime
from enum import Enum
from pydantic import BeforeValidator
from sqlalchemy import Enum as SQLAlchemyEnum
from typing import Annotated, Any
from sqlalchemy import Boolean, String, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base import BaseModelMixin

# 触发器类型枚举
class TaskTrigger(str, Enum):
    interval = "interval"
    cron = "cron"
    date = "date"

class ScheduledTask(BaseModelMixin):
    __tablename__ = "scheduled_task"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)

    # 任务名称
    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
        doc="任务名称（唯一）"
    )

    # 任务函数
    func_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="任务函数名称（请从下拉选择）"
    )

    # 触发器
    trigger: Mapped[Annotated[TaskTrigger, BeforeValidator(TaskTrigger)]] = mapped_column(
        # SQLAlchemyEnum(TaskTrigger, name="task_trigger_enum"),  # 告诉数据库这是个枚举
        String(20),
        nullable=False,
        default=TaskTrigger.interval,
        doc="任务触发类型"
    )

    # 位置参数
    args: Mapped[Any] = mapped_column(
        JSON,
        default=[],
        doc="位置参数（JSON数组），如：[\"param1\", 2]"
    )

    # 关键字参数
    kwargs: Mapped[Any] = mapped_column(
        JSON,
        default={},
        doc="关键字参数（JSON对象），如：{\"key\":\"value\"}"
    )

    # 触发器配置
    trigger_args: Mapped[Any] = mapped_column(
        JSON,
        default={},
        doc=(
            "触发器配置（JSON对象）。\n\n"
            "示例：\n"
            "- interval: {\"seconds\":10}\n"
            "- cron: {\"minute\":\"0\", \"hour\":\"12\"}\n"
            "- date: {\"run_date\":\"2025-08-07 12:00:00\"}"
        )
    )

    # 是否启用
    is_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        doc="是否启用"
    )

    # 上次运行时间（只读）
    last_run_time: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        doc="上次运行时间"
    )

    # 下次运行时间（只读）
    next_run_time: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        doc="下次运行时间"
    )
