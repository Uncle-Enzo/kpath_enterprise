"""
Enterprise integration schemas for services
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


# Integration Details Schemas
class ServiceIntegrationDetailsBase(BaseModel):
    """Base schema for service integration details"""
    access_protocol: str = Field(..., max_length=50)
    base_endpoint: Optional[str] = None
    
    # Authentication
    auth_method: Optional[str] = Field(None, max_length=50)
    auth_config: Optional[Dict[str, Any]] = None
    auth_endpoint: Optional[str] = None
    
    # Rate Limiting & Performance
    rate_limit_requests: Optional[int] = None
    rate_limit_window_seconds: Optional[int] = None
    max_concurrent_requests: Optional[int] = None
    circuit_breaker_config: Optional[Dict[str, Any]] = None
    
    # Request/Response Configuration
    default_headers: Optional[Dict[str, Any]] = None
    request_content_type: str = Field(default="application/json", max_length=100)
    response_content_type: str = Field(default="application/json", max_length=100)
    request_transform: Optional[Dict[str, Any]] = None
    response_transform: Optional[Dict[str, Any]] = None
    
    # ESB Specific Fields
    esb_type: Optional[str] = Field(None, max_length=50)
    esb_service_name: Optional[str] = None
    esb_routing_key: Optional[str] = None
    esb_operation: Optional[str] = None
    esb_adapter_type: Optional[str] = Field(None, max_length=50)
    esb_namespace: Optional[str] = None
    esb_version: Optional[str] = Field(None, max_length=20)
    
    # Health Check
    health_check_endpoint: Optional[str] = None
    health_check_interval_seconds: Optional[int] = None


class ServiceIntegrationDetailsCreate(ServiceIntegrationDetailsBase):
    """Schema for creating integration details"""
    pass


class ServiceIntegrationDetailsUpdate(BaseModel):
    """Schema for updating integration details"""
    access_protocol: Optional[str] = Field(None, max_length=50)
    base_endpoint: Optional[str] = None
    auth_method: Optional[str] = Field(None, max_length=50)
    auth_config: Optional[Dict[str, Any]] = None
    auth_endpoint: Optional[str] = None
    rate_limit_requests: Optional[int] = None
    rate_limit_window_seconds: Optional[int] = None
    max_concurrent_requests: Optional[int] = None
    circuit_breaker_config: Optional[Dict[str, Any]] = None
    default_headers: Optional[Dict[str, Any]] = None
    request_content_type: Optional[str] = Field(None, max_length=100)
    response_content_type: Optional[str] = Field(None, max_length=100)
    request_transform: Optional[Dict[str, Any]] = None
    response_transform: Optional[Dict[str, Any]] = None
    esb_type: Optional[str] = Field(None, max_length=50)
    esb_service_name: Optional[str] = None
    esb_routing_key: Optional[str] = None
    esb_operation: Optional[str] = None
    esb_adapter_type: Optional[str] = Field(None, max_length=50)
    esb_namespace: Optional[str] = None
    esb_version: Optional[str] = Field(None, max_length=20)
    health_check_endpoint: Optional[str] = None
    health_check_interval_seconds: Optional[int] = None


class ServiceIntegrationDetails(ServiceIntegrationDetailsBase):
    """Schema for integration details response"""
    id: int
    service_id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Agent Protocol Schemas
class ServiceAgentProtocolsBase(BaseModel):
    """Base schema for agent protocols"""
    message_protocol: str = Field(..., max_length=50)
    protocol_version: Optional[str] = Field(None, max_length=20)
    expected_input_format: Optional[str] = None
    response_style: Optional[str] = Field(None, max_length=50)
    
    # Communication Details
    message_examples: Optional[Dict[str, Any]] = None
    tool_schema: Optional[Dict[str, Any]] = None
    input_validation_rules: Optional[Dict[str, Any]] = None
    output_parsing_rules: Optional[Dict[str, Any]] = None
    
    # Capabilities
    requires_session_state: bool = False
    max_context_length: Optional[int] = None
    supported_languages: Optional[List[str]] = None
    supports_streaming: bool = False
    supports_async: bool = False
    supports_batch: bool = False


class ServiceAgentProtocolsCreate(ServiceAgentProtocolsBase):
    """Schema for creating agent protocols"""
    pass


class ServiceAgentProtocolsUpdate(BaseModel):
    """Schema for updating agent protocols"""
    message_protocol: Optional[str] = Field(None, max_length=50)
    protocol_version: Optional[str] = Field(None, max_length=20)
    expected_input_format: Optional[str] = None
    response_style: Optional[str] = Field(None, max_length=50)
    message_examples: Optional[Dict[str, Any]] = None
    tool_schema: Optional[Dict[str, Any]] = None
    input_validation_rules: Optional[Dict[str, Any]] = None
    output_parsing_rules: Optional[Dict[str, Any]] = None
    requires_session_state: Optional[bool] = None
    max_context_length: Optional[int] = None
    supported_languages: Optional[List[str]] = None
    supports_streaming: Optional[bool] = None
    supports_async: Optional[bool] = None
    supports_batch: Optional[bool] = None


class ServiceAgentProtocols(ServiceAgentProtocolsBase):
    """Schema for agent protocols response"""
    id: int
    service_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Service Industries Schemas
class ServiceIndustriesBase(BaseModel):
    """Base schema for service industries"""
    industry: str = Field(..., max_length=100)
    sub_industry: Optional[str] = Field(None, max_length=100)
    use_case_category: Optional[str] = Field(None, max_length=100)
    
    # Use Case Details
    use_case_description: Optional[str] = None
    business_value: Optional[str] = None
    typical_consumers: Optional[List[str]] = None
    
    # Relevance & Priority
    relevance_score: Optional[int] = Field(None, ge=0, le=100)
    priority_rank: Optional[int] = Field(None, ge=0)
    compliance_frameworks: Optional[List[str]] = None


class ServiceIndustriesCreate(ServiceIndustriesBase):
    """Schema for creating service industries"""
    pass


class ServiceIndustriesUpdate(BaseModel):
    """Schema for updating service industries"""
    industry: Optional[str] = Field(None, max_length=100)
    sub_industry: Optional[str] = Field(None, max_length=100)
    use_case_category: Optional[str] = Field(None, max_length=100)
    use_case_description: Optional[str] = None
    business_value: Optional[str] = None
    typical_consumers: Optional[List[str]] = None
    relevance_score: Optional[int] = Field(None, ge=0, le=100)
    priority_rank: Optional[int] = Field(None, ge=0)
    compliance_frameworks: Optional[List[str]] = None


class ServiceIndustries(ServiceIndustriesBase):
    """Schema for service industries response"""
    id: int
    service_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
