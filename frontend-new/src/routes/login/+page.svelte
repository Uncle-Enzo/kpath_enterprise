<script lang="ts">
  import { auth } from '$lib/stores/auth';
  import { authApi } from '$lib/api/auth';
  import { goto } from '$app/navigation';
  import type { LoginRequest } from '$lib/types';
  
  let form: LoginRequest = {
    username: '',
    password: ''
  };
  
  let loading = false;
  let error = '';
  
  async function handleSubmit() {
    loading = true;
    error = '';
    
    try {
      const response = await authApi.login(form);
      
      // Check if we have both user and token
      if (response.access_token && response.user) {
        auth.login(response.user, response.access_token);
        
        // Force hard redirect
        window.location.href = '/';
      } else {
        error = 'Invalid response from server';
      }
    } catch (err: any) {
      console.error('Login error:', err);
      error = err.response?.data?.detail || err.message || 'Login failed. Please try again.';
    } finally {
      loading = false;
    }
  }
</script>

<div class="min-h-screen flex items-center justify-center bg-gray-50">
  <div class="max-w-md w-full">
    <div class="text-center mb-8">
      <h1 class="text-3xl font-bold text-gray-900">KPath Enterprise</h1>
      <p class="mt-2 text-gray-600">Sign in to your account</p>
    </div>
    
    <div class="bg-white rounded-lg shadow-md p-6">
      <form on:submit|preventDefault={handleSubmit} class="space-y-6">
        {#if error}
          <div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        {/if}
        
        <div>
          <label for="username" class="block text-sm font-medium text-gray-700">
            Email Address
          </label>
          <input
            id="username"
            type="email"
            bind:value={form.username}
            required
            class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500 mt-1"
            placeholder="Enter your email address"
          />
        </div>
        
        <div>
          <label for="password" class="block text-sm font-medium text-gray-700">
            Password
          </label>
          <input
            id="password"
            type="password"
            bind:value={form.password}
            required
            class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500 mt-1"
            placeholder="Enter your password"
          />
        </div>
        
        <button
          type="submit"
          disabled={loading}
          class="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium disabled:opacity-50"
        >
          {loading ? 'Signing in...' : 'Sign in'}
        </button>
      </form>
    </div>
  </div>
</div>
