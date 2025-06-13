"""
Service CRUD operations
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from backend.models import Service, ServiceCapability, ServiceIndustry


class ServiceCRUD:
    """CRUD operations for services"""
    
    @staticmethod
    def create_service(
        db: Session,
        name: str,
        description: str,
        endpoint: Optional[str] = None,
        version: Optional[str] = None,
        status: str = "active",
        tool_type: str = "API",
        interaction_modes: Optional[List[str]] = None,
        visibility: str = "internal",
        deprecation_date: Optional[datetime] = None,
        deprecation_notice: Optional[str] = None,
        success_criteria: Optional[dict] = None,
        default_timeout_ms: int = 30000,
        default_retry_policy: Optional[dict] = None
    ) -> Service:
        """Create a new service"""
        service = Service(
            name=name,
            description=description,
            endpoint=endpoint,
            version=version,
            status=status,
            tool_type=tool_type,
            interaction_modes=interaction_modes,
            visibility=visibility,
            deprecation_date=deprecation_date,
            deprecation_notice=deprecation_notice,
            success_criteria=success_criteria,
            default_timeout_ms=default_timeout_ms,
            default_retry_policy=default_retry_policy
        )
        db.add(service)
        db.commit()
        db.refresh(service)
        return service
    
    @staticmethod
    def get_service(db: Session, service_id: int) -> Optional[Service]:
        """Get service by ID"""
        return db.query(Service).filter(Service.id == service_id).first()
    
    @staticmethod
    def get_service_by_name(db: Session, name: str) -> Optional[Service]:
        """Get service by name"""
        return db.query(Service).filter(Service.name == name).first()
    
    @staticmethod
    def get_services(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[Service]:
        """Get list of services with optional filtering"""
        query = db.query(Service)
        
        if status:
            query = query.filter(Service.status == status)
            
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update_service(
        db: Session,
        service_id: int,
        **kwargs
    ) -> Optional[Service]:
        """Update service attributes"""
        service = db.query(Service).filter(Service.id == service_id).first()
        
        if not service:
            return None
            
        for key, value in kwargs.items():
            if hasattr(service, key) and value is not None:
                setattr(service, key, value)
                
        db.commit()
        db.refresh(service)
        return service
    
    @staticmethod
    def delete_service(db: Session, service_id: int) -> bool:
        """Delete a service (cascades to related records)"""
        service = db.query(Service).filter(Service.id == service_id).first()
        
        if not service:
            return False
            
        db.delete(service)
        db.commit()
        return True
    
    @staticmethod
    def add_capability(
        db: Session,
        service_id: int,
        capability_name: str,
        capability_desc: str,
        input_schema: Optional[dict] = None,
        output_schema: Optional[dict] = None
    ) -> Optional[ServiceCapability]:
        """Add a capability to a service"""
        service = db.query(Service).filter(Service.id == service_id).first()
        
        if not service:
            return None
            
        capability = ServiceCapability(
            service_id=service_id,
            capability_name=capability_name,
            capability_desc=capability_desc,
            input_schema=input_schema,
            output_schema=output_schema
        )
        
        db.add(capability)
        db.commit()
        db.refresh(capability)
        return capability
    
    @staticmethod
    def add_domain(
        db: Session,
        service_id: int,
        domain: str
    ) -> Optional[ServiceIndustry]:
        """Add a domain/industry classification to a service"""
        # Check if already exists
        existing = db.query(ServiceIndustry).filter(
            and_(
                ServiceIndustry.service_id == service_id,
                ServiceIndustry.domain == domain
            )
        ).first()
        
        if existing:
            return existing
            
        industry = ServiceIndustry(
            service_id=service_id,
            domain=domain
        )
        
        db.add(industry)
        db.commit()
        db.refresh(industry)
        return industry
