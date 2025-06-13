"""
API Key Management Module for KPath Enterprise

This module handles API key generation, validation, and management.
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
            db_connection: PostgreSQL connection object
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
                      rate_limit: int = 1000) -> Tuple[str, Dict[str, Any]]:
        """
        Create a new API key for a user.
        
        Args:
            user_id: ID of the user
            name: Optional name for the API key
            permissions: Optional permissions dict (defaults to search only)
            expires_in_days: Optional expiration in days
            rate_limit: Rate limit per hour (default 1000)
            
        Returns:
            Tuple of (api_key, key_info_dict)
        """
        # Generate new key
        api_key = self.generate_api_key()
        key_hash = self.hash_api_key(api_key)
        key_prefix = api_key[:8]  # First 8 chars for identification
        
        # Default permissions
        if permissions is None:
            permissions = {"search": True}
        
        # Calculate expiration
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                INSERT INTO api_keys (user_id, key_hash, key_prefix, name, permissions, expires_at, rate_limit)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id, created_at
            """, (user_id, key_hash, key_prefix, name, json.dumps(permissions), expires_at, rate_limit))            
            key_id, created_at = cursor.fetchone()
            self.db.commit()
            
            key_info = {
                "id": key_id,
                "user_id": user_id,
                "name": name,
                "prefix": key_prefix,
                "permissions": permissions,
                "expires_at": expires_at.isoformat() if expires_at else None,
                "created_at": created_at.isoformat(),
                "rate_limit": rate_limit
            }
            
            logger.info(f"Created API key {key_prefix}... for user {user_id}")
            return api_key, key_info
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create API key: {e}")
            raise
    
    def validate_api_key(self, api_key: str, required_permission: str = "search") -> Optional[Dict[str, Any]]:
        """
        Validate an API key and check permissions.
        
        Args:
            api_key: The API key to validate
            required_permission: The permission to check for (default: "search")
            
        Returns:
            Dict with key info if valid, None if invalid
        """
        key_hash = self.hash_api_key(api_key)
        
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT k.id, k.user_id, k.permissions, k.expires_at, k.is_active,
                       k.rate_limit, k.request_count, k.last_used_at, u.username
                FROM api_keys k
                JOIN users u ON k.user_id = u.id
                WHERE k.key_hash = %s AND k.is_active = TRUE AND u.is_active = TRUE
            """, (key_hash,))
            
            result = cursor.fetchone()
            if not result:
                return None            
            key_id, user_id, permissions, expires_at, is_active, rate_limit, request_count, last_used_at, username = result
            
            # Check if key is expired
            if expires_at and expires_at < datetime.utcnow():
                logger.warning(f"API key {api_key[:8]}... is expired")
                return None
            
            # Check permissions
            perms = json.loads(permissions) if isinstance(permissions, str) else permissions
            if required_permission not in perms or not perms[required_permission]:
                logger.warning(f"API key {api_key[:8]}... lacks permission: {required_permission}")
                return None
            
            # Update last used timestamp
            cursor.execute("""
                UPDATE api_keys 
                SET last_used_at = CURRENT_TIMESTAMP, request_count = request_count + 1
                WHERE id = %s
            """, (key_id,))
            self.db.commit()
            
            return {
                "key_id": key_id,
                "user_id": user_id,
                "username": username,
                "permissions": perms,
                "rate_limit": rate_limit,
                "request_count": request_count + 1
            }
            
        except Exception as e:
            logger.error(f"Error validating API key: {e}")
            return None
    
    def check_rate_limit(self, api_key: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Check if an API key has exceeded its rate limit.
        
        Args:
            api_key: The API key to check
            
        Returns:
            Tuple of (is_within_limit, rate_info)
        """
        key_hash = self.hash_api_key(api_key)
        
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT k.id, k.rate_limit,
                       COUNT(l.id) as requests_last_hour
                FROM api_keys k
                LEFT JOIN api_key_logs l ON k.id = l.api_key_id
                    AND l.created_at > NOW() - INTERVAL '1 hour'
                WHERE k.key_hash = %s
                GROUP BY k.id, k.rate_limit
            """, (key_hash,))
            
            result = cursor.fetchone()
            if not result:
                return False, None
            
            key_id, rate_limit, requests_last_hour = result
            
            rate_info = {
                "rate_limit": rate_limit,
                "requests_last_hour": requests_last_hour,
                "remaining": max(0, rate_limit - requests_last_hour)
            }
            
            return requests_last_hour < rate_limit, rate_info
            
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            return False, None
    
    def log_api_request(self, api_key_id: int, endpoint: str, method: str,
                       ip_address: Optional[str] = None, user_agent: Optional[str] = None,
                       request_data: Optional[Dict[str, Any]] = None,
                       response_status: Optional[int] = None,
                       response_time_ms: Optional[int] = None):
        """Log an API request for analytics and rate limiting."""
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                INSERT INTO api_key_logs 
                (api_key_id, endpoint, method, ip_address, user_agent, request_data, response_status, response_time_ms)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (api_key_id, endpoint, method, ip_address, user_agent, 
                  json.dumps(request_data) if request_data else None,
                  response_status, response_time_ms))
            self.db.commit()
        except Exception as e:
            logger.error(f"Error logging API request: {e}")