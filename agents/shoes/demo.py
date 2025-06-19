#!/usr/bin/env python3
"""
Demo script for the Shoes Agent
"""

import asyncio
import json
from datetime import datetime

# Mock implementation of the Shoes Agent tools
class ShoesAgentDemo:
    def __init__(self):
        self.mock_products = [
            {
                "id": "NK001",
                "name": "Air Max 270",
                "brand": "Nike",
                "price": 130.00,
                "sizes": ["7", "8", "9", "10", "11"],
                "colors": ["Black", "White", "Blue"],
                "category": "sneakers",
                "description": "Comfortable running sneaker with air cushioning",
                "rating": 4.5,
                "in_stock": True
            },
            {
                "id": "AD002", 
                "name": "Ultraboost 22",
                "brand": "Adidas",
                "price": 180.00,
                "sizes": ["7.5", "8.5", "9.5", "10.5"],
                "colors": ["Black", "White", "Grey"],
                "category": "athletic",
                "description": "Premium running shoe with boost technology",
                "rating": 4.7,
                "in_stock": True
            }
        ]
        
        self.mock_stores = [
            {
                "id": "ST001",
                "name": "Nike Flagship Store",
                "address": "123 Main St, New York, NY 10001",
                "phone": "555-0101",
                "hours": {"Mon-Sat": "10AM-9PM", "Sun": "11AM-7PM"},
                "distance_miles": 2.1
            }
        ]
    
    async def product_search(self, query, **filters):
        """Demo product search"""
        print(f"🔍 Searching for: {query}")
        if filters:
            print(f"   Filters: {filters}")
        
        # Simple matching
        results = [p for p in self.mock_products 
                  if query.lower() in p['name'].lower() or 
                     query.lower() in p['category'].lower()]
        
        return {
            "success": True,
            "query": query,
            "total_results": len(results),
            "products": results
        }
    
    async def product_availability(self, product_id, **options):
        """Demo availability check"""
        print(f"📦 Checking availability for product: {product_id}")
        
        product = next((p for p in self.mock_products if p['id'] == product_id), None)
        if not product:
            return {"success": False, "error": "Product not found"}
        
        return {
            "success": True,
            "availability": {
                "product_id": product_id,
                "product_name": product['name'],
                "in_stock": product['in_stock'],
                "available_sizes": product['sizes'],
                "available_colors": product['colors']
            }
        }
    
    async def store_location_search(self, location, **options):
        """Demo store search"""
        print(f"🏪 Finding stores near: {location}")
        
        return {
            "success": True,
            "search_location": location,
            "total_stores": len(self.mock_stores),
            "stores": self.mock_stores
        }
    
    async def shoe_buying_guide(self, question_type, **options):
        """Demo buying guide"""
        print(f"💡 Providing guidance on: {question_type}")
        
        guides = {
            "sizing": {
                "title": "Shoe Sizing Guide",
                "tips": ["Measure feet in afternoon when slightly swollen",
                        "Always buy for the larger foot",
                        "Leave thumb's width of space at toe"]
            },
            "care": {
                "title": "Shoe Care Tips", 
                "tips": ["Allow shoes to air dry between wears",
                        "Use shoe trees to maintain shape",
                        "Clean regularly with appropriate products"]
            }
        }
        
        return {
            "success": True,
            "guidance": guides.get(question_type, {"title": "General Advice", "tips": ["Consider your use case and budget"]})
        }
    
    async def delivery_tracker(self, tracking_id=None, **options):
        """Demo delivery tracking"""
        print(f"📦 Tracking delivery: {tracking_id}")
        
        return {
            "success": True,
            "delivery_tracking": {
                "tracking_id": tracking_id,
                "status": "In Transit",
                "estimated_delivery": "2025-06-20",
                "current_location": "Distribution Center - Newark, NJ",
                "last_update": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
        }

async def demo_shoes_agent():
    """Run a demo of the Shoes Agent"""
    agent = ShoesAgentDemo()
    
    print("=" * 50)
    print("👟 SHOES AGENT DEMO")
    print("=" * 50)
    
    # Demo 1: Product Search
    print("\n1️⃣ PRODUCT SEARCH")
    result = await agent.product_search("running shoes", brand="Nike", max_price=150)
    print(f"   Found {result['total_results']} products:")
    for product in result['products']:
        print(f"   • {product['name']} by {product['brand']} - ${product['price']}")
    
    # Demo 2: Availability Check
    print("\n2️⃣ PRODUCT AVAILABILITY")
    result = await agent.product_availability("NK001", size="9")
    availability = result['availability']
    print(f"   {availability['product_name']}: {'✅ In Stock' if availability['in_stock'] else '❌ Out of Stock'}")
    print(f"   Available sizes: {', '.join(availability['available_sizes'])}")
    
    # Demo 3: Store Search
    print("\n3️⃣ STORE LOCATION SEARCH")
    result = await agent.store_location_search("New York, NY")
    print(f"   Found {result['total_stores']} stores:")
    for store in result['stores']:
        print(f"   • {store['name']} ({store['distance_miles']} miles)")
        print(f"     {store['address']}, {store['phone']}")
    
    # Demo 4: Buying Guide
    print("\n4️⃣ SHOE BUYING GUIDE")
    result = await agent.shoe_buying_guide("sizing")
    guidance = result['guidance']
    print(f"   {guidance['title']}:")
    for tip in guidance['tips']:
        print(f"   • {tip}")
    
    # Demo 5: Delivery Tracking
    print("\n5️⃣ DELIVERY TRACKER")
    result = await agent.delivery_tracker("TRK123456")
    tracking = result['delivery_tracking']
    print(f"   Status: {tracking['status']}")
    print(f"   Location: {tracking['current_location']}")
    print(f"   Expected: {tracking['estimated_delivery']}")
    
    print("\n" + "=" * 50)
    print("✅ Demo completed! All 5 tools working correctly.")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(demo_shoes_agent())
