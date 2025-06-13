<script lang="ts">
  import Fa from 'svelte-fa';
  import { faBook, faDownload, faExternalLink, faFileImport, faLightbulb, faExclamationTriangle, faCheckCircle } from '@fortawesome/free-solid-svg-icons';
  
  // Download functions
  function downloadSchema() {
    const link = document.createElement('a');
    link.href = '/docs/import-schema.json';
    link.download = 'kpath-import-schema.json';
    link.click();
  }
  
  function downloadSample() {
    const link = document.createElement('a');
    link.href = '/docs/sample-import.json';
    link.download = 'sample-import.json';
    link.click();
  }
</script>

<div class="max-w-4xl mx-auto space-y-8">
  <!-- Header -->
  <div class="flex justify-between items-start">
    <div>
      <h1 class="text-3xl font-bold text-gray-900 mb-2">Service Import Guide</h1>
      <p class="text-lg text-gray-600">Complete guide to importing services into KPATH Enterprise</p>
    </div>
    <div class="flex space-x-3">
      <button on:click={downloadSchema} class="btn btn-secondary">
        <Fa icon={faDownload} class="mr-2" />
        Schema
      </button>
      <button on:click={downloadSample} class="btn btn-secondary">
        <Fa icon={faDownload} class="mr-2" />
        Sample
      </button>
      <a href="/services/import" class="btn btn-primary">
        <Fa icon={faFileImport} class="mr-2" />
        Start Import
      </a>
    </div>
  </div>
  
  <!-- Quick Start -->
  <div class="card">
    <div class="flex items-center mb-4">
      <Fa icon={faLightbulb} class="text-yellow-500 mr-3 text-xl" />
      <h2 class="text-xl font-semibold">Quick Start</h2>
    </div>
    
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-blue-50 p-4 rounded-lg">
        <div class="font-semibold text-blue-900 mb-2">1. Download Resources</div>
        <p class="text-sm text-blue-800">Get the schema and sample files to understand the format</p>
      </div>
      <div class="bg-green-50 p-4 rounded-lg">
        <div class="font-semibold text-green-900 mb-2">2. Create JSON File</div>
        <p class="text-sm text-green-800">Build your import file following the schema structure</p>
      </div>
      <div class="bg-purple-50 p-4 rounded-lg">
        <div class="font-semibold text-purple-900 mb-2">3. Import Services</div>
        <p class="text-sm text-purple-800">Upload and import your services through the web interface</p>
      </div>
    </div>
  </div>
  
  <!-- Overview -->
  <div class="card">
    <h2 class="text-xl font-semibold mb-4">Overview</h2>
    <p class="text-gray-600 mb-4">
      The KPATH Enterprise Service Import system allows you to bulk import multiple services from a single JSON file. 
      This is ideal for initial system setup, migrating services from other systems, or creating consistent service definitions.
    </p>
    
    <div class="bg-gray-50 p-4 rounded-lg">
      <h3 class="font-medium mb-2">Supported Features:</h3>
      <ul class="text-sm text-gray-600 space-y-1">
        <li>• All service types (API, Internal Agent, External Agent, ESB Endpoint, Legacy System, Microservice)</li>
        <li>• Complete enterprise integration configurations</li>
        <li>• Authentication and security settings</li>
        <li>• Agent communication protocols</li>
        <li>• Service capabilities and industry classifications</li>
        <li>• Validation and detailed error handling</li>
      </ul>
    </div>
  </div>
  
  <!-- JSON Structure -->
  <div class="card">
    <h2 class="text-xl font-semibold mb-4">JSON File Structure</h2>
    
    <div class="bg-gray-900 text-gray-100 p-4 rounded-lg mb-4 font-mono text-sm overflow-x-auto">
      <pre>{`{
  "version": "1.0",
  "metadata": {
    "description": "Import description",
    "created_by": "admin",
    "tags": ["tag1", "tag2"]
  },
  "services": [
    {
      "name": "Service Name",
      "description": "Service description",
      "tool_type": "API",
      "endpoint": "https://api.example.com",
      "integration_details": { ... },
      "capabilities": [ ... ]
    }
  ]
}`}</pre>
    </div>
    
    <div class="bg-blue-50 border border-blue-200 rounded-md p-4">
      <div class="flex items-center mb-2">
        <Fa icon={faCheckCircle} class="text-blue-600 mr-2" />
        <span class="font-medium text-blue-900">Required Fields</span>
      </div>
      <ul class="text-sm text-blue-800 space-y-1">
        <li>• <code class="bg-blue-100 px-1 rounded">version</code> - Schema version (currently "1.0")</li>
        <li>• <code class="bg-blue-100 px-1 rounded">services</code> - Array of service objects</li>
        <li>• <code class="bg-blue-100 px-1 rounded">name</code> - Unique service name (per service)</li>
        <li>• <code class="bg-blue-100 px-1 rounded">description</code> - Service description (per service)</li>
        <li>• <code class="bg-blue-100 px-1 rounded">tool_type</code> - Service type (per service)</li>
      </ul>
    </div>
  </div>
  
  <!-- Service Types -->
  <div class="card">
    <h2 class="text-xl font-semibold mb-4">Service Types</h2>
    
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div class="border rounded-lg p-4">
        <h3 class="font-medium text-green-700 mb-2">API</h3>
        <p class="text-sm text-gray-600">REST APIs, GraphQL endpoints, web services</p>
      </div>
      <div class="border rounded-lg p-4">
        <h3 class="font-medium text-blue-700 mb-2">InternalAgent</h3>
        <p class="text-sm text-gray-600">Internal AI agents and chatbots</p>
      </div>
      <div class="border rounded-lg p-4">
        <h3 class="font-medium text-purple-700 mb-2">ExternalAgent</h3>
        <p class="text-sm text-gray-600">Third-party AI services and agents</p>
      </div>
      <div class="border rounded-lg p-4">
        <h3 class="font-medium text-orange-700 mb-2">ESBEndpoint</h3>
        <p class="text-sm text-gray-600">Enterprise Service Bus integrations</p>
      </div>
      <div class="border rounded-lg p-4">
        <h3 class="font-medium text-gray-700 mb-2">LegacySystem</h3>
        <p class="text-sm text-gray-600">Legacy systems being modernized</p>
      </div>
      <div class="border rounded-lg p-4">
        <h3 class="font-medium text-indigo-700 mb-2">MicroService</h3>
        <p class="text-sm text-gray-600">Modern microservice architectures</p>
      </div>
    </div>
  </div>
  
  <!-- Examples -->
  <div class="card">
    <h2 class="text-xl font-semibold mb-4">Example Configurations</h2>
    
    <div class="space-y-6">
      <!-- API Example -->
      <div>
        <h3 class="font-medium text-gray-900 mb-2">API Service Example</h3>
        <div class="bg-gray-900 text-gray-100 p-4 rounded-lg font-mono text-sm overflow-x-auto">
          <pre>{`{
  "name": "Customer Analytics API",
  "description": "Advanced customer analytics and insights",
  "tool_type": "API",
  "endpoint": "https://api.company.com/analytics/v1",
  "version": "1.2.0",
  "status": "active",
  "visibility": "org-wide",
  "interaction_modes": ["sync", "async"],
  "integration_details": {
    "access_protocol": "REST",
    "auth_method": "OAuth2",
    "rate_limit_requests": 1000,
    "rate_limit_window_seconds": 3600
  },
  "capabilities": [
    {
      "capability_name": "customer_segmentation",
      "capability_desc": "Segment customers by behavior"
    }
  ]
}`}</pre>
        </div>
      </div>
      
      <!-- Agent Example -->
      <div>
        <h3 class="font-medium text-gray-900 mb-2">Internal Agent Example</h3>
        <div class="bg-gray-900 text-gray-100 p-4 rounded-lg font-mono text-sm overflow-x-auto">
          <pre>{`{
  "name": "AI Support Assistant",
  "description": "Intelligent customer support agent",
  "tool_type": "InternalAgent",
  "visibility": "internal",
  "interaction_modes": ["sync", "stream"],
  "agent_protocols": {
    "message_protocol": "OpenAI",
    "protocol_version": "1.0",
    "response_style": "conversational",
    "requires_session_state": true,
    "supports_streaming": true
  },
  "capabilities": [
    {
      "capability_name": "natural_language_processing",
      "capability_desc": "Process natural language queries"
    }
  ]
}`}</pre>
        </div>
      </div>
    </div>
  </div>
  
  <!-- Import Process -->
  <div class="card">
    <h2 class="text-xl font-semibold mb-4">Import Process</h2>
    
    <div class="space-y-4">
      <div class="flex items-start space-x-3">
        <div class="bg-blue-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-medium">1</div>
        <div>
          <h3 class="font-medium">Upload File</h3>
          <p class="text-sm text-gray-600">Drag & drop your JSON file or click to browse</p>
        </div>
      </div>
      
      <div class="flex items-start space-x-3">
        <div class="bg-blue-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-medium">2</div>
        <div>
          <h3 class="font-medium">Validation</h3>
          <p class="text-sm text-gray-600">File is automatically validated against the schema</p>
        </div>
      </div>
      
      <div class="flex items-start space-x-3">
        <div class="bg-blue-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-medium">3</div>
        <div>
          <h3 class="font-medium">Preview</h3>
          <p class="text-sm text-gray-600">Review services that will be imported</p>
        </div>
      </div>
      
      <div class="flex items-start space-x-3">
        <div class="bg-blue-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-medium">4</div>
        <div>
          <h3 class="font-medium">Import</h3>
          <p class="text-sm text-gray-600">Services are created with progress tracking</p>
        </div>
      </div>
      
      <div class="flex items-start space-x-3">
        <div class="bg-blue-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-medium">5</div>
        <div>
          <h3 class="font-medium">Results</h3>
          <p class="text-sm text-gray-600">Review detailed success/failure results</p>
        </div>
      </div>
    </div>
  </div>
  
  <!-- Troubleshooting -->
  <div class="card">
    <h2 class="text-xl font-semibold mb-4">Common Issues</h2>
    
    <div class="space-y-4">
      <div class="bg-red-50 border border-red-200 rounded-md p-4">
        <div class="flex items-center mb-2">
          <Fa icon={faExclamationTriangle} class="text-red-600 mr-2" />
          <span class="font-medium text-red-900">Invalid JSON file</span>
        </div>
        <p class="text-sm text-red-800">Check JSON syntax, ensure all brackets and quotes are properly closed</p>
      </div>
      
      <div class="bg-yellow-50 border border-yellow-200 rounded-md p-4">
        <div class="flex items-center mb-2">
          <Fa icon={faExclamationTriangle} class="text-yellow-600 mr-2" />
          <span class="font-medium text-yellow-900">Service name already exists</span>
        </div>
        <p class="text-sm text-yellow-800">Service names must be unique. Use different names or delete existing services first</p>
      </div>
      
      <div class="bg-blue-50 border border-blue-200 rounded-md p-4">
        <div class="flex items-center mb-2">
          <Fa icon={faExclamationTriangle} class="text-blue-600 mr-2" />
          <span class="font-medium text-blue-900">Required field missing</span>
        </div>
        <p class="text-sm text-blue-800">Ensure all required fields are present: name, description, tool_type</p>
      </div>
    </div>
  </div>
  
  <!-- Best Practices -->
  <div class="card">
    <h2 class="text-xl font-semibold mb-4">Best Practices</h2>
    
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div>
        <h3 class="font-medium text-gray-900 mb-3">File Organization</h3>
        <ul class="text-sm text-gray-600 space-y-2">
          <li>• Use descriptive metadata and tags</li>
          <li>• Group related services together</li>
          <li>• Keep imports under 100 services per file</li>
          <li>• Use consistent naming conventions</li>
        </ul>
      </div>
      
      <div>
        <h3 class="font-medium text-gray-900 mb-3">Service Definitions</h3>
        <ul class="text-sm text-gray-600 space-y-2">
          <li>• Provide detailed, meaningful descriptions</li>
          <li>• Use appropriate tool types</li>
          <li>• Set proper visibility levels</li>
          <li>• Include complete capability definitions</li>
        </ul>
      </div>
      
      <div>
        <h3 class="font-medium text-gray-900 mb-3">Security</h3>
        <ul class="text-sm text-gray-600 space-y-2">
          <li>• Don't include actual API keys or passwords</li>
          <li>• Use placeholder values for sensitive data</li>
          <li>• Review visibility settings carefully</li>
          <li>• Store import files securely</li>
        </ul>
      </div>
      
      <div>
        <h3 class="font-medium text-gray-900 mb-3">Testing</h3>
        <ul class="text-sm text-gray-600 space-y-2">
          <li>• Always validate files before importing</li>
          <li>• Test in non-production environments first</li>
          <li>• Review all import results</li>
          <li>• Keep backups of import files</li>
        </ul>
      </div>
    </div>
  </div>
  
  <!-- Resources -->
  <div class="card">
    <h2 class="text-xl font-semibold mb-4">Resources</h2>
    
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <button on:click={downloadSchema} class="p-4 border rounded-lg hover:bg-gray-50 text-left">
        <Fa icon={faDownload} class="text-blue-600 mb-2" />
        <h3 class="font-medium mb-1">JSON Schema</h3>
        <p class="text-sm text-gray-600">Complete validation schema</p>
      </button>
      
      <button on:click={downloadSample} class="p-4 border rounded-lg hover:bg-gray-50 text-left">
        <Fa icon={faDownload} class="text-green-600 mb-2" />
        <h3 class="font-medium mb-1">Sample File</h3>
        <p class="text-sm text-gray-600">Working examples to start from</p>
      </button>
      
      <a href="/services/import" class="p-4 border rounded-lg hover:bg-gray-50 text-left">
        <Fa icon={faFileImport} class="text-purple-600 mb-2" />
        <h3 class="font-medium mb-1">Import Services</h3>
        <p class="text-sm text-gray-600">Start the import process</p>
      </a>
    </div>
  </div>
  
  <!-- Footer -->
  <div class="text-center py-8 border-t">
    <p class="text-gray-500 text-sm">
      KPATH Enterprise Service Import Guide v1.0
    </p>
    <div class="mt-2 space-x-4">
      <a href="/services" class="text-primary-600 hover:text-primary-800 text-sm">← Back to Services</a>
      <a href="/services/import" class="text-primary-600 hover:text-primary-800 text-sm">Start Import →</a>
    </div>
  </div>
</div>