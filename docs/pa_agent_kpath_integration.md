# PA Agent Integration with KPATH - Correct Implementation

## How It Should Work

The PA Agent should use KPATH search results to dynamically construct API calls to services and tools. Here's the correct flow:

### 1. Search KPATH with Appropriate Flags

For tools mode:
```json
{
    "query": "user query here",
    "search_mode": "tools_only",
    "response_mode": "compact",  // or "minimal" for efficiency
    "include_orchestration": true,  // This is key!
    "limit": 5
}
```

### 2. Extract Service Integration Details

From the KPATH response, the PA Agent should extract:
- `service.integration_details.base_endpoint` - The base URL for the service
- `service.integration_details.auth_method` - How to authenticate
- `recommended_tool.tool_name` - Which tool to call
- `tool.endpoint_pattern` - The specific endpoint pattern for the tool

### 3. Construct the Full URL

```python
base_endpoint = service['integration_details']['base_endpoint']  # e.g., "http://localhost:8000/agents/shoes"
tool_endpoint = tool['endpoint_pattern']  # e.g., "/search"
full_url = base_endpoint + tool_endpoint  # "http://localhost:8000/agents/shoes/search"
```

### 4. Current Issues

1. **Integration Details Missing in Compact Mode**: When using `response_mode="compact"` or `"minimal"`, the integration details are not included unless `include_orchestration=true` is set.

2. **Tool Endpoint Patterns**: The tools table now has an `endpoint_pattern` field, but it's not being returned in the search results.

3. **Test Hardcoding**: The current tests hardcode the endpoint mappings instead of using the data from KPATH.

### 5. Recommended Fix

The PA Agent workflow test should:
1. Always set `include_orchestration=true` when searching KPATH
2. Extract the base endpoint from integration_details
3. Use the tool's endpoint_pattern (once it's included in responses)
4. Construct URLs dynamically instead of hardcoding

### 6. Database Updates Made

- Added `endpoint_pattern` column to tools table
- Updated ShoesAgent tools with their endpoint patterns:
  - product_search: /search
  - product_availability: /availability/{product_id}
  - store_location_search: /stores
  - shoe_buying_guide: /guide
  - delivery_tracker: /track

### 7. Next Steps

1. Update the search service to include endpoint_pattern in tool responses
2. Update the PA Agent test to use dynamic URL construction
3. Ensure all agents have proper integration_details in the database
4. Document the expected KPATH response format for PA Agent integration
