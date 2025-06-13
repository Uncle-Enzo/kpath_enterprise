<script lang="ts">
  import { searchApi } from '$lib/api/search';
  import type { SearchRequest, SearchResult } from '$lib/types';
  import Fa from 'svelte-fa';
  import { faSearch, faClock, faServer, faRobot, faCog, faEye, faExclamationTriangle } from '@fortawesome/free-solid-svg-icons';
  
  let searchRequest: SearchRequest = {
    query: '',
    limit: 10,
    min_score: 0.0,
    domains: [],
    capabilities: []
  };
  
  let results: SearchResult[] = [];
  let loading = false;
  let error = '';
  let searchTime = 0;
  let hasSearched = false;
  
  async function performSearch() {
    if (!searchRequest.query.trim()) return;
    
    loading = true;
    error = '';
    hasSearched = true;
    
    const startTime = Date.now();
    
    try {
      const response = await searchApi.search(searchRequest);
      results = response.results;
      searchTime = Date.now() - startTime;
    } catch (err: any) {
      error = err.response?.data?.detail || 'Search failed';
      results = [];
    } finally {
      loading = false;
    }
  }
  
  function handleKeyPress(e: KeyboardEvent) {
    if (e.key === 'Enter') {
      performSearch();
    }
  }
  
  function getToolTypeIcon(toolType: string) {
    switch (toolType) {
      case 'InternalAgent':
      case 'ExternalAgent':
        return faRobot;
      case 'API':
      case 'MicroService':
        return faServer;
      default:
        return faCog;
    }
  }
  
  function getToolTypeColor(toolType: string) {
    switch (toolType) {
      case 'InternalAgent':
        return 'text-blue-600';
      case 'ExternalAgent':
        return 'text-purple-600';
      case 'API':
        return 'text-green-600';
      case 'ESBEndpoint':
        return 'text-orange-600';
      case 'LegacySystem':
        return 'text-gray-600';
      case 'MicroService':
        return 'text-indigo-600';
      default:
        return 'text-gray-600';
    }
  }
</script>

<div class="max-w-6xl mx-auto space-y-6">
  <div>
    <h1 class="text-2xl font-bold text-gray-900">Search Testing</h1>
    <p class="text-gray-600">Test the semantic search functionality</p>
  </div>
  
  <!-- Search Form -->
  <div class="card">
    <div class="space-y-4">
      <div class="relative">
        <Fa icon={faSearch} class="absolute left-3 top-3 text-gray-400" />
        <input
          type="text"
          bind:value={searchRequest.query}
          on:keypress={handleKeyPress}
          placeholder="Enter your search query..."
          class="input pl-10 text-lg"
        />
      </div>
      
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Max Results
          </label>
          <input
            type="number"
            bind:value={searchRequest.limit}
            min="1"
            max="100"
            class="input"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Min Score
          </label>
          <input
            type="number"
            bind:value={searchRequest.min_score}
            min="0"
            max="1"
            step="0.1"
            class="input"
          />
        </div>
        
        <div class="flex items-end">
          <button
            on:click={performSearch}
            disabled={loading || !searchRequest.query}
            class="btn btn-primary w-full"
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>
      </div>
    </div>
  </div>
  
  <!-- Results -->
  {#if error}
    <div class="card bg-red-50 border-red-200">
      <p class="text-red-700">{error}</p>
    </div>
  {/if}
  
  {#if hasSearched && !loading}
    <div class="card">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-lg font-semibold">
          {results.length} Result{results.length !== 1 ? 's' : ''} Found
        </h2>
        <div class="flex items-center text-sm text-gray-500">
          <Fa icon={faClock} class="mr-1" />
          {searchTime}ms
        </div>
      </div>
      
      {#if results.length === 0}
        <p class="text-gray-500">No services found matching your query.</p>
      {:else}
        <div class="space-y-4">
          {#each results as result, i}
            <div class="border rounded-lg p-4 hover:shadow-md transition-shadow">
              <div class="flex justify-between items-start mb-2">
                <div class="flex-1">
                  <div class="flex items-center space-x-3">
                    <h3 class="text-lg font-semibold text-gray-900">
                      {result.service.name}
                    </h3>
                    <div class="flex items-center space-x-2">
                      <Fa 
                        icon={getToolTypeIcon(result.service.tool_type)} 
                        class="{getToolTypeColor(result.service.tool_type)} text-sm" 
                        title={result.service.tool_type}
                      />
                      <span class="text-xs px-2 py-1 bg-gray-100 rounded">
                        {result.service.tool_type}
                      </span>
                    </div>
                    {#if result.service.status === 'deprecated'}
                      <span class="text-xs px-2 py-1 bg-red-100 text-red-800 rounded flex items-center">
                        <Fa icon={faExclamationTriangle} class="mr-1" />
                        Deprecated
                      </span>
                    {/if}
                  </div>
                  {#if result.service.version}
                    <span class="text-sm text-gray-500">v{result.service.version}</span>
                  {/if}
                </div>
                <div class="flex items-center space-x-3 text-sm">
                  <div class="flex items-center text-gray-500">
                    <Fa icon={faEye} class="mr-1" />
                    {result.service.visibility}
                  </div>
                  <div class="text-primary-600 font-medium">
                    Score: {result.score.toFixed(3)}
                  </div>
                </div>
              </div>
              
              <p class="text-gray-600 mb-3">{result.service.description}</p>
              
              <div class="flex flex-wrap gap-2">
                {#if result.service.interaction_modes && result.service.interaction_modes.length > 0}
                  <div class="flex items-center space-x-2">
                    <span class="text-xs text-gray-500">Modes:</span>
                    {#each result.service.interaction_modes as mode}
                      <span class="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded">
                        {mode}
                      </span>
                    {/each}
                  </div>
                {/if}
                
                {#if result.service.endpoint}
                  <div class="text-xs text-gray-500">
                    Endpoint: <code class="bg-gray-100 px-1 rounded">{result.service.endpoint}</code>
                  </div>
                {/if}
              </div>
              
              <div class="mt-3 flex justify-between items-center">
                <span class="text-xs text-gray-400">
                  Rank #{i + 1} | Distance: {result.distance?.toFixed(4) || 'N/A'}
                </span>
                <a href="/services/{result.service.id}" class="text-sm text-primary-600 hover:text-primary-800">
                  View Details →
                </a>
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </div>
  {/if}
</div>
