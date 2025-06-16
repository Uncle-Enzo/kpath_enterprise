<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import Fa from 'svelte-fa';
  import { 
    faKey, 
    faChartBar, 
    faArrowLeft, 
    faSpinner,
    faExclamationTriangle,
    faCheckCircle,
    faTimesCircle,
    faClock,
    faCalendarDay,
    faCalendarWeek,
    faServer,
    faRobot
  } from '@fortawesome/free-solid-svg-icons';
  import { apiKeysApi } from '$lib/api/apiKeys';
  import { api } from '$lib/api/client';

  let keyId: string;
  let apiKeyInfo: any = null;
  let usageStats: any = null;
  let loading = false; // Initialize as false, will be set to true when loading starts
  let error = '';
  let days = 7; // Default to last 7 days
  let isInitialized = false; // Prevent multiple simultaneous calls

  $: keyId = $page.params.id;

  onMount(async () => {
    console.log('🔵 [MOUNT] API Key Usage page mounted');
    console.log('🔵 [MOUNT] keyId from params:', $page.params.id);
    console.log('🔵 [MOUNT] isInitialized:', isInitialized);
    
    if (!isInitialized) {
      isInitialized = true;
      console.log('🔵 [MOUNT] Starting loadApiKeyUsage...');
      await loadApiKeyUsage();
    } else {
      console.log('🔵 [MOUNT] Already initialized, skipping load');
    }
  });

  async function loadApiKeyUsage() {
    console.log('🟡 [LOAD] === Starting loadApiKeyUsage ===');
    console.log('🟡 [LOAD] keyId:', keyId, 'loading:', loading);
    
    if (!keyId) {
      console.log('🔴 [LOAD] No keyId found, returning');
      return;
    }
    
    if (loading) {
      console.log('🔴 [LOAD] Already loading, returning');
      return;
    }
    
    console.log('🟡 [LOAD] Setting loading = true, clearing error');
    loading = true;
    error = '';
    
    try {
      // Get API key info using the proper API client
      console.log('🟢 [API] Fetching API key info for keyId:', keyId);
      console.log('🟢 [API] Request URL: /api-keys/' + keyId);
      
      const startTime1 = Date.now();
      apiKeyInfo = await api.get(`/api-keys/${keyId}`);
      const endTime1 = Date.now();
      
      console.log('🟢 [API] API key info received in', (endTime1 - startTime1) + 'ms:', apiKeyInfo);
      
      // Get usage statistics using the proper API client
      console.log('🟢 [API] Fetching usage stats for keyId:', keyId, 'days:', days);
      console.log('🟢 [API] Usage request - keyId type:', typeof keyId, 'parsed:', parseInt(keyId));
      
      const startTime2 = Date.now();
      usageStats = await apiKeysApi.getUsage(parseInt(keyId), days);
      const endTime2 = Date.now();
      
      console.log('🟢 [API] Usage stats received in', (endTime2 - startTime2) + 'ms:', usageStats);
      
    } catch (err: any) {
      console.error('🔴 [ERROR] === API ERROR ===');
      console.error('🔴 [ERROR] Error object:', err);
      console.error('🔴 [ERROR] Error message:', err.message);
      console.error('🔴 [ERROR] Error response:', err.response);
      console.error('🔴 [ERROR] Error response data:', err.response?.data);
      console.error('🔴 [ERROR] Error status:', err.response?.status);
      console.error('🔴 [ERROR] Error stack:', err.stack);
      
      error = err.response?.data?.detail || err.message || 'Failed to load API key usage data';
      console.error('🔴 [ERROR] Final error message set:', error);
    } finally {
      console.log('🟡 [LOAD] === Finishing loadApiKeyUsage ===');
      console.log('🟡 [LOAD] Setting loading = false');
      console.log('🟡 [LOAD] Final state - apiKeyInfo:', !!apiKeyInfo, 'usageStats:', !!usageStats, 'error:', error);
      loading = false;
    }
  }

  function goBack() {
    goto('/api-keys');
  }

  function formatDate(dateString: string) {
    return new Date(dateString).toLocaleDateString();
  }

  function formatDateTime(dateString: string) {
    return new Date(dateString).toLocaleString();
  }

  // Handle days filter change
  async function handleDaysChange() {
    if (!loading) {
      await loadApiKeyUsage();
    }
  }
</script>

<svelte:head>
  <title>API Key Usage - KPATH Enterprise</title>
</svelte:head>

<div class="max-w-6xl mx-auto space-y-6">
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
          API Key Usage Statistics
        </h1>
        {#if apiKeyInfo}
          <p class="text-sm text-gray-600 mt-1">
            {apiKeyInfo.name} • ID: {keyId}
          </p>
        {/if}
      </div>
    </div>
    
    <!-- Time Range Filter -->
    <div class="flex items-center space-x-2">
      <label for="days" class="text-sm font-medium text-gray-700">Last:</label>
      <select 
        id="days" 
        bind:value={days}
        on:change={handleDaysChange}
        class="rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 text-sm"
      >
        <option value={1}>24 hours</option>
        <option value={7}>7 days</option>
        <option value={30}>30 days</option>
        <option value={90}>90 days</option>
      </select>
    </div>
  </div>

  {#if loading}
    <div class="flex items-center justify-center py-12">
      <Fa icon={faSpinner} class="text-2xl text-primary-600 animate-spin mr-3" />
      <span class="text-gray-600">Loading API key usage statistics...</span>
    </div>
  {:else if error}
    <div class="bg-red-50 border border-red-200 rounded-lg p-4">
      <div class="flex items-center">
        <Fa icon={faExclamationTriangle} class="text-red-600 mr-2" />
        <h3 class="text-red-900 font-medium">Error Loading Data</h3>
      </div>
      <p class="text-red-800 text-sm mt-2">{error}</p>
      <button 
        on:click={loadApiKeyUsage}
        class="mt-3 btn btn-secondary btn-sm"
      >
        Try Again
      </button>
    </div>
  {:else if usageStats}
    <!-- API Key Info Card -->
    {#if apiKeyInfo}
      <div class="card">
        <h2 class="text-lg font-semibold mb-4">API Key Information</h2>
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div class="text-center p-3 bg-gray-50 rounded-lg">
            <div class="text-sm text-gray-600">Name</div>
            <div class="font-medium">{apiKeyInfo.name}</div>
          </div>
          <div class="text-center p-3 bg-gray-50 rounded-lg">
            <div class="text-sm text-gray-600">Status</div>
            <div class="font-medium flex items-center justify-center">
              {#if apiKeyInfo.is_active}
                <Fa icon={faCheckCircle} class="text-green-600 mr-1" />
                Active
              {:else}
                <Fa icon={faTimesCircle} class="text-red-600 mr-1" />
                Inactive
              {/if}
            </div>
          </div>
          <div class="text-center p-3 bg-gray-50 rounded-lg">
            <div class="text-sm text-gray-600">Created</div>
            <div class="font-medium">{formatDate(apiKeyInfo.created_at)}</div>
          </div>
          <div class="text-center p-3 bg-gray-50 rounded-lg">
            <div class="text-sm text-gray-600">Last Used</div>
            <div class="font-medium">
              {apiKeyInfo.last_used_at ? formatDateTime(apiKeyInfo.last_used_at) : 'Never'}
            </div>
          </div>
        </div>
      </div>
    {/if}

    <!-- Usage Overview -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <div class="card text-center">
        <div class="text-3xl font-bold text-blue-600">{usageStats.total_requests || 0}</div>
        <div class="text-sm text-gray-600 mt-1">Total Requests</div>
        <div class="text-xs text-gray-500 mt-1">Last {days} days</div>
      </div>
      
      <div class="card text-center">
        <div class="text-3xl font-bold text-green-600">{usageStats.requests_last_hour || 0}</div>
        <div class="text-sm text-gray-600 mt-1">Requests (Last Hour)</div>
        <div class="text-xs text-gray-500 mt-1">
          <Fa icon={faClock} class="mr-1" />
          Real-time
        </div>
      </div>
      
      <div class="card text-center">
        <div class="text-3xl font-bold text-purple-600">{usageStats.requests_today || 0}</div>
        <div class="text-sm text-gray-600 mt-1">Requests Today</div>
        <div class="text-xs text-gray-500 mt-1">
          <Fa icon={faCalendarDay} class="mr-1" />
          {formatDate(new Date().toISOString())}
        </div>
      </div>
      
      <div class="card text-center">
        <div class="text-3xl font-bold text-orange-600">{usageStats.endpoints_used?.length || 0}</div>
        <div class="text-sm text-gray-600 mt-1">Unique Endpoints</div>
        <div class="text-xs text-gray-500 mt-1">
          <Fa icon={faServer} class="mr-1" />
          Diversity
        </div>
      </div>
    </div>

    <!-- Rate Limit Information -->
    {#if usageStats.rate_limit}
      <div class="card">
        <h2 class="text-lg font-semibold mb-4">Rate Limit Status</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="text-center p-3 bg-blue-50 rounded-lg">
            <div class="text-sm text-blue-600">Requests Per Hour</div>
            <div class="font-medium text-blue-900">
              {usageStats.requests_last_hour || 0} / {usageStats.rate_limit || 'Unlimited'}
            </div>
          </div>
          <div class="text-center p-3 bg-green-50 rounded-lg">
            <div class="text-sm text-green-600">Requests Per Day</div>
            <div class="font-medium text-green-900">
              {usageStats.requests_today || 0} / {(usageStats.rate_limit || 1000) * 24}
            </div>
          </div>
          <div class="text-center p-3 bg-purple-50 rounded-lg">
            <div class="text-sm text-purple-600">Status</div>
            <div class="font-medium text-purple-900">
              {(usageStats.requests_last_hour || 0) > (usageStats.rate_limit || 1000) ? 'Throttled' : 'Normal'}
            </div>
          </div>
        </div>
      </div>
    {/if}

    <!-- Endpoint Usage Breakdown -->
    {#if usageStats.endpoints_used && usageStats.endpoints_used.length > 0}
      <div class="card">
        <h2 class="text-lg font-semibold mb-4">Endpoint Usage Breakdown</h2>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Endpoint</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Method</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Requests</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Avg Response Time</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Last Used</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              {#each usageStats.endpoints_used as endpoint}
                <tr>
                  <td class="px-4 py-3 text-sm font-mono text-gray-900">{endpoint.endpoint}</td>
                  <td class="px-4 py-3 text-sm text-gray-900">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      {endpoint.method}
                    </span>
                  </td>
                  <td class="px-4 py-3 text-sm text-gray-900">{endpoint.count}</td>
                  <td class="px-4 py-3 text-sm text-gray-900">
                    {endpoint.avg_response_time_ms ? `${Math.round(endpoint.avg_response_time_ms)}ms` : 'N/A'}
                  </td>
                  <td class="px-4 py-3 text-sm text-gray-900">
                    {endpoint.last_used ? formatDateTime(endpoint.last_used) : 'N/A'}
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      </div>
    {/if}

    <!-- Daily Usage Pattern -->
    {#if usageStats.daily_usage && usageStats.daily_usage.length > 0}
      <div class="card">
        <h2 class="text-lg font-semibold mb-4">Daily Usage Pattern</h2>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Requests</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Avg Response Time</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Unique Endpoints</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              {#each usageStats.daily_usage as day}
                <tr>
                  <td class="px-4 py-3 text-sm text-gray-900">{formatDate(day.date)}</td>
                  <td class="px-4 py-3 text-sm text-gray-900">{day.requests}</td>
                  <td class="px-4 py-3 text-sm text-gray-900">
                    {day.avg_response_time_ms ? `${Math.round(day.avg_response_time_ms)}ms` : 'N/A'}
                  </td>
                  <td class="px-4 py-3 text-sm text-gray-900">
                    {day.unique_endpoints || 0}
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      </div>
    {/if}

    <!-- No Data Message -->
    {#if (!usageStats.total_requests || usageStats.total_requests === 0)}
      <div class="card text-center py-12">
        <Fa icon={faChartBar} class="text-4xl text-gray-400 mb-4" />
        <h3 class="text-lg font-medium text-gray-900 mb-2">No Usage Data</h3>
        <p class="text-gray-600">
          This API key hasn't been used in the last {days} days.
        </p>
        <p class="text-sm text-gray-500 mt-2">
          Start making API requests to see usage statistics here.
        </p>
      </div>
    {/if}
  {/if}
</div>

<style>
  .card {
    @apply bg-white shadow-sm border border-gray-200 rounded-lg p-6;
  }
  
  .btn {
    @apply inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2;
  }
  
  .btn-secondary {
    @apply text-gray-700 bg-white border-gray-300 hover:bg-gray-50 focus:ring-primary-500;
  }
  
  .btn-sm {
    @apply px-3 py-1.5 text-xs;
  }
</style>
