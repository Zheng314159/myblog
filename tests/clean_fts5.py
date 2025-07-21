import sqlite3

db_path = "blog.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()

# 删除所有FTS5相关触发器
for trig in ["articles_ai", "articles_ad", "articles_au"]:
    try:
        c.execute(f"DROP TRIGGER IF EXISTS {trig}")
        print(f"已删除触发器 {trig}")
    except Exception as e:
        print(f"删除触发器 {trig} 失败: {e}")

# 删除所有FTS5相关表
for tbl in [
    "articles_fts", "articles_fts_config", "articles_fts_data",
    "articles_fts_docsize", "articles_fts_content", "articles_fts_idx"
]:
    try:
        c.execute(f"DROP TABLE IF EXISTS {tbl}")
        print(f"已删除表 {tbl}")
    except Exception as e:
        print(f"删除表 {tbl} 失败: {e}")

conn.commit()
conn.close()
print("FTS5相关表和触发器清理完成")