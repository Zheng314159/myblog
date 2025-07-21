# 安装 Poetry（推荐开始使用）
curl -sSL https://install.python-poetry.org | python3 -
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
python -c "import urllib.request; exec(urllib.request.urlopen('https://install.python-poetry.org').read())"
https://install.python-poetry.org
右键另存为，命名为 install-poetry.py
python install-poetry.py



poetry init            # 初始化项目
poetry add flask       # 安装依赖
poetry run python app.py  # 使用 poetry 虚拟环境运行
| 概念                      | 解释                           |
| ----------------------- | ---------------------------- |
| `pyproject.toml`        | Poetry 的配置文件，管理依赖、版本、构建等     |
| `poetry.lock`           | 锁定依赖的版本，保证跨平台一致性             |
| 虚拟环境（venv）              | Poetry 自动创建并管理，不用手动使用 `venv` |
| 开发依赖 vs 正式依赖            | 用 `--dev` 区分测试工具等开发用依赖       |
| `poetry add` / `remove` | 管理依赖，类似 pip                  |
# 推荐方式
curl -sSL https://install.python-poetry.org | python3 -
mkdir myproject && cd myproject
poetry init
或：poetry init --no-interaction

poetry add requests
poetry add pytest --dev

poetry shell              # 激活虚拟环境
python your_script.py     # 运行项目
或：poetry run python your_script.py

poetry lock   # 锁定当前依赖

# 重新拉项目后
poetry install

# 如果你开发的是库，可以直接用：
poetry build
poetry publish

| 操作         | pnpm 命令             | Poetry 命令                  |
| ---------- | ------------------- | -------------------------- |
| 添加依赖       | `pnpm add axios`    | `poetry add requests`      |
| 添加 dev 依赖  | `pnpm add -D jest`  | `poetry add --dev pytest`  |
| 删除依赖       | `pnpm remove axios` | `poetry remove requests`   |
| 安装依赖       | `pnpm install`      | `poetry install`           |
| 启动脚本       | `pnpm run dev`      | `poetry run python app.py` |
| 生成 lock 文件 | `pnpm-lock.yaml` 自动 | `poetry.lock` 自动生成         |
poetry env info --path



poetry init --no-interaction && poetry add $(cat requirements.txt)

