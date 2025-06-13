"""
Populate KPATH Enterprise database with 30 enterprise services
"""
import sys
sys.path.append('/Users/james/claude_development/kpath_enterprise')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models.models import Service, ServiceCapability, ServiceIndustry
from backend.core.config import get_settings
import json

# Get database settings
settings = get_settings()
DATABASE_URL = settings.database_url

# Create database connection
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

# Define enterprise services
enterprise_services = [
    # API ENDPOINTS (5)
    {
        "name": "CustomerDataAPI",
        "description": "Core API for accessing and managing customer master data, profiles, and preferences across the enterprise",
        "endpoint": "https://api.enterprise.com/customers/v2",
        "version": "2.3.0",
        "status": "active",
        "capabilities": [
            {"name": "retrieve_customer", "desc": "Retrieve customer profile and data by ID or email"},
            {"name": "update_customer", "desc": "Update customer information and preferences"},
            {"name": "search_customers", "desc": "Search customers by various criteria"},
            {"name": "customer_analytics", "desc": "Get customer analytics and insights"}
        ],
        "domains": ["Customer Service", "Data Management", "Analytics"]
    },
    {
        "name": "PaymentGatewayAPI",
        "description": "Enterprise payment processing API supporting multiple payment methods, currencies, and compliance standards",
        "endpoint": "https://api.enterprise.com/payments/v3",
        "version": "3.1.0",
        "status": "active",
        "capabilities": [
            {"name": "process_payment", "desc": "Process payments via credit card, ACH, wire transfer"},
            {"name": "refund_payment", "desc": "Process refunds and chargebacks"},
            {"name": "payment_status", "desc": "Check payment status and history"},
            {"name": "payment_reporting", "desc": "Generate payment reports and reconciliation"}
        ],
        "domains": ["Finance", "E-commerce", "Compliance"]
    },
    {
        "name": "InventoryManagementAPI",
        "description": "Real-time inventory tracking and management API for warehouses, stores, and distribution centers",
        "endpoint": "https://api.enterprise.com/inventory/v1",
        "version": "1.8.0",
        "status": "active",
        "capabilities": [
            {"name": "check_inventory", "desc": "Check real-time inventory levels across locations"},
            {"name": "reserve_inventory", "desc": "Reserve inventory for orders and transfers"},
            {"name": "update_inventory", "desc": "Update inventory counts and locations"},
            {"name": "inventory_forecasting", "desc": "Get inventory forecasts and recommendations"}
        ],
        "domains": ["Supply Chain", "Operations", "Retail"]
    },
    {
        "name": "AuthenticationAPI",
        "description": "Enterprise-wide authentication and authorization API with SSO, MFA, and role-based access control",
        "endpoint": "https://api.enterprise.com/auth/v4",
        "version": "4.0.0",
        "status": "active",
        "capabilities": [
            {"name": "authenticate_user", "desc": "Authenticate users with various methods (SSO, MFA)"},
            {"name": "authorize_access", "desc": "Check user permissions and roles"},
            {"name": "manage_sessions", "desc": "Create and manage user sessions"},
            {"name": "audit_access", "desc": "Audit user access and authentication events"}
        ],
        "domains": ["Security", "IT Infrastructure", "Compliance"]
    },
    {
        "name": "DocumentStorageAPI",
        "description": "Enterprise document management API for storing, retrieving, and managing business documents with versioning",
        "endpoint": "https://api.enterprise.com/documents/v2",
        "version": "2.5.0",
        "status": "active",
        "capabilities": [
            {"name": "upload_document", "desc": "Upload and store documents with metadata"},
            {"name": "retrieve_document", "desc": "Retrieve documents by ID or search criteria"},
            {"name": "version_control", "desc": "Manage document versions and history"},
            {"name": "document_search", "desc": "Full-text search across documents"}
        ],
        "domains": ["Document Management", "Compliance", "Knowledge Management"]
    },
    
    # MARKETING AGENTS (5)
    {
        "name": "CampaignOptimizationAgent",
        "description": "AI-powered agent that continuously optimizes marketing campaigns based on performance metrics and ROI",
        "endpoint": None,
        "version": "1.2.0",
        "status": "active",
        "capabilities": [
            {"name": "analyze_performance", "desc": "Analyze campaign performance metrics in real-time"},
            {"name": "optimize_targeting", "desc": "Optimize audience targeting based on conversion data"},
            {"name": "adjust_budgets", "desc": "Dynamically adjust campaign budgets for maximum ROI"},
            {"name": "predict_outcomes", "desc": "Predict campaign outcomes and recommend changes"}
        ],
        "domains": ["Marketing", "Analytics", "Automation"]
    },
    {
        "name": "ContentGenerationAgent",
        "description": "Automated content creation agent for marketing materials, social media posts, and email campaigns",
        "endpoint": None,
        "version": "2.0.0",
        "status": "active",
        "capabilities": [
            {"name": "generate_content", "desc": "Create marketing content based on brand guidelines"},
            {"name": "personalize_messages", "desc": "Personalize content for different audience segments"},
            {"name": "optimize_copy", "desc": "A/B test and optimize marketing copy"},
            {"name": "schedule_content", "desc": "Schedule content across multiple channels"}
        ],
        "domains": ["Marketing", "Content Management", "Social Media"]
    },
    {
        "name": "LeadScoringAgent",
        "description": "Machine learning agent that scores and qualifies leads based on behavior, demographics, and engagement",
        "endpoint": None,
        "version": "1.5.0",
        "status": "active",
        "capabilities": [
            {"name": "score_leads", "desc": "Calculate lead scores based on multiple factors"},
            {"name": "segment_leads", "desc": "Segment leads into qualification categories"},
            {"name": "predict_conversion", "desc": "Predict likelihood of lead conversion"},
            {"name": "route_leads", "desc": "Route qualified leads to appropriate sales teams"}
        ],
        "domains": ["Marketing", "Sales", "Analytics"]
    },
    {
        "name": "SocialMediaMonitoringAgent",
        "description": "Monitors social media channels for brand mentions, sentiment analysis, and engagement opportunities",
        "endpoint": None,
        "version": "1.8.0",
        "status": "active",
        "capabilities": [
            {"name": "monitor_mentions", "desc": "Track brand mentions across social platforms"},
            {"name": "analyze_sentiment", "desc": "Perform sentiment analysis on social conversations"},
            {"name": "identify_influencers", "desc": "Identify and track key influencers"},
            {"name": "alert_issues", "desc": "Alert on potential PR issues or opportunities"}
        ],
        "domains": ["Marketing", "Social Media", "Customer Service"]
    },
    {
        "name": "EmailMarketingAgent",
        "description": "Automated email marketing agent for campaign execution, personalization, and performance tracking",
        "endpoint": None,
        "version": "2.2.0",
        "status": "active",
        "capabilities": [
            {"name": "segment_audiences", "desc": "Create and manage email audience segments"},
            {"name": "personalize_emails", "desc": "Dynamically personalize email content"},
            {"name": "optimize_timing", "desc": "Optimize email send times for engagement"},
            {"name": "track_performance", "desc": "Track email metrics and generate reports"}
        ],
        "domains": ["Marketing", "Communications", "Analytics"]
    },
    
    # FINANCE AGENTS (6)
    {
        "name": "ExpenseApprovalAgent",
        "description": "Automated expense report processing and approval agent with policy compliance checking",
        "endpoint": None,
        "version": "1.6.0",
        "status": "active",
        "capabilities": [
            {"name": "process_expenses", "desc": "Process and validate expense reports"},
            {"name": "check_compliance", "desc": "Verify compliance with expense policies"},
            {"name": "route_approvals", "desc": "Route expenses for appropriate approvals"},
            {"name": "flag_anomalies", "desc": "Flag unusual or suspicious expenses"}
        ],
        "domains": ["Finance", "Compliance", "Operations"]
    },
    {
        "name": "InvoiceProcessingAgent",
        "description": "Intelligent agent for processing, matching, and routing invoices through the AP workflow",
        "endpoint": None,
        "version": "2.1.0",
        "status": "active",
        "capabilities": [
            {"name": "extract_data", "desc": "Extract data from invoices using OCR and AI"},
            {"name": "match_orders", "desc": "Match invoices to purchase orders and receipts"},
            {"name": "validate_invoices", "desc": "Validate invoice data and calculations"},
            {"name": "route_payment", "desc": "Route approved invoices for payment"}
        ],
        "domains": ["Finance", "Accounts Payable", "Automation"]
    },
    {
        "name": "BudgetMonitoringAgent",
        "description": "Real-time budget monitoring agent that tracks spending, forecasts overruns, and alerts stakeholders",
        "endpoint": None,
        "version": "1.4.0",
        "status": "active",
        "capabilities": [
            {"name": "track_spending", "desc": "Monitor real-time spending against budgets"},
            {"name": "forecast_budgets", "desc": "Forecast budget utilization and overruns"},
            {"name": "alert_variances", "desc": "Alert on significant budget variances"},
            {"name": "generate_reports", "desc": "Generate budget performance reports"}
        ],
        "domains": ["Finance", "Planning", "Analytics"]
    },
    {
        "name": "TaxComplianceAgent",
        "description": "Automated tax calculation, filing, and compliance agent for multiple jurisdictions",
        "endpoint": None,
        "version": "3.0.0",
        "status": "active",
        "capabilities": [
            {"name": "calculate_taxes", "desc": "Calculate taxes for various jurisdictions"},
            {"name": "prepare_filings", "desc": "Prepare tax returns and filings"},
            {"name": "track_deadlines", "desc": "Track and alert on tax deadlines"},
            {"name": "audit_compliance", "desc": "Audit transactions for tax compliance"}
        ],
        "domains": ["Finance", "Compliance", "Legal"]
    },
    {
        "name": "CashFlowForecastingAgent",
        "description": "Predictive analytics agent for cash flow forecasting and working capital optimization",
        "endpoint": None,
        "version": "1.9.0",
        "status": "active",
        "capabilities": [
            {"name": "forecast_cashflow", "desc": "Predict future cash flows based on patterns"},
            {"name": "optimize_working_capital", "desc": "Recommend working capital optimizations"},
            {"name": "scenario_analysis", "desc": "Run what-if scenarios for cash planning"},
            {"name": "alert_shortfalls", "desc": "Alert on potential cash shortfalls"}
        ],
        "domains": ["Finance", "Treasury", "Analytics"]
    },
    {
        "name": "FraudDetectionAgent",
        "description": "AI-powered fraud detection agent monitoring transactions and identifying suspicious patterns",
        "endpoint": None,
        "version": "2.5.0",
        "status": "active",
        "capabilities": [
            {"name": "monitor_transactions", "desc": "Real-time transaction monitoring and analysis"},
            {"name": "detect_anomalies", "desc": "Detect anomalous patterns and behaviors"},
            {"name": "risk_scoring", "desc": "Score transactions and entities for fraud risk"},
            {"name": "alert_security", "desc": "Alert security team on high-risk activities"}
        ],
        "domains": ["Finance", "Security", "Risk Management"]
    },    
    # BUSINESS ANALYSIS AGENTS (5)
    {
        "name": "MarketIntelligenceAgent",
        "description": "Gathers and analyzes market data, competitor information, and industry trends for strategic planning",
        "endpoint": None,
        "version": "1.7.0",
        "status": "active",
        "capabilities": [
            {"name": "track_competitors", "desc": "Monitor competitor activities and strategies"},
            {"name": "analyze_trends", "desc": "Identify and analyze market trends"},
            {"name": "forecast_market", "desc": "Forecast market conditions and opportunities"},
            {"name": "generate_insights", "desc": "Generate actionable market insights"}
        ],
        "domains": ["Business Intelligence", "Strategy", "Analytics"]
    },
    {
        "name": "PerformanceAnalyticsAgent",
        "description": "Analyzes business performance metrics, KPIs, and generates executive dashboards and reports",
        "endpoint": None,
        "version": "2.3.0",
        "status": "active",
        "capabilities": [
            {"name": "track_kpis", "desc": "Monitor and track key performance indicators"},
            {"name": "analyze_metrics", "desc": "Analyze business metrics and performance"},
            {"name": "create_dashboards", "desc": "Generate executive dashboards"},
            {"name": "identify_trends", "desc": "Identify performance trends and patterns"}
        ],
        "domains": ["Business Intelligence", "Analytics", "Reporting"]
    },
    {
        "name": "CustomerInsightsAgent",
        "description": "Analyzes customer behavior, preferences, and journey to provide actionable business insights",
        "endpoint": None,
        "version": "1.8.0",
        "status": "active",
        "capabilities": [
            {"name": "analyze_behavior", "desc": "Analyze customer behavior patterns"},
            {"name": "segment_customers", "desc": "Create customer segments and personas"},
            {"name": "predict_churn", "desc": "Predict customer churn probability"},
            {"name": "recommend_actions", "desc": "Recommend retention and growth actions"}
        ],
        "domains": ["Business Intelligence", "Customer Analytics", "Marketing"]
    },
    {
        "name": "PricingOptimizationAgent",
        "description": "Dynamic pricing agent that optimizes prices based on demand, competition, and profitability targets",
        "endpoint": None,
        "version": "1.5.0",
        "status": "active",
        "capabilities": [
            {"name": "analyze_pricing", "desc": "Analyze current pricing effectiveness"},
            {"name": "optimize_prices", "desc": "Recommend optimal pricing strategies"},
            {"name": "monitor_competition", "desc": "Monitor competitor pricing in real-time"},
            {"name": "forecast_impact", "desc": "Forecast revenue impact of price changes"}
        ],
        "domains": ["Business Intelligence", "Revenue Management", "Analytics"]
    },
    {
        "name": "ProcessMiningAgent",
        "description": "Analyzes business processes to identify bottlenecks, inefficiencies, and optimization opportunities",
        "endpoint": None,
        "version": "1.3.0",
        "status": "active",
        "capabilities": [
            {"name": "map_processes", "desc": "Automatically map business processes from logs"},
            {"name": "identify_bottlenecks", "desc": "Identify process bottlenecks and delays"},
            {"name": "recommend_improvements", "desc": "Recommend process optimizations"},
            {"name": "measure_efficiency", "desc": "Measure process efficiency and compliance"}
        ],
        "domains": ["Business Intelligence", "Operations", "Process Improvement"]
    },
    
    # DATA PROCESSING AGENTS (5)
    {
        "name": "DataQualityAgent",
        "description": "Monitors and improves data quality across enterprise systems through validation, cleansing, and enrichment",
        "endpoint": None,
        "version": "2.0.0",
        "status": "active",
        "capabilities": [
            {"name": "validate_data", "desc": "Validate data against quality rules"},
            {"name": "cleanse_data", "desc": "Clean and standardize data"},
            {"name": "enrich_data", "desc": "Enrich data with external sources"},
            {"name": "monitor_quality", "desc": "Monitor data quality metrics"}
        ],
        "domains": ["Data Management", "Quality Assurance", "Analytics"]
    },
    {
        "name": "ETLOrchestrationAgent",
        "description": "Orchestrates complex ETL/ELT pipelines for data integration across multiple systems and formats",
        "endpoint": None,
        "version": "3.1.0",
        "status": "active",
        "capabilities": [
            {"name": "schedule_pipelines", "desc": "Schedule and manage ETL pipelines"},
            {"name": "transform_data", "desc": "Transform data between formats and schemas"},
            {"name": "monitor_jobs", "desc": "Monitor ETL job execution and performance"},
            {"name": "handle_errors", "desc": "Handle errors and retry failed jobs"}
        ],
        "domains": ["Data Management", "Integration", "Automation"]
    },
    {
        "name": "DataArchivingAgent",
        "description": "Manages data lifecycle, archiving, and retention policies across enterprise data stores",
        "endpoint": None,
        "version": "1.6.0",
        "status": "active",
        "capabilities": [
            {"name": "archive_data", "desc": "Archive data based on retention policies"},
            {"name": "compress_storage", "desc": "Compress and optimize storage usage"},
            {"name": "manage_lifecycle", "desc": "Manage data lifecycle and retention"},
            {"name": "restore_data", "desc": "Restore archived data on demand"}
        ],
        "domains": ["Data Management", "Storage", "Compliance"]
    },
    {
        "name": "RealtimeStreamProcessorAgent",
        "description": "Processes real-time data streams for analytics, alerting, and event-driven architectures",
        "endpoint": None,
        "version": "2.2.0",
        "status": "active",
        "capabilities": [
            {"name": "process_streams", "desc": "Process real-time data streams"},
            {"name": "detect_events", "desc": "Detect patterns and events in streams"},
            {"name": "aggregate_metrics", "desc": "Aggregate streaming metrics in real-time"},
            {"name": "trigger_actions", "desc": "Trigger actions based on stream events"}
        ],
        "domains": ["Data Management", "Real-time Analytics", "Event Processing"]
    },
    {
        "name": "DataCatalogAgent",
        "description": "Maintains enterprise data catalog with metadata, lineage, and discovery capabilities",
        "endpoint": None,
        "version": "1.9.0",
        "status": "active",
        "capabilities": [
            {"name": "catalog_assets", "desc": "Catalog data assets and metadata"},
            {"name": "track_lineage", "desc": "Track data lineage and dependencies"},
            {"name": "enable_discovery", "desc": "Enable data discovery and search"},
            {"name": "manage_glossary", "desc": "Manage business glossary and definitions"}
        ],
        "domains": ["Data Management", "Governance", "Discovery"]
    },
    
    # HR/OPERATIONS AGENTS (4)
    {
        "name": "RecruitmentAutomationAgent",
        "description": "Automates recruitment processes including resume screening, candidate matching, and interview scheduling",
        "endpoint": None,
        "version": "1.7.0",
        "status": "active",
        "capabilities": [
            {"name": "screen_resumes", "desc": "Screen and rank resumes using AI"},
            {"name": "match_candidates", "desc": "Match candidates to job requirements"},
            {"name": "schedule_interviews", "desc": "Coordinate and schedule interviews"},
            {"name": "track_pipeline", "desc": "Track recruitment pipeline and metrics"}
        ],
        "domains": ["Human Resources", "Recruitment", "Automation"]
    },
    {
        "name": "EmployeeOnboardingAgent",
        "description": "Manages employee onboarding workflows, documentation, and task assignments for new hires",
        "endpoint": None,
        "version": "1.4.0",
        "status": "active",
        "capabilities": [
            {"name": "create_accounts", "desc": "Create accounts and provision access"},
            {"name": "assign_tasks", "desc": "Assign onboarding tasks and training"},
            {"name": "track_progress", "desc": "Track onboarding progress and completion"},
            {"name": "collect_documents", "desc": "Collect and verify required documents"}
        ],
        "domains": ["Human Resources", "Operations", "Compliance"]
    },
    {
        "name": "FacilityManagementAgent",
        "description": "Manages facility operations including space allocation, maintenance scheduling, and resource optimization",
        "endpoint": None,
        "version": "1.8.0",
        "status": "active",
        "capabilities": [
            {"name": "manage_space", "desc": "Optimize space allocation and usage"},
            {"name": "schedule_maintenance", "desc": "Schedule preventive maintenance"},
            {"name": "track_assets", "desc": "Track facility assets and equipment"},
            {"name": "handle_requests", "desc": "Process facility service requests"}
        ],
        "domains": ["Operations", "Facilities", "Asset Management"]
    },
    {
        "name": "ComplianceMonitoringAgent",
        "description": "Monitors regulatory compliance, tracks policy adherence, and manages audit preparations",
        "endpoint": None,
        "version": "2.1.0",
        "status": "active",
        "capabilities": [
            {"name": "monitor_compliance", "desc": "Monitor compliance with regulations"},
            {"name": "track_policies", "desc": "Track policy adherence and violations"},
            {"name": "prepare_audits", "desc": "Prepare documentation for audits"},
            {"name": "assess_risks", "desc": "Assess compliance risks and gaps"}
        ],
        "domains": ["Compliance", "Risk Management", "Legal"]
    }
]

def clear_existing_data():
    """Clear existing service data"""
    print("Clearing existing service data...")
    
    # Delete in correct order due to foreign keys
    db.query(ServiceCapability).delete()
    db.query(ServiceIndustry).delete()
    db.query(Service).delete()
    db.commit()
    
    print("Existing data cleared.")

def populate_services():
    """Populate database with enterprise services"""
    print(f"Starting to populate {len(enterprise_services)} enterprise services...")
    
    for service_data in enterprise_services:
        # Create service
        service = Service(
            name=service_data["name"],
            description=service_data["description"],
            endpoint=service_data.get("endpoint"),
            version=service_data["version"],
            status=service_data["status"]
        )
        db.add(service)
        db.flush()  # Get the service ID
        
        # Add capabilities
        for cap in service_data["capabilities"]:
            capability = ServiceCapability(
                service_id=service.id,
                capability_name=cap["name"],
                capability_desc=cap["desc"],
                input_schema={},  # Can be enhanced later
                output_schema={}  # Can be enhanced later
            )
            db.add(capability)
        
        # Add domains/industries
        for domain in service_data["domains"]:
            industry = ServiceIndustry(
                service_id=service.id,
                domain=domain
            )
            db.add(industry)
        
        print(f"Added: {service.name} ({len(service_data['capabilities'])} capabilities, {len(service_data['domains'])} domains)")
    
    db.commit()
    print("All services populated successfully!")

def verify_population():
    """Verify the population results"""
    total_services = db.query(Service).count()
    api_services = db.query(Service).filter(Service.endpoint.isnot(None)).count()
    agent_services = db.query(Service).filter(Service.endpoint.is_(None)).count()
    
    print(f"\nVerification Results:")
    print(f"Total Services: {total_services}")
    print(f"API Endpoints: {api_services}")
    print(f"Agent Services: {agent_services}")
    
    # Count by domain
    from sqlalchemy import func
    domain_counts = db.query(
        ServiceIndustry.domain,
        func.count(ServiceIndustry.service_id).label('count')
    ).group_by(ServiceIndustry.domain).order_by('count').all()
    
    print(f"\nServices by Domain:")
    for domain, count in domain_counts:
        print(f"  {domain}: {count}")

if __name__ == "__main__":
    try:
        clear_existing_data()
        populate_services()
        verify_population()
        
        print("\nDatabase population completed successfully!")
        print("The search index will need to be rebuilt to include the new services.")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()
