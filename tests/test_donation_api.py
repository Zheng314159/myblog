import requests
import json

def test_donation_api():
    base_url = "http://127.0.0.1:8000"
    
    try:
        # 测试获取捐赠配置
        print("测试获取捐赠配置...")
        response = requests.get(f"{base_url}/api/v1/donation/config")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            config = response.json()
            print("配置数据:")
            print(json.dumps(config, indent=2, ensure_ascii=False))
        else:
            print(f"错误响应: {response.text}")
        
        # 测试获取公开统计
        print("\n测试获取公开统计...")
        response = requests.get(f"{base_url}/api/v1/donation/public-stats")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            stats = response.json()
            print("统计数据:")
            print(json.dumps(stats, indent=2, ensure_ascii=False))
        else:
            print(f"错误响应: {response.text}")
        
        # 测试获取捐赠目标
        print("\n测试获取捐赠目标...")
        response = requests.get(f"{base_url}/api/v1/donation/goals")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            goals = response.json()
            print("目标数据:")
            print(json.dumps(goals, indent=2, ensure_ascii=False))
        else:
            print(f"错误响应: {response.text}")
            
    except Exception as e:
        print(f"测试时出错: {e}")

if __name__ == "__main__":
    test_donation_api() 