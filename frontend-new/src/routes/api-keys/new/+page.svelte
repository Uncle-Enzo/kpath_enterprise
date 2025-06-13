<script lang="ts">
  import { apiKeysApi } from '$lib/api/apiKeys';
  import { goto } from '$app/navigation';
  import type { APIKeyCreate } from '$lib/types';
  import Fa from 'svelte-fa';
  import { faCopy, faCheck } from '@fortawesome/free-solid-svg-icons';
  
  let form: APIKeyCreate = {
    name: '',
    permissions: { search: true },
    rate_limit: 1000
  };
  
  let loading = false;
  let error = '';
  let generatedKey: string | null = null;
  let copied = false;
  
  async function generateKey() {
    loading = true;
    error = '';
    
    try {
      const response = await apiKeysApi.create(form);
      generatedKey = response.api_key;
    } catch (err: any) {
      error = err.response?.data?.detail || 'Failed to generate API key';
    } finally {
      loading = false;
    }
  }
  
  function copyToClipboard() {
    if (generatedKey) {
      navigator.clipboard.writeText(generatedKey);
      copied = true;
      setTimeout(() => copied = false, 2000);
    }
  }
  
  function done() {
    goto('/api-keys');
  }
</script>

<div class="max-w-2xl mx-auto space-y-6">
  <h1 class="text-2xl font-bold text-gray-900">Generate New API Key</h1>
  
  {#if !generatedKey}
    <form on:submit|preventDefault={generateKey} class="bg-white rounded-lg shadow-md p-6 space-y-4">
      {#if error}
        <div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      {/if}
      
      <div>
        <label for="name" class="block text-sm font-medium text-gray-700">
          Key Name *
        </label>
        <input
          id="name"
          type="text"
          bind:value={form.name}
          required
          class="input mt-1"
          placeholder="e.g., Production Server"
        />
        <p class="mt-1 text-sm text-gray-500">
          A descriptive name to identify this API key
        </p>
      </div>
      
      <div>
        <label for="rate_limit" class="block text-sm font-medium text-gray-700">
          Rate Limit (requests per hour)
        </label>
        <input
          id="rate_limit"
          type="number"
          bind:value={form.rate_limit}
          min="1"
          max="10000"
          class="input mt-1"
        />
      </div>
      
      <div>
        <label for="expires_in_days" class="block text-sm font-medium text-gray-700">
          Expiration (days)
        </label>
        <input
          id="expires_in_days"
          type="number"
          bind:value={form.expires_in_days}
          min="1"
          max="365"
          class="input mt-1"
          placeholder="Leave empty for no expiration"
        />
      </div>
      
      <div class="pt-4">
        <button
          type="submit"
          disabled={loading || !form.name}
          class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium disabled:opacity-50"
        >
          {loading ? 'Generating...' : 'Generate API Key'}
        </button>
      </div>
    </form>
  {:else}
    <div class="bg-white rounded-lg shadow-md p-6">
      <div class="text-center space-y-4">
        <div class="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full">
          <Fa icon={faCheck} class="text-2xl text-green-600" />
        </div>
        
        <h2 class="text-xl font-semibold">API Key Generated Successfully!</h2>
        
        <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p class="text-sm text-yellow-800 font-medium mb-2">
            ⚠️ Important: Copy your API key now
          </p>
          <p class="text-sm text-yellow-700">
            This is the only time you'll see this key. It cannot be retrieved later.
          </p>
        </div>
        
        <div class="relative">
          <div class="bg-gray-100 rounded-lg p-4 font-mono text-sm break-all">
            {generatedKey}
          </div>
          <button
            on:click={copyToClipboard}
            class="absolute top-2 right-2 btn btn-secondary btn-sm"
          >
            <Fa icon={copied ? faCheck : faCopy} class="mr-1" />
            {copied ? 'Copied!' : 'Copy'}
          </button>
        </div>
        
        <div class="pt-4">
          <button on:click={done} class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium">
            Done
          </button>
        </div>
      </div>
    </div>
  {/if}
</div>
