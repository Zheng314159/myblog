#!/usr/bin/env python3
"""
Test frontend OAuth functionality
"""

import requests
import json
import sys

def test_frontend_oauth():
    """Test frontend OAuth functionality"""
    backend_url = "http://localhost:8000"
    frontend_url = "http://localhost:3000"
    
    print("🔍 Testing Frontend OAuth Functionality")
    print("=" * 50)
    
    # Test backend OAuth providers endpoint
    print("\n1. Testing Backend OAuth Providers:")
    try:
        response = requests.get(f"{backend_url}/api/v1/oauth/providers", timeout=10)
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
    
    # Test frontend login page accessibility
    print("\n2. Testing Frontend Login Page:")
    try:
        response = requests.get(f"{frontend_url}/login", timeout=10)
        if response.status_code == 200:
            print("   ✅ Frontend login page is accessible")
            # Check if the page contains OAuth-related content
            content = response.text.lower()
            if "github" in content or "google" in content or "oauth" in content:
                print("   ✅ Page contains OAuth-related content")
            else:
                print("   ⚠️  Page doesn't seem to contain OAuth content")
        else:
            print(f"   ❌ HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test individual OAuth health endpoints
    print("\n3. Testing Individual OAuth Health Endpoints:")
    
    # GitHub health
    try:
        response = requests.get(f"{backend_url}/api/v1/oauth/health/github", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ GitHub: {data['status']} - {data['message']}")
        else:
            print(f"   ❌ GitHub: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ GitHub: {e}")
    
    # Google health
    try:
        response = requests.get(f"{backend_url}/api/v1/oauth/health/google", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Google: {data['status']} - {data['message']}")
        else:
            print(f"   ❌ Google: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ Google: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Frontend OAuth Behavior:")
    print("- GitHub OAuth button should be visible and enabled")
    print("- Google OAuth button should be hidden (due to network issues)")
    print("- Users can still use traditional login/register")
    print("- Network issues are handled gracefully")

if __name__ == "__main__":
    test_frontend_oauth() 