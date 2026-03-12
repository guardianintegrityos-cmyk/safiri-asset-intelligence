#!/usr/bin/env python3
"""Test authentication endpoints - SECURITY_QUICKSTART Phase 2"""

import requests
import json
import sys

BASE_URL = "http://localhost:8001"

print("="*60)
print("SECURITY_QUICKSTART - Phase 2: Test Authentication")
print("="*60)

# Test 1: Login endpoint
print("\n1. Testing /auth/login endpoint...")
print("   Credentials: testuser / TestPassword123!")

login_response = requests.post(
    f"{BASE_URL}/auth/login",
    params={
        "username": "testuser",
        "password": "TestPassword123!"
    }
)

print(f"   Status Code: {login_response.status_code}")

if login_response.status_code == 200:
    print("   ✅ Login successful!")
    login_data = login_response.json()
    
    if "access_token" in login_data:
        access_token = login_data["access_token"]
        print(f"   Access Token (first 50 chars): {access_token[:50]}...")
        print(f"   Token Type: {login_data.get('token_type', 'Bearer')}")
        
        # Test 2: Use token on protected endpoint
        print("\n2. Testing /search endpoint with JWT token...")
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        search_params = {
            "name": "James Mwangi",
            "national_id": "12345678"
        }
        
        search_response = requests.get(
            f"{BASE_URL}/search",
            params=search_params,
            headers=headers
        )
        
        print(f"   Status Code: {search_response.status_code}")
        
        if search_response.status_code == 200:
            print("   ✅ Search endpoint accessible!")
            search_data = search_response.json()
            
            # Check if data is masked
            if "results" in search_data or "identities" in search_data:
                results = search_data.get("results") or search_data.get("identities", [])
                print(f"   Results: {len(results)} record(s)")
                
                # Check for masking
                print("\n   👉 Checking data masking...")
                if results and len(results) > 0:
                    first_result = results[0]
                    name_field = first_result.get("full_name") or first_result.get("name")
                    if name_field and "*" in str(name_field):
                        print(f"   ✅ Data masking active: {name_field}")
                    else:
                        print(f"   ⚠️  Name not masked: {name_field}")
                else:
                    print("   ℹ️  No results returned (expected for test data)")
        else:
            print(f"   ✗ Search request failed: {search_response.text}")
    else:
        print(f"   Response: {login_data}")
else:
    print(f"   ✗ Login failed")
    print(f"   Response: {login_response.text}")

print("\n" + "="*60)
print("Authentication testing complete!")
print("="*60)
