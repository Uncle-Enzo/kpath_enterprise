#!/usr/bin/env python3
"""Test tool search functionality via API."""

import requests
import json
import sys

# API configuration
BASE_URL = "http://localhost:8000"
API_KEY = "kpe_test_key_123"  # Update with actual API key

def test_tool_search():
    """Test the tool search API."""
    
    # Test queries
    queries = [
        ("send notifications", "tools_only"),
        ("email", "tools_only"),
        ("payment", "tools_only"),
        ("customer data", "tools_only"),
        ("customer profile", "agents_and_tools"),
    ]
    
    for query_text, search_mode in queries:
        print(f"\n{'='*60}")
        print(f"Testing: '{query_text}' with mode: {search_mode}")
        print(f"{'='*60}")
        
        # Make the search request
        url = f"{BASE_URL}/api/v1/search/search"
        headers = {
            "X-API-Key": API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "query": query_text,
            "search_mode": search_mode,
            "limit": 5,
            "include_orchestration": True
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Search successful - {data['total_results']} results found")
                print(f"  Search time: {data['search_time_ms']}ms")
                print(f"  Search mode: {data['search_mode']}")
                
                # Display results
                for idx, result in enumerate(data['results']):
                    print(f"\n  Result {idx + 1}:")
                    print(f"    Service: {result['service']['name']}")
                    print(f"    Score: {result['score']:.3f}")
                    print(f"    Entity Type: {result.get('entity_type', 'service')}")
                    
                    # Show recommended tool if available
                    if result.get('recommended_tool'):
                        tool = result['recommended_tool']
                        print(f"    ✨ Recommended Tool: {tool['tool_name']}")
                        print(f"       Description: {tool['tool_description']}")
                        print(f"       Recommendation: {tool['recommendation_reason']}")
                        
                        # Show input schema
                        if tool.get('input_schema'):
                            props = tool['input_schema'].get('properties', {})
                            if props:
                                print(f"       Inputs: {', '.join(props.keys())}")
                    
                    # Show connectivity info if service has it
                    service = result['service']
                    if service.get('integration_details'):
                        details = service['integration_details']
                        print(f"    Connectivity:")
                        print(f"       Protocol: {details.get('access_protocol')}")
                        print(f"       Endpoint: {details.get('base_endpoint')}")
                        print(f"       Auth: {details.get('auth_method')}")
                        
            else:
                print(f"✗ Search failed with status {response.status_code}")
                print(f"  Error: {response.text}")
                
        except Exception as e:
            print(f"✗ Request failed: {e}")

def check_tool_index_status():
    """Check the status of the tool index."""
    print("\nChecking tool index status...")
    
    url = f"{BASE_URL}/api/v1/search/search/debug/tool-index"
    headers = {"X-API-Key": API_KEY}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Tool index status:")
            print(f"  Search manager initialized: {data['search_manager_initialized']}")
            print(f"  Service index built: {data['service_index_built']}")
            print(f"  Tool index built: {data['tool_index_built']}")
            print(f"  Tool count: {data['tool_count']}")
            if data.get('tool_embeddings_shape'):
                print(f"  Tool embeddings shape: {data['tool_embeddings_shape']}")
        else:
            print(f"✗ Status check failed: {response.status_code}")
            
    except Exception as e:
        print(f"✗ Status check failed: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--status":
        check_tool_index_status()
    else:
        check_tool_index_status()
        test_tool_search()
