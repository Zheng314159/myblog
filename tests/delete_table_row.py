import sqlite3

conn = sqlite3.connect('blog.db')
cursor = conn.cursor()
cursor.execute("DELETE FROM user WHERE id=17")
conn.commit()
cursor.execute("SELECT id, username, role FROM user")
for row in cursor.fetchall():
    print(row)
conn.close() 