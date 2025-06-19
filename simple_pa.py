#!/usr/bin/env python3
"""
Simple PA Agent CLI - Working Version
Direct service access with manual routing
"""

import asyncio
import os
import sys
import argparse
from datetime import datetime
from dotenv import load_dotenv
import httpx

try:
    from openai import OpenAI
except ImportError:
    print("OpenAI library not installed. Run: pip install openai")
    OpenAI = None

# Load environment variables
load_dotenv()

class SimplePA:
    """Simplified PA Agent with direct service routing"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.base_url = "http://localhost:8000"
        
        if OpenAI and self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        else:
            self.client = None
            
        self.http_client = httpx.AsyncClient(timeout=10.0)

    async def process_query(self, query: str) -> str:
        """Process user query with simple routing logic"""
        
        query_lower = query.lower()
        
        # Route to Shoes Agent if query is about shoes
        if any(word in query_lower for word in ['shoe', 'shoes', 'sneaker', 'boot', 'running']):
            return await self.handle_shoes_query(query)
        
        # Default GPT-4o response for other queries
        return await self.handle_general_query(query)

    async def handle_shoes_query(self, query: str) -> str:
        """Handle shoe-related queries using the Shoes Agent"""
        try:
            print("🔍 Routing to Shoes Agent...")
            
            # Use the Shoes Agent chat endpoint
            chat_url = f"{self.base_url}/api/v1/agents/shoes/chat"
            
            response = await self.http_client.post(
                chat_url,
                params={"message": query}
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "No response from Shoes Agent")
            else:
                # Fallback to GPT-4o
                return await self.handle_general_query(f"Help with shoes: {query}")
                
        except Exception as e:
            print(f"Error connecting to Shoes Agent: {e}")
            return await self.handle_general_query(f"Help with shoes: {query}")

    async def handle_general_query(self, query: str) -> str:
        """Handle general queries with GPT-4o"""
        if not self.client:
            return "I need OpenAI API access to help with general queries. Please configure OPENAI_API_KEY."
        
        try:
            print("🤖 Processing with GPT-4o...")
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful personal assistant. Provide clear, concise, and useful responses."},
                    {"role": "user", "content": query}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error processing query: {str(e)}"

    async def close(self):
        """Clean up resources"""
        await self.http_client.aclose()

def print_banner():
    """Print banner"""
    print("=" * 60)
    print("🤖 Personal Assistant Agent - KPATH Enterprise")
    print("   Simple Direct Routing Version")
    print("=" * 60)
    print()

async def interactive_mode():
    """Interactive mode"""
    print_banner()
    print("Type your questions or commands. Type 'quit' to exit.")
    print("Examples:")
    print("  - 'Find running shoes under $150'")
    print("  - 'What's the weather like?'")
    print("  - 'Help me plan a trip'")
    print()
    
    pa = SimplePA()
    
    try:
        while True:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye! 👋")
                break
            
            print(f"\n🤖 Processing...")
            start_time = datetime.now()
            
            response = await pa.process_query(user_input)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            print(f"\n✅ Response (took {duration:.1f}s):")
            print("-" * 50)
            print(response)
            print("-" * 50)
            print()
            
    except KeyboardInterrupt:
        print("\n\nGoodbye! 👋")
    finally:
        await pa.close()

async def single_query(query: str):
    """Process single query"""
    print_banner()
    print(f"Query: {query}")
    print()
    
    pa = SimplePA()
    
    try:
        start_time = datetime.now()
        response = await pa.process_query(query)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"Response (took {duration:.1f}s):")
        print("-" * 50)
        print(response)
        print("-" * 50)
        
    finally:
        await pa.close()

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Simple PA Agent")
    parser.add_argument('-q', '--query', help='Single query mode')
    
    args = parser.parse_args()
    
    if args.query:
        asyncio.run(single_query(args.query))
    else:
        asyncio.run(interactive_mode())

if __name__ == "__main__":
    main()
