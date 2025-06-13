"""
SQLAlchemy models for KPATH Enterprise
"""
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey, Integer, 
    String, Text, JSON, ARRAY, UniqueConstraint, CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.core.database import Base


class Service(Base):
    """Core service registry"""
    __tablename__ = "services"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=False)
    endpoint = Column(Text)
    version = Column(String)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    capabilities = relationship("ServiceCapability", back_populates="service", cascade="all, delete-orphan")
    interactions = relationship("InteractionCapability", back_populates="service", cascade="all, delete-orphan")
    industries = relationship("ServiceIndustry", back_populates="service", cascade="all, delete-orphan")
    policies = relationship("AccessPolicy", back_populates="service", cascade="all, delete-orphan")
    versions = relationship("ServiceVersion", back_populates="service", cascade="all, delete-orphan")
    health_records = relationship("ServiceHealth", back_populates="service", cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint("status IN ('active', 'inactive', 'deprecated')", name="check_service_status"),
    )


class ServiceCapability(Base):
    """Individual capabilities exposed by services"""
    __tablename__ = "service_capability"
    
    id = Column(Integer, primary_key=True)
    service_id = Column(Integer, ForeignKey("services.id", ondelete="CASCADE"), nullable=False)
    capability_desc = Column(Text, nullable=False)
    capability_name = Column(String)
    input_schema = Column(JSON)
    output_schema = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    service = relationship("Service", back_populates="capabilities")


class InteractionCapability(Base):
    """Interaction patterns for services"""
    __tablename__ = "interaction_capability"
    
    id = Column(Integer, primary_key=True)
    service_id = Column(Integer, ForeignKey("services.id", ondelete="CASCADE"), nullable=False)
    interaction_desc = Column(Text, nullable=False)
    interaction_type = Column(String)
    
    # Relationships
    service = relationship("Service", back_populates="interactions")
    
    __table_args__ = (
        CheckConstraint("interaction_type IN ('sync', 'async', 'stream', 'batch')", 
                       name="check_interaction_type"),
    )


class ServiceIndustry(Base):
    """Domain classification for services"""
    __tablename__ = "service_industry"
    
    id = Column(Integer, primary_key=True)
    service_id = Column(Integer, ForeignKey("services.id", ondelete="CASCADE"), nullable=False)
    domain = Column(String, nullable=False)
    
    # Relationships
    service = relationship("Service", back_populates="industries")
    
    __table_args__ = (
        UniqueConstraint("service_id", "domain", name="uq_service_domain"),
    )


class User(Base):
    """System users"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    role = Column(String)
    org_id = Column(Integer)
    attributes = Column(JSON, default={})
    password_hash = Column(String)  # Added for authentication
    is_active = Column(Boolean, default=True)  # Add is_active field
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    audit_logs = relationship("AuditLog", back_populates="user")
    feedback_logs = relationship("FeedbackLog", back_populates="user")
    api_keys = relationship("APIKey", back_populates="user")
    query_templates = relationship("QueryTemplate", back_populates="creator")
    
    __table_args__ = (
        CheckConstraint("role IN ('admin', 'editor', 'viewer', 'user')", name="check_user_role"),
    )


class AccessPolicy(Base):
    """Access control policies"""
    __tablename__ = "access_policy"
    
    id = Column(Integer, primary_key=True)
    service_id = Column(Integer, ForeignKey("services.id", ondelete="CASCADE"))
    conditions = Column(JSON, nullable=False)
    type = Column(String)
    priority = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    service = relationship("Service", back_populates="policies")
    
    __table_args__ = (
        CheckConstraint("type IN ('RBAC', 'ABAC')", name="check_policy_type"),
    )


class FAISSIndexMetadata(Base):
    """Metadata about FAISS indexes"""
    __tablename__ = "faiss_index_metadata"
    
    id = Column(Integer, primary_key=True)
    index_name = Column(String)
    last_updated = Column(DateTime)
    embedding_model = Column(String)
    total_vectors = Column(Integer)
    index_params = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    """Audit trail for system actions"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    action = Column(String, nullable=False)
    payload = Column(JSON)
    ip_address = Column(INET)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")


class FeedbackLog(Base):
    """User feedback for search improvements"""
    __tablename__ = "feedback_log"
    
    id = Column(Integer, primary_key=True)
    query = Column(Text, nullable=False)
    query_embedding_hash = Column(String)
    selected_service_id = Column(Integer, ForeignKey("services.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))
    rank_position = Column(Integer)
    click_through = Column(Boolean, default=True)
    
    # Relationships
    selected_service = relationship("Service")
    user = relationship("User", back_populates="feedback_logs")


class CacheEntry(Base):
    """Cache storage"""
    __tablename__ = "cache_entries"
    
    key = Column(String, primary_key=True)
    value = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    hit_count = Column(Integer, default=0)


class ServiceVersion(Base):
    """Service version management"""
    __tablename__ = "service_versions"
    
    id = Column(Integer, primary_key=True)
    service_id = Column(Integer, ForeignKey("services.id"))
    version = Column(String, nullable=False)
    version_tag = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    deprecated = Column(Boolean, default=False)
    deprecated_at = Column(DateTime)
    sunset_at = Column(DateTime)
    compatible_with = Column(ARRAY(String))
    breaking_changes = Column(ARRAY(String))
    migration_notes = Column(Text)
    release_notes = Column(Text)
    
    # Relationships
    service = relationship("Service", back_populates="versions")
    
    __table_args__ = (
        UniqueConstraint("service_id", "version", name="uq_service_version"),
        CheckConstraint("version_tag IN ('stable', 'beta', 'alpha', 'deprecated')", 
                       name="check_version_tag"),
    )


class ServiceHealth(Base):
    """Service health monitoring records"""
    __tablename__ = "service_health"
    
    id = Column(Integer, primary_key=True)
    service_id = Column(Integer, ForeignKey("services.id"))
    health_status = Column(String)
    last_check = Column(DateTime)
    response_time_ms = Column(Integer)
    error_count = Column(Integer, default=0)
    consecutive_failures = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    service = relationship("Service", back_populates="health_records")
    
    __table_args__ = (
        CheckConstraint("health_status IN ('healthy', 'degraded', 'unhealthy', 'unknown')", 
                       name="check_health_status"),
    )


class APIKey(Base):
    """API key management"""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True)
    key_hash = Column(String, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    scopes = Column(ARRAY(String))
    expires_at = Column(DateTime)
    last_used = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")


class QueryTemplate(Base):
    """Reusable query templates"""
    __tablename__ = "query_templates"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    template = Column(Text, nullable=False)
    parameters = Column(JSON)
    description = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"))
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    creator = relationship("User", back_populates="query_templates")


class IntegrationConfig(Base):
    """External integration configurations"""
    __tablename__ = "integration_configs"
    
    id = Column(Integer, primary_key=True)
    type = Column(String, nullable=False)
    name = Column(String, nullable=False)
    config = Column(JSON, nullable=False)
    enabled = Column(Boolean, default=True)
    last_sync = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint("type", "name", name="uq_integration_type_name"),
    )


class UserSelection(Base):
    """Enhanced user selection tracking"""
    __tablename__ = "user_selections"
    
    id = Column(Integer, primary_key=True)
    search_id = Column(UUID(as_uuid=True), default=func.uuid_generate_v4())
    query = Column(Text, nullable=False)
    query_embedding_hash = Column(String)
    selected_service_id = Column(Integer, ForeignKey("services.id"))
    result_position = Column(Integer, nullable=False)
    selection_time_ms = Column(Integer)
    session_id = Column(UUID(as_uuid=True))
    user_satisfaction = Column(Boolean)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    selected_service = relationship("Service")
