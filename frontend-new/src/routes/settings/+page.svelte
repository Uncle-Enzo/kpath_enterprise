<script lang="ts">
  import { onMount } from 'svelte';
  import { auth } from '$lib/stores/auth';
  import Fa from 'svelte-fa';
  import { 
    faCog, 
    faDatabase, 
    faSearch, 
    faShield, 
    faBell,
    faServer,
    faSave,
    faRedo,
    faExclamationTriangle
  } from '@fortawesome/free-solid-svg-icons';
  
  let authState: any = null;
  let loading = false;
  let saveSuccess = false;
  let saveError = '';
  
  // Settings data structure
  let settings = {
    system: {
      siteName: 'KPATH Enterprise',
      maintenanceMode: false,
      debugMode: false,
      logLevel: 'info'
    },
    database: {
      connectionTimeout: 30,
      maxConnections: 100,
      queryTimeout: 30,
      backupEnabled: true,
      backupRetention: 30
    },
    search: {
      maxResults: 50,
      searchTimeout: 5000,
      enableCache: true,
      cacheExpiration: 3600,
      minQueryLength: 2
    },
    security: {
      jwtExpirationHours: 24,
      maxLoginAttempts: 5,
      lockoutDuration: 15,
      passwordMinLength: 8,
      requireMfa: false
    },
    notifications: {
      emailNotifications: true,
      systemAlerts: true,
      maintenanceNotices: true,
      securityAlerts: true
    },
    api: {
      rateLimitEnabled: true,
      defaultRateLimit: 1000,
      maxRequestSize: 10,
      enableCors: true,
      corsOrigins: '*'
    }
  };
  
  // Subscribe to auth state
  auth.subscribe(($auth) => {
    authState = $auth;
  });
  
  async function loadSettings() {
    try {
      loading = true;
      
      // In a real implementation, this would be an API call
      // For now, we'll use the default settings above
      await new Promise(resolve => setTimeout(resolve, 500));
      
    } catch (error) {
      console.error('Error loading settings:', error);
      saveError = 'Failed to load settings';
    } finally {
      loading = false;
    }
  }
  
  async function saveSettings() {
    try {
      loading = true;
      saveError = '';
      saveSuccess = false;
      
      // In a real implementation, this would be an API call to save settings
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      saveSuccess = true;
      setTimeout(() => {
        saveSuccess = false;
      }, 3000);
      
    } catch (error) {
      console.error('Error saving settings:', error);
      saveError = 'Failed to save settings';
    } finally {
      loading = false;
    }
  }
  
  async function resetToDefaults() {
    if (!confirm('Are you sure you want to reset all settings to defaults? This action cannot be undone.')) {
      return;
    }
    
    // Reset to default values
    settings = {
      system: {
        siteName: 'KPATH Enterprise',
        maintenanceMode: false,
        debugMode: false,
        logLevel: 'info'
      },
      database: {
        connectionTimeout: 30,
        maxConnections: 100,
        queryTimeout: 30,
        backupEnabled: true,
        backupRetention: 30
      },
      search: {
        maxResults: 50,
        searchTimeout: 5000,
        enableCache: true,
        cacheExpiration: 3600,
        minQueryLength: 2
      },
      security: {
        jwtExpirationHours: 24,
        maxLoginAttempts: 5,
        lockoutDuration: 15,
        passwordMinLength: 8,
        requireMfa: false
      },
      notifications: {
        emailNotifications: true,
        systemAlerts: true,
        maintenanceNotices: true,
        securityAlerts: true
      },
      api: {
        rateLimitEnabled: true,
        defaultRateLimit: 1000,
        maxRequestSize: 10,
        enableCors: true,
        corsOrigins: '*'
      }
    };
    
    await saveSettings();
  }
  
  onMount(async () => {
    // Ensure auth is initialized
    auth.init();
    
    // Wait a bit for auth to initialize
    await new Promise(resolve => setTimeout(resolve, 100));
    
    await loadSettings();
  });
  
  // Check if current user is admin
  $: isAdmin = authState?.user?.role === 'admin';
</script>

<div class="max-w-6xl mx-auto p-6">
  <div class="mb-6">
    <h1 class="text-3xl font-bold text-gray-900">System Settings</h1>
    <p class="mt-2 text-gray-600">Configure system behavior and preferences</p>
  </div>
  
  <!-- Access Control -->
  {#if !isAdmin}
    <div class="bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-3 rounded-lg mb-6">
      <p class="font-medium">Access Restricted</p>
      <p>You need admin privileges to modify system settings. Current role: {authState?.user?.role || 'unknown'}</p>
    </div>
  {:else}
    
    <!-- Success/Error Messages -->
    {#if saveSuccess}
      <div class="mb-6 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
        <p class="font-medium">Settings saved successfully!</p>
      </div>
    {/if}
    
    {#if saveError}
      <div class="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
        <p class="font-medium">{saveError}</p>
      </div>
    {/if}
    
    <form on:submit|preventDefault={saveSettings} class="space-y-8">
      
      <!-- System Settings -->
      <div class="bg-white rounded-lg shadow-md p-6">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">
          <Fa icon={faCog} class="inline mr-2" />
          System Configuration
        </h2>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label for="siteName" class="block text-sm font-medium text-gray-700 mb-1">Site Name</label>
            <input
              id="siteName"
              bind:value={settings.system.siteName}
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div>
            <label for="logLevel" class="block text-sm font-medium text-gray-700 mb-1">Log Level</label>
            <select
              id="logLevel"
              bind:value={settings.system.logLevel}
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="debug">Debug</option>
              <option value="info">Info</option>
              <option value="warning">Warning</option>
              <option value="error">Error</option>
            </select>
          </div>
          
          <div class="flex items-center space-x-4">
            <label class="flex items-center">
              <input
                type="checkbox"
                bind:checked={settings.system.maintenanceMode}
                class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span class="ml-2 text-sm text-gray-700">Maintenance Mode</span>
            </label>
            
            <label class="flex items-center">
              <input
                type="checkbox"
                bind:checked={settings.system.debugMode}
                class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span class="ml-2 text-sm text-gray-700">Debug Mode</span>
            </label>
          </div>
        </div>
      </div>
      
      <!-- Database Settings -->
      <div class="bg-white rounded-lg shadow-md p-6">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">
          <Fa icon={faDatabase} class="inline mr-2" />
          Database Configuration
        </h2>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div>
            <label for="connectionTimeout" class="block text-sm font-medium text-gray-700 mb-1">Connection Timeout (seconds)</label>
            <input
              id="connectionTimeout"
              bind:value={settings.database.connectionTimeout}
              type="number"
              min="5"
              max="300"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div>
            <label for="maxConnections" class="block text-sm font-medium text-gray-700 mb-1">Max Connections</label>
            <input
              id="maxConnections"
              bind:value={settings.database.maxConnections}
              type="number"
              min="10"
              max="1000"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div>
            <label for="queryTimeout" class="block text-sm font-medium text-gray-700 mb-1">Query Timeout (seconds)</label>
            <input
              id="queryTimeout"
              bind:value={settings.database.queryTimeout}
              type="number"
              min="5"
              max="300"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div>
            <label for="backupRetention" class="block text-sm font-medium text-gray-700 mb-1">Backup Retention (days)</label>
            <input
              id="backupRetention"
              bind:value={settings.database.backupRetention}
              type="number"
              min="7"
              max="365"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div class="flex items-center">
            <label class="flex items-center">
              <input
                type="checkbox"
                bind:checked={settings.database.backupEnabled}
                class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span class="ml-2 text-sm text-gray-700">Enable Automatic Backups</span>
            </label>
          </div>
        </div>
      </div>
      
      <!-- Search Settings -->
      <div class="bg-white rounded-lg shadow-md p-6">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">
          <Fa icon={faSearch} class="inline mr-2" />
          Search Configuration
        </h2>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div>
            <label for="maxResults" class="block text-sm font-medium text-gray-700 mb-1">Max Results per Query</label>
            <input
              id="maxResults"
              bind:value={settings.search.maxResults}
              type="number"
              min="10"
              max="1000"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div>
            <label for="searchTimeout" class="block text-sm font-medium text-gray-700 mb-1">Search Timeout (ms)</label>
            <input
              id="searchTimeout"
              bind:value={settings.search.searchTimeout}
              type="number"
              min="1000"
              max="30000"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div>
            <label for="cacheExpiration" class="block text-sm font-medium text-gray-700 mb-1">Cache Expiration (seconds)</label>
            <input
              id="cacheExpiration"
              bind:value={settings.search.cacheExpiration}
              type="number"
              min="300"
              max="86400"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div>
            <label for="minQueryLength" class="block text-sm font-medium text-gray-700 mb-1">Min Query Length</label>
            <input
              id="minQueryLength"
              bind:value={settings.search.minQueryLength}
              type="number"
              min="1"
              max="10"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div class="flex items-center">
            <label class="flex items-center">
              <input
                type="checkbox"
                bind:checked={settings.search.enableCache}
                class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span class="ml-2 text-sm text-gray-700">Enable Search Cache</span>
            </label>
          </div>
        </div>
      </div>
      
      <!-- Security Settings -->
      <div class="bg-white rounded-lg shadow-md p-6">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">
          <Fa icon={faShield} class="inline mr-2" />
          Security Configuration
        </h2>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div>
            <label for="jwtExpirationHours" class="block text-sm font-medium text-gray-700 mb-1">JWT Expiration (hours)</label>
            <input
              id="jwtExpirationHours"
              bind:value={settings.security.jwtExpirationHours}
              type="number"
              min="1"
              max="168"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div>
            <label for="maxLoginAttempts" class="block text-sm font-medium text-gray-700 mb-1">Max Login Attempts</label>
            <input
              id="maxLoginAttempts"
              bind:value={settings.security.maxLoginAttempts}
              type="number"
              min="3"
              max="10"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div>
            <label for="lockoutDuration" class="block text-sm font-medium text-gray-700 mb-1">Lockout Duration (minutes)</label>
            <input
              id="lockoutDuration"
              bind:value={settings.security.lockoutDuration}
              type="number"
              min="5"
              max="60"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div>
            <label for="passwordMinLength" class="block text-sm font-medium text-gray-700 mb-1">Min Password Length</label>
            <input
              id="passwordMinLength"
              bind:value={settings.security.passwordMinLength}
              type="number"
              min="6"
              max="32"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div class="flex items-center">
            <label class="flex items-center">
              <input
                type="checkbox"
                bind:checked={settings.security.requireMfa}
                class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span class="ml-2 text-sm text-gray-700">Require MFA</span>
            </label>
          </div>
        </div>
      </div>
      
      <!-- Action Buttons -->
      <div class="flex justify-between items-center pt-6">
        <button
          type="button"
          on:click={resetToDefaults}
          class="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg font-medium"
        >
          <Fa icon={faRedo} class="mr-2" />
          Reset to Defaults
        </button>
        
        <div class="space-x-4">
          <a href="/" class="bg-gray-200 hover:bg-gray-300 text-gray-700 px-4 py-2 rounded-lg font-medium">
            Cancel
          </a>
          <button
            type="submit"
            disabled={loading}
            class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium disabled:opacity-50"
          >
            <Fa icon={faSave} class="mr-2" />
            {loading ? 'Saving...' : 'Save Settings'}
          </button>
        </div>
      </div>
      
    </form>
    
  {/if}
  
  <!-- Footer -->
  <div class="mt-8 text-center">
    <p class="text-sm text-gray-500">
      <Fa icon={faExclamationTriangle} class="mr-1" />
      Changes to these settings may require a system restart to take effect |
      <a href="/" class="text-blue-600 hover:text-blue-800">Back to Dashboard</a>
    </p>
  </div>
</div>
