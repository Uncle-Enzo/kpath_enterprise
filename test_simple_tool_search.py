#!/usr/bin/env python3
"""Simple test for tool search functionality."""

import sys
sys.path.append('/Users/james/claude_development/kpath_enterprise')

from backend.core.database import SessionLocal
from backend.services.search_manager import get_search_manager, initialize_search
from backend.services.search.search_service import SearchQuery

def test_simple():
    db = SessionLocal()
    try:
        # Initialize search manager
        print("Initializing search manager...")
        initialize_search(db, force_rebuild=True)
        
        search_manager = get_search_manager()
        print(f"Tool index built: {search_manager.tool_index_built}")
        print(f"Tool count: {len(search_manager.tool_ids) if hasattr(search_manager, 'tool_ids') else 0}")
        
        # Simple test
        query = SearchQuery(
            text="send email",
            user_id=1,
            limit=2,
            min_score=0.0,
            search_mode="tools_only"
        )
        
        print("\nSearching for 'send email' tools...")
        try:
            results = search_manager.search(query, db)
            print(f"Found {len(results)} results")
            
            for idx, result in enumerate(results):
                print(f"\nResult {idx + 1}:")
                print(f"  Service: {result.service_data['name']}")
                print(f"  Score: {result.score:.3f}")
                
                if hasattr(result, 'recommended_tool') and result.recommended_tool:
                    tool = result.recommended_tool
                    print(f"  Tool: {tool['tool_name']}")
                    print(f"  Description: {tool['tool_description']}")
                        
        except Exception as e:
            print(f"Search failed: {e}")
            import traceback
            traceback.print_exc()
            
    finally:
        db.close()

if __name__ == "__main__":
    test_simple()
