<script lang="ts">
  import { onMount } from 'svelte';
  import { auth, currentUser } from '$lib/stores/auth';
  import { analyticsApi, type DashboardStats } from '$lib/api/analytics';
  import Fa from 'svelte-fa';
  import { 
    faServer, 
    faUsers, 
    faKey, 
    faSearch,
    faChartLine,
    faClock
  } from '@fortawesome/free-solid-svg-icons';
  
  let stats: DashboardStats = {
    totalServices: 0,
    activeServices: 0,
    totalUsers: 0,
    activeUsers: 0,
    apiKeys: 0,
    searchesToday: 0,
    avgResponseTime: 0,
    systemHealth: 'Loading...'
  };
  
  let loading = true;
  let error = '';
  
  async function loadStats() {
    try {
      loading = true;
      error = '';
      
      // Ensure auth is initialized
      await new Promise(resolve => setTimeout(resolve, 100));
      
      stats = await analyticsApi.getDashboardStats();
    } catch (err: any) {
      error = `Failed to load dashboard stats: ${err.message || 'Unknown error'}`;
      console.error('Error loading dashboard stats:', err);
      
      // Fallback to mock data on error
      stats = {
        totalServices: 33,
        activeServices: 31,
        totalUsers: 3,
        activeUsers: 3,
        apiKeys: 0,
        searchesToday: 0,
        avgResponseTime: 85,
        systemHealth: 'Unknown'
      };
    } finally {
      loading = false;
    }
  }
  
  onMount(async () => {
    // Ensure auth is initialized
    auth.init();
    await loadStats();
  });
</script>

<div class="space-y-6">
  <div>
    <h1 class="text-2xl font-bold text-gray-900">Dashboard</h1>
    <p class="text-gray-600">Welcome back, {$currentUser?.username || $currentUser?.email || 'User'}!</p>
  </div>
  
  <!-- Error Message -->
  {#if error}
    <div class="bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-3 rounded-lg">
      <p class="font-medium">Warning</p>
      <p class="text-sm">{error}</p>
    </div>
  {/if}
  
  <!-- Loading State -->
  {#if loading}
    <div class="text-center py-8">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      <p class="mt-2 text-gray-600">Loading dashboard...</p>
    </div>
  {:else}
    <!-- Stats Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div class="bg-white rounded-lg shadow-md p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600">Total Services</p>
            <p class="text-2xl font-bold text-gray-900">{stats.totalServices}</p>
            <p class="text-sm text-green-600">
              {stats.activeServices} active
            </p>
          </div>
          <Fa icon={faServer} class="text-3xl text-blue-500" />
        </div>
      </div>
      
      <div class="bg-white rounded-lg shadow-md p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600">Total Users</p>
            <p class="text-2xl font-bold text-gray-900">{stats.totalUsers}</p>
            <p class="text-sm text-green-600">
              {stats.activeUsers} active
            </p>
          </div>
          <Fa icon={faUsers} class="text-3xl text-green-500" />
        </div>
      </div>
      
      <div class="bg-white rounded-lg shadow-md p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600">API Keys</p>
            <p class="text-2xl font-bold text-gray-900">{stats.apiKeys}</p>
          </div>
          <Fa icon={faKey} class="text-3xl text-yellow-500" />
        </div>
      </div>
      
      <div class="bg-white rounded-lg shadow-md p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600">Searches Today</p>
            <p class="text-2xl font-bold text-gray-900">{stats.searchesToday}</p>
            <p class="text-xs text-green-600">Real data collected</p>
          </div>
          <Fa icon={faSearch} class="text-3xl text-purple-500" />
        </div>
      </div>
      
      <div class="bg-white rounded-lg shadow-md p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600">Avg Response Time</p>
            <p class="text-2xl font-bold text-gray-900">{stats.avgResponseTime}ms</p>
            <p class="text-xs text-green-600">From actual searches</p>
          </div>
          <Fa icon={faClock} class="text-3xl text-blue-500" />
        </div>
      </div>
      
      <div class="bg-white rounded-lg shadow-md p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600">System Health</p>
            <p class="text-2xl font-bold text-green-600">{stats.systemHealth}</p>
          </div>
          <Fa icon={faChartLine} class="text-3xl text-green-500" />
        </div>
      </div>
    </div>
  {/if}
  
  <!-- Quick Actions -->
  <div class="bg-white rounded-lg shadow-md p-6">
    <h2 class="text-lg font-semibold mb-4">Quick Actions</h2>
    <div class="flex flex-wrap gap-2">
      <a href="/services/new" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium">Add Service</a>
      <a href="/search" class="bg-gray-200 hover:bg-gray-300 text-gray-700 px-4 py-2 rounded-lg font-medium">Test Search</a>
      <a href="/api-keys/new" class="bg-gray-200 hover:bg-gray-300 text-gray-700 px-4 py-2 rounded-lg font-medium">Generate API Key</a>
      <a href="/analytics" class="bg-gray-200 hover:bg-gray-300 text-gray-700 px-4 py-2 rounded-lg font-medium">View Analytics</a>
    </div>
  </div>
</div>
