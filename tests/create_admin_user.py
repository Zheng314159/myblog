from passlib.context import CryptContext
import sqlite3
import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed = pwd_context.hash("admin123")

conn = sqlite3.connect("blog.db")
cur = conn.cursor()

# 假设密码已加密，这里用明文admin123（实际应用请用加密）
cur.execute(
    "INSERT INTO user (username, email, full_name, role, is_active, hashed_password, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
    ("admin", "admin@example.com", "超级管理员", "ADMIN", 1, hashed, datetime.datetime.now(), datetime.datetime.now())
)
conn.commit()
conn.close()
print("管理员账号创建成功，密码已加密") 