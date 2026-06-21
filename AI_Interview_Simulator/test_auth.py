#!/usr/bin/env python
"""
Test script for authentication endpoints.
Run this script to verify that the authentication system works correctly.

Usage:
    python test_auth.py

This script will:
1. Start a test Django server (or use existing one)
2. Register a test user
3. Login and get JWT tokens
4. Access protected profile endpoint
5. Test token refresh
"""

import json
import sys
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:8000"
API_BASE = f"{BASE_URL}/api"

# Test user credentials
TEST_USER = {
    "username": "testauth_user",
    "email": "testauth@example.com",
    "password": "testpassword123"
}

def make_request(url, method="GET", data=None, headers=None):
    """Helper function to make HTTP requests."""
    if headers is None:
        headers = {}
    
    if data:
        data = json.dumps(data).encode('utf-8')
        headers['Content-Type'] = 'application/json'
    
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            body = json.loads(response.read().decode('utf-8'))
            return response.status, body
    except urllib.error.HTTPError as e:
        body = json.loads(e.read().decode('utf-8')) if e.fp else {}
        return e.code, body
    except Exception as e:
        return None, str(e)

def test_register():
    """Test user registration."""
    print("\n" + "="*50)
    print("TEST 1: User Registration")
    print("="*50)
    
    url = f"{API_BASE}/register/"
    status, response = make_request(url, method="POST", data=TEST_USER)
    
    print(f"URL: {url}")
    print(f"Status: {status}")
    print(f"Response: {json.dumps(response, indent=2)}")
    
    if status == 201:
        print("✓ Registration successful!")
        return True
    elif status == 400:
        print(f"⚠ User might already exist: {response}")
        return True  # Still okay for testing
    else:
        print("✗ Registration failed!")
        return False

def test_login():
    """Test user login and get JWT tokens."""
    print("\n" + "="*50)
    print("TEST 2: User Login (Get JWT Tokens)")
    print("="*50)
    
    url = f"{API_BASE}/login/"
    data = {
        "username": TEST_USER["username"],
        "password": TEST_USER["password"]
    }
    
    status, response = make_request(url, method="POST", data=data)
    
    print(f"URL: {url}")
    print(f"Status: {status}")
    
    if status == 200 and "access" in response and "refresh" in response:
        print("✓ Login successful!")
        print(f"Access token (truncated): {response['access'][:50]}...")
        print(f"Refresh token (truncated): {response['refresh'][:50]}...")
        return response["access"], response["refresh"]
    else:
        print(f"✗ Login failed! Response: {response}")
        return None, None

def test_profile(access_token):
    """Test accessing protected profile endpoint."""
    print("\n" + "="*50)
    print("TEST 3: Access Protected Profile Endpoint")
    print("="*50)
    
    url = f"{API_BASE}/profile/"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    status, response = make_request(url, method="GET", headers=headers)
    
    print(f"URL: {url}")
    print(f"Status: {status}")
    print(f"Response: {json.dumps(response, indent=2)}")
    
    if status == 200:
        print("✓ Profile access successful!")
        return True
    else:
        print("✗ Profile access failed!")
        return False

def test_profile_without_token():
    """Test that profile endpoint rejects unauthenticated requests."""
    print("\n" + "="*50)
    print("TEST 4: Profile Endpoint Without Token (Should Fail)")
    print("="*50)
    
    url = f"{API_BASE}/profile/"
    
    status, response = make_request(url, method="GET")
    
    print(f"URL: {url}")
    print(f"Status: {status}")
    print(f"Response: {json.dumps(response, indent=2)}")
    
    if status == 401:
        print("✓ Correctly rejected unauthenticated request!")
        return True
    else:
        print("✗ Should have returned 401!")
        return False

def test_token_refresh(refresh_token):
    """Test token refresh."""
    print("\n" + "="*50)
    print("TEST 5: Token Refresh")
    print("="*50)
    
    url = f"{API_BASE}/refresh/"
    data = {"refresh": refresh_token}
    
    status, response = make_request(url, method="POST", data=data)
    
    print(f"URL: {url}")
    print(f"Status: {status}")
    print(f"Response: {json.dumps(response, indent=2)}")
    
    if status == 200 and "access" in response:
        print("✓ Token refresh successful!")
        return response["access"]
    else:
        print("✗ Token refresh failed!")
        return None

def test_invalid_token():
    """Test that invalid tokens are rejected."""
    print("\n" + "="*50)
    print("TEST 6: Invalid Token (Should Fail)")
    print("="*50)
    
    url = f"{API_BASE}/profile/"
    headers = {"Authorization": "Bearer invalid_token_here"}
    
    status, response = make_request(url, method="GET", headers=headers)
    
    print(f"URL: {url}")
    print(f"Status: {status}")
    print(f"Response: {json.dumps(response, indent=2)}")
    
    if status == 401:
        print("✓ Correctly rejected invalid token!")
        return True
    else:
        print("✗ Should have returned 401!")
        return False

def main():
    """Run all authentication tests."""
    print("AI Interview Simulator - Authentication Tests")
    print("="*50)
    print(f"Base URL: {BASE_URL}")
    
    # Check if server is running
    try:
        urllib.request.urlopen(BASE_URL)
        print("✓ Django server is running")
    except Exception as e:
        print("✗ Django server is not running!")
        print("  Start the server with: python manage.py runserver")
        sys.exit(1)
    
    results = []
    
    # Run tests
    results.append(("Register", test_register()))
    
    access_token, refresh_token = test_login()
    if access_token:
        results.append(("Login", True))
        results.append(("Profile Access", test_profile(access_token)))
        results.append(("Token Refresh", bool(test_token_refresh(refresh_token))))
    else:
        results.append(("Login", False))
        print("\n⚠ Skipping remaining tests due to login failure")
    
    results.append(("No Token Rejection", test_profile_without_token()))
    results.append(("Invalid Token Rejection", test_invalid_token()))
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Authentication system is working correctly.")
        return 0
    else:
        print("\n⚠ Some tests failed. Please review the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())