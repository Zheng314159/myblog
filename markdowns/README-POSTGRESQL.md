docker exec -it myblog-postgres-1 psql -U your_user -d blogdb

SELECT tablename FROM pg_tables WHERE schemaname = 'public';

使用 GUI 客户端连接容器中的 PostgreSQL
例如使用 DBeaver、TablePlus、pgAdmin、DataGrip，连接

docker exec -it myblog-postgres-1 bash
psql -U postgres -d blogdb

docker exec -it myblog-postgres-1 psql -U tiancai -d blogdb
#  显示所有表
\dt
# 查询具体表结构
\d article
# 查询当前数据库名
\c
# 退出
\q
SELECT id, title, tsv FROM article LIMIT 5;
\df+ update_article_tsvector
\d+ article
SELECT id FROM article WHERE tsv @@ plainto_tsquery('你的测试关键词');

