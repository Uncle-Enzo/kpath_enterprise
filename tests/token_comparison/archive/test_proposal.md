# Token Consumption Test Proposal for KPATH Enterprise

## Executive Summary

This document proposes a comprehensive approach to test and compare token consumption between two personal assistant (PA) tool selection methods:
1. **Approach 1**: PA calls KPATH basic search (agents_only mode) then manually selects a tool
2. **Approach 2**: PA calls KPATH tools search (tools_only mode) and uses the recommended tool directly

## Test Objectives

1. **Measure Total Token Consumption**: Count tokens for API responses and PA reasoning for both approaches
2. **Compare Efficiency**: Determine which approach uses fewer tokens overall
3. **Evaluate Success Rates**: Track tool selection success for each approach
4. **Analyze Performance**: Compare response times and reliability
5. **Identify Trade-offs**: Document pros/cons of each approach

## Current Implementation Status

### Available Test Infrastructure
- ✅ Token consumption test script exists: `test_token_consumption.py`
- ✅ TokenCounter class with tiktoken support
- ✅ KPathClient for API interaction
- ✅ AssistantSimulator for reasoning simulation
- ✅ Comprehensive reporting functionality

### Issues to Address
1. **API Authentication**: Current test uses API key in query parameter, but server expects JWT Bearer token
2. **Search Endpoint**: Need to verify correct endpoint routing (`/api/v1/search` vs `/api/v1/search/`)
3. **Response Format**: Need to update test to handle actual response formats for tools_only mode
4. **Tool Data Structure**: The test expects `tool_data` field but actual API may use `recommended_tool`

## Proposed Test Methodology

### 1. Fix Authentication
Update the KPathClient to use proper authentication:
```python
headers = {
    "Authorization": f"Bearer {self.api_key}",
    "Content-Type": "application/json"
}
```

### 2. Test Scenarios
Use diverse real-world queries that cover different service domains:
- Payment Processing
- Customer Communication
- Shipping Insurance 
- Data Management
- Authentication
- Risk Assessment
- Quote Generation
- Invoice Processing

### 3. Token Counting Strategy
- **API Response Tokens**: Full JSON response serialized and counted
- **Reasoning Tokens**: Simulated PA decision-making process
- **Total Tokens**: Sum of API response + reasoning tokens

### 4. Reasoning Simulation

#### Approach 1 (Basic Search + Manual Selection)
1. Parse service results
2. Analyze service descriptions
3. Consider service capabilities
4. Make service selection
5. Hypothetical additional API call for tool details
6. Select specific tool from service

#### Approach 2 (Direct Tool Search)
1. Parse tool results with recommendations
2. Evaluate recommended tools
3. Direct tool selection
4. No additional API calls needed

### 5. Metrics to Collect
- Total tokens per approach
- Response time (milliseconds)
- Success rate
- Selected tool accuracy
- Token efficiency ratio

## Test Execution Plan

### Phase 1: Environment Validation
1. Verify KPATH Enterprise is running
2. Test API connectivity
3. Validate authentication method
4. Check search endpoints

### Phase 2: Fix Test Script
1. Update authentication method
2. Correct response parsing
3. Enhance reasoning simulation
4. Add error handling

### Phase 3: Run Tests
1. Execute 10-20 diverse test scenarios
2. Collect metrics for both approaches
3. Handle failures gracefully
4. Generate comprehensive report

### Phase 4: Analysis
1. Calculate average token consumption
2. Identify token savings percentage
3. Analyze success rates
4. Document findings

## Expected Outcomes

### Hypothesis
Approach 2 (tools_only) should consume fewer tokens because:
- Single API call vs potential multiple calls
- Direct tool recommendations vs manual analysis
- Less reasoning overhead
- More focused response data

### Potential Results Format
```
KPATH ENTERPRISE TOKEN CONSUMPTION COMPARISON
=============================================
Test Date: 2025-06-18
Scenarios Tested: 10

SUMMARY STATISTICS:
- Approach 1 Average Tokens: 850
- Approach 2 Average Tokens: 425
- Token Savings: 50%
- Approach 1 Success Rate: 85%
- Approach 2 Success Rate: 95%

DETAILED RESULTS:
Scenario                 App1 Tokens  App2 Tokens  Difference  Winner
Payment Processing       823          412          +411        App2
Customer Notification    901          445          +456        App2
...
```

## Recommendations

1. **Fix Authentication**: Update test script to use Bearer token authentication
2. **Validate Endpoints**: Ensure correct API endpoint paths
3. **Install Dependencies**: Ensure tiktoken is installed for accurate token counting
4. **Run Baseline Test**: Execute a single scenario first to validate setup
5. **Full Test Suite**: Run complete test suite with diverse scenarios
6. **Document Results**: Create detailed report with findings and recommendations

## Next Steps

1. Review and approve this test proposal
2. Fix authentication and endpoint issues in test script
3. Run validation tests
4. Execute full test suite
5. Analyze results and create final report
6. Make recommendations for PA implementation strategy

## Appendix: Required Script Updates

Key changes needed in `test_token_consumption.py`:
1. Update KPathClient authentication
2. Fix response parsing for tools_only mode
3. Enhance reasoning simulation
4. Add comprehensive error handling
5. Update report generation
