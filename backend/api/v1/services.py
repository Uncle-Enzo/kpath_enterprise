"""
Service management endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.auth import get_current_active_user, require_role
from backend.models import User, Service as ServiceModel
from backend.services import ServiceCRUD
from backend.schemas import (
    Service, ServiceCreate, ServiceUpdate, ServiceList,
    ServiceCapabilityCreate, ServiceCapability
)

router = APIRouter(tags=["services"])


@router.get("/", response_model=ServiceList)
async def list_services(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all services with pagination"""
    services = ServiceCRUD.get_services(db, skip=skip, limit=limit, status=status)
    
    # Get total count with same filters
    query = db.query(ServiceModel)
    if status:
        query = query.filter(ServiceModel.status == status)
    total = query.count()
    
    return {
        "items": services,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/{service_id}", response_model=Service)
async def get_service(
    service_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific service by ID"""
    service = ServiceCRUD.get_service(db, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service


@router.post("/", response_model=Service)
async def create_service(
    service_data: ServiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Create a new service (admin only)"""
    # Check if service name already exists
    existing = ServiceCRUD.get_service_by_name(db, service_data.name)
    if existing:
        raise HTTPException(
            status_code=400, 
            detail="Service with this name already exists"
        )
    
    service = ServiceCRUD.create_service(
        db,
        name=service_data.name,
        description=service_data.description,
        endpoint=service_data.endpoint,
        version=service_data.version,
        status=service_data.status
    )
    return service


@router.put("/{service_id}", response_model=Service)
async def update_service(
    service_id: int,
    service_data: ServiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Update a service (admin only)"""
    service = ServiceCRUD.update_service(
        db,
        service_id,
        **service_data.model_dump(exclude_unset=True)
    )
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service


@router.delete("/{service_id}")
async def delete_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Delete a service (admin only)"""
    result = ServiceCRUD.delete_service(db, service_id)
    if not result:
        raise HTTPException(status_code=404, detail="Service not found")
    return {"message": "Service deleted successfully"}


@router.post("/{service_id}/capabilities", response_model=ServiceCapability)
async def add_capability(
    service_id: int,
    capability_data: ServiceCapabilityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Add a capability to a service (admin only)"""
    capability = ServiceCRUD.add_capability(
        db,
        service_id,
        capability_name=capability_data.capability_name,
        capability_desc=capability_data.capability_desc,
        input_schema=capability_data.input_schema,
        output_schema=capability_data.output_schema
    )
    if not capability:
        raise HTTPException(status_code=404, detail="Service not found")
    return capability


@router.post("/{service_id}/domains")
async def add_domain(
    service_id: int,
    domain: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Add a domain to a service (admin only)"""
    industry = ServiceCRUD.add_domain(db, service_id, domain)
    if not industry:
        raise HTTPException(status_code=404, detail="Service not found")
    return {"message": f"Domain '{domain}' added successfully"}
