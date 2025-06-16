<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import Fa from 'svelte-fa';
  import { 
    faKey, 
    faArrowLeft,
    faSpinner,
    faExclamationTriangle,
    faCheckCircle,
    faTimesCircle,
    faChartBar,
    faTrash,
    faEdit
  } from '@fortawesome/free-solid-svg-icons';
  import { api } from '$lib/api/client';

  let keyId: string;
  let apiKeyInfo: any = null;
  let loading = true;
  let error = '';

  $: keyId = $page.params.id;

  onMount(async () => {
    await loadApiKey();
  });

  async function loadApiKey() {
    if (!keyId) return;
    
    loading = true;
    error = '';
    
    try {
      // Use the proper API client instead of direct fetch
      apiKeyInfo = await api.get(`/api-keys/${keyId}`);
      
    } catch (err: any) {
      console.error('Error loading API key:', err);
      error = err.response?.data?.detail || err.message || 'Failed to load API key data';
    } finally {
      loading = false;
    }
  }

  function goBack() {
    goto('/api-keys');
  }

  function viewUsage() {
    goto(`/api-keys/${keyId}/usage`);
  }

  function formatDate(dateString: string) {
    return new Date(dateString).toLocaleDateString();
  }

  function formatDateTime(dateString: string) {
    return new Date(dateString).toLocaleString();
  }
</script>

<svelte:head>
  <title>API Key Details - KPATH Enterprise</title>
</svelte:head>

<div class="max-w-4xl mx-auto space-y-6">
  <!-- Header -->
  <div class="flex items-center justify-between">
    <div class="flex items-center space-x-4">
      <button on:click={goBack} class="btn btn-secondary btn-sm">
        <Fa icon={faArrowLeft} class="mr-2" />
        Back to API Keys
      </button>
      <div>
        <h1 class="text-2xl font-bold text-gray-900 flex items-center">
          <Fa icon={faKey} class="mr-3 text-primary-600" />
          API Key Details
        </h1>
        {#if apiKeyInfo}
          <p class="text-sm text-gray-600 mt-1">
            {apiKeyInfo.name} • ID: {keyId}
          </p>
        {/if}
      </div>
    </div>
    
    {#if apiKeyInfo}
      <div class="flex space-x-2">
        <button on:click={viewUsage} class="btn btn-primary btn-sm">
          <Fa icon={faChartBar} class="mr-2" />
          View Usage
        </button>
      </div>
    {/if}
  </div>

  {#if loading}
    <div class="flex items-center justify-center py-12">
      <Fa icon={faSpinner} class="text-2xl text-primary-600 animate-spin mr-3" />
      <span class="text-gray-600">Loading API key details...</span>
    </div>
  {:else if error}
    <div class="bg-red-50 border border-red-200 rounded-lg p-4">
      <div class="flex items-center">
        <Fa icon={faExclamationTriangle} class="text-red-600 mr-2" />
        <h3 class="text-red-900 font-medium">Error Loading Data</h3>
      </div>
      <p class="text-red-800 text-sm mt-2">{error}</p>
      <button 
        on:click={loadApiKey}
        class="mt-3 btn btn-secondary btn-sm"
      >
        Try Again
      </button>
    </div>
  {:else if apiKeyInfo}
    <!-- API Key Info -->
    <div class="card">
      <h2 class="text-lg font-semibold mb-4">API Key Information</h2>
      <div class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700">Name</label>
            <div class="mt-1 text-sm text-gray-900">{apiKeyInfo.name}</div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">Status</label>
            <div class="mt-1 flex items-center">
              {#if apiKeyInfo.is_active}
                <Fa icon={faCheckCircle} class="text-green-600 mr-2" />
                <span class="text-green-800">Active</span>
              {:else}
                <Fa icon={faTimesCircle} class="text-red-600 mr-2" />
                <span class="text-red-800">Inactive</span>
              {/if}
            </div>
          </div>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700">Created</label>
            <div class="mt-1 text-sm text-gray-900">{formatDateTime(apiKeyInfo.created_at)}</div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">Last Used</label>
            <div class="mt-1 text-sm text-gray-900">
              {apiKeyInfo.last_used_at ? formatDateTime(apiKeyInfo.last_used_at) : 'Never'}
            </div>
          </div>
        </div>
        
        {#if apiKeyInfo.expires_at}
          <div>
            <label class="block text-sm font-medium text-gray-700">Expires</label>
            <div class="mt-1 text-sm text-gray-900">{formatDateTime(apiKeyInfo.expires_at)}</div>
          </div>
        {/if}
        
        {#if apiKeyInfo.scopes && apiKeyInfo.scopes.length > 0}
          <div>
            <label class="block text-sm font-medium text-gray-700">Scopes</label>
            <div class="mt-1 flex flex-wrap gap-2">
              {#each apiKeyInfo.scopes as scope}
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
                  {scope}
                </span>
              {/each}
            </div>
          </div>
        {/if}
        
        {#if apiKeyInfo.description}
          <div>
            <label class="block text-sm font-medium text-gray-700">Description</label>
            <div class="mt-1 text-sm text-gray-900">{apiKeyInfo.description}</div>
          </div>
        {/if}
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="card">
      <h2 class="text-lg font-semibold mb-4">Quick Actions</h2>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <button 
          on:click={viewUsage}
          class="flex items-center justify-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
        >
          <Fa icon={faChartBar} class="text-primary-600 mr-3" />
          <span class="font-medium">View Usage Statistics</span>
        </button>
        
        <a 
          href="/user-guide#authentication"
          class="flex items-center justify-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
        >
          <Fa icon={faKey} class="text-green-600 mr-3" />
          <span class="font-medium">Authentication Guide</span>
        </a>
        
        <a 
          href="/api-keys"
          class="flex items-center justify-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
        >
          <Fa icon={faEdit} class="text-blue-600 mr-3" />
          <span class="font-medium">Manage All Keys</span>
        </a>
      </div>
    </div>
  {/if}
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
  
  .btn-secondary {
    @apply text-gray-700 bg-white border-gray-300 hover:bg-gray-50 focus:ring-primary-500;
  }
  
  .btn-sm {
    @apply px-3 py-1.5 text-xs;
  }
  
  /* Spinner animation */
  .animate-spin {
    animation: spin 1s linear infinite;
  }
  
  @keyframes spin {
    from {
      transform: rotate(0deg);
    }
    to {
      transform: rotate(360deg);
    }
  }
</style>
