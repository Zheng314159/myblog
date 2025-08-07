# 在 app/core/apscheduler/jobs/__init__.py
import pkgutil
import importlib

# 统一收集函数
task_func_map = {}

for _, module_name, ispkg in pkgutil.iter_modules(__path__):
    if not ispkg and module_name not in ("__init__"):
        module = importlib.import_module(f"{__name__}.{module_name}")
        if hasattr(module, "register_jobs"):
            funcs = module.register_jobs()
            if funcs:
                task_func_map.update(funcs)
