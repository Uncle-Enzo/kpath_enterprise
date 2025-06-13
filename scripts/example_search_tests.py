#!/usr/bin/env python
"""
Simple example of using the KPATH Search API test script
"""
import subprocess
import sys

# Make the script executable
script_path = "/Users/james/claude_development/kpath_enterprise/scripts/test_search_api.py"

print("KPATH Enterprise Search API Test Examples")
print("=" * 60)

# Example 1: Single query test
print("\n1. Testing a single query:")
print("-" * 40)
cmd = [
    "/Users/james/.pyenv/versions/3.10.13/envs/torch-env/bin/python",
    script_path,
    "-q", "customer data analytics"
]
subprocess.run(cmd)

# Example 2: Query with expected results
print("\n\n2. Testing with expected results:")
print("-" * 40)
cmd = [
    "/Users/james/.pyenv/versions/3.10.13/envs/torch-env/bin/python",
    script_path,
    "-q", "payment processing",
    "-e", "PaymentGatewayAPI", "InvoiceProcessingAgent"
]
subprocess.run(cmd)

# Example 3: Query with domain filter
print("\n\n3. Testing with domain filter:")
print("-" * 40)
cmd = [
    "/Users/james/.pyenv/versions/3.10.13/envs/torch-env/bin/python",
    script_path,
    "-q", "analytics",
    "-d", "Finance",
    "-e", "PerformanceAnalyticsAgent"
]
subprocess.run(cmd)

# Example 4: Run full test suite
print("\n\n4. To run the full test suite (50 test cases):")
print("-" * 40)
print("Run: ./scripts/python_torch.sh scripts/test_search_api.py -f test_data/search_test_cases.json")
print("\nThis will:")
print("- Run all 50 test cases")
print("- Validate expected results")
print("- Generate a summary report")
print("- Save detailed results to a JSON file")
