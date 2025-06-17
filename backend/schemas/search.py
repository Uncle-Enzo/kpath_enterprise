"""
Search-related Pydantic schemas for KPATH Enterprise.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class SearchRequest(BaseModel):
    """Request schema for semantic search."""
    
    query: str = Field(..., description="Natural language search query", min_length=1)
    limit: int = Field(10, description="Maximum number of results to return", ge=1, le=100)
    min_score: float = Field(0.0, description="Minimum similarity score", ge=0.0, le=1.0)
    domains: Optional[List[str]] = Field(None, description="Filter by specific domains")
    capabilities: Optional[List[str]] = Field(None, description="Filter by specific capabilities")
    include_orchestration: bool = Field(False, description="Include agent orchestration data (tools, schemas, examples)")
    search_mode: Optional[str] = Field(
        "agents_only",
        description="Search mode: agents_only (default), tools_only, agents_and_tools, workflows, capabilities",
        pattern="^(agents_only|tools_only|agents_and_tools|workflows|capabilities)$"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "customer data management service",
                "limit": 10,
                "min_score": 0.1,
                "domains": ["finance", "crm"],
                "capabilities": ["data_processing", "api_integration"],
                "include_orchestration": True,
                "search_mode": "agents_only"
            }
        }


class SearchResultSchema(BaseModel):
    """Schema for individual search result."""
    
    service_id: int = Field(..., description="Service ID")
    score: float = Field(..., description="Similarity score (0-1)", ge=0.0, le=1.0)
    rank: Optional[int] = Field(None, description="Result rank (1-based)")
    service: Dict[str, Any] = Field(..., description="Service data")
    distance: Optional[float] = Field(None, description="Vector distance (if available)")
    entity_type: Optional[str] = Field("service", description="Entity type: service, service_with_tool, workflow, capability")
    tool_data: Optional[Dict[str, Any]] = Field(None, description="Tool data if entity_type is 'tool' (deprecated)")
    recommended_tool: Optional[Dict[str, Any]] = Field(None, description="Recommended tool for the task when using tools_only search mode")
    workflow_data: Optional[Dict[str, Any]] = Field(None, description="Workflow data if entity_type is 'workflow'")
    
    class Config:
        json_schema_extra = {
            "example": {
                "service_id": 123,
                "score": 0.85,
                "rank": 1,
                "service": {
                    "id": 123,
                    "name": "Customer Data API",
                    "description": "Manages customer data and profiles",
                    "status": "active",
                    "capabilities": ["data_processing", "api_integration"],
                    "domains": ["crm", "finance"],
                    "tags": ["customer", "data", "api"]
                },
                "distance": 0.15
            }
        }


class SearchResponse(BaseModel):
    """Response schema for search results."""
    
    query: str = Field(..., description="Original search query")
    results: List[SearchResultSchema] = Field(..., description="Search results")
    total_results: int = Field(..., description="Total number of results returned")
    search_time_ms: float = Field(..., description="Search execution time in milliseconds")
    user_id: int = Field(..., description="ID of user who performed the search")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Search timestamp")
    search_mode: str = Field("agents_only", description="Search mode used for this query")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "customer data management service",
                "results": [
                    {
                        "service_id": 123,
                        "score": 0.85,
                        "rank": 1,
                        "service": {
                            "id": 123,
                            "name": "Customer Data API",
                            "description": "Manages customer data and profiles",
                            "status": "active",
                            "capabilities": ["data_processing"],
                            "domains": ["crm"],
                            "tags": ["customer", "data"]
                        }
                    }
                ],
                "total_results": 1,
                "search_time_ms": 45.2,
                "user_id": 1,
                "timestamp": "2025-06-12T10:30:00Z"
            }
        }


class ToolSearchResult(BaseModel):
    """Schema for tool search result."""
    
    tool_id: int = Field(..., description="Tool ID")
    tool_name: str = Field(..., description="Tool name")
    tool_description: str = Field(..., description="Tool description")
    parent_service_id: int = Field(..., description="Parent service ID")
    parent_service_name: str = Field(..., description="Parent service name")
    score: float = Field(..., description="Similarity score (0-1)", ge=0.0, le=1.0)
    rank: Optional[int] = Field(None, description="Result rank (1-based)")
    input_schema: Optional[Dict[str, Any]] = Field(None, description="Tool input schema")
    output_schema: Optional[Dict[str, Any]] = Field(None, description="Tool output schema")
    example_calls: Optional[List[Dict[str, Any]]] = Field(None, description="Example tool calls")
    
    class Config:
        json_schema_extra = {
            "example": {
                "tool_id": 5,
                "tool_name": "send_email",
                "tool_description": "Send email notifications to users",
                "parent_service_id": 3,
                "parent_service_name": "NotificationService",
                "score": 0.92,
                "rank": 1,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "to": {"type": "string"},
                        "subject": {"type": "string"},
                        "body": {"type": "string"}
                    }
                }
            }
        }


class WorkflowSearchResult(BaseModel):
    """Schema for workflow search result."""
    
    workflow_id: str = Field(..., description="Workflow identifier")
    workflow_name: str = Field(..., description="Workflow name")
    workflow_description: str = Field(..., description="Workflow description")
    steps: List[Dict[str, Any]] = Field(..., description="Workflow steps")
    involved_services: List[int] = Field(..., description="Service IDs involved in workflow")
    involved_tools: List[int] = Field(..., description="Tool IDs involved in workflow")
    score: float = Field(..., description="Similarity score (0-1)", ge=0.0, le=1.0)
    rank: Optional[int] = Field(None, description="Result rank (1-based)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "workflow_id": "customer_onboarding_v1",
                "workflow_name": "Customer Onboarding",
                "workflow_description": "Complete customer onboarding process",
                "steps": [
                    {"service_id": 1, "tool": "create_account", "order": 1},
                    {"service_id": 3, "tool": "send_welcome_email", "order": 2}
                ],
                "involved_services": [1, 3],
                "involved_tools": [1, 5],
                "score": 0.88,
                "rank": 1
            }
        }


class SearchStatusResponse(BaseModel):
    """Response schema for search service status."""
    
    initialized: bool = Field(..., description="Whether search service is initialized")
    index_built: bool = Field(..., description="Whether search index is built")
    embedding_service: Dict[str, Any] = Field(..., description="Embedding service status")
    search_service: Dict[str, Any] = Field(..., description="Search service status")
    files: Dict[str, Any] = Field(..., description="File status information")
    
    class Config:
        json_schema_extra = {
            "example": {
                "initialized": True,
                "index_built": True,
                "embedding_service": {
                    "type": "TFIDFEmbedder",
                    "fitted": True,
                    "dimension": 384,
                    "vocabulary_size": 5000
                },
                "search_service": {
                    "type": "FAISSSearchService",
                    "initialized": True,
                    "num_services": 25,
                    "faiss_available": True
                },
                "files": {
                    "model_exists": True,
                    "index_exists": True,
                    "model_path": "data/models/embedding_model.pkl",
                    "index_path": "data/indexes/search_index.pkl"
                }
            }
        }


class IndexRebuildRequest(BaseModel):
    """Request schema for index rebuild."""
    
    force: bool = Field(False, description="Force rebuild even if index exists")
    
    class Config:
        json_schema_extra = {
            "example": {
                "force": True
            }
        }


class SimilarServicesResponse(BaseModel):
    """Response schema for similar services query."""
    
    target_service_id: int = Field(..., description="ID of the target service")
    similar_services: List[SearchResultSchema] = Field(..., description="Similar services")
    total_results: int = Field(..., description="Number of similar services found")
    
    class Config:
        json_schema_extra = {
            "example": {
                "target_service_id": 123,
                "similar_services": [
                    {
                        "service_id": 124,
                        "score": 0.78,
                        "rank": 1,
                        "service": {
                            "id": 124,
                            "name": "Profile Management API",
                            "description": "Handles user profiles and preferences",
                            "status": "active",
                            "capabilities": ["data_processing"],
                            "domains": ["crm"],
                            "tags": ["profile", "user"]
                        }
                    }
                ],
                "total_results": 1
            }
        }


class SearchFeedbackRequest(BaseModel):
    """Schema for search result feedback."""
    
    query: str = Field(..., description="Original search query")
    service_id: int = Field(..., description="Service ID that was selected/clicked")
    rank: int = Field(..., description="Rank of the selected result")
    feedback_type: str = Field(..., description="Type of feedback", pattern="^(click|select|relevant|not_relevant)$")
    score: Optional[float] = Field(None, description="User rating if applicable", ge=0.0, le=5.0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "customer data management service",
                "service_id": 123,
                "rank": 1,
                "feedback_type": "click",
                "score": 4.5
            }
        }
