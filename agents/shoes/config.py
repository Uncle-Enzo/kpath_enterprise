"""
Shoes Agent Configuration and Tools
"""

# Service Configuration
SHOES_SERVICE_CONFIG = {
    "service_name": "ShoesAgent",
    "service_type": "AI_Assistant", 
    "description": "OpenAI GPT-4o powered agent for comprehensive shoe shopping assistance",
    "category": "E-commerce",
    "status": "active",
    "version": "1.0.0",
    "provider": "OpenAI GPT-4o",
    "base_url": "http://localhost:8000/api/v1/agents/shoes",
    "capabilities": [
        "Product Search and Filtering",
        "Real-time Stock Availability", 
        "Store Location Services",
        "Expert Shoe Buying Guidance",
        "Order and Delivery Tracking"
    ]
}

# Tool Definitions
SHOES_TOOLS = [
    {
        "tool_name": "product_search",
        "description": "Search for shoes by criteria (brand, price, size, color, category)",
        "parameters": {
            "query": "string (required) - Search query",
            "brand": "string - Brand filter",
            "category": "string - Category filter", 
            "min_price": "number - Min price",
            "max_price": "number - Max price",
            "size": "string - Size filter",
            "color": "string - Color filter"
        }
    },
    {
        "tool_name": "product_availability", 
        "description": "Check stock and availability for specific products",
        "parameters": {
            "product_id": "string (required) - Product ID",
            "size": "string - Specific size",
            "color": "string - Specific color",
            "location": "string - Store location"
        }
    },
    {
        "tool_name": "store_location_search",
        "description": "Find nearby shoe stores with details",
        "parameters": {
            "location": "string (required) - Search location",
            "radius_miles": "number - Search radius",
            "store_type": "string - Store type filter"
        }
    },
    {
        "tool_name": "shoe_buying_guide",
        "description": "Expert advice on shoe selection and care",
        "parameters": {
            "question_type": "string (required) - Type of guidance needed",
            "use_case": "string - Intended use",
            "budget": "number - Budget range"
        }
    },
    {
        "tool_name": "delivery_tracker",
        "description": "Track orders and deliveries",
        "parameters": {
            "tracking_id": "string - Tracking number",
            "order_id": "string - Order number",
            "email": "string - Email address"
        }
    }
]
