#!/usr/bin/env python3
"""
服务器重启脚本
"""

import subprocess
import time
import requests
import os
import signal
import psutil

def find_server_process():
    """查找运行中的服务器进程"""
    print("🔍 查找运行中的服务器进程...")
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] == 'python' and proc.info['cmdline']:
                cmdline = ' '.join(proc.info['cmdline'])
                if 'main.py' in cmdline or 'uvicorn' in cmdline:
                    print(f"   找到服务器进程: PID {proc.info['pid']}")
                    return proc.info['pid']
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    print("   未找到运行中的服务器进程")
    return None

def stop_server():
    """停止服务器"""
    print("🛑 停止服务器...")
    
    pid = find_server_process()
    if pid:
        try:
            os.kill(pid, signal.SIGTERM)
            print(f"   已发送停止信号到进程 {pid}")
            
            # 等待进程结束
            for i in range(10):
                try:
                    os.kill(pid, 0)  # 检查进程是否还存在
                    print(f"   等待进程结束... ({i+1}/10)")
                    time.sleep(1)
                except OSError:
                    print("   ✅ 服务器已停止")
                    return True
            
            # 如果进程还在运行，强制终止
            print("   ⚠️ 强制终止进程...")
            os.kill(pid, signal.SIGKILL)
            time.sleep(2)
            print("   ✅ 服务器已强制停止")
            return True
            
        except Exception as e:
            print(f"   ❌ 停止服务器失败: {e}")
            return False
    else:
        print("   ✅ 没有运行中的服务器")
        return True

def start_server():
    """启动服务器"""
    print("🚀 启动服务器...")
    
    try:
        # 使用subprocess启动服务器
        process = subprocess.Popen(
            ['python', 'main.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print(f"   服务器进程已启动: PID {process.pid}")
        
        # 等待服务器启动
        print("   等待服务器启动...")
        for i in range(30):
            try:
                response = requests.get('http://localhost:8000/health', timeout=2)
                if response.status_code == 200:
                    print("   ✅ 服务器启动成功")
                    return True
            except:
                pass
            
            time.sleep(1)
            if i % 5 == 0:
                print(f"   等待中... ({i+1}/30)")
        
        print("   ❌ 服务器启动超时")
        return False
        
    except Exception as e:
        print(f"   ❌ 启动服务器失败: {e}")
        return False

def test_login_page_cache():
    """测试登录页面缓存"""
    print("\n🔍 测试登录页面缓存...")
    
    try:
        response = requests.get('http://localhost:8000/jianai/login', timeout=10)
        
        print(f"   登录页面状态码: {response.status_code}")
        print(f"   Cache-Control: {response.headers.get('Cache-Control', 'Not set')}")
        print(f"   Pragma: {response.headers.get('Pragma', 'Not set')}")
        print(f"   Expires: {response.headers.get('Expires', 'Not set')}")
        
        if 'no-cache' not in response.headers.get('Cache-Control', ''):
            print("   ✅ 登录页面可以被缓存")
            return True
        else:
            print("   ❌ 登录页面仍然不缓存")
            return False
            
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🔧 服务器重启工具")
    print("=" * 50)
    
    # 停止服务器
    if not stop_server():
        print("❌ 无法停止服务器")
        return
    
    # 等待一下确保端口释放
    time.sleep(2)
    
    # 启动服务器
    if not start_server():
        print("❌ 无法启动服务器")
        return
    
    # 测试登录页面缓存
    print("\n" + "=" * 50)
    choice = input("是否要测试登录页面缓存？(y/n): ").lower().strip()
    if choice in ['y', 'yes', '是', 'Y']:
        test_login_page_cache()
    
    print("\n🎉 服务器重启完成！")
    print("💡 现在可以正常访问管理后台了")
    print("   登录地址: http://localhost:8000/jianai/login")
    print("   用户名: admin")
    print("   密码: admin123")

if __name__ == "__main__":
    main() 