#!/usr/bin/env python3
"""
Test script for the Shoes Agent
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the agents directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agents'))

from agents.shoes.shoes_agent import ShoesAgent

async def test_shoes_agent():
    """Test the Shoes Agent functionality"""
    print("Testing Shoes Agent...")
    print(f"OpenAI API Key available: {'Yes' if os.getenv('OPENAI_API_KEY') else 'No'}")
    
    # Initialize the agent
    agent = ShoesAgent()
    
    # Test 1: Product Search
    print("\n1. Testing Product Search:")
    result = await agent.product_search("running shoes", brand="Nike", max_price=150)
    print(f"   Found {result.get('total_results', 0)} products")
    if result.get('success') and result.get('products'):
        print(f"   First result: {result['products'][0]['name']} - ${result['products'][0]['price']}")
    
    # Test 2: Product Availability
    print("\n2. Testing Product Availability:")
    result = await agent.product_availability("NK001", size="9")
    if result.get('success'):
        availability = result.get('availability', {})
        print(f"   Product: {availability.get('product_name', 'Unknown')}")
        print(f"   Available: {availability.get('overall_availability', False)}")
    
    # Test 3: Store Location Search
    print("\n3. Testing Store Location Search:")
    result = await agent.store_location_search("New York")
    if result.get('success'):
        print(f"   Found {result.get('total_stores', 0)} stores")
        if result.get('stores'):
            print(f"   First store: {result['stores'][0]['name']}")
    
    # Test 4: Shoe Buying Guide
    print("\n4. Testing Shoe Buying Guide:")
    result = await agent.shoe_buying_guide("sizing")
    if result.get('success'):
        guidance = result.get('guidance', {})
        print(f"   Guide type: {guidance.get('question_type', 'Unknown')}")
        advice = guidance.get('advice', {})
        print(f"   Title: {advice.get('title', 'No title')}")
    
    # Test 5: Delivery Tracker
    print("\n5. Testing Delivery Tracker:")
    result = await agent.delivery_tracker("TRK123456")
    if result.get('success'):
        tracking = result.get('delivery_tracking', {})
        print(f"   Tracking ID: {tracking.get('tracking_id', 'Unknown')}")
        print(f"   Status: {tracking.get('current_status', 'Unknown')}")
    
    # Test 6: OpenAI Chat (if API key is available)
    print("\n6. Testing OpenAI Chat:")
    if agent.client:
        try:
            response = await agent.process_request("I'm looking for comfortable running shoes under $150")
            print(f"   Response: {response[:100]}...")
        except Exception as e:
            print(f"   Error: {str(e)}")
    else:
        print("   OpenAI client not available (API key not configured)")
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    asyncio.run(test_shoes_agent())
