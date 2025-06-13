"""
Pydantic schemas for API validation
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# Base schemas
class ServiceBase(BaseModel):
    """Base schema for services"""
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    endpoint: Optional[str] = None
    version: Optional[str] = None
    status: str = Field(default="active", pattern="^(active|inactive|deprecated)$")


class ServiceCreate(ServiceBase):
    """Schema for creating a service"""
    pass


class ServiceUpdate(BaseModel):
    """Schema for updating a service"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    endpoint: Optional[str] = None
    version: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(active|inactive|deprecated)$")


class ServiceCapabilityBase(BaseModel):
    """Base schema for service capabilities"""
    capability_name: Optional[str] = None
    capability_desc: str = Field(..., min_length=1)
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None


class ServiceCapabilityCreate(ServiceCapabilityBase):
    """Schema for creating a capability"""
    service_id: int


class ServiceCapability(ServiceCapabilityBase):
    """Schema for capability response"""
    id: int
    service_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ServiceIndustryBase(BaseModel):
    """Base schema for service industry/domain"""
    domain: str = Field(..., min_length=1)


class ServiceIndustry(ServiceIndustryBase):
    """Schema for industry response"""
    id: int
    service_id: int
    
    model_config = ConfigDict(from_attributes=True)


class Service(ServiceBase):
    """Schema for service response"""
    id: int
    created_at: datetime
    updated_at: datetime
    capabilities: List[ServiceCapability] = []
    industries: List[ServiceIndustry] = []
    
    model_config = ConfigDict(from_attributes=True)


class ServiceList(BaseModel):
    """Schema for paginated service list"""
    items: List[Service]
    total: int
    skip: int
    limit: int


# User schemas
class UserBase(BaseModel):
    """Base schema for users"""
    email: EmailStr
    role: str = Field(..., pattern="^(admin|editor|viewer|user)$")
    org_id: Optional[int] = None
    attributes: Optional[Dict[str, Any]] = Field(default_factory=dict)


class UserCreate(UserBase):
    """Schema for creating a user"""
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    email: Optional[EmailStr] = None
    role: Optional[str] = Field(None, pattern="^(admin|editor|viewer|user)$")
    org_id: Optional[int] = None
    attributes: Optional[Dict[str, Any]] = None
    password: Optional[str] = Field(None, min_length=8)


class User(UserBase):
    """Schema for user response"""
    id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool = True  # Add default value
    username: Optional[str] = None  # Add optional username field
    
    model_config = ConfigDict(from_attributes=True)


# Access Policy schemas
class AccessPolicyBase(BaseModel):
    """Base schema for access policies"""
    service_id: int
    conditions: Dict[str, Any]
    type: str = Field(..., pattern="^(RBAC|ABAC)$")
    priority: int = Field(default=0, ge=0)


class AccessPolicyCreate(AccessPolicyBase):
    """Schema for creating an access policy"""
    pass


class AccessPolicy(AccessPolicyBase):
    """Schema for access policy response"""
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
