#!/usr/bin/env python3
"""
Test script for token optimization features in KPATH Enterprise search.

Tests the new response_mode parameters and measures token reduction.
"""

import json
import requests
import time
from typing import Dict, Any

# Install tiktoken if not available
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
    encoder = tiktoken.get_encoding("cl100k_base")
except ImportError:
    TIKTOKEN_AVAILABLE = False
    print("Warning: tiktoken not available, using character estimation")


def count_tokens(text: str) -> int:
    """Count tokens in text"""
    if TIKTOKEN_AVAILABLE:
        return len(encoder.encode(str(text)))
    else:
        return len(str(text)) // 4


def make_search_request(query: str, **kwargs) -> Dict[str, Any]:
    """Make a search request and return response with timing"""
    import urllib.parse
    
    # Use GET request with query parameters (default search mode, limit=3)
    query_params = {
        "query": query,
        "limit": 3,
        "api_key": "kpe_fElyteRdsZVlypzp7qPx6yL12MoLPJ07",
        **kwargs
    }
    query_string = urllib.parse.urlencode(query_params)
    url = f"http://localhost:8000/api/v1/search?{query_string}"
    
    start_time = time.time()
    try:
        response = requests.get(url, timeout=30)
        response_time = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            data = response.json()
            token_count = count_tokens(json.dumps(data))
            return {
                "success": True,
                "data": data,
                "tokens": token_count,
                "response_time_ms": response_time,
                "status_code": response.status_code
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}: {response.text}",
                "tokens": 0,
                "response_time_ms": response_time,
                "status_code": response.status_code
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "tokens": 0,
            "response_time_ms": (time.time() - start_time) * 1000,
            "status_code": 0
        }


def test_response_modes():
    """Test different response modes and compare token usage"""
    query = "I want to buy running shoes"
    
    print("🧪 Testing Token Optimization Features")
    print("=" * 60)
    print(f"Query: '{query}'")
    print(f"Token Counter: {'tiktoken (accurate)' if TIKTOKEN_AVAILABLE else 'character estimation'}")
    print()
    
    # Test different response modes
    modes = [
        ("full", {}),
        ("compact", {}),
        ("minimal", {}),
        ("full", {"include_schemas": False}),
        ("full", {"include_examples": False}),
        ("full", {"include_schemas": False, "include_examples": False}),
        ("compact", {"field_filter": ["tool_name", "tool_description", "service_name"]})
    ]
    
    results = []
    
    for mode, kwargs in modes:
        print(f"Testing response_mode='{mode}' {kwargs}...")
        result = make_search_request(query, response_mode=mode, **kwargs)
        
        if result["success"]:
            results.append({
                "mode": f"{mode} {kwargs}",
                "tokens": result["tokens"],
                "response_time": result["response_time_ms"],
                "result_count": len(result["data"].get("results", []))
            })
            print(f"  ✅ Success: {result['tokens']} tokens, {result['response_time_ms']:.0f}ms")
        else:
            print(f"  ❌ Failed: {result['error']}")
        
        time.sleep(0.5)  # Small delay between requests
    
    print("\n" + "=" * 60)
    print("TOKEN OPTIMIZATION RESULTS")
    print("=" * 60)
    
    if results:
        baseline = results[0]["tokens"] if results else 0
        
        print(f"{'Mode':<40} {'Tokens':<10} {'Savings':<12} {'Time':<8}")
        print("-" * 70)
        
        for result in results:
            tokens = result["tokens"]
            savings = ((baseline - tokens) / baseline * 100) if baseline > 0 else 0
            time_ms = result["response_time"]
            
            print(f"{result['mode'][:39]:<40} {tokens:<10} {savings:+6.1f}%    {time_ms:6.0f}ms")
        
        print("-" * 70)
        
        if len(results) > 1:
            best_savings = max(results[1:], key=lambda x: baseline - x["tokens"])
            total_savings = baseline - best_savings["tokens"]
            percent_savings = (total_savings / baseline * 100) if baseline > 0 else 0
            
            print(f"\n🏆 Best Optimization: {best_savings['mode']}")
            print(f"💰 Token Savings: {total_savings} tokens ({percent_savings:.1f}% reduction)")
            print(f"⏱️  Performance: {best_savings['response_time']:.0f}ms")
    else:
        print("❌ No successful results to compare")


def test_detail_endpoints():
    """Test the new tool detail endpoints"""
    print("\n" + "=" * 60)
    print("TESTING TOOL DETAIL ENDPOINTS")
    print("=" * 60)
    
    # First get a tool ID from search
    search_result = make_search_request("shoes", response_mode="minimal")
    
    if not search_result["success"]:
        print("❌ Could not get tool ID from search")
        return
    
    results = search_result["data"].get("results", [])
    if not results:
        print("❌ No search results found")
        return
    
    # Get tool ID from first result
    first_result = results[0]
    recommended_tool = first_result.get("recommended_tool", {})
    tool_id = recommended_tool.get("tool_id")
    
    if not tool_id:
        print("❌ No tool ID found in search result")
        return
    
    print(f"Testing with tool_id: {tool_id}")
    
    # Test detail endpoints
    endpoints = [
        f"/api/v1/search/tools/{tool_id}/summary",
        f"/api/v1/search/tools/{tool_id}/schema", 
        f"/api/v1/search/tools/{tool_id}/examples",
        f"/api/v1/search/tools/{tool_id}/details"
    ]
    
    for endpoint in endpoints:
        url = f"http://localhost:8000{endpoint}"
        headers = {"X-API-Key": "kpe_fElyteRdsZVlypzp7qPx6yL12MoLPJ07"}
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                tokens = count_tokens(json.dumps(data))
                print(f"✅ {endpoint.split('/')[-1]:8}: {tokens:4d} tokens")
            else:
                print(f"❌ {endpoint.split('/')[-1]:8}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint.split('/')[-1]:8}: {str(e)}")


if __name__ == "__main__":
    print("🚀 KPATH Enterprise Token Optimization Test")
    print("=" * 60)
    
    # Check if API is accessible
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ KPATH API is accessible\n")
        else:
            print("❌ KPATH API health check failed")
            exit(1)
    except Exception as e:
        print(f"❌ Cannot connect to KPATH API: {e}")
        exit(1)
    
    # Run tests
    test_response_modes()
    test_detail_endpoints()
    
    print("\n" + "=" * 60)
    print("✅ Token optimization testing completed!")
    print("=" * 60)
