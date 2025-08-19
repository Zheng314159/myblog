import sqlite3
import datetime
from passlib.context import CryptContext

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed = pwd_context.hash("admin123")

# 数据库连接
conn = sqlite3.connect("blog.db")
cur = conn.cursor()

# 查询是否存在 admin 用户
cur.execute("SELECT id, email FROM user WHERE username = ?", ("admin",))
row = cur.fetchone()

if not row:
    # 如果不存在，插入
    cur.execute(
        """
        INSERT INTO user (username, email, full_name, role, is_active, hashed_password, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "admin",
            "contemnewton@163.com",
            "超级管理员",
            "ADMIN",
            1,
            hashed,
            datetime.datetime.now(),
            datetime.datetime.now(),
        ),
    )
    print("✅ 创建 admin 账号成功（邮箱：contemnewton@163.com）")

else:
    user_id, current_email = row

    try:
        # 先尝试删除
        cur.execute("DELETE FROM user WHERE id = ?", (user_id,))
        conn.commit()

        # 再重新创建
        cur.execute(
            """
            INSERT INTO user (username, email, full_name, role, is_active, hashed_password, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "admin",
                "contemnewton@163.com",
                "超级管理员",
                "ADMIN",
                1,
                hashed,
                datetime.datetime.now(),
                datetime.datetime.now(),
            ),
        )
        print("♻️ 重新创建 admin 账号成功（邮箱：contemnewton@163.com）")

    except Exception as e:
        conn.rollback()

        # 删除失败 → 更新邮箱为固定值
        cur.execute(
            """
            UPDATE user
            SET email = ?, hashed_password = ?, full_name = ?, role = ?, is_active = ?, updated_at = ?
            WHERE username = ?
            """,
            (
                "contemnewton@163.com",
                hashed,
                "超级管理员",
                "ADMIN",
                1,
                datetime.datetime.now(),
                "admin",
            ),
        )
        print("⚡ 无法删除 admin，已更新邮箱为 contemnewton@163.com")

conn.commit()
conn.close()
