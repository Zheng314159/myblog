#!/usr/bin/env python3
import os
import shutil
from datetime import datetime

def disable_google_oauth():
    """临时禁用Google OAuth，专注于GitHub OAuth"""
    print("=== 临时禁用Google OAuth ===\n")
    
    # 1. 备份当前.env文件
    env_file = ".env"
    if os.path.exists(env_file):
        backup_file = f".env.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(env_file, backup_file)
        print(f"✅ 已备份.env文件到: {backup_file}")
    else:
        print("❌ 未找到.env文件")
        return
    
    # 2. 读取当前.env文件
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"❌ 读取.env文件失败: {e}")
        return
    
    # 3. 注释掉Google OAuth配置
    new_lines = []
    google_keys = ['GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET']
    google_commented = False
    
    for line in lines:
        stripped_line = line.strip()
        if any(key in stripped_line for key in google_keys):
            if not stripped_line.startswith('#'):
                new_lines.append(f"# {line.rstrip()}\n")
                google_commented = True
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    
    # 4. 写入修改后的.env文件
    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        if google_commented:
            print("✅ 已临时禁用Google OAuth配置")
            print("   - GOOGLE_CLIENT_ID 已注释")
            print("   - GOOGLE_CLIENT_SECRET 已注释")
        else:
            print("ℹ️  Google OAuth配置已经是注释状态")
            
    except Exception as e:
        print(f"❌ 写入.env文件失败: {e}")
        return
    
    # 5. 提供重启说明
    print("\n=== 下一步操作 ===")
    print("1. 重启服务器以应用配置:")
    print("   - 停止当前服务器 (Ctrl+C)")
    print("   - 重新运行: python main.py")
    print("\n2. 验证配置:")
    print("   - GitHub OAuth应该正常工作")
    print("   - Google OAuth应该被禁用")
    print("\n3. 恢复Google OAuth (如果需要):")
    print(f"   - 恢复备份文件: {backup_file}")
    print("   - 或手动取消注释Google配置")
    
    print("\n=== 当前状态 ===")
    print("✅ GitHub OAuth: 启用")
    print("❌ Google OAuth: 临时禁用")
    print("✅ 邮箱密码登录: 可用")

if __name__ == "__main__":
    disable_google_oauth() 