#!/usr/bin/env python3
"""
测试文章发布功能
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000/api/v1"

def test_login():
    """测试登录获取token"""
    print("=== 测试登录 ===")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"登录状态码: {response.status_code}")
        print(f"登录响应: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token")
        else:
            print("登录失败")
            return None
    except Exception as e:
        print(f"登录异常: {e}")
        return None

def test_create_article(token):
    """测试创建文章"""
    print("\n=== 测试创建文章 ===")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    article_data = {
        "title": "测试文章标题",
        "content": "这是一篇测试文章的内容。\n\n支持 **Markdown** 格式。",
        "summary": "测试文章摘要",
        "status": "published",
        "tags": ["测试", "技术"],
        "has_latex": False,
        "latex_content": None
    }
    
    try:
        response = requests.post(f"{BASE_URL}/articles/", json=article_data, headers=headers)
        print(f"创建文章状态码: {response.status_code}")
        print(f"创建文章响应: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"文章创建成功，ID: {data.get('id')}")
            return data.get('id')
        else:
            print("文章创建失败")
            return None
    except Exception as e:
        print(f"创建文章异常: {e}")
        return None

def test_create_draft(token):
    """测试保存草稿"""
    print("\n=== 测试保存草稿 ===")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    article_data = {
        "title": "测试草稿标题",
        "content": "这是一篇测试草稿的内容。",
        "summary": "测试草稿摘要",
        "status": "draft",
        "tags": ["草稿"],
        "has_latex": False,
        "latex_content": None
    }
    
    try:
        response = requests.post(f"{BASE_URL}/articles/", json=article_data, headers=headers)
        print(f"保存草稿状态码: {response.status_code}")
        print(f"保存草稿响应: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"草稿保存成功，ID: {data.get('id')}")
            return data.get('id')
        else:
            print("草稿保存失败")
            return None
    except Exception as e:
        print(f"保存草稿异常: {e}")
        return None

def test_get_article(article_id, token=None):
    """测试获取文章"""
    print(f"\n=== 测试获取文章 {article_id} ===")
    
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        response = requests.get(f"{BASE_URL}/articles/{article_id}", headers=headers)
        print(f"获取文章状态码: {response.status_code}")
        print(f"获取文章响应: {response.text}")
        
        if response.status_code == 200:
            print("文章获取成功")
        else:
            print("文章获取失败")
    except Exception as e:
        print(f"获取文章异常: {e}")

def main():
    print("开始测试文章发布功能...")
    
    # 1. 登录获取token
    token = test_login()
    if not token:
        print("无法获取token，测试终止")
        return
    
    # 2. 测试创建已发布文章
    article_id = test_create_article(token)
    if article_id:
        test_get_article(article_id, token)
    
    # 3. 测试保存草稿
    draft_id = test_create_draft(token)
    if draft_id:
        test_get_article(draft_id, token)
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    main() 