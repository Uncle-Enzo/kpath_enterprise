#!/usr/bin/env python3
"""
Script to add the Shoes Agent service to KPATH Enterprise.
"""

import os
import sys
import json
from datetime import datetime

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models.models import Service, ServiceCapability, ServiceIndustry, Tool, ServiceIntegrationDetails
from backend.core.config import get_settings

# Database connection
settings = get_settings()
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def add_shoes_agent_service():
    """Add the Shoes Agent service to the database."""
    
    session = SessionLocal()
    
    try:
        # Check if service already exists
        existing_service = session.query(Service).filter_by(name="ShoesAgent").first()
        if existing_service:
            print("ShoesAgent service already exists. Skipping...")
            return
        
        # Create the service
        service = Service(
            name="ShoesAgent",
            description="OpenAI GPT-4o powered agent for comprehensive shoe shopping assistance with 5 specialized tools",
            endpoint="http://localhost:8000/api/v1/agents/shoes",
            version="1.0.0",
            status="active",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        session.add(service)
        session.flush()  # Get the service ID
        
        # Add capabilities
        capabilities = [
            "Product Search and Filtering",
            "Real-time Stock Availability", 
            "Store Location Services",
            "Expert Shoe Buying Guidance",
            "Order and Delivery Tracking"
        ]
        
        for cap in capabilities:
            capability = ServiceCapability(
                service_id=service.id,
                capability_name=cap,
                created_at=datetime.utcnow()
            )
            session.add(capability)
        
        # Add industry
        industry = ServiceIndustry(
            service_id=service.id,
            industry_name="E-commerce",
            created_at=datetime.utcnow()
        )
        session.add(industry)
        
        # Add tools
        tools_data = [
            {
                "tool_name": "product_search",
                "description": "Search for shoes by various criteria including brand, style, price range, size, color, and category",
                "endpoint": "/search",
                "method": "POST",
                "parameters": {
                    "query": {"type": "string", "required": True, "description": "Search query for shoes"},
                    "brand": {"type": "string", "required": False, "description": "Specific brand to filter by"},
                    "category": {"type": "string", "required": False, "description": "Shoe category"},
                    "min_price": {"type": "number", "required": False, "description": "Minimum price filter"},
                    "max_price": {"type": "number", "required": False, "description": "Maximum price filter"},
                    "size": {"type": "string", "required": False, "description": "Shoe size to filter by"},
                    "color": {"type": "string", "required": False, "description": "Color preference"},
                    "sort_by": {"type": "string", "required": False, "description": "Sort order"}
                },
                "example_calls": [
                    {"query": "running shoes", "brand": "Nike", "max_price": 150},
                    {"query": "boots", "category": "work", "min_price": 100}
                ]
            },
            {
                "tool_name": "product_availability",
                "description": "Check availability, stock levels, and size options for specific shoe products",
                "endpoint": "/availability/{product_id}",
                "method": "GET",
                "parameters": {
                    "product_id": {"type": "string", "required": True, "description": "Product ID to check"},
                    "size": {"type": "string", "required": False, "description": "Specific size to check"},
                    "color": {"type": "string", "required": False, "description": "Specific color to check"},
                    "location": {"type": "string", "required": False, "description": "Store location"}
                },
                "example_calls": [
                    {"product_id": "NK001", "size": "9"},
                    {"product_id": "AD002", "color": "black"}
                ]
            },
            {
                "tool_name": "store_location_search",
                "description": "Find nearby shoe stores by location with details about hours, contact info, and services",
                "endpoint": "/stores",
                "method": "GET",
                "parameters": {
                    "location": {"type": "string", "required": True, "description": "City, state, or zip code"},
                    "radius_miles": {"type": "number", "required": False, "description": "Search radius in miles"},
                    "store_type": {"type": "string", "required": False, "description": "Type of store to find"}
                },
                "example_calls": [
                    {"location": "New York, NY", "radius_miles": 10},
                    {"location": "90210", "store_type": "flagship"}
                ]
            },
            {
                "tool_name": "shoe_buying_guide",
                "description": "Provide expert advice on shoe selection, sizing, fit, care, and recommendations",
                "endpoint": "/guide",
                "method": "POST",
                "parameters": {
                    "question_type": {"type": "string", "required": True, "description": "Type of guidance needed"},
                    "use_case": {"type": "string", "required": False, "description": "How shoes will be used"},
                    "budget": {"type": "number", "required": False, "description": "Budget range"}
                },
                "example_calls": [
                    {"question_type": "sizing", "use_case": "running"},
                    {"question_type": "selection", "budget": 200}
                ]
            },
            {
                "tool_name": "delivery_tracker",
                "description": "Track shoe orders and deliveries with real-time status updates",
                "endpoint": "/track",
                "method": "GET",
                "parameters": {
                    "tracking_id": {"type": "string", "required": False, "description": "Tracking number"},
                    "order_id": {"type": "string", "required": False, "description": "Order number"},
                    "email": {"type": "string", "required": False, "description": "Email address"}
                },
                "example_calls": [
                    {"tracking_id": "TRK123456"},
                    {"order_id": "ORD789", "email": "customer@example.com"}
                ]
            }
        ]
        
        for tool_data in tools_data:
            tool = Tool(
                service_id=service.id,
                tool_name=tool_data["tool_name"],
                tool_description=tool_data["description"],
                endpoint=tool_data["endpoint"],
                method=tool_data["method"],
                parameters_schema=json.dumps(tool_data["parameters"]),
                example_calls=json.dumps(tool_data["example_calls"]),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(tool)
        
        # Add integration details
        integration_details = ServiceIntegrationDetails(
            service_id=service.id,
            connectivity_requirements=json.dumps({
                "requires_api_key": True,
                "requires_openai_key": True,
                "network_access": True
            }),
            data_formats_supported=json.dumps(["JSON", "Natural Language"]),
            authentication_methods=json.dumps(["API Key", "Bearer Token"]),
            rate_limiting_info=json.dumps({"requests_per_hour": 100, "burst_limit": 10}),
            error_handling_guidance=json.dumps({
                "retry_policy": "exponential_backoff",
                "max_retries": 3,
                "timeout_handling": "graceful_degradation"
            }),
            integration_examples=json.dumps({
                "basic_search": "POST /search with query parameter",
                "availability_check": "GET /availability/{product_id}",
                "chat_interface": "POST /chat with natural language message"
            }),
            created_at=datetime.utcnow()
        )
        session.add(integration_details)
        
        session.commit()
        print(f"Successfully added ShoesAgent service with ID: {service.id}")
        print(f"Added {len(tools_data)} tools and {len(capabilities)} capabilities")
        
    except Exception as e:
        session.rollback()
        print(f"Error adding ShoesAgent service: {str(e)}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    print("Adding ShoesAgent service to KPATH Enterprise...")
    add_shoes_agent_service()
    print("Done!")
