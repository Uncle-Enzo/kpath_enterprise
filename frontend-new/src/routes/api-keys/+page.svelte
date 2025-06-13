<script lang="ts">
  import { onMount } from 'svelte';
  import { apiKeysApi } from '$lib/api/apiKeys';
  import type { APIKey } from '$lib/types';
  import { format } from 'date-fns';
  import Fa from 'svelte-fa';
  import { faPlus, faTrash, faKey, faCopy } from '@fortawesome/free-solid-svg-icons';
  
  let apiKeys: APIKey[] = [];
  let loading = true;
  let error = '';
  let showCreateModal = false;
  let newKeyData: any = null;
  
  async function loadApiKeys() {
    try {
      loading = true;
      apiKeys = await apiKeysApi.list();
    } catch (err: any) {
      error = 'Failed to load API keys';
    } finally {
      loading = false;
    }
  }
  
  async function revokeKey(keyId: number) {
    if (!confirm('Are you sure you want to revoke this API key? This action cannot be undone.')) return;
    
    try {
      await apiKeysApi.revoke(keyId);
      await loadApiKeys();
    } catch (err) {
      alert('Failed to revoke API key');
    }
  }
  
  function copyToClipboard(text: string) {
    navigator.clipboard.writeText(text);
    alert('Copied to clipboard!');
  }
  
  onMount(loadApiKeys);
</script>

<div class="space-y-6">
  <div class="flex justify-between items-center">
    <h1 class="text-2xl font-bold text-gray-900">API Keys</h1>
    <a href="/api-keys/new" class="btn btn-primary">
      <Fa icon={faPlus} class="mr-2" />
      Generate New Key
    </a>
  </div>
  
  <div class="card">
    <p class="text-sm text-gray-600 mb-4">
      API keys allow programmatic access to the KPath Enterprise API. Keep your keys secure and never share them publicly.
    </p>
    
    {#if loading}
      <div class="text-center py-8">
        <p class="text-gray-500">Loading API keys...</p>
      </div>
    {:else if error}
      <div class="text-center py-8">
        <p class="text-red-500">{error}</p>
      </div>
    {:else if apiKeys.length === 0}
      <div class="text-center py-8">
        <Fa icon={faKey} class="text-4xl text-gray-300 mb-3" />
        <p class="text-gray-500">No API keys yet</p>
        <p class="text-sm text-gray-400 mt-1">Generate your first API key to get started</p>
      </div>
    {:else}
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead>
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Name
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Key Prefix
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Created
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Last Used
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            {#each apiKeys as key}
              <tr>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm font-medium text-gray-900">{key.name}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <code class="text-sm bg-gray-100 px-2 py-1 rounded">{key.prefix}...</code>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {format(new Date(key.created_at), 'MMM d, yyyy')}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {key.last_used ? format(new Date(key.last_used), 'MMM d, yyyy') : 'Never'}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full {key.active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}">
                    {key.active ? 'Active' : 'Revoked'}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <a href="/api-keys/{key.id}/usage" class="text-primary-600 hover:text-primary-900 mr-3">
                    View Usage
                  </a>
                  {#if key.active}
                    <button on:click={() => revokeKey(key.id)} class="text-red-600 hover:text-red-900">
                      <Fa icon={faTrash} />
                    </button>
                  {/if}
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}
  </div>
</div>
