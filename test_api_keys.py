#!/usr/bin/env python3
"""
API Key Testing Script

This script tests the API key functionality for KPath Enterprise.
"""

import sys
import os
import json
import requests
from datetime import datetime

# Add the project root to the path
sys.path.append('/Users/james/claude_development/kpath_enterprise')

from api_key_manager_fixed import APIKeyManager
from backend.core.database import SessionLocal
from backend.models.models import User

def test_api_key_creation():
    """Test creating API keys"""
    print("Testing API Key Creation...")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Get the admin user
        admin_user = db.query(User).filter(User.email == 'admin@kpath.ai').first()
        if not admin_user:
            print("❌ Admin user not found!")
            return None
            
        print(f"✅ Found admin user: {admin_user.email} (ID: {admin_user.id})")
        
        # Create API key manager
        api_manager = APIKeyManager(db)
        
        # Create a test API key
        api_key, key_info = api_manager.create_api_key(
            user_id=admin_user.id,
            name="Test API Key",
            scopes=["search", "admin"],
            expires_in_days=30
        )
        
        print(f"✅ Created API key: {api_key}")
        print(f"   Key info: {json.dumps(key_info, indent=2)}")
        
        return api_key, key_info
        
    except Exception as e:
        print(f"❌ Error creating API key: {e}")
        return None
    finally:
        db.close()

def test_api_key_validation(api_key):
    """Test validating API keys"""
    print("\nTesting API Key Validation...")
    
    db = SessionLocal()
    
    try:
        api_manager = APIKeyManager(db)
        
        # Test validation
        key_info = api_manager.validate_api_key(api_key, "search")
        
        if key_info:
            print(f"✅ API key validation successful")
            print(f"   User ID: {key_info['user_id']}")
            print(f"   Username: {key_info['username']}")
            print(f"   Scopes: {key_info['scopes']}")
        else:
            print("❌ API key validation failed")
            
    except Exception as e:
        print(f"❌ Error validating API key: {e}")
    finally:
        db.close()

def test_api_key_search_endpoint(api_key):
    """Test using API key with search endpoint"""
    print("\nTesting API Key with Search Endpoint...")
    
    # Test with query parameter
    try:
        response = requests.get(
            "http://localhost:8000/api/v1/search",
            params={
                "query": "customer data management",
                "limit": 5,
                "api_key": api_key
            },
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Search with API key (query parameter) successful")
            data = response.json()
            print(f"   Found {data.get('total_results', 0)} results")
        else:
            print(f"❌ Search failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing search endpoint: {e}")
    
    # Test with header
    try:
        response = requests.get(
            "http://localhost:8000/api/v1/search",
            params={
                "query": "notification services",
                "limit": 5
            },
            headers={
                "X-API-Key": api_key
            },
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Search with API key (header) successful")
            data = response.json()
            print(f"   Found {data.get('total_results', 0)} results")
        else:
            print(f"❌ Search failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing search endpoint with header: {e}")

def list_existing_keys():
    """List existing API keys"""
    print("\nListing Existing API Keys...")
    
    db = SessionLocal()
    
    try:
        admin_user = db.query(User).filter(User.email == 'admin@kpath.ai').first()
        if not admin_user:
            print("❌ Admin user not found!")
            return
            
        api_manager = APIKeyManager(db)
        keys = api_manager.list_api_keys(admin_user.id)
        
        if keys:
            print(f"✅ Found {len(keys)} API keys:")
            for key in keys:
                print(f"   - ID: {key['id']}, Name: {key['name']}, Active: {key['active']}")
                print(f"     Scopes: {key['scopes']}")
                print(f"     Created: {key['created_at']}")
                if key['last_used']:
                    print(f"     Last used: {key['last_used']}")
                print()
        else:
            print("ℹ️  No API keys found")
            
    except Exception as e:
        print(f"❌ Error listing API keys: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("🔑 KPath Enterprise API Key Testing")
    print("=" * 50)
    
    # List existing keys first
    list_existing_keys()
    
    # Create a new API key
    result = test_api_key_creation()
    
    if result:
        api_key, key_info = result
        
        # Test validation
        test_api_key_validation(api_key)
        
        # Test with search endpoint
        test_api_key_search_endpoint(api_key)
        
        print(f"\n🎉 Testing complete!")
        print(f"Your API key: {api_key}")
        print(f"You can now use this key for API requests.")
    else:
        print("\n❌ API key creation failed, skipping further tests")
