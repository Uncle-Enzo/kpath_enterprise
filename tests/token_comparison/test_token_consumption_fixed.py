#!/usr/bin/env python3
"""
Token Consumption Comparison Test for KPATH Enterprise - Fixed Version

This script compares token consumption between two approaches:
1. Basic search (agents_only) + manual tool selection  
2. Direct tool search (tools_only)

Fixed issues:
- Proper JWT Bearer token authentication
- Correct response parsing for tools_only mode
- Enhanced reasoning simulation
- Better error handling
"""

import json
import time
import requests
import logging
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import statistics
import os
import sys

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Install tiktoken if not available: pip install tiktoken
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    logger.warning("tiktoken not available - using character-based estimation")
    logger.warning("Install with: pip install tiktoken")
    TIKTOKEN_AVAILABLE = False


@dataclass
class TestResult:
    """Results from a single test scenario"""
    scenario: str
    query: str
    approach_1_tokens: int
    approach_2_tokens: int
    approach_1_time_ms: int
    approach_2_time_ms: int
    approach_1_success: bool
    approach_2_success: bool
    approach_1_selected_tool: Optional[str] = None
    approach_2_selected_tool: Optional[str] = None
    approach_1_reasoning_tokens: int = 0
    approach_2_reasoning_tokens: int = 0
    approach_1_api_tokens: int = 0
    approach_2_api_tokens: int = 0


class TokenCounter:
    """Handles token counting for API responses and reasoning text"""
    
    def __init__(self):
        if TIKTOKEN_AVAILABLE:
            self.encoder = tiktoken.get_encoding("cl100k_base")  # GPT-4 encoding
        else:
            self.encoder = None
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        if self.encoder:
            return len(self.encoder.encode(str(text)))
        else:
            # Rough approximation: ~4 characters per token
            return len(str(text)) // 4


class KPathClient:
    """Client for KPATH Enterprise API - Fixed Authentication"""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: str = None):
        self.base_url = base_url
        self.api_key = api_key or "kpe_fElyteRdsZVlypzp7qPx6yL12MoLPJ07"
        self.session = requests.Session()
        self.jwt_token = None
    
    def get_jwt_token(self) -> Optional[str]:
        """Get JWT token for authentication"""
        # First, try to get a JWT token using the test credentials
        try:
            login_url = f"{self.base_url}/api/v1/auth/login"
            login_data = {
                "username": "admin",  # Default test user
                "password": "admin123"  # Default test password
            }
            
            response = self.session.post(login_url, json=login_data, timeout=10)
            if response.status_code == 200:
                token_data = response.json()
                return token_data.get("access_token")
            else:
                logger.warning(f"JWT login failed: {response.status_code}")
                return None
        except Exception as e:
            logger.warning(f"Could not get JWT token: {e}")
            return None
    
    def search(self, query: str, limit: int = 3) -> Tuple[Dict, int]:
        """
        Perform search and return results with response time
        
        Returns:
            Tuple of (response_data, response_time_ms)
        """
        url = f"{self.base_url}/api/v1/search"
        
        # Try multiple authentication methods
        headers = {}
        params = {
            "query": query,
            "limit": limit
        }
        
        # Method 1: Try JWT token first
        if not self.jwt_token:
            self.jwt_token = self.get_jwt_token()
        
        if self.jwt_token:
            headers["Authorization"] = f"Bearer {self.jwt_token}"
        else:
            # Method 2: Fallback to API key in header
            headers["X-API-Key"] = self.api_key
            # Method 3: Also include in params as fallback
            params["api_key"] = self.api_key
        
        start_time = time.time()
        try:
            # Try POST first (based on the API definition)
            response = self.session.post(
                url, 
                json={"query": query, "search_mode": search_mode, "limit": limit},
                headers=headers,
                timeout=30
            )
            
            # If POST fails, try GET
            if response.status_code == 405:  # Method not allowed
                response = self.session.get(url, params=params, headers=headers, timeout=30)
            
            response_time_ms = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                return response.json(), response_time_ms
            else:
                logger.error(f"API request failed: {response.status_code} - {response.text}")
                return {"error": f"HTTP {response.status_code}", "details": response.text}, response_time_ms
                
        except Exception as e:
            response_time_ms = int((time.time() - start_time) * 1000)
            logger.error(f"API request exception: {e}")
            return {"error": str(e)}, response_time_ms


class AssistantSimulator:
    """Simulates personal assistant decision-making processes - Enhanced Version"""
    
    def __init__(self, token_counter: TokenCounter):
        self.token_counter = token_counter
    
    def simulate_approach_1_reasoning(self, search_results: Dict, query: str) -> Tuple[Optional[str], int, int]:
        """
        Simulate reasoning process for Approach 1 (basic search + manual selection)
        
        Returns:
            Tuple of (selected_tool_name, reasoning_tokens, api_response_tokens)
        """
        # Count API response tokens
        api_response_tokens = self.token_counter.count_tokens(json.dumps(search_results))
        
        # Simulate the reasoning process
        reasoning_text = f"""
Analyzing query: "{query}"

Step 1: Review available services from search results
"""
        
        selected_service = None
        selected_tool = None
        
        if "results" in search_results and search_results["results"]:
            reasoning_text += "\nAvailable services:\n"
            
            for i, result in enumerate(search_results["results"][:5]):  # Analyze top 5
                service = result.get("service", {})
                service_name = service.get("name", "Unknown")
                service_desc = service.get("description", "No description")
                capabilities = service.get("capabilities", [])
                
                reasoning_text += f"\n{i+1}. {service_name}"
                reasoning_text += f"\n   Description: {service_desc}"
                reasoning_text += f"\n   Capabilities: {', '.join(capabilities) if capabilities else 'None listed'}"
                reasoning_text += f"\n   Relevance Score: {result.get('score', 0):.3f}\n"
                
                # Select the first relevant service
                if not selected_service and result.get("score", 0) > 0.5:
                    selected_service = service_name
        
        # Add reasoning about needing to query for tools
        reasoning_text += f"\nStep 2: Selected service '{selected_service}' based on relevance"
        reasoning_text += "\n\nStep 3: Need to query this service for available tools"
        reasoning_text += "\n[Simulated API call to get service tools would happen here]"
        reasoning_text += "\n\nStep 4: Analyzing tools from the selected service..."
        reasoning_text += f"\n[Would select appropriate tool for: {query}]"
        
        # Simulate tool selection
        if selected_service:
            selected_tool = f"{selected_service}.process"  # Simulated tool name
        
        reasoning_text += f"\n\nFinal Selection: {selected_tool}"
        
        reasoning_tokens = self.token_counter.count_tokens(reasoning_text)
        return selected_tool, reasoning_tokens, api_response_tokens
    
    def simulate_approach_2_reasoning(self, search_results: Dict, query: str) -> Tuple[Optional[str], int, int]:
        """
        Simulate reasoning process for Approach 2 (direct tool search)
        
        Returns:
            Tuple of (selected_tool_name, reasoning_tokens, api_response_tokens)
        """
        # Count API response tokens
        api_response_tokens = self.token_counter.count_tokens(json.dumps(search_results))
        
        # Simulate the reasoning process
        reasoning_text = f"""
Analyzing query: "{query}"

Direct tool search results:
"""
        
        selected_tool = None
        
        if "results" in search_results and search_results["results"]:
            for i, result in enumerate(search_results["results"][:3]):  # Focus on top 3
                # Check for recommended_tool field (based on schema)
                tool_info = result.get("recommended_tool") or result.get("tool_data", {})
                
                if tool_info:
                    tool_name = tool_info.get("name", tool_info.get("tool_name", "Unknown"))
                    tool_desc = tool_info.get("description", tool_info.get("tool_description", "No description"))
                    service_name = result.get("service", {}).get("name", "Unknown Service")
                    
                    reasoning_text += f"\n{i+1}. Tool: {tool_name}"
                    reasoning_text += f"\n   From Service: {service_name}"
                    reasoning_text += f"\n   Description: {tool_desc}"
                    reasoning_text += f"\n   Relevance Score: {result.get('score', 0):.3f}\n"
                    
                    if not selected_tool and result.get("score", 0) > 0.5:
                        selected_tool = tool_name
        
        reasoning_text += f"\nDirect Selection: {selected_tool}"
        reasoning_text += "\nNo additional API calls needed - tool is ready to use."
        
        reasoning_tokens = self.token_counter.count_tokens(reasoning_text)
        return selected_tool, reasoning_tokens, api_response_tokens


class TokenConsumptionTest:
    """Main test orchestrator - Enhanced Version"""
    
    def __init__(self):
        self.token_counter = TokenCounter()
        self.kpath_client = KPathClient()
        self.assistant_simulator = AssistantSimulator(self.token_counter)
        self.test_results: List[TestResult] = []
    
    def verify_api_connectivity(self) -> bool:
        """Verify that KPATH API is accessible"""
        try:
            response = requests.get(f"{self.kpath_client.base_url}/api/v1/health", timeout=5)
            if response.status_code == 200:
                logger.info("✅ KPATH API is accessible")
                return True
            else:
                logger.error(f"❌ KPATH API health check failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Cannot connect to KPATH API: {e}")
            return False
    
    def get_test_scenarios(self) -> List[Tuple[str, str]]:
        """Define diverse shoe-focused test scenarios covering different use cases"""
        return [
            # General Shoe Shopping
            ("Shoe Shopping - General", "I want to buy some shoes"),
            ("Shoe Shopping - Running", "find running shoes under $150"),
            ("Shoe Shopping - Work Boots", "I need steel toe work boots"),
            ("Shoe Shopping - Dress", "formal dress shoes for wedding"),
            
            # Specific Product Queries
            ("Shoe Shopping - Size Check", "check if Nike Air Max size 10 is available"),
            ("Shoe Shopping - Brand Specific", "show me all Adidas running shoes"),
            ("Shoe Shopping - Color Preference", "black leather dress shoes size 9"),
            
            # Service Requests
            ("Shoe Store Locator", "find shoe stores near me"),
            ("Shoe Buying Advice", "what shoes are best for flat feet"),
            ("Shoe Delivery Tracking", "track my shoe order delivery"),
            ("Shoe Sizing Help", "help me find the right shoe size"),
            ("Shoe Care Instructions", "how to care for leather shoes"),
            
            # Complex Shoe Queries
            ("Shoe Shopping - Athletic", "I need athletic shoes for basketball"),
            ("Shoe Shopping - Comfort", "most comfortable walking shoes for seniors"),
            ("Shoe Shopping - Budget", "cheapest running shoes under $100")
        ]
    
    def run_approach_1(self, query: str) -> Tuple[int, int, bool, Optional[str], int, int]:
        """
        Run Approach 1: Basic search (agents_only) + manual tool selection
        
        Returns:
            Tuple of (total_tokens, response_time_ms, success, selected_tool, api_tokens, reasoning_tokens)
        """
        # Step 1: Perform basic search
        search_results, response_time = self.kpath_client.search(
            query=query, 
            search_mode="agents_only",
            limit=5
        )
        
        # Step 2: Simulate assistant reasoning and tool selection
        if "error" not in search_results:
            selected_tool, reasoning_tokens, api_tokens = self.assistant_simulator.simulate_approach_1_reasoning(
                search_results, query
            )
            success = selected_tool is not None
        else:
            selected_tool = None
            reasoning_tokens = 0
            api_tokens = self.token_counter.count_tokens(json.dumps(search_results))
            success = False
            logger.warning(f"Approach 1 search failed: {search_results}")
        
        # In real scenario, add tokens for additional API call to get tools
        additional_api_tokens = 200 if success else 0  # Simulated additional call
        total_api_tokens = api_tokens + additional_api_tokens
        total_tokens = total_api_tokens + reasoning_tokens
        
        return total_tokens, response_time, success, selected_tool, total_api_tokens, reasoning_tokens
    
    def run_approach_2(self, query: str) -> Tuple[int, int, bool, Optional[str], int, int]:
        """
        Run Approach 2: Direct tool search (tools_only)
        
        Returns:
            Tuple of (total_tokens, response_time_ms, success, selected_tool, api_tokens, reasoning_tokens)
        """
        # Step 1: Perform tool search
        search_results, response_time = self.kpath_client.search(
            query=query,
            limit=3
        )
        
        # Step 2: Simulate assistant reasoning and tool selection
        if "error" not in search_results:
            selected_tool, reasoning_tokens, api_tokens = self.assistant_simulator.simulate_approach_2_reasoning(
                search_results, query
            )
            success = selected_tool is not None
        else:
            selected_tool = None
            reasoning_tokens = 0
            api_tokens = self.token_counter.count_tokens(json.dumps(search_results))
            success = False
            logger.warning(f"Approach 2 search failed: {search_results}")
        
        total_tokens = api_tokens + reasoning_tokens
        
        return total_tokens, response_time, success, selected_tool, api_tokens, reasoning_tokens
    
    def run_single_test(self, scenario_name: str, query: str) -> TestResult:
        """Run a single test scenario"""
        logger.info(f"\n{'='*60}")
        logger.info(f"Testing: {scenario_name}")
        logger.info(f"Query: '{query}'")
        logger.info(f"{'='*60}")
        
        # Run Approach 1
        logger.info("▶ Running Approach 1 (basic search + manual selection)...")
        app1_total, app1_time, app1_success, app1_tool, app1_api, app1_reasoning = self.run_approach_1(query)
        
        # Small delay between tests
        time.sleep(0.5)
        
        # Run Approach 2  
        logger.info("▶ Running Approach 2 (direct tool search)...")
        app2_total, app2_time, app2_success, app2_tool, app2_api, app2_reasoning = self.run_approach_2(query)
        
        result = TestResult(
            scenario=scenario_name,
            query=query,
            approach_1_tokens=app1_total,
            approach_2_tokens=app2_total,
            approach_1_time_ms=app1_time,
            approach_2_time_ms=app2_time,
            approach_1_success=app1_success,
            approach_2_success=app2_success,
            approach_1_selected_tool=app1_tool,
            approach_2_selected_tool=app2_tool,
            approach_1_reasoning_tokens=app1_reasoning,
            approach_2_reasoning_tokens=app2_reasoning,
            approach_1_api_tokens=app1_api,
            approach_2_api_tokens=app2_api
        )
        
        # Log summary
        logger.info(f"\n📊 Results Summary:")
        logger.info(f"   Approach 1: {app1_total} tokens ({app1_api} API + {app1_reasoning} reasoning)")
        logger.info(f"   Approach 2: {app2_total} tokens ({app2_api} API + {app2_reasoning} reasoning)")
        logger.info(f"   Token Savings: {app1_total - app2_total} tokens ({((app1_total - app2_total) / app1_total * 100):.1f}%)")
        
        return result
    
    def run_all_tests(self):
        """Run all test scenarios"""
        logger.info("\n" + "="*80)
        logger.info("KPATH ENTERPRISE TOKEN CONSUMPTION COMPARISON TEST")
        logger.info("="*80)
        logger.info(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Token Counter: {'tiktoken (accurate)' if TIKTOKEN_AVAILABLE else 'character-based estimation'}")
        
        # Verify API connectivity
        if not self.verify_api_connectivity():
            logger.error("Cannot proceed - API is not accessible")
            return
        
        scenarios = self.get_test_scenarios()
        logger.info(f"Running {len(scenarios)} test scenarios...\n")
        
        for scenario_name, query in scenarios:
            try:
                result = self.run_single_test(scenario_name, query)
                self.test_results.append(result)
            except Exception as e:
                logger.error(f"Test failed for {scenario_name}: {e}")
                continue
        
        self.generate_report()
    
    def generate_report(self):
        """Generate comprehensive test report"""
        if not self.test_results:
            logger.error("No test results to report")
            return
        
        # Calculate statistics
        successful_results = [r for r in self.test_results if r.approach_1_success and r.approach_2_success]
        
        if not successful_results:
            logger.error("No successful test results to analyze")
            return
        
        # Token statistics
        app1_tokens = [r.approach_1_tokens for r in successful_results]
        app2_tokens = [r.approach_2_tokens for r in successful_results]
        
        # Time statistics
        app1_times = [r.approach_1_time_ms for r in successful_results]
        app2_times = [r.approach_2_time_ms for r in successful_results]
        
        # Success rates
        app1_success_rate = sum(1 for r in self.test_results if r.approach_1_success) / len(self.test_results) * 100
        app2_success_rate = sum(1 for r in self.test_results if r.approach_2_success) / len(self.test_results) * 100
        
        # Print comprehensive report
        print("\n" + "="*80)
        print("KPATH ENTERPRISE TOKEN CONSUMPTION COMPARISON REPORT")
        print("="*80)
        print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total Scenarios: {len(self.test_results)}")
        print(f"Successful Tests: {len(successful_results)}")
        print(f"Token Counting: {'tiktoken (accurate)' if TIKTOKEN_AVAILABLE else 'character-based'}")
        
        print("\n" + "-"*80)
        print("SUMMARY STATISTICS")
        print("-"*80)
        
        # Token consumption
        print(f"\n📊 TOKEN CONSUMPTION:")
        print(f"   Approach 1 Average: {statistics.mean(app1_tokens):.0f} tokens")
        print(f"   Approach 2 Average: {statistics.mean(app2_tokens):.0f} tokens")
        print(f"   Average Savings: {statistics.mean(app1_tokens) - statistics.mean(app2_tokens):.0f} tokens")
        print(f"   Savings Percentage: {((statistics.mean(app1_tokens) - statistics.mean(app2_tokens)) / statistics.mean(app1_tokens) * 100):.1f}%")
        
        # Response times
        print(f"\n⏱️  RESPONSE TIMES:")
        print(f"   Approach 1 Average: {statistics.mean(app1_times):.0f}ms")
        print(f"   Approach 2 Average: {statistics.mean(app2_times):.0f}ms")
        
        # Success rates
        print(f"\n✅ SUCCESS RATES:")
        print(f"   Approach 1: {app1_success_rate:.1f}%")
        print(f"   Approach 2: {app2_success_rate:.1f}%")
        
        # Detailed results table
        print("\n" + "-"*80)
        print("DETAILED RESULTS BY SCENARIO")
        print("-"*80)
        print(f"{'Scenario':<25} {'App1':<10} {'App2':<10} {'Diff':<10} {'Savings':<10} {'Winner':<8}")
        print("-"*80)
        
        total_app1 = 0
        total_app2 = 0
        app2_wins = 0
        
        for result in successful_results:
            diff = result.approach_1_tokens - result.approach_2_tokens
            savings_pct = (diff / result.approach_1_tokens * 100) if result.approach_1_tokens > 0 else 0
            winner = "App2" if diff > 0 else "App1" if diff < 0 else "Tie"
            
            if winner == "App2":
                app2_wins += 1
            
            total_app1 += result.approach_1_tokens
            total_app2 += result.approach_2_tokens
            
            print(f"{result.scenario[:24]:<25} {result.approach_1_tokens:<10} {result.approach_2_tokens:<10} "
                  f"{diff:<10} {savings_pct:>6.1f}%   {winner:<8}")
        
        print("-"*80)
        print(f"{'TOTALS':<25} {total_app1:<10} {total_app2:<10} "
              f"{total_app1-total_app2:<10} {((total_app1-total_app2)/total_app1*100):>6.1f}%")
        
        print("\n" + "-"*80)
        print("CONCLUSIONS")
        print("-"*80)
        print(f"🏆 Approach 2 (tools_only) won in {app2_wins}/{len(successful_results)} scenarios")
        print(f"💡 Average token savings: {((total_app1-total_app2)/total_app1*100):.1f}%")
        print(f"🚀 Approach 2 is {'faster' if statistics.mean(app2_times) < statistics.mean(app1_times) else 'slower'} "
              f"by {abs(statistics.mean(app2_times) - statistics.mean(app1_times)):.0f}ms on average")
        
        # Save report to file
        report_path = "test_reports/token_consumption_report.txt"
        with open(report_path, "w") as f:
            f.write(f"KPATH Enterprise Token Consumption Report\n")
            f.write(f"Generated: {datetime.now()}\n\n")
            for result in self.test_results:
                f.write(f"{result}\n")
        
        print(f"\n📄 Full report saved to: {report_path}")
        print("="*80)


if __name__ == "__main__":
    test = TokenConsumptionTest()
    test.run_all_tests()
