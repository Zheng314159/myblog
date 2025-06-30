#!/usr/bin/env python3
"""
Test OAuth health check endpoints
"""

import requests
import json
import sys

def test_oauth_health():
    """Test OAuth health check endpoints"""
    base_url = "http://localhost:8000"
    
    print("🔍 Testing OAuth Health Check Endpoints")
    print("=" * 50)
    
    # Test GitHub OAuth health
    print("\n1. Testing GitHub OAuth Health:")
    try:
        response = requests.get(f"{base_url}/api/v1/oauth/health/github", timeout=15)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {data['status']}")
            print(f"   📝 Message: {data['message']}")
        else:
            print(f"   ❌ HTTP {response.status_code}: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test Google OAuth health
    print("\n2. Testing Google OAuth Health:")
    try:
        response = requests.get(f"{base_url}/api/v1/oauth/health/google", timeout=15)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {data['status']}")
            print(f"   📝 Message: {data['message']}")
        else:
            print(f"   ❌ HTTP {response.status_code}: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test OAuth providers endpoint
    print("\n3. Testing OAuth Providers Endpoint:")
    try:
        response = requests.get(f"{base_url}/api/v1/oauth/providers", timeout=15)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Found {len(data['providers'])} providers:")
            for provider in data['providers']:
                print(f"      - {provider['display_name']}: {provider['status']}")
                print(f"        Message: {provider['message']}")
        else:
            print(f"   ❌ HTTP {response.status_code}: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Summary:")
    print("- If Google status is 'unavailable', the Google login button will be hidden")
    print("- If GitHub status is 'unavailable', the GitHub login button will be disabled")
    print("- Network issues will be automatically detected and handled gracefully")

if __name__ == "__main__":
    test_oauth_health() 