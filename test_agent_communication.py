#!/usr/bin/env python3
"""
Quick test of agent-to-agent communication
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_KEY = "kpe_fElyteRdsZVlypzp7qPx6yL12MoLPJ07"

def test_agent_communication():
    """Test the agent-to-agent communication pattern"""
    
    print("🧪 Testing Agent-to-Agent Communication")
    print("=" * 50)
    
    # Step 1: Search KPATH for shoe services
    print("\n1️⃣ Searching KPATH for shoe services...")
    search_url = f"{BASE_URL}/api/v1/search"
    search_payload = {
        "query": "shoes",
        "search_mode": "agents_and_tools",
        "include_orchestration": True,
        "response_mode": "compact",
        "limit": 1
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }
    
    response = requests.post(search_url, json=search_payload, headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"   Error: {response.text}")
        return
    
    search_results = response.json()
    if not search_results.get("results"):
        print("   No results found")
        return
    
    # Extract service info
    result = search_results["results"][0]
    service = result.get("service", {})
    integration = service.get("integration_details", {})
    
    print(f"   Found: {service.get('name', 'Unknown')}")
    print(f"   Base Endpoint: {integration.get('base_endpoint', 'Not found')}")
    
    # Step 2: Test direct chat endpoint (if available)
    if integration.get("base_endpoint"):
        chat_endpoint = f"{integration['base_endpoint']}/chat"
        print(f"\n2️⃣ Testing chat endpoint: {chat_endpoint}")
        
        # Simple message
        simple_message = {
            "message": "test connection"
        }
        
        try:
            response = requests.post(chat_endpoint, json=simple_message, headers=headers)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ Chat endpoint is accessible!")
            else:
                print(f"   Response: {response.text[:200]}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Step 3: Test agent-to-agent message
        print("\n3️⃣ Testing agent-to-agent communication...")
        
        agent_message = {
            "message": "I want to buy running shoes",
            "context": {
                "source_agent": "PA_Agent",
                "session_id": f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "timestamp": datetime.now().isoformat(),
                "user_intent": "I want to buy running shoes",
                "kpath_analysis": {
                    "matched_service": service.get("name", "Unknown"),
                    "confidence_score": result.get("score", 0.0),
                    "recommended_tool": "product_search"
                },
                "suggested_action": {
                    "tool": "product_search",
                    "parameters": {
                        "query": "running shoes",
                        "category": "athletic"
                    }
                }
            }
        }
        
        try:
            response = requests.post(chat_endpoint, json=agent_message, headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("   ✅ Agent-to-agent communication successful!")
                print(f"   Response preview: {str(result)[:200]}...")
            else:
                print(f"   Response: {response.text[:200]}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    else:
        print("\n⚠️  No integration details available for testing")
    
    print("\n" + "=" * 50)
    print("Test complete!")


if __name__ == "__main__":
    test_agent_communication()
