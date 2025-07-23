
docker compose -f docker-compose.dev.yml build backend
docker compose -f docker-compose.dev.yml run --rm backend alembic upgrade head
docker compose -f docker-compose.dev.yml run --rm backend python scripts/init_db.py


  init_db:
    build:
      context: .
      dockerfile: Dockerfile.backend.dev
    command: python scripts/init_db.py
    env_file:
      - .env.development
    depends_on:
      - postgres


docker compose -f docker-compose.dev.yml run --rm init_db

docker compose -f docker-compose.dev.yml up -d redis postgres
docker compose -f docker-compose.dev.yml run --rm backend python scripts/init_db.py
docker compose -f docker-compose.dev.yml run --rm backend python scripts/init_sqlite.py
docker compose -f docker-compose.dev.yml run --rm backend python scripts/migrate_sqlite_to_pg.py
docker exec -it myblog-dev-backend-1 python scripts/migrate_sqlite_to_pg.py

docker compose -f docker-compose.dev.yml run --rm backend ls -lh blog.db

docker compose -f docker-compose.dev.yml run --rm \
  -v $(pwd)/blog.db:/app/blog.db \
  backend python scripts/migrate_sqlite_to_pg.py


# 服务器日志查看
docker compose -f docker-compose.prod.yml logs -f nginx
docker compose -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.prod.yml logs -f frontend
# 停止服务
docker compose -f docker-compose.prod.yml down
# 清理卷和网络
docker compose -f docker-compose.prod.yml down -v
# 构建并启动容器
docker compose -f docker-compose.prod.yml up -d --build

docker compose -f docker-compose.dev.yml -p myblog-dev up -d
docker compose -f docker-compose.prod.yml -p myblog-prod up -d

# 清理旧容器/网络/volume
docker compose -p myblog-dev down -v
docker compose -p myblog-prod down -v
docker network prune
docker volume prune

docker compose -f docker-compose.prod.yml -p myblog-prod exec backend printenv | grep SECRET


docker run -it --rm \
  --entrypoint /bin/sh \
  -v $(pwd)/nginx.conf:/etc/nginx/nginx.conf:ro \
  nginx:alpine
cat /etc/nginx/nginx.conf | nl
grep -rn upstream /etc/nginx/


docker compose -f docker-compose.dev.yml -p myblog-dev run --rm backend python scripts/migrate_sqlite_to_pg.py
docker compose -f docker-compose.prod.yml -p myblog-prod run --rm backend python scripts/migrate_sqlite_to_pg.py

# 容器开发初始化
docker compose -f docker-compose.dev.yml -p myblog-dev run --rm backend python scripts/init_db.py
docker compose -f docker-compose.dev.yml -p myblog-dev run --rm backend python scripts/migrate_sqlite_to_pg.py
docker compose -f docker-compose.dev.yml -p myblog-dev up --build

# 容器开发初始化
docker compose -f docker-compose.prod.yml -p myblog-prod run --rm backend python scripts/init_db.prod.py
docker compose -f docker-compose.prod.yml -p myblog-prod run --rm backend python scripts/migrate_sqlite_to_pg.py
docker compose -f docker-compose.prod.yml -p myblog-prod up --build

docker exec -it <backend-container> bash
ls $(python -c "import sqladmin; print(sqladmin.__path__[0])")/static

