"""
Service import endpoint for bulk service creation
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import json

from backend.core.database import get_db
from backend.core.auth import get_current_active_user, require_role
from backend.models import User
from backend.services import ServiceCRUD
from backend.schemas import ServiceCreate
from pydantic import BaseModel, ValidationError

router = APIRouter(tags=["import"])


class ImportServiceData(BaseModel):
    """Schema for importing service data"""
    name: str
    description: str
    endpoint: Optional[str] = None
    version: Optional[str] = None
    status: str = "active"
    tool_type: str = "API"
    interaction_modes: Optional[List[str]] = None
    visibility: str = "internal"
    deprecation_date: Optional[str] = None
    deprecation_notice: Optional[str] = None
    success_criteria: Optional[Dict[str, Any]] = None
    default_timeout_ms: int = 30000
    default_retry_policy: Optional[Dict[str, Any]] = None
    integration_details: Optional[Dict[str, Any]] = None
    agent_protocols: Optional[Dict[str, Any]] = None
    capabilities: Optional[List[Dict[str, Any]]] = None
    industries: Optional[List[Dict[str, Any]]] = None


class ImportSchema(BaseModel):
    """Schema for the import file structure"""
    version: str
    metadata: Optional[Dict[str, Any]] = None
    services: List[ImportServiceData]


class ImportResult(BaseModel):
    """Result of an import operation"""
    success: bool
    service_name: str
    service_id: Optional[int] = None
    error: Optional[str] = None
    warnings: List[str] = []


class ImportResponse(BaseModel):
    """Response for import operation"""
    total_services: int
    successful_imports: int
    failed_imports: int
    results: List[ImportResult]
    validation_errors: List[str] = []


@router.post("/services/import", response_model=ImportResponse)
async def import_services(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Import multiple services from a JSON file
    """
    # Verify admin role
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Validate file type
    if not file.filename.endswith('.json'):
        raise HTTPException(status_code=400, detail="Only JSON files are supported")
    
    try:
        # Read and parse JSON file
        content = await file.read()
        data = json.loads(content)
        
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON file: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")
    
    # Validate against schema
    validation_errors = []
    try:
        import_data = ImportSchema(**data)
    except ValidationError as e:
        validation_errors = [f"{err['loc']}: {err['msg']}" for err in e.errors()]
        return ImportResponse(
            total_services=0,
            successful_imports=0,
            failed_imports=0,
            results=[],
            validation_errors=validation_errors
        )
    
    # Import services
    results = []
    successful_imports = 0
    failed_imports = 0
    
    for service_data in import_data.services:
        result = await _import_single_service(db, service_data, current_user)
        results.append(result)
        
        if result.success:
            successful_imports += 1
        else:
            failed_imports += 1
    
    return ImportResponse(
        total_services=len(import_data.services),
        successful_imports=successful_imports,
        failed_imports=failed_imports,
        results=results,
        validation_errors=validation_errors
    )


async def _import_single_service(
    db: Session, 
    service_data: ImportServiceData, 
    current_user: User
) -> ImportResult:
    """
    Import a single service with all its related data
    """
    warnings = []
    
    try:
        # Check if service name already exists
        existing_service = ServiceCRUD.get_service_by_name(db, service_data.name)
        if existing_service:
            return ImportResult(
                success=False,
                service_name=service_data.name,
                error=f"Service with name '{service_data.name}' already exists"
            )
        
        # Create base service
        service = ServiceCRUD.create_service(
            db=db,
            name=service_data.name,
            description=service_data.description,
            endpoint=service_data.endpoint,
            version=service_data.version,
            status=service_data.status,
            tool_type=service_data.tool_type,
            interaction_modes=service_data.interaction_modes,
            visibility=service_data.visibility,
            deprecation_date=service_data.deprecation_date,
            deprecation_notice=service_data.deprecation_notice,
            success_criteria=service_data.success_criteria,
            default_timeout_ms=service_data.default_timeout_ms,
            default_retry_policy=service_data.default_retry_policy
        )
        
        # Import integration details if provided
        if service_data.integration_details:
            try:
                # For now, we'll store this in the service record
                # TODO: Implement full integration details table
                warnings.append(f"Integration details noted but not fully implemented yet")
            except Exception as e:
                warnings.append(f"Failed to import integration details: {str(e)}")
        
        # Import agent protocols if provided
        if service_data.agent_protocols:
            try:
                # For now, we'll store this in the service record
                # TODO: Implement full agent protocols table
                warnings.append(f"Agent protocols noted but not fully implemented yet")
            except Exception as e:
                warnings.append(f"Failed to import agent protocols: {str(e)}")
        
        # Import capabilities if provided
        if service_data.capabilities:
            for capability in service_data.capabilities:
                try:
                    ServiceCRUD.add_capability(
                        db=db,
                        service_id=service.id,
                        capability_name=capability.get('capability_name'),
                        capability_desc=capability['capability_desc'],
                        input_schema=capability.get('input_schema'),
                        output_schema=capability.get('output_schema')
                    )
                except Exception as e:
                    warnings.append(f"Failed to import capability '{capability.get('capability_name', 'unknown')}': {str(e)}")
        
        # Import industries if provided  
        if service_data.industries:
            for industry in service_data.industries:
                try:
                    # For now, we'll store this as a simple industry relationship
                    # TODO: Implement full industries table
                    warnings.append(f"Industry '{industry.get('industry', 'unknown')}' noted but not fully implemented yet")
                except Exception as e:
                    warnings.append(f"Failed to import industry '{industry.get('industry', 'unknown')}': {str(e)}")
        
        return ImportResult(
            success=True,
            service_name=service_data.name,
            service_id=service.id,
            warnings=warnings
        )
        
    except Exception as e:
        return ImportResult(
            success=False,
            service_name=service_data.name,
            error=str(e)
        )


@router.post("/services/validate-import")
async def validate_import_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """
    Validate an import file without importing
    """
    if not file.filename.endswith('.json'):
        raise HTTPException(status_code=400, detail="Only JSON files are supported")
    
    try:
        content = await file.read()
        data = json.loads(content)
        
        # Validate against schema
        import_data = ImportSchema(**data)
        
        # Additional validation
        service_names = [service.name for service in import_data.services]
        duplicate_names = []
        seen_names = set()
        
        for name in service_names:
            if name in seen_names:
                duplicate_names.append(name)
            seen_names.add(name)
        
        return {
            "valid": True,
            "service_count": len(import_data.services),
            "duplicate_names": duplicate_names,
            "metadata": import_data.metadata
        }
        
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")
    except ValidationError as e:
        return {
            "valid": False,
            "errors": [f"{err['loc']}: {err['msg']}" for err in e.errors()]
        }
