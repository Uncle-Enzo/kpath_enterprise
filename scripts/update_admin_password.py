"""
Update admin user password
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.database import SessionLocal
from backend.services.user_crud import UserCRUD
from backend.models import User

def update_admin_password():
    """Update admin user password"""
    db = SessionLocal()
    
    try:
        # Get admin user
        admin = db.query(User).filter(User.email == "admin@kpath.local").first()
        if not admin:
            print("❌ Admin user not found")
            return
        
        # Update password hash
        admin.password_hash = UserCRUD.get_password_hash("admin123")
        db.commit()
        
        print(f"✅ Admin password updated for: {admin.email}")
        print("⚠️  Password is 'admin123' - please change it!")
        
    except Exception as e:
        print(f"❌ Error updating admin password: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_admin_password()
