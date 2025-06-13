#!/usr/bin/env python3
"""
Test script for API Key authentication with FastAPI endpoints.

This script demonstrates how to:
1. Authenticate with username/password to get a JWT token
2. Create an API key using the JWT token
3. Use the API key to make search requests
"""

import requests
import json
import sys
from typing import Optional, Dict, Any


class KPathAPIClient:
    """Client for interacting with KPath Enterprise API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self.jwt_token: Optional[str] = None
        self.api_key: Optional[str] = None
    
    def login(self, username: str, password: str) -> bool:
        """Login with username/password to get JWT token."""
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/auth/login",
                json={"username": username, "password": password}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.jwt_token = data.get("access_token")
                print(f"✓ Successfully logged in as {username}")
                return True
            else:
                print(f"✗ Login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"✗ Login error: {e}")
            return False
    
    def create_api_key(self, name: str, rate_limit: int = 1000) -> Optional[str]:
        """Create a new API key."""
        if not self.jwt_token:
            print("✗ Must login first to create API key")
            return None
        
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/api-keys",
                headers={"Authorization": f"Bearer {self.jwt_token}"},
                json={
                    "name": name,
                    "permissions": {"search": True},
                    "rate_limit": rate_limit
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.api_key = data.get("api_key")
                print(f"✓ Created API key: {self.api_key[:20]}...")
                print(f"  Name: {data.get('name')}")
                print(f"  Rate limit: {data.get('rate_limit')}/hour")
                return self.api_key
            else:
                print(f"✗ Failed to create API key: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"✗ API key creation error: {e}")
            return None
    def search_with_api_key(self, query: str, limit: int = 10) -> Optional[Dict[str, Any]]:
        """Search using API key authentication."""
        if not self.api_key:
            print("✗ No API key available")
            return None
        
        try:
            # Use GET method with API key
            response = requests.get(
                f"{self.base_url}/api/v1/search",
                headers={"X-API-Key": self.api_key},
                params={
                    "query": query,
                    "limit": limit
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Search successful: Found {data.get('total_results', 0)} results")
                
                # Check rate limit headers
                if "X-RateLimit-Remaining" in response.headers:
                    print(f"  Rate limit remaining: {response.headers['X-RateLimit-Remaining']}")
                
                return data
            else:
                print(f"✗ Search failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"✗ Search error: {e}")
            return None
    
    def list_api_keys(self) -> Optional[list]:
        """List all API keys for the user."""
        if not self.jwt_token:
            print("✗ Must login first")
            return None
        
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/api-keys",
                headers={"Authorization": f"Bearer {self.jwt_token}"}
            )
            
            if response.status_code == 200:
                keys = response.json()
                print(f"✓ Found {len(keys)} API keys")
                for key in keys:
                    print(f"  - {key['name']} ({key['prefix']}...)")
                return keys
            else:
                print(f"✗ Failed to list keys: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"✗ List keys error: {e}")
            return None


def main():
    """Main test function."""
    print("KPath Enterprise API Key Test")
    print("=" * 50)
    
    # Initialize client
    client = KPathAPIClient()
    
    # Test credentials (update these)
    username = "test_user"
    password = "test_password"
    
    # Step 1: Login
    print("\n1. Logging in...")
    if not client.login(username, password):
        print("Failed to login. Please check credentials.")
        return
    
    # Step 2: Create API key
    print("\n2. Creating API key...")
    api_key = client.create_api_key("Test API Key", rate_limit=100)
    if not api_key:
        print("Failed to create API key")
        return
    
    # Step 3: Test search with API key
    print("\n3. Testing search with API key...")
    results = client.search_with_api_key("customer data management", limit=5)
    if results:
        print(f"   Query: '{results.get('query')}'")
        print(f"   Results: {len(results.get('results', []))}")
    
    # Step 4: List API keys
    print("\n4. Listing all API keys...")
    client.list_api_keys()
    
    print("\n✓ Test completed successfully!")
    print(f"\nYour API key: {api_key}")
    print("\nYou can now use this key in your applications:")
    print(f"curl -H 'X-API-Key: {api_key}' '{client.base_url}/api/v1/search?query=test'")


if __name__ == "__main__":
    main()