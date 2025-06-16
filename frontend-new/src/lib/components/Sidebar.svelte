<script lang="ts">
  import { page } from '$app/stores';
  import { isAdmin } from '$lib/stores/auth';
  import Fa from 'svelte-fa';
  import { 
    faHome, 
    faSearch, 
    faServer, 
    faUsers, 
    faKey,
    faCog,
    faChartBar,
    faBook
  } from '@fortawesome/free-solid-svg-icons';
  
  export let open: boolean;
  
  const menuItems = [
    { icon: faHome, label: 'Dashboard', href: '/', adminOnly: false },
    { icon: faSearch, label: 'Search', href: '/search', adminOnly: false },
    { icon: faServer, label: 'Services', href: '/services', adminOnly: false },
    { icon: faUsers, label: 'Users', href: '/users', adminOnly: true },
    { icon: faKey, label: 'API Keys', href: '/api-keys', adminOnly: false },
    { icon: faChartBar, label: 'Analytics', href: '/analytics', adminOnly: false },
    { icon: faBook, label: 'User Guide', href: '/user-guide', adminOnly: false },
    { icon: faCog, label: 'Settings', href: '/settings', adminOnly: true },
  ];
  
  $: currentPath = $page.url.pathname;
</script>

<aside class="fixed left-0 top-16 h-[calc(100vh-4rem)] bg-gray-900 text-white transition-all duration-300 {open ? 'w-64' : 'w-16'} z-40">
  <nav class="mt-8">
    {#each menuItems as item}
      {#if !item.adminOnly || $isAdmin}
        <a
          href={item.href}
          class="flex items-center px-4 py-3 hover:bg-gray-800 transition-colors {currentPath === item.href ? 'bg-gray-800 border-l-4 border-primary-500' : ''}"
        >
          <Fa icon={item.icon} class="text-lg {open ? 'mr-3' : 'mx-auto'}" />
          {#if open}
            <span>{item.label}</span>
          {/if}
        </a>
      {/if}
    {/each}
  </nav>
</aside>
