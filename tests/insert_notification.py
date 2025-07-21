import sqlite3

conn = sqlite3.connect("blog.db")
cur = conn.cursor()
cur.execute(
    "INSERT INTO system_notification (title, message, notification_type, is_sent) VALUES (?, ?, ?, ?)",
    ("生产公告", "欢迎使用生产环境通知推送！", "info", 0)
)
conn.commit()
conn.close()
print("插入成功") 