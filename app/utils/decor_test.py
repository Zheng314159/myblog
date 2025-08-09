from functools import wraps
import inspect
from typing import Callable, List
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse
from fastapi import Request
from sqladmin import action
from starlette.responses import RedirectResponse
from app.models.scheduled_task import ScheduledTask
from app.core.database import async_session

def action_with_pks(name: str, label: str, confirmation_message: str, pass_object: bool = True):
    def decorator(func: Callable):
        @action(name=name, label=label, confirmation_message=confirmation_message)
        async def wrapper(self, request: Request):
            pks_raw = request.query_params.get("pks")
            results = []
            if not pks_raw:
                results.append("❌ 未收到 pks 参数")
            else:
                pks: List[str] = [pk.strip() for pk in pks_raw.split(",") if pk.strip()]
                if not pks:
                    results.append("❌ 未收到 pks 参数")
                else:
                    async with async_session() as session:
                        for pk in pks:
                            try:
                                task = await session.get(ScheduledTask, pk)
                                if not task:
                                    raise ValueError(f"任务 {pk} 不存在")
                                msg = await func(self, request, task)
                                results.append(f"✅ {task.name}: {msg}")
                            except Exception as e:
                                results.append(f"❌ {pk}: {e}")

            # 存一次性提示
            request.session["flash_messages"] = results

            # 跳回原页面
            referer = request.headers.get("referer")
            if referer:
                return RedirectResponse(referer, status_code=303)
            base_path = "/".join(request.url.path.split("/")[:3])
            return RedirectResponse(f"{base_path}/list", status_code=303)

        wrapper.__signature__ = inspect.Signature(
            parameters=[
                inspect.Parameter("self", inspect.Parameter.POSITIONAL_OR_KEYWORD),
                inspect.Parameter("request", inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=Request),
            ]
        )
        return wrapper
    return decorator
