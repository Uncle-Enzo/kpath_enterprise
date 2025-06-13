# KPATH Enterprise Search API Testing

This directory contains test scripts and data for testing the KPATH Enterprise Search API.

## Files

- `test_search_api.py` - Main test script for the Search API
- `search_test_cases.json` - 50 test cases with expected results
- `example_search_tests.py` - Simple examples of how to use the test script

## Prerequisites

1. Make sure the KPATH server is running:
   ```bash
   ./scripts/start_server.sh
   ```

2. Ensure you're using the torch-env:
   ```bash
   pyenv activate torch-env
   ```

## Usage

### Run a Single Query Test

```bash
# Basic search
./scripts/python_torch.sh scripts/test_search_api.py -q "customer data management"

# With expected results
./scripts/python_torch.sh scripts/test_search_api.py -q "payment processing" -e PaymentGatewayAPI InvoiceProcessingAgent

# With domain filter
./scripts/python_torch.sh scripts/test_search_api.py -q "analytics" -d Finance Marketing

# With capability filter
./scripts/python_torch.sh scripts/test_search_api.py -q "customer" -c retrieve update
```

### Run the Full Test Suite

```bash
# Run all 50 test cases
./scripts/python_torch.sh scripts/test_search_api.py -f test_data/search_test_cases.json
```

This will:
- Execute all 50 test cases
- Validate expected vs actual results
- Generate a pass/fail summary
- Save detailed results to `search_test_results_[timestamp].json`

### Run Example Tests

```bash
# Run example test scenarios
./scripts/python_torch.sh scripts/example_search_tests.py
```

## Test Case Format

Test cases in `search_test_cases.json` have this structure:

```json
{
  "id": 1,
  "description": "Search for customer data management",
  "query": "customer data management",
  "expected_services": ["CustomerDataAPI", "CustomerInsightsAgent"],
  "domains": null,  // Optional domain filters
  "capabilities": null  // Optional capability filters
}
```

## Understanding Results

### Single Query Output
```
🔍 Testing: 'customer data analytics'
   ⏱️  Response time: 0.125s
   📊 Found 5 results
  #1 CustomerInsightsAgent (Score: 0.649)
      Analyzes customer behavior, preferences, and journey to provide actionable bu...
      Capabilities: Analyze customer behavior patterns, Create customer segments...
      Domains: Business Intelligence, Customer Analytics, Marketing
```

### Test Suite Summary
```
📊 Test Summary:
   Total tests: 50
   ✅ Passed: 45
   ❌ Failed: 5
   Success rate: 90.0%
```

## Interpreting Scores

- **Score > 0.7**: Excellent match
- **Score 0.5-0.7**: Good match
- **Score 0.3-0.5**: Moderate match
- **Score < 0.3**: Weak match

## Adding New Test Cases

Edit `test_data/search_test_cases.json` and add new cases following the existing format. Consider:

1. **Coverage**: Test different types of queries
2. **Filters**: Include tests with domain and capability filters
3. **Edge Cases**: Test with misspellings, synonyms, partial matches
4. **Expected Results**: List the most relevant services (top 3-5)

## Troubleshooting

1. **Authentication Failed**: Check server is running and credentials are correct
2. **No Results**: Verify search index is built with `./scripts/python_torch.sh scripts/rebuild_search_index.py`
3. **Unexpected Results**: Check if services have been added/modified in database
4. **Connection Error**: Ensure server is running on http://localhost:8000
