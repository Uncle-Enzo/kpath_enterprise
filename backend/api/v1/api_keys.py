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
from backend.core.auth import get_current_user, get_current_user_flexible
from backend.models.models import User
from backend.schemas.api_key import (
    APIKeyCreate, APIKeyResponse, APIKeyListResponse,
    APIKeyUsageResponse
)
from api_key_manager_fixed import APIKeyManager

logger = logging.getLogger(__name__)
router = APIRouter(tags=["api-keys"])


@router.post("/", response_model=APIKeyResponse)
async def create_api_key(
    request: APIKeyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_flexible)
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
    current_user: User = Depends(get_current_user_flexible)
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


@router.get("/{key_id}", response_model=APIKeyListResponse)
async def get_api_key(
    key_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_flexible)
):
    """
    Get details for a specific API key.
    
    Note: The actual API key value is not returned, only metadata.
    """
    logger.info(f"🟢 [GET_API_KEY] Request for key_id: {key_id}, user_id: {current_user.id}")
    
    try:
        from backend.models.models import APIKey
        
        logger.info(f"🟢 [GET_API_KEY] Querying database for key_id: {key_id}")
        
        # Find the API key
        api_key = db.query(APIKey).filter(
            APIKey.id == key_id,
            APIKey.user_id == current_user.id
        ).first()
        
        if not api_key:
            logger.warning(f"🟡 [GET_API_KEY] API key not found - key_id: {key_id}, user_id: {current_user.id}")
            raise HTTPException(status_code=404, detail="API key not found")
        
        logger.info(f"🟢 [GET_API_KEY] API key found - name: {api_key.name}, active: {api_key.active}")
        
        response = APIKeyListResponse(
            id=api_key.id,
            name=api_key.name,
            prefix=api_key.key_hash[:8],  # Show prefix from hash
            last_used=api_key.last_used,
            expires_at=api_key.expires_at,
            created_at=api_key.created_at,
            active=api_key.active
        )
        
        logger.info(f"🟢 [GET_API_KEY] Returning response: {response.dict()}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"🔴 [GET_API_KEY] Error getting API key: {e}")
        logger.error(f"🔴 [GET_API_KEY] Exception type: {type(e)}")
        raise HTTPException(status_code=500, detail="Failed to get API key")


@router.delete("/{key_id}")
async def revoke_api_key(
    key_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_flexible)
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
    current_user: User = Depends(get_current_user_flexible)
):
    """
    Get usage statistics for an API key.
    
    ### Parameters:
    - **days**: Number of days of usage history (1-90, default: 7)
    
    ### Returns:
    Usage statistics including request counts, endpoints used, and rate limit info.
    """
    logger.info(f"🟢 [GET_USAGE] Request for key_id: {key_id}, days: {days}, user_id: {current_user.id}")
    
    try:
        from backend.models.models import APIKey, APIRequestLog
        from sqlalchemy import func, desc
        from datetime import timedelta
        
        logger.info(f"🟢 [GET_USAGE] Verifying key ownership")
        
        # Verify key ownership
        api_key = db.query(APIKey).filter(
            APIKey.id == key_id,
            APIKey.user_id == current_user.id
        ).first()
        
        if not api_key:
            logger.warning(f"🟡 [GET_USAGE] API key not found - key_id: {key_id}, user_id: {current_user.id}")
            raise HTTPException(status_code=404, detail="API key not found")
        
        logger.info(f"🟢 [GET_USAGE] API key verified - name: {api_key.name}")
        
        # Calculate date ranges
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        hour_ago = datetime.utcnow() - timedelta(hours=1)
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        logger.info(f"🟢 [GET_USAGE] Date ranges - cutoff: {cutoff_date}, hour_ago: {hour_ago}, today_start: {today_start}")
        
        # Get total requests
        logger.info(f"🟢 [GET_USAGE] Querying total requests")
        total_requests = db.query(func.count(APIRequestLog.id)).filter(
            APIRequestLog.api_key_id == key_id,
            APIRequestLog.timestamp >= cutoff_date
        ).scalar() or 0
        logger.info(f"🟢 [GET_USAGE] Total requests: {total_requests}")
        
        # Get requests in last hour
        logger.info(f"🟢 [GET_USAGE] Querying requests last hour")
        requests_last_hour = db.query(func.count(APIRequestLog.id)).filter(
            APIRequestLog.api_key_id == key_id,
            APIRequestLog.timestamp >= hour_ago
        ).scalar() or 0
        logger.info(f"🟢 [GET_USAGE] Requests last hour: {requests_last_hour}")
        
        # Get requests today
        logger.info(f"🟢 [GET_USAGE] Querying requests today")
        requests_today = db.query(func.count(APIRequestLog.id)).filter(
            APIRequestLog.api_key_id == key_id,
            APIRequestLog.timestamp >= today_start
        ).scalar() or 0
        logger.info(f"🟢 [GET_USAGE] Requests today: {requests_today}")
        
        # Get endpoint usage statistics
        logger.info(f"🟢 [GET_USAGE] Querying endpoint statistics")
        endpoint_stats = db.query(
            APIRequestLog.endpoint,
            APIRequestLog.method,
            func.count(APIRequestLog.id).label('count'),
            func.avg(APIRequestLog.response_time_ms).label('avg_response_time'),
            func.max(APIRequestLog.timestamp).label('last_used')
        ).filter(
            APIRequestLog.api_key_id == key_id,
            APIRequestLog.timestamp >= cutoff_date
        ).group_by(
            APIRequestLog.endpoint, APIRequestLog.method
        ).order_by(desc('count')).all()
        
        endpoints_used = []
        for stat in endpoint_stats:
            endpoints_used.append({
                'endpoint': stat.endpoint,
                'method': stat.method,
                'count': stat.count,
                'avg_response_time_ms': round(stat.avg_response_time, 2) if stat.avg_response_time else 0,
                'last_used': stat.last_used.isoformat() if stat.last_used else None
            })
        
        logger.info(f"🟢 [GET_USAGE] Endpoint stats: {len(endpoints_used)} endpoints")
        
        # Get daily usage breakdown
        logger.info(f"🟢 [GET_USAGE] Querying daily usage")
        daily_stats = db.query(
            func.date(APIRequestLog.timestamp).label('date'),
            func.count(APIRequestLog.id).label('requests'),
            func.avg(APIRequestLog.response_time_ms).label('avg_response_time'),
            func.count(func.distinct(APIRequestLog.endpoint)).label('unique_endpoints')
        ).filter(
            APIRequestLog.api_key_id == key_id,
            APIRequestLog.timestamp >= cutoff_date
        ).group_by(
            func.date(APIRequestLog.timestamp)
        ).order_by('date').all()
        
        daily_usage = []
        for stat in daily_stats:
            daily_usage.append({
                'date': stat.date.isoformat() if stat.date else None,
                'requests': stat.requests,
                'avg_response_time_ms': round(stat.avg_response_time, 2) if stat.avg_response_time else 0,
                'unique_endpoints': stat.unique_endpoints
            })
        
        logger.info(f"🟢 [GET_USAGE] Daily usage: {len(daily_usage)} days")
        
        response = APIKeyUsageResponse(
            key_id=key_id,
            total_requests=total_requests,
            requests_last_hour=requests_last_hour,
            requests_today=requests_today,
            rate_limit=1000,  # Default rate limit - can be made configurable
            endpoints_used=endpoints_used,
            daily_usage=daily_usage
        )
        
        logger.info(f"🟢 [GET_USAGE] Returning usage response: total_requests={total_requests}, endpoints={len(endpoints_used)}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"🔴 [GET_USAGE] Error getting API key usage: {e}")
        logger.error(f"🔴 [GET_USAGE] Exception type: {type(e)}")
        logger.error(f"🔴 [GET_USAGE] Exception args: {e.args}")
        raise HTTPException(status_code=500, detail="Failed to get usage statistics")