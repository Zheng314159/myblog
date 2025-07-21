
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
docker compose -f docker-compose.dev.yml run --rm backend ls -lh blog.db

docker compose -f docker-compose.dev.yml run --rm \
  -v $(pwd)/blog.db:/app/blog.db \
  backend python scripts/migrate_sqlite_to_pg.py
