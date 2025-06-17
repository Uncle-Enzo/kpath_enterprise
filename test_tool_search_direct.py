#!/usr/bin/env python3
"""Test tool search functionality directly."""

import sys
sys.path.append('/Users/james/claude_development/kpath_enterprise')

from backend.core.database import SessionLocal
from backend.services.search_manager import get_search_manager, initialize_search
from backend.services.search.search_service import SearchQuery

def test_tool_search_direct():
    """Test tool search without going through API."""
    db = SessionLocal()
    try:
        # Initialize search manager if needed
        print("Initializing search manager...")
        initialize_search(db, force_rebuild=True)
        
        search_manager = get_search_manager()
        print(f"\nSearch manager state:")
        print(f"  Initialized: {search_manager.is_initialized}")
        print(f"  Index built: {search_manager.index_built}")
        print(f"  Tool index built: {search_manager.tool_index_built}")
        print(f"  Tool count: {len(search_manager.tool_ids) if hasattr(search_manager, 'tool_ids') else 0}")
        
        # Test queries
        test_queries = [
            ("send notifications", "tools_only"),
            ("email service", "tools_only"),
            ("payment processing", "tools_only"),
            ("customer profile", "agents_and_tools"),
        ]
        
        for query_text, mode in test_queries:
            print(f"\n{'='*60}")
            print(f"Testing: '{query_text}' (mode: {mode})")
            print(f"{'='*60}")
            
            query = SearchQuery(
                text=query_text,
                user_id=1,
                limit=5,
                min_score=0.0,
                search_mode=mode
            )
            
            try:
                results = search_manager.search(query, db)
                print(f"✓ Found {len(results)} results")
                
                for idx, result in enumerate(results):
                    print(f"\nResult {idx + 1}:")
                    print(f"  Service: {result.service_data['name']}")
                    print(f"  Score: {result.score:.3f}")
                    print(f"  Entity Type: {getattr(result, 'entity_type', 'service')}")
                    
                    # Show recommended tool if available
                    if hasattr(result, 'recommended_tool') and result.recommended_tool:
                        tool = result.recommended_tool
                        print(f"  ✨ Recommended Tool: {tool['tool_name']}")
                        print(f"     Description: {tool['tool_description']}")
                        print(f"     Reason: {tool['recommendation_reason']}")
                        
                        # Show input schema
                        if tool.get('input_schema'):
                            props = tool['input_schema'].get('properties', {})
                            if props:
                                print(f"     Inputs: {', '.join(props.keys())}")
                    
                    # Show connectivity info
                    service = result.service_data
                    if service.get('integration_details'):
                        details = service['integration_details']
                        if details:
                            print(f"  Connectivity:")
                            print(f"     Protocol: {details.get('access_protocol')}")
                            print(f"     Endpoint: {details.get('base_endpoint')}")
                            print(f"     Auth: {details.get('auth_method')}")
                        
            except Exception as e:
                print(f"✗ Search failed: {e}")
                import traceback
                traceback.print_exc()
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_tool_search_direct()
