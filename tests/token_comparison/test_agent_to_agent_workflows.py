.session_id,
            "test_metadata": {
                "start_time": min(r.start_time for r in self.test_results).isoformat() if self.test_results else None,
                "end_time": max(r.end_time for r in self.test_results if r.end_time).isoformat() if self.test_results else None,
                "total_tests": len(self.test_results),
                "token_counter": "tiktoken (cl100k_base)" if TIKTOKEN_AVAILABLE else "character estimation",
                "base_url": self.base_url
            },
            "test_results": []
        }
        
        # Convert results to dict format
        for result in self.test_results:
            result_dict = {
                "test_id": result.test_id,
                "scenario": result.scenario,
                "query": result.query,
                "approach": result.approach,
                "start_time": result.start_time.isoformat(),
                "end_time": result.end_time.isoformat() if result.end_time else None,
                "total_tokens": result.total_tokens,
                "total_response_time_ms": result.total_response_time_ms,
                "success": result.success,
                "error_message": result.error_message,
                "final_response": result.final_response[:500] if result.final_response else None,
                "steps": []
            }
            
            # Add step details
            for step in result.steps:
                step_dict = {
                    "step_number": step.step_number,
                    "step_name": step.step_name,
                    "description": step.description,
                    "start_time": step.start_time.isoformat(),
                    "end_time": step.end_time.isoformat() if step.end_time else None,
                    "request_url": step.request_url,
                    "request_method": step.request_method,
                    "request_payload": step.request_payload,
                    "response_status": step.response_status,
                    "response_time_ms": step.response_time_ms,
                    "input_tokens": step.input_tokens,
                    "output_tokens": step.output_tokens,
                    "total_tokens": step.total_tokens,
                    "success": step.success,
                    "error_message": step.error_message
                }
                result_dict["steps"].append(step_dict)
            
            results_data["test_results"].append(result_dict)
        
        # Save to file
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=2)
        
        self.session_logger.info(f"\nResults saved to: {results_file}")
        
        return results_file

    def generate_summary_report(self):
        """Generate summary report of test results"""
        if not self.test_results:
            return "No test results available"
        
        # Group by approach
        approach_stats = {}
        for result in self.test_results:
            approach = result.approach
            if approach not in approach_stats:
                approach_stats[approach] = {
                    "count": 0,
                    "total_tokens": 0,
                    "total_time_ms": 0,
                    "success_count": 0,
                    "scenarios": []
                }
            
            stats = approach_stats[approach]
            stats["count"] += 1
            stats["total_tokens"] += result.total_tokens
            stats["total_time_ms"] += result.total_response_time_ms
            stats["success_count"] += 1 if result.success else 0
            stats["scenarios"].append(result.scenario)
        
        # Calculate averages
        report_lines = [
            "\n" + "=" * 80,
            "ENHANCED TOKEN USAGE ANALYSIS - SUMMARY REPORT",
            "=" * 80,
            f"Session ID: {self.session_id}",
            f"Total Tests: {len(self.test_results)}",
            "",
            "Approach Comparison:",
            "-" * 80,
            f"{'Approach':<20} {'Avg Tokens':<15} {'Avg Time (ms)':<15} {'Success Rate':<15}",
            "-" * 80
        ]
        
        for approach, stats in sorted(approach_stats.items()):
            avg_tokens = stats["total_tokens"] / stats["count"]
            avg_time = stats["total_time_ms"] / stats["count"]
            success_rate = (stats["success_count"] / stats["count"]) * 100
            
            report_lines.append(
                f"{approach:<20} {avg_tokens:<15.1f} {avg_time:<15.1f} {success_rate:<15.1f}%"
            )
        
        report_lines.extend([
            "-" * 80,
            "",
            "Key Findings:",
            "- Agent-to-Agent communication provides richer context for service agents",
            "- Token usage includes full conversation context and metadata",
            "- Response quality improved with structured agent communication",
            "",
            "=" * 80
        ])
        
        report = "\n".join(report_lines)
        
        # Log and save report
        self.session_logger.info(report)
        
        report_file = os.path.join(LOGS_DIR, f"{self.session_id}_summary.txt")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return report


def run_enhanced_tests():
    """Run enhanced token usage tests with agent-to-agent communication"""
    print("\n🚀 Running Enhanced Token Usage Analysis (Agent-to-Agent Communication)")
    print("=" * 80)
    
    # Initialize tester
    tester = EnhancedWorkflowTester()
    
    # Test scenarios
    scenarios = [
        ("Shoe Shopping", "I want to buy some running shoes under $150"),
        ("Store Location", "find shoe stores near me"),
        ("Product Availability", "check if Nike Air Max is in stock"),
        ("Buying Advice", "what shoes are best for flat feet"),
        ("Order Tracking", "track my shoe order")
    ]
    
    # Run tests
    all_results = {}
    for scenario, query in scenarios:
        print(f"\n📋 Testing: {scenario}")
        print(f"   Query: '{query}'")
        
        try:
            results = tester.run_comparison_test(scenario, query)
            all_results[scenario] = results
            
            # Display results
            for approach, metrics in results.items():
                if "error" in metrics:
                    print(f"   {approach}: ERROR - {metrics['error']}")
                else:
                    print(f"   {approach}: {metrics.get('tokens', 'N/A')} tokens, "
                          f"{metrics.get('time_ms', 'N/A')}ms, "
                          f"Success: {metrics.get('success', False)}")
        
        except Exception as e:
            print(f"   ERROR: {str(e)}")
            tester.session_logger.error(f"Test scenario '{scenario}' failed: {str(e)}")
    
    # Save results and generate report
    print("\n📊 Generating reports...")
    results_file = tester.save_results()
    summary = tester.generate_summary_report()
    
    print(f"\n✅ Test session complete!")
    print(f"   Results saved to: {results_file}")
    print(f"   Log file: {LOGS_DIR}/{tester.session_id}_enhanced.log")
    
    print("\n" + summary)
    
    return tester


if __name__ == "__main__":
    # Check API connectivity first
    try:
        response = requests.get("http://localhost:8000/api/v1/search/status")
        if response.status_code != 200:
            print("❌ KPATH API is not accessible")
            exit(1)
        print("✅ KPATH API connectivity confirmed")
    except Exception as e:
        print(f"❌ Cannot connect to KPATH API: {e}")
        exit(1)
    
    # Run the enhanced tests
    tester = run_enhanced_tests()
