"""
Search Module with API Key Authentication for KPath Enterprise

This module provides search functionality with API key authentication.
"""

import json
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import logging
from functools import wraps
from api_key_manager import APIKeyManager

logger = logging.getLogger(__name__)


class SearchError(Exception):
    """Base exception for search-related errors."""
    pass


class AuthenticationError(SearchError):
    """Raised when API key authentication fails."""
    pass


class RateLimitError(SearchError):
    """Raised when rate limit is exceeded."""
    pass


def require_api_key(permission: str = "search"):
    """
    Decorator to require API key authentication for a function.
    
    Args:
        permission: Required permission (default: "search")
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, api_key: str, *args, **kwargs):
            # Validate API key
            key_info = self.api_key_manager.validate_api_key(api_key, permission)
            if not key_info:
                raise AuthenticationError("Invalid or expired API key")
            
            # Check rate limit
            within_limit, rate_info = self.api_key_manager.check_rate_limit(api_key)            if not within_limit:
                raise RateLimitError(f"Rate limit exceeded. Limit: {rate_info['rate_limit']}/hour")
            
            # Add key info to kwargs for logging
            kwargs['_api_key_info'] = key_info
            kwargs['_rate_info'] = rate_info
            
            return func(self, api_key, *args, **kwargs)
        return wrapper
    return decorator


class SearchEngine:
    """Main search engine with API key authentication."""
    
    def __init__(self, db_connection):
        """
        Initialize the search engine.
        
        Args:
            db_connection: PostgreSQL connection object
        """
        self.db = db_connection
        self.api_key_manager = APIKeyManager(db_connection)
    
    @require_api_key("search")
    def search(self, api_key: str, query: str, 
               filters: Optional[Dict[str, Any]] = None,
               limit: int = 10,
               offset: int = 0,
               **kwargs) -> Dict[str, Any]:
        """
        Execute a search query with API key authentication.
        
        Args:
            api_key: API key for authentication
            query: Search query string
            filters: Optional filters to apply
            limit: Maximum number of results (default: 10, max: 100)
            offset: Result offset for pagination (default: 0)
            
        Returns:
            Dict containing search results and metadata
        """
        start_time = time.time()
        
        # Get API key info from decorator
        api_key_info = kwargs.get('_api_key_info', {})
        rate_info = kwargs.get('_rate_info', {})        
        # Validate and sanitize parameters
        limit = min(max(1, limit), 100)  # Enforce max limit of 100
        offset = max(0, offset)
        
        try:
            # TODO: Implement actual search logic here
            # This is a placeholder implementation
            cursor = self.db.cursor()
            
            # Example search query (replace with actual search implementation)
            search_sql = """
                SELECT id, title, content, created_at
                FROM documents
                WHERE to_tsvector('english', title || ' ' || content) @@ plainto_tsquery('english', %s)
                ORDER BY ts_rank(to_tsvector('english', title || ' ' || content), plainto_tsquery('english', %s)) DESC
                LIMIT %s OFFSET %s
            """
            
            # Execute search
            cursor.execute(search_sql, (query, query, limit, offset))
            results = cursor.fetchall()
            
            # Format results
            formatted_results = []
            for row in results:
                formatted_results.append({
                    "id": row[0],
                    "title": row[1],
                    "content": row[2][:200] + "..." if len(row[2]) > 200 else row[2],
                    "created_at": row[3].isoformat() if row[3] else None
                })
            
            # Get total count
            cursor.execute("""
                SELECT COUNT(*)
                FROM documents
                WHERE to_tsvector('english', title || ' ' || content) @@ plainto_tsquery('english', %s)
            """, (query,))
            total_count = cursor.fetchone()[0]
            
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # Log the request
            self.api_key_manager.log_api_request(
                api_key_id=api_key_info['key_id'],
                endpoint="/search",
                method="GET",                request_data={"query": query, "filters": filters, "limit": limit, "offset": offset},
                response_status=200,
                response_time_ms=response_time_ms
            )
            
            return {
                "success": True,
                "query": query,
                "results": formatted_results,
                "pagination": {
                    "limit": limit,
                    "offset": offset,
                    "total": total_count,
                    "has_more": (offset + limit) < total_count
                },
                "meta": {
                    "response_time_ms": response_time_ms,
                    "rate_limit": {
                        "limit": rate_info.get('rate_limit'),
                        "remaining": rate_info.get('remaining'),
                        "requests_last_hour": rate_info.get('requests_last_hour')
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            
            # Log failed request
            self.api_key_manager.log_api_request(
                api_key_id=api_key_info['key_id'],
                endpoint="/search",
                method="GET",
                request_data={"query": query, "filters": filters},
                response_status=500,
                response_time_ms=int((time.time() - start_time) * 1000)
            )
            
            raise SearchError(f"Search failed: {str(e)}")
    
    @require_api_key("search")
    def advanced_search(self, api_key: str, **search_params) -> Dict[str, Any]:
        """
        Execute an advanced search with multiple parameters.
        
        This method supports POST requests with complex search criteria.
        """
        # TODO: Implement advanced search logic
        return self.search(api_key, search_params.get('query', ''), **search_params)