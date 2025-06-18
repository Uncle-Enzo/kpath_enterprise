# KPATH Enterprise Token Consumption Test Report

**Generated Automatically**

## Report Information
- **Generated**: 2025-06-18 13:12:50
- **Test Duration**: 6.2 seconds
- **Token Counting Method**: tiktoken (GPT-4)
- **Test Environment**: http://localhost:8000

## System Health Check
- API Accessible: ✅
- API Version: 1.0.0

## Executive Summary

### Key Findings
- **Tests Run**: 8
- **Successful Tests**: 8
- **Average Tokens (Approach 1)**: 1582
- **Average Tokens (Approach 2)**: 4573
- **Token Difference**: +2991 (+189.1%)
- **Average Response Time (Approach 1)**: 185ms
- **Average Response Time (Approach 2)**: 73ms

### Conclusion
Approach 2 uses 189.1% more tokens but provides:
- Single API call (vs 2 calls)
- 60% faster response time
- Simpler implementation logic

## Detailed Test Results

| Scenario | App1 Tokens | App2 Tokens | Difference | App1 Time | App2 Time |
|----------|-------------|-------------|------------|-----------|-----------|
| Payment Processing | 1542 | 4109 | +2567 (+166.5%) | 1120ms | 79ms |
| Customer Notification | 1670 | 3941 | +2271 (+136.0%) | 59ms | 79ms |
| Shipping Insurance | 1661 | 6344 | +4683 (+281.9%) | 50ms | 57ms |
| Customer Data Lookup | 1520 | 3982 | +2462 (+162.0%) | 49ms | 109ms |
| Invoice Generation | 1524 | 3884 | +2360 (+154.9%) | 51ms | 66ms |
| Risk Assessment | 1657 | 6113 | +4456 (+268.9%) | 50ms | 62ms |
| Authentication | 1567 | 4311 | +2744 (+175.1%) | 50ms | 72ms |
| Fraud Detection | 1512 | 3898 | +2386 (+157.8%) | 49ms | 64ms |

## Token Usage Breakdown

### Approach 1 (Traditional)
- Service Search API: 1320 tokens
- Tool Query API (est): 200 tokens
- PA Reasoning: 62 tokens
- **Total Average**: 1582 tokens

### Approach 2 (Direct Tool Search)
- Tool Search API: 4517 tokens
- PA Reasoning: 56 tokens
- **Total Average**: 4573 tokens

## Recommendations

### ✅ Use Direct Tool Search (Approach 2) for:
- Production personal assistant systems
- Interactive applications requiring fast responses
- Systems prioritizing simplicity and reliability

### ⚠️ Consider Traditional Search (Approach 1) for:
- Extremely token-constrained environments
- Service discovery without immediate tool selection
- Legacy system compatibility

## Test Artifacts

- Test Script: `generate_report.py`
- Raw Results: Embedded in this report
- Report Generated: 2025-06-18 13:12:50