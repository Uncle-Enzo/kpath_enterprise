"""
Quick test of KPATH Enterprise API
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_api():
    print("Testing KPATH Enterprise API...")
    
    # 1. Test health endpoint
    print("\n1. Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/api/v1/health/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # 2. Test login
    print("\n2. Testing login...")
    login_data = {
        "username": "admin@kpath.local",
        "password": "admin123"
    }
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        data=login_data
    )
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✅ Login successful!")
        print(f"Token: {token[:20]}...")
        
        # 3. Test authenticated endpoint
        print("\n3. Testing authenticated endpoint (list services)...")
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BASE_URL}/api/v1/services/",
            headers=headers
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Total services: {data.get('total', 0)}")
        if data.get('items'):
            print("Services found:")
            for service in data['items']:
                print(f"  - {service['name']}: {service['description']}")
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_api()
