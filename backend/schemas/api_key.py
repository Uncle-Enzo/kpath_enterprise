"""
API Key schemas for request/response models.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class APIKeyCreate(BaseModel):
    """Request model for creating an API key."""
    name: str = Field(..., description="Descriptive name for the API key")
    permissions: Optional[Dict[str, Any]] = Field(
        default={"search": True},
        description="JSON object defining permissions"
    )
    expires_in_days: Optional[int] = Field(
        None,
        ge=1,
        le=365,
        description="Number of days until the key expires"
    )
    rate_limit: Optional[int] = Field(
        1000,
        ge=1,
        le=10000,
        description="Maximum requests per hour"
    )


class APIKeyResponse(BaseModel):
    """Response model for API key creation."""
    api_key: str = Field(..., description="The actual API key (only shown once)")
    id: int
    name: str
    prefix: str = Field(..., description="First 8 characters of the key")
    permissions: Dict[str, Any]
    expires_at: Optional[str]
    created_at: str
    rate_limit: int


class APIKeyListResponse(BaseModel):
    """Response model for listing API keys."""
    id: int
    name: str
    prefix: str
    last_used: Optional[datetime]
    expires_at: Optional[datetime]
    created_at: datetime
    active: bool


class APIKeyUsageResponse(BaseModel):
    """Response model for API key usage statistics."""
    key_id: int
    total_requests: int
    requests_last_hour: int
    requests_today: int
    rate_limit: int
    endpoints_used: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of endpoints and their usage counts"
    )
    daily_usage: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Daily usage statistics"
    )