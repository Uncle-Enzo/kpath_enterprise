"""
Debug authentication issues
"""
import requests
import json

# Test login
print("Testing login...")
login_response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    data={
        "username": "admin@kpath.ai",
        "password": "1234rt4rd"
    },
    headers={"Content-Type": "application/x-www-form-urlencoded"}
)

print(f"Login status: {login_response.status_code}")
if login_response.status_code == 200:
    token_data = login_response.json()
    print(f"Token received: {token_data.get('access_token', 'NO TOKEN')[:50]}...")
    print(f"User data: {json.dumps(token_data.get('user', {}), indent=2)}")
    
    # Test accessing users endpoint
    print("\nTesting /users endpoint...")
    users_response = requests.get(
        "http://localhost:8000/api/v1/users",
        headers={"Authorization": f"Bearer {token_data['access_token']}"}
    )
    print(f"Users endpoint status: {users_response.status_code}")
    if users_response.status_code != 200:
        print(f"Users error: {users_response.text}")
    
    # Test accessing API keys endpoint
    print("\nTesting /api-keys endpoint...")
    keys_response = requests.get(
        "http://localhost:8000/api/v1/api-keys",
        headers={"Authorization": f"Bearer {token_data['access_token']}"}
    )
    print(f"API Keys endpoint status: {keys_response.status_code}")
    if keys_response.status_code != 200:
        print(f"API Keys error: {keys_response.text}")
else:
    print(f"Login failed: {login_response.text}")
