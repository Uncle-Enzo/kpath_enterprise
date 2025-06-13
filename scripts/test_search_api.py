#!/usr/bin/env python
"""
Test script for KPATH Enterprise Search API
Tests search functionality with various queries and validates results
"""
import sys
import json
import time
from typing import List, Dict, Any
import requests
from datetime import datetime

# Add project root to path
sys.path.append('/Users/james/claude_development/kpath_enterprise')

# Configuration
API_BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"
TEST_EMAIL = "admin@kpath.local"
TEST_PASSWORD = "admin123"

class SearchAPITester:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.api_prefix = API_PREFIX
        self.token = None
        self.headers = {}
        
    def login(self) -> bool:
        """Authenticate and get JWT token"""
        print("🔐 Authenticating...")
        try:
            # OAuth2PasswordRequestForm expects form-encoded data
            response = requests.post(
                f"{self.base_url}{self.api_prefix}/auth/login",
                data={"username": TEST_EMAIL, "password": TEST_PASSWORD},
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.headers = {"Authorization": f"Bearer {self.token}"}
                print("✅ Authentication successful")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False
    
    def search(self, query: str, domains: List[str] = None, 
               capabilities: List[str] = None, limit: int = 10) -> Dict[str, Any]:
        """Execute a search query"""
        search_data = {
            "query": query,
            "limit": limit,
            "min_score": 0.1
        }
        
        if domains:
            search_data["domains"] = domains
        if capabilities:
            search_data["capabilities"] = capabilities
            
        try:
            url = f"{self.base_url}{self.api_prefix}/search/search"
            print(f"   🌐 URL: {url}")
            print(f"   📦 Payload: {search_data}")
            
            response = requests.post(
                url,
                json=search_data,
                headers=self.headers
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "data": response.json(),
                    "query": query
                }
            else:
                return {
                    "success": False,
                    "error": f"Status {response.status_code}: {response.text}",
                    "query": query
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
    
    def format_result(self, result: Dict[str, Any]) -> str:
        """Format a single search result for display"""
        service = result.get("service", {})
        score = result.get("score", 0)
        rank = result.get("rank", 0)
        
        output = []
        output.append(f"  #{rank} {service.get('name', 'Unknown')} (Score: {score:.3f})")
        output.append(f"      {service.get('description', 'No description')[:80]}...")
        
        # Show capabilities
        capabilities = service.get("capabilities", [])
        if capabilities:
            cap_list = [cap.get("capability_desc", "") for cap in capabilities[:3]]
            output.append(f"      Capabilities: {', '.join(cap_list)}")
        
        # Show domains
        industries = service.get("industries", [])
        if industries:
            domain_list = [ind.get("domain", "") for ind in industries]
            output.append(f"      Domains: {', '.join(domain_list)}")
            
        return "\n".join(output)
    
    def run_single_test(self, query: str, expected_services: List[str] = None,
                       domains: List[str] = None, capabilities: List[str] = None) -> Dict[str, Any]:
        """Run a single search test"""
        print(f"\n🔍 Testing: '{query}'")
        if domains:
            print(f"   Domains filter: {domains}")
        if capabilities:
            print(f"   Capabilities filter: {capabilities}")
            
        start_time = time.time()
        result = self.search(query, domains, capabilities)
        elapsed_time = time.time() - start_time
        
        if result["success"]:
            results = result["data"]
            if isinstance(results, dict) and "results" in results:
                # Handle wrapped response
                actual_results = results["results"]
                print(f"   ⏱️  Response time: {elapsed_time:.3f}s")
                print(f"   📊 Found {len(actual_results)} results")
                
                # Show top 5 results
                for i, res in enumerate(actual_results[:5]):
                    print(self.format_result(res))
            
            # Check expected results if provided
            if expected_services:
                found_services = [r["service"]["name"] for r in results]
                matches = []
                misses = []
                
                for expected in expected_services:
                    if expected in found_services[:5]:  # Check top 5
                        position = found_services.index(expected) + 1
                        matches.append(f"{expected} (#{position})")
                    else:
                        misses.append(expected)
                
                print(f"\n   ✅ Expected services found: {', '.join(matches) if matches else 'None'}")
                if misses:
                    print(f"   ❌ Expected services missing: {', '.join(misses)}")
                    
                result["validation"] = {
                    "expected": expected_services,
                    "found": found_services[:5],
                    "matches": len(matches),
                    "total_expected": len(expected_services)
                }
        else:
            print(f"   ❌ Search failed: {result['error']}")
            
        result["elapsed_time"] = elapsed_time
        return result
    
    def run_test_file(self, test_file: str):
        """Run tests from a JSON test file"""
        print(f"\n📁 Loading test cases from: {test_file}")
        
        try:
            with open(test_file, 'r') as f:
                test_data = json.load(f)
        except Exception as e:
            print(f"❌ Failed to load test file: {e}")
            return
        
        test_cases = test_data.get("test_cases", [])
        print(f"📋 Found {len(test_cases)} test cases")
        
        results = []
        passed = 0
        failed = 0
        
        for i, test_case in enumerate(test_cases):
            print(f"\n{'='*60}")
            print(f"Test Case #{i+1}: {test_case.get('description', 'No description')}")
            
            result = self.run_single_test(
                query=test_case.get("query"),
                expected_services=test_case.get("expected_services"),
                domains=test_case.get("domains"),
                capabilities=test_case.get("capabilities")
            )
            
            # Determine pass/fail
            if result["success"]:
                validation = result.get("validation", {})
                if validation:
                    if validation["matches"] >= len(validation["expected"]) * 0.6:  # 60% threshold
                        print("\n   🟢 Test PASSED")
                        passed += 1
                    else:
                        print("\n   🔴 Test FAILED (insufficient matches)")
                        failed += 1
                else:
                    print("\n   🟡 Test completed (no validation)")
                    passed += 1
            else:
                print("\n   🔴 Test FAILED (search error)")
                failed += 1
                
            results.append(result)
        
        # Summary
        print(f"\n{'='*60}")
        print(f"📊 Test Summary:")
        print(f"   Total tests: {len(test_cases)}")
        print(f"   ✅ Passed: {passed}")
        print(f"   ❌ Failed: {failed}")
        print(f"   Success rate: {(passed/len(test_cases)*100):.1f}%")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"search_test_results_{timestamp}.json"
        with open(results_file, 'w') as f:
            json.dump({
                "timestamp": timestamp,
                "summary": {
                    "total": len(test_cases),
                    "passed": passed,
                    "failed": failed
                },
                "results": results
            }, f, indent=2)
        print(f"\n📄 Results saved to: {results_file}")

def main():
    """Main test execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test KPATH Enterprise Search API")
    parser.add_argument("--query", "-q", help="Single query to test")
    parser.add_argument("--file", "-f", help="JSON file with test cases")
    parser.add_argument("--domains", "-d", nargs="+", help="Domain filters")
    parser.add_argument("--capabilities", "-c", nargs="+", help="Capability filters")
    parser.add_argument("--expected", "-e", nargs="+", help="Expected service names")
    
    args = parser.parse_args()
    
    # Initialize tester
    tester = SearchAPITester()
    
    # Authenticate
    if not tester.login():
        print("Failed to authenticate. Is the server running?")
        sys.exit(1)
    
    # Run tests
    if args.file:
        # Run test file
        tester.run_test_file(args.file)
    elif args.query:
        # Run single query
        tester.run_single_test(
            query=args.query,
            expected_services=args.expected,
            domains=args.domains,
            capabilities=args.capabilities
        )
    else:
        # Run some example queries
        print("\n🚀 Running example searches...")
        
        examples = [
            ("customer data management", ["CustomerDataAPI", "CustomerInsightsAgent"]),
            ("financial reporting", ["PerformanceAnalyticsAgent", "BudgetMonitoringAgent"]),
            ("email marketing", ["EmailMarketingAgent", "EmailService"]),
            ("fraud detection", ["FraudDetectionAgent"]),
            ("invoice processing", ["InvoiceProcessingAgent", "InvoiceAPI"])
        ]
        
        for query, expected in examples:
            tester.run_single_test(query, expected)

if __name__ == "__main__":
    main()
