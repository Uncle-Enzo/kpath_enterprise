#!/usr/bin/env python3
"""
Simple API Key Creation Script (No external dependencies)

This script creates an API key directly in the database.
"""

import sys
import os
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

if __name__ == "__main__":
    print("🔑 Creating API Key for KPath Enterprise")
    print("=" * 50)
    
    try:
        from backend.core.database import SessionLocal
        from backend.models.models import User, APIKey
        
        # Create database session
        db = SessionLocal()
        
        # Get the admin user
        admin_user = db.query(User).filter(User.email == 'admin@kpath.ai').first()
        if not admin_user:
            print("❌ Admin user not found!")
            sys.exit(1)
            
        print(f"✅ Found admin user: {admin_user.email} (ID: {admin_user.id})")
        
        # Generate API key
        api_key = generate_api_key()
        key_hash = hash_api_key(api_key)
        
        # Create API key record
        new_key = APIKey(
            key_hash=key_hash,
            user_id=admin_user.id,
            name="Admin API Key",
            scopes=["search", "admin"],
            expires_at=datetime.utcnow() + timedelta(days=365),  # 1 year
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
        
        # Test curl command
        print(f"\n🧪 Test your API key with curl:")
        print(f'curl "http://localhost:8000/api/v1/search?query=customer%20data&api_key={api_key}"')
        
        print(f"\n📋 Or test with header:")
        print(f'curl -H "X-API-Key: {api_key}" "http://localhost:8000/api/v1/search?query=customer%20data"')
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
