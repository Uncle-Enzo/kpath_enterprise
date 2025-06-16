"""
API Key Management Module for KPath Enterprise (Fixed to work with current DB schema)

This module handles API key generation, validation, and management.
Adapted to work with the existing database schema.
"""

import hashlib
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
import psycopg2
from psycopg2 import sql
import json
import logging

logger = logging.getLogger(__name__)


class APIKeyManager:
    """Manages API keys for the KPath Enterprise system."""
    
    # API key prefix for identification
    KEY_PREFIX = "kpe_"
    # Key length (excluding prefix)
    KEY_LENGTH = 32
    
    def __init__(self, db_connection):
        """
        Initialize the API Key Manager.
        
        Args:
            db_connection: PostgreSQL connection object or SQLAlchemy session
        """
        self.db = db_connection
    
    def generate_api_key(self) -> str:
        """
        Generate a new API key.
        
        Returns:
            str: A new API key with prefix
        """
        # Generate secure random string
        alphabet = string.ascii_letters + string.digits
        random_part = ''.join(secrets.choice(alphabet) for _ in range(self.KEY_LENGTH))
        return f"{self.KEY_PREFIX}{random_part}"
    
    def hash_api_key(self, api_key: str) -> str:
        """
        Hash an API key for secure storage.
        
        Args:
            api_key: The plain text API key
            
        Returns:
            str: SHA256 hash of the API key
        """
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    def create_api_key(self, user_id: int, name: Optional[str] = None,
                      permissions: Optional[Dict[str, Any]] = None,
                      expires_in_days: Optional[int] = None,
                      rate_limit: Optional[int] = None) -> Tuple[str, Dict[str, Any]]:
        """
        Create a new API key for a user.
        
        Args:
            user_id: ID of the user
            name: Optional name for the API key
            permissions: Optional permissions dict (defaults to {"search": True})
            expires_in_days: Optional expiration in days
            rate_limit: Optional rate limit per hour
            
        Returns:
            Tuple of (api_key, key_info_dict)
        """
        # Generate new key
        api_key = self.generate_api_key()
        key_hash = self.hash_api_key(api_key)
        
        # Convert permissions to scopes for backward compatibility
        if permissions is None:
            permissions = {"search": True}
        
        # Extract scopes from permissions
        scopes = [key for key, value in permissions.items() if value]
        
        # Calculate expiration
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        try:
            # Check if it's SQLAlchemy session or raw connection
            if hasattr(self.db, 'execute') and hasattr(self.db, 'commit'):
                # SQLAlchemy session
                from backend.models.models import APIKey
                
                new_key = APIKey(
                    key_hash=key_hash,
                    user_id=user_id,
                    name=name,
                    scopes=scopes,
                    expires_at=expires_at,
                    active=True
                )
                
                self.db.add(new_key)
                self.db.commit()
                
                key_info = {
                    "id": new_key.id,
                    "user_id": user_id,
                    "name": name,
                    "prefix": api_key[:12],  # First 12 chars as prefix
                    "permissions": permissions,
                    "scopes": scopes,
                    "expires_at": expires_at.isoformat() if expires_at else None,
                    "created_at": new_key.created_at.isoformat(),
                    "active": True,
                    "rate_limit": rate_limit or 1000
                }
                
            else:
                # Raw psycopg2 connection
                cursor = self.db.cursor()
                cursor.execute("""
                    INSERT INTO api_keys (user_id, key_hash, name, scopes, expires_at, active)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id, created_at
                """, (user_id, key_hash, name, scopes, expires_at, True))
                
                key_id, created_at = cursor.fetchone()
                self.db.commit()
                
                key_info = {
                    "id": key_id,
                    "user_id": user_id,
                    "name": name,
                    "prefix": api_key[:12],  # First 12 chars as prefix
                    "permissions": permissions,
                    "scopes": scopes,
                    "expires_at": expires_at.isoformat() if expires_at else None,
                    "created_at": created_at.isoformat(),
                    "active": True,
                    "rate_limit": rate_limit or 1000
                }
            
            logger.info(f"Created API key for user {user_id}")
            return api_key, key_info
            
        except Exception as e:
            if hasattr(self.db, 'rollback'):
                self.db.rollback()
            logger.error(f"Failed to create API key: {e}")
            raise
    
    def validate_api_key(self, api_key: str, required_scope: str = "search") -> Optional[Dict[str, Any]]:
        """
        Validate an API key and check scopes.
        
        Args:
            api_key: The API key to validate
            required_scope: The scope to check for (default: "search")
            
        Returns:
            Dict with key info if valid, None if invalid
        """
        key_hash = self.hash_api_key(api_key)
        
        try:
            if hasattr(self.db, 'execute') and hasattr(self.db, 'query'):
                # SQLAlchemy session
                from backend.models.models import APIKey, User
                
                result = self.db.query(APIKey, User).join(User, APIKey.user_id == User.id).filter(
                    APIKey.key_hash == key_hash,
                    APIKey.active == True,
                    User.is_active == True
                ).first()
                
                if not result:
                    return None
                
                api_key_obj, user = result
                
                # Check if key is expired
                if api_key_obj.expires_at and api_key_obj.expires_at < datetime.utcnow():
                    logger.warning(f"API key is expired")
                    return None
                
                # Check scopes
                if api_key_obj.scopes and required_scope not in api_key_obj.scopes:
                    logger.warning(f"API key lacks scope: {required_scope}")
                    return None
                
                # Update last used timestamp
                api_key_obj.last_used = datetime.utcnow()
                self.db.commit()
                
                return {
                    "key_id": api_key_obj.id,
                    "user_id": user.id,
                    "username": user.email,  # Using email as username for now
                    "scopes": api_key_obj.scopes or [],
                    "name": api_key_obj.name
                }
                
            else:
                # Raw psycopg2 connection
                cursor = self.db.cursor()
                cursor.execute("""
                    SELECT k.id, k.user_id, k.scopes, k.expires_at, k.active,
                           k.name, k.last_used, u.email
                    FROM api_keys k
                    JOIN users u ON k.user_id = u.id
                    WHERE k.key_hash = %s AND k.active = TRUE AND u.is_active = TRUE
                """, (key_hash,))
                
                result = cursor.fetchone()
                if not result:
                    return None
                
                key_id, user_id, scopes, expires_at, active, name, last_used, username = result
                
                # Check if key is expired
                if expires_at and expires_at < datetime.utcnow():
                    logger.warning(f"API key is expired")
                    return None
                
                # Check scopes
                if scopes and required_scope not in scopes:
                    logger.warning(f"API key lacks scope: {required_scope}")
                    return None
                
                # Update last used timestamp
                cursor.execute("""
                    UPDATE api_keys 
                    SET last_used = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (key_id,))
                self.db.commit()
                
                return {
                    "key_id": key_id,
                    "user_id": user_id,
                    "username": username,
                    "scopes": scopes or [],
                    "name": name
                }
                
        except Exception as e:
            logger.error(f"Error validating API key: {e}")
            return None
    
    def list_api_keys(self, user_id: int) -> list:
        """
        List all API keys for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of API key info dicts
        """
        try:
            if hasattr(self.db, 'query'):
                # SQLAlchemy session
                from backend.models.models import APIKey
                
                keys = self.db.query(APIKey).filter(APIKey.user_id == user_id).all()
                
                result = []
                for key in keys:
                    result.append({
                        "id": key.id,
                        "name": key.name,
                        "scopes": key.scopes or [],
                        "expires_at": key.expires_at.isoformat() if key.expires_at else None,
                        "last_used": key.last_used.isoformat() if key.last_used else None,
                        "created_at": key.created_at.isoformat(),
                        "active": key.active
                    })
                
                return result
                
            else:
                # Raw psycopg2 connection
                cursor = self.db.cursor()
                cursor.execute("""
                    SELECT id, name, scopes, expires_at, last_used, created_at, active
                    FROM api_keys
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                """, (user_id,))
                
                results = cursor.fetchall()
                
                keys = []
                for result in results:
                    key_id, name, scopes, expires_at, last_used, created_at, active = result
                    keys.append({
                        "id": key_id,
                        "name": name,
                        "scopes": scopes or [],
                        "expires_at": expires_at.isoformat() if expires_at else None,
                        "last_used": last_used.isoformat() if last_used else None,
                        "created_at": created_at.isoformat(),
                        "active": active
                    })
                
                return keys
                
        except Exception as e:
            logger.error(f"Error listing API keys: {e}")
            return []
    
    def deactivate_api_key(self, key_id: int, user_id: int) -> bool:
        """
        Deactivate an API key.
        
        Args:
            key_id: ID of the API key
            user_id: ID of the user (for security)
            
        Returns:
            bool: True if successful
        """
        try:
            if hasattr(self.db, 'query'):
                # SQLAlchemy session
                from backend.models.models import APIKey
                
                key = self.db.query(APIKey).filter(
                    APIKey.id == key_id,
                    APIKey.user_id == user_id
                ).first()
                
                if key:
                    key.active = False
                    self.db.commit()
                    return True
                    
            else:
                # Raw psycopg2 connection
                cursor = self.db.cursor()
                cursor.execute("""
                    UPDATE api_keys 
                    SET active = FALSE
                    WHERE id = %s AND user_id = %s
                """, (key_id, user_id))
                
                if cursor.rowcount > 0:
                    self.db.commit()
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deactivating API key: {e}")
            return False
    
    def log_api_request(self, api_key_id: Optional[int], endpoint: str, method: str,
                       status_code: int, response_time_ms: int = 0):
        """Log an API request for analytics."""
        try:
            if hasattr(self.db, 'add'):
                # SQLAlchemy session
                from backend.models.models import APIRequestLog
                
                log = APIRequestLog(
                    api_key_id=api_key_id,
                    endpoint=endpoint,
                    method=method,
                    status_code=status_code,
                    response_time_ms=response_time_ms
                )
                
                self.db.add(log)
                self.db.commit()
                
            else:
                # Raw psycopg2 connection
                cursor = self.db.cursor()
                cursor.execute("""
                    INSERT INTO api_request_logs 
                    (api_key_id, endpoint, method, status_code, response_time_ms)
                    VALUES (%s, %s, %s, %s, %s)
                """, (api_key_id, endpoint, method, status_code, response_time_ms))
                self.db.commit()
                
        except Exception as e:
            logger.error(f"Error logging API request: {e}")
