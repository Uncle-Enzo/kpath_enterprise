<script lang="ts">
  import { onMount } from 'svelte';
  import { servicesApi } from '$lib/api/services';
  import type { Service } from '$lib/types';
  import Fa from 'svelte-fa';
  import { faPlus, faEdit, faTrash, faSearch, faCog, faRobot, faServer, faFileImport, faBook } from '@fortawesome/free-solid-svg-icons';
  
  let services: Service[] = [];
  let loading = true;
  let error = '';
  let searchQuery = '';
  let currentPage = 1;
  let totalPages = 1;
  let filterToolType = '';
  let filterVisibility = '';
  
  $: filteredServices = services.filter(service => {
    const matchesSearch = 
      service.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      service.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesToolType = !filterToolType || service.tool_type === filterToolType;
    const matchesVisibility = !filterVisibility || service.visibility === filterVisibility;
    return matchesSearch && matchesToolType && matchesVisibility;
  });
  
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
  
  function getToolTypeIcon(toolType: string) {
    switch (toolType) {
      case 'InternalAgent':
      case 'ExternalAgent':
        return faRobot;
      case 'API':
      case 'MicroService':
        return faServer;
      default:
        return faCog;
    }
  }
  
  function getToolTypeColor(toolType: string) {
    switch (toolType) {
      case 'InternalAgent':
        return 'text-blue-600';
      case 'ExternalAgent':
        return 'text-purple-600';
      case 'API':
        return 'text-green-600';
      case 'ESBEndpoint':
        return 'text-orange-600';
      case 'LegacySystem':
        return 'text-gray-600';
      case 'MicroService':
        return 'text-indigo-600';
      default:
        return 'text-gray-600';
    }
  }
  
  onMount(loadServices);
</script>

<div class="space-y-6">
  <div class="flex justify-between items-center">
    <h1 class="text-2xl font-bold text-gray-900">Services</h1>
    <div class="flex space-x-3">
      <a href="/services/import-guide" class="btn btn-secondary">
        <Fa icon={faBook} class="mr-2" />
        Import Guide
      </a>
      <a href="/services/import" class="btn btn-secondary">
        <Fa icon={faFileImport} class="mr-2" />
        Import Services
      </a>
      <a href="/services/new" class="btn btn-primary">
        <Fa icon={faPlus} class="mr-2" />
        Add Service
      </a>
    </div>
  </div>
  
  <!-- Filters and Search -->
  <div class="card">
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="relative">
        <Fa icon={faSearch} class="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
        <input
          type="text"
          bind:value={searchQuery}
          placeholder="Search services..."
          class="input pl-10"
        />
      </div>
      
      <select bind:value={filterToolType} class="input">
        <option value="">All Tool Types</option>
        <option value="API">API Endpoint</option>
        <option value="InternalAgent">Internal Agent</option>
        <option value="ExternalAgent">External Agent</option>
        <option value="ESBEndpoint">ESB Endpoint</option>
        <option value="LegacySystem">Legacy System</option>
        <option value="MicroService">Microservice</option>
      </select>
      
      <select bind:value={filterVisibility} class="input">
        <option value="">All Visibility Levels</option>
        <option value="internal">Internal</option>
        <option value="org-wide">Organization Wide</option>
        <option value="public">Public</option>
        <option value="restricted">Restricted</option>
      </select>
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
                Type
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Description
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Visibility
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Modes
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
                  {#if service.version}
                    <div class="text-xs text-gray-500">v{service.version}</div>
                  {/if}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <Fa icon={getToolTypeIcon(service.tool_type)} class="{getToolTypeColor(service.tool_type)} mr-2" />
                    <span class="text-sm text-gray-900">{service.tool_type}</span>
                  </div>
                </td>
                <td class="px-6 py-4">
                  <div class="text-sm text-gray-500 max-w-xs truncate">{service.description}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full {service.status === 'active' ? 'bg-green-100 text-green-800' : service.status === 'deprecated' ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800'}">
                    {service.status}
                  </span>
                  {#if service.deprecation_notice}
                    <div class="text-xs text-red-600 mt-1">Deprecated</div>
                  {/if}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="text-sm text-gray-900">{service.visibility}</span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  {#if service.interaction_modes && service.interaction_modes.length > 0}
                    <div class="flex flex-wrap gap-1">
                      {#each service.interaction_modes as mode}
                        <span class="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">
                          {mode}
                        </span>
                      {/each}
                    </div>
                  {:else}
                    <span class="text-sm text-gray-400">-</span>
                  {/if}
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
