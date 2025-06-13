<script lang="ts">
  import { auth, currentUser } from '$lib/stores/auth';
  import { goto } from '$app/navigation';
  import Fa from 'svelte-fa';
  import { faBars, faUser, faSignOutAlt } from '@fortawesome/free-solid-svg-icons';
  
  export let sidebarOpen: boolean;
  
  let dropdownOpen = false;
  
  function toggleSidebar() {
    sidebarOpen = !sidebarOpen;
  }
  
  function logout() {
    auth.logout();
    goto('/login');
  }
</script>

<nav class="fixed top-0 left-0 right-0 bg-white shadow-md z-50">
  <div class="px-4 h-16 flex items-center justify-between">
    <div class="flex items-center">
      <button 
        on:click={toggleSidebar}
        class="p-2 rounded-lg hover:bg-gray-100 transition-colors"
      >
        <Fa icon={faBars} class="text-gray-600" />
      </button>
      <h1 class="ml-4 text-xl font-bold text-gray-800">KPath Enterprise</h1>
    </div>
    
    {#if $currentUser}
      <div class="relative">
        <button
          on:click={() => dropdownOpen = !dropdownOpen}
          class="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-100 transition-colors"
        >
          <Fa icon={faUser} class="text-gray-600" />
          <span class="text-gray-700">{$currentUser.username}</span>
        </button>
        
        {#if dropdownOpen}
          <div class="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg py-1">
            <div class="px-4 py-2 border-b">
              <p class="text-sm text-gray-500">Role: {$currentUser.role}</p>
            </div>
            <button
              on:click={logout}
              class="w-full text-left px-4 py-2 hover:bg-gray-100 flex items-center space-x-2"
            >
              <Fa icon={faSignOutAlt} class="text-gray-600" />
              <span>Logout</span>
            </button>
          </div>
        {/if}
      </div>
    {/if}
  </div>
</nav>

<svelte:window on:click={() => dropdownOpen = false} />
