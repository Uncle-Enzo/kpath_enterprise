<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { usersApi } from '$lib/api/users';
  import { goto } from '$app/navigation';
  import { isAdmin } from '$lib/stores/auth';
  import type { User } from '$lib/types';
  import Fa from 'svelte-fa';
  import { faUser, faEnvelope, faLock, faUserShield, faToggleOn, faToggleOff } from '@fortawesome/free-solid-svg-icons';
  
  let userId = parseInt($page.params.id);
  let user: User | null = null;
  let loading = true;
  let saving = false;
  let error = '';
  let fieldErrors: Record<string, string> = {};
  
  let formData = {
    username: '',
    email: '',
    password: '',
    confirmPassword: '', 
    role: 'user' as 'admin' | 'editor' | 'viewer' | 'user',
    is_active: true
  };
  
  let showPasswordFields = false;
  
  const roles = [
    { value: 'admin', label: 'Administrator', description: 'Full system access' },
    { value: 'editor', label: 'Editor', description: 'Can create and edit services' },
    { value: 'viewer', label: 'Viewer', description: 'Read-only access' },
    { value: 'user', label: 'User', description: 'Basic user access' }
  ];
  
  async function loadUser() {
    try {
      loading = true;
      user = await usersApi.get(userId);
      
      // Populate form with user data
      formData.username = user.username || '';
      formData.email = user.email;
      formData.role = user.role;
      formData.is_active = user.is_active;
      formData.password = '';
      formData.confirmPassword = '';
      
    } catch (err: any) {
      error = 'Failed to load user';
      console.error('Error loading user:', err);
    } finally {
      loading = false;
    }
  }
  
  function validateForm() {
    fieldErrors = {};
    
    if (!formData.username.trim()) {
      fieldErrors.username = 'Username is required';
    } else if (formData.username.length < 3) {
      fieldErrors.username = 'Username must be at least 3 characters';
    }
    
    if (!formData.email.trim()) {
      fieldErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      fieldErrors.email = 'Please enter a valid email address';
    }
    
    // Only validate password if changing it
    if (showPasswordFields) {
      if (!formData.password) {
        fieldErrors.password = 'Password is required';
      } else if (formData.password.length < 8) {
        fieldErrors.password = 'Password must be at least 8 characters';
      }
      
      if (formData.password !== formData.confirmPassword) {
        fieldErrors.confirmPassword = 'Passwords do not match';
      }
    }
    
    return Object.keys(fieldErrors).length === 0;
  }
  
  async function handleSubmit() {
    if (!validateForm()) return;
    
    saving = true;
    error = '';
    
    try {
      const updateData: any = {
        username: formData.username,
        email: formData.email,
        role: formData.role
      };
      
      // Only include password if it's being changed
      if (showPasswordFields && formData.password) {
        updateData.password = formData.password;
      }
      
      await usersApi.update(userId, updateData);
      goto('/users');
    } catch (err: any) {
      if (err.response?.data?.detail) {
        error = err.response.data.detail;
      } else {
        error = 'Failed to update user. Please try again.';
      }
    } finally {
      saving = false;
    }
  }
  
  async function toggleUserStatus() {
    try {
      await usersApi.update(userId, { is_active: !formData.is_active });
      formData.is_active = !formData.is_active;
      if (user) {
        user.is_active = formData.is_active;
      }
    } catch (err: any) {
      error = 'Failed to update user status';
    }
  }
  
  function getRoleColor(role: string) {
    switch (role) {
      case 'admin': return 'text-red-600';
      case 'editor': return 'text-blue-600';
      case 'viewer': return 'text-green-600';
      default: return 'text-gray-600';
    }
  }
  
  onMount(loadUser);
</script>

{#if !$isAdmin}
  <div class="max-w-2xl mx-auto">
    <div class="card">
      <p class="text-red-500">Access denied. Admin privileges required.</p>
      <div class="mt-4">
        <a href="/users" class="text-primary-600 hover:text-primary-800">← Back to Users</a>
      </div>
    </div>
  </div>
{:else}
  <div class="max-w-2xl mx-auto space-y-6">
    <div class="flex items-center space-x-3">
      <a href="/users" class="text-primary-600 hover:text-primary-800">← Back to Users</a>
    </div>
    
    {#if loading}
      <div class="card">
        <div class="text-center py-8">
          <p class="text-gray-500">Loading user...</p>
        </div>
      </div>
    {:else if error && !user}
      <div class="card">
        <div class="text-center py-8">
          <p class="text-red-500">{error}</p>
        </div>
      </div>
    {:else}
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Edit User</h1>
        <p class="text-gray-600">Update user information and permissions</p>
      </div>
      
      <!-- User Status Card -->
      <div class="card">
        <div class="flex justify-between items-center">
          <div>
            <h2 class="text-lg font-semibold text-gray-900">User Status</h2>
            <p class="text-sm text-gray-600">
              Current status: 
              <span class="font-medium {formData.is_active ? 'text-green-600' : 'text-red-600'}">
                {formData.is_active ? 'Active' : 'Inactive'}
              </span>
            </p>
          </div>
          <button 
            on:click={toggleUserStatus}
            class="flex items-center space-x-2 px-4 py-2 rounded-lg border {formData.is_active ? 'bg-red-50 border-red-200 text-red-700 hover:bg-red-100' : 'bg-green-50 border-green-200 text-green-700 hover:bg-green-100'}"
          >
            <Fa icon={formData.is_active ? faToggleOn : faToggleOff} />
            <span>{formData.is_active ? 'Deactivate' : 'Activate'}</span>
          </button>
        </div>
      </div>
      
      <!-- Edit Form -->
      <form on:submit|preventDefault={handleSubmit} class="card space-y-6">
        {#if error}
          <div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        {/if}
        
        <!-- Username -->
        <div>
          <label for="username" class="block text-sm font-medium text-gray-700 mb-1">
            <Fa icon={faUser} class="mr-2" />
            Username *
          </label>
          <input
            id="username"
            type="text"
            bind:value={formData.username}
            required
            class="input {fieldErrors.username ? 'border-red-300' : ''}"
            placeholder="Enter username"
          />
          {#if fieldErrors.username}
            <p class="text-red-600 text-sm mt-1">{fieldErrors.username}</p>
          {/if}
        </div>
        
        <!-- Email -->
        <div>
          <label for="email" class="block text-sm font-medium text-gray-700 mb-1">
            <Fa icon={faEnvelope} class="mr-2" />
            Email Address *
          </label>
          <input
            id="email"
            type="email"
            bind:value={formData.email}
            required
            class="input {fieldErrors.email ? 'border-red-300' : ''}"
            placeholder="user@company.com"
          />
          {#if fieldErrors.email}
            <p class="text-red-600 text-sm mt-1">{fieldErrors.email}</p>
          {/if}
        </div>
        
        <!-- Password Change -->
        <div class="border-t pt-4">
          <div class="flex items-center justify-between mb-4">
            <label class="text-sm font-medium text-gray-700">
              <Fa icon={faLock} class="mr-2" />
              Change Password
            </label>
            <button 
              type="button"
              on:click={() => showPasswordFields = !showPasswordFields}
              class="text-sm text-primary-600 hover:text-primary-800"
            >
              {showPasswordFields ? 'Cancel' : 'Change Password'}
            </button>
          </div>
          
          {#if showPasswordFields}
            <div class="space-y-4">
              <div>
                <label for="password" class="block text-sm font-medium text-gray-700 mb-1">
                  New Password *
                </label>
                <input
                  id="password"
                  type="password"
                  bind:value={formData.password}
                  class="input {fieldErrors.password ? 'border-red-300' : ''}"
                  placeholder="Minimum 8 characters"
                />
                {#if fieldErrors.password}
                  <p class="text-red-600 text-sm mt-1">{fieldErrors.password}</p>
                {/if}
              </div>
              
              <div>
                <label for="confirmPassword" class="block text-sm font-medium text-gray-700 mb-1">
                  Confirm New Password *
                </label>
                <input
                  id="confirmPassword"
                  type="password"
                  bind:value={formData.confirmPassword}
                  class="input {fieldErrors.confirmPassword ? 'border-red-300' : ''}"
                  placeholder="Re-enter password"
                />
                {#if fieldErrors.confirmPassword}
                  <p class="text-red-600 text-sm mt-1">{fieldErrors.confirmPassword}</p>
                {/if}
              </div>
            </div>
          {/if}
        </div>
        
        <!-- Role -->
        <div class="border-t pt-4">
          <label class="block text-sm font-medium text-gray-700 mb-3">
            <Fa icon={faUserShield} class="mr-2" />
            User Role *
          </label>
          <div class="space-y-3">
            {#each roles as role}
              <label class="flex items-start space-x-3 p-3 border rounded-lg hover:bg-gray-50 cursor-pointer {formData.role === role.value ? 'border-primary-500 bg-primary-50' : 'border-gray-200'}">
                <input
                  type="radio"
                  name="role"
                  value={role.value}
                  bind:group={formData.role}
                  class="mt-1"
                />
                <div class="flex-1">
                  <div class="flex items-center space-x-2">
                    <span class="font-medium text-gray-900">{role.label}</span>
                    <span class="{getRoleColor(role.value)} text-sm">({role.value})</span>
                  </div>
                  <p class="text-sm text-gray-600">{role.description}</p>
                </div>
              </label>
            {/each}
          </div>
        </div>
        
        <!-- Submit Button -->
        <div class="flex justify-end space-x-3 pt-4 border-t">
          <a href="/users" class="btn btn-secondary">
            Cancel
          </a>
          <button 
            type="submit" 
            disabled={saving}
            class="btn btn-primary"
          >
            {saving ? 'Saving...' : 'Update User'}
          </button>
        </div>
      </form>
    {/if}
  </div>
{/if}