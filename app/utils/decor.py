from fastapi import Request
from sqladmin import action
from functools import wraps
from typing import Callable
from starlette.responses import RedirectResponse
from app.models.scheduled_task import ScheduledTask
from app.core.database import async_session


def action_with_pks(name: str, label: str, confirmation_message: str, pass_object: bool = True):
    print("✅hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh Using custom action_with_pks!")  # 加这行
    def decorator(func: Callable):
        @action(name=name, label=label, confirmation_message=confirmation_message)
        @wraps(func)
        async def wrapper(self, request: Request, pks: list[str]):
            print(f"qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq装饰器捕获pks: {pks}")
            results = []
            async with async_session() as session:
                for pk in pks:
                    try:
                        if pass_object:
                            task = await session.get(ScheduledTask, pk)
                            if not task:
                                raise ValueError(f"任务 {pk} 不存在")
                            msg = await func(self, request, task)
                            label = task.name
                        else:
                            msg = await func(self, request, pk)
                            label = str(pk)
                        results.append(f"✅ {label}: {msg}")
                    except Exception as e:
                        results.append(f"❌ {label}: {e}")

            request.session["messages"] = results
            return RedirectResponse(request.url_for(f"{self.identity}-list"), status_code=303)

        return wrapper
    return decorator
