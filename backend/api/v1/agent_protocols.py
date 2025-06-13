"""
Agent protocol management endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.auth import get_current_active_user, require_role
from backend.models import User, ServiceAgentProtocols as AgentProtocolModel
from backend.schemas import (
    ServiceAgentProtocols, ServiceAgentProtocolsCreate, 
    ServiceAgentProtocolsUpdate
)

router = APIRouter(tags=["agent-protocols"])


@router.get("/services/{service_id}/agent-protocols", response_model=ServiceAgentProtocols)
async def get_service_agent_protocols(
    service_id: int,
    db: Session = Depends(get_db)
):
    """Get agent protocols for a service"""
    protocols = db.query(AgentProtocolModel).filter(
        AgentProtocolModel.service_id == service_id
    ).first()
    
    if not protocols:
        raise HTTPException(status_code=404, detail="Agent protocols not found")
    
    return protocols


@router.post("/services/{service_id}/agent-protocols", response_model=ServiceAgentProtocols)
async def create_service_agent_protocols(
    service_id: int,
    protocol_data: ServiceAgentProtocolsCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Create agent protocols for a service (admin only)"""
    # Check if protocols already exist
    existing = db.query(AgentProtocolModel).filter(
        AgentProtocolModel.service_id == service_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400, 
            detail="Agent protocols already exist for this service"
        )
    
    protocols = AgentProtocolModel(
        service_id=service_id,
        **protocol_data.model_dump()
    )
    
    db.add(protocols)
    db.commit()
    db.refresh(protocols)
    return protocols


@router.put("/services/{service_id}/agent-protocols", response_model=ServiceAgentProtocols)
async def update_service_agent_protocols(
    service_id: int,
    protocol_data: ServiceAgentProtocolsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Update agent protocols for a service (admin only)"""
    protocols = db.query(AgentProtocolModel).filter(
        AgentProtocolModel.service_id == service_id
    ).first()
    
    if not protocols:
        raise HTTPException(status_code=404, detail="Agent protocols not found")
    
    for key, value in protocol_data.model_dump(exclude_unset=True).items():
        setattr(protocols, key, value)
    
    db.commit()
    db.refresh(protocols)
    return protocols


@router.delete("/services/{service_id}/agent-protocols")
async def delete_service_agent_protocols(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """Delete agent protocols for a service (admin only)"""
    protocols = db.query(AgentProtocolModel).filter(
        AgentProtocolModel.service_id == service_id
    ).first()
    
    if not protocols:
        raise HTTPException(status_code=404, detail="Agent protocols not found")
    
    db.delete(protocols)
    db.commit()
    
    return {"message": "Agent protocols deleted successfully"}
