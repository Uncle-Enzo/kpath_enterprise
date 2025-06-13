"""
User management endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.auth import get_current_active_user, require_role
from backend.models import User as UserModel
from backend.services import UserCRUD
from backend.schemas import User, UserCreate, UserUpdate

router = APIRouter(tags=["users"])


@router.get("/", response_model=List[User])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    role: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_role("admin"))
):
    """List all users (admin only)"""
    users = UserCRUD.get_users(db, skip=skip, limit=limit, role=role)
    return users


@router.get("/me", response_model=User)
async def get_current_user(
    current_user: UserModel = Depends(get_current_active_user)
):
    """Get current user info"""
    return current_user


@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_role("admin"))
):
    """Get a specific user by ID (admin only)"""
    user = UserCRUD.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/", response_model=User)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_role("admin"))
):
    """Create a new user (admin only)"""
    # Check if email already exists
    existing = UserCRUD.get_user_by_email(db, user_data.email)
    if existing:
        raise HTTPException(
            status_code=400,
            detail="User with this email already exists"
        )
    
    user = UserCRUD.create_user(
        db,
        email=user_data.email,
        username=user_data.username,
        password=user_data.password,
        role=user_data.role,
        org_id=user_data.org_id,
        attributes=user_data.attributes
    )
    return user


@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_role("admin"))
):
    """Update a user (admin only)"""
    user = UserCRUD.update_user(
        db,
        user_id,
        **user_data.model_dump(exclude_unset=True)
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_role("admin"))
):
    """Delete a user (admin only)"""
    # Prevent self-deletion
    if user_id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete your own account"
        )
    
    result = UserCRUD.delete_user(db, user_id)
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}
