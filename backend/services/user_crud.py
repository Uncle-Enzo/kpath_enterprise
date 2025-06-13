"""
User CRUD operations
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from backend.models import User


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserCRUD:
    """CRUD operations for users"""
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_user(
        db: Session,
        email: str,
        password: str,
        role: str = "user",
        username: Optional[str] = None,
        org_id: Optional[int] = None,
        attributes: Optional[dict] = None
    ) -> User:
        """Create a new user with hashed password"""
        user = User(
            email=email,
            username=username,
            role=role,
            org_id=org_id,
            attributes=attributes or {},
            password_hash=UserCRUD.get_password_hash(password)
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def get_user(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_users(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        role: Optional[str] = None
    ) -> List[User]:
        """Get list of users with optional filtering"""
        query = db.query(User)
        
        if role:
            query = query.filter(User.role == role)
            
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update_user(
        db: Session,
        user_id: int,
        **kwargs
    ) -> Optional[User]:
        """Update user attributes"""
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return None
            
        # Handle password update separately
        if "password" in kwargs:
            password = kwargs.pop("password")
            user.password_hash = UserCRUD.get_password_hash(password)
            
        for key, value in kwargs.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
                
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """Delete a user"""
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return False
            
        db.delete(user)
        db.commit()
        return True
    
    @staticmethod
    def authenticate_user(
        db: Session,
        email: str,
        password: str
    ) -> Optional[User]:
        """Authenticate a user by email and password"""
        user = UserCRUD.get_user_by_email(db, email)
        if not user:
            return None
        if not UserCRUD.verify_password(password, user.password_hash):
            return None
        return user
