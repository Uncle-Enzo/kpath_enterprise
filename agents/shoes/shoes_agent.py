"""
Shoes Agent - OpenAI GPT-4o powered agent for shoe shopping assistance
Provides comprehensive shoe shopping support through 5 specialized tools
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import uuid
import asyncio
from dataclasses import dataclass, asdict

try:
    import openai
    from openai import OpenAI
except ImportError:
    print("OpenAI library not installed. Run: pip install openai")
    openai = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TokenUsage:
    """Track token usage for a session"""
    session_id: str
    timestamp: datetime
    operation: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    model: str
    query: str = ""
    response_preview: str = ""

@dataclass
class SessionMetrics:
    """Overall session metrics"""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_tokens: int = 0
    total_api_calls: int = 0
    queries_processed: int = 0
    token_usage_history: List[TokenUsage] = None
    
    def __post_init__(self):
        if self.token_usage_history is None:
            self.token_usage_history = []

@dataclass
class ShoeProduct:
    """Represents a shoe product"""
    id: str
    name: str
    brand: str
    price: float
    sizes: List[str]
    colors: List[str]
    category: str
    description: str
    image_url: str
    rating: float
    in_stock: bool

@dataclass  
class StoreLocation:
    """Represents a store location"""
    id: str
    name: str
    address: str
    city: str
    state: str
    zip_code: str
    phone: str
    hours: Dict[str, str]
    latitude: float
    longitude: float

@dataclass
class DeliveryStatus:
    """Represents delivery tracking information"""
    tracking_id: str
    order_id: str
    status: str
    estimated_delivery: str
    current_location: str
    last_update: str

class ShoesAgent:
    """
    OpenAI GPT-4o powered agent for comprehensive shoe shopping assistance.
    
    Provides 5 specialized tools:
    1. Product Search - Find shoes by criteria
    2. Product Availability - Check stock and availability
    3. Store Location Search - Find nearby stores
    4. Shoe Buying Guide - Expert advice and recommendations
    5. Delivery Tracker - Track orders and deliveries
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Shoes Agent with OpenAI API key"""
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        
        # Token usage tracking
        self.session_id = f"shoes_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.session_metrics = SessionMetrics(
            session_id=self.session_id,
            start_time=datetime.now()
        )
        
        if not self.api_key:
            logger.warning("No OpenAI API key provided. Some features may not work.")
            
        if openai and self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        else:
            self.client = None
            
        # Mock data for demonstration (in production, these would connect to real databases/APIs)
        self._initialize_mock_data()
        
        # Define available tools
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "product_search",
                    "description": "Search for shoes by various criteria including brand, style, price range, size, color, and category",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query for shoes"},
                            "brand": {"type": "string", "description": "Specific brand to filter by"},
                            "category": {"type": "string", "description": "Shoe category (sneakers, boots, dress, casual, athletic, etc.)"},
                            "min_price": {"type": "number", "description": "Minimum price filter"},
                            "max_price": {"type": "number", "description": "Maximum price filter"},
                            "size": {"type": "string", "description": "Shoe size to filter by"},
                            "color": {"type": "string", "description": "Color preference"},
                            "sort_by": {"type": "string", "enum": ["price_low", "price_high", "rating", "name"], "description": "Sort order"}
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function", 
                "function": {
                    "name": "product_availability",
                    "description": "Check availability, stock levels, and size options for specific shoe products",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "product_id": {"type": "string", "description": "Product ID to check availability for"},
                            "size": {"type": "string", "description": "Specific size to check"},
                            "color": {"type": "string", "description": "Specific color to check"},
                            "location": {"type": "string", "description": "Check availability at specific store location"}
                        },
                        "required": ["product_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "store_location_search", 
                    "description": "Find nearby shoe stores by location, with details about hours, contact info, and available services",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {"type": "string", "description": "City, state, or zip code to search near"},
                            "radius_miles": {"type": "number", "description": "Search radius in miles", "default": 25},
                            "store_type": {"type": "string", "enum": ["all", "flagship", "outlet", "department"], "description": "Type of store to find"},
                            "services": {"type": "array", "items": {"type": "string"}, "description": "Required services (fitting, repair, custom orders, etc.)"}
                        },
                        "required": ["location"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "shoe_buying_guide",
                    "description": "Provide expert advice on shoe selection, sizing, fit, care, and recommendations based on use case",
                    "parameters": {
                        "type": "object", 
                        "properties": {
                            "use_case": {"type": "string", "description": "How the shoes will be used (running, work, casual, formal, etc.)"},
                            "foot_type": {"type": "string", "description": "Foot characteristics (wide, narrow, flat, high arch, etc.)"},
                            "budget": {"type": "number", "description": "Budget range for shoe purchase"},
                            "brand_preference": {"type": "string", "description": "Preferred or avoided brands"},
                            "question_type": {"type": "string", "enum": ["sizing", "fit", "care", "selection", "comparison"], "description": "Type of guidance needed"}
                        },
                        "required": ["question_type"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delivery_tracker",
                    "description": "Track shoe orders and deliveries, providing real-time status updates and estimated delivery times",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "tracking_id": {"type": "string", "description": "Delivery tracking number"},
                            "order_id": {"type": "string", "description": "Order number from purchase"},
                            "email": {"type": "string", "description": "Email address associated with order"},
                            "phone": {"type": "string", "description": "Phone number associated with order"}
                        }
                    }
                }
            }
        ]
    
    def _initialize_mock_data(self):
        """Initialize mock data for demonstration purposes"""
        self.mock_products = [
            ShoeProduct("NK001", "Air Max 270", "Nike", 130.00, ["7", "8", "9", "10", "11"], 
                       ["Black", "White", "Blue"], "sneakers", "Comfortable running sneaker with air cushioning", 
                       "https://example.com/airmax270.jpg", 4.5, True),
            ShoeProduct("AD002", "Ultraboost 22", "Adidas", 180.00, ["7.5", "8.5", "9.5", "10.5"], 
                       ["Black", "White", "Grey"], "athletic", "Premium running shoe with boost technology",
                       "https://example.com/ultraboost.jpg", 4.7, True),
            ShoeProduct("NB003", "990v5", "New Balance", 185.00, ["8", "9", "10", "11", "12"],
                       ["Grey", "Navy", "Black"], "casual", "Made in USA premium lifestyle sneaker",
                       "https://example.com/990v5.jpg", 4.6, False),
            ShoeProduct("TM004", "Chelsea Boot", "Timberland", 200.00, ["8", "9", "10", "11"],
                       ["Brown", "Black"], "boots", "Waterproof leather chelsea boot",
                       "https://example.com/chelsea.jpg", 4.4, True),
            ShoeProduct("CO005", "Chuck Taylor", "Converse", 60.00, ["6", "7", "8", "9", "10", "11"],
                       ["Black", "White", "Red"], "casual", "Classic canvas high-top sneaker",
                       "https://example.com/chucktaylor.jpg", 4.2, True)
        ]
        
        self.mock_stores = [
            StoreLocation("ST001", "Nike Flagship Store", "123 Main St", "New York", "NY", "10001",
                         "555-0101", {"Mon-Sat": "10AM-9PM", "Sun": "11AM-7PM"}, 40.7128, -74.0060),
            StoreLocation("ST002", "Adidas Originals", "456 Broadway", "New York", "NY", "10013", 
                         "555-0102", {"Mon-Sat": "10AM-8PM", "Sun": "12PM-6PM"}, 40.7589, -73.9851),
            StoreLocation("ST003", "Foot Locker", "789 5th Ave", "New York", "NY", "10022",
                         "555-0103", {"Mon-Sun": "10AM-9PM"}, 40.7614, -73.9776)
        ]
        
        self.mock_deliveries = {
            "TRK123456": DeliveryStatus("TRK123456", "ORD789", "In Transit", "2025-06-20", 
                                      "Distribution Center - Newark, NJ", "2025-06-18 14:30"),
            "TRK789012": DeliveryStatus("TRK789012", "ORD456", "Delivered", "2025-06-17", 
                                      "Delivered to Front Door", "2025-06-17 16:45")
        }
    
    async def product_search(self, query: str, brand: str = None, category: str = None, 
                           min_price: float = None, max_price: float = None, 
                           size: str = None, color: str = None, sort_by: str = "rating") -> Dict[str, Any]:
        """Search for shoes by various criteria"""
        try:
            # Filter products based on criteria
            filtered_products = []
            
            for product in self.mock_products:
                # Apply filters
                if brand and brand.lower() not in product.brand.lower():
                    continue
                if category and category.lower() not in product.category.lower():
                    continue
                if min_price and product.price < min_price:
                    continue
                if max_price and product.price > max_price:
                    continue
                if size and size not in product.sizes:
                    continue
                if color and color.lower() not in [c.lower() for c in product.colors]:
                    continue
                
                # Check if query matches name, brand, or description
                if query.lower() in product.name.lower() or \
                   query.lower() in product.brand.lower() or \
                   query.lower() in product.description.lower():
                    filtered_products.append(product)

            # Sort results
            if sort_by == "price_low":
                filtered_products.sort(key=lambda x: x.price)
            elif sort_by == "price_high":
                filtered_products.sort(key=lambda x: x.price, reverse=True)
            elif sort_by == "rating":
                filtered_products.sort(key=lambda x: x.rating, reverse=True)
            elif sort_by == "name":
                filtered_products.sort(key=lambda x: x.name)
            
            # Convert to dict format
            results = []
            for product in filtered_products[:10]:  # Limit to top 10 results
                results.append({
                    "id": product.id,
                    "name": product.name,
                    "brand": product.brand,
                    "price": product.price,
                    "sizes": product.sizes,
                    "colors": product.colors,
                    "category": product.category,
                    "description": product.description,
                    "rating": product.rating,
                    "in_stock": product.in_stock
                })
            
            return {
                "success": True,
                "query": query,
                "total_results": len(filtered_products),
                "products": results
            }
        except Exception as e:
            logger.error(f"Error in product_search: {str(e)}")
            return {"success": False, "error": str(e)}

    async def product_availability(self, product_id: str, size: str = None, 
                                 color: str = None, location: str = None) -> Dict[str, Any]:
        """Check availability and stock levels for specific products"""
        try:
            # Find the product
            product = None
            for p in self.mock_products:
                if p.id == product_id:
                    product = p
                    break
            
            if not product:
                return {"success": False, "error": "Product not found"}
            
            # Mock availability check
            availability = {
                "product_id": product_id,
                "product_name": product.name,
                "brand": product.brand,
                "base_price": product.price,
                "overall_availability": product.in_stock,
                "available_sizes": product.sizes if product.in_stock else [],
                "available_colors": product.colors if product.in_stock else []
            }
            
            return {"success": True, "availability": availability}
            
        except Exception as e:
            logger.error(f"Error in product_availability: {str(e)}")
            return {"success": False, "error": str(e)}

    async def store_location_search(self, location: str, radius_miles: int = 25, 
                                  store_type: str = "all", services: list = None) -> Dict[str, Any]:
        """Find nearby shoe stores with details"""
        try:
            matching_stores = []
            
            for store in self.mock_stores:
                if location.lower() in store.city.lower() or location.lower() in store.state.lower():
                    store_info = {
                        "id": store.id,
                        "name": store.name,
                        "address": f"{store.address}, {store.city}, {store.state} {store.zip_code}",
                        "phone": store.phone,
                        "hours": store.hours,
                        "distance_miles": 5.2  # Mock distance
                    }
                    matching_stores.append(store_info)
            
            return {
                "success": True,
                "search_location": location,
                "total_stores": len(matching_stores),
                "stores": matching_stores
            }
            
        except Exception as e:
            logger.error(f"Error in store_location_search: {str(e)}")
            return {"success": False, "error": str(e)}

    async def shoe_buying_guide(self, question_type: str, **kwargs) -> Dict[str, Any]:
        """Provide expert shoe buying advice"""
        try:
            guidance = {"question_type": question_type}
            
            if question_type == "sizing":
                guidance["advice"] = {
                    "title": "Shoe Sizing Guide",
                    "tips": [
                        "Measure feet in the afternoon when slightly swollen",
                        "Always measure both feet and buy for the larger foot",
                        "Leave about a thumb's width between longest toe and shoe end"
                    ]
                }
            elif question_type == "selection":
                guidance["advice"] = {
                    "title": "Shoe Selection Guide",
                    "tips": [
                        "Consider your primary use case",
                        "Invest in quality for frequently worn shoes",
                        "Try shoes on in the afternoon"
                    ]
                }
            
            return {"success": True, "guidance": guidance}
            
        except Exception as e:
            logger.error(f"Error in shoe_buying_guide: {str(e)}")
            return {"success": False, "error": str(e)}

    async def delivery_tracker(self, tracking_id: str = None, **kwargs) -> Dict[str, Any]:
        """Track shoe orders and deliveries"""
        try:
            if tracking_id and tracking_id in self.mock_deliveries:
                delivery_info = self.mock_deliveries[tracking_id]
                return {
                    "success": True,
                    "delivery_tracking": {
                        "tracking_id": delivery_info.tracking_id,
                        "order_id": delivery_info.order_id,
                        "current_status": delivery_info.status,
                        "estimated_delivery": delivery_info.estimated_delivery,
                        "current_location": delivery_info.current_location,
                        "last_update": delivery_info.last_update
                    }
                }
            else:
                return {"success": False, "error": "Tracking information not found"}
            
        except Exception as e:
            logger.error(f"Error in delivery_tracker: {str(e)}")
            return {"success": False, "error": str(e)}

    async def process_request(self, user_message: str) -> str:
        """Process a user request using OpenAI GPT-4o with function calling"""
        if not self.client:
            return "OpenAI client not initialized. Please provide a valid API key."
        
        try:
            self.session_metrics.queries_processed += 1
            
            system_prompt = """You are a specialized Shoes Shopping Assistant. 
            You help customers find shoes, check availability, locate stores, provide buying advice, and track deliveries.
            Use the available tools to provide accurate and helpful responses."""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            # Track token usage
            final_response = response.choices[0].message.content
            self.track_token_usage("chat_response", response, user_message, final_response)
            
            return final_response
                
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            return f"I apologize, but I encountered an error: {str(e)}"

# Convenience functions for direct tool access
async def search_products(query: str, **kwargs) -> Dict[str, Any]:
    """Direct access to product search functionality"""
    agent = ShoesAgent()
    return await agent.product_search(query, **kwargs)

async def check_availability(product_id: str, **kwargs) -> Dict[str, Any]:
    """Direct access to availability checking"""
    agent = ShoesAgent()
    return await agent.product_availability(product_id, **kwargs)
    
    def track_token_usage(self, operation: str, response, query: str = "", response_preview: str = ""):
        """Track token usage from OpenAI API response"""
        try:
            if hasattr(response, 'usage') and response.usage:
                usage = TokenUsage(
                    session_id=self.session_id,
                    timestamp=datetime.now(),
                    operation=operation,
                    prompt_tokens=response.usage.prompt_tokens,
                    completion_tokens=response.usage.completion_tokens,
                    total_tokens=response.usage.total_tokens,
                    model=getattr(response, 'model', 'gpt-4o'),
                    query=query,
                    response_preview=response_preview[:200] if response_preview else ""
                )
                
                self.session_metrics.token_usage_history.append(usage)
                self.session_metrics.total_tokens += usage.total_tokens
                self.session_metrics.total_api_calls += 1
                
                logger.info(f"Shoes Agent Token usage - {operation}: {usage.total_tokens} tokens (prompt: {usage.prompt_tokens}, completion: {usage.completion_tokens})")
                
        except Exception as e:
            logger.error(f"Error tracking token usage: {str(e)}")
    
    def get_session_metrics(self) -> Dict[str, Any]:
        """Get current session metrics"""
        if self.session_metrics.end_time is None:
            self.session_metrics.end_time = datetime.now()
            
        return {
            "agent_type": "ShoesAgent",
            "session_id": self.session_metrics.session_id,
            "start_time": self.session_metrics.start_time.isoformat(),
            "end_time": self.session_metrics.end_time.isoformat() if self.session_metrics.end_time else None,
            "duration_seconds": (self.session_metrics.end_time - self.session_metrics.start_time).total_seconds() if self.session_metrics.end_time else None,
            "total_tokens": self.session_metrics.total_tokens,
            "total_api_calls": self.session_metrics.total_api_calls,
            "queries_processed": self.session_metrics.queries_processed,
            "average_tokens_per_query": self.session_metrics.total_tokens / max(1, self.session_metrics.queries_processed),
            "token_usage_breakdown": [asdict(usage) for usage in self.session_metrics.token_usage_history]
        }
    
    def save_session_metrics(self, filepath: Optional[str] = None):
        """Save session metrics to file"""
        if filepath is None:
            filepath = f"shoes_agent_metrics_{self.session_id}.json"
            
        metrics = self.get_session_metrics()
        
        with open(filepath, 'w') as f:
            json.dump(metrics, f, indent=2, default=str)
            
        logger.info(f"Shoes Agent session metrics saved to {filepath}")
