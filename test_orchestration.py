#!/usr/bin/env python3
"""
Test script for agent orchestration enhancement.
Tests both regular search and orchestration-enhanced search.
"""

import requests
import json
import sys

def test_orchestration():
    """Test the new orchestration functionality."""
    
    base_url = "http://localhost:8000"
    api_key = "kpe_TestKey123456789012345678901234"
    
    print("🔬 Testing Agent Orchestration Enhancement")
    print("=" * 50)
    
    # Test 1: Regular search (backward compatibility)
    print("\n📋 Test 1: Regular Search (Backward Compatibility)")
    print("-" * 45)
    
    try:
        response = requests.get(
            f"{base_url}/api/v1/search/search",
            params={
                "query": "customer data management",
                "limit": 2,
                "include_orchestration": False
            },
            headers={"X-API-Key": api_key},
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Results found: {data.get('total_results', 0)}")
            if data.get('results'):
                service = data['results'][0]['service']
                print(f"Service: {service.get('name', 'Unknown')}")
                print(f"Has tools field: {'tools' in service}")
                print(f"Has agent_protocol: {'agent_protocol' in service}")
                print("✅ Regular search working")
            else:
                print("❌ No results returned")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    
    except Exception as e:
        print(f"❌ Regular search failed: {e}")
    
    # Test 2: Orchestration-enhanced search
    print("\n🤖 Test 2: Orchestration-Enhanced Search")
    print("-" * 40)
    
    try:
        response = requests.get(
            f"{base_url}/api/v1/search/search",
            params={
                "query": "customer data management", 
                "limit": 2,
                "include_orchestration": True
            },
            headers={"X-API-Key": api_key},
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Results found: {data.get('total_results', 0)}")
            
            if data.get('results'):
                service = data['results'][0]['service']
                print(f"Service: {service.get('name', 'Unknown')}")
                print(f"Agent Protocol: {service.get('agent_protocol', 'None')}")
                print(f"Auth Type: {service.get('auth_type', 'None')}")
                
                tools = service.get('tools', [])
                print(f"Tools available: {len(tools)}")
                
                if tools:
                    print(f"First tool: {tools[0].get('tool_name', 'Unknown')}")
                    print(f"Tool description: {tools[0].get('description', 'No description')}")
                    print(f"Has input schema: {'input_schema' in tools[0]}")
                    print(f"Has output schema: {'output_schema' in tools[0]}")
                    print(f"Has examples: {'example_calls' in tools[0]}")
                
                orchestration_summary = service.get('orchestration_summary', {})
                print(f"Orchestration summary: {orchestration_summary}")
                
                print("✅ Orchestration search working!")
            else:
                print("❌ No results returned")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    
    except Exception as e:
        print(f"❌ Orchestration search failed: {e}")
    
    # Test 3: POST method with orchestration
    print("\n📨 Test 3: POST Method with Orchestration")
    print("-" * 35)
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/search/search",
            json={
                "query": "payment processing",
                "limit": 1,
                "include_orchestration": True
            },
            headers={
                "X-API-Key": api_key,
                "Content-Type": "application/json"
            },
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Results found: {data.get('total_results', 0)}")
            
            if data.get('results'):
                service = data['results'][0]['service']
                tools = service.get('tools', [])
                print(f"Service: {service.get('name', 'Unknown')}")
                print(f"Tools: {len(tools)}")
                if tools:
                    for i, tool in enumerate(tools[:2]):  # Show first 2 tools
                        print(f"  Tool {i+1}: {tool.get('tool_name', 'Unknown')}")
                print("✅ POST orchestration working!")
            else:
                print("❌ No results returned")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    
    except Exception as e:
        print(f"❌ POST orchestration search failed: {e}")
    
    print("\n🎯 Testing Complete!")
    print("=" * 50)

if __name__ == "__main__":
    test_orchestration()
