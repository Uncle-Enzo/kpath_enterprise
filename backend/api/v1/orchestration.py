"""
API endpoints for agent orchestration functionality
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.auth import get_current_user
from backend.models.models import Tool, InvocationLog, Service, User
from backend.schemas.orchestration_schemas import (
    ToolCreate, ToolUpdate, ToolResponse,
    InvocationLogCreate, InvocationLogResponse,
    ServiceOrchestrationUpdate, OrchestrationAnalytics
)

router = APIRouter()


@router.post("/tools", response_model=ToolResponse, status_code=status.HTTP_201_CREATED)
async def create_tool(
    tool: ToolCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new tool definition for a service"""
    
    # Verify the service exists
    service = db.query(Service).filter(Service.id == tool.service_id).first()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    # Check if tool name already exists for this service
    existing_tool = db.query(Tool).filter(
        Tool.service_id == tool.service_id,
        Tool.tool_name == tool.tool_name
    ).first()
    if existing_tool:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Tool with this name already exists for this service"
        )
    
    # Create the tool
    db_tool = Tool(**tool.dict())
    db.add(db_tool)
    db.commit()
    db.refresh(db_tool)
    
    return db_tool


@router.get("/tools", response_model=List[ToolResponse])
async def get_tools(
    service_id: Optional[int] = None,
    active_only: bool = True,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get tools, optionally filtered by service"""
    
    query = db.query(Tool)
    
    if service_id:
        query = query.filter(Tool.service_id == service_id)
    
    if active_only:
        query = query.filter(Tool.is_active == True)
    
    tools = query.offset(skip).limit(limit).all()
    return tools


@router.get("/tools/{tool_id}", response_model=ToolResponse)
async def get_tool(
    tool_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific tool by ID"""
    
    tool = db.query(Tool).filter(Tool.id == tool_id).first()
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool not found"
        )
    
    return tool


@router.put("/tools/{tool_id}", response_model=ToolResponse)
async def update_tool(
    tool_id: int,
    tool_update: ToolUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a tool definition"""
    
    tool = db.query(Tool).filter(Tool.id == tool_id).first()
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool not found"
        )
    
    # Update only provided fields
    update_data = tool_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tool, field, value)
    
    db.commit()
    db.refresh(tool)
    
    return tool


@router.delete("/tools/{tool_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tool(
    tool_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a tool definition"""
    
    tool = db.query(Tool).filter(Tool.id == tool_id).first()
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool not found"
        )
    
    db.delete(tool)
    db.commit()


@router.post("/invocation-logs", response_model=InvocationLogResponse, status_code=status.HTTP_201_CREATED)
async def create_invocation_log(
    log: InvocationLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new invocation log entry"""
    
    # Verify the tool exists
    tool = db.query(Tool).filter(Tool.id == log.tool_id).first()
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool not found"
        )
    
    # Create the invocation log
    db_log = InvocationLog(**log.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    
    return db_log


@router.get("/invocation-logs", response_model=List[InvocationLogResponse])
async def get_invocation_logs(
    tool_id: Optional[int] = None,
    service_id: Optional[int] = None,
    success_only: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get invocation logs with optional filters"""
    
    query = db.query(InvocationLog)
    
    if tool_id:
        query = query.filter(InvocationLog.tool_id == tool_id)
    
    if service_id:
        query = query.filter(InvocationLog.target_service_id == service_id)
    
    if success_only is not None:
        query = query.filter(InvocationLog.success_status == success_only)
    
    # Order by most recent first
    query = query.order_by(InvocationLog.created_at.desc())
    
    logs = query.offset(skip).limit(limit).all()
    return logs


@router.put("/services/{service_id}/orchestration", response_model=dict)
async def update_service_orchestration(
    service_id: int,
    orchestration_update: ServiceOrchestrationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update orchestration metadata for a service"""
    
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    # Update only provided fields
    update_data = orchestration_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(service, field, value)
    
    db.commit()
    db.refresh(service)
    
    return {
        "message": "Service orchestration metadata updated successfully",
        "service_id": service_id,
        "updated_fields": list(update_data.keys())
    }


@router.get("/analytics/orchestration", response_model=OrchestrationAnalytics)
async def get_orchestration_analytics(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get orchestration analytics and metrics"""
    
    from datetime import datetime, timedelta
    from sqlalchemy import func
    
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Total invocations
    total_invocations = db.query(InvocationLog).filter(
        InvocationLog.created_at >= start_date
    ).count()
    
    # Successful invocations
    successful_invocations = db.query(InvocationLog).filter(
        InvocationLog.created_at >= start_date,
        InvocationLog.success_status == True
    ).count()
    
    # Failed invocations
    failed_invocations = total_invocations - successful_invocations
    
    # Average response time
    avg_response_time = db.query(func.avg(InvocationLog.response_time_ms)).filter(
        InvocationLog.created_at >= start_date,
        InvocationLog.response_time_ms.isnot(None)
    ).scalar() or 0.0
    
    # Most used tools
    most_used_tools = db.query(
        Tool.tool_name,
        func.count(InvocationLog.id).label('usage_count')
    ).join(InvocationLog).filter(
        InvocationLog.created_at >= start_date
    ).group_by(Tool.tool_name).order_by(
        func.count(InvocationLog.id).desc()
    ).limit(10).all()
    
    # Top initiator agents
    top_initiators = db.query(
        InvocationLog.initiator_agent,
        func.count(InvocationLog.id).label('invocation_count')
    ).filter(
        InvocationLog.created_at >= start_date
    ).group_by(InvocationLog.initiator_agent).order_by(
        func.count(InvocationLog.id).desc()
    ).limit(10).all()
    
    # Error rate percentage
    error_rate = (failed_invocations / total_invocations * 100) if total_invocations > 0 else 0.0
    
    return OrchestrationAnalytics(
        total_invocations=total_invocations,
        successful_invocations=successful_invocations,
        failed_invocations=failed_invocations,
        average_response_time_ms=float(avg_response_time),
        most_used_tools=[
            {"tool_name": tool, "usage_count": count} 
            for tool, count in most_used_tools
        ],
        error_rate_percentage=error_rate,
        top_initiator_agents=[
            {"agent_name": agent, "invocation_count": count}
            for agent, count in top_initiators
        ],
        performance_trends={
            "period_days": days,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
    )
