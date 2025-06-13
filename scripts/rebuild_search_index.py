"""
Rebuild FAISS search index for KPATH Enterprise
"""
import sys
sys.path.append('/Users/james/claude_development/kpath_enterprise')

from backend.services.search_manager import initialize_search, get_search_manager
from backend.services.search.search_service import SearchQuery
from backend.core.database import SessionLocal

def rebuild_search_index():
    """Rebuild the FAISS search index with all services"""
    print("Rebuilding search index...")
    
    db = SessionLocal()
    
    try:
        # Initialize search with force rebuild
        initialize_search(db, force_rebuild=True)
        
        # Get the search manager to verify and test
        search_manager = get_search_manager()
        
        print("Search index rebuilt successfully!")
        
        # Test a search query
        print("\nTesting search functionality...")
        query = SearchQuery(
            text="financial reporting",
            limit=5,
            min_score=0.1
        )
        results = search_manager.search(query, db)
        
        print(f"Found {len(results)} results for 'financial reporting':")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result.service_data['name']} (Score: {result.score:.3f})")
            
        # Test another query
        print("\nTesting search for 'customer data':")
        query2 = SearchQuery(
            text="customer data",
            limit=5,
            min_score=0.1
        )
        results2 = search_manager.search(query2, db)
        
        for i, result in enumerate(results2, 1):
            print(f"{i}. {result.service_data['name']} (Score: {result.score:.3f})")
            
        # Test with domain filter
        print("\nTesting search for 'analysis' in Finance domain:")
        query3 = SearchQuery(
            text="analysis",
            limit=5,
            min_score=0.1,
            domains=["Finance"]
        )
        results3 = search_manager.search(query3, db)
        
        for i, result in enumerate(results3, 1):
            print(f"{i}. {result.service_data['name']} (Score: {result.score:.3f})")
            
    except Exception as e:
        print(f"Error rebuilding index: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    rebuild_search_index()
