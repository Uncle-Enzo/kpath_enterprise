#!/usr/bin/env python3
"""
Command Line Interface for Personal Assistant Agent
"""

import asyncio
import argparse
import sys
import os
from datetime import datetime

# Add the agents directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from agents.pa.pa_agent import PersonalAssistantAgent

def print_banner():
    """Print the PA Agent banner"""
    print("=" * 60)
    print("🤖 Personal Assistant Agent - KPATH Enterprise")
    print("   Powered by OpenAI GPT-4o")
    print("=" * 60)
    print()

async def interactive_mode():
    """Run the PA Agent in interactive mode"""
    print_banner()
    print("Interactive mode started. Type 'quit' or 'exit' to stop.")
    print("Type 'help' for available commands.")
    print()
    
    # Initialize the PA Agent
    agent = PersonalAssistantAgent()
    
    if not agent.client:
        print("⚠️  Warning: OpenAI API key not configured. AI features limited.")
        print()
    
    try:
        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                # Handle special commands
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye! 👋")
                    break
                elif user_input.lower() == 'help':
                    print_help()
                    continue
                elif user_input.lower() == 'status':
                    await check_status(agent)
                    continue
                
                # Process the user query
                print(f"\n🤖 PA Agent: Processing your request...")
                print("-" * 50)
                
                start_time = datetime.now()
                response = await agent.process_request(user_input)
                end_time = datetime.now()
                
                print(f"\n✅ Response (took {(end_time - start_time).total_seconds():.1f}s):")
                print(response)
                print("-" * 50)
                print()
                
            except KeyboardInterrupt:
                print("\n\nInterrupted by user. Goodbye! 👋")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                print()
    
    finally:
        await agent.close()

async def single_query_mode(query: str):
    """Process a single query and exit"""
    print_banner()
    print(f"Processing query: '{query}'")
    print()
    
    agent = PersonalAssistantAgent()
    
    try:
        start_time = datetime.now()
        response = await agent.process_request(query)
        end_time = datetime.now()
        
        print(f"Response (took {(end_time - start_time).total_seconds():.1f}s):")
        print("-" * 50)
        print(response)
        print("-" * 50)
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        await agent.close()

def print_help():
    """Print help information"""
    print("\n📖 Available Commands:")
    print("  help    - Show this help message")
    print("  status  - Check PA Agent and KPATH connection status")
    print("  quit    - Exit the PA Agent")
    print("  exit    - Exit the PA Agent")
    print("  q       - Exit the PA Agent")
    print("\n💡 Example queries:")
    print("  'Find running shoes under $150'")
    print("  'I need to track my delivery'")
    print("  'What tools are available for payments?'")
    print("  'Help me find a good restaurant'")
    print()

async def check_status(agent):
    """Check the status of PA Agent and KPATH connection"""
    print("\n🔍 Checking PA Agent Status...")
    
    # Check OpenAI connection
    if agent.client:
        print("✅ OpenAI GPT-4o: Connected")
    else:
        print("❌ OpenAI GPT-4o: Not configured")
    
    # Check KPATH connection
    try:
        health_url = f"{agent.kpath_base_url}/api/v1/health"
        response = await agent.http_client.get(health_url)
        if response.status_code == 200:
            print("✅ KPATH Enterprise: Connected")
        else:
            print(f"⚠️  KPATH Enterprise: Connected but returned status {response.status_code}")
    except Exception as e:
        print(f"❌ KPATH Enterprise: Connection failed - {str(e)}")
    
    # Test search functionality
    try:
        test_results = await agent.search_kpath("test query", limit=1)
        if "error" not in test_results:
            print("✅ KPATH Search: Working")
        else:
            print(f"❌ KPATH Search: Error - {test_results['error']}")
    except Exception as e:
        print(f"❌ KPATH Search: Failed - {str(e)}")
    
    print()

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Personal Assistant Agent - KPATH Enterprise",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py                                    # Interactive mode
  python cli.py -q "find running shoes"           # Single query
  python cli.py --query "track my delivery"       # Single query (long form)
        """
    )
    
    parser.add_argument(
        '-q', '--query',
        type=str,
        help='Process a single query and exit'
    )
    
    parser.add_argument(
        '--kpath-url',
        type=str,
        default='http://localhost:8000',
        help='KPATH Enterprise base URL (default: http://localhost:8000)'
    )
    
    args = parser.parse_args()
    
    # Set the KPATH URL if provided
    if args.kpath_url:
        os.environ['KPATH_BASE_URL'] = args.kpath_url
    
    # Run the appropriate mode
    if args.query:
        asyncio.run(single_query_mode(args.query))
    else:
        asyncio.run(interactive_mode())

if __name__ == "__main__":
    main()
