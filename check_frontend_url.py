#!/usr/bin/env python3
"""
检查前端URL配置
"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def check_frontend_url():
    """检查前端URL配置"""
    print("=== 前端URL配置检查 ===")
    
    # 从环境变量获取配置
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    print(f"当前FRONTEND_URL: {frontend_url}")
    
    # 检查.env文件
    env_file = '.env'
    if os.path.exists(env_file):
        print(f"\n.env文件存在")
        
        # 读取.env文件内容
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否包含FRONTEND_URL
        if 'FRONTEND_URL=' in content:
            print("✅ .env文件中已配置FRONTEND_URL")
        else:
            print("⚠️  .env文件中未配置FRONTEND_URL")
            print("建议添加: FRONTEND_URL=http://localhost:3000")
    else:
        print("❌ .env文件不存在")
    
    # 测试配置
    print(f"\n=== 测试配置 ===")
    print(f"重置密码链接将使用: {frontend_url}/reset-password?token=...")
    
    # 检查端口
    if ":3000" in frontend_url:
        print("✅ 端口配置为3000（React默认端口）")
    elif ":5173" in frontend_url:
        print("✅ 端口配置为5173（Vite默认端口）")
    else:
        print(f"⚠️  使用自定义端口: {frontend_url}")
    
    return frontend_url

def set_frontend_url(url: str):
    """设置前端URL"""
    print(f"\n=== 设置前端URL为: {url} ===")
    
    env_file = '.env'
    
    if not os.path.exists(env_file):
        print("❌ .env文件不存在，请先创建")
        return False
    
    # 读取.env文件
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换或添加FRONTEND_URL
    if 'FRONTEND_URL=' in content:
        # 替换现有的配置
        lines = content.split('\n')
        new_lines = []
        for line in lines:
            if line.startswith('FRONTEND_URL='):
                new_lines.append(f'FRONTEND_URL={url}')
            else:
                new_lines.append(line)
        content = '\n'.join(new_lines)
        print("✅ 已更新现有FRONTEND_URL配置")
    else:
        # 添加新配置
        content += f'\nFRONTEND_URL={url}'
        print("✅ 已添加FRONTEND_URL配置")
    
    # 写回文件
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 前端URL已设置为: {url}")
    return True

def main():
    """主函数"""
    print("前端URL配置工具")
    print("=" * 50)
    
    # 检查当前配置
    current_url = check_frontend_url()
    
    # 询问是否需要修改
    print(f"\n当前前端URL: {current_url}")
    choice = input("是否需要修改前端URL？(y/n): ").strip().lower()
    
    if choice == 'y':
        new_url = input("请输入新的前端URL (例如: http://localhost:3000): ").strip()
        if new_url:
            if set_frontend_url(new_url):
                print("\n✅ 配置已更新，请重启服务器以应用新配置")
            else:
                print("\n❌ 配置更新失败")
        else:
            print("\n❌ URL不能为空")
    else:
        print("\n✅ 保持当前配置")
    
    print("\n=== 使用说明 ===")
    print("1. 确保前端服务器正在运行")
    print("2. 确保FRONTEND_URL配置正确")
    print("3. 重启后端服务器以应用配置")
    print("4. 重新发送重置密码邮件以使用新链接")

if __name__ == "__main__":
    main() 