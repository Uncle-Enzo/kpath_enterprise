#!/usr/bin/env python3
"""
Verify Shoes Agent Registration in Database
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models.models import Service, Tool
from backend.core.config import get_settings

# Database connection using torch-env
settings = get_settings()
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def verify_shoes_agent():
    """Verify the Shoes Agent is properly registered"""
    session = SessionLocal()
    
    try:
        # Find the ShoesAgent service
        service = session.query(Service).filter_by(name="ShoesAgent").first()
        
        if not service:
            print("❌ ShoesAgent service not found in database")
            return False
        
        print(f"✅ ShoesAgent service found (ID: {service.id})")
        print(f"   Description: {service.description}")
        print(f"   Endpoint: {service.endpoint}")
        print(f"   Version: {service.version}")
        print(f"   Status: {service.status}")
        
        # Get the tools
        tools = session.query(Tool).filter_by(service_id=service.id).all()
        print(f"   Tools: {len(tools)} tools registered")
        
        for tool in tools:
            print(f"   - {tool.tool_name}: {tool.tool_description}")
        
        # Verify all 5 tools are present
        expected_tools = [
            "product_search",
            "product_availability", 
            "store_location_search",
            "shoe_buying_guide",
            "delivery_tracker"
        ]
        
        found_tools = [tool.tool_name for tool in tools]
        missing_tools = [tool for tool in expected_tools if tool not in found_tools]
        
        if missing_tools:
            print(f"❌ Missing tools: {missing_tools}")
            return False
        
        print("✅ All 5 required tools are registered")
        
        # Check for OpenAI API key
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            print(f"✅ OpenAI API key configured (length: {len(api_key)})")
        else:
            print("❌ OpenAI API key not configured")
            return False
        
        print("\n🎉 ShoesAgent verification successful!")
        print("   - Service registered in database ✅")
        print("   - All 5 tools present ✅") 
        print("   - OpenAI API key configured ✅")
        print("   - Ready for use ✅")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during verification: {str(e)}")
        return False
    finally:
        session.close()

if __name__ == "__main__":
    print("Verifying Shoes Agent Registration...")
    success = verify_shoes_agent()
    if success:
        print("\n✅ Shoes Agent is fully operational!")
    else:
        print("\n❌ Shoes Agent verification failed!")
