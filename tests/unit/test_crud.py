"""
Unit tests for CRUD operations
"""
import pytest

from backend.services.service_crud import ServiceCRUD
from backend.services.user_crud import UserCRUD
from backend.services.policy_crud import PolicyCRUD


class TestServiceCRUD:
    """Test ServiceCRUD operations"""
    
    def test_create_service(self, db_session):
        """Test creating a service via CRUD"""
        service = ServiceCRUD.create_service(
            db_session,
            name="CRUDTestService",
            description="Testing CRUD operations",
            endpoint="https://crud.test.com",
            version="1.0.0"
        )
        
        assert service.id is not None
        assert service.name == "CRUDTestService"
        assert service.status == "active"
    
    def test_get_service(self, db_session):
        """Test retrieving a service"""
        # Create service
        service = ServiceCRUD.create_service(
            db_session,
            name="GetTestService",
            description="Test get operation"
        )
        
        # Retrieve by ID
        retrieved = ServiceCRUD.get_service(db_session, service.id)
        assert retrieved is not None
        assert retrieved.id == service.id
        assert retrieved.name == "GetTestService"
        
        # Retrieve by name
        retrieved_by_name = ServiceCRUD.get_service_by_name(
            db_session, 
            "GetTestService"
        )
        assert retrieved_by_name is not None
        assert retrieved_by_name.id == service.id
    
    def test_update_service(self, db_session):
        """Test updating a service"""
        # Create service
        service = ServiceCRUD.create_service(
            db_session,
            name="UpdateTestService",
            description="Original description"
        )
        
        # Update
        updated = ServiceCRUD.update_service(
            db_session,
            service.id,
            description="Updated description",
            version="2.0.0"
        )
        
        assert updated is not None
        assert updated.description == "Updated description"
        assert updated.version == "2.0.0"
        assert updated.name == "UpdateTestService"  # Unchanged
    
    def test_delete_service(self, db_session):
        """Test deleting a service"""
        # Create service
        service = ServiceCRUD.create_service(
            db_session,
            name="DeleteTestService",
            description="To be deleted"
        )
        service_id = service.id
        
        # Delete
        result = ServiceCRUD.delete_service(db_session, service_id)
        assert result is True
        
        # Verify deletion
        deleted = ServiceCRUD.get_service(db_session, service_id)
        assert deleted is None
    
    def test_add_capability(self, db_session):
        """Test adding capability to service"""
        # Create service
        service = ServiceCRUD.create_service(
            db_session,
            name="CapabilityTestService",
            description="Testing capabilities"
        )
        
        # Add capability
        capability = ServiceCRUD.add_capability(
            db_session,
            service.id,
            capability_name="TestAction",
            capability_desc="Performs test action",
            input_schema={"type": "object"},
            output_schema={"type": "string"}
        )
        
        assert capability is not None
        assert capability.capability_name == "TestAction"
        assert capability.service_id == service.id
