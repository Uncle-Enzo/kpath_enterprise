<script lang="ts">
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import { servicesApi } from '$lib/api/services';
  import ServiceForm from '$lib/components/ServiceForm.svelte';
  import type { ServiceCreateRequest } from '$lib/api/services';
  
  let serviceId = parseInt($page.params.id);
  let service: Partial<ServiceCreateRequest> = {};
  let loading = true;
  let error = '';
  
  async function loadService() {
    try {
      const data = await servicesApi.get(serviceId);
      service = {
        name: data.name,
        description: data.description,
        endpoint: data.endpoint,
        version: data.version,
        status: data.status,
        capabilities: data.capabilities?.map(c => ({
          capability_name: c.capability_name,
          capability_desc: c.capability_desc
        })) || [],
        domains: data.domains || []
      };
    } catch (err) {
      error = 'Failed to load service';
    } finally {
      loading = false;
    }
  }
  
  onMount(loadService);
</script>

<div class="max-w-4xl mx-auto space-y-6">
  <h1 class="text-2xl font-bold text-gray-900">Edit Service</h1>
  
  {#if loading}
    <div class="card">
      <p class="text-gray-500">Loading service...</p>
    </div>
  {:else if error}
    <div class="card">
      <p class="text-red-500">{error}</p>
    </div>
  {:else}
    <ServiceForm {service} isEdit={true} {serviceId} />
  {/if}
</div>
