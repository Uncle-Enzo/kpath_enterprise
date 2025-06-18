#!/usr/bin/env python3
"""
Token Consumption Comparison Test for KPATH Enterprise

This script compares token consumption between two approaches:
1. Basic search (agents_only) + manual tool selection  
2. Direct tool search (tools_only)

The test simulates a personal assistant making tool selection decisions
and measures the total token consumption for each approach.
"""

import json
import time
import requests
import logging
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import statistics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Install tiktoken if not available: pip install tiktoken
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    logger.warning("tiktoken not available - using character-based estimation")
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
    """Client for KPATH Enterprise API"""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: str = None):
        self.base_url = base_url
        self.api_key = api_key or "kpe_fElyteRdsZVlypzp7qPx6yL12MoLPJ07"  # Test API key from docs
        self.session = requests.Session()
    
    def search(self, query: str, search_mode: str = "agents_only", limit: int = 10) -> Tuple[Dict, int]:
        """
        Perform search and return results with response time
        
        Returns:
            Tuple of (response_data, response_time_ms)
        """
        url = f"{self.base_url}/api/v1/search"
        params = {
            "query": query,
            "search_mode": search_mode,
            "limit": limit,
            "api_key": self.api_key
        }
        
        start_time = time.time()
        try:
            response = self.session.get(url, params=params, timeout=30)
            response_time_ms = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                return response.json(), response_time_ms
            else:
                logger.error(f"API request failed: {response.status_code} - {response.text}")
                return {"error": f"HTTP {response.status_code}"}, response_time_ms
                
        except Exception as e:
            response_time_ms = int((time.time() - start_time) * 1000)
            logger.error(f"API request exception: {e}")
            return {"error": str(e)}, response_time_ms


class AssistantSimulator:
    """Simulates personal assistant decision-making processes"""
    
    def __init__(self, token_counter: TokenCounter):
        self.token_counter = token_counter
    
    def simulate_approach_1_reasoning(self, search_results: Dict, query: str) -> Tuple[Optional[str], int]:
        """
        Simulate reasoning process for Approach 1 (basic search + manual selection)
        
        Returns:
            Tuple of (selected_tool_name, reasoning_tokens_used)
        """
        # Simulate the reasoning process a personal assistant would go through
        reasoning_text = f"""
        Query: {query}
        
        Available services from search:
        """
        
        selected_tool = None
        
        if "results" in search_results:
            for i, result in enumerate(search_results["results"][:3]):  # Focus on top 3
                service = result.get("service", {})
                reasoning_text += f"\n{i+1}. {service.get('name', 'Unknown')} - {service.get('description', 'No description')}"
                
                # Simple heuristic for tool selection
                if not selected_tool:
                    selected_tool = service.get('name', 'Unknown')
        
        # Add reasoning about tool selection
        reasoning_text += f"\n\nSelected service: {selected_tool}\n"
        reasoning_text += "Now I need to determine what specific tools this service offers and select the most appropriate one.\n"
        reasoning_text += "This requires additional analysis of the service's capabilities and available tools.\n"
        
        # In real scenario, assistant would need to make additional API calls or reasoning
        reasoning_text += "Additional reasoning needed to select specific tool from service capabilities.\n"
        
        reasoning_tokens = self.token_counter.count_tokens(reasoning_text)
        return selected_tool, reasoning_tokens
    
    def simulate_approach_2_reasoning(self, search_results: Dict, query: str) -> Tuple[Optional[str], int]:
        """
        Simulate reasoning process for Approach 2 (direct tool search)
        
        Returns:
            Tuple of (selected_tool_name, reasoning_tokens_used)
        """
        reasoning_text = f"""
        Query: {query}
        
        Available tools from search:
        """
        
        selected_tool = None
        
        if "results" in search_results:
            for i, result in enumerate(search_results["results"][:3]):  # Focus on top 3
                tool_data = result.get("tool_data", {})
                if tool_data:
                    tool_name = tool_data.get("tool_name", "Unknown")
                    tool_desc = tool_data.get("tool_description", "No description")
                    reasoning_text += f"\n{i+1}. {tool_name} - {tool_desc}"
                    
                    if not selected_tool:
                        selected_tool = tool_name
        
        # Add selection reasoning
        reasoning_text += f"\n\nSelected tool: {selected_tool}\n"
        reasoning_text += "This tool directly matches my query requirements.\n"
        
        reasoning_tokens = self.token_counter.count_tokens(reasoning_text)
        return selected_tool, reasoning_tokens


class TokenConsumptionTest:
    """Main test orchestrator"""
    
    def __init__(self):
        self.token_counter = TokenCounter()
        self.kpath_client = KPathClient()
        self.assistant_simulator = AssistantSimulator(self.token_counter)
        self.test_results: List[TestResult] = []
    
    def get_test_scenarios(self) -> List[Tuple[str, str]]:
        """Define test scenarios (name, query)"""
        return [
            ("Payment Processing", "I need to process a payment for $150"),
            ("Customer Notification", "Send a notification to customer about shipment delivery"),
            ("Shipping Insurance", "Calculate shipping insurance for valuable items worth $5000"),
            ("Customer Data Lookup", "Get customer data for user ID 12345"),
            ("Invoice Generation", "Generate an invoice for recent order #ORD-2024-001"),
            ("Risk Assessment", "Assess risk for international shipping to Europe"),
            ("Quote Generation", "Generate shipping quote for 50 packages"),
            ("Coverage Analysis", "Analyze insurance coverage options for fragile goods"),
            ("Payment Gateway", "Process credit card payment with fraud detection"),
            ("Authentication Check", "Verify user authentication token")
        ]
    
    def run_approach_1(self, query: str) -> Tuple[int, int, bool, Optional[str]]:
        """
        Run Approach 1: Basic search (agents_only) + manual tool selection
        
        Returns:
            Tuple of (total_tokens, response_time_ms, success, selected_tool)
        """
        # Step 1: Perform basic search
        search_results, response_time = self.kpath_client.search(
            query=query, 
            search_mode="agents_only",
            limit=5
        )
        
        # Count tokens in API response
        api_response_tokens = self.token_counter.count_tokens(json.dumps(search_results))
        
        # Step 2: Simulate assistant reasoning and tool selection
        if "error" not in search_results:
            selected_tool, reasoning_tokens = self.assistant_simulator.simulate_approach_1_reasoning(
                search_results, query
            )
            success = selected_tool is not None
        else:
            selected_tool = None
            reasoning_tokens = 0
            success = False
        
        total_tokens = api_response_tokens + reasoning_tokens
        
        return total_tokens, response_time, success, selected_tool
    
    def run_approach_2(self, query: str) -> Tuple[int, int, bool, Optional[str]]:
        """
        Run Approach 2: Direct tool search (tools_only)
        
        Returns:
            Tuple of (total_tokens, response_time_ms, success, selected_tool)
        """
        # Step 1: Perform tool search
        search_results, response_time = self.kpath_client.search(
            query=query,
            search_mode="tools_only", 
            limit=5
        )
        
        # Count tokens in API response
        api_response_tokens = self.token_counter.count_tokens(json.dumps(search_results))
        
        # Step 2: Simulate assistant reasoning and tool selection
        if "error" not in search_results:
            selected_tool, reasoning_tokens = self.assistant_simulator.simulate_approach_2_reasoning(
                search_results, query
            )
            success = selected_tool is not None
        else:
            selected_tool = None
            reasoning_tokens = 0
            success = False
        
        total_tokens = api_response_tokens + reasoning_tokens
        
        return total_tokens, response_time, success, selected_tool
    
    def run_single_test(self, scenario_name: str, query: str) -> TestResult:
        """Run a single test scenario"""
        logger.info(f"Testing scenario: {scenario_name}")
        logger.info(f"Query: {query}")
        
        # Run Approach 1
        logger.info("Running Approach 1 (basic search + manual selection)...")
        app1_tokens, app1_time, app1_success, app1_tool = self.run_approach_1(query)
        
        # Small delay between tests
        time.sleep(1)
        
        # Run Approach 2  
        logger.info("Running Approach 2 (direct tool search)...")
        app2_tokens, app2_time, app2_success, app2_tool = self.run_approach_2(query)
        
        result = TestResult(
            scenario=scenario_name,
            query=query,
            approach_1_tokens=app1_tokens,
            approach_2_tokens=app2_tokens,
            approach_1_time_ms=app1_time,
            approach_2_time_ms=app2_time,
            approach_1_success=app1_success,
            approach_2_success=app2_success,
            approach_1_selected_tool=app1_tool,
            approach_2_selected_tool=app2_tool
        )
        
        logger.info(f"Results - App1: {app1_tokens} tokens, App2: {app2_tokens} tokens")
        logger.info("="*50)
        
        return result
    
    def run_all_tests(self):
        """Run all test scenarios"""
        logger.info("Starting Token Consumption Comparison Test")
        logger.info("="*60)
        
        scenarios = self.get_test_scenarios()
        
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
        
        logger.info("GENERATING COMPREHENSIVE COMPARISON REPORT")
        logger.info("="*80)
        
        # Calculate statistics
        approach_1_tokens = [r.approach_1_tokens for r in self.test_results if r.approach_1_success]
        approach_2_tokens = [r.approach_2_tokens for r in self.test_results if r.approach_2_success]
        
        approach_1_times = [r.approach_1_time_ms for r in self.test_results if r.approach_1_success]
        approach_2_times = [r.approach_2_time_ms for r in self.test_results if r.approach_2_success]
        
        # Success rates
        approach_1_success_rate = sum(1 for r in self.test_results if r.approach_1_success) / len(self.test_results)
        approach_2_success_rate = sum(1 for r in self.test_results if r.approach_2_success) / len(self.test_results)
        
        print("\n" + "="*80)
        print("KPATH ENTERPRISE TOKEN CONSUMPTION COMPARISON REPORT")
        print("="*80)
        print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total Scenarios Tested: {len(self.test_results)}")
        print(f"Token Counting Method: {'tiktoken (accurate)' if TIKTOKEN_AVAILABLE else 'character estimation'}")
        print()
        
        # Detailed results table
        print("DETAILED RESULTS BY SCENARIO")
        print("-" * 80)
        print(f"{'Scenario':<25} {'App1 Tokens':<12} {'App2 Tokens':<12} {'Difference':<12} {'Winner':<10}")
        print("-" * 80)
        
        total_app1_tokens = 0
        total_app2_tokens = 0
        app1_wins = 0
        app2_wins = 0
        
        for result in self.test_results:
            diff = result.approach_1_tokens - result.approach_2_tokens
            winner = "App1" if diff < 0 else "App2" if diff > 0 else "Tie"
            
            if winner == "App1":
                app1_wins += 1
            elif winner == "App2":
                app2_wins += 1
            
            total_app1_tokens += result.approach_1_tokens
            total_app2_tokens += result.approach_2_tokens
            
            print(f"{result.scenario[:24]:<25} {result.approach_1_tokens:<12} {result.approach_2_tokens:<12} {diff:+<12} {winner:<10}")
        