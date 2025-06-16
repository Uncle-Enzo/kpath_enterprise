#!/usr/bin/env python3
"""
KPath Enterprise API Key Generator

Usage:
    python3 create_production_api_key.py --user-email admin@kpath.ai --name "Production API Key"
    python3 create_production_api_key.py --user-id 3 --name "Development Key" --days 30
"""

import sys
import os
import argparse
import hashlib
import secrets
import string
from datetime import datetime, timedelta

# Add the project root to the path
sys.path.append('/Users/james/claude_development/kpath_enterprise')

def generate_api_key():
    """Generate a new API key"""
    KEY_PREFIX = "kpe_"
    KEY_LENGTH = 32
    
    alphabet = string.ascii_letters + string.digits
    random_part = ''.join(secrets.choice(alphabet) for _ in range(KEY_LENGTH))
    return f"{KEY_PREFIX}{random_part}"

def hash_api_key(api_key: str) -> str:
    """Hash an API key for secure storage"""
    return hashlib.sha256(api_key.encode()).hexdigest()

def create_api_key(user_id=None, user_email=None, name="API Key", scopes=None, expires_in_days=365):
    """Create a new API key"""
    if scopes is None:
        scopes = ["search", "admin"]
    
    try:
        from backend.core.database import SessionLocal
        from backend.models.models import User, APIKey
        
        # Create database session
        db = SessionLocal()
        
        # Get user
        if user_email:
            user = db.query(User).filter(User.email == user_email).first()
        elif user_id:
            user = db.query(User).filter(User.id == user_id).first()
        else:
            print("❌ Must provide either --user-email or --user-id")
            return None
            
        if not user:
            print(f"❌ User not found: {user_email or user_id}")
            return None
            
        print(f"✅ Found user: {user.email} (ID: {user.id})")
        
        # Generate API key
        api_key = generate_api_key()
        key_hash = hash_api_key(api_key)
        
        # Calculate expiration
        expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        # Create API key record
        new_key = APIKey(
            key_hash=key_hash,
            user_id=user.id,
            name=name,
            scopes=scopes,
            expires_at=expires_at,
            active=True
        )
        
        db.add(new_key)
        db.commit()
        
        print(f"✅ Created API key successfully!")
        print(f"   API Key: {api_key}")
        print(f"   Key ID: {new_key.id}")
        print(f"   Name: {new_key.name}")
        print(f"   Scopes: {new_key.scopes}")
        print(f"   Expires: {new_key.expires_at}")
        
        print(f"\n🧪 Test your API key:")
        print(f'curl -H "X-API-Key: {api_key}" "http://localhost:8000/api/v1/search/search?query=customer%20data"')
        
        db.close()
        return api_key
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create API keys for KPath Enterprise")
    parser.add_argument("--user-email", help="User email address")
    parser.add_argument("--user-id", type=int, help="User ID")
    parser.add_argument("--name", default="API Key", help="Name for the API key")
    parser.add_argument("--scopes", nargs="+", default=["search"], help="API key scopes")
    parser.add_argument("--days", type=int, default=365, help="Days until expiration")
    
    args = parser.parse_args()
    
    print("🔑 KPath Enterprise API Key Generator")
    print("=" * 50)
    
    api_key = create_api_key(
        user_id=args.user_id,
        user_email=args.user_email,
        name=args.name,
        scopes=args.scopes,
        expires_in_days=args.days
    )
    
    if api_key:
        print(f"\n🎉 API Key created successfully!")
        print(f"Save this key securely - it cannot be retrieved again.")
    else:
        print(f"\n❌ Failed to create API key.")
        sys.exit(1)
