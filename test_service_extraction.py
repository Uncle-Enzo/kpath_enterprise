#!/usr/bin/env python3
"""
Test the fixed service name extraction
"""

import requests
import json

# Test traditional approach
print("Testing traditional approach...")
response = requests.post(
    "http://localhost:8000/api/v1/search",
    json={
        "query": "I want to buy some shoes",
        "search_mode": "agents_only",
        "limit": 5
    },
    headers={
        "X-API-Key": "kpe_fElyteRdsZVlypzp7qPx6yL12MoLPJ07"
    }
)

if response.status_code == 200:
    data = response.json()
    if data.get("results"):
        result = data["results"][0]
        service = result.get("service", {})
        service_name = service.get("name", "Unknown")
        print(f"✅ Service found: {service_name}")
        
        # This is what the test will try to call
        if service_name == "ShoesAgent":
            url = "http://localhost:8000/api/v1/agents/shoes/chat"
        else:
            url = f"http://localhost:8000/api/v1/services/{service_name.lower()}/execute"
        print(f"   Would call: {url}")
        
        # Test if it exists
        test_response = requests.get(url.replace("/chat", "/status").replace("/execute", ""))
        print(f"   Endpoint test: {test_response.status_code}")

# Test tools approach  
print("\nTesting tools approach...")
response = requests.post(
    "http://localhost:8000/api/v1/search",
    json={
        "query": "I want to buy some shoes",
        "search_mode": "tools_only",
        "response_mode": "compact",
        "limit": 5
    },
    headers={
        "X-API-Key": "kpe_fElyteRdsZVlypzp7qPx6yL12MoLPJ07"
    }
)

if response.status_code == 200:
    data = response.json()
    if data.get("results"):
        result = data["results"][0]
        tool = result.get("recommended_tool", {})
        tool_name = tool.get("tool_name", "unknown")
        service_name = tool.get("service_name", "Unknown")
        print(f"✅ Tool found: {service_name}.{tool_name}")
        
        # This is what the test will try to call
        if service_name == "ShoesAgent":
            tool_endpoints = {
                'product_search': '/api/v1/agents/shoes/search',
                'shoe_buying_guide': '/api/v1/agents/shoes/guide'
            }
            url = f"http://localhost:8000{tool_endpoints.get(tool_name, '/api/v1/agents/shoes/search')}"
        else:
            url = f"http://localhost:8000/api/v1/tools/{tool_name}/execute"
        print(f"   Would call: {url}")
