<script lang="ts">
  import { onMount } from 'svelte';
  import { auth } from '$lib/stores/auth';
  import { usersApi, type UserCreateRequest } from '$lib/api/users';
  import type { User } from '$lib/types';
  
  let authState: any = null;
  let users: User[] = [];
  let loading = true;
  let error = '';
  let showCreateForm = false;
  let editingUser: User | null = null;
  
  // Form data
  let formData: UserCreateRequest = {
    username: '',
    email: '',
    password: '',
    role: 'user'
  };
  
  // Subscribe to auth state
  auth.subscribe(($auth) => {
    authState = $auth;
  });
  
  // Load users on mount
  onMount(async () => {
    // Ensure auth is initialized
    auth.init();
    
    // Wait a bit for auth to initialize
    await new Promise(resolve => setTimeout(resolve, 100));
    
    await loadUsers();
  });
  
  async function loadUsers() {
    try {
      loading = true;
      error = '';
      
      // Debug auth state
      console.log('Auth state during loadUsers:', authState);
      console.log('Token:', authState?.token ? 'Present' : 'Missing');
      console.log('User:', authState?.user);
      
      users = await usersApi.list();
      console.log('Loaded users:', users);
    } catch (err: any) {
      error = `Failed to load users: ${err.message || 'Unknown error'}`;
      console.error('Error loading users:', err);
      console.error('Error response:', err.response);
    } finally {
      loading = false;
    }
  }
  
  async function createUser() {
    try {
      error = '';
      const newUser = await usersApi.create(formData);
      users = [...users, newUser];
      resetForm();
      showCreateForm = false;
    } catch (err: any) {
      error = `Failed to create user: ${err.message || 'Unknown error'}`;
      console.error('Error creating user:', err);
    }
  }
  
  async function updateUser() {
    if (!editingUser) return;
    
    try {
      error = '';
      const updatedUser = await usersApi.update(editingUser.id, {
        username: formData.username,
        email: formData.email,
        role: formData.role,
        ...(formData.password ? { password: formData.password } : {})
      });
      
      users = users.map(u => u.id === editingUser!.id ? updatedUser : u);
      resetForm();
      editingUser = null;
    } catch (err: any) {
      error = `Failed to update user: ${err.message || 'Unknown error'}`;
      console.error('Error updating user:', err);
    }
  }
  
  async function deleteUser(user: User) {
    if (!confirm(`Are you sure you want to delete user "${user.email}"?`)) {
      return;
    }
    
    try {
      error = '';
      await usersApi.delete(user.id);
      users = users.filter(u => u.id !== user.id);
    } catch (err: any) {
      error = `Failed to delete user: ${err.message || 'Unknown error'}`;
      console.error('Error deleting user:', err);
    }
  }
  
  function startEdit(user: User) {
    editingUser = user;
    formData = {
      username: user.username || '',
      email: user.email,
      password: '', // Don't populate password for security
      role: user.role
    };
    showCreateForm = true;
  }
  
  function resetForm() {
    formData = {
      username: '',
      email: '',
      password: '',
      role: 'user'
    };
    showCreateForm = false;
    editingUser = null;
  }
  
  function getRoleBadgeClass(role: string) {
    switch (role) {
      case 'admin': return 'bg-red-100 text-red-800';
      case 'editor': return 'bg-blue-100 text-blue-800';
      case 'viewer': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  }
  
  // Check if current user is admin
  $: isAdmin = authState?.user?.role === 'admin';
  $: currentUserId = authState?.user?.id;
</script>

<div class="max-w-7xl mx-auto p-6">
  <div class="mb-6">
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">User Management</h1>
        <p class="mt-2 text-gray-600">Manage system users and their permissions</p>
      </div>
      
      {#if isAdmin}
        <button
          on:click={() => showCreateForm = true}
          class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium"
        >
          Add New User
        </button>
      {/if}
    </div>
  </div>
  
  <!-- Error Message -->
  {#if error}
    <div class="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
      {error}
    </div>
  {/if}
  
  <!-- Auth Check -->
  {#if !isAdmin}
    <div class="bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-3 rounded-lg mb-6">
      <p class="font-medium">Access Restricted</p>
      <p>You need admin privileges to manage users. Current role: {authState?.user?.role || 'unknown'}</p>
    </div>
  {/if}
  
  <!-- Create/Edit Form Modal -->
  {#if showCreateForm}
    <div class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div class="px-6 py-4 border-b">
          <h3 class="text-lg font-semibold">
            {editingUser ? 'Edit User' : 'Create New User'}
          </h3>
        </div>
        
        <form on:submit|preventDefault={editingUser ? updateUser : createUser} class="px-6 py-4 space-y-4">
          <div>
            <label for="username" class="block text-sm font-medium text-gray-700 mb-1">Username</label>
            <input
              id="username"
              bind:value={formData.username}
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter username (optional)"
            />
          </div>
          
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700 mb-1">Email *</label>
            <input
              id="email"
              bind:value={formData.email}
              type="email"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter email address"
            />
          </div>
          
          <div>
            <label for="password" class="block text-sm font-medium text-gray-700 mb-1">
              Password {editingUser ? '(leave blank to keep current)' : '*'}
            </label>
            <input
              id="password"
              bind:value={formData.password}
              type="password"
              required={!editingUser}
              minlength="8"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder={editingUser ? 'Enter new password (optional)' : 'Enter password (min 8 chars)'}
            />
          </div>
          
          <div>
            <label for="role" class="block text-sm font-medium text-gray-700 mb-1">Role *</label>
            <select
              id="role"
              bind:value={formData.role}
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="user">User</option>
              <option value="viewer">Viewer</option>
              <option value="editor">Editor</option>
              <option value="admin">Admin</option>
            </select>
          </div>
          
          <div class="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              on:click={resetForm}
              class="px-4 py-2 text-gray-700 bg-gray-200 hover:bg-gray-300 rounded-md"
            >
              Cancel
            </button>
            <button
              type="submit"
              class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md"
            >
              {editingUser ? 'Update User' : 'Create User'}
            </button>
          </div>
        </form>
      </div>
    </div>
  {/if}
  
  <!-- Users Table -->
  <div class="bg-white shadow-sm rounded-lg overflow-hidden">
    {#if loading}
      <div class="p-6 text-center">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p class="mt-2 text-gray-600">Loading users...</p>
      </div>
    {:else if users.length === 0}
      <div class="p-6 text-center text-gray-500">
        <p>No users found.</p>
      </div>
    {:else}
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                User
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Role
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Created
              </th>
              {#if isAdmin}
                <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              {/if}
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            {#each users as user (user.id)}
              <tr class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <div class="flex-shrink-0 h-10 w-10">
                      <div class="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                        <span class="text-sm font-medium text-gray-700">
                          {(user.username || user.email).charAt(0).toUpperCase()}
                        </span>
                      </div>
                    </div>
                    <div class="ml-4">
                      <div class="text-sm font-medium text-gray-900">
                        {user.username || 'No username'}
                      </div>
                      <div class="text-sm text-gray-500">{user.email}</div>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full {getRoleBadgeClass(user.role)}">
                    {user.role}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full {user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}">
                    {user.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {new Date(user.created_at).toLocaleDateString()}
                </td>
                {#if isAdmin}
                  <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div class="flex justify-end space-x-2">
                      <button
                        on:click={() => startEdit(user)}
                        class="text-blue-600 hover:text-blue-900"
                      >
                        Edit
                      </button>
                      {#if user.id !== currentUserId}
                        <button
                          on:click={() => deleteUser(user)}
                          class="text-red-600 hover:text-red-900"
                        >
                          Delete
                        </button>
                      {:else}
                        <span class="text-gray-400 cursor-not-allowed">Delete</span>
                      {/if}
                    </div>
                  </td>
                {/if}
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}
  </div>
  
  <!-- Footer -->
  <div class="mt-6 text-center">
    <p class="text-sm text-gray-500">
      Total users: {users.length} | 
      <a href="/users/debug" class="text-blue-600 hover:text-blue-800">Debug Page</a> |
      <a href="/" class="text-blue-600 hover:text-blue-800">Back to Dashboard</a>
    </p>
  </div>
</div>
