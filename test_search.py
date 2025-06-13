#!/usr/bin/env python3
"""
Test script for KPath Enterprise search functionality with API key authentication.

Tests API key generation, validation, search functionality, rate limiting, and error handling.
"""

import unittest
import time
import psycopg2
from datetime import datetime, timedelta
import json
import logging
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api_key_manager import APIKeyManager
from search import SearchEngine, AuthenticationError, RateLimitError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestDatabaseSetup:
    """Set up test database and tables."""
    
    @staticmethod
    def create_test_schema(connection):
        """Create necessary tables for testing."""
        cursor = connection.cursor()
        
        # Create test documents table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create text search index
        cursor.execute("""            CREATE INDEX IF NOT EXISTS idx_documents_search 
            ON documents USING gin(to_tsvector('english', title || ' ' || content));
        """)
        
        connection.commit()
        logger.info("Test schema created successfully")
    
    @staticmethod
    def insert_test_data(connection):
        """Insert sample documents for testing."""
        cursor = connection.cursor()
        
        test_documents = [
            ("Python Programming Guide", "Learn Python programming with comprehensive examples and best practices."),
            ("Database Design Patterns", "Explore advanced database design patterns for scalable applications."),
            ("API Security Best Practices", "Essential security practices for building secure REST APIs."),
            ("Machine Learning Basics", "Introduction to machine learning concepts and algorithms."),
            ("Cloud Architecture Guide", "Design principles for modern cloud-native applications.")
        ]
        
        for title, content in test_documents:
            cursor.execute(
                "INSERT INTO documents (title, content) VALUES (%s, %s)",
                (title, content)
            )
        
        connection.commit()
        logger.info(f"Inserted {len(test_documents)} test documents")


class TestAPIKeyManager(unittest.TestCase):
    """Test cases for API key management."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database connection."""
        cls.connection = psycopg2.connect(
            dbname="kpath_enterprise",
            host="localhost",
            port=5432
        )
        cls.api_key_manager = APIKeyManager(cls.connection)
        
        # Create test user
        cursor = cls.connection.cursor()
        cursor.execute("""
            INSERT INTO users (username, email) 
            VALUES ('test_user', 'test@example.com')
            ON CONFLICT (username) DO UPDATE SET email = EXCLUDED.email
            RETURNING id
        """)        cls.test_user_id = cursor.fetchone()[0]
        cls.connection.commit()
    
    def test_generate_api_key(self):
        """Test API key generation."""
        key = self.api_key_manager.generate_api_key()
        self.assertTrue(key.startswith("kpe_"))
        self.assertEqual(len(key), len("kpe_") + 32)
    
    def test_create_and_validate_api_key(self):
        """Test creating and validating an API key."""
        # Create API key
        api_key, key_info = self.api_key_manager.create_api_key(
            user_id=self.test_user_id,
            name="Test Key",
            permissions={"search": True, "admin": False}
        )
        
        # Validate the key
        validation_result = self.api_key_manager.validate_api_key(api_key)
        self.assertIsNotNone(validation_result)
        self.assertEqual(validation_result['user_id'], self.test_user_id)
        self.assertTrue(validation_result['permissions']['search'])
        self.assertFalse(validation_result['permissions'].get('admin', False))
    
    def test_invalid_api_key(self):
        """Test validation with invalid API key."""
        result = self.api_key_manager.validate_api_key("kpe_invalid_key_12345")
        self.assertIsNone(result)
    
    def test_expired_api_key(self):
        """Test validation with expired API key."""
        # Create key that expires immediately
        api_key, _ = self.api_key_manager.create_api_key(
            user_id=self.test_user_id,
            name="Expired Key",
            expires_in_days=-1  # Already expired
        )
        
        result = self.api_key_manager.validate_api_key(api_key)
        self.assertIsNone(result)


class TestSearchEngine(unittest.TestCase):
    """Test cases for search functionality with API authentication."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""        cls.connection = psycopg2.connect(
            dbname="kpath_enterprise",
            host="localhost",
            port=5432
        )
        
        # Set up test data
        TestDatabaseSetup.create_test_schema(cls.connection)
        TestDatabaseSetup.insert_test_data(cls.connection)
        
        # Create test user and API key
        cursor = cls.connection.cursor()
        cursor.execute("""
            INSERT INTO users (username, email) 
            VALUES ('search_test_user', 'search@example.com')
            ON CONFLICT (username) DO UPDATE SET email = EXCLUDED.email
            RETURNING id
        """)
        cls.test_user_id = cursor.fetchone()[0]
        cls.connection.commit()
        
        # Create API key for testing
        cls.api_key_manager = APIKeyManager(cls.connection)
        cls.api_key, _ = cls.api_key_manager.create_api_key(
            user_id=cls.test_user_id,
            name="Search Test Key",
            rate_limit=10  # Low limit for testing
        )
        
        cls.search_engine = SearchEngine(cls.connection)
    
    def test_search_with_valid_api_key(self):
        """Test search with valid API key."""
        results = self.search_engine.search(
            api_key=self.api_key,
            query="Python",
            limit=5
        )
        
        self.assertTrue(results['success'])
        self.assertIn('results', results)
        self.assertIn('pagination', results)
        self.assertIn('meta', results)
        self.assertGreater(len(results['results']), 0)
    
    def test_search_without_api_key(self):
        """Test search without API key."""
        with self.assertRaises(AuthenticationError):
            self.search_engine.search(
                api_key="",
                query="Python"
            )    
    def test_search_with_invalid_api_key(self):
        """Test search with invalid API key."""
        with self.assertRaises(AuthenticationError):
            self.search_engine.search(
                api_key="kpe_invalid_key",
                query="Python"
            )
    
    def test_rate_limiting(self):
        """Test rate limiting functionality."""
        # Create a key with very low rate limit
        limited_key, _ = self.api_key_manager.create_api_key(
            user_id=self.test_user_id,
            name="Rate Limited Key",
            rate_limit=3
        )
        
        # Make requests up to the limit
        for i in range(3):
            results = self.search_engine.search(
                api_key=limited_key,
                query=f"Test {i}"
            )
            self.assertTrue(results['success'])
        
        # Next request should fail
        with self.assertRaises(RateLimitError):
            self.search_engine.search(
                api_key=limited_key,
                query="Over limit"
            )
    
    def test_search_pagination(self):
        """Test search pagination."""
        # First page
        page1 = self.search_engine.search(
            api_key=self.api_key,
            query="programming",
            limit=2,
            offset=0
        )
        
        # Second page
        page2 = self.search_engine.search(
            api_key=self.api_key,
            query="programming",
            limit=2,
            offset=2
        )
        
        # Check that results are different
        self.assertNotEqual(page1['results'], page2['results'])    
    def test_search_performance(self):
        """Test search performance metrics."""
        results = self.search_engine.search(
            api_key=self.api_key,
            query="database"
        )
        
        # Check that performance metrics are included
        self.assertIn('response_time_ms', results['meta'])
        self.assertIsInstance(results['meta']['response_time_ms'], int)
        self.assertGreater(results['meta']['response_time_ms'], 0)


def run_tests():
    """Run all tests and provide summary."""
    logger.info("Starting KPath Enterprise Search Tests")
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestAPIKeyManager))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSearchEngine))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Summary
    logger.info(f"\nTest Summary:")
    logger.info(f"Tests run: {result.testsRun}")
    logger.info(f"Failures: {len(result.failures)}")
    logger.info(f"Errors: {len(result.errors)}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    # Check database connection
    try:
        conn = psycopg2.connect(
            dbname="kpath_enterprise",
            host="localhost",
            port=5432
        )
        conn.close()
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        logger.error("Please ensure PostgreSQL is running and the 'kpath_enterprise' database exists.")
        sys.exit(1)
    
    # Run tests
    success = run_tests()
    sys.exit(0 if success else 1)