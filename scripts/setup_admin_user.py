"""
Create or update admin user with specified credentials
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.database import SessionLocal
from backend.services.user_crud import UserCRUD
from backend.models import User

def setup_admin_user():
    """Create or update admin user with specified credentials"""
    db = SessionLocal()
    
    email = "admin@kpath.ai"
    password = "1234rt4rd"
    
    try:
        # Check if user exists
        existing = db.query(User).filter(User.email == email).first()
        
        if existing:
            print(f"Admin user '{email}' already exists, updating password...")
            # Update password
            existing.password_hash = UserCRUD.get_password_hash(password)
            existing.role = "admin"  # Ensure admin role
            existing.is_active = True  # Ensure active
            db.commit()
            print(f"✅ Password updated for: {email}")
        else:
            print(f"Creating new admin user '{email}'...")
            # Create new admin user
            admin = UserCRUD.create_user(
                db,
                email=email,
                password=password,
                role="admin",
                attributes={"department": "IT", "full_access": True}
            )
            print(f"✅ Admin user created: {admin.email}")
        
        print(f"\n📧 Email: {email}")
        print(f"🔑 Password: {password}")
        print("\n✅ You can now login to the admin interface!")
        
    except Exception as e:
        print(f"❌ Error setting up admin user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    setup_admin_user()
