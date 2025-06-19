"""
Enhanced Shoes Agent API - Handles agent-to-agent communication
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
import logging
from datetime import datetime
from .shoes_agent import ShoesAgent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agents/shoes", tags=["Shoes Agent"])

# Initialize the agent
shoes_agent = ShoesAgent()

# Enhanced message models for agent-to-agent communication
class AgentContext(BaseModel):
    source_agent: str
    session_id: Optional[str] = None
    timestamp: Optional[str] = None
    user_intent: str
    kpath_analysis: Optional[Dict[str, Any]] = None
    suggested_action: Optional[Dict[str, Any]] = None
    available_tools: Optional[List[str]] = None

class AgentMessage(BaseModel):
    message: str
    context: Optional[AgentContext] = None
    integration_info: Optional[Dict[str, Any]] = None
    conversation_history: Optional[List[Dict[str, Any]]] = None

class AgentResponse(BaseModel):
    response: Any
    metadata: Dict[str, Any]
    tools_used: Optional[List[str]] = None
    confidence: float = 1.0
    processing_time_ms: Optional[int] = None

# Original endpoints remain the same
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
    brand: Optional[str] = None,
    services: Optional[List[str]] = None
):
    """Find nearby shoe stores"""
    try:
        result = await shoes_agent.store_location_search(
            location=location, radius_miles=radius_miles, 
            brand=brand, services=services
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/guide")
async def get_buying_guide(
    question_type: str = "general",
    use_case: Optional[str] = None,
    foot_type: Optional[str] = None,
    budget: Optional[float] = None,
    brand_preference: Optional[List[str]] = None
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

# Enhanced chat endpoint for agent-to-agent communication
@router.post("/chat", response_model=AgentResponse)
async def enhanced_chat(request: AgentMessage):
    """
    Enhanced chat endpoint that handles agent-to-agent communication
    with full context and autonomous decision-making
    """
    start_time = datetime.now()
    
    try:
        logger.info(f"Received agent communication from {request.context.source_agent if request.context else 'Unknown'}")
        
        # Extract context if provided
        if request.context:
            user_intent = request.context.user_intent
            suggested_tool = request.context.suggested_action.get("tool") if request.context.suggested_action else None
            suggested_params = request.context.suggested_action.get("parameters", {}) if request.context.suggested_action else {}
            source_agent = request.context.source_agent
            session_id = request.context.session_id
            
            logger.info(f"Context: User intent='{user_intent}', Suggested tool='{suggested_tool}'")
            
            # Autonomous decision making
            if suggested_tool:
                # The PA Agent suggested a specific tool - let's evaluate if it's appropriate
                tool_result = await _execute_suggested_tool(
                    suggested_tool, 
                    user_intent,
                    suggested_params
                )
                
                if tool_result["success"]:
                    processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
                    
                    return AgentResponse(
                        response=tool_result["result"],
                        metadata={
                            "source_agent": "ShoesAgent",
                            "target_session": session_id,
                            "tool_decision": f"Accepted suggestion: {suggested_tool}",
                            "processing_notes": tool_result.get("notes", ""),
                            "timestamp": datetime.now().isoformat()
                        },
                        tools_used=[suggested_tool],
                        confidence=tool_result.get("confidence", 0.95),
                        processing_time_ms=processing_time
                    )
                else:
                    # Suggested tool failed or wasn't appropriate
                    logger.warning(f"Suggested tool {suggested_tool} failed: {tool_result.get('error')}")
                    # Fall through to natural language processing
            
            # Process with natural language understanding
            result = await shoes_agent.process_request(user_intent)
            
        else:
            # No context provided - process as regular chat
            result = await shoes_agent.process_request(request.message)
        
        processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return AgentResponse(
            response=result,
            metadata={
                "source_agent": "ShoesAgent",
                "processing_mode": "natural_language",
                "timestamp": datetime.now().isoformat()
            },
            tools_used=["gpt-4o-analysis"],
            confidence=0.9,
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        logger.error(f"Error in enhanced chat: {str(e)}")
        
        processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return AgentResponse(
            response=f"I encountered an error processing your request: {str(e)}",
            metadata={
                "source_agent": "ShoesAgent",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            },
            tools_used=[],
            confidence=0.0,
            processing_time_ms=processing_time
        )

async def _execute_suggested_tool(tool_name: str, user_query: str, 
                                 parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a specific tool based on PA Agent's suggestion
    """
    try:
        logger.info(f"Executing suggested tool: {tool_name} with params: {parameters}")
        
        if tool_name == "product_search":
            # Extract or enhance parameters from user query if needed
            query = parameters.get("query", user_query)
            result = await shoes_agent.product_search(
                query=query,
                brand=parameters.get("brand"),
                category=parameters.get("category"),
                min_price=parameters.get("min_price"),
                max_price=parameters.get("max_price"),
                size=parameters.get("size"),
                color=parameters.get("color"),
                sort_by=parameters.get("sort_by", "rating")
            )
            
            if result.get("success") and result.get("products"):
                return {
                    "success": True,
                    "result": f"Found {result['total_results']} shoes matching your criteria. Here are the top options:\n\n" + 
                             _format_product_results(result["products"][:5]),
                    "confidence": 0.95,
                    "notes": f"Searched for: {query}"
                }
            else:
                return {
                    "success": False,
                    "error": "No products found matching criteria"
                }
                
        elif tool_name == "product_availability":
            product_id = parameters.get("product_id")
            if not product_id:
                return {"success": False, "error": "Product ID required for availability check"}
                
            result = await shoes_agent.product_availability(
                product_id=product_id,
                size=parameters.get("size"),
                color=parameters.get("color"),
                location=parameters.get("location")
            )
            
            if result.get("success"):
                return {
                    "success": True,
                    "result": _format_availability_result(result),
                    "confidence": 0.98,
                    "notes": f"Checked availability for product {product_id}"
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Availability check failed")
                }
                
        elif tool_name == "store_location_search":
            location = parameters.get("location", "user location")
            result = await shoes_agent.store_location_search(
                location=location,
                radius_miles=parameters.get("radius_miles", 25),
                brand=parameters.get("brand"),
                services=parameters.get("services")
            )
            
            if result.get("success") and result.get("stores"):
                return {
                    "success": True,
                    "result": f"Found {len(result['stores'])} shoe stores near {location}:\n\n" +
                             _format_store_results(result["stores"][:5]),
                    "confidence": 0.92,
                    "notes": f"Searched within {parameters.get('radius_miles', 25)} miles of {location}"
                }
            else:
                return {
                    "success": False,
                    "error": "No stores found in the specified area"
                }
                
        elif tool_name == "shoe_buying_guide":
            result = await shoes_agent.shoe_buying_guide(
                question_type=parameters.get("question_type", "general"),
                use_case=parameters.get("use_case"),
                foot_type=parameters.get("foot_type"),
                budget=parameters.get("budget"),
                brand_preference=parameters.get("brand_preference")
            )
            
            if result.get("success"):
                return {
                    "success": True,
                    "result": result.get("advice", ""),
                    "confidence": 0.90,
                    "notes": "Provided personalized buying guidance"
                }
            else:
                return {
                    "success": False,
                    "error": "Could not generate buying guide"
                }
                
        elif tool_name == "delivery_tracker":
            # Need at least one identifier
            tracking_id = parameters.get("tracking_id")
            order_id = parameters.get("order_id")
            
            if not tracking_id and not order_id:
                return {"success": False, "error": "Tracking ID or Order ID required"}
                
            result = await shoes_agent.delivery_tracker(
                tracking_id=tracking_id,
                order_id=order_id,
                email=parameters.get("email"),
                phone=parameters.get("phone")
            )
            
            if result.get("success"):
                return {
                    "success": True,
                    "result": _format_tracking_result(result),
                    "confidence": 0.99,
                    "notes": f"Tracked using {'tracking ID' if tracking_id else 'order ID'}"
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Tracking information not found")
                }
                
        else:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}"
            }
            
    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

# Helper functions to format results
def _format_product_results(products: List[Dict]) -> str:
    """Format product search results for display"""
    formatted = []
    for i, product in enumerate(products, 1):
        formatted.append(
            f"{i}. **{product['name']}** - ${product['price']}\n"
            f"   Brand: {product['brand']} | Rating: {product['rating']}/5\n"
            f"   {product['description'][:100]}..."
        )
    return "\n".join(formatted)

def _format_availability_result(result: Dict) -> str:
    """Format availability check results"""
    availability = result.get("availability", {})
    return (
        f"Product: {result.get('product_name', 'Unknown')}\n"
        f"In Stock: {'Yes' if availability.get('in_stock') else 'No'}\n"
        f"Available Sizes: {', '.join(availability.get('sizes', []))}\n"
        f"Available Colors: {', '.join(availability.get('colors', []))}\n"
        f"Stock Level: {availability.get('stock_level', 'Unknown')}"
    )

def _format_store_results(stores: List[Dict]) -> str:
    """Format store location results"""
    formatted = []
    for i, store in enumerate(stores, 1):
        formatted.append(
            f"{i}. **{store['name']}**\n"
            f"   📍 {store['address']}\n"
            f"   📞 {store['phone']} | 🚗 {store['distance']} miles"
        )
    return "\n".join(formatted)

def _format_tracking_result(result: Dict) -> str:
    """Format delivery tracking results"""
    tracking = result.get("tracking_info", {})
    return (
        f"Order Status: {tracking.get('status', 'Unknown')}\n"
        f"Current Location: {tracking.get('current_location', 'Unknown')}\n"
        f"Last Update: {tracking.get('last_update', 'Unknown')}\n"
        f"Estimated Delivery: {tracking.get('estimated_delivery', 'Unknown')}"
    )

# Legacy simple chat endpoint (backward compatibility)
@router.post("/chat/simple")
async def simple_chat(message: str):
    """Simple chat endpoint for backward compatibility"""
    try:
        result = await shoes_agent.process_request(message)
        return {"response": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
