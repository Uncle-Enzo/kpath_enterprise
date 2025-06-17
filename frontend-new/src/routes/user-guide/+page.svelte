<script lang="ts">
  import { onMount } from 'svelte';
  import Fa from 'svelte-fa';
  import { 
    faBook, 
    faSearch, 
    faCode, 
    faExternalLinkAlt, 
    faInfoCircle,
    faServer,
    faRobot,
    faCog,
    faKey,
    faCheckCircle,
    faTimesCircle,
    faCopy,
    faPlay,
    faChartBar,
    faDownload,
    faFilePdf,
    faSpinner
  } from '@fortawesome/free-solid-svg-icons';
  
  let copySuccess = '';
  let isPdfGenerating = false;
  
  function copyToClipboard(text: string, element: string) {
    navigator.clipboard.writeText(text).then(() => {
      copySuccess = element;
      setTimeout(() => copySuccess = '', 2000);
    });
  }

  async function generatePDF() {
    isPdfGenerating = true;
    
    try {
      // Import the PDF generator utility
      const { generateUserGuidePDF } = await import('$lib/utils/pdfGenerator');
      
      // Generate the PDF
      const pdf = await generateUserGuidePDF();
      
      // Save the PDF
      pdf.save('KPATH-Enterprise-User-Guide.pdf');
      
    } catch (error) {
      console.error('Error generating PDF:', error);
      alert('Error generating PDF. Please try again or contact support.');
    } finally {
      isPdfGenerating = false;
    }
  }

  // Code examples as variables to avoid parsing issues
  const postCurlExample = `curl -X POST http://localhost:8000/api/v1/search \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \\
  -d '{
    "query": "customer data management",
    "limit": 10,
    "min_score": 0.0,
    "domains": [],
    "capabilities": []
  }'`;

  const getCurlExample = `curl -X GET "http://localhost:8000/api/v1/search?query=customer%20data&limit=10" \\
  -H "X-API-Key: YOUR_API_KEY"`;

  const getCurlQueryExample = `curl -X GET "http://localhost:8000/api/v1/search?query=customer%20data&limit=10&api_key=YOUR_API_KEY"`;

  // Agent Orchestration Examples (NEW - June 17, 2025)
  const getCurlOrchestrationExample = `curl -X GET "http://localhost:8000/api/v1/search/search?query=customer%20data&limit=5&include_orchestration=true" \\
  -H "X-API-Key: YOUR_API_KEY"`;

  const postOrchestrationExample = `curl -X POST http://localhost:8000/api/v1/search/search \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: YOUR_API_KEY" \\
  -d '{
    "query": "customer data management",
    "limit": 5,
    "include_orchestration": true
  }'`;

  const responseExample = {
    "query": "payment processing",
    "results": [
      {
        "service_id": 5,
        "score": 0.530907168072185,
        "rank": 1,
        "service": {
          "id": 5,
          "name": "PaymentGatewayAPI",
          "description": "Enterprise payment processing API supporting multiple payment methods, currencies, and compliance standards",
          "endpoint": "https://api.enterprise.com/payments/v3",
          "version": "3.1.0",
          "status": "active",
          "tool_type": "API",
          "visibility": "internal",
          "interaction_modes": ["REST"],
          "capabilities": [
            "Process payments via credit card, ACH, wire transfer",
            "Process refunds and chargebacks",
            "Check payment status and history",
            "Generate payment reports and reconciliation"
          ],
          "domains": ["Finance", "E-commerce", "Compliance"],
          "tags": [],
          "agent_protocol": "kpath-v1",
          "auth_type": "api_key",
          "auth_config": {
            "encryption": "required",
            "header_name": "X-API-Key",
            "validation_endpoint": "/api/validate-key"
          },
          "tool_recommendations": {
            "use_cases": ["payment_processing", "financial_transactions"],
            "primary_tools": ["process_payment"]
          },
          "agent_capabilities": {
            "compliance": ["PCI-DSS", "SOX"],
            "response_format": "json",
            "supports_streaming": false,
            "supported_currencies": ["USD", "EUR", "GBP"],
            "max_concurrent_requests": 5
          },
          "communication_patterns": {
            "idempotency": "required",
            "retry_policy": {
              "backoff_ms": 2000,
              "max_attempts": 2
            },
            "request_style": "REST",
            "async_supported": true,
            "batch_operations": true
          },
          "orchestration_metadata": {
            "discovery_tags": ["payment", "transaction", "finance"],
            "security_level": "high",
            "business_domain": "Financial Services",
            "sla_response_time_ms": 2000,
            "integration_complexity": "high"
          },
          "default_timeout_ms": 30000,
          "integration_details": {
            "access_protocol": "https",
            "base_endpoint": "https://api.enterprise.com/payments/v3",
            "auth_method": "None",
            "rate_limit_requests": null,
            "rate_limit_window_seconds": null,
            "max_concurrent_requests": null,
            "health_check_endpoint": null
          }
        },
        "distance": null
      }
    ],
    "total_results": 1,
    "search_time_ms": 1028.0,
    "user_id": 3,
    "timestamp": "2025-06-16T10:32:28.532913"
  };

  // Orchestration-Enhanced Response Example (NEW)
  const orchestrationResponseExample = {
    "query": "customer data management",
    "results": [
      {
        "service_id": 4,
        "score": 0.8234,
        "rank": 1,
        "service": {
          "id": 4,
          "name": "CustomerDataAPI",
          "description": "Core API for accessing and managing customer master data, profiles, and preferences",
          "agent_protocol": "kpath-v1",
          "auth_type": "bearer_token",
          "tools": [
            {
              "tool_name": "get_customer_profile",
              "description": "Retrieve complete customer profile and preferences data",
              "input_schema": {
                "type": "object",
                "required": ["customer_id"],
                "properties": {
                  "customer_id": {
                    "type": "string",
                    "description": "Unique customer identifier"
                  },
                  "include_preferences": {
                    "type": "boolean",
                    "default": true
                  }
                }
              },
              "output_schema": {
                "type": "object",
                "properties": {
                  "customer_id": {"type": "string"},
                  "name": {"type": "string"},
                  "email": {"type": "string"},
                  "preferences": {"type": "object"}
                }
              },
              "example_calls": {
                "basic_lookup": {
                  "customer_id": "CUST-12345"
                },
                "with_preferences": {
                  "customer_id": "CUST-12345",
                  "include_preferences": true
                }
              },
              "tool_version": "1.0.0",
              "is_active": true
            }
          ],
          "orchestration_summary": {
            "total_tools": 2,
            "protocol_version": "kpath-v1",
            "authentication_required": true,
            "supports_orchestration": true,
            "tool_count_by_type": {
              "data_retrieval": 2
            }
          }
        }
      }
    ],
    "total_results": 1,
    "search_time_ms": 234.5,
    "user_id": 3,
    "timestamp": "2025-06-17T11:45:00.000Z"
  };
</script>

<div class="max-w-4xl mx-auto space-y-8" id="user-guide-content">
  <div class="text-center">
    <div class="flex items-center justify-center mb-4">
      <Fa icon={faBook} class="text-4xl text-primary-600 mr-3" />
      <h1 class="text-3xl font-bold text-gray-900">User Guide</h1>
    </div>
    <p class="text-lg text-gray-600 mb-6">
      Complete guide to using KPATH Enterprise for semantic service discovery
    </p>
    
    <!-- PDF Download Section -->
    <div class="bg-gradient-to-r from-green-50 to-blue-50 border border-green-200 rounded-lg p-4 mb-6">
      <div class="flex items-center justify-center space-x-4">
        <div class="flex items-center">
          <Fa icon={faFilePdf} class="text-red-600 text-xl mr-2" />
          <span class="font-medium text-gray-800">Download Updated User Guide (with API Keys & Enhanced Responses)</span>
        </div>
        <button
          on:click={generatePDF}
          disabled={isPdfGenerating}
          class="btn btn-primary btn-sm flex items-center"
        >
          {#if isPdfGenerating}
            <Fa icon={faSpinner} class="mr-2 animate-spin" />
            Generating...
          {:else}
            <Fa icon={faDownload} class="mr-2" />
            Download PDF
          {/if}
        </button>
      </div>
      <div class="mt-2 space-y-1">
        <p class="text-sm text-green-700">
          ✅ <strong>Updated June 17, 2025:</strong> Now includes complete agent orchestration with tool schemas, examples, and invocation metadata
        </p>
        <p class="text-sm text-blue-700">
          🎉 <strong>NEW:</strong> Use <code class="bg-blue-100 px-2 py-1 rounded text-xs">include_orchestration=true</code> to receive complete tool definitions for agent-to-agent communication
        </p>
      </div>
    </div>
  </div>

  <!-- Table of Contents -->
  <div class="card">
    <h2 class="text-xl font-semibold mb-4 flex items-center">
      <Fa icon={faInfoCircle} class="mr-2 text-primary-600" />
      Table of Contents
    </h2>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
      <a href="#overview" class="text-primary-600 hover:text-primary-800">1. System Overview</a>
      <a href="#search-ui" class="text-primary-600 hover:text-primary-800">2. Search via Web Interface</a>
      <a href="#search-api" class="text-primary-600 hover:text-primary-800">3. Search via API</a>
      <a href="#parameters" class="text-primary-600 hover:text-primary-800">4. Search Parameters</a>
      <a href="#response-format" class="text-primary-600 hover:text-primary-800">5. Response Format</a>
      <a href="#examples" class="text-primary-600 hover:text-primary-800">6. Example Queries</a>
      <a href="#authentication" class="text-primary-600 hover:text-primary-800">7. Authentication & API Keys</a>
      <a href="#orchestration" class="text-primary-600 hover:text-primary-800">8. Agent Orchestration</a>
      <a href="#integrations" class="text-primary-600 hover:text-primary-800">9. ESB Integration Guides</a>
    </div>
  </div>

  <!-- System Overview -->
  <div id="overview" class="card">
    <h2 class="text-2xl font-semibold mb-4 flex items-center">
      <Fa icon={faServer} class="mr-2 text-primary-600" />
      1. System Overview
    </h2>
    <div class="space-y-4">
      <p class="text-gray-700">
        KPATH Enterprise is a semantic search service that helps AI assistants and agents discover internal services, tools, and capabilities using natural language queries. The system understands intent and meaning, not just keywords.
      </p>
      
      <div class="bg-blue-50 p-4 rounded-lg">
        <h3 class="font-semibold text-blue-900 mb-2">Key Features:</h3>
        <ul class="list-disc list-inside text-blue-800 space-y-1">
          <li><strong>Semantic Understanding:</strong> Finds services based on meaning and context</li>
          <li><strong>Natural Language:</strong> Use conversational queries like "send email notifications"</li>
          <li><strong>Agent Orchestration:</strong> Complete tool definitions for agent-to-agent communication</li>
          <li><strong>Real-time Analytics:</strong> Performance monitoring and usage tracking</li>
          <li><strong>Flexible Access:</strong> Web interface, REST API, and API key authentication</li>
        </ul>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
        <div class="text-center p-4 bg-gray-50 rounded-lg">
          <Fa icon={faServer} class="text-2xl text-green-600 mb-2" />
          <h4 class="font-semibold">33 Services</h4>
          <p class="text-sm text-gray-600">Available for discovery</p>
        </div>
        <div class="text-center p-4 bg-gray-50 rounded-lg">
          <Fa icon={faRobot} class="text-2xl text-blue-600 mb-2" />
          <h4 class="font-semibold">5 Tools</h4>
          <p class="text-sm text-gray-600">With orchestration schemas</p>
        </div>
        <div class="text-center p-4 bg-gray-50 rounded-lg">
          <Fa icon={faKey} class="text-2xl text-orange-600 mb-2" />
          <h4 class="font-semibold">1 API Key</h4>
          <p class="text-sm text-gray-600">Active and tested</p>
        </div>
      </div>
    </div>
  </div>

  <!-- Search via Web Interface -->
  <div id="search-ui" class="card">
    <h2 class="text-2xl font-semibold mb-4 flex items-center">
      <Fa icon={faSearch} class="mr-2 text-primary-600" />
      2. Search via Web Interface
    </h2>
    <div class="space-y-4">
      <p class="text-gray-700">
        The easiest way to search is through the web interface. Navigate to the <a href="/search" class="text-primary-600 hover:text-primary-800">Search page</a> and enter your query.
      </p>
      
      <div class="bg-green-50 p-4 rounded-lg">
        <h3 class="font-semibold text-green-900 mb-2">How to Use:</h3>
        <ol class="list-decimal list-inside text-green-800 space-y-2">
          <li>Go to the <a href="/search" class="text-primary-600 hover:text-primary-800 underline">Search page</a></li>
          <li>Enter your query in natural language (e.g., "customer data management")</li>
          <li>Optionally adjust parameters like result limit and minimum score</li>
          <li>Click "Search" or press Enter</li>
          <li>Review results ranked by relevance score</li>
        </ol>
      </div>

      <div class="border-l-4 border-yellow-400 pl-4 py-2 bg-yellow-50">
        <p class="text-yellow-800">
          <strong>Tip:</strong> The search understands synonyms and context. Try queries like "send notifications", "process payments", or "validate user tokens".
        </p>
      </div>
    </div>
  </div>

  <!-- Search via API -->
  <div id="search-api" class="card">
    <h2 class="text-2xl font-semibold mb-4 flex items-center">
      <Fa icon={faCode} class="mr-2 text-primary-600" />
      3. Search via API
    </h2>
    <div class="space-y-6">
      <p class="text-gray-700">
        The search API provides programmatic access for applications, agents, and integrations.
      </p>

      <!-- POST Method -->
      <div class="bg-gray-50 p-4 rounded-lg">
        <h3 class="font-semibold mb-3 flex items-center">
          POST Method (Recommended)
          <button 
            on:click={() => copyToClipboard(postCurlExample, 'post-curl')}
            class="ml-2 px-2 py-1 text-xs bg-primary-600 text-white rounded hover:bg-primary-700"
          >
            <Fa icon={faCopy} class="mr-1" />
            {copySuccess === 'post-curl' ? 'Copied!' : 'Copy'}
          </button>
        </h3>
        <div class="bg-gray-900 text-gray-100 p-4 rounded text-sm overflow-x-auto">
          <pre><code>{postCurlExample}</code></pre>
        </div>
      </div>

      <!-- GET Method -->
      <div class="bg-gray-50 p-4 rounded-lg">
        <h3 class="font-semibold mb-3 flex items-center">
          GET Method (API Key Friendly)
          <button 
            on:click={() => copyToClipboard(getCurlExample, 'get-curl')}
            class="ml-2 px-2 py-1 text-xs bg-primary-600 text-white rounded hover:bg-primary-700"
          >
            <Fa icon={faCopy} class="mr-1" />
            {copySuccess === 'get-curl' ? 'Copied!' : 'Copy'}
          </button>
        </h3>
        <h4 class="text-sm font-medium mb-2">Option 1: API Key in Header</h4>
        <div class="bg-gray-900 text-gray-100 p-4 rounded text-sm overflow-x-auto mb-4">
          <pre><code>{getCurlExample}</code></pre>
        </div>
        
        <h4 class="text-sm font-medium mb-2 flex items-center">
          Option 2: API Key as Query Parameter
          <button 
            on:click={() => copyToClipboard(getCurlQueryExample, 'get-curl-param')}
            class="ml-2 px-2 py-1 text-xs bg-primary-600 text-white rounded hover:bg-primary-700"
          >
            <Fa icon={faCopy} class="mr-1" />
            {copySuccess === 'get-curl-param' ? 'Copied!' : 'Copy'}
          </button>
        </h4>
        <div class="bg-gray-900 text-gray-100 p-4 rounded text-sm overflow-x-auto">
          <pre><code>{getCurlQueryExample}</code></pre>
        </div>
        <p class="text-xs text-gray-600 mt-2">
          <strong>Note:</strong> API key can be passed either in the X-API-Key header or as a query parameter for maximum flexibility.
        </p>
      </div>

      <!-- Agent Orchestration Examples (NEW) -->
      <div class="bg-green-50 p-4 rounded-lg border border-green-200">
        <h3 class="font-semibold mb-3 flex items-center text-green-900">
          🎉 NEW: Agent Orchestration Enhanced Search
        </h3>
        <p class="text-sm text-green-800 mb-4">
          Use <code class="bg-green-100 px-2 py-1 rounded">include_orchestration=true</code> to receive complete tool schemas, examples, and orchestration metadata for agent-to-agent communication.
        </p>
        
        <h4 class="text-sm font-medium mb-2 flex items-center text-green-800">
          GET Method with Orchestration
          <button 
            on:click={() => copyToClipboard(getCurlOrchestrationExample, 'get-orchestration')}
            class="ml-2 px-2 py-1 text-xs bg-green-600 text-white rounded hover:bg-green-700"
          >
            <Fa icon={faCopy} class="mr-1" />
            {copySuccess === 'get-orchestration' ? 'Copied!' : 'Copy'}
          </button>
        </h4>
        <div class="bg-gray-900 text-gray-100 p-4 rounded text-sm overflow-x-auto mb-4">
          <pre><code>{getCurlOrchestrationExample}</code></pre>
        </div>
        
        <h4 class="text-sm font-medium mb-2 flex items-center text-green-800">
          POST Method with Orchestration
          <button 
            on:click={() => copyToClipboard(postOrchestrationExample, 'post-orchestration')}
            class="ml-2 px-2 py-1 text-xs bg-green-600 text-white rounded hover:bg-green-700"
          >
            <Fa icon={faCopy} class="mr-1" />
            {copySuccess === 'post-orchestration' ? 'Copied!' : 'Copy'}
          </button>
        </h4>
        <div class="bg-gray-900 text-gray-100 p-4 rounded text-sm overflow-x-auto">
          <pre><code>{postOrchestrationExample}</code></pre>
        </div>
        
        <div class="mt-3 p-3 bg-green-100 rounded">
          <h5 class="font-medium text-green-900 text-sm mb-2">What You'll Get:</h5>
          <ul class="text-xs text-green-800 space-y-1 list-disc list-inside">
            <li><strong>Complete Tool Schemas:</strong> Input/output definitions for direct agent invocation</li>
            <li><strong>Example Calls:</strong> Ready-to-use examples with different parameter combinations</li>
            <li><strong>Authentication Details:</strong> Specific auth configuration per service</li>
            <li><strong>Orchestration Metadata:</strong> Protocol versions, SLA expectations, security levels</li>
            <li><strong>Communication Patterns:</strong> Retry policies, idempotency, async support</li>
          </ul>
        </div>
      </div>

      <!-- API Endpoints -->
      <div class="border border-gray-200 rounded-lg overflow-hidden">
        <div class="bg-gray-100 px-4 py-2 font-semibold">Available Endpoints</div>
        <div class="divide-y divide-gray-200">
          <div class="p-4">
            <code class="bg-green-100 text-green-800 px-2 py-1 rounded">POST /api/v1/search</code>
            <p class="text-sm text-gray-600 mt-1">Semantic search with JSON request body</p>
          </div>
          <div class="p-4">
            <code class="bg-blue-100 text-blue-800 px-2 py-1 rounded">GET /api/v1/search</code>
            <p class="text-sm text-gray-600 mt-1">Semantic search with query parameters</p>
          </div>
          <div class="p-4">
            <code class="bg-purple-100 text-purple-800 px-2 py-1 rounded">GET /api/v1/search/similar/&#123;service_id&#125;</code>
            <p class="text-sm text-gray-600 mt-1">Find services similar to a specific service</p>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Search Parameters -->
  <div id="parameters" class="card">
    <h2 class="text-2xl font-semibold mb-4 flex items-center">
      <Fa icon={faCog} class="mr-2 text-primary-600" />
      4. Search Parameters
    </h2>
    <div class="space-y-4">
      <p class="text-gray-700 mb-6">
        Configure your search with these parameters to get the most relevant results:
      </p>

      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Parameter</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Default</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr>
              <td class="px-4 py-3 font-mono text-sm bg-red-50">query</td>
              <td class="px-4 py-3 text-sm text-gray-900">string</td>
              <td class="px-4 py-3 text-sm text-gray-500">required</td>
              <td class="px-4 py-3 text-sm text-gray-900">Natural language search query</td>
            </tr>
            <tr>
              <td class="px-4 py-3 font-mono text-sm">limit</td>
              <td class="px-4 py-3 text-sm text-gray-900">integer</td>
              <td class="px-4 py-3 text-sm text-gray-500">10</td>
              <td class="px-4 py-3 text-sm text-gray-900">Maximum number of results (1-100)</td>
            </tr>
            <tr>
              <td class="px-4 py-3 font-mono text-sm">min_score</td>
              <td class="px-4 py-3 text-sm text-gray-900">float</td>
              <td class="px-4 py-3 text-sm text-gray-500">0.0</td>
              <td class="px-4 py-3 text-sm text-gray-900">Minimum relevance score (0.0-1.0)</td>
            </tr>
            <tr>
              <td class="px-4 py-3 font-mono text-sm">domains</td>
              <td class="px-4 py-3 text-sm text-gray-900">array</td>
              <td class="px-4 py-3 text-sm text-gray-500">[]</td>
              <td class="px-4 py-3 text-sm text-gray-900">Filter by service domains</td>
            </tr>
            <tr>
              <td class="px-4 py-3 font-mono text-sm">capabilities</td>
              <td class="px-4 py-3 text-sm text-gray-900">array</td>
              <td class="px-4 py-3 text-sm text-gray-500">[]</td>
              <td class="px-4 py-3 text-sm text-gray-900">Filter by service capabilities</td>
            </tr>
            <tr class="bg-blue-50">
              <td class="px-4 py-3 font-mono text-sm">api_key</td>
              <td class="px-4 py-3 text-sm text-gray-900">string</td>
              <td class="px-4 py-3 text-sm text-gray-500">optional</td>
              <td class="px-4 py-3 text-sm text-gray-900">API key for authentication (GET method only)</td>
            </tr>
            <tr class="bg-green-50">
              <td class="px-4 py-3 font-mono text-sm">include_orchestration</td>
              <td class="px-4 py-3 text-sm text-gray-900">boolean</td>
              <td class="px-4 py-3 text-sm text-gray-500">false</td>
              <td class="px-4 py-3 text-sm text-gray-900">Include complete tool schemas, examples, and orchestration metadata for agent-to-agent communication</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="bg-blue-50 p-4 rounded-lg">
        <h3 class="font-semibold text-blue-900 mb-2">Parameter Tips:</h3>
        <ul class="list-disc list-inside text-blue-800 space-y-1">
          <li><strong>Query:</strong> Use natural language like "send email notifications" or "process credit card payments"</li>
          <li><strong>Limit:</strong> Start with 10 results, increase if you need more options</li>
          <li><strong>Min Score:</strong> Use 0.3-0.5 to filter out loosely related results</li>
          <li><strong>Domains:</strong> Filter by business areas like "Finance", "Communication", "Authentication"</li>
          <li><strong>Capabilities:</strong> Filter by specific capabilities like "send", "validate", "process"</li>
          <li><strong>API Key:</strong> Can be passed in header (X-API-Key) or as query parameter (api_key) for GET requests</li>
          <li><strong>Include Orchestration:</strong> Set to true to receive complete tool schemas, examples, and metadata for agent-to-agent communication</li>
        </ul>
      </div>
    </div>
  </div>

  <!-- Response Format -->
  <div id="response-format" class="card">
    <h2 class="text-2xl font-semibold mb-4 flex items-center">
      <Fa icon={faCode} class="mr-2 text-primary-600" />
      5. Response Format
    </h2>
    <div class="space-y-4">
      <p class="text-gray-700">
        The API returns search results in a structured JSON format with relevance scoring and detailed service information.
      </p>

      <div class="bg-gray-50 p-4 rounded-lg">
        <h3 class="font-semibold mb-3 flex items-center">
          Example Response
          <button 
            on:click={() => copyToClipboard(JSON.stringify(responseExample, null, 2), 'response-json')}
            class="ml-2 px-2 py-1 text-xs bg-primary-600 text-white rounded hover:bg-primary-700"
          >
            <Fa icon={faCopy} class="mr-1" />
            {copySuccess === 'response-json' ? 'Copied!' : 'Copy'}
          </button>
        </h3>
        <div class="bg-gray-900 text-gray-100 p-4 rounded text-sm overflow-x-auto">
          <pre><code>{JSON.stringify(responseExample, null, 2)}</code></pre>
        </div>
      </div>

      <!-- Agent Orchestration Response Example (NEW) -->
      <div class="bg-green-50 border border-green-200 rounded-lg p-4">
        <h3 class="font-semibold mb-3 flex items-center text-green-900">
          🎉 NEW: Agent Orchestration Response (include_orchestration=true)
          <button 
            on:click={() => copyToClipboard(JSON.stringify(orchestrationResponseExample, null, 2), 'orchestration-response')}
            class="ml-2 px-2 py-1 text-xs bg-green-600 text-white rounded hover:bg-green-700"
          >
            <Fa icon={faCopy} class="mr-1" />
            {copySuccess === 'orchestration-response' ? 'Copied!' : 'Copy'}
          </button>
        </h3>
        <p class="text-sm text-green-800 mb-3">
          When <code class="bg-green-100 px-2 py-1 rounded">include_orchestration=true</code>, the response includes complete tool definitions for agent-to-agent communication:
        </p>
        <div class="bg-gray-900 text-gray-100 p-4 rounded text-sm overflow-x-auto">
          <pre><code>{JSON.stringify(orchestrationResponseExample, null, 2)}</code></pre>
        </div>
        <div class="mt-3 p-3 bg-green-100 rounded">
          <h4 class="font-medium text-green-900 text-sm mb-2">Key Orchestration Fields:</h4>
          <ul class="text-xs text-green-800 space-y-1 list-disc list-inside grid grid-cols-1 md:grid-cols-2 gap-2">
            <li><code>tools[]</code> - Complete tool definitions with schemas</li>
            <li><code>input_schema</code> - JSON schema for parameter validation</li>
            <li><code>output_schema</code> - Response structure definition</li>
            <li><code>example_calls</code> - Ready-to-use invocation examples</li>
            <li><code>orchestration_summary</code> - Tool counts and capabilities</li>
            <li><code>tool_count_by_type</code> - Categorized tool inventory</li>
          </ul>
        </div>
      </div>

      <!-- Response Fields -->
      <div class="space-y-4">
        <h3 class="font-semibold">Response Fields:</h3>
        
        <!-- Root Level Fields -->
        <div>
          <h4 class="font-medium text-gray-800 mb-2">Root Level Fields:</h4>
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Field</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr>
                  <td class="px-4 py-3 font-mono text-sm">query</td>
                  <td class="px-4 py-3 text-sm text-gray-900">string</td>
                  <td class="px-4 py-3 text-sm text-gray-900">Original search query</td>
                </tr>
                <tr>
                  <td class="px-4 py-3 font-mono text-sm">results</td>
                  <td class="px-4 py-3 text-sm text-gray-900">array</td>
                  <td class="px-4 py-3 text-sm text-gray-900">Array of matching services with detailed metadata</td>
                </tr>
                <tr>
                  <td class="px-4 py-3 font-mono text-sm">total_results</td>
                  <td class="px-4 py-3 text-sm text-gray-900">integer</td>
                  <td class="px-4 py-3 text-sm text-gray-900">Number of results returned</td>
                </tr>
                <tr>
                  <td class="px-4 py-3 font-mono text-sm">search_time_ms</td>
                  <td class="px-4 py-3 text-sm text-gray-900">float</td>
                  <td class="px-4 py-3 text-sm text-gray-900">Search execution time in milliseconds</td>
                </tr>
                <tr>
                  <td class="px-4 py-3 font-mono text-sm">user_id</td>
                  <td class="px-4 py-3 text-sm text-gray-900">integer</td>
                  <td class="px-4 py-3 text-sm text-gray-900">ID of the user who made the request</td>
                </tr>
                <tr>
                  <td class="px-4 py-3 font-mono text-sm">timestamp</td>
                  <td class="px-4 py-3 text-sm text-gray-900">string</td>
                  <td class="px-4 py-3 text-sm text-gray-900">ISO timestamp of when the search was performed</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Result Item Fields -->
        <div>
          <h4 class="font-medium text-gray-800 mb-2">Result Item Fields:</h4>
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Field</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr>
                  <td class="px-4 py-3 font-mono text-sm">service_id</td>
                  <td class="px-4 py-3 text-sm text-gray-900">integer</td>
                  <td class="px-4 py-3 text-sm text-gray-900">Unique identifier for the service</td>
                </tr>
                <tr>
                  <td class="px-4 py-3 font-mono text-sm">score</td>
                  <td class="px-4 py-3 text-sm text-gray-900">float</td>
                  <td class="px-4 py-3 text-sm text-gray-900">Relevance score (0.0-1.0, higher is more relevant)</td>
                </tr>
                <tr>
                  <td class="px-4 py-3 font-mono text-sm">rank</td>
                  <td class="px-4 py-3 text-sm text-gray-900">integer</td>
                  <td class="px-4 py-3 text-sm text-gray-900">Result position (1-based)</td>
                </tr>
                <tr>
                  <td class="px-4 py-3 font-mono text-sm">service</td>
                  <td class="px-4 py-3 text-sm text-gray-900">object</td>
                  <td class="px-4 py-3 text-sm text-gray-900">Complete service definition with orchestration metadata</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Enhanced Service Object Fields -->
        <div class="bg-blue-50 p-4 rounded-lg">
          <h4 class="font-medium text-blue-900 mb-2">Enhanced Service Object (NEW - Agent Orchestration):</h4>
          <p class="text-sm text-blue-800 mb-3">The service object now includes comprehensive orchestration metadata for agent-to-agent communication:</p>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h5 class="font-medium text-blue-800 text-sm mb-2">Core Service Info:</h5>
              <ul class="text-xs text-blue-700 space-y-1 list-disc list-inside">
                <li><code>id</code>, <code>name</code>, <code>description</code></li>
                <li><code>endpoint</code>, <code>version</code>, <code>status</code></li>
                <li><code>tool_type</code>, <code>visibility</code></li>
                <li><code>interaction_modes</code>, <code>capabilities</code></li>
                <li><code>domains</code>, <code>tags</code></li>
              </ul>
            </div>
            <div>
              <h5 class="font-medium text-blue-800 text-sm mb-2">Agent Protocol Info:</h5>
              <ul class="text-xs text-blue-700 space-y-1 list-disc list-inside">
                <li><code>agent_protocol</code> - Protocol version (e.g., "kpath-v1")</li>
                <li><code>auth_type</code> - Authentication method</li>
                <li><code>auth_config</code> - Authentication configuration</li>
                <li><code>tool_recommendations</code> - Recommended tools/use cases</li>
                <li><code>agent_capabilities</code> - Detailed capabilities</li>
              </ul>
            </div>
          </div>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
            <div>
              <h5 class="font-medium text-blue-800 text-sm mb-2">Communication Patterns:</h5>
              <ul class="text-xs text-blue-700 space-y-1 list-disc list-inside">
                <li><code>idempotency</code> - Idempotency requirements</li>
                <li><code>retry_policy</code> - Retry configuration</li>
                <li><code>request_style</code> - Communication style</li>
                <li><code>async_supported</code> - Async support</li>
                <li><code>batch_operations</code> - Batch support</li>
              </ul>
            </div>
            <div>
              <h5 class="font-medium text-blue-800 text-sm mb-2">Orchestration Metadata:</h5>
              <ul class="text-xs text-blue-700 space-y-1 list-disc list-inside">
                <li><code>discovery_tags</code> - Tags for service discovery</li>
                <li><code>security_level</code> - Security classification</li>
                <li><code>business_domain</code> - Business domain</li>
                <li><code>sla_response_time_ms</code> - SLA expectations</li>
                <li><code>integration_complexity</code> - Complexity level</li>
              </ul>
            </div>
          </div>
        </div>

        <div class="bg-green-50 border border-green-200 rounded-lg p-4">
          <h4 class="font-medium text-green-900 mb-2">🎉 What's New in the Response:</h4>
          <div class="text-sm text-green-800 space-y-1">
            <p><strong>✅ Complete Tool Definitions:</strong> Full schema for agent-to-agent communication</p>
            <p><strong>✅ Authentication Details:</strong> Specific auth configuration per service</p>
            <p><strong>✅ Communication Patterns:</strong> Retry policies, idempotency, async support</p>
            <p><strong>✅ Orchestration Metadata:</strong> Discovery tags, security levels, SLA expectations</p>
            <p><strong>✅ Agent Capabilities:</strong> Detailed capability definitions and compliance info</p>
            <p><strong>✅ Integration Details:</strong> Complete integration specifications</p>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Example Queries -->
  <div id="examples" class="card">
    <h2 class="text-2xl font-semibold mb-4 flex items-center">
      <Fa icon={faPlay} class="mr-2 text-primary-600" />
      6. Example Queries
    </h2>
    <div class="space-y-6">
      <p class="text-gray-700">
        Here are example queries that work well with KPATH Enterprise's semantic search:
      </p>

      <!-- Good Queries -->
      <div class="bg-green-50 border border-green-200 rounded-lg p-4">
        <h3 class="font-semibold text-green-900 mb-3">
          <Fa icon={faCheckCircle} class="mr-2" />
          Effective Queries
        </h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="space-y-2">
            <h4 class="font-medium text-green-800">Business Intent:</h4>
            <ul class="text-sm text-green-700 space-y-1">
              <li>"customer data management"</li>
              <li>"send email notifications"</li>
              <li>"process credit card payments"</li>
              <li>"validate user authentication"</li>
              <li>"generate financial reports"</li>
            </ul>
          </div>
          <div class="space-y-2">
            <h4 class="font-medium text-green-800">Technical Actions:</h4>
            <ul class="text-sm text-green-700 space-y-1">
              <li>"check inventory levels"</li>
              <li>"document storage and retrieval"</li>
              <li>"user profile lookup"</li>
              <li>"payment processing gateway"</li>
              <li>"token validation service"</li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Poor Queries -->
      <div class="bg-red-50 border border-red-200 rounded-lg p-4">
        <h3 class="font-semibold text-red-900 mb-3">
          <Fa icon={faTimesCircle} class="mr-2" />
          Less Effective Queries
        </h3>
        <div class="space-y-2">
          <ul class="text-sm text-red-700 space-y-1">
            <li>Single words like "customer" or "payment" (too broad)</li>
            <li>Technical jargon without context like "API endpoint"</li>
            <li>Very specific implementation details</li>
            <li>Questions rather than statements</li>
          </ul>
        </div>
      </div>

      <!-- Real Examples -->
      <div class="bg-gray-50 p-4 rounded-lg">
        <h3 class="font-semibold mb-3">Try These Examples:</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="space-y-3">
            {#each [
              "customer profile data",
              "payment transaction processing", 
              "user authentication validation",
              "inventory stock checking"
            ] as exampleQuery}
              <div class="flex items-center justify-between bg-white p-3 rounded border">
                <code class="text-sm">{exampleQuery}</code>
                <a href="/search?q={encodeURIComponent(exampleQuery)}" 
                   class="text-xs bg-primary-600 text-white px-2 py-1 rounded hover:bg-primary-700">
                  Try It
                </a>
              </div>
            {/each}
          </div>
          <div class="space-y-3">
            {#each [
              "document management system",
              "notification sending service",
              "financial data processing",
              "sales reporting tools"
            ] as exampleQuery}
              <div class="flex items-center justify-between bg-white p-3 rounded border">
                <code class="text-sm">{exampleQuery}</code>
                <a href="/search?q={encodeURIComponent(exampleQuery)}" 
                   class="text-xs bg-primary-600 text-white px-2 py-1 rounded hover:bg-primary-700">
                  Try It
                </a>
              </div>
            {/each}
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Authentication -->
  <div id="authentication" class="card">
    <h2 class="text-2xl font-semibold mb-4 flex items-center">
      <Fa icon={faKey} class="mr-2 text-primary-600" />
      7. Authentication & API Keys
    </h2>
    <div class="space-y-4">
      <p class="text-gray-700">
        KPATH Enterprise supports multiple authentication methods for different use cases:
      </p>

      <!-- API Key Status -->
      <div class="bg-green-50 border border-green-200 rounded-lg p-4">
        <h3 class="font-semibold text-green-900 mb-2">
          <Fa icon={faCheckCircle} class="mr-2" />
          API Key Status: FULLY IMPLEMENTED ✅
        </h3>
        <p class="text-green-800 text-sm">
          <strong>Update (June 16, 2025):</strong> API key functionality has been successfully implemented and tested. 
          Both header and query parameter authentication methods are working correctly.
        </p>
        <div class="mt-2 text-green-700 text-sm">
          <strong>Testing Results:</strong>
          <ul class="list-disc list-inside ml-4">
            <li>✅ Header authentication: Working (X-API-Key header)</li>
            <li>✅ Query parameter authentication: Working (?api_key=...)</li>
            <li>✅ Response time: 45-165ms average</li>
            <li>✅ Security: SHA256 hashing implemented</li>
            <li>✅ Database integration: Fully operational</li>
          </ul>
        </div>
      </div>

      <!-- JWT Authentication -->
      <div class="border border-gray-200 rounded-lg p-4">
        <h3 class="font-semibold mb-2">JWT Token Authentication</h3>
        <p class="text-sm text-gray-600 mb-3">Best for web applications and user-based access</p>
        <div class="bg-gray-900 text-gray-100 p-3 rounded text-sm">
          <code>Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...</code>
        </div>
        <p class="text-xs text-gray-500 mt-2">Get JWT tokens from <code>/api/v1/auth/login</code></p>
      </div>

      <!-- API Key Authentication -->
      <div class="border border-green-200 bg-green-50 rounded-lg p-4">
        <h3 class="font-semibold mb-2 text-green-900">API Key Authentication (Recommended)</h3>
        <p class="text-sm text-green-800 mb-3">Best for service-to-service communication - Now fully working!</p>
        
        <h4 class="font-medium text-green-800 mb-2">Method 1: Header (Recommended)</h4>
        <div class="bg-gray-900 text-gray-100 p-3 rounded text-sm mb-3">
          <code>X-API-Key: kpe_your_api_key_here</code>
        </div>
        
        <h4 class="font-medium text-green-800 mb-2">Method 2: Query Parameter</h4>
        <div class="bg-gray-900 text-gray-100 p-3 rounded text-sm">
          <code>?api_key=kpe_your_api_key_here</code>
        </div>
        
        <p class="text-xs text-green-600 mt-2">
          Generate API keys from the <a href="/api-keys" class="text-primary-600 hover:text-primary-800 underline">API Keys page</a>
        </p>
      </div>

      <!-- Live Testing Examples -->
      <div class="bg-blue-50 p-4 rounded-lg">
        <h3 class="font-semibold text-blue-900 mb-2">Live Testing Examples (Verified Working):</h3>
        <div class="space-y-3">
          <div>
            <h4 class="text-sm font-medium text-blue-800">Header Method (✅ Tested):</h4>
            <div class="bg-blue-900 text-blue-100 p-2 rounded text-xs mt-1 overflow-x-auto">
              <code>curl -H "X-API-Key: kpe_TestKey123456789012345678901234" "http://localhost:8000/api/v1/search/search?query=customer%20data"</code>
            </div>
          </div>
          <div>
            <h4 class="text-sm font-medium text-blue-800">Query Parameter Method (✅ Tested):</h4>
            <div class="bg-blue-900 text-blue-100 p-2 rounded text-xs mt-1 overflow-x-auto">
              <code>curl "http://localhost:8000/api/v1/search/search?query=customer%20data&api_key=kpe_TestKey123456789012345678901234"</code>
            </div>
          </div>
          <div class="text-xs text-blue-700 mt-2">
            <strong>Note:</strong> Replace the test key with your actual API key from the API Keys page.
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Agent Orchestration -->
  <div id="orchestration" class="card">
    <h2 class="text-2xl font-semibold mb-4 flex items-center">
      <Fa icon={faRobot} class="mr-2 text-primary-600" />
      8. Agent Orchestration (New!)
    </h2>
    <div class="space-y-4">
      <p class="text-gray-700">
        KPATH Enterprise includes advanced agent orchestration capabilities for agent-to-agent communication with complete tool definitions and invocation tracking. <strong>NEW: Use <code class="bg-green-100 px-2 py-1 rounded">include_orchestration=true</code> to receive complete tool schemas and orchestration metadata!</strong>
      </p>

      <!-- Enhanced Response Format -->
      <div class="bg-green-50 border border-green-200 rounded-lg p-4">
        <h3 class="font-semibold text-green-900 mb-3">
          <Fa icon={faCheckCircle} class="mr-2" />
          🎉 Tool Schema Integration - FULLY OPERATIONAL ✅
        </h3>
        <p class="text-green-800 text-sm mb-3">
          <strong>Update (June 17, 2025):</strong> Complete tool definitions with input/output schemas, examples, and orchestration metadata are now included in search responses when <code class="bg-green-100 px-2 py-1 rounded">include_orchestration=true</code>:
        </p>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="space-y-2">
            <h4 class="font-medium text-green-800">Tool Schema Information:</h4>
            <ul class="text-sm text-green-700 space-y-1 list-disc list-inside">
              <li>Complete input/output JSON schemas</li>
              <li>Ready-to-use example calls</li>
              <li>Validation rules and error handling</li>
              <li>Tool versioning and status</li>
            </ul>
          </div>
          <div class="space-y-2">
            <h4 class="font-medium text-green-800">Orchestration Details:</h4>
            <ul class="text-sm text-green-700 space-y-1 list-disc list-inside">
              <li>Agent protocol versions (kpath-v1)</li>
              <li>Authentication requirements per service</li>
              <li>Communication patterns and retry policies</li>
              <li>Tool categorization and capabilities</li>
            </ul>
          </div>
        </div>
        
        <div class="mt-3 p-3 bg-green-100 rounded">
          <p class="text-xs text-green-700">
            <strong>Try it now:</strong> Add <code>&include_orchestration=true</code> to any search query to see complete tool definitions with schemas and examples. For example: 
            <a href="/search?q=customer%20data&include_orchestration=true" class="text-primary-600 hover:text-primary-800 underline">customer data with orchestration</a>
          </p>
        </div>
      </div>

      <!-- Tool Management -->
      <div class="bg-purple-50 border border-purple-200 rounded-lg p-4">
        <h3 class="font-semibold text-purple-900 mb-3">
          <Fa icon={faCog} class="mr-2" />
          Tool Management Endpoints
        </h3>
        <div class="space-y-2">
          <div class="flex justify-between items-center">
            <code class="text-sm bg-purple-100 text-purple-800 px-2 py-1 rounded">GET /api/v1/orchestration/tools</code>
            <span class="text-xs text-purple-600">List all tools</span>
          </div>
          <div class="flex justify-between items-center">
            <code class="text-sm bg-purple-100 text-purple-800 px-2 py-1 rounded">POST /api/v1/orchestration/tools</code>
            <span class="text-xs text-purple-600">Create new tool</span>
          </div>
          <div class="flex justify-between items-center">
            <code class="text-sm bg-purple-100 text-purple-800 px-2 py-1 rounded">GET /api/v1/orchestration/invocation-logs</code>
            <span class="text-xs text-purple-600">View invocation logs</span>
          </div>
          <div class="flex justify-between items-center">
            <code class="text-sm bg-purple-100 text-purple-800 px-2 py-1 rounded">GET /api/v1/orchestration/analytics/orchestration</code>
            <span class="text-xs text-purple-600">Get analytics</span>
          </div>
        </div>
      </div>

      <!-- Current Tool Examples -->
      <div class="border border-gray-200 rounded-lg p-4">
        <h3 class="font-semibold mb-3">Available Tools (5 total):</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="space-y-2">
            <div class="bg-gray-50 p-3 rounded">
              <h4 class="font-medium text-sm">get_customer_profile</h4>
              <p class="text-xs text-gray-600">CustomerDataAPI - Retrieve customer data</p>
            </div>
            <div class="bg-gray-50 p-3 rounded">
              <h4 class="font-medium text-sm">process_payment</h4>
              <p class="text-xs text-gray-600">PaymentGatewayAPI - Process transactions</p>
            </div>
          </div>
          <div class="space-y-2">
            <div class="bg-gray-50 p-3 rounded">
              <h4 class="font-medium text-sm">check_inventory</h4>
              <p class="text-xs text-gray-600">InventoryAPI - Check stock levels</p>
            </div>
            <div class="bg-gray-50 p-3 rounded">
              <h4 class="font-medium text-sm">validate_token</h4>
              <p class="text-xs text-gray-600">AuthenticationAPI - Token validation</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Live Analytics -->
      <div class="bg-green-50 border border-green-200 rounded-lg p-4">
        <h3 class="font-semibold text-green-900 mb-3">
          <Fa icon={faChartBar} class="mr-2" />
          Live Analytics Available
        </h3>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
          <div>
            <div class="text-2xl font-bold text-green-800">6</div>
            <div class="text-xs text-green-600">Total Invocations</div>
          </div>
          <div>
            <div class="text-2xl font-bold text-green-800">83%</div>
            <div class="text-xs text-green-600">Success Rate</div>
          </div>
          <div>
            <div class="text-2xl font-bold text-green-800">607ms</div>
            <div class="text-xs text-green-600">Avg Response</div>
          </div>
          <div>
            <div class="text-2xl font-bold text-green-800">5</div>
            <div class="text-xs text-green-600">Active Tools</div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- ESB Integration Guides -->
  <div id="integrations" class="card">
    <h2 class="text-2xl font-semibold mb-4 flex items-center">
      <Fa icon={faServer} class="mr-2 text-primary-600" />
      9. ESB Integration Guides (New!)
    </h2>
    <div class="space-y-4">
      <p class="text-gray-700">
        KPATH Enterprise integrates seamlessly with Enterprise Service Bus (ESB) platforms to provide intelligent, semantic-based service discovery for your integration flows. Comprehensive guides are now available for popular ESB platforms.
      </p>

      <!-- Integration Benefits -->
      <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 class="font-semibold text-blue-900 mb-3">
          <Fa icon={faCheckCircle} class="mr-2" />
          Integration Benefits
        </h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="space-y-2">
            <h4 class="font-medium text-blue-800">Dynamic Discovery:</h4>
            <ul class="text-sm text-blue-700 space-y-1 list-disc list-inside">
              <li>Natural language service queries</li>
              <li>Real-time service discovery</li>
              <li>Semantic matching for accuracy</li>
              <li>Cost and performance optimization</li>
            </ul>
          </div>
          <div class="space-y-2">
            <h4 class="font-medium text-blue-800">Enterprise Features:</h4>
            <ul class="text-sm text-blue-700 space-y-1 list-disc list-inside">
              <li>Circuit breakers for resilience</li>
              <li>Intelligent result caching</li>
              <li>Multi-region support</li>
              <li>A/B testing capabilities</li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Mulesoft Integration -->
      <div class="bg-orange-50 border border-orange-200 rounded-lg p-4">
        <h3 class="font-semibold text-orange-900 mb-3">
          <img src="data:image/svg+xml,%3Csvg width='20' height='20' viewBox='0 0 24 24' fill='%23ea580c' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M12 2L2 7v10c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7l-10-5z'/%3E%3C/svg%3E" alt="Mulesoft" class="inline-block mr-2 h-5 w-5" />
          Mulesoft Integration Guide
        </h3>
        <p class="text-orange-800 text-sm mb-3">
          Complete guide for integrating KPATH with Mulesoft Anypoint Platform
        </p>
        <div class="space-y-2">
          <h4 class="font-medium text-orange-800 text-sm">What's Included:</h4>
          <ul class="text-sm text-orange-700 space-y-1 list-disc list-inside ml-4">
            <li>Direct HTTP integration patterns</li>
            <li>Custom KPATH connector implementation</li>
            <li>Anypoint Exchange integration</li>
            <li>Dynamic routing with DataWeave</li>
            <li>Circuit breaker and caching patterns</li>
            <li>Real-world use cases and examples</li>
          </ul>
        </div>
        <div class="mt-4">
          <a href="/docs/integrations/mulesoft" 
             class="inline-flex items-center text-sm text-primary-600 hover:text-primary-800">
            <Fa icon={faExternalLinkAlt} class="mr-1" />
            View Mulesoft Integration Guide
          </a>
        </div>
      </div>

      <!-- Apache Camel Integration -->
      <div class="bg-red-50 border border-red-200 rounded-lg p-4">
        <h3 class="font-semibold text-red-900 mb-3">
          <img src="data:image/svg+xml,%3Csvg width='20' height='20' viewBox='0 0 24 24' fill='%23dc2626' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z'/%3E%3C/svg%3E" alt="Apache Camel" class="inline-block mr-2 h-5 w-5" />
          Apache Camel Integration Guide
        </h3>
        <p class="text-red-800 text-sm mb-3">
          Complete guide for integrating KPATH with Apache Camel routes
        </p>
        <div class="space-y-2">
          <h4 class="font-medium text-red-800 text-sm">What's Included:</h4>
          <ul class="text-sm text-red-700 space-y-1 list-disc list-inside ml-4">
            <li>Basic service discovery routes</li>
            <li>Custom KPATH component development</li>
            <li>Content-based routing patterns</li>
            <li>Stream processing with Kafka integration</li>
            <li>Camel K (Kubernetes) examples</li>
            <li>Spring Boot configuration</li>
          </ul>
        </div>
        <div class="mt-4">
          <a href="/docs/integrations/apache-camel" 
             class="inline-flex items-center text-sm text-primary-600 hover:text-primary-800">
            <Fa icon={faExternalLinkAlt} class="mr-1" />
            View Apache Camel Integration Guide
          </a>
        </div>
      </div>

      <!-- Quick Start Summary -->
      <div class="bg-green-50 border border-green-200 rounded-lg p-4">
        <h3 class="font-semibold text-green-900 mb-3">
          <Fa icon={faPlay} class="mr-2" />
          Quick Start Examples
        </h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <h4 class="font-medium text-green-800 text-sm mb-2">Mulesoft Quick Start:</h4>
            <div class="bg-gray-900 text-gray-100 p-2 rounded text-xs overflow-x-auto">
              <pre><code>&lt;http:request method="POST" 
              path="/api/v1/search/search"&gt;
  &lt;http:headers&gt;
    &lt;http:header key="X-API-Key" 
                 value="{'{your-api-key-here}'}" /&gt;
  &lt;/http:headers&gt;
&lt;/http:request&gt;</code></pre>
            </div>
          </div>
          <div>
            <h4 class="font-medium text-green-800 text-sm mb-2">Apache Camel Quick Start:</h4>
            <div class="bg-gray-900 text-gray-100 p-2 rounded text-xs overflow-x-auto">
              <pre><code>from("direct:discover")
  .setHeader("X-API-Key", 
            constant("{'{your-api-key-here}'}"))
  .to("http://localhost:8000" +
      "/api/v1/search/search")</code></pre>
            </div>
          </div>
        </div>
      </div>

      <!-- Common Use Cases -->
      <div class="border border-gray-200 rounded-lg p-4">
        <h3 class="font-semibold mb-3">Common Integration Use Cases:</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="bg-gray-50 p-3 rounded">
            <h4 class="font-medium text-sm mb-1">Customer 360 View</h4>
            <p class="text-xs text-gray-600">Discover all customer-related services dynamically</p>
            <code class="text-xs bg-gray-200 px-1 py-0.5 rounded">Query: "customer profile data history"</code>
          </div>
          <div class="bg-gray-50 p-3 rounded">
            <h4 class="font-medium text-sm mb-1">Payment Processing</h4>
            <p class="text-xs text-gray-600">Find the best payment processor for each transaction</p>
            <code class="text-xs bg-gray-200 px-1 py-0.5 rounded">Query: "payment processing USD credit"</code>
          </div>
          <div class="bg-gray-50 p-3 rounded">
            <h4 class="font-medium text-sm mb-1">Notification Routing</h4>
            <p class="text-xs text-gray-600">Route notifications to the right channel</p>
            <code class="text-xs bg-gray-200 px-1 py-0.5 rounded">Query: "send notification email urgent"</code>
          </div>
          <div class="bg-gray-50 p-3 rounded">
            <h4 class="font-medium text-sm mb-1">Document Management</h4>
            <p class="text-xs text-gray-600">Find document storage and retrieval services</p>
            <code class="text-xs bg-gray-200 px-1 py-0.5 rounded">Query: "document storage retrieval"</code>
          </div>
        </div>
      </div>

      <!-- Resources -->
      <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <h3 class="font-semibold text-yellow-900 mb-2">📚 Integration Resources</h3>
        <div class="text-yellow-800 text-sm space-y-1">
          <p><strong>✅ ESB Integration Summary:</strong> Quick overview and comparison</p>
          <p><strong>✅ Mulesoft Guide:</strong> Complete implementation patterns and examples</p>
          <p><strong>✅ Apache Camel Guide:</strong> Routes, components, and best practices</p>
          <p><strong>✅ Code Examples:</strong> Ready-to-use integration patterns</p>
          <p><strong>✅ Best Practices:</strong> Caching, error handling, and monitoring</p>
        </div>
        <div class="mt-3">
          <a href="/docs/integrations/" 
             target="_blank"
             class="inline-flex items-center text-sm text-primary-600 hover:text-primary-800">
            <Fa icon={faExternalLinkAlt} class="mr-1" />
            View All Integration Documentation
          </a>
        </div>
      </div>
    </div>
  </div>

  <!-- Testing Section -->
  <div class="card bg-primary-50 border-primary-200">
    <h2 class="text-2xl font-semibold mb-4 flex items-center text-primary-900">
      <Fa icon={faPlay} class="mr-2" />
      Ready to Test?
    </h2>
    <div class="space-y-4">
      <p class="text-primary-800">
        Now that you understand how KPATH Enterprise works, try these quick tests:
      </p>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="bg-white p-4 rounded-lg">
          <h3 class="font-semibold mb-2">Web Interface Testing</h3>
          <p class="text-sm text-gray-600 mb-3">Test the search functionality through the web UI</p>
          <a href="/search" class="btn btn-primary btn-sm">
            <Fa icon={faSearch} class="mr-1" />
            Go to Search Page
          </a>
        </div>
        
        <div class="bg-white p-4 rounded-lg">
          <h3 class="font-semibold mb-2">API Testing</h3>
          <p class="text-sm text-gray-600 mb-3">Get an API key and test programmatic access</p>
          <a href="/api-keys" class="btn btn-primary btn-sm">
            <Fa icon={faKey} class="mr-1" />
            Generate API Key
          </a>
        </div>
      </div>

      <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <h3 class="font-semibold text-yellow-900 mb-2">🎉 Recent Updates (June 16, 2025)</h3>
        <div class="text-yellow-800 text-sm space-y-1">
          <p><strong>✅ API Key Authentication:</strong> Fully implemented and tested</p>
          <p><strong>✅ Dual Authentication Methods:</strong> Both header and query parameter working</p>
          <p><strong>✅ Security:</strong> SHA256 hashing and secure generation implemented</p>
          <p><strong>✅ Performance:</strong> 45-165ms response times with API key authentication</p>
          <p><strong>🔬 Agent Orchestration:</strong> Implemented (5 tools) - currently in testing phase</p>
          <p><strong>📚 ESB Integration Guides:</strong> New Mulesoft and Apache Camel integration documentation</p>
        </div>
      </div>
    </div>
  </div>
</div>

<style>
  .card {
    @apply bg-white shadow-sm border border-gray-200 rounded-lg p-6;
  }
  
  .btn {
    @apply inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2;
  }
  
  .btn-primary {
    @apply text-white bg-primary-600 hover:bg-primary-700 focus:ring-primary-500;
  }
  
  .btn-sm {
    @apply px-3 py-1.5 text-xs;
  }
  
  .btn:disabled {
    @apply opacity-50 cursor-not-allowed;
  }
  
  /* Custom scrollbar for code blocks */
  pre::-webkit-scrollbar {
    height: 8px;
  }
  
  pre::-webkit-scrollbar-track {
    background: #374151;
  }
  
  pre::-webkit-scrollbar-thumb {
    background: #6B7280;
    border-radius: 4px;
  }
  
  pre::-webkit-scrollbar-thumb:hover {
    background: #9CA3AF;
  }
</style>