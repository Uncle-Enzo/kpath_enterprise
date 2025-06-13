#!/usr/bin/env python3
"""
Example usage of the KPath Enterprise Search API with API key authentication.

This script demonstrates how to:
- Create API keys
- Use API keys for search requests
- Handle authentication errors
- Check rate limits
"""

import psycopg2
import json
from api_key_manager import APIKeyManager
from search import SearchEngine, AuthenticationError, RateLimitError


def main():
    # Connect to database
    connection = psycopg2.connect(
        dbname="kpath_enterprise",
        host="localhost",
        port=5432
    )
    
    # Initialize managers
    api_key_manager = APIKeyManager(connection)
    search_engine = SearchEngine(connection)
    
    # Example 1: Create a new API key
    print("Creating new API key...")
    api_key, key_info = api_key_manager.create_api_key(
        user_id=1,  # Assuming user ID 1 exists
        name="Demo API Key",
        permissions={"search": True},
        expires_in_days=30,
        rate_limit=100
    )
    
    print(f"Generated API Key: {api_key}")
    print(f"Key Info: {json.dumps(key_info, indent=2)}")
    
    # Example 2: Perform a search
    print("\nPerforming search...")
    try:
        results = search_engine.search(
            api_key=api_key,
            query="Python programming",
            limit=5
        )        
        print(f"Search Results: {json.dumps(results, indent=2)}")
    except AuthenticationError as e:
        print(f"Authentication failed: {e}")
    except RateLimitError as e:
        print(f"Rate limit exceeded: {e}")
    
    # Example 3: Check rate limit status
    print("\nChecking rate limit...")
    within_limit, rate_info = api_key_manager.check_rate_limit(api_key)
    print(f"Within rate limit: {within_limit}")
    print(f"Rate info: {json.dumps(rate_info, indent=2)}")
    
    # Example 4: Advanced search (POST)
    print("\nPerforming advanced search...")
    try:
        advanced_results = search_engine.advanced_search(
            api_key=api_key,
            query="database",
            filters={"category": "technology"},
            limit=10,
            offset=0
        )
        print(f"Advanced Search Results: {json.dumps(advanced_results, indent=2)}")
    except Exception as e:
        print(f"Advanced search error: {e}")
    
    connection.close()


if __name__ == "__main__":
    main()