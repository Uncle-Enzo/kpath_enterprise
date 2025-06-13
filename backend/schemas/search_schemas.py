"""
Schemas for search and feedback operations
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


# Search schemas
class SearchRequest(BaseModel):
    """Schema for search request"""
    query: str = Field(..., min_length=1, max_length=1000)
    user_context: Optional[Dict[str, Any]] = None
    options: Optional[Dict[str, Any]] = Field(default_factory=dict)


class SearchOptions(BaseModel):
    """Schema for search options"""
    limit: int = Field(default=10, ge=1, le=100)
    min_score: float = Field(default=0.7, ge=0.0, le=1.0)
    include_feedback_boost: bool = True
    domains: Optional[List[str]] = None
    exclude_services: Optional[List[str]] = None


class ServiceSearchResult(BaseModel):
    """Schema for individual search result"""
    service: Dict[str, Any]
    capability: Optional[Dict[str, Any]] = None
    score: float
    feedback_boost: float = 0.0
    final_score: float
    runtime: Optional[Dict[str, Any]] = None


class SearchResponse(BaseModel):
    """Schema for search response"""
    query: str
    results: List[ServiceSearchResult]
    metadata: Dict[str, Any]


# Feedback schemas
class FeedbackLogCreate(BaseModel):
    """Schema for logging feedback"""
    search_id: str
    selected_service_id: int
    result_position: int = Field(..., ge=1)
    selection_time_ms: Optional[int] = Field(None, ge=0)
    user_action: str = "clicked"
    session_id: Optional[str] = None
    user_satisfaction: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class FeedbackResponse(BaseModel):
    """Schema for feedback response"""
    status: str
    feedback_id: str
    message: str


# Health check schemas
class HealthStatus(BaseModel):
    """Schema for health status"""
    status: str = Field(..., pattern="^(healthy|degraded|unhealthy)$")
    components: Dict[str, str]
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Authentication schemas
class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"
    user: Optional[Dict[str, Any]] = None


class TokenData(BaseModel):
    """Schema for token payload"""
    user_id: Optional[int] = None
    email: Optional[str] = None
    role: Optional[str] = None


class LoginRequest(BaseModel):
    """Schema for login request"""
    email: str
    password: str
