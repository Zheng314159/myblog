#!/usr/bin/env python3
import requests
import json

def test_statistics():
    url = "http://localhost:8000/api/v1/config/statistics"
    
    try:
        response = requests.get(url)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Statistics data:")
            for key, value in data.items():
                print(f"  {key}: {value}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_statistics() 