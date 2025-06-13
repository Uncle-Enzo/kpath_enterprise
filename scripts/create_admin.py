"""
Create a test admin user
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.database import SessionLocal
from backend.services.user_crud import UserCRUD

def create_admin_user():
    """Create a test admin user"""
    db = SessionLocal()
    
    try:
        # Check if admin already exists
        existing = UserCRUD.get_user_by_email(db, "admin@kpath.local")
        if existing:
            print("Admin user already exists")
            return
        
        # Create admin user
        admin = UserCRUD.create_user(
            db,
            email="admin@kpath.local",
            password="admin123",  # Change in production!
            role="admin",
            attributes={"department": "IT", "full_access": True}
        )
        
        print(f"✅ Admin user created: {admin.email}")
        print("⚠️  Default password is 'admin123' - please change it!")
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()
