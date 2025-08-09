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
        # 这里不能用 wraps，否则会覆盖掉签名
        @action(name=name, label=label, confirmation_message=confirmation_message)
        async def wrapper(self, request: Request):
            pks_raw = request.query_params.get("pks")
            results = []
            if not pks_raw:
                results.append({"error": "未收到pks参数"})
            else:
                pks: List[str] = [pk.strip() for pk in pks_raw.split(",") if pk.strip()]
            if not pks:
                results.append({"error": "未收到pks参数"})
            else:
                async with async_session() as session:
                    for pk in pks:
                        try:
                            task = await session.get(ScheduledTask, pk)
                            if not task:
                                raise ValueError(f"任务 {pk} 不存在")
                            msg = await func(self, request, task)
                            label_name = task.name
                            results.append(f"✅ {label_name}: {msg}")
                        except Exception as e:
                            results.append(f"❌ {pk}: {e}")

            request.session["messages"] = results

            referer = request.headers.get("referer")
            msg_param = {"msg": results}

            def clean_url_and_add_msg(url: str, msg_param: dict):
                parsed = urlparse(url)
                query_dict = parse_qs(parsed.query)
                query_dict.pop("msg", None)  # 移除旧的 msg
                query_dict.update(msg_param)  # 加上新的 msg
                new_query = urlencode(query_dict, doseq=True)
                return urlunparse(parsed._replace(query=new_query))

            if referer:
                return RedirectResponse(clean_url_and_add_msg(referer, msg_param), status_code=303)

            # 兜底
            base_path = "/".join(request.url.path.split("/")[:3])
            list_url = f"{base_path}/list"
            return RedirectResponse(clean_url_and_add_msg(list_url, msg_param), status_code=303)

        # 关键：显式声明签名，确保 FastAPI / SQLAdmin 知道有 pks
        wrapper.__signature__ = inspect.Signature(
            parameters=[
                inspect.Parameter("self", inspect.Parameter.POSITIONAL_OR_KEYWORD),
                inspect.Parameter("request", inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=Request),
            ]
        )

        return wrapper
    return decorator

