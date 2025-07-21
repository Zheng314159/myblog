# FastAPI Blog System

一个完整的 FastAPI 博客系统，包含用户认证、文章管理、评论系统、标签管理等功能。

## 功能特性

- 🔐 **用户认证系统**
  - JWT 认证 (Access Token + Refresh Token)
  - 用户注册/登录
  - 角色权限控制 (Admin/Moderator/User)
  - Token 黑名单管理
  - 密码重置功能

- 📧 **异步邮件通知**
  - 用户注册欢迎邮件
  - 密码重置邮件
  - 评论通知邮件
  - BackgroundTasks 异步处理

- 📝 **富文本文章管理**
  - Markdown 富文本编辑
  - LaTeX 数学公式支持
  - 文章状态管理 (草稿/已发布/已归档)
  - 文章标签系统
  - 文章搜索和过滤
  - 文件上传和图片存储

- 🧮 **LaTeX 数学公式支持**
  - 行内数学公式 ($...$ 或 \(...\))
  - 块级数学公式 ($$...$$ 或 \[...\])
  - LaTeX 环境支持 (equation, align, matrix 等)
  - 实时 LaTeX 预览
  - LaTeX 语法验证
  - 自动渲染为高质量图片
  - 支持化学公式 (mhchem)
  - 支持图表绘制 (TikZ, pgfplots)

- 💬 **评论系统**
  - 多级评论支持（回复功能）
  - 评论审核功能
  - 实时评论通知

- 🏷️ **标签管理**
  - 标签创建和管理
  - 文章标签关联
  - 热门标签统计

- 🔌 **WebSocket 实时通知**
  - 实时评论通知
  - 文章更新广播
  - 系统消息推送
  - 频道订阅管理

- 🛠️ **技术特性**
  - 异步数据库操作 (SQLModel + AsyncSession)
  - Redis 缓存和会话管理 (redis[async])
  - 全局异常处理
  - CORS 支持
  - 请求日志记录
  - 数据库迁移 (Alembic)
  - SMTP 邮件发送
  - 文件上传处理

## 项目结构

```
my_cursor/
├── app/
│   ├── api/
│   │   ├── deps.py              # API 依赖项
│   │   └── v1/
│   │       ├── auth.py          # 认证 API
│   │       ├── article.py       # 文章 API (包含LaTeX支持)
│   │       ├── tag.py           # 标签 API
│   │       └── websocket.py     # WebSocket API
│   ├── core/
│   │   ├── config.py            # 配置管理
│   │   ├── database.py          # 数据库连接
│   │   ├── email.py             # 邮件服务
│   │   ├── tasks.py             # 异步任务服务
│   │   ├── websocket.py         # WebSocket 管理器
│   │   ├── exceptions.py        # 自定义异常
│   │   ├── middleware.py        # 中间件
│   │   ├── redis.py             # Redis 管理 (redis[async])
│   │   ├── security.py          # 安全相关
│   │   └── latex.py             # LaTeX 渲染服务
│   ├── models/
│   │   ├── user.py              # 用户模型
│   │   ├── article.py           # 文章模型 (包含LaTeX字段)
│   │   ├── comment.py           # 评论模型
│   │   └── tag.py               # 标签模型
│   └── schemas/
│       ├── auth.py              # 认证 Schema
│       ├── article.py           # 文章 Schema (包含LaTeX字段)
│       └── tag.py               # 标签 Schema
├── frontend/
│   └── src/
│       └── api/
│           └── index.js         # React API 接口
├── uploads/                     # 文件上传目录
│   ├── images/                  # 图片文件
│   ├── articles/                # 文章文件
│   └── latex/                   # LaTeX 渲染图片
├── alembic/                     # 数据库迁移
├── main.py                      # 主启动文件
├── start.py                     # 启动脚本
├── run_server.py                # 简单启动脚本
├── test_system.py               # 系统测试脚本
├── test_extended_features.py    # 扩展功能测试脚本
├── test_redis.py                # Redis 连接测试脚本
├── test_models.py               # 模型测试脚本
├── test_health.py               # 健康检查测试脚本
├── test_email.py                # 邮件功能测试脚本
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

# 邮件设置
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_FROM=your-email@gmail.com
EMAIL_ENABLED=false

# CORS 设置
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8080"]

# 应用设置
APP_NAME=FastAPI Blog System
DEBUG=true
```

### 3. 邮件配置

#### Gmail 配置示例

1. 启用两步验证
2. 生成应用专用密码
3. 在 `.env` 中配置：

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=your-gmail@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_FROM=your-gmail@gmail.com
EMAIL_ENABLED=true
```

#### 其他邮件服务商

- **QQ邮箱**: `smtp.qq.com:587`
- **163邮箱**: `smtp.163.com:587`
- **Outlook**: `smtp-mail.outlook.com:587`

### 4. 启动 Redis

确保 Redis 服务正在运行：

```bash
# Windows
redis-server

# Linux/Mac
sudo service redis start

# Docker
docker run -d -p 6379:6379 redis:alpine
```

### 5. 测试系统

```bash
# 测试模型和数据库
python test_models.py

# 测试 Redis 连接
python test_redis.py

# 测试健康检查
python test_health.py

# 测试邮件功能
python test_email.py

# 测试扩展功能
python test_extended_features.py
```

### 6. 运行应用

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

### 7. 测试系统功能

```bash
python test_system.py
```

### 8. 访问 API 文档

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- 健康检查: http://127.0.0.1:8000/health

## API 端点

### 认证相关

- `POST /api/v1/auth/register` - 用户注册（自动发送欢迎邮件）
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/refresh` - 刷新 Token
- `POST /api/v1/auth/logout` - 用户登出
- `POST /api/v1/auth/forgot-password` - 发送密码重置邮件
- `POST /api/v1/auth/reset-password` - 重置密码

### 文章管理

- `GET /api/v1/articles` - 获取文章列表
- `POST /api/v1/articles` - 创建文章
- `GET /api/v1/articles/{id}` - 获取文章详情
- `PUT /api/v1/articles/{id}` - 更新文章
- `DELETE /api/v1/articles/{id}` - 删除文章
- `POST /api/v1/articles/upload-image` - 上传图片
- `GET /api/v1/articles/images/{filename}` - 获取图片

### 评论系统

- `GET /api/v1/articles/{id}/comments` - 获取文章评论
- `POST /api/v1/articles/{id}/comments` - 创建评论
- `DELETE /api/v1/articles/comments/{id}` - 删除评论

### 标签管理

- `GET /api/v1/tags` - 获取标签列表
- `POST /api/v1/tags` - 创建标签（管理员）
- `GET /api/v1/tags/{id}` - 获取标签详情
- `PUT /api/v1/tags/{id}` - 更新标签（管理员）
- `DELETE /api/v1/tags/{id}` - 删除标签（管理员）
- `GET /api/v1/tags/popular` - 获取热门标签

### WebSocket

- `WS /api/v1/ws` - WebSocket 连接
- `GET /api/v1/ws/status` - 获取连接状态
- `POST /api/v1/ws/broadcast` - 广播消息（管理员）

### 其他端点

- `GET /` - 根路径
- `GET /health` - 健康检查

## 富文本编辑功能

### Markdown 支持

系统支持完整的 Markdown 语法：

```markdown
# 标题
## 二级标题

**粗体文本**
*斜体文本*

- 列表项 1
- 列表项 2

[链接文本](URL)

![图片描述](图片URL)

```python
# 代码块
def hello():
    print("Hello, World!")
```

> 引用文本
```

### 文件上传

支持图片文件上传：

- 支持格式：JPG, PNG, GIF, WebP
- 最大文件大小：5MB
- 自动生成唯一文件名
- 返回可访问的URL

### 文章状态

- **DRAFT** - 草稿状态
- **PUBLISHED** - 已发布
- **ARCHIVED** - 已归档

## 评论系统

### 功能特性

- ✅ **多级评论**：支持回复评论，形成评论树
- ✅ **实时通知**：新评论实时推送给文章作者
- ✅ **权限控制**：用户只能删除自己的评论
- ✅ **内容过滤**：防止恶意内容

### 评论结构

```json
{
  "id": 1,
  "content": "评论内容",
  "author": {
    "id": 1,
    "username": "user1",
    "full_name": "User One"
  },
  "article_id": 1,
  "parent_id": null,
  "replies": [
    {
      "id": 2,
      "content": "回复内容",
      "parent_id": 1
    }
  ],
  "created_at": "2024-01-01T00:00:00Z"
}
```

## WebSocket 实时通知

### 连接方式

```javascript
// 建立连接
const ws = new WebSocket('ws://127.0.0.1:8000/api/v1/ws');

// 发送认证消息
ws.onopen = () => {
  ws.send(JSON.stringify({
    token: 'your-access-token'
  }));
};

// 处理消息
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('收到消息:', data);
};
```

### 消息类型

#### 1. 评论通知
```json
{
  "type": "comment_notification",
  "data": {
    "commenter_name": "用户名",
    "article_title": "文章标题",
    "comment_content": "评论内容..."
  }
}
```

#### 2. 文章更新通知
```json
{
  "type": "article_update",
  "data": {
    "article_id": 1,
    "article_title": "文章标题",
    "action": "created"
  }
}
```

#### 3. 系统通知
```json
{
  "type": "system_notification",
  "data": {
    "title": "通知标题",
    "message": "通知内容",
    "notification_type": "info"
  }
}
```

### 频道订阅

```javascript
// 订阅文章频道
ws.send(JSON.stringify({
  type: 'subscribe',
  data: { channel: 'article_1' }
}));

// 订阅全局文章频道
ws.send(JSON.stringify({
  type: 'subscribe',
  data: { channel: 'articles' }
}));
```

## React 前端集成

### API 接口

提供了完整的 React API 接口：

```javascript
import { authAPI, articleAPI, tagAPI, wsManager } from './api';

// 用户认证
const login = async (credentials) => {
  const response = await authAPI.login(credentials);
  localStorage.setItem('access_token', response.access_token);
  return response;
};

// 文章管理
const createArticle = async (articleData) => {
  return await articleAPI.createArticle(articleData);
};

// WebSocket 连接
wsManager.connect(token);
wsManager.onMessage('comment_notification', (data) => {
  console.log('新评论:', data);
});
```

### 主要功能

- ✅ **用户认证**：登录、注册、Token 管理
- ✅ **文章管理**：CRUD 操作、Markdown 编辑
- ✅ **文件上传**：图片上传、进度显示
- ✅ **评论系统**：多级评论、实时更新
- ✅ **标签管理**：标签 CRUD、热门标签
- ✅ **实时通知**：WebSocket 连接、消息处理
- ✅ **错误处理**：统一错误处理、重试机制

## 邮件功能

### 功能特性

- ✅ **异步处理**: 使用 FastAPI BackgroundTasks 异步发送邮件
- ✅ **多种邮件类型**: 欢迎邮件、密码重置、评论通知
- ✅ **HTML 支持**: 支持纯文本和 HTML 格式邮件
- ✅ **配置灵活**: 可通过环境变量控制邮件功能开关
- ✅ **错误处理**: 完善的错误处理和日志记录

### 邮件类型

1. **欢迎邮件** (`send_welcome_email`)
   - 用户注册时自动发送
   - 包含欢迎信息和系统介绍

2. **密码重置邮件** (`send_password_reset_email`)
   - 用户请求密码重置时发送
   - 包含重置链接和说明

3. **评论通知邮件** (`send_comment_notification_email`)
   - 文章收到新评论时发送给作者
   - 包含评论内容和文章信息

### 使用方法

#### 在 API 中使用

```python
from fastapi import BackgroundTasks
from app.core.tasks import add_welcome_email_task

@router.post("/register")
async def register(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    # 创建用户...
    
    # 添加欢迎邮件任务
    add_welcome_email_task(background_tasks, user.email, user.username)
    
    return {"message": "User registered successfully"}
```

#### 直接使用邮件服务

```python
from app.core.email import email_service

# 发送欢迎邮件
success = email_service.send_welcome_email("user@example.com", "用户名")

# 发送密码重置邮件
success = email_service.send_password_reset_email(
    "user@example.com", "用户名", "reset-token"
)

# 发送评论通知邮件
success = email_service.send_comment_notification_email(
    "author@example.com", "作者名", "文章标题", "评论内容"
)
```

### 测试邮件功能

```bash
# 运行邮件测试脚本
python test_email.py
```

测试脚本会：
1. 检查邮件配置
2. 测试各种邮件类型
3. 验证后台任务功能

## LaTeX 数学公式支持

### 功能特性

- ✅ **多种公式格式**: 支持行内公式 ($...$) 和块级公式 ($$...$$)
- ✅ **LaTeX 环境**: 支持 equation、align、matrix 等环境
- ✅ **实时预览**: 提供 LaTeX 预览功能
- ✅ **语法验证**: 自动验证 LaTeX 语法
- ✅ **高质量渲染**: 使用 pdflatex 生成高质量图片
- ✅ **化学公式**: 支持 mhchem 化学公式
- ✅ **图表绘制**: 支持 TikZ 和 pgfplots

### 支持的 LaTeX 包

- `amsmath`: 数学公式
- `amssymb`: 数学符号
- `physics`: 物理符号
- `siunitx`: 单位和数字
- `chemfig`: 化学结构
- `tikz`: 图形绘制
- `pgfplots`: 数据图表
- `mhchem`: 化学公式

### 使用方法

#### 1. 在文章中使用 LaTeX

```markdown
# 数学公式示例

## 行内公式
当 $a \neq 0$ 时，方程 $ax^2 + bx + c = 0$ 的解为：

## 块级公式
二次方程的求根公式：

$$x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$$

## 积分公式
定积分：

$$\int_{0}^{\infty} e^{-x} dx = 1$$

## 矩阵
$$A = \begin{pmatrix}
a & b \\
c & d
\end{pmatrix}$$

## 化学公式
$$\ce{H2O + CO2 -> H2CO3}$$
```

#### 2. LaTeX 预览 API

```bash
# 预览 LaTeX 内容
curl -X POST "http://127.0.0.1:8000/api/v1/articles/latex/preview" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "latex_content=\frac{a}{b}&block_type=block"
```

#### 3. LaTeX 语法验证

```bash
# 验证 LaTeX 语法
curl -X POST "http://127.0.0.1:8000/api/v1/articles/latex/validate" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "latex_content=\frac{a}{b}"
```

#### 4. 创建包含 LaTeX 的文章

```python
import requests

article_data = {
    "title": "LaTeX 测试文章",
    "content": "# 数学公式\n\n二次方程：$ax^2 + bx + c = 0$\n\n求根公式：\n\n$$x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$$",
    "summary": "测试 LaTeX 功能",
    "status": "published",
    "tags": ["LaTeX", "数学"],
    "has_latex": True,
    "latex_content": "\\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}"
}

response = requests.post(
    "http://127.0.0.1:8000/api/v1/articles",
    json=article_data,
    headers={"Authorization": f"Bearer {access_token}"}
)
```

### API 端点

#### 1. LaTeX 预览
- **POST** `/api/v1/articles/latex/preview`
- **参数**: 
  - `latex_content`: LaTeX 内容
  - `block_type`: 公式类型 (`inline` 或 `block`)
- **返回**: 渲染后的图片 URL

#### 2. LaTeX 验证
- **POST** `/api/v1/articles/latex/validate`
- **参数**: `latex_content`: LaTeX 内容
- **返回**: 验证结果和错误信息

#### 3. 获取 LaTeX 图片
- **GET** `/api/v1/articles/latex/{filename}`
- **返回**: LaTeX 渲染的图片文件

### 测试 LaTeX 功能

```bash
# 运行 LaTeX 功能测试
python test_latex.py
```

测试脚本会：
1. 测试 LaTeX 语法验证
2. 测试 LaTeX 预览功能
3. 测试包含 LaTeX 的文章创建
4. 验证 LaTeX 渲染结果

### 系统要求

LaTeX 功能需要以下系统依赖：

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install texlive-full imagemagick
```

#### CentOS/RHEL
```bash
sudo yum install texlive-scheme-full ImageMagick
```

#### macOS
```bash
brew install texlive imagemagick
```

#### Windows
1. 安装 MiKTeX: https://miktex.org/
2. 安装 ImageMagick: https://imagemagick.org/
3. 将安装路径添加到系统 PATH

### 故障排除

#### LaTeX 渲染失败

**问题**: LaTeX 内容无法渲染为图片

**解决方案**:
- 检查系统是否安装了 pdflatex 和 ImageMagick
- 确认 LaTeX 语法是否正确
- 查看服务器日志中的错误信息
- 检查 uploads/latex 目录权限

#### 图片转换失败

**问题**: PDF 无法转换为 PNG

**解决方案**:
- 确认 ImageMagick 安装正确
- 检查 convert 命令是否可用
- 验证输出目录权限
- 检查磁盘空间是否充足

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

## 故障排除

### 常见问题

#### 1. 邮件发送失败

**问题**: 邮件发送失败或超时

**解决方案**:
- 检查 SMTP 配置是否正确
- 确认邮箱密码是应用专用密码
- 检查网络连接和防火墙设置
- 查看日志中的具体错误信息

#### 2. 邮件功能未启用

**问题**: 邮件功能被禁用

**解决方案**:
- 设置 `EMAIL_ENABLED=true` 在 `.env` 文件中
- 确保所有邮件配置都已正确设置

#### 3. 后台任务不执行

**问题**: BackgroundTasks 不工作

**解决方案**:
- 确保在 API 端点中正确注入 `BackgroundTasks`
- 检查任务函数是否正确添加
- 查看服务器日志确认任务执行

#### 4. 文件上传失败

**问题**: 文件上传返回错误

**解决方案**:
- 检查文件大小是否超过限制（5MB）
- 确认文件格式是否支持
- 检查上传目录权限
- 查看服务器日志

#### 5. WebSocket 连接失败

**问题**: WebSocket 无法连接

**解决方案**:
- 确认服务器正在运行
- 检查 WebSocket URL 是否正确
- 确认 Token 是否有效
- 查看浏览器控制台错误信息

#### 6. Redis 连接失败

**问题**: Redis 连接错误

**解决方案**:
- 确保 Redis 服务正在运行
- 检查 Redis URL 配置
- 确认 Redis 端口可访问

#### 7. 数据库连接问题

**问题**: 数据库连接失败

**解决方案**:
- 检查数据库 URL 配置
- 确保数据库文件有写入权限
- 运行数据库迁移

### 日志查看

查看详细的错误日志：

```bash
# 启动时查看日志
python start.py

# 或使用 uvicorn 查看详细日志
uvicorn main:app --reload --host 127.0.0.1 --port 8000 --log-level debug
```

## 开发指南

### 添加新的邮件类型

1. 在 `app/core/email.py` 中添加新的邮件方法
2. 在 `app/core/tasks.py` 中添加对应的任务函数
3. 在需要的地方调用任务函数

### 自定义邮件模板

邮件模板在 `EmailService` 类中定义，可以修改 HTML 和文本内容来自定义样式。

### 扩展后台任务

可以在 `TaskService` 类中添加新的异步任务，用于处理其他后台操作。

### 添加新的 WebSocket 消息类型

1. 在 `app/core/websocket.py` 中添加新的通知方法
2. 在相应的 API 端点中调用通知方法
3. 在前端添加对应的消息处理器

### 扩展文件上传功能

1. 修改 `app/api/v1/article.py` 中的文件上传逻辑
2. 添加新的文件类型支持
3. 实现文件处理和处理后的回调

### 添加新的 API 端点

1. 在 `app/api/v1/` 下创建新的路由文件
2. 在 `main.py` 中注册路由
3. 添加相应的 Schema 和模型

### 前端开发

1. 在 `frontend/src/api/index.js` 中添加新的 API 方法
2. 创建对应的 React 组件
3. 实现状态管理和错误处理

## 性能优化

### 数据库优化

- 使用索引优化查询性能
- 实现分页查询
- 使用缓存减少数据库访问

### 缓存策略

- Redis 缓存热点数据
- 实现缓存失效机制
- 使用 CDN 加速静态资源

### 异步处理

- 使用 BackgroundTasks 处理耗时操作
- 实现任务队列
- 优化邮件发送和文件处理

## 安全考虑

### 认证安全

- JWT Token 过期时间设置
- Token 黑名单机制
- 密码强度验证

### 文件上传安全

- 文件类型验证
- 文件大小限制
- 文件名安全处理

### API 安全

- 输入验证和清理
- SQL 注入防护
- XSS 攻击防护

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！ 