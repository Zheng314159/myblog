import requests
import json

def test_config_api():
    try:
        # 测试 /api/v1/config 接口
        print("测试 /api/v1/config 接口...")
        response = requests.get("http://127.0.0.1:8000/api/v1/config")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            config = response.json()
            print("配置数据获取成功！")
            print(f"应用名称: {config.get('app_name')}")
            print(f"调试模式: {config.get('debug')}")
            print(f"邮箱启用: {config.get('email_enabled')}")
        else:
            print(f"错误响应: {response.text}")
            
        # 测试 /api/v1/config/statistics 接口
        print("\n测试 /api/v1/config/statistics 接口...")
        response = requests.get("http://127.0.0.1:8000/api/v1/config/statistics")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            stats = response.json()
            print("统计数据获取成功！")
            print(f"文章总数: {stats.get('total_articles')}")
            print(f"用户总数: {stats.get('total_users')}")
            print(f"媒体文件总数: {stats.get('total_media')}")
        else:
            print(f"错误响应: {response.text}")
            
    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == "__main__":
    test_config_api() 