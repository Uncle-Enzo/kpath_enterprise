"""
Service integration management endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.auth import get_current_active_user, require_role
from backend.models import User, ServiceIntegrationDetails as IntegrationModel
from backend.schemas import (
    ServiceIntegrationDetails, ServiceIntegrationDetailsCreate, 
    ServiceIntegrationDetailsUpdate
)

router = APIRouter(tags=["integration"])


@router.get("/services/{service_id}/integration", response_model=ServiceIntegrationDetails)
async def get_service_integration(
    service_id: int,
    db: Session = Depends(get_db)
):
    """Get integration details for a service"""
    integration = db.query(IntegrationModel).filter(
        IntegrationModel.service_id == service_id
    ).first()
    
    if not integration:
        raise HTTPException(status_code=404, detail="Integration details not found")
    
    return integration


@router.post("/services/{service_id}/integration", response_model=ServiceIntegrationDetails)
async def create_service_integration(
    service_id: int,
    integration_data: ServiceIntegrationDetailsCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Create integration details for a service (admin only)"""
    # Check if integration already exists
    existing = db.query(IntegrationModel).filter(
        IntegrationModel.service_id == service_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400, 
            detail="Integration details already exist for this service"
        )
    
    integration = IntegrationModel(
        service_id=service_id,
        **integration_data.model_dump()
    )
    
    db.add(integration)
    db.commit()
    db.refresh(integration)
    return integration


@router.put("/services/{service_id}/integration", response_model=ServiceIntegrationDetails)
async def update_service_integration(
    service_id: int,
    integration_data: ServiceIntegrationDetailsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Update integration details for a service (admin only)"""
    integration = db.query(IntegrationModel).filter(
        IntegrationModel.service_id == service_id
    ).first()
    
    if not integration:
        raise HTTPException(status_code=404, detail="Integration details not found")
    
    for key, value in integration_data.model_dump(exclude_unset=True).items():
        setattr(integration, key, value)
    
    db.commit()
    db.refresh(integration)
    return integration


@router.delete("/services/{service_id}/integration")
async def delete_service_integration(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Delete integration details for a service (admin only)"""
    integration = db.query(IntegrationModel).filter(
        IntegrationModel.service_id == service_id
    ).first()
    
    if not integration:
        raise HTTPException(status_code=404, detail="Integration details not found")
    
    db.delete(integration)
    db.commit()
    
    return {"message": "Integration details deleted successfully"}
