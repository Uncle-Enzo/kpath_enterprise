#!/usr/bin/env python3
import sys
sys.path.append('/Users/james/claude_development/kpath_enterprise')

from backend.core.database import SessionLocal
from backend.services.search_manager import get_search_manager

def test_tool_search():
    db = SessionLocal()
    try:
        search_manager = get_search_manager()
        print(f"Search manager initialized: {search_manager.is_initialized}")
        print(f"Index built: {search_manager.index_built}")
        print(f"Tool index built: {search_manager.tool_index_built}")
        print(f"Number of tool IDs: {len(search_manager.tool_ids) if search_manager.tool_ids else 0}")
        
        # Try building tool index
        if not search_manager.tool_index_built:
            print("\nBuilding tool index...")
            search_manager._build_tool_index(db)
            print(f"Tool index built: {search_manager.tool_index_built}")
            print(f"Number of tool IDs: {len(search_manager.tool_ids) if search_manager.tool_ids else 0}")
        
        # Check for tools in database
        from backend.models.models import Tool
        tools = db.query(Tool).all()
        print(f"\nTotal tools in database: {len(tools)}")
        for tool in tools[:3]:  # Show first 3
            print(f"  - {tool.tool_name}: {tool.tool_description}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_tool_search()
