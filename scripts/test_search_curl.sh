#!/bin/bash
# Quick test of KPATH search API using curl

echo "1. Getting auth token..."
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@kpath.local&password=admin123" \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

if [ -z "$TOKEN" ]; then
    echo "Failed to get auth token"
    exit 1
fi

echo "2. Token received: ${TOKEN:0:20}..."

echo "3. Testing search endpoint..."
curl -X POST http://localhost:8000/api/v1/search/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "customer data analytics",
    "limit": 5,
    "min_score": 0.1
  }' \
  | python3 -m json.tool

echo -e "\n4. Checking search status..."
curl -X GET http://localhost:8000/api/v1/search/search/status \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool
