"""
Initialize the search service and build the FAISS index
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.search_manager import get_search_manager
from backend.core.database import SessionLocal

def initialize_search():
    """Initialize the search service"""
    db = SessionLocal()
    try:
        # Get the search manager singleton
        search_manager = get_search_manager()
        
        # Initialize the service with database
        print("🔄 Initializing search service...")
        search_manager.initialize(db, force_rebuild=True)
        print("✅ Search service initialized!")
        
        # Check status
        status = search_manager.status()
        print(f"📊 Status: {status}")
        
        print("\n🎉 Search service is ready to use!")
        
    except Exception as e:
        print(f"❌ Error initializing search service: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    initialize_search()
