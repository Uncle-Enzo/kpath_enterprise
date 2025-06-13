<script lang="ts">
  import '../app.css';
  import { onMount } from 'svelte';
  import { auth, isAuthenticated } from '$lib/stores/auth';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import Navbar from '$lib/components/Navbar.svelte';
  import Sidebar from '$lib/components/Sidebar.svelte';
  
  let sidebarOpen = true;
  let authInitialized = false;
  
  onMount(() => {
    auth.init();
    authInitialized = true;
    
    // Handle client-side routing protection
    const unsubscribe = page.subscribe(($page) => {
      const publicPaths = ['/login', '/register'];
      const isPublicPath = publicPaths.includes($page.url.pathname);
      
      // Wait for auth to initialize
      setTimeout(() => {
        if (!$isAuthenticated && !isPublicPath) {
          goto('/login');
        } else if ($isAuthenticated && $page.url.pathname === '/login') {
          goto('/');
        }
      }, 100);
    });
    
    return () => unsubscribe();
  });
  
  $: isAuthPage = $page.url.pathname === '/login' || $page.url.pathname === '/register';
</script>

<div class="min-h-screen bg-gray-50">
  {#if !isAuthPage}
    <Navbar bind:sidebarOpen />
    <div class="flex">
      <Sidebar bind:open={sidebarOpen} />
      <main class="flex-1 p-6 {sidebarOpen ? 'ml-64' : 'ml-16'} transition-all duration-300 mt-16">
        <slot />
      </main>
    </div>
  {:else}
    <slot />
  {/if}
</div>
