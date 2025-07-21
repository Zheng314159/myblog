| 注意点         | 说明                                                                                          |
| ----------- | ------------------------------------------------------------------------------------------- |
| 端口映射        | 默认访问 WSL 服务时需通过 `localhost:<端口>`，注意防火墙和 WSL 网络设置。                                           |
| 不支持 systemd | 无法使用 `systemctl`，但你可以用 `supervisord`、`tmux`、`nohup` 等代替服务管理。                                |
| 文件权限        | Windows 与 Linux 文件系统权限管理不同，尽量把代码放在 WSL 的 Linux 目录下 `/home/xxx`，而不是 Windows 的挂载目录 `/mnt/c/`。 |
| 性能差异        | 虽然足够模拟部署，但 WSL 性能仍略低于真实服务器，尤其是文件 I/O、数据库操作时。                                                |
# 非Docker化部署流程：
	# 1. 创建并激活虚拟环境
	python3 -m venv venv
	source venv/bin/activate

	# 2. 安装依赖
	pip install -r requirements.txt

	# 3. 设置环境变量
	export ENVIRONMENT=production

	# 4. 启动数据库（本地 PostgreSQL）
	sudo service postgresql start

	# 5. 启动应用（Gunicorn + Uvicorn workers）
	gunicorn app.main:app -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 --workers 4
#  或者使用 Docker 模拟：
	# 安装 Docker
	sudo apt update && sudo apt install docker.io docker-compose

	# 使用 docker-compose 启动服务
	docker-compose -f docker-compose.production.yml up --build -d
🧪 小技巧
• 使用 .env.production 配置生产环境变量
• 使用 alembic upgrade head 模拟数据库版本迁移
• 使用 curl 或 httpie 模拟请求接口，代替浏览器访问
• 使用 loguru 或 uvicorn.log_config 自定义日志格式，观察日志输出
# 安装依赖组件（仅需一次）
sudo apt update
sudo apt install python3-venv python3-dev postgresql redis git -y

# 配置 PostgreSQL（仅需一次）
sudo -u postgres createuser your_user --createdb
sudo -u postgres psql -c "ALTER USER your_user WITH PASSWORD 'your_password';"
createdb -U your_user your_database

# 日志目录准备
mkdir -p logs
touch logs/access.log logs/error.log

# 启动方式（WSL 中）
bash scripts/deploy_wsl.sh

