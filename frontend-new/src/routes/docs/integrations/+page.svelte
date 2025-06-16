<script lang="ts">
  import { faArrowLeft, faFileAlt, faExternalLinkAlt } from '@fortawesome/free-solid-svg-icons';
  import Fa from 'svelte-fa';
</script>

<div class="min-h-screen bg-gray-50">
  <div class="max-w-4xl mx-auto p-8">
    <div class="bg-white rounded-lg shadow-sm p-8">
      <a href="/user-guide" class="inline-flex items-center text-primary-600 hover:text-primary-800 mb-6">
        <Fa icon={faArrowLeft} class="mr-2" />
        Back to User Guide
      </a>
      
      <h1 class="text-3xl font-bold text-gray-900 mb-6">KPATH Enterprise Integration Documentation</h1>
      
      <p class="text-gray-600 mb-8">
        Welcome to the KPATH Enterprise integration documentation. These guides will help you integrate KPATH with your existing Enterprise Service Bus (ESB) and integration platforms.
      </p>
      
      <h2 class="text-2xl font-semibold text-gray-800 mb-4">Available Integration Guides</h2>
      
      <div class="space-y-4 mb-8">
        <div class="bg-gray-50 p-6 rounded-lg border border-gray-200 hover:bg-gray-100 transition-colors">
          <a href="/docs/integrations/esb-summary" class="block">
            <h3 class="text-lg font-semibold text-primary-600 mb-2 flex items-center">
              <Fa icon={faFileAlt} class="mr-2" />
              ESB Integration Summary
            </h3>
            <p class="text-gray-600">Quick overview and comparison of ESB integration approaches with KPATH Enterprise.</p>
          </a>
        </div>
        
        <div class="bg-gray-50 p-6 rounded-lg border border-gray-200 hover:bg-gray-100 transition-colors">
          <a href="/docs/integrations/mulesoft" class="block">
            <h3 class="text-lg font-semibold text-primary-600 mb-2 flex items-center">
              <Fa icon={faFileAlt} class="mr-2" />
              Mulesoft Integration Guide
            </h3>
            <p class="text-gray-600">Complete implementation patterns and examples for integrating KPATH with Mulesoft, including HTTP connectors, custom components, and Anypoint Exchange integration.</p>
          </a>
        </div>
        
        <div class="bg-gray-50 p-6 rounded-lg border border-gray-200 hover:bg-gray-100 transition-colors">
          <a href="/docs/integrations/apache-camel" class="block">
            <h3 class="text-lg font-semibold text-primary-600 mb-2 flex items-center">
              <Fa icon={faFileAlt} class="mr-2" />
              Apache Camel Integration Guide
            </h3>
            <p class="text-gray-600">Routes, components, and best practices for integrating KPATH with Apache Camel, including Spring Boot configuration and Camel K examples.</p>
          </a>
        </div>
      </div>
      
      <h2 class="text-2xl font-semibold text-gray-800 mb-4">Key Integration Features</h2>
      
      <ul class="list-disc list-inside space-y-2 text-gray-600 mb-8">
        <li>Dynamic service discovery using natural language queries</li>
        <li>API key and JWT authentication support</li>
        <li>Intelligent routing based on semantic search</li>
        <li>Caching strategies for performance optimization</li>
        <li>Circuit breaker patterns for resilience</li>
        <li>Multi-region service discovery</li>
        <li>Real-time monitoring and metrics</li>
      </ul>
      
      <h2 class="text-2xl font-semibold text-gray-800 mb-4">Getting Started</h2>
      
      <p class="text-gray-600 mb-4">To get started with KPATH Enterprise integration:</p>
      
      <ol class="list-decimal list-inside space-y-2 text-gray-600">
        <li>Choose your integration platform (Mulesoft or Apache Camel)</li>
        <li>Obtain an API key from the KPATH admin interface</li>
        <li>Follow the appropriate integration guide</li>
        <li>Test with the provided examples</li>
        <li>Implement your specific use cases</li>
      </ol>
    </div>
  </div>
</div>
