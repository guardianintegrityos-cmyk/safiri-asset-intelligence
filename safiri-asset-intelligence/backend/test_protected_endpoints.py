#!/usr/bin/env python3
"""
SECURITY_QUICKSTART - Phase 3: Test Protected Endpoints & Data Masking
Verify that search results are properly masked to prevent PII leakage
"""

import requests
import json

BASE_URL = "http://localhost:8001"

print("="*70)
print("SECURITY_QUICKSTART - Phase 3: Protected Endpoints & Data Masking")
print("="*70)

# Step 1: Get JWT token
print("\n[Step 1] Authenticating...")
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    params={
        "username": "testuser",
        "password": "TestPassword123!"
    }
)

if login_response.status_code != 200:
    print(f"❌ Authentication failed: {login_response.text}")
    exit(1)

login_data = login_response.json()
access_token = login_data["access_token"]
print(f"✅ Authentication successful")
print(f"   Access Token: {access_token[:50]}...")

# Step 2: Test /search endpoint with JWT
print("\n[Step 2] Testing /search endpoint with JWT token...")
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

# Test search query
search_params = {
    "query": "James Mwangi 12345678",  # Query expects single string
    "country": "kenya"  # Optional country parameter
}

search_response = requests.get(
    f"{BASE_URL}/search",
    params=search_params,
    headers=headers
)

print(f"   Status Code: {search_response.status_code}")

if search_response.status_code == 200:
    print("   ✅ /search endpoint accessible with JWT token")
    
    search_data = search_response.json()
    print(f"\n   Response keys: {list(search_data.keys())}")
    
    # Check for masking
    print("\n[Step 3] Verifying Data Masking...")
    
    # Pretty print response (limited)
    response_str = json.dumps(search_data, indent=2)[:500]
    print(f"   Response preview:\n{response_str}...")
    
    # Look for masked data
    response_full = json.dumps(search_data)
    if "*" in response_full:
        print("\n   ✅ Data masking is ACTIVE (found masked values with *)")
        
        # Count masked fields
        masked_count = response_full.count("*")
        print(f"      Masked characters found: {masked_count}")
    else:
        print("\n   ⚠️  No masked data with * found - verify masking is configured")
    
    # Check for specific PII patterns
    if "TestPassword" in response_full or "12345678" in response_full:
        print("   ⚠️  WARNING: Unmasked sensitive data detected in response!")
    else:
        print("   ✅ No obvious unmasked PII detected in response")
        
elif search_response.status_code == 401:
    print(f"   ❌ JWT token invalid: {search_response.text}")
elif search_response.status_code == 403:
    print(f"   ❌ Access denied: {search_response.text}")
else:
    print(f"   ❌ Unexpected error: {search_response.status_code}")
    print(f"      Response: {search_response.text}")

# Step 4: Test rate limiting
print("\n[Step 4] Testing Rate Limiting (10 searches per hour limit)...")
print("   Making 3 sequential requests to /search...")

success_count = 0
for i in range(3):
    resp = requests.get(
        f"{BASE_URL}/search",
        params={"query": f"TestPerson{i}", "country": "kenya"},
        headers=headers
    )
    
    if resp.status_code == 200:
        success_count += 1
        print(f"   Request {i+1}: ✅ Success")
    elif resp.status_code == 429:
        print(f"   Request {i+1}: ⚠️  Rate limited (Too Many Requests)")
    else:
        print(f"   Request {i+1}: {resp.status_code}")

print(f"   Successful requests: {success_count}/3")

# Step 5: Test fraud detection score
print("\n[Step 5] Testing Fraud Detection...")
fraud_response = requests.get(
    f"{BASE_URL}/fraud-check/12345678",
    headers=headers
)

if fraud_response.status_code == 200:
    fraud_data = fraud_response.json()
    print(f"   ✅ Fraud detection endpoint accessible")
    
    if "fraud_score" in fraud_data:
        score = fraud_data["fraud_score"]
        print(f"      Fraud Score: {score}")
        
        if score < 0.3:
            print(f"      Assessment: Low risk (below 0.3)")
        elif score < 0.6:
            print(f"      Assessment: Medium risk")
        else:
            print(f"      Assessment: High risk (human review needed)")
    else:
        print(f"   Response: {fraud_data}")
else:
    print(f"   ℹ️ Fraud check endpoint status: {fraud_response.status_code}")

print("\n" + "="*70)
print("SECURITY_QUICKSTART - Phase 3 Complete")
print("="*70)
print("\n✅ All endpoint tests completed!")
print("\nNext: Run identity verification tests (Phase 4)")
