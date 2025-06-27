#!/usr/bin/env python3
"""
Debug script to test token creation and verification
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.core.security import create_access_token, verify_token
from datetime import timedelta

def test_token_creation_and_verification():
    """Test token creation and verification"""
    print("=== Token Debug Test ===")
    print(f"Secret key: {settings.secret_key[:20]}...")
    print(f"Algorithm: {settings.algorithm}")
    
    # Test data
    test_data = {
        "sub": "testuser",
        "user_id": 1,
        "role": "user"
    }
    
    print(f"\nTest data: {test_data}")
    
    # Create token
    print("\n--- Creating token ---")
    token = create_access_token(test_data)
    print(f"Token created: {token[:50]}...")
    
    # Verify token
    print("\n--- Verifying token ---")
    payload = verify_token(token)
    print(f"Verification result: {payload}")
    
    if payload:
        print("✅ Token verification successful!")
        print(f"Username: {payload.get('sub')}")
        print(f"User ID: {payload.get('user_id')}")
        print(f"Role: {payload.get('role')}")
        print(f"Type: {payload.get('type')}")
    else:
        print("❌ Token verification failed!")
    
    # Test with a sample token from localStorage (if provided)
    print("\n--- Testing with sample token ---")
    sample_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlciIsInVzZXJfaWQiOjEsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzM1Njg5NjAwLCJ0eXBlIjoiYWNjZXNzIn0.example"
    
    try:
        payload = verify_token(sample_token)
        print(f"Sample token verification: {payload}")
    except Exception as e:
        print(f"Sample token verification failed: {e}")

if __name__ == "__main__":
    test_token_creation_and_verification() 