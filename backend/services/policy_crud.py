"""
Access Policy CRUD operations
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from backend.models import AccessPolicy


class PolicyCRUD:
    """CRUD operations for access policies"""
    
    @staticmethod
    def create_policy(
        db: Session,
        service_id: int,
        conditions: dict,
        policy_type: str = "RBAC",
        priority: int = 0
    ) -> AccessPolicy:
        """Create a new access policy"""
        policy = AccessPolicy(
            service_id=service_id,
            conditions=conditions,
            type=policy_type,
            priority=priority
        )
        db.add(policy)
        db.commit()
        db.refresh(policy)
        return policy
    
    @staticmethod
    def get_policy(db: Session, policy_id: int) -> Optional[AccessPolicy]:
        """Get policy by ID"""
        return db.query(AccessPolicy).filter(AccessPolicy.id == policy_id).first()
    
    @staticmethod
    def get_policies_for_service(
        db: Session,
        service_id: int
    ) -> List[AccessPolicy]:
        """Get all policies for a service"""
        return db.query(AccessPolicy)\
            .filter(AccessPolicy.service_id == service_id)\
            .order_by(AccessPolicy.priority.desc())\
            .all()
    
    @staticmethod
    def get_policies(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        policy_type: Optional[str] = None
    ) -> List[AccessPolicy]:
        """Get list of policies with optional filtering"""
        query = db.query(AccessPolicy)
        
        if policy_type:
            query = query.filter(AccessPolicy.type == policy_type)
            
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update_policy(
        db: Session,
        policy_id: int,
        **kwargs
    ) -> Optional[AccessPolicy]:
        """Update policy attributes"""
        policy = db.query(AccessPolicy).filter(AccessPolicy.id == policy_id).first()
        
        if not policy:
            return None
            
        for key, value in kwargs.items():
            if hasattr(policy, key) and value is not None:
                setattr(policy, key, value)
                
        db.commit()
        db.refresh(policy)
        return policy
    
    @staticmethod
    def delete_policy(db: Session, policy_id: int) -> bool:
        """Delete a policy"""
        policy = db.query(AccessPolicy).filter(AccessPolicy.id == policy_id).first()
        
        if not policy:
            return False
            
        db.delete(policy)
        db.commit()
        return True
    
    @staticmethod
    def evaluate_policies(
        db: Session,
        service_id: int,
        user_context: dict
    ) -> bool:
        """Evaluate if user has access to service based on policies"""
        policies = PolicyCRUD.get_policies_for_service(db, service_id)
        
        if not policies:
            # No policies means open access
            return True
        
        for policy in policies:
            if policy.type == "RBAC":
                # Check role-based access
                required_roles = policy.conditions.get("allowed_roles", [])
                user_role = user_context.get("role")
                if user_role and user_role in required_roles:
                    return True
            
            elif policy.type == "ABAC":
                # Check attribute-based access
                # This is a simple implementation - could be more complex
                required_attrs = policy.conditions.get("required_attributes", {})
                user_attrs = user_context.get("attributes", {})
                
                if all(user_attrs.get(k) == v for k, v in required_attrs.items()):
                    return True
        
        return False
