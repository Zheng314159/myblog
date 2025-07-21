#!/usr/bin/env python3
"""
简单的服务器启动脚本
"""

import uvicorn
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.append(str(Path(__file__).parent))

def main():
    """启动服务器"""
    print("🚀 启动 FastAPI 博客系统...")
    print("=" * 50)
    print("🌐 服务器地址:")
    print("   - 本地访问: http://127.0.0.1:8000")
    print("   - API文档: http://127.0.0.1:8000/docs")
    print("   - ReDoc文档: http://127.0.0.1:8000/redoc")
    print("=" * 50)
    print("按 Ctrl+C 停止服务器")
    print()
    
    try:
        uvicorn.run(
            "main:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 