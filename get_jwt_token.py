#!/usr/bin/env python3
"""Get JWT token for testing."""

import requests
import json

BASE_URL = "http://localhost:8000"

# Login to get JWT token
login_data = {
    "username": "admin@kpath.ai",
    "password": "admin123"  # Default password - update if different
}

response = requests.post(f"{BASE_URL}/api/v1/auth/login", data=login_data)
if response.status_code == 200:
    token_data = response.json()
    print(f"JWT Token: {token_data['access_token']}")
    print(f"Token type: {token_data['token_type']}")
else:
    print(f"Login failed: {response.status_code}")
    print(response.text)
