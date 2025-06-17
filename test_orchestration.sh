#!/bin/bash

echo "🔬 Testing Agent Orchestration Enhancement"
echo "=" | tr -c '\n' '=' | head -c 50; echo

echo
echo "📋 Test 1: Regular Search (Backward Compatibility)"
echo "-" | tr -c '\n' '-' | head -c 45; echo

echo "Testing regular search without orchestration..."
curl -s -X GET \
  "http://localhost:8000/api/v1/search/search?query=customer%20data%20management&limit=1&include_orchestration=false" \
  -H "X-API-Key: kpe_TestKey123456789012345678901234" \
  | python3 -m json.tool | head -30

echo
echo "🤖 Test 2: Orchestration-Enhanced Search"  
echo "-" | tr -c '\n' '-' | head -c 40; echo

echo "Testing orchestration-enhanced search..."
curl -s -X GET \
  "http://localhost:8000/api/v1/search/search?query=customer%20data%20management&limit=1&include_orchestration=true" \
  -H "X-API-Key: kpe_TestKey123456789012345678901234" \
  | python3 -c "
import json, sys
data = json.load(sys.stdin)
if 'results' in data and data['results']:
    service = data['results'][0]['service']
    print(f'Service: {service.get(\"name\", \"Unknown\")}')
    print(f'Agent Protocol: {service.get(\"agent_protocol\", \"None\")}')
    print(f'Auth Type: {service.get(\"auth_type\", \"None\")}')
    tools = service.get('tools', [])
    print(f'Tools available: {len(tools)}')
    if tools:
        print(f'First tool: {tools[0].get(\"tool_name\", \"Unknown\")}')
        print(f'Has input schema: {\"input_schema\" in tools[0]}')
        print(f'Has output schema: {\"output_schema\" in tools[0]}')
        print(f'Has examples: {\"example_calls\" in tools[0]}')
    orchestration = service.get('orchestration_summary', {})
    print(f'Total tools: {orchestration.get(\"total_tools\", 0)}')
    print(f'Supports orchestration: {orchestration.get(\"supports_orchestration\", False)}')
    print('✅ Orchestration data included!')
else:
    print('❌ No results or error')
    print(json.dumps(data, indent=2)[:500])
"

echo
echo "📨 Test 3: POST Method with Orchestration"
echo "-" | tr -c '\n' '-' | head -c 35; echo

echo "Testing POST method with orchestration..."
curl -s -X POST \
  "http://localhost:8000/api/v1/search/search" \
  -H "X-API-Key: kpe_TestKey123456789012345678901234" \
  -H "Content-Type: application/json" \
  -d '{"query": "payment processing", "limit": 1, "include_orchestration": true}' \
  | python3 -c "
import json, sys
data = json.load(sys.stdin)
if 'results' in data and data['results']:
    service = data['results'][0]['service']
    tools = service.get('tools', [])
    print(f'Service: {service.get(\"name\", \"Unknown\")}')
    print(f'Tools: {len(tools)}')
    if tools:
        for i, tool in enumerate(tools[:2]):
            print(f'  Tool {i+1}: {tool.get(\"tool_name\", \"Unknown\")}')
            print(f'    Description: {tool.get(\"description\", \"No description\")}')
    print('✅ POST orchestration working!')
else:
    print('❌ No results or error')
    print(json.dumps(data, indent=2)[:500])
"

echo
echo "🎯 Testing Complete!"
echo "=" | tr -c '\n' '=' | head -c 50; echo
