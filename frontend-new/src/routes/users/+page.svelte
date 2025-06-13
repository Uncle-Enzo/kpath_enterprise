<script lang="ts">
  import { onMount } from 'svelte';
  import { usersApi } from '$lib/api/users';
  import { isAdmin } from '$lib/stores/auth';
  import type { User } from '$lib/types';
  import Fa from 'svelte-fa';
  import { faPlus, faEdit, faTrash } from '@fortawesome/free-solid-svg-icons';
  
  let users: User[] = [];
  let loading = true;
  let error = '';
  
  async function loadUsers() {
    try {
      loading = true;
      const response = await usersApi.list();
      users = response.users;
    } catch (err: any) {
      error = 'Failed to load users';
    } finally {
      loading = false;
    }
  }
  
  async function deleteUser(id: number) {
    if (!confirm('Are you sure you want to delete this user?')) return;
    
    try {
      await usersApi.delete(id);
      await loadUsers();
    } catch (err) {
      alert('Failed to delete user');
    }
  }
  
  onMount(() => {
    if ($isAdmin) {
      loadUsers();
    }
  });
</script>

{#if !$isAdmin}
  <div class="card">
    <p class="text-red-500">Access denied. Admin privileges required.</p>
  </div>
{:else}
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold text-gray-900">Users</h1>
      <a href="/users/new" class="btn btn-primary">
        <Fa icon={faPlus} class="mr-2" />
        Add User
      </a>
    </div>
    
    <div class="card">
      {#if loading}
        <div class="text-center py-8">
          <p class="text-gray-500">Loading users...</p>
        </div>
      {:else if error}
        <div class="text-center py-8">
          <p class="text-red-500">{error}</p>
        </div>
      {:else if users.length === 0}
        <div class="text-center py-8">
          <p class="text-gray-500">No users found</p>
        </div>
      {:else}
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Username
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Email
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Role
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              {#each users as user}
                <tr>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm font-medium text-gray-900">{user.username}</div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm text-gray-500">{user.email}</div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                      {user.role}
                    </span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full {user.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}">
                      {user.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <a href="/users/{user.id}" class="text-primary-600 hover:text-primary-900 mr-3">
                      <Fa icon={faEdit} />
                    </a>
                    <button on:click={() => deleteUser(user.id)} class="text-red-600 hover:text-red-900">
                      <Fa icon={faTrash} />
                    </button>
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      {/if}
    </div>
  </div>
{/if}
