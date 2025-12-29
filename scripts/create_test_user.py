#!/usr/bin/env python3
"""
Create a test user for development.
This script adds a test user directly to the in-memory database.
Note: This only works if the server is running and you call the signup endpoint.
For a standalone solution, use the signup endpoint via curl or the frontend.
"""

import requests
import sys

API_BASE_URL = "http://localhost:4051"

def create_test_user(email: str = "test@example.com", password: str = "test12345", name: str = "Test User"):
    """Create a test user via the signup endpoint."""
    url = f"{API_BASE_URL}/v1/auth/signup/email"
    
    payload = {
        "email": email,
        "password": password,
        "name": name
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Test user created successfully!")
            print(f"\n📧 Email: {email}")
            print(f"🔑 Password: {password}")
            print(f"👤 Name: {name}")
            print(f"\n🎫 Access Token: {data.get('access_token', 'N/A')[:50]}...")
            return True
        elif response.status_code == 400:
            error = response.json().get('detail', 'Unknown error')
            if 'already registered' in error.lower():
                print(f"ℹ️  User {email} already exists. You can use these credentials to log in:")
                print(f"   Email: {email}")
                print(f"   Password: {password}")
                return True
            else:
                print(f"❌ Error: {error}")
                return False
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Error: Could not connect to {API_BASE_URL}")
        print("   Make sure the control-plane server is running:")
        print("   cd apps/control-plane && uvicorn app.main:app --reload --port 4051")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        email = sys.argv[1]
        password = sys.argv[2] if len(sys.argv) > 2 else "test12345"
        name = sys.argv[3] if len(sys.argv) > 3 else "Test User"
    else:
        email = "test@example.com"
        password = "test12345"
        name = "Test User"
    
    print("🚀 Creating test user...")
    print(f"   API: {API_BASE_URL}")
    print()
    
    success = create_test_user(email, password, name)
    sys.exit(0 if success else 1)

