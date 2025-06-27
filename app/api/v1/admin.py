import fastapi_admin
from fastapi_admin.app import app as admin_app
from fastapi_admin.providers.login import UsernamePasswordProvider
from fastapi_admin.resources import Field, Model
from fastapi_admin.file_upload import FileUpload
from fastapi_admin.template import templates
from fastapi import FastAPI
from starlette.requests import Request
from app.models.user import User
from app.models.article import Article
from app.models.tag import Tag
from app.models.comment import Comment
from app.core.config import settings
import tortoise

async def on_startup():
    await fastapi_admin.app.configure(
        logo_url="/static/logo.png",
        template_folders=["templates"],
        providers=[
            UsernamePasswordProvider(
                admin_model=User,
                login_logo_url="/static/logo.png"
            )
        ],
        file_upload=FileUpload(uploads_dir="uploads"),
        admin_path="/admin",
        database_url=settings.database_url,
        models=[User, Article, Tag, Comment],
    )

# FastAPI-Admin 需要Tortoise ORM初始化
async def init_tortoise():
    await tortoise.Tortoise.init(
        db_url=settings.database_url,
        modules={"models": ["app.models.user", "app.models.article", "app.models.tag", "app.models.comment"]}
    )
    await tortoise.Tortoise.generate_schemas()

# 在主应用main.py中引入并挂载admin_app 