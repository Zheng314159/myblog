#!/usr/bin/env python3
import requests
import json

def test_refresh_error():
    url = "http://localhost:8000/api/v1/auth/refresh"
    data = {"refresh_token": "test"}
    
    try:
        response = requests.post(url, json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_refresh_error() 