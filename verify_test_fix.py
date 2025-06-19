#!/usr/bin/env python3
"""
Quick test to verify token test fixes
"""

import requests
import json

# Test KPATH search first
print("Testing KPATH search structure...")
response = requests.post(
    "http://localhost:8000/api/v1/search",
    json={
        "query": "shoes",
        "search_mode": "agents_only",
        "limit": 1
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
        print(f"✅ Service name found: {service.get('name', 'NOT FOUND')}")
        print(f"   Service ID: {service.get('id', 'NOT FOUND')}")
        print(f"   Structure verified!")
    else:
        print("❌ No results found")
else:
    print(f"❌ Search failed: {response.status_code}")

# Test tools search
print("\nTesting tools search structure...")
response = requests.post(
    "http://localhost:8000/api/v1/search",
    json={
        "query": "shoes",
        "search_mode": "tools_only",
        "limit": 1
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
        print(f"✅ Tool name found: {tool.get('tool_name', 'NOT FOUND')}")
        print(f"   Service name: {tool.get('service_name', 'NOT FOUND')}")
        print(f"   Structure verified!")
    else:
        print("❌ No results found")
else:
    print(f"❌ Search failed: {response.status_code}")
