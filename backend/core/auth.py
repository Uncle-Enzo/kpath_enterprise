"""
JWT and API Key Authentication module
"""
from datetime import datetime, timedelta
from typing import Optional, Union
import logging

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from sqlalchemy.orm import Session

from backend.core.config import get_settings
from backend.core.database import get_db
from backend.models import User
from backend.schemas import TokenData
from api_key_manager import APIKeyManager

settings = get_settings()
logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.secret_key, 
        algorithm=settings.algorithm
    )
    return encoded_jwt


def decode_token(token: str) -> Optional[TokenData]:
    """Decode and validate a JWT token"""
    try:
        payload = jwt.decode(
            token, 
            settings.secret_key, 
            algorithms=[settings.algorithm]
        )
        user_id: str = payload.get("sub")  # JWT sub is typically a string
        email: str = payload.get("email")
        role: str = payload.get("role")
        
        if user_id is None:
            return None
        
        # Convert user_id to int if it's a string
        try:
            user_id_int = int(user_id)
        except (ValueError, TypeError):
            logger.error(f"Invalid user_id in token: {user_id}")
            return None
            
        return TokenData(
            user_id=user_id_int,
            email=email,
            role=role
        )
    except JWTError as e:
        logger.error(f"JWT decode error: {str(e)}")
        return None


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get the current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    logger.debug(f"Attempting to decode token: {token[:20]}...")
    token_data = decode_token(token)
    if token_data is None:
        logger.error("Token decode returned None")
        raise credentials_exception
    
    logger.debug(f"Token decoded successfully. User ID: {token_data.user_id}")
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None:
        logger.error(f"User not found with ID: {token_data.user_id}")
        raise credentials_exception
    
    logger.debug(f"User found: {user.email}, role: {user.role}")
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Ensure the current user is active"""
    # Add any additional checks here (e.g., user.is_active)
    return current_user


def require_role(required_role: str):
    """Dependency to require a specific role"""
    async def role_checker(current_user: User = Depends(get_current_active_user)):
        if current_user.role != required_role and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker


def require_roles(allowed_roles: list[str]):
    """Dependency to require one of several roles"""
    async def role_checker(current_user: User = Depends(get_current_active_user)):
        if current_user.role not in allowed_roles and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker


# API Key Authentication
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_api_key_user(
    api_key: Optional[str] = Depends(api_key_header),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get user from API key if provided"""
    if not api_key:
        return None
    
    api_key_manager = APIKeyManager(db)
    key_info = api_key_manager.validate_api_key(api_key)
    
    if not key_info:
        return None
    
    # Check rate limit
    within_limit, rate_info = api_key_manager.check_rate_limit(api_key)
    if not within_limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Limit: {rate_info['rate_limit']}/hour",
            headers={"X-RateLimit-Limit": str(rate_info['rate_limit']),
                    "X-RateLimit-Remaining": "0"}
        )
    
    # Get user
    user = db.query(User).filter(User.id == key_info['user_id']).first()
    if not user:
        return None
    
    # Store API key info in user object for later use
    user.api_key_info = key_info
    user.rate_info = rate_info
    
    return user


async def get_current_user_flexible(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme),
    api_key: Optional[str] = Depends(api_key_header)
) -> User:
    """Get current user from either JWT token or API key"""
    # Try API key first (if provided)
    if api_key:
        api_key_user = await get_api_key_user(api_key, db)
        if api_key_user:
            return api_key_user
    
    # Fall back to JWT token
    if token:
        try:
            user = await get_current_user(token, db)
            if user:
                return user
        except:
            pass
    
    # No valid authentication
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def optional_auth(
    token: Optional[str] = Depends(oauth2_scheme),
    api_key: Optional[str] = Depends(api_key_header),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Optional authentication - returns User if authenticated, None otherwise"""
    # Try API key first
    if api_key:
        api_key_manager = APIKeyManager(db)
        key_info = api_key_manager.validate_api_key(api_key)
        if key_info:
            user = db.query(User).filter(User.id == key_info['user_id']).first()
            if user:
                user.api_key_info = key_info
                return user
    
    # Try JWT token
    if token:
        try:
            token_data = decode_token(token)
            if token_data:
                user = db.query(User).filter(User.id == token_data.user_id).first()
                if user:
                    return user
        except:
            pass
    
    return None