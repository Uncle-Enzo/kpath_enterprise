<script lang="ts">
  import { searchApi } from '$lib/api/search';
  import type { SearchRequest, SearchResult } from '$lib/types';
  import Fa from 'svelte-fa';
  import { faSearch, faClock, faServer } from '@fortawesome/free-solid-svg-icons';
  
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
    <div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
      {error}
    </div>
  {/if}
  
  {#if hasSearched && !loading}
    <div class="card">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold">
          Results ({results.length})
        </h2>
        <div class="flex items-center text-sm text-gray-600">
          <Fa icon={faClock} class="mr-1" />
          {searchTime}ms
        </div>
      </div>
      
      {#if results.length === 0}
        <p class="text-gray-500 text-center py-8">No results found</p>
      {:else}
        <div class="space-y-4">
          {#each results as result}
            <div class="border rounded-lg p-4 hover:shadow-md transition-shadow">
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <div class="flex items-center">
                    <Fa icon={faServer} class="mr-2 text-gray-400" />
                    <h3 class="font-semibold text-lg">{result.service.name}</h3>
                    <span class="ml-3 px-2 py-1 bg-primary-100 text-primary-700 text-xs rounded-full">
                      Score: {result.score.toFixed(3)}
                    </span>
                  </div>
                  <p class="text-gray-600 mt-1">{result.service.description}</p>
                  
                  {#if result.service.domains && result.service.domains.length > 0}
                    <div class="mt-2 flex flex-wrap gap-1">
                      {#each result.service.domains as domain}
                        <span class="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
                          {domain}
                        </span>
                      {/each}
                    </div>
                  {/if}
                  
                  {#if result.service.endpoint}
                    <p class="text-sm text-gray-500 mt-2">
                      Endpoint: <code class="bg-gray-100 px-1 rounded">{result.service.endpoint}</code>
                    </p>
                  {/if}
                </div>
                <div class="ml-4 text-right">
                  <p class="text-sm text-gray-500">Rank #{result.rank}</p>
                </div>
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </div>
  {/if}
</div>
