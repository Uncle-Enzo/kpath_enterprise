#!/usr/bin/env python3
"""
Script to add 50 typical enterprise retail API services to KPATH Enterprise.
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List

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

def create_retail_services():
    """Create 50 typical enterprise retail API services."""
    
    services_data = [
        {
            "name": "AdvancedInventoryAPI",
            "version": "3.2.0",
            "description": "Real-time inventory tracking and management across all channels",
            "endpoint": "https://api.enterprise.com/inventory/v3",
            "capabilities": ["Inventory Tracking", "Stock Management", "Warehouse Management"],
            "tools": [
                {"name": "check_stock_levels", "description": "Check current stock levels by SKU or location"},
                {"name": "update_inventory", "description": "Update inventory quantities"},
                {"name": "reserve_inventory", "description": "Reserve inventory for orders"},
                {"name": "transfer_inventory", "description": "Transfer inventory between locations"},
                {"name": "get_low_stock_alerts", "description": "Get items below reorder threshold"}
            ]
        },
        {
            "name": "POSIntegrationAPI",
            "version": "5.1.0",
            "description": "Point of Sale system integration for retail stores",
            "endpoint": "https://api.enterprise.com/pos/v5",
            "capabilities": ["Transaction Processing", "Receipt Management", "Cashier Management"],
            "tools": [
                {"name": "process_transaction", "description": "Process a POS transaction"},
                {"name": "void_transaction", "description": "Void a completed transaction"},
                {"name": "generate_receipt", "description": "Generate digital or print receipts"},
                {"name": "open_cash_drawer", "description": "Trigger cash drawer opening"},
                {"name": "end_of_day_report", "description": "Generate daily sales reports"}
            ]
        },
        {
            "name": "CustomerLoyaltyAPI",
            "version": "2.8.0",
            "description": "Customer loyalty program management and rewards",
            "endpoint": "https://api.enterprise.com/loyalty/v2",
            "capabilities": ["Loyalty Programs", "Rewards Management", "Points Tracking"],
            "tools": [
                {"name": "add_loyalty_points", "description": "Add points to customer account"},
                {"name": "redeem_rewards", "description": "Redeem loyalty rewards"},
                {"name": "check_points_balance", "description": "Check customer points balance"},
                {"name": "get_tier_status", "description": "Get customer loyalty tier status"},
                {"name": "issue_reward_voucher", "description": "Issue reward vouchers"}
            ]
        },
        {
            "name": "PricingEngineAPI",
            "version": "4.0.0",
            "description": "Dynamic pricing and promotion management",
            "endpoint": "https://api.enterprise.com/pricing/v4",
            "capabilities": ["Dynamic Pricing", "Promotion Management", "Price Optimization"],
            "tools": [
                {"name": "calculate_price", "description": "Calculate item price with promotions"},
                {"name": "create_promotion", "description": "Create new promotional campaigns"},
                {"name": "apply_discount", "description": "Apply discounts to items"},
                {"name": "get_competitor_pricing", "description": "Get competitor price comparisons"},
                {"name": "optimize_pricing", "description": "AI-driven price optimization"}
            ]
        },
        {
            "name": "OrderManagementAPI",
            "version": "3.5.0",
            "description": "Omnichannel order management and fulfillment",
            "endpoint": "https://api.enterprise.com/orders/v3",
            "capabilities": ["Order Processing", "Order Tracking", "Fulfillment Management"],
            "tools": [
                {"name": "create_order", "description": "Create new customer order"},
                {"name": "update_order_status", "description": "Update order fulfillment status"},
                {"name": "track_order", "description": "Track order location and status"},
                {"name": "cancel_order", "description": "Cancel customer order"},
                {"name": "split_order", "description": "Split order for multiple fulfillments"}
            ]
        }
    ]
    
    # Continue with more services...
    services_data.extend([
        {
            "name": "ProductCatalogAPI",
            "version": "2.4.0",
            "description": "Product information management and catalog services",
            "endpoint": "https://api.enterprise.com/catalog/v2",
            "capabilities": ["Product Management", "Catalog Search", "Category Management"],
            "tools": [
                {"name": "search_products", "description": "Search product catalog"},
                {"name": "get_product_details", "description": "Get detailed product information"},
                {"name": "update_product", "description": "Update product attributes"},
                {"name": "manage_categories", "description": "Manage product categories"},
                {"name": "bulk_import_products", "description": "Bulk import product data"}
            ]
        },
        {
            "name": "ShippingOptimizationAPI",
            "version": "3.1.0",
            "description": "Shipping rate calculation and carrier management",
            "endpoint": "https://api.enterprise.com/shipping/v3",
            "capabilities": ["Rate Shopping", "Label Generation", "Tracking Integration"],
            "tools": [
                {"name": "calculate_shipping_rates", "description": "Get shipping rates from carriers"},
                {"name": "generate_shipping_label", "description": "Generate shipping labels"},
                {"name": "track_shipment", "description": "Track shipment status"},
                {"name": "schedule_pickup", "description": "Schedule carrier pickups"},
                {"name": "validate_address", "description": "Validate shipping addresses"}
            ]
        },
        {
            "name": "ReturnManagementAPI",
            "version": "2.2.0",
            "description": "Returns processing and reverse logistics",
            "endpoint": "https://api.enterprise.com/returns/v2",
            "capabilities": ["Return Processing", "RMA Management", "Refund Processing"],
            "tools": [
                {"name": "initiate_return", "description": "Start return process"},
                {"name": "generate_rma", "description": "Generate return authorization"},
                {"name": "process_refund", "description": "Process customer refunds"},
                {"name": "track_return", "description": "Track return shipment"},
                {"name": "inspect_return", "description": "Log return inspection results"}
            ]
        },
        {
            "name": "SupplierIntegrationAPI",
            "version": "2.7.0",
            "description": "Supplier and vendor management integration",
            "endpoint": "https://api.enterprise.com/suppliers/v2",
            "capabilities": ["Vendor Management", "Purchase Orders", "EDI Integration"],
            "tools": [
                {"name": "create_purchase_order", "description": "Create supplier purchase orders"},
                {"name": "check_supplier_inventory", "description": "Check supplier stock levels"},
                {"name": "submit_edi_order", "description": "Submit EDI formatted orders"},
                {"name": "track_po_status", "description": "Track purchase order status"},
                {"name": "manage_vendor_catalog", "description": "Update vendor product catalogs"}
            ]
        },
        {
            "name": "StoreLocatorAPI",
            "version": "1.8.0",
            "description": "Store location and availability services",
            "endpoint": "https://api.enterprise.com/stores/v1",
            "capabilities": ["Store Locator", "Inventory Lookup", "Store Information"],
            "tools": [
                {"name": "find_nearby_stores", "description": "Find stores by location"},
                {"name": "check_store_inventory", "description": "Check product availability in store"},
                {"name": "get_store_hours", "description": "Get store operating hours"},
                {"name": "reserve_for_pickup", "description": "Reserve items for store pickup"},
                {"name": "get_store_services", "description": "Get available store services"}
            ]
        }
    ])
    
    # Add more retail services
    services_data.extend([
        {
            "name": "MarketingAutomationAPI",
            "version": "3.3.0",
            "description": "Marketing campaign automation and management",
            "endpoint": "https://api.enterprise.com/marketing/v3",
            "capabilities": ["Campaign Management", "Email Marketing", "Customer Segmentation"],
            "tools": [
                {"name": "create_campaign", "description": "Create marketing campaigns"},
                {"name": "send_email_campaign", "description": "Send targeted email campaigns"},
                {"name": "segment_customers", "description": "Create customer segments"},
                {"name": "track_campaign_metrics", "description": "Track campaign performance"},
                {"name": "personalize_content", "description": "Generate personalized content"}
            ]
        },
        {
            "name": "CustomerReviewsAPI",
            "version": "2.1.0",
            "description": "Product reviews and ratings management",
            "endpoint": "https://api.enterprise.com/reviews/v2",
            "capabilities": ["Review Management", "Rating Analytics", "Moderation"],
            "tools": [
                {"name": "submit_review", "description": "Submit product review"},
                {"name": "moderate_review", "description": "Moderate review content"},
                {"name": "get_product_ratings", "description": "Get product rating analytics"},
                {"name": "respond_to_review", "description": "Respond to customer reviews"},
                {"name": "flag_inappropriate", "description": "Flag inappropriate content"}
            ]
        },
        {
            "name": "GiftCardAPI",
            "version": "2.5.0",
            "description": "Gift card issuance and management",
            "endpoint": "https://api.enterprise.com/giftcards/v2",
            "capabilities": ["Gift Card Issuance", "Balance Management", "Redemption"],
            "tools": [
                {"name": "issue_gift_card", "description": "Issue new gift cards"},
                {"name": "check_balance", "description": "Check gift card balance"},
                {"name": "redeem_gift_card", "description": "Redeem gift card value"},
                {"name": "transfer_balance", "description": "Transfer balance between cards"},
                {"name": "bulk_activate", "description": "Bulk activate gift cards"}
            ]
        },
        {
            "name": "FraudDetectionAPI",
            "version": "4.2.0",
            "description": "Real-time fraud detection and prevention",
            "endpoint": "https://api.enterprise.com/fraud/v4",
            "capabilities": ["Fraud Detection", "Risk Scoring", "Transaction Monitoring"],
            "tools": [
                {"name": "analyze_transaction", "description": "Analyze transaction for fraud"},
                {"name": "calculate_risk_score", "description": "Calculate fraud risk score"},
                {"name": "flag_suspicious_activity", "description": "Flag suspicious activities"},
                {"name": "verify_identity", "description": "Verify customer identity"},
                {"name": "block_fraudulent_card", "description": "Block compromised cards"}
            ]
        },
        {
            "name": "WorkforceManagementAPI",
            "version": "3.0.0",
            "description": "Employee scheduling and workforce optimization",
            "endpoint": "https://api.enterprise.com/workforce/v3",
            "capabilities": ["Staff Scheduling", "Time Tracking", "Labor Analytics"],
            "tools": [
                {"name": "create_schedule", "description": "Create employee schedules"},
                {"name": "track_attendance", "description": "Track employee attendance"},
                {"name": "calculate_labor_costs", "description": "Calculate labor costs"},
                {"name": "manage_shifts", "description": "Manage shift assignments"},
                {"name": "forecast_staffing_needs", "description": "Forecast staffing requirements"}
            ]
        }
    ])
    
    # Add even more services to reach 50
    services_data.extend([
        {
            "name": "SubscriptionManagementAPI",
            "version": "2.3.0",
            "description": "Subscription service management and billing",
            "endpoint": "https://api.enterprise.com/subscriptions/v2",
            "capabilities": ["Subscription Management", "Recurring Billing", "Plan Management"],
            "tools": [
                {"name": "create_subscription", "description": "Create new subscriptions"},
                {"name": "manage_billing_cycle", "description": "Manage billing cycles"},
                {"name": "update_subscription_plan", "description": "Change subscription plans"},
                {"name": "pause_subscription", "description": "Pause active subscriptions"},
                {"name": "generate_invoices", "description": "Generate subscription invoices"}
            ]
        },
        {
            "name": "ProductRecommendationAPI",
            "version": "3.1.0",
            "description": "AI-powered product recommendations",
            "endpoint": "https://api.enterprise.com/recommendations/v3",
            "capabilities": ["Personalized Recommendations", "Cross-selling", "Upselling"],
            "tools": [
                {"name": "get_recommendations", "description": "Get personalized product recommendations"},
                {"name": "analyze_purchase_history", "description": "Analyze customer purchase patterns"},
                {"name": "suggest_complementary_items", "description": "Suggest complementary products"},
                {"name": "trending_products", "description": "Get trending product recommendations"},
                {"name": "collaborative_filtering", "description": "Apply collaborative filtering"}
            ]
        },
        {
            "name": "DigitalAssetManagementAPI",
            "version": "2.6.0",
            "description": "Digital asset storage and management",
            "endpoint": "https://api.enterprise.com/dam/v2",
            "capabilities": ["Asset Storage", "Image Processing", "Metadata Management"],
            "tools": [
                {"name": "upload_asset", "description": "Upload digital assets"},
                {"name": "resize_image", "description": "Resize and optimize images"},
                {"name": "generate_thumbnails", "description": "Generate asset thumbnails"},
                {"name": "tag_assets", "description": "Add metadata tags to assets"},
                {"name": "search_assets", "description": "Search digital asset library"}
            ]
        },
        {
            "name": "TaxCalculationAPI",
            "version": "3.4.0",
            "description": "Sales tax calculation and compliance",
            "endpoint": "https://api.enterprise.com/tax/v3",
            "capabilities": ["Tax Calculation", "Compliance Reporting", "Nexus Management"],
            "tools": [
                {"name": "calculate_sales_tax", "description": "Calculate sales tax for transactions"},
                {"name": "validate_tax_exemption", "description": "Validate tax exemption certificates"},
                {"name": "generate_tax_reports", "description": "Generate tax compliance reports"},
                {"name": "update_tax_rates", "description": "Update tax rate tables"},
                {"name": "audit_tax_transactions", "description": "Audit tax calculations"}
            ]
        },
        {
            "name": "CustomerServiceChatAPI",
            "version": "2.9.0",
            "description": "Customer service chat and messaging platform",
            "endpoint": "https://api.enterprise.com/chat/v2",
            "capabilities": ["Live Chat", "Chatbot Integration", "Ticket Management"],
            "tools": [
                {"name": "initiate_chat", "description": "Start customer chat session"},
                {"name": "route_to_agent", "description": "Route chat to human agent"},
                {"name": "send_automated_response", "description": "Send bot responses"},
                {"name": "create_support_ticket", "description": "Create support tickets from chat"},
                {"name": "analyze_sentiment", "description": "Analyze customer sentiment"}
            ]
        }
    ])
    
    # Continue adding more services...
    services_data.extend([
        {
            "name": "MobileAppAPI",
            "version": "4.1.0",
            "description": "Mobile application backend services",
            "endpoint": "https://api.enterprise.com/mobile/v4",
            "capabilities": ["Push Notifications", "App Analytics", "Deep Linking"],
            "tools": [
                {"name": "send_push_notification", "description": "Send push notifications"},
                {"name": "track_app_events", "description": "Track mobile app events"},
                {"name": "manage_deep_links", "description": "Manage app deep links"},
                {"name": "sync_offline_data", "description": "Sync offline mobile data"},
                {"name": "get_app_analytics", "description": "Get mobile app analytics"}
            ]
        },
        {
            "name": "SocialMediaIntegrationAPI",
            "version": "2.7.0",
            "description": "Social media platform integration",
            "endpoint": "https://api.enterprise.com/social/v2",
            "capabilities": ["Social Posting", "Social Commerce", "Influencer Management"],
            "tools": [
                {"name": "post_to_social", "description": "Post content to social platforms"},
                {"name": "sync_social_catalog", "description": "Sync product catalog to social"},
                {"name": "track_social_metrics", "description": "Track social media metrics"},
                {"name": "manage_influencers", "description": "Manage influencer relationships"},
                {"name": "social_listening", "description": "Monitor brand mentions"}
            ]
        },
        {
            "name": "VirtualTryOnAPI",
            "version": "1.5.0",
            "description": "AR/VR virtual product try-on services",
            "endpoint": "https://api.enterprise.com/virtual-tryon/v1",
            "capabilities": ["AR Try-On", "Size Recommendation", "3D Modeling"],
            "tools": [
                {"name": "render_ar_model", "description": "Render AR product models"},
                {"name": "capture_measurements", "description": "Capture customer measurements"},
                {"name": "recommend_size", "description": "Recommend product sizes"},
                {"name": "generate_3d_view", "description": "Generate 3D product views"},
                {"name": "save_virtual_outfit", "description": "Save virtual outfit combinations"}
            ]
        },
        {
            "name": "StoreAnalyticsAPI",
            "version": "3.2.0",
            "description": "In-store analytics and heat mapping",
            "endpoint": "https://api.enterprise.com/store-analytics/v3",
            "capabilities": ["Foot Traffic Analysis", "Heat Mapping", "Conversion Tracking"],
            "tools": [
                {"name": "track_foot_traffic", "description": "Track store foot traffic"},
                {"name": "generate_heat_map", "description": "Generate store heat maps"},
                {"name": "analyze_dwell_time", "description": "Analyze customer dwell time"},
                {"name": "calculate_conversion_rate", "description": "Calculate in-store conversion"},
                {"name": "optimize_store_layout", "description": "Suggest layout optimizations"}
            ]
        },
        {
            "name": "B2BCommerceAPI",
            "version": "2.8.0",
            "description": "Business-to-business commerce platform",
            "endpoint": "https://api.enterprise.com/b2b/v2",
            "capabilities": ["Quote Management", "Contract Pricing", "Bulk Orders"],
            "tools": [
                {"name": "create_quote", "description": "Create B2B quotes"},
                {"name": "manage_contracts", "description": "Manage B2B contracts"},
                {"name": "process_bulk_order", "description": "Process bulk orders"},
                {"name": "set_tiered_pricing", "description": "Set volume-based pricing"},
                {"name": "manage_credit_terms", "description": "Manage customer credit terms"}
            ]
        }
    ])
    
    # Add final set of services to reach 50
    services_data.extend([
        {
            "name": "ContentManagementAPI",
            "version": "3.5.0",
            "description": "Content management and publishing system",
            "endpoint": "https://api.enterprise.com/cms/v3",
            "capabilities": ["Content Publishing", "Version Control", "Workflow Management"],
            "tools": [
                {"name": "publish_content", "description": "Publish content to channels"},
                {"name": "manage_versions", "description": "Manage content versions"},
                {"name": "approve_content", "description": "Content approval workflow"},
                {"name": "schedule_publishing", "description": "Schedule content publishing"},
                {"name": "translate_content", "description": "Translate content to languages"}
            ]
        },
        {
            "name": "EventManagementAPI",
            "version": "2.3.0",
            "description": "In-store and virtual event management",
            "endpoint": "https://api.enterprise.com/events/v2",
            "capabilities": ["Event Creation", "Registration Management", "Virtual Events"],
            "tools": [
                {"name": "create_event", "description": "Create retail events"},
                {"name": "manage_registrations", "description": "Manage event registrations"},
                {"name": "stream_virtual_event", "description": "Stream virtual shopping events"},
                {"name": "track_attendance", "description": "Track event attendance"},
                {"name": "send_event_reminders", "description": "Send event reminders"}
            ]
        },
        {
            "name": "StyleAdvisorAPI",
            "version": "1.9.0",
            "description": "AI-powered style and fashion advice",
            "endpoint": "https://api.enterprise.com/style-advisor/v1",
            "capabilities": ["Style Recommendations", "Outfit Building", "Trend Analysis"],
            "tools": [
                {"name": "get_style_profile", "description": "Create customer style profile"},
                {"name": "build_outfit", "description": "Build complete outfits"},
                {"name": "analyze_trends", "description": "Analyze fashion trends"},
                {"name": "match_colors", "description": "Match colors and patterns"},
                {"name": "suggest_alternatives", "description": "Suggest style alternatives"}
            ]
        },
        {
            "name": "WarrantyManagementAPI",
            "version": "2.4.0",
            "description": "Product warranty and service plan management",
            "endpoint": "https://api.enterprise.com/warranty/v2",
            "capabilities": ["Warranty Registration", "Claims Processing", "Service Plans"],
            "tools": [
                {"name": "register_warranty", "description": "Register product warranties"},
                {"name": "file_warranty_claim", "description": "File warranty claims"},
                {"name": "check_warranty_status", "description": "Check warranty status"},
                {"name": "sell_service_plan", "description": "Sell extended service plans"},
                {"name": "schedule_service", "description": "Schedule warranty service"}
            ]
        },
        {
            "name": "CompetitorAnalysisAPI",
            "version": "2.1.0",
            "description": "Competitive intelligence and market analysis",
            "endpoint": "https://api.enterprise.com/competitor-analysis/v2",
            "capabilities": ["Price Monitoring", "Market Analysis", "Trend Tracking"],
            "tools": [
                {"name": "monitor_competitor_prices", "description": "Monitor competitor pricing"},
                {"name": "analyze_market_share", "description": "Analyze market share data"},
                {"name": "track_product_launches", "description": "Track competitor products"},
                {"name": "compare_promotions", "description": "Compare promotional strategies"},
                {"name": "generate_insights", "description": "Generate competitive insights"}
            ]
        }
    ])
    
    # Add remaining services to reach 50
    services_data.extend([
        {
            "name": "CustomerDataPlatformAPI",
            "version": "3.6.0",
            "description": "Unified customer data platform and CDP",
            "endpoint": "https://api.enterprise.com/cdp/v3",
            "capabilities": ["Data Unification", "Identity Resolution", "Audience Building"],
            "tools": [
                {"name": "unify_customer_data", "description": "Unify customer data sources"},
                {"name": "resolve_identity", "description": "Resolve customer identities"},
                {"name": "build_audience", "description": "Build customer audiences"},
                {"name": "export_segments", "description": "Export customer segments"},
                {"name": "calculate_ltv", "description": "Calculate customer lifetime value"}
            ]
        },
        {
            "name": "FinancialReportingAPI",
            "version": "2.9.0",
            "description": "Financial reporting and analytics",
            "endpoint": "https://api.enterprise.com/finance/v2",
            "capabilities": ["Financial Reports", "Revenue Analytics", "Forecasting"],
            "tools": [
                {"name": "generate_p_and_l", "description": "Generate P&L reports"},
                {"name": "analyze_revenue", "description": "Analyze revenue streams"},
                {"name": "forecast_sales", "description": "Forecast future sales"},
                {"name": "calculate_margins", "description": "Calculate profit margins"},
                {"name": "budget_tracking", "description": "Track budget vs actual"}
            ]
        },
        {
            "name": "VendorPortalAPI",
            "version": "2.5.0",
            "description": "Vendor self-service portal and collaboration",
            "endpoint": "https://api.enterprise.com/vendor-portal/v2",
            "capabilities": ["Vendor Onboarding", "Document Management", "Performance Tracking"],
            "tools": [
                {"name": "onboard_vendor", "description": "Onboard new vendors"},
                {"name": "submit_documents", "description": "Submit vendor documents"},
                {"name": "track_performance", "description": "Track vendor performance"},
                {"name": "manage_contracts", "description": "Manage vendor contracts"},
                {"name": "collaborate_on_products", "description": "Collaborate on products"}
            ]
        },
        {
            "name": "StoreMaintenanceAPI",
            "version": "1.7.0",
            "description": "Store maintenance and facilities management",
            "endpoint": "https://api.enterprise.com/maintenance/v1",
            "capabilities": ["Work Order Management", "Asset Tracking", "Preventive Maintenance"],
            "tools": [
                {"name": "create_work_order", "description": "Create maintenance work orders"},
                {"name": "track_assets", "description": "Track store assets"},
                {"name": "schedule_maintenance", "description": "Schedule preventive maintenance"},
                {"name": "log_issues", "description": "Log maintenance issues"},
                {"name": "manage_contractors", "description": "Manage service contractors"}
            ]
        },
        {
            "name": "TradeInProgramAPI",
            "version": "2.2.0",
            "description": "Product trade-in and buyback programs",
            "endpoint": "https://api.enterprise.com/tradein/v2",
            "capabilities": ["Trade-In Valuation", "Condition Assessment", "Credit Processing"],
            "tools": [
                {"name": "evaluate_trade_in", "description": "Evaluate trade-in value"},
                {"name": "assess_condition", "description": "Assess product condition"},
                {"name": "process_trade_credit", "description": "Process trade-in credits"},
                {"name": "ship_trade_in", "description": "Arrange trade-in shipping"},
                {"name": "recycle_products", "description": "Process product recycling"}
            ]
        }
    ])
    
    # Final services to complete the set of 50
    services_data.extend([
        {
            "name": "LocalizationAPI",
            "version": "2.6.0",
            "description": "Multi-language and regional adaptation services",
            "endpoint": "https://api.enterprise.com/localization/v2",
            "capabilities": ["Translation Services", "Currency Conversion", "Regional Compliance"],
            "tools": [
                {"name": "translate_content", "description": "Translate product content"},
                {"name": "convert_currency", "description": "Convert prices to local currency"},
                {"name": "adapt_for_region", "description": "Adapt content for regions"},
                {"name": "validate_compliance", "description": "Check regional compliance"},
                {"name": "format_addresses", "description": "Format addresses by country"}
            ]
        },
        {
            "name": "InstallmentPaymentAPI",
            "version": "2.4.0",
            "description": "Buy now pay later and installment services",
            "endpoint": "https://api.enterprise.com/installments/v2",
            "capabilities": ["BNPL Services", "Payment Plans", "Credit Checks"],
            "tools": [
                {"name": "check_eligibility", "description": "Check BNPL eligibility"},
                {"name": "create_payment_plan", "description": "Create installment plans"},
                {"name": "process_installment", "description": "Process installment payments"},
                {"name": "manage_defaults", "description": "Manage payment defaults"},
                {"name": "calculate_interest", "description": "Calculate interest charges"}
            ]
        },
        {
            "name": "ProductBundlingAPI",
            "version": "2.3.0",
            "description": "Product bundle creation and management",
            "endpoint": "https://api.enterprise.com/bundles/v2",
            "capabilities": ["Bundle Creation", "Dynamic Pricing", "Inventory Allocation"],
            "tools": [
                {"name": "create_bundle", "description": "Create product bundles"},
                {"name": "calculate_bundle_price", "description": "Calculate bundle pricing"},
                {"name": "allocate_bundle_inventory", "description": "Allocate bundle inventory"},
                {"name": "suggest_bundles", "description": "AI-suggested bundles"},
                {"name": "track_bundle_performance", "description": "Track bundle sales"}
            ]
        },
        {
            "name": "SustainabilityAPI",
            "version": "1.8.0",
            "description": "Sustainability tracking and reporting",
            "endpoint": "https://api.enterprise.com/sustainability/v1",
            "capabilities": ["Carbon Footprint", "Sustainable Products", "ESG Reporting"],
            "tools": [
                {"name": "calculate_carbon_footprint", "description": "Calculate product carbon footprint"},
                {"name": "track_sustainable_products", "description": "Track eco-friendly products"},
                {"name": "generate_esg_report", "description": "Generate ESG reports"},
                {"name": "offset_carbon", "description": "Manage carbon offset programs"},
                {"name": "verify_certifications", "description": "Verify sustainability certs"}
            ]
        },
        {
            "name": "QueueManagementAPI",
            "version": "2.1.0",
            "description": "In-store queue and appointment management",
            "endpoint": "https://api.enterprise.com/queue/v2",
            "capabilities": ["Virtual Queuing", "Appointment Booking", "Wait Time Management"],
            "tools": [
                {"name": "join_virtual_queue", "description": "Join store virtual queue"},
                {"name": "book_appointment", "description": "Book shopping appointments"},
                {"name": "estimate_wait_time", "description": "Estimate queue wait times"},
                {"name": "notify_customer", "description": "Notify when turn arrives"},
                {"name": "manage_capacity", "description": "Manage store capacity"}
            ]
        }
    ])
    
    # Final five services to reach exactly 50
    services_data.extend([
        {
            "name": "AuctionPlatformAPI",
            "version": "2.5.0",
            "description": "Online auction and bidding platform",
            "endpoint": "https://api.enterprise.com/auctions/v2",
            "capabilities": ["Auction Management", "Bid Processing", "Reserve Pricing"],
            "tools": [
                {"name": "create_auction", "description": "Create product auctions"},
                {"name": "place_bid", "description": "Place auction bids"},
                {"name": "set_reserve_price", "description": "Set reserve prices"},
                {"name": "extend_auction", "description": "Extend auction timing"},
                {"name": "process_winning_bid", "description": "Process winning bids"}
            ]
        },
        {
            "name": "RentalServiceAPI",
            "version": "2.2.0",
            "description": "Product rental and leasing services",
            "endpoint": "https://api.enterprise.com/rentals/v2",
            "capabilities": ["Rental Management", "Lease Tracking", "Deposit Handling"],
            "tools": [
                {"name": "create_rental", "description": "Create rental agreements"},
                {"name": "calculate_rental_fee", "description": "Calculate rental fees"},
                {"name": "track_rental_period", "description": "Track rental periods"},
                {"name": "process_deposit", "description": "Handle security deposits"},
                {"name": "manage_returns", "description": "Manage rental returns"}
            ]
        },
        {
            "name": "PersonalShopperAPI",
            "version": "1.9.0",
            "description": "Personal shopping assistant services",
            "endpoint": "https://api.enterprise.com/personal-shopper/v1",
            "capabilities": ["Style Consultation", "Product Curation", "Shopping Assistance"],
            "tools": [
                {"name": "schedule_consultation", "description": "Schedule shopper consultation"},
                {"name": "create_lookbook", "description": "Create personalized lookbooks"},
                {"name": "curate_products", "description": "Curate product selections"},
                {"name": "chat_with_shopper", "description": "Chat with personal shopper"},
                {"name": "save_preferences", "description": "Save style preferences"}
            ]
        },
        {
            "name": "StoreDesignAPI",
            "version": "1.6.0",
            "description": "Store layout and visual merchandising",
            "endpoint": "https://api.enterprise.com/store-design/v1",
            "capabilities": ["Layout Planning", "Visual Merchandising", "Planogram Management"],
            "tools": [
                {"name": "create_planogram", "description": "Create store planograms"},
                {"name": "optimize_layout", "description": "Optimize store layouts"},
                {"name": "manage_displays", "description": "Manage product displays"},
                {"name": "track_compliance", "description": "Track planogram compliance"},
                {"name": "visualize_store", "description": "3D store visualization"}
            ]
        },
        {
            "name": "DropshippingAPI",
            "version": "2.7.0",
            "description": "Dropshipping integration and management",
            "endpoint": "https://api.enterprise.com/dropship/v2",
            "capabilities": ["Supplier Integration", "Order Routing", "Inventory Sync"],
            "tools": [
                {"name": "route_to_supplier", "description": "Route orders to suppliers"},
                {"name": "sync_dropship_inventory", "description": "Sync supplier inventory"},
                {"name": "track_dropship_order", "description": "Track dropship orders"},
                {"name": "calculate_margins", "description": "Calculate dropship margins"},
                {"name": "manage_suppliers", "description": "Manage dropship suppliers"}
            ]
        },
        {
            "name": "CustomerInsightsAPI",
            "version": "3.0.0",
            "description": "Advanced customer analytics and insights",
            "endpoint": "https://api.enterprise.com/insights/v3",
            "capabilities": ["Behavior Analytics", "Predictive Modeling", "Segmentation"],
            "tools": [
                {"name": "analyze_behavior", "description": "Analyze customer behavior patterns"},
                {"name": "predict_churn", "description": "Predict customer churn probability"},
                {"name": "calculate_clv", "description": "Calculate customer lifetime value"},
                {"name": "identify_vip_customers", "description": "Identify VIP customers"},
                {"name": "generate_insights_report", "description": "Generate customer insights"}
            ]
        },
        {
            "name": "SmartPricingAPI",
            "version": "2.8.0",
            "description": "AI-driven competitive pricing optimization",
            "endpoint": "https://api.enterprise.com/smart-pricing/v2",
            "capabilities": ["Price Intelligence", "Competitor Monitoring", "Dynamic Pricing"],
            "tools": [
                {"name": "monitor_competitors", "description": "Monitor competitor prices in real-time"},
                {"name": "optimize_price_points", "description": "Optimize pricing across channels"},
                {"name": "test_price_elasticity", "description": "Test price elasticity"},
                {"name": "forecast_revenue_impact", "description": "Forecast pricing impact"},
                {"name": "automate_repricing", "description": "Automate repricing rules"}
            ]
        },
        {
            "name": "UnifiedCommerceAPI",
            "version": "4.0.0",
            "description": "Unified commerce platform orchestration",
            "endpoint": "https://api.enterprise.com/unified-commerce/v4",
            "capabilities": ["Channel Orchestration", "Order Routing", "Inventory Sync"],
            "tools": [
                {"name": "sync_channels", "description": "Synchronize data across channels"},
                {"name": "route_orders_optimally", "description": "Route orders to optimal fulfillment"},
                {"name": "unify_customer_profiles", "description": "Unify customer profiles"},
                {"name": "orchestrate_promotions", "description": "Orchestrate cross-channel promotions"},
                {"name": "consolidate_reporting", "description": "Consolidate channel reporting"}
            ]
        },
        {
            "name": "RetailAnalyticsAPI",
            "version": "3.3.0",
            "description": "Comprehensive retail analytics platform",
            "endpoint": "https://api.enterprise.com/analytics/v3",
            "capabilities": ["Sales Analytics", "Performance Metrics", "Predictive Analytics"],
            "tools": [
                {"name": "analyze_sales_trends", "description": "Analyze sales trends and patterns"},
                {"name": "calculate_kpis", "description": "Calculate retail KPIs"},
                {"name": "forecast_demand", "description": "Forecast product demand"},
                {"name": "analyze_basket_data", "description": "Analyze shopping basket data"},
                {"name": "benchmark_performance", "description": "Benchmark store performance"}
            ]
        }
    ])
    
    return services_data

def add_services_to_database():
    """Add all services to the database."""
    db = SessionLocal()
    
    try:
        services_data = create_retail_services()
        print(f"Adding {len(services_data)} retail enterprise services...")
        
        for idx, service_data in enumerate(services_data, 1):
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
            db.flush()  # Get the service ID
            
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
                rate_limit_requests=1000,
                rate_limit_window_seconds=60,
                max_concurrent_requests=10,
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
            
            if idx % 5 == 0:
                print(f"Added {idx}/{len(services_data)} services...")
                db.commit()
        
        # Final commit
        db.commit()
        print(f"✅ Successfully added {len(services_data)} retail enterprise services!")
        
        # Print summary
        total_services = db.query(Service).count()
        total_tools = db.query(Tool).count()
        print(f"\nDatabase now contains:")
        print(f"- Total services: {total_services}")
        print(f"- Total tools: {total_tools}")
        
    except Exception as e:
        print(f"❌ Error adding services: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("KPATH Enterprise - Adding Retail Enterprise Services")
    print("=" * 50)
    add_services_to_database()
