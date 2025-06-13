<script lang="ts">
  import { onMount } from 'svelte';
  import { auth } from '$lib/stores/auth';
  
  let authState = null;
  let testResult = '';
  let loading = false;
  
  auth.subscribe(($auth) => {
    authState = $auth;
    console.log('Auth state:', $auth);
  });
  
  async function testAuth() {
    loading = true;
    testResult = '';
    
    try {
      // Test 1: Check localStorage
      const token = localStorage.getItem('token');
      const user = localStorage.getItem('user');
      
      testResult += `Token in localStorage: ${token ? 'YES (' + token.substring(0, 20) + '...)' : 'NO'}\n`;
      testResult += `User in localStorage: ${user ? 'YES' : 'NO'}\n`;
      
      if (user) {
        const userObj = JSON.parse(user);
        testResult += `User role: ${userObj.role}\n`;
        testResult += `User email: ${userObj.email}\n`;
      }
      
      // Test 2: Test users API directly
      if (token) {
        testResult += '\n--- Testing Users API ---\n';
        
        const response = await fetch('/api/v1/users/', {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        
        testResult += `API Response Status: ${response.status}\n`;
        testResult += `API Response OK: ${response.ok}\n`;
        
        if (response.ok) {
          const users = await response.json();
          testResult += `Users count: ${users.length}\n`;
        } else {
          const errorText = await response.text();
          testResult += `Error: ${errorText}\n`;
        }
      }
      
    } catch (error) {
      testResult += `\nError: ${error.message}\n`;
    } finally {
      loading = false;
    }
  }
  
  async function testLogin() {
    loading = true;
    testResult = '';
    
    try {
      const formData = new URLSearchParams();
      formData.append('username', 'admin@kpath.ai');
      formData.append('password', '1234rt4rd');
      
      const response = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: formData
      });
      
      testResult += `Login Status: ${response.status}\n`;
      
      if (response.ok) {
        const data = await response.json();
        testResult += `Login successful!\n`;
        testResult += `Token received: ${data.access_token.substring(0, 20)}...\n`;
        testResult += `User: ${JSON.stringify(data.user, null, 2)}\n`;
        
        // Store in localStorage
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('user', JSON.stringify(data.user));
        
        // Update auth store
        auth.login(data.user, data.access_token);
        
        testResult += '\nStored in localStorage and auth store!\n';
      } else {
        const errorText = await response.text();
        testResult += `Login failed: ${errorText}\n`;
      }
    } catch (error) {
      testResult += `Login error: ${error.message}\n`;
    } finally {
      loading = false;
    }
  }
  
  onMount(() => {
    auth.init();
  });
</script>

<div class="max-w-4xl mx-auto p-6 space-y-6">
  <h1 class="text-2xl font-bold">Users Page Debug</h1>
  
  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
    <!-- Auth State -->
    <div class="bg-white p-6 rounded-lg shadow">
      <h2 class="text-lg font-semibold mb-4">Current Auth State</h2>
      <pre class="bg-gray-100 p-4 rounded text-sm overflow-auto">{JSON.stringify(authState, null, 2)}</pre>
    </div>
    
    <!-- Actions -->
    <div class="bg-white p-6 rounded-lg shadow">
      <h2 class="text-lg font-semibold mb-4">Debug Actions</h2>
      <div class="space-y-3">
        <button on:click={testLogin} disabled={loading} class="w-full bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50">
          {loading ? 'Testing...' : 'Test Login'}
        </button>
        <button on:click={testAuth} disabled={loading} class="w-full bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700 disabled:opacity-50">
          {loading ? 'Testing...' : 'Test Auth & Users API'}
        </button>
        <a href="/users" class="block w-full bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 text-center">
          Go to Users Page
        </a>
        <a href="/login" class="block w-full bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700 text-center">
          Go to Login Page
        </a>
      </div>
    </div>
  </div>
  
  <!-- Results -->
  {#if testResult}
    <div class="bg-white p-6 rounded-lg shadow">
      <h2 class="text-lg font-semibold mb-4">Test Results</h2>
      <pre class="bg-gray-900 text-green-400 p-4 rounded text-sm overflow-auto">{testResult}</pre>
    </div>
  {/if}
</div>