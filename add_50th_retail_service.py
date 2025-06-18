#!/usr/bin/env python3
"""
Script to add the 50th retail enterprise service.
"""

import os
import sys
from datetime import datetime

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models.models import Service, ServiceCapability, ServiceIndustry, Tool, ServiceIntegrationDetails, ServiceAgentProtocols
from backend.core.config import get_settings

# Database connection
settings = get_settings()
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def add_final_service():
    """Add the 50th retail service."""
    db = SessionLocal()
    
    try:
        service_data = {
            "name": "OmniChannelFulfillmentAPI",
            "version": "4.5.0",
            "description": "Advanced omnichannel fulfillment orchestration and optimization",
            "endpoint": "https://api.enterprise.com/omnichannel-fulfillment/v4",
            "capabilities": ["Order Orchestration", "Fulfillment Optimization", "Cross-Channel Inventory"],
            "tools": [
                {"name": "optimize_fulfillment_routing", "description": "Find optimal fulfillment location for orders"},
                {"name": "split_order_intelligently", "description": "Intelligently split orders across locations"},
                {"name": "promise_delivery_date", "description": "Calculate and promise accurate delivery dates"},
                {"name": "manage_store_fulfillment", "description": "Manage ship-from-store operations"},
                {"name": "track_cross_channel_inventory", "description": "Track inventory across all channels"},
                {"name": "orchestrate_curbside_pickup", "description": "Orchestrate curbside pickup operations"},
                {"name": "manage_locker_delivery", "description": "Manage locker and alternative delivery"},
                {"name": "optimize_carrier_selection", "description": "Select optimal carrier for shipments"}
            ]
        }
        
        # Create service
        service = Service(
            name=service_data["name"],
            version=service_data["version"],
            description=service_data["description"],
            endpoint=service_data["endpoint"],
            status="active",
            tool_type="API",
            visibility="internal",
            default_timeout_ms=30000
        )
        
        db.add(service)
        db.flush()
        
        # Add capabilities
        for cap_name in service_data["capabilities"]:
            capability = ServiceCapability(
                service_id=service.id,
                capability_name=cap_name,
                capability_desc=f"{cap_name} capability for {service.name}"
            )
            db.add(capability)
        
        # Add retail industry association
        industry = ServiceIndustry(
            service_id=service.id,
            domain="Retail"
        )
        db.add(industry)
        
        # Add tools
        for tool_data in service_data["tools"]:
            tool = Tool(
                service_id=service.id,
                tool_name=tool_data["name"],
                tool_description=tool_data["description"],
                tool_version="1.0.0",
                is_active=True,
                input_schema={
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "status": {"type": "string"},
                        "data": {"type": "object"}
                    }
                },
                example_calls=[{
                    "description": f"Example call to {tool_data['name']}",
                    "input": {},
                    "output": {"status": "success", "data": {}}
                }],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(tool)
        
        # Add integration details
        integration = ServiceIntegrationDetails(
            service_id=service.id,
            access_protocol="REST",
            base_endpoint=service_data["endpoint"],
            auth_method="Bearer Token",
            auth_config={"type": "bearer", "header": "Authorization"},
            rate_limit_requests=2000,
            rate_limit_window_seconds=60,
            max_concurrent_requests=20,
            default_headers={"Content-Type": "application/json"},
            request_content_type="application/json",
            response_content_type="application/json",
            health_check_endpoint="/health",
            health_check_interval_seconds=300
        )
        db.add(integration)
        
        # Add agent protocol
        protocol = ServiceAgentProtocols(
            service_id=service.id,
            message_protocol="HTTP/REST",
            protocol_version="1.1",
            expected_input_format="JSON",
            response_style="structured",
            message_examples=[{
                "request": {"example": "request"},
                "response": {"example": "response"}
            }],
            tool_schema={
                "type": "object",
                "properties": {}
            }
        )
        db.add(protocol)
        
        db.commit()
        print(f"✅ Successfully added {service_data['name']}!")
        
        # Print final summary
        total_services = db.query(Service).count()
        total_tools = db.query(Tool).count()
        retail_services = db.query(Service).join(ServiceIndustry).filter(ServiceIndustry.domain == "Retail").count()
        
        print(f"\nFinal Database Statistics:")
        print(f"- Total services: {total_services}")
        print(f"- Total tools: {total_tools}")
        print(f"- Retail services: {retail_services}")
        
    except Exception as e:
        print(f"❌ Error adding service: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("Adding the 50th Retail Enterprise Service")
    print("=" * 50)
    add_final_service()
