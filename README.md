# FastAPI Blog System

一个完整的 FastAPI 博客系统，包含用户认证、文章管理、评论系统、标签管理等功能。

## 功能特性

- 🔐 **用户认证系统**
  - JWT 认证 (Access Token + Refresh Token)
  - 用户注册/登录
  - 角色权限控制 (Admin/Moderator/User)
  - Token 黑名单管理

- 📝 **文章管理**
  - 文章发布、编辑、删除
  - 文章状态管理 (草稿/已发布/已归档)
  - 文章标签系统

- 💬 **评论系统**
  - 多级评论支持
  - 评论审核功能

- 🏷️ **标签管理**
  - 标签创建和管理
  - 文章标签关联

- 🛠️ **技术特性**
  - 异步数据库操作 (SQLModel + AsyncSession)
  - Redis 缓存和会话管理 (redis[async])
  - 全局异常处理
  - CORS 支持
  - 请求日志记录
  - 数据库迁移 (Alembic)

## 项目结构

```
my_cursor/
├── app/
│   ├── api/
│   │   ├── deps.py              # API 依赖项
│   │   └── v1/
│   │       └── auth.py          # 认证 API
│   │   └── v1/
│   │       └── article.py       # 文章 API
│   │   └── v1/
│   │       └── comment.py       # 评论 API
│   │   └── v1/
│   │       └── tag.py           # 标签 API
│   ├── core/
│   │   ├── config.py            # 配置管理
│   │   ├── database.py          # 数据库连接
│   │   ├── exceptions.py        # 自定义异常
│   │   ├── middleware.py        # 中间件
│   │   ├── redis.py             # Redis 管理 (redis[async])
│   │   └── security.py          # 安全相关
│   ├── models/
│   │   ├── user.py              # 用户模型
│   │   ├── article.py           # 文章模型
│   │   ├── comment.py           # 评论模型
│   │   └── tag.py               # 标签模型
│   └── schemas/
│       └── auth.py              # 认证 Schema
├── alembic/                     # 数据库迁移
├── main.py                      # 主启动文件
├── start.py                     # 启动脚本
├── run_server.py                # 简单启动脚本
├── test_system.py               # 系统测试脚本
├── test_redis.py                # Redis 连接测试脚本
├── test_models.py               # 模型测试脚本
├── test_health.py               # 健康检查测试脚本
├── requirements.txt             # 依赖包
├── alembic.ini                  # Alembic 配置
└── README.md                    # 项目说明
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 环境配置

复制 `env.example` 为 `.env` 并修改配置：

```bash
cp env.example .env
```

编辑 `.env` 文件：

```env
# 数据库
DATABASE_URL=sqlite+aiosqlite:///./blog.db

# JWT 设置
SECRET_KEY=your-secret-key-here-make-it-long-and-secure
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Redis 设置
REDIS_URL=redis://localhost:6379/0

# CORS 设置
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8080"]

# 应用设置
APP_NAME=FastAPI Blog System
DEBUG=true
```

### 3. 启动 Redis

确保 Redis 服务正在运行：

```bash
# Windows
redis-server

# Linux/Mac
sudo service redis start

# Docker
docker run -d -p 6379:6379 redis:alpine
```

### 4. 测试系统

```bash
# 测试模型和数据库
python test_models.py

# 测试 Redis 连接
python test_redis.py

# 测试健康检查
python test_health.py
```

### 5. 运行应用

```bash
# 使用启动脚本（推荐）
python start.py

# 或使用简单启动脚本
python run_server.py

# 或直接运行
python main.py

# 或使用 uvicorn
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### 6. 测试系统功能

```bash
python test_system.py
```

### 7. 访问 API 文档

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- 健康检查: http://127.0.0.1:8000/health

## API 端点

### 认证相关

- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/refresh` - 刷新 Token
- `POST /api/v1/auth/logout` - 用户登出

### 其他端点

- `GET /` - 根路径
- `GET /health` - 健康检查

## 数据库迁移

### 初始化 Alembic

```bash
alembic init alembic
```

### 创建迁移

```bash
alembic revision --autogenerate -m "Initial migration"
```

### 执行迁移

```bash
alembic upgrade head
```

## 开发说明

### Redis 配置

本项目使用 `redis[async]` 包进行异步 Redis 操作，替代了已弃用的 `aioredis` 包。

主要变更：
- 使用 `redis.asyncio` 模块
- 支持同步和异步操作
- 更好的类型提示支持

### 模型关系

项目使用 SQLModel 定义数据模型，支持以下关系类型：

- **一对多关系**：用户与文章、文章与评论
- **多对多关系**：文章与标签
- **自引用关系**：评论的父子关系

所有模型都使用 `TYPE_CHECKING` 来避免循环导入问题。

### 添加新的 API 路由

1. 在 `app/api/v1/` 下创建新的路由文件
2. 在 `main.py` 中注册路由

### 添加新的模型

1. 在 `app/models/` 下创建模型文件
2. 更新 `app/models/__init__.py`
3. 创建数据库迁移

### 权限控制

使用依赖项进行权限控制：

```python
from app.api.deps import require_admin, require_moderator

@router.get("/admin-only")
async def admin_endpoint(
    current_user: Annotated[dict, Depends(require_admin)]
):
    return {"message": "Admin only"}
```

## 技术栈

- **FastAPI** - Web 框架
- **SQLModel** - ORM 和 Pydantic 集成
- **SQLAlchemy** - 数据库 ORM
- **Alembic** - 数据库迁移
- **Redis** - 缓存和会话存储 (redis[async])
- **python-jose** - JWT 处理
- **passlib** - 密码哈希
- **pydantic-settings** - 配置管理

## 故障排除

### 模型导入错误

如果遇到 `Relationship() got an unexpected keyword argument 'remote_side'` 错误：

1. 确保使用正确的 SQLModel 语法
2. 对于自引用关系，使用 `sa_relationship_kwargs` 参数
3. 使用 `TYPE_CHECKING` 避免循环导入

### 认证中间件错误

如果遇到 `AuthenticationError: Missing or invalid authorization header` 错误：

1. 确保公开路径（如 `/`, `/health`, `/docs`）已添加到中间件的白名单
2. 检查中间件配置是否正确
3. 重启服务器

### 健康检查失败

如果健康检查返回 500 错误：

1. 确保 `/health` 端点已添加到中间件的公开路径列表
2. 检查 Redis 连接是否正常
3. 运行 `python test_health.py` 进行诊断

### Redis 连接问题

如果遇到 Redis 连接问题，请检查：

1. Redis 服务是否正在运行
2. Redis 端口 (6379) 是否可访问
3. 运行 `python test_redis.py` 进行连接测试

### 依赖安装问题

如果遇到依赖安装问题：

```bash
# 升级 pip
python -m pip install --upgrade pip

# 重新安装依赖
pip install -r requirements.txt --force-reinstall
```

### 数据库问题

如果遇到数据库问题：

```bash
# 测试模型和数据库连接
python test_models.py

# 删除数据库文件重新创建
rm blog.db
python test_models.py
```

### 测试脚本问题

如果测试脚本失败：

1. 确保服务器在 `http://127.0.0.1:8000` 运行
2. 检查网络连接和防火墙设置
3. 使用 `python test_health.py` 验证基本连接

## 许可证

MIT License 