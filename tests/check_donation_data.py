import sqlite3
from decimal import Decimal

def check_donation_data():
    try:
        conn = sqlite3.connect('blog.db')
        cursor = conn.cursor()
        
        # 检查 donationconfig 表的数据
        cursor.execute("SELECT * FROM donationconfig;")
        config_data = cursor.fetchall()
        print(f"donationconfig 表中有 {len(config_data)} 条记录")
        
        if config_data:
            print("第一条记录:")
            for i, value in enumerate(config_data[0]):
                print(f"  列 {i}: {value}")
        
        # 检查表结构
        cursor.execute("PRAGMA table_info(donationconfig);")
        columns = cursor.fetchall()
        print("\ndonationconfig 表结构:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        # 检查 donationrecord 表
        cursor.execute("SELECT COUNT(*) FROM donationrecord;")
        record_count = cursor.fetchone()[0]
        print(f"\ndonationrecord 表中有 {record_count} 条记录")
        
        # 检查 donationgoal 表
        cursor.execute("SELECT COUNT(*) FROM donationgoal;")
        goal_count = cursor.fetchone()[0]
        print(f"donationgoal 表中有 {goal_count} 条记录")
        
        conn.close()
        
    except Exception as e:
        print(f"检查数据时出错: {e}")

if __name__ == "__main__":
    check_donation_data() 