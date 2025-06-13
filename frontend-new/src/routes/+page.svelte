<script lang="ts">
  import { onMount } from 'svelte';
  import { currentUser } from '$lib/stores/auth';
  import Fa from 'svelte-fa';
  import { 
    faServer, 
    faUsers, 
    faKey, 
    faSearch,
    faChartLine,
    faClock
  } from '@fortawesome/free-solid-svg-icons';
  
  // Dashboard stats (would be fetched from API)
  let stats = {
    totalServices: 0,
    activeServices: 0,
    totalUsers: 0,
    apiKeys: 0,
    searchesToday: 0,
    avgResponseTime: 0
  };
  
  let recentActivity: any[] = [];
  
  onMount(async () => {
    // TODO: Fetch actual stats from API
    stats = {
      totalServices: 42,
      activeServices: 38,
      totalUsers: 15,
      apiKeys: 23,
      searchesToday: 156,
      avgResponseTime: 87
    };
  });
</script>

<div class="space-y-6">
  <div>
    <h1 class="text-2xl font-bold text-gray-900">Dashboard</h1>
    <p class="text-gray-600">Welcome back, {$currentUser?.username || 'User'}!</p>
  </div>
  
  <!-- Stats Grid -->
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    <div class="card">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm text-gray-600">Total Services</p>
          <p class="text-2xl font-bold text-gray-900">{stats.totalServices}</p>
          <p class="text-sm text-green-600">
            {stats.activeServices} active
          </p>
        </div>
        <Fa icon={faServer} class="text-3xl text-primary-500" />
      </div>
    </div>
    
    <div class="card">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm text-gray-600">Total Users</p>
          <p class="text-2xl font-bold text-gray-900">{stats.totalUsers}</p>
        </div>
        <Fa icon={faUsers} class="text-3xl text-green-500" />
      </div>
    </div>
    
    <div class="card">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm text-gray-600">API Keys</p>
          <p class="text-2xl font-bold text-gray-900">{stats.apiKeys}</p>
        </div>
        <Fa icon={faKey} class="text-3xl text-yellow-500" />
      </div>
    </div>
    
    <div class="card">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm text-gray-600">Searches Today</p>
          <p class="text-2xl font-bold text-gray-900">{stats.searchesToday}</p>
        </div>
        <Fa icon={faSearch} class="text-3xl text-purple-500" />
      </div>
    </div>
    
    <div class="card">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm text-gray-600">Avg Response Time</p>
          <p class="text-2xl font-bold text-gray-900">{stats.avgResponseTime}ms</p>
        </div>
        <Fa icon={faClock} class="text-3xl text-blue-500" />
      </div>
    </div>
    
    <div class="card">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm text-gray-600">System Health</p>
          <p class="text-2xl font-bold text-green-600">Healthy</p>
        </div>
        <Fa icon={faChartLine} class="text-3xl text-green-500" />
      </div>
    </div>
  </div>
  
  <!-- Quick Actions -->
  <div class="card">
    <h2 class="text-lg font-semibold mb-4">Quick Actions</h2>
    <div class="flex flex-wrap gap-2">
      <a href="/services/new" class="btn btn-primary">Add Service</a>
      <a href="/search" class="btn btn-secondary">Test Search</a>
      <a href="/api-keys/new" class="btn btn-secondary">Generate API Key</a>
    </div>
  </div>
</div>
