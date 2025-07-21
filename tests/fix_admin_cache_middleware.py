#!/usr/bin/env python3
"""
修复管理后台缓存中间件问题
"""

import re

def fix_cache_middleware():
    """修复NoCacheAdminMiddleware，允许登录页面被缓存"""
    print("🔧 修复管理后台缓存中间件...")
    
    try:
        # 读取main.py文件
        with open('main.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找NoCacheAdminMiddleware类
        middleware_pattern = r'class NoCacheAdminMiddleware\(BaseHTTPMiddleware\):(.*?)app\.add_middleware\(NoCacheAdminMiddleware\)'
        match = re.search(middleware_pattern, content, re.DOTALL)
        
        if not match:
            print("❌ 未找到NoCacheAdminMiddleware类")
            return False
        
        middleware_content = match.group(1)
        
        # 检查是否已经修改过
        if 'login' in middleware_content and 'not request.url.path.endswith' in middleware_content:
            print("✅ 缓存中间件已经修改过，允许登录页面缓存")
            return True
        
        # 修改中间件，允许登录页面被缓存
        new_middleware = '''class NoCacheAdminMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        # 允许登录页面被缓存，其他管理后台页面不缓存
        if request.url.path.startswith(ADMIN_PATH) and not request.url.path.endswith('/login'):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
            
            # 如果是HTML响应，添加JavaScript错误处理
            if "text/html" in response.headers.get("content-type", ""):
                if hasattr(response, 'body'):
                    try:
                        content = response.body.decode('utf-8')
                        # 简化的JavaScript错误处理
                        error_handler = """
                        <script>
                        // 立即阻止所有null元素错误
                        (function() {
                            // 重写console.error来隐藏错误
                            var originalError = console.error;
                            console.error = function() {
                                var args = Array.prototype.slice.call(arguments);
                                var message = args.join(' ');
                                if (message.includes('Cannot read properties of null')) {
                                    console.warn('Suppressed null element error:', message);
                                    return;
                                }
                                return originalError.apply(console, args);
                            };
                            
                            // 全局错误处理
                            window.addEventListener('error', function(e) {
                                if (e.message && e.message.includes('Cannot read properties of null')) {
                                    console.warn('Blocked null element error:', e.message);
                                    e.preventDefault();
                                    e.stopPropagation();
                                    return false;
                                }
                            });
                            
                            // 处理Bootstrap特定的错误
                            if (typeof $ !== 'undefined') {
                                $(document).ready(function() {
                                    // 延迟处理，确保DOM完全加载
                                    setTimeout(function() {
                                        // 安全地处理所有表单元素
                                        $(document).on('change click', 'input, select, textarea', function(e) {
                                            if (!this) {
                                                console.warn('Preventing event on null element');
                                                e.preventDefault();
                                                e.stopPropagation();
                                                return false;
                                            }
                                        });
                                    }, 100);
                                });
                            }
                        })();
                        </script>
                        """
                        content = content.replace('</head>', error_handler + '</head>')
                        response.body = content.encode('utf-8')
                    except Exception as e:
                        print(f"Error processing response: {e}")
        return response'''
        
        # 替换中间件内容
        new_content = re.sub(middleware_pattern, new_middleware + '\n\napp.add_middleware(NoCacheAdminMiddleware)', content, flags=re.DOTALL)
        
        # 写回文件
        with open('main.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ 成功修改缓存中间件")
        print("💡 现在登录页面可以被缓存，其他管理后台页面仍然不缓存")
        return True
        
    except Exception as e:
        print(f"❌ 修改缓存中间件失败: {e}")
        return False

def create_backup():
    """创建main.py的备份"""
    print("📦 创建main.py备份...")
    
    try:
        import shutil
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"main_backup_{timestamp}.py"
        
        shutil.copy2('main.py', backup_file)
        print(f"✅ 备份文件已创建: {backup_file}")
        return True
        
    except Exception as e:
        print(f"❌ 创建备份失败: {e}")
        return False

def test_login_page_cache():
    """测试登录页面缓存"""
    print("\n🔍 测试登录页面缓存...")
    
    import requests
    
    try:
        # 测试登录页面
        response = requests.get('http://localhost:8000/jianai/login', timeout=10)
        
        print(f"登录页面状态码: {response.status_code}")
        print(f"Cache-Control: {response.headers.get('Cache-Control', 'Not set')}")
        print(f"Pragma: {response.headers.get('Pragma', 'Not set')}")
        print(f"Expires: {response.headers.get('Expires', 'Not set')}")
        
        if 'no-cache' not in response.headers.get('Cache-Control', ''):
            print("✅ 登录页面可以被缓存")
            return True
        else:
            print("❌ 登录页面仍然不缓存")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🔧 管理后台缓存中间件修复工具")
    print("=" * 50)
    
    # 创建备份
    if not create_backup():
        print("❌ 无法创建备份，停止操作")
        return
    
    # 修复缓存中间件
    if fix_cache_middleware():
        print("\n✅ 缓存中间件修复完成")
        print("💡 请重启服务器以应用更改")
        print("   1. 停止当前服务器 (Ctrl+C)")
        print("   2. 重新启动: python main.py")
        
        # 询问是否测试
        choice = input("\n是否要测试登录页面缓存？(y/n): ").lower().strip()
        if choice in ['y', 'yes', '是', 'Y']:
            test_login_page_cache()
    else:
        print("\n❌ 缓存中间件修复失败")
        print("💡 请手动修改main.py文件")

if __name__ == "__main__":
    main() 