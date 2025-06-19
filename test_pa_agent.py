#!/usr/bin/env python3
"""
Simple test for PA Agent
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the agents directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from agents.pa.pa_agent import PersonalAssistantAgent

async def test_pa_agent():
    """Test the PA Agent with a simple query"""
    print("Testing PA Agent...")
    
    # Check environment
    api_key = os.getenv('OPENAI_API_KEY')
    print(f"OpenAI API Key available: {'Yes' if api_key else 'No'}")
    
    # Initialize agent
    agent = PersonalAssistantAgent()
    
    try:
        # Test KPATH connection
        print("Testing KPATH connection...")
        search_results = await agent.search_kpath("test", limit=2)
        print(f"KPATH search test: {'Success' if 'results' in search_results else 'Failed'}")
        
        if 'results' in search_results:
            print(f"Found {len(search_results['results'])} results")
        
        # Test a simple query
        print("\nTesting simple query: 'shoes'")
        response = await agent.process_request("shoes")
        print(f"Response length: {len(response)} characters")
        print(f"Response preview: {response[:200]}...")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        await agent.close()

if __name__ == "__main__":
    asyncio.run(test_pa_agent())
