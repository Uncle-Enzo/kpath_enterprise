# API Key Usage Examples for KPath Enterprise

## Authentication Methods

KPath Enterprise supports two authentication methods:

1. **JWT Token** - For user sessions and web applications
2. **API Key** - For server-to-server communication and integrations

## Using API Keys

### Creating an API Key

First, authenticate with your username/password to get a JWT token, then create an API key:

```bash
# 1. Login to get JWT token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'

# 2. Create API key (using JWT token from step 1)
curl -X POST http://localhost:8000/api/v1/api-keys \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Production Server",
    "permissions": {"search": true},
    "rate_limit": 1000
  }'
```

### Using API Keys for Search

Once you have an API key, you can use it to authenticate requests:

#### GET Request (Recommended for simple searches)

```bash
curl -X GET "http://localhost:8000/api/v1/search?query=customer%20data&limit=10" \
  -H "X-API-Key: kpe_your_api_key_here"
```

#### POST Request (For complex searches with filters)

```bash
curl -X POST http://localhost:8000/api/v1/search \
  -H "X-API-Key: kpe_your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "customer data management",
    "limit": 10,
    "min_score": 0.5,
    "domains": ["sales", "marketing"],
    "capabilities": ["data storage"]
  }'
```

## Programming Language Examples

### Python

```python
import requests

# Your API key
API_KEY = "kpe_your_api_key_here"
BASE_URL = "http://localhost:8000/api/v1"

# Search using API key
response = requests.get(
    f"{BASE_URL}/search",
    headers={"X-API-Key": API_KEY},
    params={
        "query": "customer data management",
        "limit": 10
    }
)

if response.status_code == 200:
    data = response.json()
    print(f"Found {data['total_results']} results")
    for result in data['results']:
        print(f"- {result['service']['name']} (score: {result['score']:.2f})")
else:
    print(f"Error: {response.status_code}")
```

### JavaScript (Node.js)

```javascript
const axios = require('axios');

const API_KEY = 'kpe_your_api_key_here';
const BASE_URL = 'http://localhost:8000/api/v1';

async function search(query) {
    try {
        const response = await axios.get(`${BASE_URL}/search`, {
            headers: {
                'X-API-Key': API_KEY
            },
            params: {
                query: query,
                limit: 10
            }
        });
        
        console.log(`Found ${response.data.total_results} results`);
        response.data.results.forEach(result => {
            console.log(`- ${result.service.name} (score: ${result.score.toFixed(2)})`);
        });
    } catch (error) {
        console.error('Search failed:', error.response?.status);
    }
}

search('customer data management');
```

### JavaScript (Browser/Fetch)

```javascript
const API_KEY = 'kpe_your_api_key_here';
const BASE_URL = 'http://localhost:8000/api/v1';

async function search(query) {
    const params = new URLSearchParams({
        query: query,
        limit: 10
    });
    
    try {
        const response = await fetch(`${BASE_URL}/search?${params}`, {
            headers: {
                'X-API-Key': API_KEY
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log(`Found ${data.total_results} results`);
        } else {
            console.error('Search failed:', response.status);
        }
    } catch (error) {
        console.error('Request failed:', error);
    }
}
```

## Rate Limiting

API keys have rate limits to prevent abuse. The default is 1000 requests per hour.

### Rate Limit Headers

Every response includes rate limit information:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
```

### Handling Rate Limits

```python
response = requests.get(url, headers={"X-API-Key": API_KEY})

if response.status_code == 429:
    print("Rate limit exceeded")
    print(f"Limit: {response.headers.get('X-RateLimit-Limit')}")
    print(f"Remaining: {response.headers.get('X-RateLimit-Remaining')}")
```

## API Key Management

### List Your API Keys

```bash
curl -X GET http://localhost:8000/api/v1/api-keys \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Revoke an API Key

```bash
curl -X DELETE http://localhost:8000/api/v1/api-keys/{key_id} \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Get API Key Usage Statistics

```bash
curl -X GET http://localhost:8000/api/v1/api-keys/{key_id}/usage?days=7 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Security Best Practices

1. **Never expose API keys in client-side code** - API keys should only be used in server-side applications
2. **Store keys securely** - Use environment variables or secure key management systems
3. **Rotate keys regularly** - Create new keys and revoke old ones periodically
4. **Use appropriate rate limits** - Set rate limits based on your actual needs
5. **Monitor usage** - Regularly check API key usage for unusual patterns

## Environment Variables

```bash
# .env file
KPATH_API_KEY=kpe_your_api_key_here
KPATH_BASE_URL=http://localhost:8000

# Python usage
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('KPATH_API_KEY')
```

## Error Handling

Common error responses:

- `401 Unauthorized` - Invalid or missing API key
- `403 Forbidden` - API key lacks required permissions
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error (retry with backoff)

## Support

For issues or questions about API keys, please contact support or check the project documentation.