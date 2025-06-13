<script lang="ts">
  import { onMount } from 'svelte';
  import { servicesApi } from '$lib/api/services';
  import type { Service } from '$lib/types';
  import Fa from 'svelte-fa';
  import { faPlus, faEdit, faTrash, faSearch } from '@fortawesome/free-solid-svg-icons';
  
  let services: Service[] = [];
  let loading = true;
  let error = '';
  let searchQuery = '';
  let currentPage = 1;
  let totalPages = 1;
  
  $: filteredServices = services.filter(service => 
    service.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    service.description.toLowerCase().includes(searchQuery.toLowerCase())
  );
  
  async function loadServices() {
    try {
      loading = true;
      console.log('Loading services...');
      const skip = (currentPage - 1) * 20;
      const response = await servicesApi.list({ skip, limit: 20 });
      console.log('Services response:', response);
      services = response.items || [];
      totalPages = Math.ceil((response.total || 0) / (response.limit || 20));
    } catch (err: any) {
      error = err.message || 'Failed to load services';
      console.error('Error loading services:', err);
    } finally {
      loading = false;
    }
  }
  
  async function deleteService(id: number) {
    if (!confirm('Are you sure you want to delete this service?')) return;
    
    try {
      await servicesApi.delete(id);
      await loadServices();
    } catch (err) {
      alert('Failed to delete service');
    }
  }
  
  onMount(loadServices);
</script>

<div class="space-y-6">
  <div class="flex justify-between items-center">
    <h1 class="text-2xl font-bold text-gray-900">Services</h1>
    <a href="/services/new" class="btn btn-primary">
      <Fa icon={faPlus} class="mr-2" />
      Add Service
    </a>
  </div>
  
  <!-- Search Bar -->
  <div class="card">
    <div class="relative">
      <Fa icon={faSearch} class="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
      <input
        type="text"
        bind:value={searchQuery}
        placeholder="Search services..."
        class="input pl-10"
      />
    </div>
  </div>
  
  <!-- Services Table -->
  <div class="card overflow-hidden">
    {#if loading}
      <div class="text-center py-8">
        <p class="text-gray-500">Loading services...</p>
      </div>
    {:else if error}
      <div class="text-center py-8">
        <p class="text-red-500">{error}</p>
      </div>
    {:else if filteredServices.length === 0}
      <div class="text-center py-8">
        <p class="text-gray-500">No services found</p>
      </div>
    {:else}
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Name
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Description
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Version
              </th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            {#each filteredServices as service}
              <tr class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm font-medium text-gray-900">{service.name}</div>
                </td>
                <td class="px-6 py-4">
                  <div class="text-sm text-gray-500">{service.description}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full {service.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}">
                    {service.status}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {service.version || '-'}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <a href="/services/{service.id}" class="text-primary-600 hover:text-primary-900 mr-3">
                    <Fa icon={faEdit} />
                  </a>
                  <button on:click={() => deleteService(service.id)} class="text-red-600 hover:text-red-900">
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
