#!/usr/bin/env python3
"""
Simplified Token Consumption Test for KPATH Enterprise

This version uses API key authentication directly in query parameters
to avoid JWT authentication issues.
"""

import json
import requests
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_KEY = "kpe_fElyteRdsZVlypzp7qPx6yL12MoLPJ07"

# Test scenarios
TEST_SCENARIOS = [
    ("Payment Processing", "I need to process a payment for $150"),
    ("Customer Notification", "Send notification to customer about shipment"),
    ("Shipping Insurance", "Calculate shipping insurance for items worth $5000"),
    ("Customer Data", "Get customer profile information"),
    ("Invoice Generation", "Generate invoice for recent order"),
]

def count_tokens_simple(text):
    """Simple token estimation (4 chars = 1 token)"""
    return len(str(text)) // 4

def test_approach_1(query):
    """Test Approach 1: Basic search (agents_only)"""
    url = f"{BASE_URL}/api/v1/search"
    params = {
        "query": query,
        "search_mode": "agents_only",
        "limit": 5,
        "api_key": API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            # Count tokens in response
            response_tokens = count_tokens_simple(json.dumps(data))
            
            # Simulate reasoning for service selection
            reasoning = f"""
Query: {query}

Available services:
"""
            if "results" in data:
                for i, result in enumerate(data["results"][:3]):
                    service = result.get("service", {})
                    reasoning += f"\n{i+1}. {service.get('name')} - {service.get('description')}"
            
            reasoning += "\n\nNeed additional API call to get tools from selected service..."
            reasoning += "\nEstimated additional tokens for tool query: 200"
            
            reasoning_tokens = count_tokens_simple(reasoning)
            additional_api_tokens = 200  # Simulated second API call
            
            total_tokens = response_tokens + reasoning_tokens + additional_api_tokens
            
            return {
                "success": True,
                "total_tokens": total_tokens,
                "api_tokens": response_tokens + additional_api_tokens,
                "reasoning_tokens": reasoning_tokens,
                "response_time": response.elapsed.total_seconds() * 1000
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}",
                "total_tokens": 0
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "total_tokens": 0
        }

def test_approach_2(query):
    """Test Approach 2: Direct tool search (tools_only)"""
    url = f"{BASE_URL}/api/v1/search"
    params = {
        "query": query,
        "search_mode": "tools_only",
        "limit": 5,
        "api_key": API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            # Count tokens in response
            response_tokens = count_tokens_simple(json.dumps(data))
            
            # Simulate reasoning for tool selection
            reasoning = f"""
Query: {query}

Available tools with recommendations:
"""
            if "results" in data:
                for i, result in enumerate(data["results"][:3]):
                    tool = result.get("recommended_tool", {})
                    if tool:
                        reasoning += f"\n{i+1}. {tool.get('name')} - {tool.get('description')}"
            
            reasoning += "\n\nDirect tool selection - no additional API calls needed."
            
            reasoning_tokens = count_tokens_simple(reasoning)
            
            total_tokens = response_tokens + reasoning_tokens
            
            return {
                "success": True,
                "total_tokens": total_tokens,
                "api_tokens": response_tokens,
                "reasoning_tokens": reasoning_tokens,
                "response_time": response.elapsed.total_seconds() * 1000
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}",
                "total_tokens": 0
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "total_tokens": 0
        }

def main():
    print("="*80)
    print("KPATH ENTERPRISE TOKEN CONSUMPTION TEST - SIMPLIFIED")
    print("="*80)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API: {BASE_URL}")
    print()
    
    results = []
    
    for scenario_name, query in TEST_SCENARIOS:
        print(f"\nTesting: {scenario_name}")
        print(f"Query: '{query}'")
        print("-"*60)
        
        # Test Approach 1
        print("Approach 1 (agents_only + manual selection)...")
        app1_result = test_approach_1(query)
        
        # Test Approach 2
        print("Approach 2 (tools_only direct search)...")
        app2_result = test_approach_2(query)
        
        # Calculate savings
        if app1_result["success"] and app2_result["success"]:
            savings = app1_result["total_tokens"] - app2_result["total_tokens"]
            savings_pct = (savings / app1_result["total_tokens"] * 100) if app1_result["total_tokens"] > 0 else 0
            
            print(f"\nResults:")
            print(f"  Approach 1: {app1_result['total_tokens']} tokens ({app1_result['api_tokens']} API + {app1_result['reasoning_tokens']} reasoning)")
            print(f"  Approach 2: {app2_result['total_tokens']} tokens ({app2_result['api_tokens']} API + {app2_result['reasoning_tokens']} reasoning)")
            print(f"  Savings: {savings} tokens ({savings_pct:.1f}%)")
            
            results.append({
                "scenario": scenario_name,
                "app1_tokens": app1_result["total_tokens"],
                "app2_tokens": app2_result["total_tokens"],
                "savings": savings,
                "savings_pct": savings_pct
            })
        else:
            print(f"\nTest failed:")
            if not app1_result["success"]:
                print(f"  Approach 1 error: {app1_result.get('error')}")
            if not app2_result["success"]:
                print(f"  Approach 2 error: {app2_result.get('error')}")
    
    # Summary report
    if results:
        print("\n" + "="*80)
        print("SUMMARY REPORT")
        print("="*80)
        
        total_app1 = sum(r["app1_tokens"] for r in results)
        total_app2 = sum(r["app2_tokens"] for r in results)
        avg_savings_pct = sum(r["savings_pct"] for r in results) / len(results)
        
        print(f"\nScenarios tested: {len(results)}")
        print(f"Total tokens Approach 1: {total_app1}")
        print(f"Total tokens Approach 2: {total_app2}")
        print(f"Total savings: {total_app1 - total_app2} tokens")
        print(f"Average savings: {avg_savings_pct:.1f}%")
        
        print("\nDetailed Results:")
        print(f"{'Scenario':<25} {'App1':<10} {'App2':<10} {'Savings':<15}")
        print("-"*65)
        for r in results:
            print(f"{r['scenario']:<25} {r['app1_tokens']:<10} {r['app2_tokens']:<10} {r['savings']} ({r['savings_pct']:.1f}%)")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()
