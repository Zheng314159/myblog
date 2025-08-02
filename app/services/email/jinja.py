from typing import Any
from jinja2 import Environment, FileSystemLoader, select_autoescape
# import os
# template_path = os.path.join(os.path.dirname(__file__), "templates","zh")

from pathlib import Path
template_dir = Path(__file__).parent / "templates" / "zh"

jinja_env = Environment(
    loader=FileSystemLoader(template_dir),
    autoescape=select_autoescape(
        enabled_extensions=("html", "xml"),
        default_for_string=False,
        default=False
    )
)


def render_template(name: str, context:dict[str,Any]|None=None) -> str:
    return jinja_env.get_template(name).render(**(context or {}))
