"""
Populate sample services for testing
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.database import SessionLocal
from backend.services.service_crud import ServiceCRUD
from backend.schemas import ServiceCreate
from backend.models import Service

def create_sample_services():
    """Create sample services for testing"""
    db = SessionLocal()
    
    sample_services = [
        {
            "name": "Sales Analytics Service",
            "description": "Provides comprehensive sales data analysis, reporting, and visualization capabilities",
            "endpoint": "https://api.kpath.ai/sales-analytics",
            "version": "2.1.0",
            "status": "active",
            "capabilities": [
                {
                    "capability_name": "Sales Report Generation",
                    "capability_desc": "Generate detailed sales reports with custom date ranges and filters"
                },
                {
                    "capability_name": "Revenue Analysis",
                    "capability_desc": "Analyze revenue trends, forecasts, and performance metrics"
                }
            ],
            "domains": ["sales", "analytics", "reporting"]
        },
        {
            "name": "Customer Data Platform",
            "description": "Unified customer data management and insights platform for 360-degree customer view",
            "endpoint": "https://api.kpath.ai/customer-platform",
            "version": "3.0.2",
            "status": "active",
            "capabilities": [
                {
                    "capability_name": "Customer Profile Management",
                    "capability_desc": "Create and manage comprehensive customer profiles"
                },
                {
                    "capability_name": "Segmentation Engine",
                    "capability_desc": "Advanced customer segmentation based on behavior and demographics"
                }
            ],
            "domains": ["customer", "marketing", "data"]
        },
        {
            "name": "Inventory Management System",
            "description": "Real-time inventory tracking, optimization, and forecasting service",
            "endpoint": "https://api.kpath.ai/inventory",
            "version": "1.8.5",
            "status": "active",
            "capabilities": [
                {
                    "capability_name": "Stock Level Monitoring",
                    "capability_desc": "Real-time monitoring of inventory levels across warehouses"
                },
                {
                    "capability_name": "Reorder Prediction",
                    "capability_desc": "ML-based prediction for optimal reorder points"
                }
            ],
            "domains": ["inventory", "warehouse", "logistics"]
        },
        {
            "name": "Financial Reporting Engine",
            "description": "Automated financial reporting and compliance documentation generator",
            "endpoint": "https://api.kpath.ai/finance-reports",
            "version": "4.2.0",
            "status": "active",
            "capabilities": [
                {
                    "capability_name": "P&L Statement Generation",
                    "capability_desc": "Generate profit and loss statements with drill-down capabilities"
                },
                {
                    "capability_name": "Tax Compliance Reports",
                    "capability_desc": "Automated tax reporting for multiple jurisdictions"
                }
            ],
            "domains": ["finance", "accounting", "compliance"]
        },
        {
            "name": "HR Analytics Dashboard",
            "description": "Human resources analytics and employee performance tracking system",
            "endpoint": "https://api.kpath.ai/hr-analytics",
            "version": "2.5.1",
            "status": "active",
            "capabilities": [
                {
                    "capability_name": "Employee Performance Tracking",
                    "capability_desc": "Track and analyze employee performance metrics"
                },
                {
                    "capability_name": "Retention Analysis",
                    "capability_desc": "Predictive analytics for employee retention risk"
                }
            ],
            "domains": ["hr", "analytics", "workforce"]
        }
    ]
    
    try:
        created_count = 0
        for service_data in sample_services:
            # Check if service already exists
            existing = db.query(Service).filter(
                Service.name == service_data["name"]
            ).first()
            
            if not existing:
                # Create the service first
                service = ServiceCRUD.create_service(
                    db,
                    name=service_data["name"],
                    description=service_data["description"],
                    endpoint=service_data.get("endpoint"),
                    version=service_data.get("version"),
                    status=service_data.get("status", "active")
                )
                
                # Add capabilities
                for cap in service_data.get("capabilities", []):
                    ServiceCRUD.add_capability(
                        db,
                        service.id,
                        cap["capability_name"],
                        cap["capability_desc"],
                        cap.get("input_schema"),
                        cap.get("output_schema")
                    )
                
                # Add domains/industries
                # TODO: Implement add_industry method
                # for domain in service_data.get("domains", []):
                #     ServiceCRUD.add_industry(db, service.id, domain)
                
                created_count += 1
                print(f"✅ Created service: {service.name}")
            else:
                print(f"⚠️  Service already exists: {service_data['name']}")
        
        print(f"\n✅ Created {created_count} new services")
        print("🔍 You can now test the search functionality!")
        
    except Exception as e:
        print(f"❌ Error creating services: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_services()
