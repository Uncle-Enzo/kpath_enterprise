#!/usr/bin/env python3
"""
Add Shipping Insurance Agent Service with 50 Tools

This script adds a comprehensive shipping insurance service with 50 tools
covering quotes, risk assessment, value assessment, limitations, scope,
and underwriter validation and selection.
"""

import sys
import os
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, '/Users/james/claude_development/kpath_enterprise')

from backend.core.database import SessionLocal
from backend.models.models import Service, Tool, ServiceCapability, ServiceIndustry, ServiceIntegrationDetails

def create_shipping_insurance_service():
    """Create the main shipping insurance service."""
    
    service = Service(
        name="ShippingInsuranceAPI",
        description="Comprehensive shipping insurance platform providing quotes, risk assessment, value assessment, coverage analysis, and underwriter selection for maritime and logistics insurance",
        endpoint="https://api.enterprise.com/shipping-insurance/v2",
        version="2.1.0",
        status="active",
        tool_type="API",
        visibility="internal",
        interaction_modes=["REST", "GraphQL"],
        default_timeout_ms=45000,
        success_criteria="HTTP 200-299 response with valid insurance data",
        agent_protocol="kpath-v1",
        auth_type="bearer_token",
        tool_recommendations={
            "use_cases": [
                "shipping_insurance", "cargo_protection", "risk_assessment",
                "underwriter_selection", "coverage_analysis"
            ],
            "primary_tools": [
                "get_instant_quote", "assess_cargo_risk", "validate_coverage_scope",
                "select_underwriter", "calculate_premium"
            ]
        },
        agent_capabilities={
            "compliance": ["IMO", "IMDG", "Lloyd's", "P&I"],
            "response_format": "json",
            "supports_streaming": False,
            "supported_currencies": ["USD", "EUR", "GBP", "JPY"],
            "coverage_types": ["All Risk", "FPA", "WA", "Institute Cargo Clauses"],
            "max_concurrent_requests": 15,
            "geographic_coverage": "worldwide"
        },
        communication_patterns={
            "idempotency": "required",
            "retry_policy": {
                "backoff_ms": 3000,
                "max_attempts": 3
            },
            "request_style": "REST",  
            "async_supported": True,
            "batch_operations": True,
            "rate_limiting": {
                "requests_per_minute": 100,
                "burst_limit": 20
            }
        },
        orchestration_metadata={
            "discovery_tags": [
                "insurance", "shipping", "cargo", "maritime", "logistics",
                "risk", "underwriting", "coverage", "quotes"
            ],
            "security_level": "high",
            "business_domain": "Insurance & Risk Management",
            "sla_response_time_ms": 3000,
            "integration_complexity": "high",
            "data_sensitivity": "confidential"
        }
    )
    
    return service

def create_service_capabilities():
    """Create service capabilities."""
    
    capabilities = [
        ServiceCapability(
            capability_name="Quote Generation",
            capability_desc="Generate insurance quotes for various shipping scenarios with real-time pricing"
        ),
        ServiceCapability(
            capability_name="Risk Assessment", 
            capability_desc="Comprehensive risk analysis including route, cargo, weather, and geopolitical risks"
        ),
        ServiceCapability(
            capability_name="Value Assessment",
            capability_desc="Accurate cargo and shipment valuation using market data and declared values"
        ),
        ServiceCapability(
            capability_name="Coverage Analysis",
            capability_desc="Detailed analysis of insurance coverage scope, limitations, and exclusions"
        ),
        ServiceCapability(
            capability_name="Underwriter Management",
            capability_desc="Underwriter validation, selection, and matching based on risk profiles"
        ),
        ServiceCapability(
            capability_name="Compliance Verification",
            capability_desc="Ensure compliance with international maritime and insurance regulations"
        )
    ]
    
    return capabilities

def create_service_industries():
    """Create service industry associations."""
    
    industries = [
        ServiceIndustry(domain="Insurance"),
        ServiceIndustry(domain="Maritime"),
        ServiceIndustry(domain="Logistics"),
        ServiceIndustry(domain="Risk Management"),
        ServiceIndustry(domain="Finance")
    ]
    
    return industries

def create_integration_details():
    """Create integration details."""
    
    integration = ServiceIntegrationDetails(
        access_protocol="https",
        base_endpoint="https://api.enterprise.com/shipping-insurance/v2",
        auth_method="Bearer Token",
        auth_config={
            "token_type": "JWT",
            "token_endpoint": "https://auth.enterprise.com/shipping-insurance/token",
            "scopes": ["quotes:read", "risk:assess", "underwriter:select"]
        },
        auth_endpoint="https://auth.enterprise.com/shipping-insurance/oauth2",
        rate_limit_requests=100,
        rate_limit_window_seconds=60,
        max_concurrent_requests=15,
        circuit_breaker_config={
            "failure_threshold": 5,
            "timeout_ms": 45000,
            "reset_timeout_ms": 60000
        },
        default_headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-API-Version": "2.1.0"
        },
        request_content_type="application/json",
        response_content_type="application/json",
        health_check_endpoint="/health",
        health_check_interval_seconds=30
    )
    
    return integration

def create_shipping_insurance_tools():
    """Create all 50 shipping insurance tools."""
    
    tools = []
    
    # QUOTES TOOLS (10 tools)
    quotes_tools = [        # 1. get_instant_quote
        Tool(
            tool_name="get_instant_quote",
            tool_description="Generate instant shipping insurance quote for standard cargo",
            input_schema={
                "type": "object",
                "required": ["cargo_value", "origin", "destination", "cargo_type"],
                "properties": {
                    "cargo_value": {"type": "number", "minimum": 100, "description": "Declared cargo value in USD"},
                    "origin": {"type": "string", "description": "Origin port/location code"},
                    "destination": {"type": "string", "description": "Destination port/location code"},
                    "cargo_type": {"type": "string", "enum": ["general", "electronics", "machinery", "textiles", "food"], "description": "Type of cargo being shipped"}
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "quote_id": {"type": "string"},
                    "premium": {"type": "number"},
                    "coverage_amount": {"type": "number"},
                    "deductible": {"type": "number"},
                    "policy_type": {"type": "string"},
                    "valid_until": {"type": "string", "format": "date-time"}
                }
            },
            example_calls={
                "electronics_shipment": {
                    "cargo_value": 50000,
                    "origin": "USLAX",
                    "destination": "DEHAM",
                    "cargo_type": "electronics"
                }
            }
        ),
        
        # 2. get_custom_quote
        Tool(
            tool_name="get_custom_quote",
            tool_description="Generate customized insurance quote with specific coverage requirements",
            input_schema={
                "type": "object",
                "required": ["cargo_details", "coverage_requirements", "route_info"],
                "properties": {
                    "cargo_details": {
                        "type": "object",
                        "properties": {
                            "value": {"type": "number"},
                            "type": {"type": "string"},
                            "description": {"type": "string"},
                            "packaging": {"type": "string"}
                        }
                    },
                    "coverage_requirements": {
                        "type": "object", 
                        "properties": {
                            "coverage_type": {"type": "string", "enum": ["all_risk", "fpa", "wa", "institute_a", "institute_b", "institute_c"]},
                            "additional_perils": {"type": "array", "items": {"type": "string"}},
                            "exclude_perils": {"type": "array", "items": {"type": "string"}}
                        }
                    },
                    "route_info": {
                        "type": "object",
                        "properties": {
                            "transit_mode": {"type": "string", "enum": ["ocean", "air", "land", "multimodal"]},
                            "vessel_details": {"type": "object"},
                            "expected_duration": {"type": "integer"}
                        }
                    }
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "quote_id": {"type": "string"},
                    "detailed_premium": {"type": "object"},
                    "coverage_breakdown": {"type": "object"},
                    "terms_conditions": {"type": "array"},
                    "validity_period": {"type": "string"}
                }
            }
        ),

        # 3. get_bulk_quotes
        Tool(
            tool_name="get_bulk_quotes",
            tool_description="Generate multiple quotes for bulk shipping operations",
            input_schema={
                "type": "object",
                "required": ["shipments", "bulk_discount_eligible"],
                "properties": {
                    "shipments": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "shipment_id": {"type": "string"},
                                "cargo_value": {"type": "number"},
                                "route": {"type": "object"},
                                "cargo_type": {"type": "string"}
                            }
                        }
                    },
                    "bulk_discount_eligible": {"type": "boolean"},
                    "annual_volume": {"type": "number", "description": "Expected annual shipping volume"}
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "bulk_quote_id": {"type": "string"},
                    "individual_quotes": {"type": "array"},
                    "bulk_discount": {"type": "number"},
                    "total_premium": {"type": "number"},
                    "volume_tier": {"type": "string"}
                }
            }
        ),

        # 4. calculate_premium
        Tool(
            tool_name="calculate_premium",
            tool_description="Calculate insurance premium based on risk factors and coverage",
            input_schema={
                "type": "object",
                "required": ["base_value", "risk_factors", "coverage_percentage"],
                "properties": {
                    "base_value": {"type": "number"},
                    "risk_factors": {
                        "type": "object",
                        "properties": {
                            "route_risk_score": {"type": "number", "minimum": 1, "maximum": 10},
                            "cargo_risk_score": {"type": "number", "minimum": 1, "maximum": 10},
                            "seasonal_factor": {"type": "number"},
                            "vessel_age_factor": {"type": "number"}
                        }
                    },
                    "coverage_percentage": {"type": "number", "minimum": 100, "maximum": 120}
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "base_premium": {"type": "number"},
                    "risk_adjustments": {"type": "object"},
                    "final_premium": {"type": "number"},
                    "premium_breakdown": {"type": "object"}
                }
            }
        ),

        # 5. compare_quotes
        Tool(
            tool_name="compare_quotes",
            tool_description="Compare multiple insurance quotes and provide recommendations",
            input_schema={
                "type": "object",
                "required": ["quote_ids"],
                "properties": {
                    "quote_ids": {"type": "array", "items": {"type": "string"}},
                    "comparison_criteria": {
                        "type": "array",
                        "items": {"type": "string", "enum": ["premium", "coverage", "deductible", "exclusions", "claims_process"]}
                    }
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "comparison_matrix": {"type": "object"},
                    "recommended_quote": {"type": "string"},
                    "savings_analysis": {"type": "object"},
                    "risk_coverage_analysis": {"type": "object"}
                }
            }
        ),

        # 6. get_renewal_quote
        Tool(
            tool_name="get_renewal_quote",
            tool_description="Generate renewal quote for existing policy",
            input_schema={
                "type": "object",
                "required": ["policy_number", "renewal_date"],
                "properties": {
                    "policy_number": {"type": "string"},
                    "renewal_date": {"type": "string", "format": "date"},
                    "updated_cargo_value": {"type": "number"},
                    "claims_history": {"type": "boolean"}
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "renewal_quote_id": {"type": "string"},
                    "current_premium": {"type": "number"},
                    "renewal_premium": {"type": "number"},
                    "premium_change": {"type": "object"},
                    "updated_terms": {"type": "object"}
                }
            }
        ),

        # 7. get_spot_rate_quote
        Tool(
            tool_name="get_spot_rate_quote",
            tool_description="Get spot market insurance rates for immediate coverage",
            input_schema={
                "type": "object",
                "required": ["urgent_shipment", "departure_date"],
                "properties": {
                    "urgent_shipment": {"type": "boolean"},
                    "departure_date": {"type": "string", "format": "date"},
                    "cargo_details": {"type": "object"},
                    "coverage_duration": {"type": "integer", "description": "Coverage duration in days"}
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "spot_rate": {"type": "number"},
                    "premium_surcharge": {"type": "number"},
                    "immediate_coverage": {"type": "boolean"},
                    "rate_validity": {"type": "string"}
                }
            }
        ),

        # 8. estimate_annual_premium
        Tool(
            tool_name="estimate_annual_premium",
            tool_description="Estimate annual premium for regular shipping operations",
            input_schema={
                "type": "object",
                "required": ["annual_cargo_value", "shipping_frequency", "route_patterns"],
                "properties": {
                    "annual_cargo_value": {"type": "number"},
                    "shipping_frequency": {"type": "integer", "description": "Shipments per year"},
                    "route_patterns": {"type": "array", "items": {"type": "object"}},
                    "volume_discount_tier": {"type": "string", "enum": ["bronze", "silver", "gold", "platinum"]}
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "estimated_annual_premium": {"type": "number"},
                    "volume_discount": {"type": "number"},
                    "payment_terms": {"type": "object"},
                    "coverage_summary": {"type": "object"}
                }
            }
        ),

        # 9. get_conditional_quote
        Tool(
            tool_name="get_conditional_quote",
            tool_description="Generate quote with specific conditions and requirements",
            input_schema={
                "type": "object",
                "required": ["base_quote_params", "conditions"],
                "properties": {
                    "base_quote_params": {"type": "object"},
                    "conditions": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "condition_type": {"type": "string"},
                                "requirement": {"type": "string"},
                                "compliance_needed": {"type": "boolean"}
                            }
                        }
                    }
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "conditional_quote": {"type": "object"},
                    "conditions_impact": {"type": "object"},
                    "compliance_requirements": {"type": "array"},
                    "additional_premium": {"type": "number"}
                }
            }
        ),

        # 10. validate_quote_accuracy
        Tool(
            tool_name="validate_quote_accuracy",
            tool_description="Validate and verify accuracy of generated quotes",
            input_schema={
                "type": "object",
                "required": ["quote_id", "validation_criteria"],
                "properties": {
                    "quote_id": {"type": "string"},
                    "validation_criteria": {
                        "type": "object",
                        "properties": {
                            "market_rate_check": {"type": "boolean"},
                            "risk_assessment_verification": {"type": "boolean"},
                            "regulatory_compliance": {"type": "boolean"}
                        }
                    }
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "validation_status": {"type": "string", "enum": ["valid", "invalid", "needs_review"]},
                    "accuracy_score": {"type": "number"},
                    "discrepancies": {"type": "array"},
                    "recommendations": {"type": "array"}
                }
            }
        )    ]
    
    # Add quotes tools to main list
    tools.extend(quotes_tools)
    
    # RISK ASSESSMENT TOOLS (10 tools)
    risk_assessment_tools = [
        # 11. assess_cargo_risk
        Tool(
            tool_name="assess_cargo_risk",
            tool_description="Assess risk factors specific to cargo type and characteristics",
            input_schema={
                "type": "object",
                "required": ["cargo_details", "packaging_info"],
                "properties": {
                    "cargo_details": {
                        "type": "object",
                        "properties": {
                            "cargo_type": {"type": "string"},
                            "value": {"type": "number"},
                            "hazard_class": {"type": "string"},
                            "fragility": {"type": "string", "enum": ["low", "medium", "high"]}
                        }
                    },
                    "packaging_info": {
                        "type": "object",
                        "properties": {
                            "container_type": {"type": "string"},
                            "protection_level": {"type": "string"},
                            "special_handling": {"type": "boolean"}
                        }
                    }
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "risk_score": {"type": "number", "minimum": 1, "maximum": 10},
                    "risk_factors": {"type": "array"},
                    "mitigation_recommendations": {"type": "array"},
                    "premium_impact": {"type": "number"}
                }
            }
        ),

        # 12. assess_route_risk
        Tool(
            tool_name="assess_route_risk",
            tool_description="Analyze risks associated with shipping routes and transit paths",
            input_schema={
                "type": "object",
                "required": ["origin", "destination", "transit_mode"],
                "properties": {
                    "origin": {"type": "string"},
                    "destination": {"type": "string"},
                    "transit_mode": {"type": "string", "enum": ["ocean", "air", "land", "multimodal"]},
                    "intermediate_ports": {"type": "array", "items": {"type": "string"}},
                    "seasonal_factors": {"type": "boolean"}
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "route_risk_score": {"type": "number"},
                    "high_risk_segments": {"type": "array"},
                    "weather_risks": {"type": "object"},
                    "geopolitical_risks": {"type": "object"},
                    "piracy_risk": {"type": "string", "enum": ["low", "medium", "high"]}
                }
            }
        ),

        # 13. assess_weather_risk
        Tool(
            tool_name="assess_weather_risk",
            tool_description="Evaluate weather-related risks for shipping timeline",
            input_schema={
                "type": "object",
                "required": ["route", "departure_date", "season"],
                "properties": {
                    "route": {"type": "object"},
                    "departure_date": {"type": "string", "format": "date"},
                    "season": {"type": "string", "enum": ["spring", "summer", "autumn", "winter"]},
                    "weather_sensitivity": {"type": "string", "enum": ["low", "medium", "high"]}
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "weather_risk_score": {"type": "number"},
                    "storm_probability": {"type": "number"},
                    "delay_risk": {"type": "string"},
                    "recommended_departure_window": {"type": "object"}
                }
            }
        ),

        # 14. assess_vessel_risk
        Tool(
            tool_name="assess_vessel_risk",
            tool_description="Evaluate risks associated with specific vessels or carriers",
            input_schema={
                "type": "object",
                "required": ["vessel_details", "carrier_info"],
                "properties": {
                    "vessel_details": {
                        "type": "object",
                        "properties": {
                            "vessel_name": {"type": "string"},
                            "imo_number": {"type": "string"},
                            "age": {"type": "integer"},
                            "flag_state": {"type": "string"},
                            "vessel_type": {"type": "string"}
                        }
                    },
                    "carrier_info": {
                        "type": "object",
                        "properties": {
                            "carrier_name": {"type": "string"},
                            "safety_rating": {"type": "string"},
                            "claims_history": {"type": "object"}
                        }
                    }
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "vessel_risk_score": {"type": "number"},
                    "safety_assessment": {"type": "object"},
                    "carrier_reliability": {"type": "string"},
                    "recommended_actions": {"type": "array"}
                }
            }
        ),

        # 15. assess_port_risk
        Tool(
            tool_name="assess_port_risk",
            tool_description="Analyze risks associated with specific ports and terminals",
            input_schema={
                "type": "object",
                "required": ["port_codes", "cargo_handling_requirements"],
                "properties": {
                    "port_codes": {"type": "array", "items": {"type": "string"}},
                    "cargo_handling_requirements": {"type": "object"},
                    "storage_duration": {"type": "integer", "description": "Days in port"}
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "port_risk_scores": {"type": "object"},
                    "security_levels": {"type": "object"},
                    "handling_risks": {"type": "object"},
                    "theft_risk": {"type": "string", "enum": ["low", "medium", "high"]}
                }
            }
        ),

        # 16. assess_geopolitical_risk
        Tool(
            tool_name="assess_geopolitical_risk",
            tool_description="Evaluate geopolitical risks affecting shipping routes",
            input_schema={
                "type": "object",
                "required": ["countries", "transit_waters"],
                "properties": {
                    "countries": {"type": "array", "items": {"type": "string"}},
                    "transit_waters": {"type": "array", "items": {"type": "string"}},
                    "cargo_sensitivity": {"type": "string", "enum": ["standard", "sensitive", "restricted"]}
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "geopolitical_risk_score": {"type": "number"},
                    "sanctions_impact": {"type": "object"},
                    "regulatory_restrictions": {"type": "array"},
                    "alternative_routes": {"type": "array"}
                }
            }
        ),

        # 17. assess_environmental_risk
        Tool(
            tool_name="assess_environmental_risk",
            tool_description="Evaluate environmental risks and compliance requirements",
            input_schema={
                "type": "object",
                "required": ["cargo_environmental_impact", "route_environmental_zones"],
                "properties": {
                    "cargo_environmental_impact": {"type": "string", "enum": ["minimal", "moderate", "significant"]},
                    "route_environmental_zones": {"type": "array"},
                    "environmental_regulations": {"type": "object"}
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "environmental_risk_score": {"type": "number"},
                    "compliance_requirements": {"type": "array"},
                    "potential_penalties": {"type": "object"},
                    "mitigation_measures": {"type": "array"}
                }
            }
        ),

        # 18. assess_cyber_risk
        Tool(
            tool_name="assess_cyber_risk",
            tool_description="Evaluate cyber security risks for digital shipping operations",
            input_schema={
                "type": "object",
                "required": ["digital_systems_involved", "data_sensitivity"],
                "properties": {
                    "digital_systems_involved": {"type": "array"},
                    "data_sensitivity": {"type": "string", "enum": ["public", "internal", "confidential", "restricted"]},
                    "cyber_security_measures": {"type": "object"}
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "cyber_risk_score": {"type": "number"},
                    "vulnerability_assessment": {"type": "object"},
                    "recommended_protections": {"type": "array"},
                    "coverage_recommendations": {"type": "object"}
                }
            }
        ),

        # 19. assess_total_risk_profile
        Tool(
            tool_name="assess_total_risk_profile",
            tool_description="Comprehensive risk assessment combining all risk factors",
            input_schema={
                "type": "object",
                "required": ["individual_risk_scores"],
                "properties": {
                    "individual_risk_scores": {
                        "type": "object",
                        "properties": {
                            "cargo_risk": {"type": "number"},
                            "route_risk": {"type": "number"},
                            "vessel_risk": {"type": "number"},
                            "weather_risk": {"type": "number"},
                            "geopolitical_risk": {"type": "number"}
                        }
                    },
                    "risk_tolerance": {"type": "string", "enum": ["conservative", "moderate", "aggressive"]}
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "overall_risk_score": {"type": "number"},
                    "risk_category": {"type": "string"},
                    "insurability": {"type": "string", "enum": ["standard", "non-standard", "declined"]},
                    "premium_loading": {"type": "number"}
                }
            }
        ),

        # 20. generate_risk_report
        Tool(
            tool_name="generate_risk_report",
            tool_description="Generate comprehensive risk assessment report",
            input_schema={
                "type": "object",
                "required": ["shipment_id", "risk_assessments"],
                "properties": {
                    "shipment_id": {"type": "string"},
                    "risk_assessments": {"type": "object"},
                    "report_format": {"type": "string", "enum": ["summary", "detailed", "executive"]},
                    "include_recommendations": {"type": "boolean"}
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "report_id": {"type": "string"},
                    "executive_summary": {"type": "string"},
                    "detailed_analysis": {"type": "object"},
                    "risk_matrix": {"type": "object"},
                    "actionable_recommendations": {"type": "array"}
                }
            }
        )
    ]
    
    # Add risk assessment tools to main list
    tools.extend(risk_assessment_tools)    
    # VALUE ASSESSMENT TOOLS (8 tools)
    value_assessment_tools = [
        # 21. calculate_cargo_value
        Tool(
            tool_name="calculate_cargo_value",
            tool_description="Calculate accurate cargo value for insurance purposes",
            input_schema={
                "type": "object",
                "required": ["cargo_details", "valuation_method"],
                "properties": {
                    "cargo_details": {
                        "type": "object",
                        "properties": {
                            "description": {"type": "string"},
                            "quantity": {"type": "number"},
                            "unit_value": {"type": "number"},
                            "currency": {"type": "string"}
                        }
                    },
                    "valuation_method": {"type": "string", "enum": ["cost", "market", "replacement", "agreed"]}
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "calculated_value": {"type": "number"},
                    "valuation_basis": {"type": "string"},
                    "supporting_documentation": {"type": "array"},
                    "confidence_level": {"type": "string"}
                }
            }
        ),

        # 22. validate_declared_value
        Tool(
            tool_name="validate_declared_value",
            tool_description="Validate declared cargo value against market standards",
            input_schema={
                "type": "object",
                "required": ["declared_value", "cargo_description", "market_data"],
                "properties": {
                    "declared_value": {"type": "number"},
                    "cargo_description": {"type": "string"},
                    "market_data": {"type": "object"},
                    "supporting_documents": {"type": "array"}
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "validation_status": {"type": "string", "enum": ["valid", "questionable", "invalid"]},
                    "market_comparison": {"type": "object"},
                    "recommended_value": {"type": "number"},
                    "variance_explanation": {"type": "string"}
                }
            }
        ),

        # 23. assess_market_value
        Tool(
            tool_name="assess_market_value",
            tool_description="Determine current market value of cargo",
            input_schema={
                "type": "object",
                "required": ["commodity_details", "market_conditions"],
                "properties": {
                    "commodity_details": {
                        "type": "object",
                        "properties": {
                            "commodity_type": {"type": "string"},
                            "grade_quality": {"type": "string"},
                            "specifications": {"type": "object"}
                        }
                    },
                    "market_conditions": {
                        "type": "object",
                        "properties": {
                            "market_date": {"type": "string", "format": "date"},
                            "geographic_market": {"type": "string"},
                            "demand_supply_factors": {"type": "object"}
                        }
                    }
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "market_value": {"type": "number"},
                    "value_range": {"type": "object"},
                    "market_volatility": {"type": "string"},
                    "price_trends": {"type": "object"}
                }
            }
        ),

        # 24. calculate_replacement_cost
        Tool(
            tool_name="calculate_replacement_cost",
            tool_description="Calculate replacement cost for damaged or lost cargo",
            input_schema={
                "type": "object",
                "required": ["original_cargo", "replacement_location", "time_factor"],
                "properties": {
                    "original_cargo": {"type": "object"},
                    "replacement_location": {"type": "string"},
                    "time_factor": {"type": "integer", "description": "Days to replacement"},
                    "urgency_factor": {"type": "string", "enum": ["standard", "urgent", "critical"]}
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "replacement_cost": {"type": "number"},
                    "cost_breakdown": {"type": "object"},
                    "time_impact": {"type": "number"},
                    "availability_assessment": {"type": "string"}
                }
            }
        ),

        # 25. assess_depreciation_factors
        Tool(
            tool_name="assess_depreciation_factors",
            tool_description="Assess depreciation factors affecting cargo value",
            input_schema={
                "type": "object",
                "required": ["cargo_type", "age_condition", "market_factors"],
                "properties": {
                    "cargo_type": {"type": "string"},
                    "age_condition": {
                        "type": "object",
                        "properties": {
                            "manufacture_date": {"type": "string", "format": "date"},
                            "condition": {"type": "string", "enum": ["new", "good", "fair", "poor"]}
                        }
                    },
                    "market_factors": {"type": "object"}
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "depreciation_rate": {"type": "number"},
                    "adjusted_value": {"type": "number"},
                    "depreciation_factors": {"type": "array"},
                    "residual_value": {"type": "number"}
                }
            }
        ),

        # 26. calculate_salvage_value
        Tool(
            tool_name="calculate_salvage_value",
            tool_description="Calculate potential salvage value in case of damage",
            input_schema={
                "type": "object",
                "required": ["damaged_cargo", "damage_extent", "salvage_location"],
                "properties": {
                    "damaged_cargo": {"type": "object"},
                    "damage_extent": {"type": "string", "enum": ["minor", "moderate", "severe", "total"]},
                    "salvage_location": {"type": "string"},
                    "salvage_market_conditions": {"type": "object"}
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "salvage_value": {"type": "number"},
                    "salvage_percentage": {"type": "number"},
                    "disposal_costs": {"type": "number"},
                    "net_salvage_value": {"type": "number"}
                }
            }
        ),

        # 27. assess_currency_impact
        Tool(
            tool_name="assess_currency_impact",
            tool_description="Assess currency exchange impact on cargo valuation",
            input_schema={
                "type": "object",
                "required": ["base_currency", "policy_currency", "value_amount"],
                "properties": {
                    "base_currency": {"type": "string"},
                    "policy_currency": {"type": "string"},
                    "value_amount": {"type": "number"},
                    "exchange_rate_date": {"type": "string", "format": "date"},
                    "currency_hedging": {"type": "boolean"}
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "converted_value": {"type": "number"},
                    "exchange_rate_used": {"type": "number"},
                    "currency_risk": {"type": "object"},
                    "hedging_recommendations": {"type": "array"}
                }
            }
        ),

        # 28. generate_valuation_certificate
        Tool(
            tool_name="generate_valuation_certificate",
            tool_description="Generate official valuation certificate for insurance purposes",
            input_schema={
                "type": "object",
                "required": ["valuation_data", "certification_requirements"],
                "properties": {
                    "valuation_data": {"type": "object"},
                    "certification_requirements": {
                        "type": "object",
                        "properties": {
                            "certifier_credentials": {"type": "string"},
                            "regulatory_compliance": {"type": "array"},
                            "validity_period": {"type": "integer"}
                        }
                    }
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "certificate_id": {"type": "string"},
                    "certified_value": {"type": "number"},
                    "certifier_details": {"type": "object"},
                    "validity_dates": {"type": "object"},
                    "certificate_document": {"type": "string"}
                }
            }
        )
    ]
    
    # Add value assessment tools to main list
    tools.extend(value_assessment_tools)    
    # LIMITATIONS TOOLS (8 tools)
    limitations_tools = [
        # 29. analyze_coverage_limitations
        Tool(
            tool_name="analyze_coverage_limitations",
            tool_description="Analyze policy coverage limitations and exclusions",
            input_schema={
                "type": "object",
                "required": ["policy_type", "cargo_details", "route_info"],
                "properties": {
                    "policy_type": {"type": "string", "enum": ["all_risk", "fpa", "wa", "institute_a", "institute_b", "institute_c"]},
                    "cargo_details": {"type": "object"},
                    "route_info": {"type": "object"}
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "coverage_limitations": {"type": "array"},
                    "exclusions": {"type": "array"},
                    "conditions": {"type": "array"},
                    "coverage_gaps": {"type": "array"}
                }
            }
        ),

        # 30. check_policy_exclusions
        Tool(
            tool_name="check_policy_exclusions",
            tool_description="Check specific exclusions that apply to the cargo and route",
            input_schema={
                "type": "object",
                "required": ["exclusion_categories", "cargo_risk_profile"],
                "properties": {
                    "exclusion_categories": {"type": "array"},
                    "cargo_risk_profile": {"type": "object"},
                    "special_circumstances": {"type": "array"}
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "applicable_exclusions": {"type": "array"},
                    "exclusion_impact": {"type": "object"},
                    "mitigation_options": {"type": "array"},
                    "additional_coverage_needed": {"type": "array"}
                }
            }
        ),

        # 31. validate_coverage_limits
        Tool(
            tool_name="validate_coverage_limits",
            tool_description="Validate that coverage limits meet cargo value requirements",
            input_schema={
                "type": "object",
                "required": ["cargo_value", "proposed_limits", "coverage_type"],
                "properties": {
                    "cargo_value": {"type": "number"},
                    "proposed_limits": {"type": "object"},
                    "coverage_type": {"type": "string"},
                    "regulatory_requirements": {"type": "object"}
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "limit_adequacy": {"type": "string", "enum": ["adequate", "insufficient", "excessive"]},
                    "recommended_limits": {"type": "object"},
                    "gap_analysis": {"type": "object"},
                    "regulatory_compliance": {"type": "boolean"}
                }
            }
        ),

        # 32. assess_deductible_impact
        Tool(
            tool_name="assess_deductible_impact",
            tool_description="Assess impact of different deductible options",
            input_schema={
                "type": "object",
                "required": ["deductible_options", "claim_probability", "cargo_value"],
                "properties": {
                    "deductible_options": {"type": "array"},
                    "claim_probability": {"type": "number"},
                    "cargo_value": {"type": "number"},
                    "risk_tolerance": {"type": "string"}
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "deductible_analysis": {"type": "object"},
                    "cost_benefit_analysis": {"type": "object"},
                    "recommended_deductible": {"type": "number"},
                    "premium_savings": {"type": "number"}
                }
            }
        ),

        # 33. check_territorial_limits
        Tool(
            tool_name="check_territorial_limits",
            tool_description="Check territorial coverage limits and restrictions",
            input_schema={
                "type": "object",
                "required": ["coverage_territory", "planned_route"],
                "properties": {
                    "coverage_territory": {"type": "object"},
                    "planned_route": {"type": "object"},
                    "high_risk_areas": {"type": "array"}
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "territorial_coverage": {"type": "object"},
                    "restricted_areas": {"type": "array"},
                    "additional_premium_areas": {"type": "array"},
                    "coverage_recommendations": {"type": "array"}
                }
            }
        ),

        # 34. analyze_time_limitations
        Tool(
            tool_name="analyze_time_limitations",
            tool_description="Analyze time-based coverage limitations and restrictions",
            input_schema={
                "type": "object",
                "required": ["policy_period", "transit_duration", "storage_requirements"],
                "properties": {
                    "policy_period": {"type": "object"},
                    "transit_duration": {"type": "integer"},
                    "storage_requirements": {"type": "object"}
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "time_coverage_analysis": {"type": "object"},
                    "coverage_gaps": {"type": "array"},
                    "extension_requirements": {"type": "object"},
                    "additional_premium": {"type": "number"}
                }
            }
        ),

        # 35. check_cargo_limitations
        Tool(
            tool_name="check_cargo_limitations",
            tool_description="Check specific limitations that apply to cargo type",
            input_schema={
                "type": "object",
                "required": ["cargo_type", "cargo_characteristics"],
                "properties": {
                    "cargo_type": {"type": "string"},
                    "cargo_characteristics": {"type": "object"},
                    "special_conditions": {"type": "array"}
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "cargo_specific_limitations": {"type": "array"},
                    "handling_restrictions": {"type": "array"},
                    "coverage_modifications": {"type": "object"},
                    "compliance_requirements": {"type": "array"}
                }
            }
        ),

        # 36. generate_limitations_summary
        Tool(
            tool_name="generate_limitations_summary",
            tool_description="Generate comprehensive summary of all policy limitations",
            input_schema={
                "type": "object",
                "required": ["policy_details", "cargo_details", "route_details"],
                "properties": {
                    "policy_details": {"type": "object"},
                    "cargo_details": {"type": "object"},
                    "route_details": {"type": "object"}
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "limitations_summary": {"type": "object"},
                    "key_exclusions": {"type": "array"},
                    "coverage_warnings": {"type": "array"},
                    "recommended_actions": {"type": "array"}
                }
            }
        )
    ]
    
    # Add limitations tools to main list
    tools.extend(limitations_tools)
    
    # SCOPE TOOLS (7 tools)
    scope_tools = [
        # 37. define_coverage_scope
        Tool(
            tool_name="define_coverage_scope",
            tool_description="Define comprehensive coverage scope for shipping insurance",
            input_schema={
                "type": "object",
                "required": ["coverage_requirements", "business_needs"],
                "properties": {
                    "coverage_requirements": {"type": "object"},
                    "business_needs": {"type": "object"},
                    "risk_appetite": {"type": "string", "enum": ["conservative", "moderate", "aggressive"]}
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "coverage_scope": {"type": "object"},
                    "included_perils": {"type": "array"},
                    "coverage_extensions": {"type": "array"},
                    "scope_limitations": {"type": "array"}
                }
            }
        ),

        # 38. validate_coverage_scope
        Tool(
            tool_name="validate_coverage_scope",
            tool_description="Validate that coverage scope meets all requirements",
            input_schema={
                "type": "object",
                "required": ["proposed_scope", "requirements_checklist"],
                "properties": {
                    "proposed_scope": {"type": "object"},
                    "requirements_checklist": {"type": "array"},
                    "regulatory_requirements": {"type": "object"}
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "scope_validation": {"type": "object"},
                    "requirements_met": {"type": "array"},
                    "gaps_identified": {"type": "array"},
                    "recommendations": {"type": "array"}
                }
            }
        ),

        # 39. analyze_geographic_scope
        Tool(
            tool_name="analyze_geographic_scope",
            tool_description="Analyze geographic coverage scope and limitations",
            input_schema={
                "type": "object",
                "required": ["coverage_areas", "operational_regions"],
                "properties": {
                    "coverage_areas": {"type": "array"},
                    "operational_regions": {"type": "array"},
                    "excluded_territories": {"type": "array"}
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "geographic_coverage": {"type": "object"},
                    "coverage_map": {"type": "object"},
                    "exclusion_impact": {"type": "object"},
                    "expansion_options": {"type": "array"}
                }
            }
        ),

        # 40. assess_temporal_scope
        Tool(
            tool_name="assess_temporal_scope",
            tool_description="Assess temporal coverage scope and duration requirements",
            input_schema={
                "type": "object",
                "required": ["coverage_period", "business_cycle"],
                "properties": {
                    "coverage_period": {"type": "object"},
                    "business_cycle": {"type": "object"},
                    "seasonal_variations": {"type": "object"}
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "temporal_coverage": {"type": "object"},
                    "coverage_calendar": {"type": "object"},
                    "renewal_schedule": {"type": "object"},
                    "coverage_continuity": {"type": "boolean"}
                }
            }
        ),

        # 41. analyze_modal_scope
        Tool(
            tool_name="analyze_modal_scope",
            tool_description="Analyze coverage scope across different transport modes",
            input_schema={
                "type": "object",
                "required": ["transport_modes", "multimodal_requirements"],
                "properties": {
                    "transport_modes": {"type": "array"},
                    "multimodal_requirements": {"type": "object"},
                    "intermodal_transfers": {"type": "array"}
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "modal_coverage": {"type": "object"},
                    "transfer_coverage": {"type": "object"},
                    "mode_specific_limitations": {"type": "object"},
                    "integrated_coverage": {"type": "boolean"}
                }
            }
        ),

        # 42. check_scope_compliance
        Tool(
            tool_name="check_scope_compliance",
            tool_description="Check coverage scope compliance with regulations and standards",
            input_schema={
                "type": "object",
                "required": ["coverage_scope", "applicable_regulations"],
                "properties": {
                    "coverage_scope": {"type": "object"},
                    "applicable_regulations": {"type": "array"},
                    "industry_standards": {"type": "array"}
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "compliance_status": {"type": "object"},
                    "regulatory_gaps": {"type": "array"},
                    "compliance_recommendations": {"type": "array"},
                    "certification_requirements": {"type": "array"}
                }
            }
        ),

        # 43. optimize_coverage_scope
        Tool(
            tool_name="optimize_coverage_scope",
            tool_description="Optimize coverage scope for cost-effectiveness and protection",
            input_schema={
                "type": "object",
                "required": ["current_scope", "optimization_criteria"],
                "properties": {
                    "current_scope": {"type": "object"},
                    "optimization_criteria": {"type": "object"},
                    "budget_constraints": {"type": "object"}
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "optimized_scope": {"type": "object"},
                    "cost_savings": {"type": "number"},
                    "coverage_improvements": {"type": "array"},
                    "trade_off_analysis": {"type": "object"}
                }
            }
        )
    ]
    
    # Add scope tools to main list
    tools.extend(scope_tools)
    
    # UNDERWRITER TOOLS (7 tools) 
    underwriter_tools = [
        # 44. validate_underwriter_credentials
        Tool(
            tool_name="validate_underwriter_credentials",
            tool_description="Validate underwriter credentials and authorization",
            input_schema={
                "type": "object",
                "required": ["underwriter_id", "credentials"],
                "properties": {
                    "underwriter_id": {"type": "string"},
                    "credentials": {
                        "type": "object",
                        "properties": {
                            "license_number": {"type": "string"},
                            "regulatory_body": {"type": "string"},
                            "specializations": {"type": "array"},
                            "authorization_level": {"type": "string"}
                        }
                    }
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "validation_status": {"type": "string", "enum": ["valid", "invalid", "expired", "suspended"]},
                    "credential_details": {"type": "object"},
                    "authority_confirmation": {"type": "object"},
                    "restrictions": {"type": "array"}
                }
            }
        ),

        # 45. select_optimal_underwriter
        Tool(
            tool_name="select_optimal_underwriter",
            tool_description="Select optimal underwriter based on risk profile and requirements",
            input_schema={
                "type": "object",
                "required": ["risk_profile", "coverage_requirements", "underwriter_pool"],
                "properties": {
                    "risk_profile": {"type": "object"},
                    "coverage_requirements": {"type": "object"},
                    "underwriter_pool": {"type": "array"},
                    "selection_criteria": {
                        "type": "object",
                        "properties": {
                            "expertise_weight": {"type": "number"},
                            "capacity_weight": {"type": "number"},
                            "pricing_weight": {"type": "number"},
                            "service_weight": {"type": "number"}
                        }
                    }
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "selected_underwriter": {"type": "object"},
                    "selection_rationale": {"type": "string"},
                    "alternative_options": {"type": "array"},
                    "expected_terms": {"type": "object"}
                }
            }
        ),

        # 46. assess_underwriter_capacity
        Tool(
            tool_name="assess_underwriter_capacity",
            tool_description="Assess underwriter capacity for specific risks",
            input_schema={
                "type": "object",
                "required": ["underwriter_id", "risk_amount", "risk_type"],
                "properties": {
                    "underwriter_id": {"type": "string"},
                    "risk_amount": {"type": "number"},
                    "risk_type": {"type": "string"},
                    "existing_exposures": {"type": "object"}
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "available_capacity": {"type": "number"},
                    "capacity_utilization": {"type": "number"},
                    "capacity_constraints": {"type": "array"},
                    "reinsurance_requirements": {"type": "object"}
                }
            }
        ),

        # 47. evaluate_underwriter_expertise
        Tool(
            tool_name="evaluate_underwriter_expertise",
            tool_description="Evaluate underwriter expertise in specific risk areas",
            input_schema={
                "type": "object",
                "required": ["underwriter_profile", "required_expertise"],
                "properties": {
                    "underwriter_profile": {"type": "object"},
                    "required_expertise": {"type": "array"},
                    "risk_complexity": {"type": "string", "enum": ["standard", "complex", "specialized"]}
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "expertise_score": {"type": "number"},
                    "relevant_experience": {"type": "object"},
                    "specialization_match": {"type": "object"},
                    "competency_gaps": {"type": "array"}
                }
            }
        ),

        # 48. check_underwriter_appetite
        Tool(
            tool_name="check_underwriter_appetite",
            tool_description="Check underwriter appetite for specific risk types",
            input_schema={
                "type": "object",
                "required": ["underwriter_id", "risk_characteristics"],
                "properties": {
                    "underwriter_id": {"type": "string"},
                    "risk_characteristics": {"type": "object"},
                    "market_conditions": {"type": "object"}
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "appetite_level": {"type": "string", "enum": ["high", "medium", "low", "none"]},
                    "appetite_factors": {"type": "object"},
                    "preferred_terms": {"type": "object"},
                    "pricing_expectations": {"type": "object"}
                }
            }
        ),

        # 49. validate_underwriter_performance
        Tool(
            tool_name="validate_underwriter_performance",
            tool_description="Validate underwriter past performance and track record",
            input_schema={
                "type": "object",
                "required": ["underwriter_id", "performance_period"],
                "properties": {
                    "underwriter_id": {"type": "string"},
                    "performance_period": {"type": "object"},
                    "performance_metrics": {"type": "array"}
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "performance_score": {"type": "number"},
                    "claims_ratio": {"type": "number"},
                    "profitability": {"type": "object"},
                    "service_quality": {"type": "object"},
                    "market_reputation": {"type": "string"}
                }
            }
        ),

        # 50. generate_underwriter_recommendation
        Tool(
            tool_name="generate_underwriter_recommendation",
            tool_description="Generate comprehensive underwriter recommendation report",
            input_schema={
                "type": "object",
                "required": ["evaluation_results", "business_requirements"],
                "properties": {
                    "evaluation_results": {"type": "object"},
                    "business_requirements": {"type": "object"},
                    "strategic_considerations": {"type": "object"}
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "primary_recommendation": {"type": "object"},
                    "alternative_recommendations": {"type": "array"},
                    "recommendation_rationale": {"type": "string"},
                    "implementation_plan": {"type": "object"},
                    "monitoring_requirements": {"type": "array"}
                }
            }
        )
    ]
    
    # Add underwriter tools to main list
    tools.extend(underwriter_tools)
    
    return tools

def main():
    """Main execution function to add shipping insurance service with 50 tools."""
    
    db = SessionLocal()
    
    try:
        print("Creating Shipping Insurance Agent Service with 50 Tools...")
        print("=" * 60)
        
        # Create the main service
        service = create_shipping_insurance_service()
        db.add(service)
        db.flush()  # Get the service ID
        
        print(f"✅ Created service: {service.name}")
        print(f"   Service ID: {service.id}")
        print(f"   Version: {service.version}")
        print(f"   Endpoint: {service.endpoint}")
        
        # Create service capabilities
        capabilities = create_service_capabilities()
        for capability in capabilities:
            capability.service_id = service.id
            db.add(capability)
        
        print(f"✅ Added {len(capabilities)} service capabilities")
        
        # Create service industries
        industries = create_service_industries()
        for industry in industries:
            industry.service_id = service.id
            db.add(industry)
        
        print(f"✅ Added {len(industries)} industry associations")
        
        # Create integration details
        integration = create_integration_details()
        integration.service_id = service.id
        db.add(integration)
        
        print("✅ Added integration details")
        
        # Create all 50 tools
        tools = create_shipping_insurance_tools()
        for tool in tools:
            tool.service_id = service.id
            db.add(tool)
        
        print(f"✅ Added {len(tools)} tools:")
        
        # Display tools by category
        tool_categories = {
            "Quotes": tools[0:10],
            "Risk Assessment": tools[10:20], 
            "Value Assessment": tools[20:28],
            "Limitations": tools[28:36],
            "Scope": tools[36:43],
            "Underwriter": tools[43:50]
        }
        
        for category, category_tools in tool_categories.items():
            print(f"   📊 {category} Tools ({len(category_tools)}):")
            for tool in category_tools:
                print(f"      - {tool.tool_name}")
        
        # Commit all changes
        db.commit()
        
        print("\n" + "=" * 60)
        print("🎉 SUCCESS! Shipping Insurance Service Added Successfully!")
        print("=" * 60)
        print(f"Service Name: {service.name}")
        print(f"Total Tools: {len(tools)}")
        print(f"Service ID: {service.id}")
        print(f"Database: kpath_enterprise")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Update the project status
        print("\n📝 Updating project status document...")
        update_project_status(service, tools)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def update_project_status(service, tools):
    """Update the project status document."""
    
    status_update = f"""

## Shipping Insurance Service Addition
### Status: COMPLETED ✅
### Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**NEW SERVICE ADDED:**
- **Service Name**: {service.name}
- **Service ID**: {service.id} 
- **Version**: {service.version}
- **Total Tools**: {len(tools)}
- **Endpoint**: {service.endpoint}

**TOOL BREAKDOWN:**
- Quote Generation: 10 tools
- Risk Assessment: 10 tools  
- Value Assessment: 8 tools
- Limitations Analysis: 8 tools
- Coverage Scope: 7 tools
- Underwriter Management: 7 tools

**CAPABILITIES ADDED:**
- Quote Generation - Real-time pricing and quote generation
- Risk Assessment - Comprehensive risk analysis across multiple dimensions
- Value Assessment - Accurate cargo and shipment valuation
- Coverage Analysis - Detailed coverage scope and limitations analysis
- Underwriter Management - Complete underwriter validation and selection
- Compliance Verification - International maritime and insurance regulations

**INTEGRATION DETAILS:**
- Authentication: Bearer Token (JWT)
- Rate Limit: 100 requests/minute
- Max Concurrent: 15 requests
- Protocol: HTTPS REST API
- Response Format: JSON
- Geographic Coverage: Worldwide
- Supported Currencies: USD, EUR, GBP, JPY

**DATABASE IMPACT:**
- 1 new service record
- 50 new tool records
- 6 new capability records
- 5 new industry association records
- 1 new integration details record

**NEXT STEPS:**
- Service is ready for API integration
- Tools available for search and orchestration
- Can be tested via tool search API
- Ready for frontend integration

"""
    
    try:
        with open('/Users/james/claude_development/kpath_enterprise/docs/project_status.txt', 'a') as f:
            f.write(status_update)
        print("✅ Project status document updated successfully")
    except Exception as e:
        print(f"⚠️  Warning: Could not update project status: {e}")

if __name__ == "__main__":
    main()
