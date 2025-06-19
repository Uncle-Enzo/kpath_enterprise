# KPATH Enterprise Tool Search User Guide

## Overview

KPATH Enterprise now includes advanced tool search capabilities that enable semantic discovery of tools and services with complete connectivity information. This guide covers all aspects of using the tool search functionality.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Authentication](#authentication)
3. [Search Modes](#search-modes)
4. [API Endpoints](#api-endpoints)
5. [Response Format](#response-format)
6. [Examples](#examples)
7. [Advanced Features](#advanced-features)
8. [Integration Guide](#integration-guide)

## Quick Start

### Basic Tool Search

Find tools using natural language queries:

```bash
# Find payment processing tools
curl "http://localhost:8000/api/v1/search?query=payment%20processing&search_mode=tools_only&api_key=YOUR_API_KEY"

# Find customer management tools
curl "http://localhost:8000/api/v1/search?query=customer&search_mode=tools_only&api_key=YOUR_API_KEY"
```

### Response Example

```json
{
  "query": "payment processing",
  "results": [
    {
      "service_id": 5,
      "score": 0.929,
      "rank": 1,
      "service": {
        "name": "PaymentGatewayAPI",
        "description": "Enterprise payment processing API",
        "integration_details": {
          "access_protocol": "https",
          "base_endpoint": "https://api.enterprise.com/payments/v3",
          "auth_method": "api_key",
          "request_content_type": "application/json"
        }
      },
      "recommended_tool": {
        "tool_name": "process_payment",
        "tool_description": "Process a payment transaction",
        "input_schema": {
          "type": "object",
          "required": ["amount", "currency", "payment_method"],
          "properties": {
            "amount": {"type": "number", "minimum": 0.01},
            "currency": {"enum": ["USD", "EUR", "GBP"]},
            "payment_method": {"type": "string"}
          }
        }
      }
    }
  ],
  "total_results": 3,
  "search_time_ms": 36,
  "search_mode": "tools_only"
}
```

## Authentication

KPATH Enterprise supports multiple authentication methods:

### API Key in Header (Recommended)
```bash
curl -H "X-API-Key: YOUR_API_KEY" "http://localhost:8000/api/v1/search?query=payment"
```

### API Key in Query Parameter
```bash
curl "http://localhost:8000/api/v1/search?query=payment&api_key=YOUR_API_KEY"
```

### Getting an API Key

Use the provided API key for testing:
```
kpe_fElyteRdsZVlypzp7qPx6yL12MoLPJ07
```

Or create a new one using the API key management endpoints.

## Search Modes

KPATH Enterprise offers multiple search modes for different use cases:

### 1. Tools Only (`tools_only`)
**Best for**: Agent integration, tool discovery
**Returns**: Tools with full connectivity information and recommendations

```bash
curl "http://localhost:8000/api/v1/search?query=email&search_mode=tools_only&api_key=YOUR_KEY"
```

### 2. Agents and Tools (`agents_and_tools`)
**Best for**: Comprehensive discovery
**Returns**: Mixed results with both services and tools, ranked by relevance

```bash
curl "http://localhost:8000/api/v1/search?query=customer&search_mode=agents_and_tools&api_key=YOUR_KEY"
```

### 3. Workflows (`workflows`)
**Best for**: Pattern discovery
**Returns**: Common invocation patterns and workflows

```bash
curl "http://localhost:8000/api/v1/search?query=payment&search_mode=workflows&api_key=YOUR_KEY"
```

### 4. Capabilities (`capabilities`)
**Best for**: Capability-based search
**Returns**: Services and tools grouped by capabilities

```bash
curl "http://localhost:8000/api/v1/search?query=authentication&search_mode=capabilities&api_key=YOUR_KEY"
```

## API Endpoints

### Main Search Endpoint

**GET** `/api/v1/search`

**Parameters:**
- `query` (required): Search query string
- `search_mode` (optional): Search mode (default: "agents_only")
- `limit` (optional): Maximum results (default: 10, max: 100)
- `min_score` (optional): Minimum relevance score (0.0-1.0)
- `api_key` (optional): API key for authentication

**POST** `/api/v1/search`

**Request Body:**
```json
{
  "query": "payment processing",
  "search_mode": "tools_only",
  "limit": 5,
  "min_score": 0.7,
  "include_orchestration": true
}
```

### Additional Endpoints

- **GET** `/api/v1/search/similar/{service_id}` - Find similar services
- **POST** `/api/v1/search/feedback` - Submit search feedback
- **GET** `/api/v1/search/feedback/stats` - Get feedback statistics

## Response Format

### Tool Search Response Structure

```json
{
  "query": "search query",
  "results": [
    {
      "service_id": 5,
      "score": 0.929,
      "rank": 1,
      "service": {
        "id": 5,
        "name": "ServiceName",
        "description": "Service description",
        "endpoint": "https://api.example.com",
        "status": "active",
        "integration_details": {
          "access_protocol": "https",
          "base_endpoint": "https://api.example.com",
          "auth_method": "api_key",
          "request_content_type": "application/json",
          "response_content_type": "application/json"
        },
        "agent_capabilities": {
          "response_format": "json",
          "supports_streaming": false,
          "max_concurrent_requests": 10
        }
      },
      "recommended_tool": {
        "tool_id": 3,
        "tool_name": "tool_name",
        "tool_description": "Tool description",
        "input_schema": {
          "type": "object",
          "required": ["param1"],
          "properties": {
            "param1": {"type": "string"}
          }
        },
        "output_schema": {
          "type": "object",
          "properties": {
            "result": {"type": "string"}
          }
        },
        "example_calls": {
          "basic_example": {
            "param1": "example_value"
          }
        }
      }
    }
  ],
  "total_results": 3,
  "search_time_ms": 36,
  "search_mode": "tools_only"
}
```

## Examples

### 1. Payment Processing Tools

```bash
curl "http://localhost:8000/api/v1/search?query=payment%20processing&search_mode=tools_only&api_key=kpe_fElyteRdsZVlypzp7qPx6yL12MoLPJ07&limit=3"
```

**Expected Results:**
- PaymentGatewayAPI → process_payment tool
- Complete payment schemas and examples
- Authentication and endpoint information

### 2. Customer Management

```bash
curl "http://localhost:8000/api/v1/search?query=customer&search_mode=tools_only&api_key=kpe_fElyteRdsZVlypzp7qPx6yL12MoLPJ07"
```

**Expected Results:**
- CustomerDataAPI → get_customer_profile tool
- Customer search and management tools
- Profile and preferences schemas

### 3. Email and Communication

```bash
curl "http://localhost:8000/api/v1/search?query=email&search_mode=tools_only&api_key=kpe_fElyteRdsZVlypzp7qPx6yL12MoLPJ07"
```

**Expected Results:**
- Email sending tools
- Communication service integrations
- Message formatting and delivery options

### 4. Advanced POST Request

```bash
curl -X POST "http://localhost:8000/api/v1/search" \
     -H "X-API-Key: kpe_fElyteRdsZVlypzp7qPx6yL12MoLPJ07" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "inventory management",
       "search_mode": "tools_only",
       "limit": 5,
       "min_score": 0.5,
       "include_orchestration": true
     }'
```

## Advanced Features

### 1. Relevance Scoring

Tool search uses semantic similarity scoring:
- **0.9-1.0**: Excellent match (highly relevant)
- **0.7-0.9**: Good match (relevant)
- **0.5-0.7**: Fair match (somewhat relevant)
- **0.0-0.5**: Poor match (low relevance)

### 2. Tool Recommendations

Each result includes intelligent tool recommendations with:
- **Tool Metadata**: Names, descriptions, versions
- **Input/Output Schemas**: Complete JSON schemas for validation
- **Example Calls**: Ready-to-use examples with different parameters
- **Recommendation Reasoning**: Explanation of why the tool was recommended

### 3. Connectivity Information

Complete integration details for each service:
- **Endpoints**: Base URLs and specific endpoints
- **Authentication**: Methods, headers, and configuration
- **Request/Response Formats**: Content types and data structures
- **Rate Limiting**: Request limits and throttling information
- **Circuit Breaker**: Fault tolerance configuration

### 4. Performance Monitoring

Track search performance:
- **Response Times**: Typical range 5-50ms
- **Success Rates**: Query success and failure rates
- **Usage Analytics**: Popular queries and tools
- **Feedback System**: User interaction tracking

## Integration Guide

### For Agent Developers

1. **Use tools_only mode** for the most relevant tool discoveries
2. **Parse input_schema** to understand required parameters
3. **Use example_calls** as templates for tool invocation
4. **Check integration_details** for connectivity requirements
5. **Implement error handling** based on service capabilities

### For Application Developers

1. **Implement search UI** using the search API
2. **Cache frequent searches** to improve performance
3. **Use feedback endpoints** to improve search quality
4. **Monitor search analytics** for usage patterns
5. **Handle authentication** securely with API keys

### For System Integrators

1. **Map existing tools** to KPATH search results
2. **Use connectivity information** for integration planning
3. **Leverage workflow discovery** for process automation
4. **Implement capability-based routing** for service selection
5. **Monitor service health** through the integration details

## Troubleshooting

### Common Issues

1. **404 Not Found**
   - Check URL path: Use `/api/v1/search` (not `/api/v1/search/search`)
   - Verify API key is valid and active

2. **401 Unauthorized**
   - Ensure API key is provided via header or query parameter
   - Check API key format and permissions

3. **500 Internal Server Error**
   - Check server logs for specific error details
   - Verify database connectivity
   - Ensure search index is built

### Performance Tips

1. **Use specific queries** for better results
2. **Set appropriate min_score** to filter low-quality results
3. **Limit results** to reasonable numbers (10-20 for UI, 3-5 for agents)
4. **Cache results** for frequently used queries
5. **Use batch requests** when searching for multiple terms

## Token Usage Testing and Analysis

KPATH Enterprise includes a comprehensive token usage testing framework to help optimize performance and costs. See the **[Token Testing Guide](token-testing-guide.md)** for complete documentation.

### Quick Testing

Run comprehensive token analysis with detailed logging:

```bash
cd /Users/james/claude_development/kpath_enterprise
./tests/token_comparison/run_all_token_tests.sh
```

### What Gets Tested
- **4 Different Approaches**: Traditional, Tools Full, Tools Compact, Tools Minimal
- **5 Realistic Scenarios**: Shoe shopping, payment processing, customer notifications, etc.
- **Complete Analysis**: HTTP requests, responses, token usage, and performance metrics

### Output Files
- **Session Logs**: `tests/token_comparison/test_logs/*.log` - Detailed workflow documentation
- **JSON Results**: `tests/token_comparison/test_logs/*_results.json` - Structured data for analysis
- **Console Output**: Real-time progress and summary statistics

### Key Results
Based on comprehensive testing:
- **Tools Minimal**: 1,905 tokens avg, 243ms response time ⭐ **RECOMMENDED**
- **Tools Compact**: 3,142 tokens avg, 243ms response time
- **Traditional**: 3,324 tokens avg, 760ms response time
- **Tools Full**: 8,794 tokens avg, 271ms response time

**Breakthrough**: Tools Minimal uses **42.7% fewer tokens** than traditional approach while being **3x faster**.

### For More Details
See **[Token Testing Guide](token-testing-guide.md)** for:
- Complete testing framework documentation
- How to extend and customize tests
- Detailed result interpretation
- Integration with production workflows
- Cost analysis and optimization strategies

## Support and Resources

- **API Documentation**: http://localhost:8000/docs
- **System Health**: http://localhost:8000/health
- **Project Status**: `/docs/project_status.txt`
- **Token Testing Guide**: `/docs/token-testing-guide.md`
- **Frontend Interface**: http://localhost:5173

For technical support or feature requests, refer to the project documentation or contact the development team.
