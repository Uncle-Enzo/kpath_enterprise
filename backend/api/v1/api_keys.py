"""
API Key Management endpoints for KPATH Enterprise.

Provides endpoints for creating, listing, and managing API keys.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging

from backend.core.database import get_db
from backend.core.auth import get_current_user
from backend.models.models import User
from backend.schemas.api_key import (
    APIKeyCreate, APIKeyResponse, APIKeyListResponse,
    APIKeyUsageResponse
)
from api_key_manager import APIKeyManager

logger = logging.getLogger(__name__)
router = APIRouter(tags=["api-keys"])


@router.post("/", response_model=APIKeyResponse)
async def create_api_key(
    request: APIKeyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new API key for the authenticated user.
    
    The API key will be returned only once. Store it securely as it cannot be retrieved again.
    
    ### Parameters:
    - **name**: A descriptive name for the API key (e.g., "Production Server")
    - **permissions**: JSON object defining permissions (defaults to {"search": true})
    - **expires_in_days**: Optional expiration period in days
    - **rate_limit**: Requests per hour limit (default: 1000)
    
    ### Returns:
    The complete API key (only shown once) and key metadata.
    """
    try:
        api_key_manager = APIKeyManager(db)
        
        # Create the API key
        api_key, key_info = api_key_manager.create_api_key(
            user_id=current_user.id,
            name=request.name,
            permissions=request.permissions or {"search": True},
            expires_in_days=request.expires_in_days,
            rate_limit=request.rate_limit or 1000
        )
        
        return APIKeyResponse(
            api_key=api_key,  # Only returned on creation
            id=key_info["id"],
            name=key_info["name"],
            prefix=key_info["prefix"],
            permissions=key_info["permissions"],
            expires_at=key_info["expires_at"],
            created_at=key_info["created_at"],
            rate_limit=key_info["rate_limit"]
        )
        
    except Exception as e:
        logger.error(f"Error creating API key: {e}")
        raise HTTPException(status_code=500, detail="Failed to create API key")

@router.get("/", response_model=List[APIKeyListResponse])
async def list_api_keys(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all API keys for the authenticated user.
    
    Note: The actual API key values are not returned, only metadata.
    """
    try:
        # Query API keys for the user
        from backend.models.models import APIKey
        
        keys = db.query(APIKey).filter(
            APIKey.user_id == current_user.id,
            APIKey.active == True
        ).all()
        
        return [
            APIKeyListResponse(
                id=key.id,
                name=key.name,
                prefix=key.key_hash[:8],  # Show prefix from hash
                last_used=key.last_used,
                expires_at=key.expires_at,
                created_at=key.created_at,
                active=key.active
            )
            for key in keys
        ]
        
    except Exception as e:
        logger.error(f"Error listing API keys: {e}")
        raise HTTPException(status_code=500, detail="Failed to list API keys")


@router.delete("/{key_id}")
async def revoke_api_key(
    key_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Revoke (deactivate) an API key.
    
    The key cannot be reactivated once revoked.
    """
    try:
        from backend.models.models import APIKey
        
        # Find the API key
        api_key = db.query(APIKey).filter(
            APIKey.id == key_id,
            APIKey.user_id == current_user.id
        ).first()
        
        if not api_key:
            raise HTTPException(status_code=404, detail="API key not found")
        
        # Deactivate the key
        api_key.active = False
        db.commit()
        
        return {"message": "API key revoked successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error revoking API key: {e}")
        raise HTTPException(status_code=500, detail="Failed to revoke API key")

@router.get("/{key_id}/usage", response_model=APIKeyUsageResponse)
async def get_api_key_usage(
    key_id: int,
    days: int = Query(default=7, ge=1, le=90, description="Number of days of usage data"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get usage statistics for an API key.
    
    ### Parameters:
    - **days**: Number of days of usage history (1-90, default: 7)
    
    ### Returns:
    Usage statistics including request counts, endpoints used, and rate limit info.
    """
    try:
        from backend.models.models import APIKey
        from sqlalchemy import func
        
        # Verify key ownership
        api_key = db.query(APIKey).filter(
            APIKey.id == key_id,
            APIKey.user_id == current_user.id
        ).first()
        
        if not api_key:
            raise HTTPException(status_code=404, detail="API key not found")
        
        # Get usage statistics from api_key_logs
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # This would need the actual api_key_logs table from the schema
        # For now, return mock data
        return APIKeyUsageResponse(
            key_id=key_id,
            total_requests=0,
            requests_last_hour=0,
            requests_today=0,
            rate_limit=api_key.rate_limit if hasattr(api_key, 'rate_limit') else 1000,
            endpoints_used=[],
            daily_usage=[]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting API key usage: {e}")
        raise HTTPException(status_code=500, detail="Failed to get API key usage")