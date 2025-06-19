"""
Script to register the Shoes Agent as a service in KPATH Enterprise
"""

import asyncio
import sys
import os

# Add the project root to the path
sys.path.append('/Users/james/claude_development/kpath_enterprise')

from backend.services.service_crud import ServiceCRUD
from backend.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

async def register_shoes_agent():
    """Register the Shoes Agent and its tools in the database"""
    
    # Get database session
    async for db in get_db():
        service_crud = ServiceCRUD(db)
        
        try:
            # Service data
            service_data = {
                "service_name": "ShoesAgent",
                "service_type": "AI_Assistant",
                "description": "OpenAI GPT-4o powered agent for comprehensive shoe shopping assistance with 5 specialized tools",
                "category": "E-commerce",
                "status": "active",
                "version": "1.0.0",
                "provider": "OpenAI",
                "base_url": "http://localhost:8000/api/v1/agents/shoes",
                "authentication_type": "api_key",
                "rate_limit": "100/hour",
                "timeout_seconds": 30
            }
            
            # Create the service
            print("Creating Shoes Agent service...")
            service = await service_crud.create_service(**service_data)
            print(f"✅ Service created with ID: {service.id}")
            
            # Tools data
            tools_data = [
                {
                    "service_id": service.id,
                    "tool_name": "product_search", 
                    "description": "Search for shoes by various criteria including brand, style, price range, size, color, and category",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query for shoes"},
                            "brand": {"type": "string", "description": "Specific brand to filter by"},
                            "category": {"type": "string", "description": "Shoe category"},
                            "min_price": {"type": "number", "description": "Minimum price filter"},
                            "max_price": {"type": "number", "description": "Maximum price filter"},
                            "size": {"type": "string", "description": "Shoe size to filter by"},
                            "color": {"type": "string", "description": "Color preference"},
                            "sort_by": {"type": "string", "enum": ["price_low", "price_high", "rating", "name"]}
                        },
                        "required": ["query"]
                    },
                    "output_schema": {
                        "type": "object",
                        "properties": {
                            "success": {"type": "boolean"},
                            "products": {"type": "array"},
                            "total_results": {"type": "integer"}
                        }
                    },
                    "example_calls": [
                        {"query": "running shoes", "brand": "Nike", "max_price": 150}
                    ]
                },
