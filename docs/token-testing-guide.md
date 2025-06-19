# KPATH Enterprise Token Usage Testing Guide

## Overview

KPATH Enterprise includes a comprehensive token usage testing framework that measures and compares the efficiency of different search approaches. The testing system provides detailed logging, complete HTTP request/response capture, and structured analysis to help optimize production deployments.

## Quick Start

### Running the Tests

The simplest way to run comprehensive token analysis:

```bash
cd /Users/james/claude_development/kpath_enterprise
./tests/token_comparison/run_all_token_tests.sh
```

This automatically provides:
- ✅ **Detailed workflow analysis** with step-by-step documentation
- ✅ **Individual log files** for each test session
- ✅ **Complete HTTP capture** with requests, responses, and timing
- ✅ **Structured JSON results** for analysis and automation
- ✅ **Token breakdown** for every operation using tiktoken
- ✅ **Performance metrics** with precise timing measurements

### Alternative Options

```bash
# Basic unified report only (legacy mode)
./tests/token_comparison/run_all_token_tests.sh --simple

# Direct execution of logging version
./tests/token_comparison/run_logged_workflow_test.sh

# Python script execution
cd tests/token_comparison
python3 test_detailed_workflows_with_logging.py
```

## What Gets Tested

### Test Scenarios
The framework tests 5 realistic scenarios:
1. **Shoe Shopping**: "I want to buy some shoes"
2. **Payment Processing**: "process payment for $150"
3. **Customer Notification**: "send notification to customer"  
4. **Shipping Insurance**: "calculate shipping insurance for valuable items"
5. **Invoice Generation**: "generate invoice for order"

### Approaches Compared
Each scenario tests 4 different approaches:
1. **Traditional (agents_only)**: Basic service search + manual tool selection
2. **Tools Full (tools_only)**: Direct tool search with complete metadata
3. **Tools Compact (optimized)**: Tool search with reduced metadata
4. **Tools Minimal (ultra-light)**: Ultra-optimized tool search

### Workflow Steps Analyzed
Each approach is broken down into detailed steps with **complete HTTP capture**:
1. **PA Agent Query Processing**: Initial query analysis
2. **KPATH Search**: Search for relevant tools/services (full HTTP request/response logged)
3. **Analysis & Planning**: Result processing and execution planning
4. **Service/Tool Communication**: **🆕 ACTUAL HTTP calls to target services/tools logged**
   - **Traditional Approach**: PA Agent → Service Chat endpoint (e.g., `/agents/shoes/chat`)
   - **Tools Approach**: PA Agent → Specific Tool endpoints (e.g., `/agents/shoes/search`)
   - **Complete conversation captured**: Request payloads, response data, timing, tokens

## Output Files and Locations

### Generated Files
Every test run creates files in `tests/token_comparison/test_logs/`:

#### 1. Session Log File (`.log`)
**Filename**: `token_test_YYYYMMDD_HHMMSS_sessionid.log`

**Contents**:
- Complete workflow documentation
- Every HTTP request and response
- Step-by-step token breakdown
- Performance timing analysis
- Error tracking and debugging information

**Sample Log Entry** (Enhanced with actual service communication):
```
2025-06-19 10:30:15 | INFO | STEP 4: Service Communication
2025-06-19 10:30:15 | INFO |   Description: PA Agent communicates with ShoesAgent
2025-06-19 10:30:15 | INFO |   Request URL: POST http://localhost:8000/agents/shoes/chat
2025-06-19 10:30:15 | INFO |   Request Payload: {
  "message": "User wants help with: I want to buy some shoes. Please provide appropriate assistance."
}
2025-06-19 10:30:15 | INFO |   Response Status: HTTP 200
2025-06-19 10:30:15 | INFO |   Response Time: 245ms
2025-06-19 10:30:15 | INFO |   Response Data: {
  "response": "I can help you find shoes! Here are some great options..."
}
2025-06-19 10:30:15 | INFO |   Tokens: 15 input + 156 output = 171 total
2025-06-19 10:30:15 | INFO |   Success: True
```

#### 2. JSON Results File (`_results.json`)
**Filename**: `token_test_YYYYMMDD_HHMMSS_sessionid_results.json`

**Contents**: Machine-readable structured data including:
- Session metadata
- Complete test results
- Step-by-step details
- Token usage breakdown
- Performance metrics

**Use Cases**:
- Automated analysis and reporting
- Integration with monitoring tools
- Historical trend analysis
- Cost modeling and optimization

### Viewing Results

#### Latest Log File
```bash
# View the most recent log
tail -f tests/token_comparison/test_logs/$(ls -t tests/token_comparison/test_logs/*.log | head -1)

# List all log files
ls -la tests/token_comparison/test_logs/
```

#### JSON Analysis
```bash
# View structured results
cat tests/token_comparison/test_logs/*_results.json | jq '.'

# Extract specific metrics
jq '.test_results[] | {scenario, approach, total_tokens, total_response_time_ms}' tests/token_comparison/test_logs/*_results.json
```

## Understanding the Results

### Key Metrics

#### Token Usage
- **Input Tokens**: Tokens used for requests (queries, parameters)
- **Output Tokens**: Tokens returned in responses
- **Total Tokens**: Sum of input and output tokens per step/test

#### Performance
- **Response Time**: Milliseconds for each HTTP request
- **Success Rate**: Percentage of successful operations
- **Step Duration**: Time taken for each workflow step

#### Efficiency Rankings
Based on recent test results:
1. **Tools Minimal**: 1,905 tokens avg, 243ms, 100% success ⭐ **RECOMMENDED**
2. **Tools Compact**: 3,142 tokens avg, 243ms, 100% success
3. **Traditional**: 3,324 tokens avg, 760ms, 100% success
4. **Tools Full**: 8,794 tokens avg, 271ms, 100% success

### Sample Results Interpretation

```
Approach             Avg Tokens   Avg Time (ms)   Success Rate
tools_minimal        1,905        243             100.0%
traditional          3,324        760             100.0%
tools_compact        3,142        243             100.0%
tools_full           8,794        271             100.0%
```

**Key Insight**: Tools Minimal uses **42.7% fewer tokens** than traditional approach while being **3x faster**.

## Architecture and File Structure

### Test Framework Components

```
tests/token_comparison/
├── run_all_token_tests.sh                    # Main test runner (comprehensive by default)
├── run_logged_workflow_test.sh               # Standalone logging test runner
├── test_detailed_workflows_with_logging.py   # Enhanced test implementation
├── test_detailed_workflows.py                # Basic detailed workflow tests
├── test_optimized_comparison.py              # Optimization comparison tests
├── generate_unified_report.py                # Report generation
├── test_logs/                                # Generated log files
│   ├── token_test_YYYYMMDD_HHMMSS_*.log      # Session log files
│   └── token_test_YYYYMMDD_HHMMSS_*_results.json # JSON results
└── test_reports/                             # Generated reports
    ├── COMPREHENSIVE_WORKFLOW_ANALYSIS_REPORT.md
    ├── UNIFIED_TOKEN_ANALYSIS_REPORT.md
    └── various other analysis reports
```

### Core Classes and Components

#### `LoggedWorkflowTester`
Main test runner class with comprehensive logging capabilities:
- **Session Management**: Unique session IDs and logging setup
- **HTTP Capture**: Complete request/response logging
- **Token Counting**: Precise tiktoken-based measurement
- **Step Tracking**: Detailed workflow step analysis

#### `WorkflowStep`
Data structure representing individual workflow steps:
- Request details (URL, method, headers, payload)
- Response details (status, timing, data)
- Token analysis (input, output, total)
- Success/failure tracking

#### `DetailedTestResult`
Complete test result container:
- Test metadata (ID, scenario, query, approach)
- Workflow steps collection
- Summary metrics
- Success/failure status

### Token Counting Implementation

The framework uses `tiktoken` for accurate token counting:

```python
class TokenCounter:
    def __init__(self):
        if TIKTOKEN_AVAILABLE:
            self.encoder = tiktoken.get_encoding("cl100k_base")  # GPT-4 compatible
    
    def count_tokens(self, text: str) -> int:
        if self.encoder:
            return len(self.encoder.encode(str(text)))
        else:
            return len(str(text)) // 4  # Fallback estimation
```

## Extending the Testing Framework

### Adding New Test Scenarios

1. **Edit the scenarios list** in `test_detailed_workflows_with_logging.py`:

```python
scenarios = [
    ("Shoe Shopping", "I want to buy some shoes"),
    ("Payment Processing", "process payment for $150"),
    # Add your new scenario here
    ("New Scenario", "your test query here"),
]
```

2. **Consider the query complexity** - ensure it's realistic and tests relevant functionality.

### Adding New Approaches

1. **Create a new test method** in the `LoggedWorkflowTester` class:

```python
def test_new_approach_workflow(self, test_id: str, scenario: str, query: str) -> DetailedTestResult:
    result = DetailedTestResult(
        test_id=test_id,
        scenario=scenario,
        query=query,
        approach="new_approach",
        start_time=datetime.now()
    )
    
    # Implement your workflow steps here
    # Each step should use self.create_step() and self.execute_request()
    
    return result
```

2. **Add to the test runner** in `run_comprehensive_tests()`:

```python
# Add after existing approach tests
try:
    new_result = self.test_new_approach_workflow(test_id + "_new", scenario, query)
    self.test_results.append(new_result)
    self.session_logger.info(f"✅ New Approach: {new_result.total_tokens} tokens, {new_result.total_response_time_ms}ms")
except Exception as e:
    self.session_logger.error(f"❌ New Approach failed: {e}")
```

### Customizing Logging

#### Log Levels
Adjust logging verbosity by modifying the logger setup:

```python
# For more detailed logging
self.session_logger.setLevel(logging.DEBUG)

# For less verbose logging
self.session_logger.setLevel(logging.WARNING)
```

#### Custom Log Formats
Modify the formatter in `setup_session_logger()`:

```python
formatter = logging.Formatter(
    '%(asctime)s | %(levelname)-8s | Custom: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
```

### Adding New Metrics

1. **Extend the `WorkflowStep` class** with new fields:

```python
@dataclass
class WorkflowStep:
    # Existing fields...
    custom_metric: Optional[float] = None
    additional_data: Dict[str, Any] = field(default_factory=dict)
```

2. **Capture metrics** during test execution:

```python
step.custom_metric = calculate_your_metric()
step.additional_data['custom_field'] = your_data
```

3. **Include in reporting** by updating the report generation methods.

### Integration with External Tools

#### Monitoring Systems
Use the JSON output for integration:

```python
import json

# Load test results
with open('test_logs/token_test_YYYYMMDD_HHMMSS_sessionid_results.json') as f:
    results = json.load(f)

# Send to monitoring system
for test_result in results['test_results']:
    send_to_monitoring_system(test_result)
```

#### CI/CD Integration
Create automated test execution:

```bash
#!/bin/bash
# ci_token_test.sh

# Run tests
./tests/token_comparison/run_all_token_tests.sh

# Parse results for CI
if [ $? -eq 0 ]; then
    echo "Token tests passed"
    exit 0
else
    echo "Token tests failed"
    exit 1
fi
```

## Troubleshooting

### Common Issues

#### API Not Accessible
```bash
# Error: Cannot connect to KPATH API
# Solution: Start the backend
./restart.sh
```

#### Missing Dependencies
```bash
# Error: tiktoken not available
# Solution: Install required packages
pip install tiktoken requests
```

#### Permission Denied
```bash
# Error: Permission denied
# Solution: Make scripts executable
chmod +x tests/token_comparison/run_all_token_tests.sh
```

### Debug Mode

Enable debug logging for troubleshooting:

1. **Edit the test file** to set debug level:
```python
self.session_logger.setLevel(logging.DEBUG)
```

2. **Run with debug output**:
```bash
python3 -u test_detailed_workflows_with_logging.py 2>&1 | tee debug.log
```

### Validating Results

#### Token Count Accuracy
Compare with OpenAI's official token counting:
```python
import tiktoken
encoder = tiktoken.get_encoding("cl100k_base")
tokens = len(encoder.encode("your text here"))
```

#### HTTP Request Verification
Check log files for complete request/response details:
```bash
grep -A 10 -B 5 "Request URL" tests/token_comparison/test_logs/*.log
```

## Best Practices

### Test Environment
- Ensure clean environment with no cached data
- Use consistent API endpoints and authentication
- Run tests during low-traffic periods for accurate timing

### Result Analysis
- Focus on relative comparisons rather than absolute values
- Run multiple test sessions to validate consistency
- Consider statistical significance for small differences

### Production Deployment
- Use test results to configure production settings
- Monitor actual production metrics vs. test predictions
- Regularly re-run tests as system evolves

## Integration with Development Workflow

### Pre-Deployment Testing
```bash
# Before deploying optimizations
./tests/token_comparison/run_all_token_tests.sh

# Compare results with baseline
# Deploy if results show improvement
```

### Performance Monitoring
Use JSON results to track trends over time:
```python
# trend_analysis.py
import json
import matplotlib.pyplot as plt

# Load multiple test results
# Generate trend charts
# Alert on performance regressions
```

### Cost Analysis
Calculate production cost implications:
```python
# cost_calculator.py
def calculate_monthly_cost(tokens_per_request, requests_per_month):
    # GPT-4o pricing: ~$10 per 1M tokens
    return (tokens_per_request * requests_per_month / 1_000_000) * 10
```

This comprehensive testing framework provides the foundation for data-driven optimization of your KPATH Enterprise deployment, ensuring maximum efficiency and cost-effectiveness in production environments.
