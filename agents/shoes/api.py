"""
Shoes Agent - Simple API Implementation
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
import asyncio
from .shoes_agent import ShoesAgent

router = APIRouter(prefix="/agents/shoes", tags=["Shoes Agent"])

# Initialize the agent
shoes_agent = ShoesAgent()

@router.post("/search")
async def search_products(
    query: str,
    brand: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    size: Optional[str] = None,
    color: Optional[str] = None,
    sort_by: str = "rating"
):
    """Search for shoes by various criteria"""
    try:
        result = await shoes_agent.product_search(
            query=query, brand=brand, category=category,
            min_price=min_price, max_price=max_price,
            size=size, color=color, sort_by=sort_by
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/availability/{product_id}")
async def check_availability(
    product_id: str,
    size: Optional[str] = None,
    color: Optional[str] = None,
    location: Optional[str] = None
):
    """Check product availability"""
    try:
        result = await shoes_agent.product_availability(
            product_id=product_id, size=size, color=color, location=location
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stores")
async def find_stores(
    location: str,
    radius_miles: int = 25,
    store_type: str = "all"
):
    """Find nearby shoe stores"""
    try:
        result = await shoes_agent.store_location_search(
            location=location, radius_miles=radius_miles, store_type=store_type
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/guide")
async def get_buying_guide(
    question_type: str,
    use_case: Optional[str] = None,
    foot_type: Optional[str] = None,
    budget: Optional[float] = None,
    brand_preference: Optional[str] = None
):
    """Get expert shoe buying advice"""
    try:
        result = await shoes_agent.shoe_buying_guide(
            question_type=question_type, use_case=use_case,
            foot_type=foot_type, budget=budget, brand_preference=brand_preference
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/track")
async def track_delivery(
    tracking_id: Optional[str] = None,
    order_id: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None
):
    """Track delivery status"""
    try:
        result = await shoes_agent.delivery_tracker(
            tracking_id=tracking_id, order_id=order_id, email=email, phone=phone
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat")
async def chat_with_agent(message: str):
    """Chat directly with the Shoes Agent using OpenAI GPT-4o"""
    try:
        result = await shoes_agent.process_request(message)
        return {"response": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
