#!/usr/bin/env python3
"""
修复邮箱配置脚本
"""
import os
import shutil

def fix_email_config():
    """修复邮箱配置"""
    print("=== 修复邮箱配置 ===")
    
    # 检查.env文件是否存在
    if not os.path.exists('.env'):
        print("❌ .env文件不存在，正在从env.example创建...")
        shutil.copy('env.example', '.env')
        print("✅ 已创建.env文件")
    
    # 读取.env文件内容
    with open('.env', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查当前EMAIL_ENABLED设置
    if 'EMAIL_ENABLED=true' in content:
        print("当前EMAIL_ENABLED=true，正在修改为false...")
        content = content.replace('EMAIL_ENABLED=true', 'EMAIL_ENABLED=false')
        
        # 写回文件
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ 已修改EMAIL_ENABLED=false")
    elif 'EMAIL_ENABLED=false' in content:
        print("✅ EMAIL_ENABLED已经是false")
    else:
        print("⚠️ 未找到EMAIL_ENABLED设置")
    
    print("\n请重启服务器以应用新的配置！")

if __name__ == "__main__":
    fix_email_config() 