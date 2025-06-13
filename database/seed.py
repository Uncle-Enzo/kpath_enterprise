"""
Seed database with test data
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from sqlalchemy.orm import Session
from backend.core.database import SessionLocal, engine
from backend.models import (
    Service, ServiceCapability, ServiceIndustry, 
    User, InteractionCapability
)

def seed_database():
    """Populate database with test data"""
    db = SessionLocal()
    
    try:
        # Create test users
        admin_user = User(
            email="admin@kpath.local",
            role="admin",
            attributes={"department": "IT"}
        )
        
        test_user = User(
            email="user@kpath.local", 
            role="user",
            attributes={"department": "Engineering"}
        )
        
        db.add_all([admin_user, test_user])
        db.commit()
        
        # Create test services
        services_data = [
            {
                "name": "EmailService",
                "description": "Send and manage email communications",
                "endpoint": "https://api.internal/email/v1",
                "version": "1.0.0",
                "capabilities": [
                    {
                        "capability_name": "SendEmail",
                        "capability_desc": "Send an email message to one or more recipients"
                    },
                    {
                        "capability_name": "CreateTemplate", 
                        "capability_desc": "Create reusable email templates"
                    }
                ],
                "domains": ["Communication", "Notification"],
                "interaction_type": "async"
            },
            {
                "name": "CalendarService",
                "description": "Manage calendar events and scheduling",
                "endpoint": "https://api.internal/calendar/v2", 
                "version": "2.0.0",
                "capabilities": [
                    {
                        "capability_name": "CreateEvent",
                        "capability_desc": "Schedule a new meeting or event on the calendar"
                    },
                    {
                        "capability_name": "FindAvailability",
                        "capability_desc": "Find available time slots for multiple participants"
                    }
                ],
                "domains": ["Scheduling", "Productivity"],
                "interaction_type": "sync"
            },
            {
                "name": "InvoiceAPI",
                "description": "Process and manage financial invoices",
                "endpoint": "https://api.internal/finance/invoice",
                "version": "3.1.0", 
                "capabilities": [
                    {
                        "capability_name": "CreateInvoice",
                        "capability_desc": "Generate a new invoice for products or services"
                    },
                    {
                        "capability_name": "ProcessPayment",
                        "capability_desc": "Process payment for an existing invoice"
                    }
                ],
                "domains": ["Finance", "Accounting"],
                "interaction_type": "sync"
            }
        ]
        
        for service_data in services_data:
            # Create service
            service = Service(
                name=service_data["name"],
                description=service_data["description"],
                endpoint=service_data["endpoint"],
                version=service_data["version"],
                status="active"
            )
            db.add(service)
            db.flush()
            
            # Add capabilities
            for cap in service_data["capabilities"]:
                capability = ServiceCapability(
                    service_id=service.id,
                    capability_name=cap["capability_name"],
                    capability_desc=cap["capability_desc"]
                )
                db.add(capability)
            
            # Add domains
            for domain in service_data["domains"]:
                industry = ServiceIndustry(
                    service_id=service.id,
                    domain=domain
                )
                db.add(industry)
            
            # Add interaction type
            interaction = InteractionCapability(
                service_id=service.id,
                interaction_desc=f"{service_data['interaction_type']} interaction pattern",
                interaction_type=service_data["interaction_type"]
            )
            db.add(interaction)
        
        db.commit()
        print("✅ Database seeded successfully!")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
