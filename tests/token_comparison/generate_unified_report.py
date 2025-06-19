#!/usr/bin/env python3
"""
Comprehensive Token Consumption Report Generator

This script runs all token consumption tests and generates a unified report comparing:
1. Original PA approaches (tools_only vs agents_only)
2. Agent-to-agent standard workflow  
3. Agent-to-agent tool search workflow

Provides complete analysis across all workflow types.
"""

import json
import requests
import time
import os
import sys
import subprocess
from datetime import datetime
from typing import Dict, List, Tuple, Any
import statistics

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

# Import our test modules
from test_token_consumption_fixed import TokenConsumptionTest
from test_agent_to_agent_workflows import AgentWorkflowTest

# Configuration
BASE_URL = "http://localhost:8000"
API_KEY = "kpe_fElyteRdsZVlypzp7qPx6yL12MoLPJ07"
UNIFIED_REPORT_PATH = "test_reports/UNIFIED_TOKEN_ANALYSIS_REPORT.md"


class UnifiedTestRunner:
    """Runs all token consumption tests and generates unified analysis"""
    
    def __init__(self):
        self.test_start_time = None
        self.test_end_time = None
        self.pa_results = {}
        self.agent_results = {}
        
    def check_system_health(self) -> Dict[str, Any]:
        """Check if KPATH system is running and ready"""
        health_info = {
            "api_accessible": False,
            "api_version": None,
            "search_working": False
        }
        
        try:
            # Check health endpoint
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                health_info["api_accessible"] = True
                
            # Test search endpoint
            response = requests.get(
                f"{BASE_URL}/api/v1/search",
                params={"query": "test", "api_key": API_KEY},
                timeout=10
            )
            if response.status_code == 200:
                health_info["search_working"] = True
                health_info["api_version"] = "1.0.0"
                
        except Exception as e:
            health_info["error"] = str(e)
            
        return health_info
    
    def run_pa_focused_tests(self):
        """Run the original PA-focused token consumption tests"""
        print("🔍 Running PA-Focused Token Consumption Tests...")
        print("=" * 60)
        
        try:
            pa_test = TokenConsumptionTest()
            pa_test.run_all_tests()
            
            # Extract results
            if pa_test.test_results:
                successful_results = [r for r in pa_test.test_results 
                                    if r.approach_1_success and r.approach_2_success]
                
                if successful_results:
                    approach_1_tokens = [r.approach_1_tokens for r in successful_results]
                    approach_2_tokens = [r.approach_2_tokens for r in successful_results]
                    
                    self.pa_results = {
                        "test_count": len(successful_results),
                        "approach_1_avg": statistics.mean(approach_1_tokens),
                        "approach_2_avg": statistics.mean(approach_2_tokens),
                        "approach_1_name": "Traditional (agents_only + manual selection)",
                        "approach_2_name": "Direct Tool Search (tools_only)",
                        "raw_results": successful_results
                    }
                    
                    print(f"✅ PA Tests Complete - {len(successful_results)} successful scenarios")
                else:
                    print("❌ No successful PA test results")
            else:
                print("❌ PA tests failed to generate results")
                
        except Exception as e:
            print(f"❌ PA tests failed: {e}")
            self.pa_results = {"error": str(e)}
    
    def run_agent_workflow_tests(self):
        """Run the agent-to-agent workflow tests"""
        print("\n🤖 Running Agent-to-Agent Workflow Tests...")
        print("=" * 60)
        
        try:
            agent_test = AgentWorkflowTest()
            
            # Run a smaller subset for comprehensive analysis
            scenarios = agent_test.get_test_scenarios()[:8]  # First 8 scenarios
            
            standard_results = []
            tool_search_results = []
            
            for scenario_name, query in scenarios:
                try:
                    print(f"Testing: {scenario_name}")
                    standard_result, tool_search_result = agent_test.run_single_test(scenario_name, query)
                    
                    if standard_result.success:
                        standard_results.append(standard_result)
                    if tool_search_result.success:
                        tool_search_results.append(tool_search_result)
                        
                except Exception as e:
                    print(f"  ❌ Failed: {e}")
                    continue
            
            # Store results
            if standard_results and tool_search_results:
                self.agent_results = {
                    "test_count": len(standard_results),
                    "standard_avg": statistics.mean([r.total_tokens for r in standard_results]),
                    "tool_search_avg": statistics.mean([r.total_tokens for r in tool_search_results]),
                    "standard_name": "Standard Agent-to-Agent",
                    "tool_search_name": "Tool Search Agent-to-Agent",
                    "standard_results": standard_results,
                    "tool_search_results": tool_search_results
                }
                
                print(f"✅ Agent Tests Complete - {len(standard_results)} successful scenarios per workflow")
            else:
                print("❌ No successful agent test results")
                
        except Exception as e:
            print(f"❌ Agent tests failed: {e}")
            self.agent_results = {"error": str(e)}
    
    def generate_unified_report(self):
        """Generate comprehensive unified report comparing all approaches"""
        
        report_lines = []
        
        # Header
        report_lines.extend([
            "# KPATH Enterprise Unified Token Consumption Analysis",
            "",
            "**Comprehensive Comparison of All Workflow Approaches**",
            "",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Test Duration**: {(self.test_end_time - self.test_start_time).total_seconds():.1f} seconds",
            "",
            "## Executive Summary",
            "",
            "This report provides a comprehensive analysis of token consumption across different",
            "workflow approaches in KPATH Enterprise, from simple PA tool selection to complete",
            "agent-to-agent task execution workflows.",
            ""
        ])
        
        # System Health
        system_health = self.check_system_health()
        report_lines.extend([
            "## System Configuration",
            "",
            f"- **API Endpoint**: {BASE_URL}",
            f"- **API Status**: {'✅ Online' if system_health.get('api_accessible') else '❌ Offline'}",
            f"- **Search Status**: {'✅ Working' if system_health.get('search_working') else '❌ Failed'}",
            f"- **API Version**: {system_health.get('api_version', 'Unknown')}",
            ""
        ])
        
        # Results Analysis
        if "error" not in self.pa_results and "error" not in self.agent_results:
            report_lines.extend([
                "## Token Consumption Results",
                "",
                "### PA-Focused Approaches (Discovery Only)",
                ""
            ])
            
            if self.pa_results:
                pa_diff = self.pa_results["approach_2_avg"] - self.pa_results["approach_1_avg"]
                pa_pct = (pa_diff / self.pa_results["approach_1_avg"] * 100) if self.pa_results["approach_1_avg"] > 0 else 0
                
                report_lines.extend([
                    f"- **{self.pa_results['approach_1_name']}**: {self.pa_results['approach_1_avg']:.0f} tokens average",
                    f"- **{self.pa_results['approach_2_name']}**: {self.pa_results['approach_2_avg']:.0f} tokens average",
                    f"- **Difference**: {pa_diff:+.0f} tokens ({pa_pct:+.1f}%)",
                    f"- **Test Scenarios**: {self.pa_results['test_count']}",
                    ""
                ])
            
            if self.agent_results:
                agent_diff = self.agent_results["tool_search_avg"] - self.agent_results["standard_avg"]
                agent_pct = (agent_diff / self.agent_results["standard_avg"] * 100) if self.agent_results["standard_avg"] > 0 else 0
                
                report_lines.extend([
                    "### Agent-to-Agent Workflows (Complete Execution)",
                    "",
                    f"- **{self.agent_results['standard_name']}**: {self.agent_results['standard_avg']:.0f} tokens average",
                    f"- **{self.agent_results['tool_search_name']}**: {self.agent_results['tool_search_avg']:.0f} tokens average", 
                    f"- **Difference**: {agent_diff:+.0f} tokens ({agent_pct:+.1f}%)",
                    f"- **Test Scenarios**: {self.agent_results['test_count']}",
                    ""
                ])
        
        # Error handling
        if "error" in self.pa_results:
            report_lines.extend([
                "## PA Test Errors",
                f"- Error: {self.pa_results['error']}",
                ""
            ])
            
        if "error" in self.agent_results:
            report_lines.extend([
                "## Agent Test Errors", 
                f"- Error: {self.agent_results['error']}",
                ""
            ])
        
        # Footer
        report_lines.extend([
            "---",
            "",
            f"**Report Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**KPATH Enterprise Version**: 1.0.0",
            f"**Test Environment**: {BASE_URL}",
            ""
        ])
        
        return "\n".join(report_lines)
    
    def run_all_tests(self):
        """Run all tests and generate unified report"""
        self.test_start_time = datetime.now()
        
        print("🚀 KPATH Enterprise Unified Token Consumption Analysis")
        print("=" * 70)
        print(f"Started: {self.test_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Check system health first
        health = self.check_system_health()
        if not health.get("api_accessible") or not health.get("search_working"):
            print("❌ System health check failed - cannot proceed")
            print(f"API Accessible: {health.get('api_accessible')}")
            print(f"Search Working: {health.get('search_working')}")
            if "error" in health:
                print(f"Error: {health['error']}")
            return
        
        print("✅ System health check passed")
        print()
        
        # Run PA-focused tests
        self.run_pa_focused_tests()
        
        # Run agent workflow tests
        self.run_agent_workflow_tests()
        
        self.test_end_time = datetime.now()
        
        # Generate unified report
        print(f"\n📊 Generating Unified Analysis Report...")
        report_content = self.generate_unified_report()
        
        # Save report
        with open(UNIFIED_REPORT_PATH, "w") as f:
            f.write(report_content)
        
        print(f"✅ Unified report saved to: {UNIFIED_REPORT_PATH}")
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print executive summary to console"""
        print("\n" + "=" * 70)
        print("EXECUTIVE SUMMARY")
        print("=" * 70)
        
        if "error" not in self.pa_results and "error" not in self.agent_results:
            print(f"\n🔍 PA DISCOVERY APPROACHES:")
            print(f"   Traditional (agents_only): {self.pa_results['approach_1_avg']:.0f} tokens")
            print(f"   Direct Tool Search: {self.pa_results['approach_2_avg']:.0f} tokens")
            
            pa_diff = self.pa_results["approach_2_avg"] - self.pa_results["approach_1_avg"]
            pa_winner = "Traditional" if pa_diff > 0 else "Direct Tool Search"
            print(f"   Winner: {pa_winner} (saves {abs(pa_diff):.0f} tokens)")
            
            print(f"\n🤖 AGENT EXECUTION WORKFLOWS:")
            print(f"   Standard Agent-to-Agent: {self.agent_results['standard_avg']:.0f} tokens")
            print(f"   Tool Search Agent-to-Agent: {self.agent_results['tool_search_avg']:.0f} tokens")
            
            agent_diff = self.agent_results["tool_search_avg"] - self.agent_results["standard_avg"]
            agent_winner = "Standard" if agent_diff > 0 else "Tool Search"
            print(f"   Winner: {agent_winner} (saves {abs(agent_diff):.0f} tokens)")
            
            # Cross-comparison
            discovery_cost = self.pa_results['approach_1_avg']
            execution_cost = self.agent_results['standard_avg']
            multiplier = execution_cost / discovery_cost if discovery_cost > 0 else 0
            
            print(f"\n💰 COST ANALYSIS:")
            print(f"   Discovery Only: {discovery_cost:.0f} tokens")
            print(f"   Complete Execution: {execution_cost:.0f} tokens")
            print(f"   Execution Overhead: {multiplier:.1f}x discovery cost")
            
        else:
            if "error" in self.pa_results:
                print(f"❌ PA tests failed: {self.pa_results['error']}")
            if "error" in self.agent_results:
                print(f"❌ Agent tests failed: {self.agent_results['error']}")
        
        print(f"\n📄 Full analysis available in: {UNIFIED_REPORT_PATH}")
        print("=" * 70)


if __name__ == "__main__":
    runner = UnifiedTestRunner()
    runner.run_all_tests()
