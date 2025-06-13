"""
Add is_active column to users table
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.database import engine
from sqlalchemy import text

def add_is_active_column():
    """Add is_active column to users table if it doesn't exist"""
    try:
        with engine.begin() as conn:
            # Check if column exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='users' AND column_name='is_active'
            """))
            
            if not result.fetchone():
                print("Adding is_active column to users table...")
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN is_active BOOLEAN DEFAULT TRUE
                """))
                print("✅ Column added successfully")
            else:
                print("✅ is_active column already exists")
                
    except Exception as e:
        print(f"❌ Error adding column: {e}")

if __name__ == "__main__":
    add_is_active_column()
