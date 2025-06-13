"""
Unit tests for database models
"""
import pytest
from datetime import datetime

from backend.models import (
    Service, ServiceCapability, ServiceIndustry,
    User, AccessPolicy
)


class TestServiceModel:
    """Test Service model"""
    
    def test_create_service(self, db_session):
        """Test creating a service"""
        service = Service(
            name="TestService",
            description="Test service description",
            endpoint="https://api.test.com",
            version="1.0.0",
            status="active"
        )
        
        db_session.add(service)
        db_session.commit()
        
        assert service.id is not None
        assert service.name == "TestService"
        assert service.created_at is not None
        assert service.updated_at is not None
    
    def test_service_relationships(self, db_session):
        """Test service relationships"""
        service = Service(
            name="RelationshipTest",
            description="Testing relationships"
        )
        db_session.add(service)
        db_session.flush()
        
        # Add capability
        capability = ServiceCapability(
            service_id=service.id,
            capability_name="TestCapability",
            capability_desc="Test capability description"
        )
        db_session.add(capability)
        
        # Add industry
        industry = ServiceIndustry(
            service_id=service.id,
            domain="Testing"
        )
        db_session.add(industry)
        
        db_session.commit()
        
        # Test relationships
        assert len(service.capabilities) == 1
        assert service.capabilities[0].capability_name == "TestCapability"
        assert len(service.industries) == 1
        assert service.industries[0].domain == "Testing"
    
    def test_service_status_constraint(self, db_session):
        """Test service status constraint"""
        with pytest.raises(Exception):  # Should raise constraint violation
            service = Service(
                name="BadStatus",
                description="Invalid status",
                status="invalid_status"  # Not in allowed values
            )
            db_session.add(service)
            db_session.commit()


class TestUserModel:
    """Test User model"""
    
    def test_create_user(self, db_session):
        """Test creating a user"""
        user = User(
            email="test@example.com",
            role="user",
            attributes={"department": "Testing"}
        )
        
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.attributes["department"] == "Testing"
    
    def test_user_role_constraint(self, db_session):
        """Test user role constraint"""
        with pytest.raises(Exception):  # Should raise constraint violation
            user = User(
                email="bad@example.com",
                role="invalid_role"  # Not in allowed values
            )
            db_session.add(user)
            db_session.commit()


class TestAccessPolicyModel:
    """Test AccessPolicy model"""
    
    def test_create_policy(self, db_session):
        """Test creating an access policy"""
        # First create a service
        service = Service(
            name="PolicyTestService",
            description="Service for policy testing"
        )
        db_session.add(service)
        db_session.flush()
        
        # Create policy
        policy = AccessPolicy(
            service_id=service.id,
            conditions={"allowed_roles": ["admin", "editor"]},
            type="RBAC",
            priority=10
        )
        
        db_session.add(policy)
        db_session.commit()
        
        assert policy.id is not None
        assert policy.conditions["allowed_roles"] == ["admin", "editor"]
        assert policy.type == "RBAC"
        assert policy.priority == 10
