<script lang="ts">
  import { servicesApi } from '$lib/api/services';
  import { goto } from '$app/navigation';
  import Fa from 'svelte-fa';
  import { faPlus, faTrash, faInfoCircle } from '@fortawesome/free-solid-svg-icons';
  import type { ServiceCreate, ServiceUpdate, ServiceIntegrationDetailsCreate, ServiceAgentProtocolsCreate } from '$lib/types';
  import { TOOL_TYPES, VISIBILITY_LEVELS, INTERACTION_MODES } from '$lib/types';
  
  export let service: Partial<ServiceCreate> = {
    name: '',
    description: '',
    endpoint: '',
    version: '',
    status: 'active',
    tool_type: 'API',
    interaction_modes: [],
    visibility: 'internal',
    default_timeout_ms: 30000
  };
  
  export let isEdit = false;
  export let serviceId: number | null = null;
  
  let loading = false;
  let error = '';
  let activeTab = 'basic';
  
  // Integration details
  let integrationDetails: ServiceIntegrationDetailsCreate = {
    access_protocol: 'REST',
    request_content_type: 'application/json',
    response_content_type: 'application/json'
  };
  
  // Agent protocols
  let agentProtocols: ServiceAgentProtocolsCreate = {
    message_protocol: 'JSON-RPC',
    requires_session_state: false,
    supports_streaming: false,
    supports_async: false,
    supports_batch: false
  };
  
  let hasIntegrationDetails = false;
  let hasAgentProtocols = false;
  
  // Load existing data if editing
  async function loadServiceDetails() {
    if (isEdit && serviceId) {
      try {
        // Try to load integration details
        const integration = await servicesApi.getIntegration(serviceId);
        if (integration) {
          integrationDetails = integration;
          hasIntegrationDetails = true;
        }
      } catch (err) {
        // No integration details exist yet
      }
      
      try {
        // Try to load agent protocols
        const protocols = await servicesApi.getAgentProtocols(serviceId);
        if (protocols) {
          agentProtocols = protocols;
          hasAgentProtocols = true;
        }
      } catch (err) {
        // No agent protocols exist yet
      }
    }
  }
  
  // Capabilities management
  let newCapability = {
    capability_name: '',
    capability_desc: ''
  };
  
  let capabilities: any[] = [];
  
  function addCapability() {
    if (newCapability.capability_desc) {
      capabilities = [...capabilities, { ...newCapability }];
      newCapability = { capability_name: '', capability_desc: '' };
    }
  }
  
  function removeCapability(index: number) {
    capabilities = capabilities.filter((_, i) => i !== index);
  }
  
  // Success criteria
  let successCriteriaJson = '';
  
  // Retry policy
  let retryPolicyJson = '';
  
  // Parse JSON fields
  function parseJsonField(field: string) {
    try {
      return field ? JSON.parse(field) : null;
    } catch {
      return null;
    }
  }
  
  async function handleSubmit() {
    loading = true;
    error = '';
    
    try {
      // Prepare service data
      const serviceData: ServiceCreate = {
        ...service,
        success_criteria: parseJsonField(successCriteriaJson),
        default_retry_policy: parseJsonField(retryPolicyJson)
      };
      
      let savedServiceId: number;
      
      if (isEdit && serviceId) {
        await servicesApi.update(serviceId, serviceData as ServiceUpdate);
        savedServiceId = serviceId;
      } else {
        const newService = await servicesApi.create(serviceData);
        savedServiceId = newService.id;
      }
      
      // Save integration details if needed
      if (activeTab === 'integration' || hasIntegrationDetails) {
        if (hasIntegrationDetails) {
          await servicesApi.updateIntegration(savedServiceId, integrationDetails);
        } else {
          await servicesApi.createIntegration(savedServiceId, integrationDetails);
        }
      }
      
      // Save agent protocols if tool type is agent
      if ((service.tool_type?.includes('Agent') || hasAgentProtocols) && activeTab === 'agent') {
        if (hasAgentProtocols) {
          await servicesApi.updateAgentProtocols(savedServiceId, agentProtocols);
        } else {
          await servicesApi.createAgentProtocols(savedServiceId, agentProtocols);
        }
      }
      
      // Save capabilities
      for (const cap of capabilities) {
        await servicesApi.addCapability(savedServiceId, cap);
      }
      
      goto('/services');
    } catch (err: any) {
      error = err.response?.data?.detail || err.message || 'Failed to save service';
    } finally {
      loading = false;
    }
  }
  
  // Initialize on mount
  import { onMount } from 'svelte';
  onMount(() => {
    if (service.success_criteria) {
      successCriteriaJson = JSON.stringify(service.success_criteria, null, 2);
    }
    if (service.default_retry_policy) {
      retryPolicyJson = JSON.stringify(service.default_retry_policy, null, 2);
    }
    loadServiceDetails();
  });
</script>

<form on:submit|preventDefault={handleSubmit} class="space-y-6">
  {#if error}
    <div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
      {error}
    </div>
  {/if}
  
  <!-- Tab Navigation -->
  <div class="border-b border-gray-200">
    <nav class="-mb-px flex space-x-8" aria-label="Tabs">
      <button
        type="button"
        on:click={() => activeTab = 'basic'}
        class="whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm {activeTab === 'basic' ? 'border-primary-500 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
      >
        Basic Information
      </button>
      <button
        type="button"
        on:click={() => activeTab = 'integration'}
        class="whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm {activeTab === 'integration' ? 'border-primary-500 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
      >
        Integration Details
      </button>
      {#if service.tool_type?.includes('Agent')}
        <button
          type="button"
          on:click={() => activeTab = 'agent'}
          class="whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm {activeTab === 'agent' ? 'border-primary-500 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
        >
          Agent Protocols
        </button>
      {/if}
      <button
        type="button"
        on:click={() => activeTab = 'capabilities'}
        class="whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm {activeTab === 'capabilities' ? 'border-primary-500 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
      >
        Capabilities
      </button>
    </nav>
  </div>

  <!-- Basic Information Tab -->
  {#if activeTab === 'basic'}
    <div class="card">
      <h3 class="text-lg font-semibold mb-4">Basic Information</h3>
      
      <div class="space-y-4">
        <div>
          <label for="name" class="block text-sm font-medium text-gray-700">
            Service Name *
          </label>
          <input
            id="name"
            type="text"
            bind:value={service.name}
            required
            class="input mt-1"
            placeholder="e.g., Customer Analytics API"
          />
        </div>
        
        <div>
          <label for="description" class="block text-sm font-medium text-gray-700">
            Description *
          </label>
          <textarea
            id="description"
            bind:value={service.description}
            required
            rows="3"
            class="input mt-1"
            placeholder="Describe what this service does..."
          />
        </div>
        
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label for="tool_type" class="block text-sm font-medium text-gray-700">
              Tool Type *
            </label>
            <select
              id="tool_type"
              bind:value={service.tool_type}
              required
              class="input mt-1"
            >
              {#each TOOL_TYPES as type}
                <option value={type.value}>{type.label}</option>
              {/each}
            </select>
          </div>
          
          <div>
            <label for="visibility" class="block text-sm font-medium text-gray-700">
              Visibility *
            </label>
            <select
              id="visibility"
              bind:value={service.visibility}
              required
              class="input mt-1"
            >
              {#each VISIBILITY_LEVELS as level}
                <option value={level.value}>{level.label}</option>
              {/each}
            </select>
          </div>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Interaction Modes
          </label>
          <div class="space-y-2">
            {#each INTERACTION_MODES as mode}
              <label class="flex items-center">
                <input
                  type="checkbox"
                  value={mode.value}
                  checked={service.interaction_modes?.includes(mode.value)}
                  on:change={(e) => {
                    if (e.currentTarget.checked) {
                      service.interaction_modes = [...(service.interaction_modes || []), mode.value];
                    } else {
                      service.interaction_modes = service.interaction_modes?.filter(m => m !== mode.value) || [];
                    }
                  }}
                  class="rounded text-primary-600 mr-2"
                />
                <span class="text-sm">{mode.label}</span>
              </label>
            {/each}
          </div>
        </div>
        
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label for="endpoint" class="block text-sm font-medium text-gray-700">
              Endpoint
            </label>
            <input
              id="endpoint"
              type="text"
              bind:value={service.endpoint}
              class="input mt-1"
              placeholder="https://api.example.com/v1"
            />
          </div>
          
          <div>
            <label for="version" class="block text-sm font-medium text-gray-700">
              Version
            </label>
            <input
              id="version"
              type="text"
              bind:value={service.version}
              class="input mt-1"
              placeholder="1.0.0"
            />
          </div>
        </div>
        
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label for="status" class="block text-sm font-medium text-gray-700">
              Status
            </label>
            <select
              id="status"
              bind:value={service.status}
              class="input mt-1"
            >
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="deprecated">Deprecated</option>
            </select>
          </div>
          
          <div>
            <label for="default_timeout_ms" class="block text-sm font-medium text-gray-700">
              Default Timeout (ms)
            </label>
            <input
              id="default_timeout_ms"
              type="number"
              bind:value={service.default_timeout_ms}
              min="0"
              class="input mt-1"
              placeholder="30000"
            />
          </div>
        </div>
        
        {#if service.status === 'deprecated'}
          <div>
            <label for="deprecation_notice" class="block text-sm font-medium text-gray-700">
              Deprecation Notice
            </label>
            <textarea
              id="deprecation_notice"
              bind:value={service.deprecation_notice}
              rows="2"
              class="input mt-1"
              placeholder="Explain why this service is deprecated..."
            />
          </div>
        {/if}
        
        <div>
          <label for="success_criteria" class="block text-sm font-medium text-gray-700">
            Success Criteria (JSON)
            <Fa icon={faInfoCircle} class="text-gray-400 ml-1" title="Define success conditions like status codes, response time, etc." />
          </label>
          <textarea
            id="success_criteria"
            bind:value={successCriteriaJson}
            rows="4"
            class="input mt-1 font-mono text-sm"
            placeholder={`{
  "status_codes": [200, 201],
  "max_response_time_ms": 1000
}`}
          />
        </div>
        
        <div>
          <label for="retry_policy" class="block text-sm font-medium text-gray-700">
            Default Retry Policy (JSON)
          </label>
          <textarea
            id="retry_policy"
            bind:value={retryPolicyJson}
            rows="4"
            class="input mt-1 font-mono text-sm"
            placeholder={`{
  "max_retries": 3,
  "backoff_multiplier": 2,
  "initial_interval_ms": 1000
}`}
          />
        </div>
      </div>
    </div>
  {/if}

  <!-- Integration Details Tab -->
  {#if activeTab === 'integration'}
    <div class="card">
      <h3 class="text-lg font-semibold mb-4">Integration Details</h3>
      
      <div class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label for="access_protocol" class="block text-sm font-medium text-gray-700">
              Access Protocol *
            </label>
            <select
              id="access_protocol"
              bind:value={integrationDetails.access_protocol}
              required
              class="input mt-1"
            >
              <option value="REST">REST</option>
              <option value="GraphQL">GraphQL</option>
              <option value="gRPC">gRPC</option>
              <option value="SOAP">SOAP</option>
              <option value="WebSocket">WebSocket</option>
              <option value="ESB">ESB</option>
            </select>
          </div>
          
          <div>
            <label for="base_endpoint" class="block text-sm font-medium text-gray-700">
              Base Endpoint
            </label>
            <input
              id="base_endpoint"
              type="text"
              bind:value={integrationDetails.base_endpoint}
              class="input mt-1"
              placeholder="https://api.example.com/v1"
            />
          </div>
        </div>
        
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label for="auth_method" class="block text-sm font-medium text-gray-700">
              Authentication Method
            </label>
            <select
              id="auth_method"
              bind:value={integrationDetails.auth_method}
              class="input mt-1"
            >
              <option value="">None</option>
              <option value="OAuth2">OAuth 2.0</option>
              <option value="JWT">JWT</option>
              <option value="APIKey">API Key</option>
              <option value="Basic">Basic Auth</option>
              <option value="Custom">Custom</option>
            </select>
          </div>
          
          <div>
            <label for="auth_endpoint" class="block text-sm font-medium text-gray-700">
              Auth Endpoint
            </label>
            <input
              id="auth_endpoint"
              type="text"
              bind:value={integrationDetails.auth_endpoint}
              class="input mt-1"
              placeholder="https://auth.example.com/token"
            />
          </div>
        </div>
        
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label for="rate_limit_requests" class="block text-sm font-medium text-gray-700">
              Rate Limit (requests)
            </label>
            <input
              id="rate_limit_requests"
              type="number"
              bind:value={integrationDetails.rate_limit_requests}
              min="0"
              class="input mt-1"
              placeholder="100"
            />
          </div>
          
          <div>
            <label for="rate_limit_window_seconds" class="block text-sm font-medium text-gray-700">
              Rate Limit Window (seconds)
            </label>
            <input
              id="rate_limit_window_seconds"
              type="number"
              bind:value={integrationDetails.rate_limit_window_seconds}
              min="0"
              class="input mt-1"
              placeholder="60"
            />
          </div>
        </div>
        
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label for="request_content_type" class="block text-sm font-medium text-gray-700">
              Request Content Type
            </label>
            <input
              id="request_content_type"
              type="text"
              bind:value={integrationDetails.request_content_type}
              class="input mt-1"
              placeholder="application/json"
            />
          </div>
          
          <div>
            <label for="response_content_type" class="block text-sm font-medium text-gray-700">
              Response Content Type
            </label>
            <input
              id="response_content_type"
              type="text"
              bind:value={integrationDetails.response_content_type}
              class="input mt-1"
              placeholder="application/json"
            />
          </div>
        </div>
        
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label for="health_check_endpoint" class="block text-sm font-medium text-gray-700">
              Health Check Endpoint
            </label>
            <input
              id="health_check_endpoint"
              type="text"
              bind:value={integrationDetails.health_check_endpoint}
              class="input mt-1"
              placeholder="/health"
            />
          </div>
          
          <div>
            <label for="health_check_interval_seconds" class="block text-sm font-medium text-gray-700">
              Health Check Interval (seconds)
            </label>
            <input
              id="health_check_interval_seconds"
              type="number"
              bind:value={integrationDetails.health_check_interval_seconds}
              min="0"
              class="input mt-1"
              placeholder="30"
            />
          </div>
        </div>
        
        {#if integrationDetails.access_protocol === 'ESB'}
          <hr class="my-4" />
          <h4 class="text-md font-medium mb-3">ESB Configuration</h4>
          
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label for="esb_type" class="block text-sm font-medium text-gray-700">
                ESB Type
              </label>
              <select
                id="esb_type"
                bind:value={integrationDetails.esb_type}
                class="input mt-1"
              >
                <option value="">Select ESB Type</option>
                <option value="MuleSoft">MuleSoft</option>
                <option value="IBMIntegrationBus">IBM Integration Bus</option>
                <option value="OracleServiceBus">Oracle Service Bus</option>
                <option value="WSO2">WSO2</option>
                <option value="Other">Other</option>
              </select>
            </div>
            
            <div>
              <label for="esb_service_name" class="block text-sm font-medium text-gray-700">
                ESB Service Name
              </label>
              <input
                id="esb_service_name"
                type="text"
                bind:value={integrationDetails.esb_service_name}
                class="input mt-1"
                placeholder="CustomerService"
              />
            </div>
          </div>
        {/if}
      </div>
    </div>
  {/if}

  <!-- Agent Protocols Tab -->
  {#if activeTab === 'agent' && service.tool_type?.includes('Agent')}
    <div class="card">
      <h3 class="text-lg font-semibold mb-4">Agent Protocols</h3>
      
      <div class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label for="message_protocol" class="block text-sm font-medium text-gray-700">
              Message Protocol *
            </label>
            <select
              id="message_protocol"
              bind:value={agentProtocols.message_protocol}
              required
              class="input mt-1"
            >
              <option value="JSON-RPC">JSON-RPC</option>
              <option value="OpenAI">OpenAI Format</option>
              <option value="Anthropic">Anthropic Format</option>
              <option value="Custom">Custom Format</option>
            </select>
          </div>
          
          <div>
            <label for="protocol_version" class="block text-sm font-medium text-gray-700">
              Protocol Version
            </label>
            <input
              id="protocol_version"
              type="text"
              bind:value={agentProtocols.protocol_version}
              class="input mt-1"
              placeholder="2.0"
            />
          </div>
        </div>
        
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label for="response_style" class="block text-sm font-medium text-gray-700">
              Response Style
            </label>
            <select
              id="response_style"
              bind:value={agentProtocols.response_style}
              class="input mt-1"
            >
              <option value="">Default</option>
              <option value="structured">Structured</option>
              <option value="conversational">Conversational</option>
              <option value="technical">Technical</option>
              <option value="casual">Casual</option>
            </select>
          </div>
          
          <div>
            <label for="max_context_length" class="block text-sm font-medium text-gray-700">
              Max Context Length
            </label>
            <input
              id="max_context_length"
              type="number"
              bind:value={agentProtocols.max_context_length}
              min="0"
              class="input mt-1"
              placeholder="4096"
            />
          </div>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Agent Capabilities
          </label>
          <div class="space-y-2">
            <label class="flex items-center">
              <input
                type="checkbox"
                bind:checked={agentProtocols.requires_session_state}
                class="rounded text-primary-600 mr-2"
              />
              <span class="text-sm">Requires Session State</span>
            </label>
            <label class="flex items-center">
              <input
                type="checkbox"
                bind:checked={agentProtocols.supports_streaming}
                class="rounded text-primary-600 mr-2"
              />
              <span class="text-sm">Supports Streaming</span>
            </label>
            <label class="flex items-center">
              <input
                type="checkbox"
                bind:checked={agentProtocols.supports_async}
                class="rounded text-primary-600 mr-2"
              />
              <span class="text-sm">Supports Async</span>
            </label>
            <label class="flex items-center">
              <input
                type="checkbox"
                bind:checked={agentProtocols.supports_batch}
                class="rounded text-primary-600 mr-2"
              />
              <span class="text-sm">Supports Batch Processing</span>
            </label>
          </div>
        </div>
      </div>
    </div>
  {/if}
  
  <!-- Capabilities Tab -->
  {#if activeTab === 'capabilities'}
    <div class="card">
      <h3 class="text-lg font-semibold mb-4">Service Capabilities</h3>
      
      <div class="space-y-4">
        <div class="border rounded-lg p-4 bg-gray-50">
          <div class="space-y-3">
            <input
              type="text"
              bind:value={newCapability.capability_name}
              placeholder="Capability name (optional)"
              class="input"
            />
            <textarea
              bind:value={newCapability.capability_desc}
              placeholder="Describe this capability..."
              rows="2"
              class="input"
            />
            <button
              type="button"
              on:click={addCapability}
              class="btn btn-secondary btn-sm"
              disabled={!newCapability.capability_desc}
            >
              <Fa icon={faPlus} class="mr-2" />
              Add Capability
            </button>
          </div>
        </div>
        
        {#if capabilities.length > 0}
          <div class="space-y-2">
            {#each capabilities as capability, i}
              <div class="border rounded-lg p-3 bg-white">
                <div class="flex justify-between items-start">
                  <div class="flex-1">
                    {#if capability.capability_name}
                      <h4 class="font-medium text-sm">{capability.capability_name}</h4>
                    {/if}
                    <p class="text-sm text-gray-600">{capability.capability_desc}</p>
                  </div>
                  <button
                    type="button"
                    on:click={() => removeCapability(i)}
                    class="text-red-500 hover:text-red-700 ml-2"
                  >
                    <Fa icon={faTrash} />
                  </button>
                </div>
              </div>
            {/each}
          </div>
        {/if}
      </div>
    </div>
  {/if}
  
  <!-- Submit Buttons -->
  <div class="flex justify-end space-x-3">
    <a href="/services" class="btn btn-secondary">
      Cancel
    </a>
    <button
      type="submit"
      disabled={loading}
      class="btn btn-primary"
    >
      {loading ? 'Saving...' : (isEdit ? 'Update Service' : 'Create Service')}
    </button>
  </div>
</form>
