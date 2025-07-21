from passlib.context import CryptContext
import sqlite3

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed = pwd_context.hash("admin123")

conn = sqlite3.connect("blog.db")
cur = conn.cursor()
cur.execute(
    "UPDATE user SET hashed_password = ? WHERE username = ?",
    (hashed, "admin")
)
conn.commit()
conn.close()
print("admin 密码已加密并更新为 admin123") 