<script lang="ts">
  import { servicesApi, type ServiceCreateRequest } from '$lib/api/services';
  import { goto } from '$app/navigation';
  import Fa from 'svelte-fa';
  import { faPlus, faTrash } from '@fortawesome/free-solid-svg-icons';
  
  export let service: Partial<ServiceCreateRequest> = {
    name: '',
    description: '',
    endpoint: '',
    version: '',
    status: 'active',
    capabilities: [],
    domains: []
  };
  
  export let isEdit = false;
  export let serviceId: number | null = null;
  
  let loading = false;
  let error = '';
  
  let newCapability = {
    capability_name: '',
    capability_desc: ''
  };
  
  let newDomain = '';
  
  function addCapability() {
    if (newCapability.capability_name && newCapability.capability_desc) {
      service.capabilities = [...(service.capabilities || []), { ...newCapability }];
      newCapability = { capability_name: '', capability_desc: '' };
    }
  }
  
  function removeCapability(index: number) {
    service.capabilities = service.capabilities?.filter((_, i) => i !== index) || [];
  }
  
  function addDomain() {
    if (newDomain && !service.domains?.includes(newDomain)) {
      service.domains = [...(service.domains || []), newDomain];
      newDomain = '';
    }
  }
  
  function removeDomain(domain: string) {
    service.domains = service.domains?.filter(d => d !== domain) || [];
  }
  
  async function handleSubmit() {
    loading = true;
    error = '';
    
    try {
      if (isEdit && serviceId) {
        await servicesApi.update(serviceId, service as ServiceCreateRequest);
      } else {
        await servicesApi.create(service as ServiceCreateRequest);
      }
      goto('/services');
    } catch (err: any) {
      error = err.response?.data?.detail || 'Failed to save service';
    } finally {
      loading = false;
    }
  }
</script>

<form on:submit|preventDefault={handleSubmit} class="space-y-6">
  {#if error}
    <div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
      {error}
    </div>
  {/if}
  
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
          placeholder="e.g., CustomerService"
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
        </select>
      </div>
    </div>
  </div>
  
  <div class="card">
    <h3 class="text-lg font-semibold mb-4">Capabilities</h3>
    
    {#if service.capabilities && service.capabilities.length > 0}
      <div class="space-y-2 mb-4">
        {#each service.capabilities as capability, i}
          <div class="flex items-center justify-between p-3 bg-gray-50 rounded">
            <div>
              <p class="font-medium">{capability.capability_name}</p>
              <p class="text-sm text-gray-600">{capability.capability_desc}</p>
            </div>
            <button
              type="button"
              on:click={() => removeCapability(i)}
              class="text-red-600 hover:text-red-700"
            >
              <Fa icon={faTrash} />
            </button>
          </div>
        {/each}
      </div>
    {/if}
    
    <div class="space-y-2">
      <input
        type="text"
        bind:value={newCapability.capability_name}
        placeholder="Capability name"
        class="input"
      />
      <input
        type="text"
        bind:value={newCapability.capability_desc}
        placeholder="Capability description"
        class="input"
      />
      <button
        type="button"
        on:click={addCapability}
        class="btn btn-secondary"
      >
        <Fa icon={faPlus} class="mr-2" />
        Add Capability
      </button>
    </div>
  </div>
  
  <div class="card">
    <h3 class="text-lg font-semibold mb-4">Domains</h3>
    
    {#if service.domains && service.domains.length > 0}
      <div class="flex flex-wrap gap-2 mb-4">
        {#each service.domains as domain}
          <span class="px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm flex items-center">
            {domain}
            <button
              type="button"
              on:click={() => removeDomain(domain)}
              class="ml-2 text-primary-900 hover:text-red-600"
            >
              ×
            </button>
          </span>
        {/each}
      </div>
    {/if}
    
    <div class="flex gap-2">
      <input
        type="text"
        bind:value={newDomain}
        placeholder="Add domain (e.g., Finance, HR)"
        class="input flex-1"
      />
      <button
        type="button"
        on:click={addDomain}
        class="btn btn-secondary"
      >
        Add
      </button>
    </div>
  </div>
  
  <div class="flex justify-end space-x-3">
    <a href="/services" class="btn btn-secondary">Cancel</a>
    <button
      type="submit"
      disabled={loading}
      class="btn btn-primary"
    >
      {loading ? 'Saving...' : (isEdit ? 'Update Service' : 'Create Service')}
    </button>
  </div>
</form>
