"""
Simple seed script for initial data
"""
import psycopg2
from psycopg2.extras import Json
from datetime import datetime

# Database connection
conn = psycopg2.connect(
    database="kpath_enterprise",
    user="james",
    host="localhost"
)
cur = conn.cursor()

try:
    # Create test users
    users = [
        ("admin@kpath.local", "admin", Json({"department": "IT"})),
        ("user@kpath.local", "user", Json({"department": "Engineering"}))
    ]
    
    for email, role, attributes in users:
        cur.execute("""
            INSERT INTO users (email, role, attributes) 
            VALUES (%s, %s, %s)
            ON CONFLICT (email) DO NOTHING
        """, (email, role, attributes))
    
    # Create test services
    services = [
        {
            "name": "EmailService",
            "description": "Send and manage email communications",
            "endpoint": "https://api.internal/email/v1",
            "version": "1.0.0"
        },
        {
            "name": "CalendarService", 
            "description": "Manage calendar events and scheduling",
            "endpoint": "https://api.internal/calendar/v2",
            "version": "2.0.0"
        },
        {
            "name": "InvoiceAPI",
            "description": "Process and manage financial invoices",
            "endpoint": "https://api.internal/finance/invoice",
            "version": "3.1.0"
        }
    ]
    
    for service in services:
        # Insert service
        cur.execute("""
            INSERT INTO services (name, description, endpoint, version, status)
            VALUES (%(name)s, %(description)s, %(endpoint)s, %(version)s, 'active')
            ON CONFLICT (name) DO UPDATE SET
                description = EXCLUDED.description,
                endpoint = EXCLUDED.endpoint,
                version = EXCLUDED.version
            RETURNING id
        """, service)
        
        service_id = cur.fetchone()[0]
        
        # Add capabilities based on service
        if service["name"] == "EmailService":
            capabilities = [
                ("SendEmail", "Send an email message to one or more recipients"),
                ("CreateTemplate", "Create reusable email templates")
            ]
            domains = ["Communication", "Notification"]
        elif service["name"] == "CalendarService":
            capabilities = [
                ("CreateEvent", "Schedule a new meeting or event on the calendar"),
                ("FindAvailability", "Find available time slots for multiple participants")
            ]
            domains = ["Scheduling", "Productivity"]
        else:  # InvoiceAPI
            capabilities = [
                ("CreateInvoice", "Generate a new invoice for products or services"),
                ("ProcessPayment", "Process payment for an existing invoice")
            ]
            domains = ["Finance", "Accounting"]
        
        # Insert capabilities
        for cap_name, cap_desc in capabilities:
            cur.execute("""
                INSERT INTO service_capability (service_id, capability_name, capability_desc)
                VALUES (%s, %s, %s)
            """, (service_id, cap_name, cap_desc))
        
        # Insert domains
        for domain in domains:
            cur.execute("""
                INSERT INTO service_industry (service_id, domain)
                VALUES (%s, %s)
                ON CONFLICT (service_id, domain) DO NOTHING
            """, (service_id, domain))
    
    conn.commit()
    print("✅ Database seeded successfully!")
    
    # Display what was created
    cur.execute("SELECT COUNT(*) FROM users")
    user_count = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM services")
    service_count = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM service_capability")
    capability_count = cur.fetchone()[0]
    
    print(f"📊 Created: {user_count} users, {service_count} services, {capability_count} capabilities")
    
except Exception as e:
    print(f"❌ Error: {e}")
    conn.rollback()
finally:
    cur.close()
    conn.close()
