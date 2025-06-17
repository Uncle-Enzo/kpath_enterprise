#!/usr/bin/env python3
"""
Debug script to identify search service issues.
"""

import traceback
import sys
import os

# Add the project root to the path
sys.path.insert(0, '/Users/james/claude_development/kpath_enterprise')

try:
    print("1. Testing database connection...")
    from backend.core.database import SessionLocal
    db = SessionLocal()
    print("✓ Database connection successful")
    db.close()
    
    print("\n2. Testing search manager import...")
    from backend.services.search_manager import get_search_manager
    print("✓ Search manager import successful")
    
    print("\n3. Testing search manager initialization...")
    search_manager = get_search_manager()
    print(f"✓ Search manager created: {type(search_manager)}")
    print(f"  - Initialized: {search_manager.is_initialized}")
    print(f"  - Index built: {search_manager.index_built}")
    
    print("\n4. Testing embedding service...")
    print(f"  - Embedding service: {type(search_manager.embedding_service)}")
    
    print("\n5. Testing search service...")
    print(f"  - Search service: {type(search_manager.search_service)}")
    print(f"  - Search service initialized: {search_manager.search_service.is_initialized}")
    
    print("\n6. Testing search manager initialization with DB...")
    db = SessionLocal()
    try:
        search_manager.initialize(db, force_rebuild=False)
        print("✓ Search manager initialization successful")
        print(f"  - Initialized: {search_manager.is_initialized}")
        print(f"  - Index built: {search_manager.index_built}")
        print(f"  - Tool index built: {search_manager.tool_index_built}")
    except Exception as e:
        print(f"✗ Search manager initialization failed: {e}")
        traceback.print_exc()
    finally:
        db.close()

except Exception as e:
    print(f"✗ Error: {e}")
    traceback.print_exc()
