import sqlite3

def check_donation_tables():
    try:
        conn = sqlite3.connect('blog.db')
        cursor = conn.cursor()
        
        # 检查捐赠相关表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%donation%';")
        donation_tables = cursor.fetchall()
        print("捐赠相关表:", [t[0] for t in donation_tables])
        
        # 检查所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        all_tables = cursor.fetchall()
        print("所有表:", [t[0] for t in all_tables])
        
        # 检查 donation_config 表的结构
        if donation_tables:
            cursor.execute("PRAGMA table_info(donation_config);")
            columns = cursor.fetchall()
            print("donation_config 表结构:")
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
        
        conn.close()
        
    except Exception as e:
        print(f"检查数据库时出错: {e}")

if __name__ == "__main__":
    check_donation_tables() 