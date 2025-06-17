#!/usr/bin/env python3
"""
Debug script for agent orchestration implementation.
Tests Tool model and database queries.
"""

import sys
import os
import traceback

# Add backend to path
sys.path.append('/Users/james/claude_development/kpath_enterprise/backend')

def test_tool_model():
    """Test if Tool model can be imported and queried."""
    print("🔬 Testing Tool Model Import and Database Query")
    print("=" * 55)
    
    try:
        # Test imports
        print("1. Testing imports...")
        from backend.core.database import SessionLocal
        from backend.models.models import Tool, Service
        print("✅ Successfully imported Tool and Service models")
        
        # Test database connection
        print("2. Testing database connection...")
        db = SessionLocal()
        print("✅ Database connection established")
        
        # Test basic Tool query
        print("3. Testing Tool model query...")
        tools_count = db.query(Tool).count()
        print(f"✅ Found {tools_count} tools in database")
        
        # Test Tool query with service filter
        print("4. Testing Tool query with service filter...")
        service_ids = [4, 5, 6, 7]  # Known service IDs with tools
        tools_with_services = db.query(Tool).filter(Tool.service_id.in_(service_ids)).all()
        print(f"✅ Found {len(tools_with_services)} tools for services {service_ids}")
        
        # Test individual tool data structure
        if tools_with_services:
            print("5. Testing tool data structure...")
            tool = tools_with_services[0]
            print(f"Tool name: {tool.tool_name}")
            print(f"Service ID: {tool.service_id}")
            print(f"Description: {tool.tool_description}")
            print(f"Has input schema: {tool.input_schema is not None}")
            print(f"Has output schema: {tool.output_schema is not None}")
            print(f"Has examples: {tool.example_calls is not None}")
            print("✅ Tool data structure looks good")
        
        # Test tool data formatting (similar to search implementation)
        print("6. Testing tool data formatting...")
        tools_by_service = {}
        for tool in tools_with_services:
            if tool.service_id not in tools_by_service:
                tools_by_service[tool.service_id] = []
            
            tool_data = {
                'tool_name': tool.tool_name,
                'description': tool.tool_description,
                'input_schema': tool.input_schema,
                'output_schema': tool.output_schema,
                'example_calls': tool.example_calls,
                'validation_rules': tool.validation_rules,
                'error_handling': tool.error_handling,
                'performance_notes': tool.performance_notes,
                'version': tool.version,
                'last_updated': tool.last_updated.isoformat() if tool.last_updated else None
            }
            tools_by_service[tool.service_id].append(tool_data)
        
        print(f"✅ Successfully formatted tools for {len(tools_by_service)} services")
        for service_id, tools in tools_by_service.items():
            print(f"   Service {service_id}: {len(tools)} tools")
        
        # Test service query
        print("7. Testing Service model query...")
        services = db.query(Service).filter(Service.id.in_(service_ids), Service.status == 'active').all()
        print(f"✅ Found {len(services)} active services")
        
        db.close()
        print("\n🎉 All tests passed! Tool model and queries working correctly.")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(f"Traceback:\n{traceback.format_exc()}")
        return False

def test_search_query_with_orchestration():
    """Test the search query with orchestration flag."""
    print("\n🔍 Testing Search Query with Orchestration")
    print("=" * 45)
    
    try:
        from backend.services.search.search_service import SearchQuery
        
        # Create a search query with orchestration
        query = SearchQuery(
            text="customer data management",
            user_id=1,
            limit=1,
            min_score=0.0,
            include_orchestration=True
        )
        
        print(f"✅ SearchQuery created successfully")
        print(f"   Query: {query.text}")
        print(f"   Include orchestration: {query.include_orchestration}")
        
        return True
        
    except Exception as e:
        print(f"❌ SearchQuery creation failed: {e}")
        print(f"Traceback:\n{traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Agent Orchestration Debug Session")
    print("=" * 50)
    
    success1 = test_tool_model()
    success2 = test_search_query_with_orchestration()
    
    if success1 and success2:
        print("\n✅ DEBUG RESULT: All tests passed - issue is likely in search service logic")
    else:
        print("\n❌ DEBUG RESULT: Found issues in basic functionality")
    
    print("\n" + "=" * 50)
