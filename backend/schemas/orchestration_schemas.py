"""
Pydantic schemas for agent orchestration functionality
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class ToolBase(BaseModel):
    """Base schema for tool definitions"""
    tool_name: str = Field(..., description="Name of the tool")
    tool_description: str = Field(..., description="Description of what the tool does")
    input_schema: Dict[str, Any] = Field(..., description="JSON schema for tool input parameters")
    output_schema: Optional[Dict[str, Any]] = Field(None, description="JSON schema for tool output")
    example_calls: Optional[Dict[str, Any]] = Field(None, description="Example invocation patterns")
    validation_rules: Optional[Dict[str, Any]] = Field(None, description="Input validation rules")
    error_handling: Optional[Dict[str, Any]] = Field(None, description="Error handling configuration")
    tool_version: str = Field("1.0.0", description="Tool version")
    is_active: bool = Field(True, description="Whether the tool is active")
    deprecation_date: Optional[datetime] = Field(None, description="When the tool will be deprecated")
    deprecation_notice: Optional[str] = Field(None, description="Deprecation notice message")
    performance_metrics: Optional[Dict[str, Any]] = Field(None, description="Performance benchmarks")
    rate_limit_config: Optional[Dict[str, Any]] = Field(None, description="Rate limiting configuration")


class ToolCreate(ToolBase):
    """Schema for creating a new tool"""
    service_id: int = Field(..., description="ID of the service this tool belongs to")


class ToolUpdate(BaseModel):
    """Schema for updating an existing tool"""
    tool_name: Optional[str] = None
    tool_description: Optional[str] = None
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None
    example_calls: Optional[Dict[str, Any]] = None
    validation_rules: Optional[Dict[str, Any]] = None
    error_handling: Optional[Dict[str, Any]] = None
    tool_version: Optional[str] = None
    is_active: Optional[bool] = None
    deprecation_date: Optional[datetime] = None
    deprecation_notice: Optional[str] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    rate_limit_config: Optional[Dict[str, Any]] = None


class ToolResponse(ToolBase):
    """Schema for tool responses"""
    id: int
    service_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class InvocationLogBase(BaseModel):
    """Base schema for invocation logs"""
    initiator_agent: str = Field(..., description="Agent that initiated the invocation")
    target_agent: str = Field(..., description="Target agent that was invoked")
    tool_called: str = Field(..., description="Name of the tool that was called")
    input_parameters: Optional[Dict[str, Any]] = Field(None, description="Parameters sent to the tool")
    output_result: Optional[Dict[str, Any]] = Field(None, description="Result returned by the tool")
    success_status: bool = Field(..., description="Whether the invocation was successful")
    error_details: Optional[Dict[str, Any]] = Field(None, description="Error details if invocation failed")
    response_time_ms: Optional[int] = Field(None, description="Response time in milliseconds")
    invocation_start: datetime = Field(..., description="When the invocation started")
    invocation_end: Optional[datetime] = Field(None, description="When the invocation ended")
    session_id: Optional[str] = Field(None, description="Session ID for tracking")
    trace_id: Optional[str] = Field(None, description="Trace ID for distributed tracing")
    performance_metrics: Optional[Dict[str, Any]] = Field(None, description="Performance metrics")


class InvocationLogCreate(InvocationLogBase):
    """Schema for creating invocation logs"""
    target_service_id: int = Field(..., description="ID of the target service")
    tool_id: int = Field(..., description="ID of the tool that was invoked")
    user_id: Optional[int] = Field(None, description="ID of the user who initiated the invocation")


class InvocationLogResponse(InvocationLogBase):
    """Schema for invocation log responses"""
    id: int
    target_service_id: int
    tool_id: int
    user_id: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ServiceOrchestrationUpdate(BaseModel):
    """Schema for updating service orchestration metadata"""
    agent_protocol: Optional[str] = Field(None, description="Agent communication protocol")
    auth_type: Optional[str] = Field(None, description="Authentication type required")
    auth_config: Optional[Dict[str, Any]] = Field(None, description="Authentication configuration")
    tool_recommendations: Optional[Dict[str, Any]] = Field(None, description="Tool recommendation metadata")
    agent_capabilities: Optional[Dict[str, Any]] = Field(None, description="Agent capability definitions")
    communication_patterns: Optional[Dict[str, Any]] = Field(None, description="Communication patterns")
    orchestration_metadata: Optional[Dict[str, Any]] = Field(None, description="General orchestration metadata")


class AgentOrchestrationResponse(BaseModel):
    """Schema for agent orchestration API responses (future use)"""
    agent_id: str = Field(..., description="Unique identifier for the agent")
    agent_name: str = Field(..., description="Human-readable agent name")
    description: str = Field(..., description="Description of agent capabilities")
    recommended_tool: Dict[str, Any] = Field(..., description="Recommended tool with full schema")
    access_method: str = Field(..., description="How to access the agent (http, grpc, etc.)")
    endpoint: str = Field(..., description="Agent endpoint URL")
    auth_type: str = Field(..., description="Authentication type required")
    agent_protocol: str = Field(..., description="Communication protocol version")


class ToolInvocationRequest(BaseModel):
    """Schema for tool invocation requests"""
    tool: str = Field(..., description="Name of the tool to invoke")
    parameters: Dict[str, Any] = Field(..., description="Parameters for the tool")
    trace_id: Optional[str] = Field(None, description="Trace ID for request tracking")
    session_id: Optional[str] = Field(None, description="Session ID for context")


class ToolInvocationResponse(BaseModel):
    """Schema for tool invocation responses"""
    success: bool = Field(..., description="Whether the invocation was successful")
    result: Optional[Dict[str, Any]] = Field(None, description="Tool execution result")
    error: Optional[str] = Field(None, description="Error message if unsuccessful")
    response_time_ms: int = Field(..., description="Response time in milliseconds")
    trace_id: Optional[str] = Field(None, description="Trace ID for request tracking")


class OrchestrationAnalytics(BaseModel):
    """Schema for orchestration analytics data"""
    total_invocations: int = Field(..., description="Total number of tool invocations")
    successful_invocations: int = Field(..., description="Number of successful invocations")
    failed_invocations: int = Field(..., description="Number of failed invocations")
    average_response_time_ms: float = Field(..., description="Average response time")
    most_used_tools: List[Dict[str, Any]] = Field(..., description="Most frequently used tools")
    error_rate_percentage: float = Field(..., description="Error rate as percentage")
    top_initiator_agents: List[Dict[str, Any]] = Field(..., description="Most active initiator agents")
    performance_trends: Dict[str, Any] = Field(..., description="Performance trends over time")
