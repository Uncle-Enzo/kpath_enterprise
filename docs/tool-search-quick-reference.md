# KPATH Enterprise Tool Search - Quick Reference

## 🚀 Quick Start Commands

```bash
# Test API Key
API_KEY="kpe_fElyteRdsZVlypzp7qPx6yL12MoLPJ07"

# Find payment tools
curl "http://localhost:8000/api/v1/search?query=payment&search_mode=tools_only&api_key=$API_KEY"

# Find customer tools  
curl "http://localhost:8000/api/v1/search?query=customer&search_mode=tools_only&api_key=$API_KEY"

# Find email tools
curl "http://localhost:8000/api/v1/search?query=email&search_mode=tools_only&api_key=$API_KEY"
```

## 📊 Search Modes

| Mode | Description | Best For |
|------|-------------|----------|
| `tools_only` | Tools with connectivity info | Agent integration |
| `agents_and_tools` | Mixed results | Comprehensive discovery |
| `workflows` | Invocation patterns | Process automation |
| `capabilities` | Capability-based | Feature discovery |

## 🔑 Authentication

```bash
# Header (recommended)
curl -H "X-API-Key: $API_KEY" "http://localhost:8000/api/v1/search?query=payment"

# Query parameter
curl "http://localhost:8000/api/v1/search?query=payment&api_key=$API_KEY"
```

## 📝 POST Request Example

```bash
curl -X POST "http://localhost:8000/api/v1/search" \
     -H "X-API-Key: $API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "payment",
       "search_mode": "tools_only",
       "limit": 5,
       "min_score": 0.7
     }'
```

## 🎯 Response Structure

```json
{
  "query": "payment",
  "results": [
    {
      "service_id": 5,
      "score": 0.929,
      "service": {
        "name": "PaymentGatewayAPI",
        "integration_details": {
          "base_endpoint": "https://api.enterprise.com/payments/v3",
          "auth_method": "api_key"
        }
      },
      "recommended_tool": {
        "tool_name": "process_payment",
        "input_schema": {...},
        "example_calls": {...}
      }
    }
  ],
  "search_time_ms": 36
}
```

## 🔗 Key Endpoints

- **Main Search**: `GET /api/v1/search`
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Frontend**: http://localhost:5173

## ⚡ Performance

- **Response Time**: 5-50ms typical
- **Relevance**: 91-93% for good matches
- **Available Tools**: 6 across 4 services
- **Search Modes**: 4 different modes

## 🛠️ Available Tools

1. **process_payment** - PaymentGatewayAPI
2. **send_email** - PaymentGatewayAPI  
3. **get_customer_profile** - CustomerDataAPI
4. **search_customers** - CustomerDataAPI
5. **check_inventory** - InventoryManagementAPI
6. **validate_token** - AuthenticationAPI

## 📚 Documentation

- **Complete Guide**: `/docs/tool-search-user-guide.md`
- **Project Status**: `/docs/project_status.txt`
- **User Guide Info**: `/USER_GUIDE_UPDATE_INFO.txt`

## 🔧 Status: FULLY OPERATIONAL ✅
