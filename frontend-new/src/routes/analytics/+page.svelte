<script lang="ts">
  import { onMount } from 'svelte';
  import { auth } from '$lib/stores/auth';
  import Fa from 'svelte-fa';
  import { 
    faChartBar, 
    faUsers, 
    faKey, 
    faSearch, 
    faServer,
    faDatabase,
    faClock,
    faArrowUp,
    faArrowDown
  } from '@fortawesome/free-solid-svg-icons';
  
  let authState: any = null;
  let loading = true;
  let analytics = {
    users: {
      total: 0,
      active: 0,
      adminCount: 0,
      recentLogins: 0
    },
    apiKeys: {
      total: 0,
      active: 0,
      totalRequests: 0,
      requestsToday: 0
    },
    services: {
      total: 0,
      active: 0,
      deprecated: 0,
      byType: {}
    },
    search: {
      totalQueries: 0,
      queriesThisWeek: 0,
      avgResponseTime: 0,
      topQueries: []
    },
    system: {
      uptime: '0 days',
      dbConnections: 0,
      memoryUsage: 0,
      cpuUsage: 0
    }
  };
  
  // Subscribe to auth state
  auth.subscribe(($auth) => {
    authState = $auth;
  });
  
  async function loadAnalytics() {
    try {
      loading = true;
      
      // In a real implementation, these would be API calls
      // For now, we'll simulate the data
      
      // Simulate API calls with mock data
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      analytics = {
        users: {
          total: 3,
          active: 3,
          adminCount: 2,
          recentLogins: 5
        },
        apiKeys: {
          total: 0,
          active: 0,
          totalRequests: 0,
          requestsToday: 0
        },
        services: {
          total: 33,
          active: 31,
          deprecated: 2,
          byType: {
            'API': 15,
            'Microservice': 8,
            'Agent': 5,
            'Legacy': 3,
            'ESB': 2
          }
        },
        search: {
          totalQueries: 127,
          queriesThisWeek: 23,
          avgResponseTime: 85,
          topQueries: [
            { query: 'customer management', count: 12 },
            { query: 'payment processing', count: 8 },
            { query: 'inventory tracking', count: 6 },
            { query: 'user authentication', count: 5 },
            { query: 'data analytics', count: 4 }
          ]
        },
        system: {
          uptime: '2 days, 14 hours',
          dbConnections: 12,
          memoryUsage: 68,
          cpuUsage: 23
        }
      };
      
    } catch (error) {
      console.error('Error loading analytics:', error);
    } finally {
      loading = false;
    }
  }
  
  onMount(async () => {
    // Ensure auth is initialized
    auth.init();
    
    // Wait a bit for auth to initialize
    await new Promise(resolve => setTimeout(resolve, 100));
    
    await loadAnalytics();
  });
  
  // Check if current user is admin
  $: isAdmin = authState?.user?.role === 'admin';
  $: canViewAnalytics = isAdmin || authState?.user?.role === 'editor';
</script>

<div class="max-w-7xl mx-auto p-6">
  <div class="mb-6">
    <h1 class="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
    <p class="mt-2 text-gray-600">System metrics and usage analytics</p>
  </div>
  
  <!-- Access Control -->
  {#if !canViewAnalytics}
    <div class="bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-3 rounded-lg mb-6">
      <p class="font-medium">Access Restricted</p>
      <p>You need admin or editor privileges to view analytics. Current role: {authState?.user?.role || 'unknown'}</p>
    </div>
  {:else}
    
    <!-- Loading State -->
    {#if loading}
      <div class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <p class="mt-4 text-gray-600">Loading analytics...</p>
      </div>
    {:else}
      
      <!-- Key Metrics Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <!-- Users Card -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <Fa icon={faUsers} class="text-blue-600 text-xl" />
              </div>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">Total Users</p>
              <p class="text-2xl font-bold text-gray-900">{analytics.users.total}</p>
              <p class="text-sm text-green-600">
                <Fa icon={faArrowUp} class="inline mr-1" />
                {analytics.users.active} active
              </p>
            </div>
          </div>
        </div>
        
        <!-- API Keys Card -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <Fa icon={faKey} class="text-green-600 text-xl" />
              </div>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">API Keys</p>
              <p class="text-2xl font-bold text-gray-900">{analytics.apiKeys.total}</p>
              <p class="text-sm text-gray-600">
                {analytics.apiKeys.active} active
              </p>
            </div>
          </div>
        </div>
        
        <!-- Services Card -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <Fa icon={faServer} class="text-purple-600 text-xl" />
              </div>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">Services</p>
              <p class="text-2xl font-bold text-gray-900">{analytics.services.total}</p>
              <p class="text-sm text-green-600">
                <Fa icon={faArrowUp} class="inline mr-1" />
                {analytics.services.active} active
              </p>
            </div>
          </div>
        </div>
        
        <!-- Search Queries Card -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                <Fa icon={faSearch} class="text-orange-600 text-xl" />
              </div>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">Search Queries</p>
              <p class="text-2xl font-bold text-gray-900">{analytics.search.totalQueries}</p>
              <p class="text-sm text-blue-600">
                {analytics.search.queriesThisWeek} this week
              </p>
            </div>
          </div>
        </div>
      </div>
      
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <!-- Service Types Distribution -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Service Distribution</h3>
          <div class="space-y-3">
            {#each Object.entries(analytics.services.byType) as [type, count]}
              <div class="flex items-center justify-between">
                <span class="text-sm font-medium text-gray-600">{type}</span>
                <div class="flex items-center">
                  <span class="text-sm font-bold text-gray-900 mr-2">{count}</span>
                  <div class="w-20 bg-gray-200 rounded-full h-2">
                    <div 
                      class="bg-blue-600 h-2 rounded-full" 
                      style="width: {(count / analytics.services.total) * 100}%"
                    ></div>
                  </div>
                </div>
              </div>
            {/each}
          </div>
        </div>
        
        <!-- Top Search Queries -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Top Search Queries</h3>
          <div class="space-y-3">
            {#each analytics.search.topQueries as query, index}
              <div class="flex items-center justify-between">
                <div class="flex items-center">
                  <span class="text-sm font-bold text-gray-400 mr-3">#{index + 1}</span>
                  <span class="text-sm text-gray-900">{query.query}</span>
                </div>
                <span class="text-sm font-bold text-blue-600">{query.count}</span>
              </div>
            {/each}
          </div>
        </div>
      </div>
      
      <!-- System Health -->
      <div class="bg-white rounded-lg shadow-md p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">
          <Fa icon={faDatabase} class="inline mr-2" />
          System Health
        </h3>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <!-- Uptime -->
          <div class="text-center">
            <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-2">
              <Fa icon={faClock} class="text-green-600 text-xl" />
            </div>
            <p class="text-sm font-medium text-gray-500">System Uptime</p>
            <p class="text-lg font-bold text-gray-900">{analytics.system.uptime}</p>
          </div>
          
          <!-- Database Connections -->
          <div class="text-center">
            <div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-2">
              <Fa icon={faDatabase} class="text-blue-600 text-xl" />
            </div>
            <p class="text-sm font-medium text-gray-500">DB Connections</p>
            <p class="text-lg font-bold text-gray-900">{analytics.system.dbConnections}</p>
          </div>
          
          <!-- Memory Usage -->
          <div class="text-center">
            <div class="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-2">
              <Fa icon={faChartBar} class="text-yellow-600 text-xl" />
            </div>
            <p class="text-sm font-medium text-gray-500">Memory Usage</p>
            <p class="text-lg font-bold text-gray-900">{analytics.system.memoryUsage}%</p>
            <div class="w-full bg-gray-200 rounded-full h-2 mt-2">
              <div 
                class="bg-yellow-600 h-2 rounded-full" 
                style="width: {analytics.system.memoryUsage}%"
              ></div>
            </div>
          </div>
          
          <!-- CPU Usage -->
          <div class="text-center">
            <div class="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-2">
              <Fa icon={faServer} class="text-red-600 text-xl" />
            </div>
            <p class="text-sm font-medium text-gray-500">CPU Usage</p>
            <p class="text-lg font-bold text-gray-900">{analytics.system.cpuUsage}%</p>
            <div class="w-full bg-gray-200 rounded-full h-2 mt-2">
              <div 
                class="bg-red-600 h-2 rounded-full" 
                style="width: {analytics.system.cpuUsage}%"
              ></div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Performance Metrics -->
      <div class="mt-6 bg-white rounded-lg shadow-md p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Performance Metrics</h3>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="text-center p-4 bg-gray-50 rounded-lg">
            <p class="text-2xl font-bold text-green-600">{analytics.search.avgResponseTime}ms</p>
            <p class="text-sm text-gray-600">Avg Search Response Time</p>
          </div>
          
          <div class="text-center p-4 bg-gray-50 rounded-lg">
            <p class="text-2xl font-bold text-blue-600">99.9%</p>
            <p class="text-sm text-gray-600">System Availability</p>
          </div>
          
          <div class="text-center p-4 bg-gray-50 rounded-lg">
            <p class="text-2xl font-bold text-purple-600">0</p>
            <p class="text-sm text-gray-600">Failed Requests (24h)</p>
          </div>
        </div>
      </div>
      
    {/if}
  {/if}
  
  <!-- Footer -->
  <div class="mt-8 text-center">
    <p class="text-sm text-gray-500">
      Analytics updated in real-time | 
      <a href="/" class="text-blue-600 hover:text-blue-800">Back to Dashboard</a>
    </p>
  </div>
</div>
