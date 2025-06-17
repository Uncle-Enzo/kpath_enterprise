#!/usr/bin/env python3
"""
Test tool search with current configuration.
"""

import sys
import os
sys.path.insert(0, '/Users/james/claude_development/kpath_enterprise')

from backend.core.database import SessionLocal
from backend.services.search_manager import get_search_manager
from backend.services.search.search_service import SearchQuery

def test_tool_search():
    print("Testing tool search functionality...")
    
    db = SessionLocal()
    try:
        # Get search manager
        search_manager = get_search_manager()
        print(f"Search manager initialized: {search_manager.is_initialized}")
        
        # Create a search query for tools
        query = SearchQuery(
            text="payment processing",
            user_id=1,
            limit=5,
            min_score=0.0,
            search_mode="tools_only"
        )
        
        print(f"\nExecuting search: '{query.text}' with mode '{query.search_mode}'")
        
        # Execute search
        results = search_manager.search(query, db)
        
        print(f"✓ Search completed successfully!")
        print(f"  Found {len(results)} results")
        
        # Display results
        for i, result in enumerate(results, 1):
            print(f"\n  Result {i}:")
            print(f"    Service ID: {result.service_id}")
            print(f"    Score: {result.score:.3f}")
            print(f"    Service: {result.service_data.get('name', 'Unknown')}")
            
            # Check for tool recommendation
            if hasattr(result, 'recommended_tool'):
                tool = getattr(result, 'recommended_tool', None)
                if tool:
                    print(f"    ✨ Recommended Tool: {tool.get('tool_name', 'Unknown')}")
                    print(f"       Description: {tool.get('tool_description', 'No description')}")
        
        return True
        
    except Exception as e:
        print(f"✗ Search failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = test_tool_search()
    if success:
        print("\n✅ Tool search test completed successfully!")
    else:
        print("\n❌ Tool search test failed!")
