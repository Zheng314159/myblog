# 理解 Alembic 的核心概念
名词	说明
Migration（迁移）	数据库结构的版本更新（如添加字段、删除表）
Revision（版本）	每次迁移生成的文件，记录版本变更
Head / Base / Current	数据库迁移版本状态管理标识
Autogenerate（自动生成）	根据模型变更自动生成迁移脚本
# 快速搭建 Alembic 项目(以 FastAPI + SQLModel + Alembic 为例)
1. 安装 Alembic
   pip install alembic
2. 初始化 Alembic
   alembic init alembic
会生成：
  alembic/
    versions/         # 存放迁移脚本
    env.py            # 迁移环境配置（连接数据库）
  alembic.ini         # 主配置文件
# 配置数据库连接（关键）
修改 alembic.ini 或 .env 环境文件中配置连接：
  sqlalchemy.url = postgresql+asyncpg://user:password@localhost:5432/dbname
  异步 SQLModel 用 postgresql+asyncpg，同步用 postgresql。
修改 alembic/env.py（异步版本）
# 自动生成迁移脚本
  alembic revision --autogenerate -m "add new field to user"
查看并手动确认生成的脚本
# 执行数据库迁移
alembic upgrade head   # 升级到最新版本
alembic downgrade -1   # 回退上一个版本
alembic history        # 查看历史版本
alembic current        # 当前数据库版本
# 快速调试技巧
初始化空表结构到数据库	alembic upgrade head
从空数据库重新初始化	清空 DB → alembic upgrade head
清除迁移记录	清空 versions 目录或 alembic_version 表
# 调试建议
每次迁移前运行 alembic revision --autogenerate 后要 人工检查脚本是否正确。
不建议在生产环境运行 --autogenerate，要先在开发环境测试无误后部署。
使用 Alembic 管理初始版本：alembic revision --autogenerate -m "init"。
# 学习路径建议
阶段	学习重点
1	配置数据库 URL，了解 alembic.ini 与 env.py
2	会写 alembic revision 和 upgrade
3	掌握 autogenerate 的陷阱（如默认值/类型变更不自动识别）
4	会合并多个 heads，掌握版本冲突处理
# 常见问题总结
问题	原因
自动生成脚本为空	没有修改模型结构或 metadata 没正确配置
async engine 报错	env.py 未使用 asyncio.run()
新增字段无效	数据库已存在旧表，字段未添加，需手动迁移
回滚失败	脚本未实现 downgrade()
# 常用 Alembic 命令
# 生成迁移脚本
alembic revision --autogenerate -m "initial migration"
# 应用迁移
alembic upgrade head
# 回退迁移
alembic downgrade -1
# 查看版本
alembic current
# 在开发环境运行：
ENVIRONMENT=development alembic upgrade head
# 在生产环境运行：
alembic -x env=production upgrade head
ENVIRONMENT=production alembic upgrade head
docker compose exec backend alembic upgrade head
# Windows 用户（CMD 或 PowerShell）：
  $env:ENVIRONMENT="production"; alembic upgrade head
#  一键初始化脚本
  ENVIRONMENT=production python scripts/init_db.py
  $env:ENVIRONMENT="production"
  python scripts/init_db.py



  ENVIRONMENT=development alembic revision --autogenerate -m "add new field"
  ENVIRONMENT=production alembic revision --autogenerate -m "add new field"

  # 删除数据库中 alembic_version 表中的记录（或整个数据库重建）
alembic stamp head
alembic upgrade head

  File "F:\myblog\myblogenv\lib\site-packages\alembic\util\compat.py", line 71, in read_config_parser
    return file_config.read(file_argument, encoding="locale")修改encoding

