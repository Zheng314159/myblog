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



# 配置虚拟环境路径
poetry config virtualenvs.in-project false
# 重新创建虚拟环境
poetry env use python3.12
# 确认依赖
poetry show
# 查看 Poetry 虚拟环境路径
poetry env info --path
# 列出 site-packages 下的已安装包
poetry run python -m site
# 查找具体包的路径
poetry run python -c "import pycryptodomex; print(pycryptodomex.__file__)"
# 列出所有包及其来源路径
poetry run pip list --format=columns
poetry run pip show pycryptodomex
# 进入虚拟环境手动查
poetry shell
cd $(python -c "import site; print(site.getsitepackages()[0])")
ls -l



# 添加开发依赖
poetry add --group dev pytest pytest-asyncio

# 安装shell补全
poetry completions bash >> ~/.bashrc
# 或 zsh
poetry completions zsh >> ~/.zshrc


# 1. 生成 lock 文件
poetry lock

# 2. 安装依赖
poetry install

# 3. 若你要导出成 requirements.txt 给 Docker 用：
poetry export -f requirements.txt --without-hashes -o requirements.txt
# 运行以下命令来检测 pyproject.toml 是否语法正确：
poetry check
#  试重新锁定依赖验证配置是否有效：
poetry lock --no-update
