#!/usr/bin/env python3
"""
测试动态配置切换功能
"""
import os
import time
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

BASE_URL = "http://localhost:8000"

def test_config_endpoint():
    """测试配置端点"""
    print("=== 测试配置端点 ===")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/auth/config")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            config = response.json()
            print(f"邮箱功能启用: {config.get('email_enabled', False)}")
            print(f"OAuth功能启用: {config.get('oauth_enabled', False)}")
            return config
        else:
            print(f"❌ 请求失败: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return None

def modify_env_file(enabled: bool):
    """修改.env文件中的EMAIL_ENABLED设置"""
    print(f"\n=== 修改EMAIL_ENABLED为 {enabled} ===")
    
    if not os.path.exists('.env'):
        print("❌ .env文件不存在")
        return False
    
    # 读取.env文件
    with open('.env', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换EMAIL_ENABLED设置
    if 'EMAIL_ENABLED=true' in content:
        content = content.replace('EMAIL_ENABLED=true', f'EMAIL_ENABLED={str(enabled).lower()}')
    elif 'EMAIL_ENABLED=false' in content:
        content = content.replace('EMAIL_ENABLED=false', f'EMAIL_ENABLED={str(enabled).lower()}')
    else:
        # 如果不存在，添加到文件末尾
        content += f'\nEMAIL_ENABLED={str(enabled).lower()}'
    
    # 写回文件
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 已修改EMAIL_ENABLED={enabled}")
    return True

def test_dynamic_switch():
    """测试动态切换功能"""
    print("=== 测试动态配置切换 ===")
    
    # 初始状态
    print("\n1. 检查初始状态...")
    initial_config = test_config_endpoint()
    if not initial_config:
        print("❌ 无法获取初始配置")
        return
    
    initial_enabled = initial_config.get('email_enabled', False)
    print(f"初始EMAIL_ENABLED: {initial_enabled}")
    
    # 切换到相反状态
    new_enabled = not initial_enabled
    print(f"\n2. 切换到 {new_enabled}...")
    
    if not modify_env_file(new_enabled):
        print("❌ 修改.env文件失败")
        return
    
    # 等待一下让文件系统同步
    time.sleep(1)
    
    # 测试新状态
    print(f"\n3. 检查新状态...")
    new_config = test_config_endpoint()
    if not new_config:
        print("❌ 无法获取新配置")
        return
    
    new_enabled_actual = new_config.get('email_enabled', False)
    print(f"新EMAIL_ENABLED: {new_enabled_actual}")
    
    # 验证切换是否成功
    if new_enabled_actual == new_enabled:
        print("✅ 动态切换成功！")
    else:
        print("❌ 动态切换失败")
        print(f"期望: {new_enabled}, 实际: {new_enabled_actual}")
    
    # 切换回原状态
    print(f"\n4. 切换回原状态 {initial_enabled}...")
    modify_env_file(initial_enabled)
    time.sleep(1)
    
    final_config = test_config_endpoint()
    if final_config:
        final_enabled = final_config.get('email_enabled', False)
        print(f"最终EMAIL_ENABLED: {final_enabled}")
        
        if final_enabled == initial_enabled:
            print("✅ 恢复原状态成功！")
        else:
            print("❌ 恢复原状态失败")

def test_multiple_switches():
    """测试多次切换"""
    print("\n=== 测试多次切换 ===")
    
    for i in range(3):
        print(f"\n--- 第 {i+1} 次切换 ---")
        
        # 获取当前状态
        config = test_config_endpoint()
        if not config:
            print("❌ 无法获取配置")
            continue
        
        current_enabled = config.get('email_enabled', False)
        print(f"当前状态: {current_enabled}")
        
        # 切换到相反状态
        new_enabled = not current_enabled
        modify_env_file(new_enabled)
        time.sleep(1)
        
        # 验证切换
        new_config = test_config_endpoint()
        if new_config:
            actual_enabled = new_config.get('email_enabled', False)
            if actual_enabled == new_enabled:
                print(f"✅ 第 {i+1} 次切换成功")
            else:
                print(f"❌ 第 {i+1} 次切换失败")

def main():
    """主函数"""
    print("动态配置切换测试工具")
    print("=" * 50)
    
    # 检查服务器是否运行
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        if response.status_code != 200:
            print("❌ 服务器未正常运行，请先启动服务器")
            return
    except:
        print("❌ 无法连接到服务器，请先启动服务器")
        return
    
    print("✅ 服务器连接正常")
    
    # 测试动态切换
    test_dynamic_switch()
    
    # 测试多次切换
    test_multiple_switches()
    
    print("\n=== 测试完成 ===")
    print("如果所有测试都通过，说明动态配置切换功能正常工作！")

if __name__ == "__main__":
    main() 