"""
Authentication endpoints
"""
from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import logging

from backend.core.config import get_settings
from backend.core.database import get_db
from backend.core.auth import create_access_token
from backend.services.user_crud import UserCRUD
from backend.schemas import Token
from backend.models.models import UserLoginLog

logger = logging.getLogger(__name__)
settings = get_settings()
router = APIRouter(tags=["auth"])


@router.post("/login", response_model=Token)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login to obtain JWT access token.
    
    ### Authentication:
    Use OAuth2 password flow with form-encoded data:
    - **username**: User's email address
    - **password**: User's password
    
    ### Example:
    ```
    curl -X POST /api/v1/auth/login \
      -H "Content-Type: application/x-www-form-urlencoded" \
      -d "username=admin@kpath.local&password=admin123"
    ```
    
    ### Response:
    Returns a JWT token valid for 30 minutes. Include this token in subsequent requests:
    ```
    Authorization: Bearer <access_token>
    ```
    
    ### Test Credentials:
    - Username: `admin@kpath.local`
    - Password: `admin123`
    """
    user = UserCRUD.authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Log successful login for analytics
    try:
        login_log = UserLoginLog(
            user_id=user.id,
            email=user.email,
            login_timestamp=datetime.utcnow(),
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("User-Agent")
        )
        db.add(login_log)
        db.commit()
    except Exception as log_error:
        logger.warning(f"Failed to log user login: {log_error}")
        # Don't fail login if logging fails
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "role": user.role
        },
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "username": user.email  # For compatibility
        }
    }
