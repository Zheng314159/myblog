#!/usr/bin/env python3
"""
快速切换EMAIL_ENABLED设置的工具
"""
import os
import sys

def toggle_email_enabled():
    """切换EMAIL_ENABLED设置"""
    env_file = '.env'
    
    if not os.path.exists(env_file):
        print("❌ .env文件不存在")
        return False
    
    # 读取.env文件
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查当前状态
    current_enabled = 'EMAIL_ENABLED=true' in content
    print(f"当前EMAIL_ENABLED状态: {current_enabled}")
    
    # 切换到相反状态
    new_enabled = not current_enabled
    
    if current_enabled:
        content = content.replace('EMAIL_ENABLED=true', 'EMAIL_ENABLED=false')
        print("🔄 切换到: false")
    else:
        content = content.replace('EMAIL_ENABLED=false', 'EMAIL_ENABLED=true')
        print("🔄 切换到: true")
    
    # 写回文件
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ EMAIL_ENABLED已设置为: {new_enabled}")
    print("\n💡 提示:")
    print("1. 现在可以运行 python test_dynamic_config.py 来测试动态切换")
    print("2. 或者直接测试注册/登录功能")
    print("3. 无需重启服务器，配置会自动重新加载")
    
    return True

def set_email_enabled(enabled: bool):
    """设置EMAIL_ENABLED为指定值"""
    env_file = '.env'
    
    if not os.path.exists(env_file):
        print("❌ .env文件不存在")
        return False
    
    # 读取.env文件
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查当前状态
    current_enabled = 'EMAIL_ENABLED=true' in content
    print(f"当前EMAIL_ENABLED状态: {current_enabled}")
    
    if current_enabled == enabled:
        print(f"✅ EMAIL_ENABLED已经是 {enabled}")
        return True
    
    # 设置新状态
    if enabled:
        content = content.replace('EMAIL_ENABLED=false', 'EMAIL_ENABLED=true')
        print("🔄 设置为: true")
    else:
        content = content.replace('EMAIL_ENABLED=true', 'EMAIL_ENABLED=false')
        print("🔄 设置为: false")
    
    # 写回文件
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ EMAIL_ENABLED已设置为: {enabled}")
    return True

def show_current_status():
    """显示当前状态"""
    env_file = '.env'
    
    if not os.path.exists(env_file):
        print("❌ .env文件不存在")
        return
    
    # 读取.env文件
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查当前状态
    current_enabled = 'EMAIL_ENABLED=true' in content
    print(f"当前EMAIL_ENABLED状态: {current_enabled}")
    
    # 显示相关配置
    lines = content.split('\n')
    email_configs = [line for line in lines if 'EMAIL' in line.upper() and '=' in line]
    
    print("\n📧 邮箱相关配置:")
    for config in email_configs:
        if 'PASSWORD' in config.upper():
            # 隐藏密码
            key, value = config.split('=', 1)
            print(f"  {key.strip()}: {'*' * len(value.strip())}")
        else:
            print(f"  {config.strip()}")

def main():
    """主函数"""
    print("邮箱功能切换工具")
    print("=" * 30)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'toggle':
            toggle_email_enabled()
        elif command == 'on':
            set_email_enabled(True)
        elif command == 'off':
            set_email_enabled(False)
        elif command == 'status':
            show_current_status()
        else:
            print("❌ 未知命令")
            print("用法:")
            print("  python toggle_email.py toggle  # 切换状态")
            print("  python toggle_email.py on      # 启用邮箱")
            print("  python toggle_email.py off     # 禁用邮箱")
            print("  python toggle_email.py status  # 显示状态")
    else:
        # 交互模式
        print("请选择操作:")
        print("1. 切换EMAIL_ENABLED状态")
        print("2. 启用邮箱功能")
        print("3. 禁用邮箱功能")
        print("4. 显示当前状态")
        print("5. 退出")
        
        choice = input("\n请输入选择 (1-5): ").strip()
        
        if choice == '1':
            toggle_email_enabled()
        elif choice == '2':
            set_email_enabled(True)
        elif choice == '3':
            set_email_enabled(False)
        elif choice == '4':
            show_current_status()
        elif choice == '5':
            print("👋 再见！")
        else:
            print("❌ 无效选择")

if __name__ == "__main__":
    main() 