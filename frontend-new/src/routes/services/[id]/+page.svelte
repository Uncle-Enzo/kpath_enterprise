<script lang="ts">
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import { servicesApi } from '$lib/api/services';
  import ServiceForm from '$lib/components/ServiceForm.svelte';
  import type { ServiceCreate } from '$lib/types';
  
  let serviceId = parseInt($page.params.id);
  let service: Partial<ServiceCreate> = {};
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
        tool_type: data.tool_type,
        interaction_modes: data.interaction_modes,
        visibility: data.visibility,
        deprecation_date: data.deprecation_date,
        deprecation_notice: data.deprecation_notice,
        success_criteria: data.success_criteria,
        default_timeout_ms: data.default_timeout_ms,
        default_retry_policy: data.default_retry_policy
      };
    } catch (err) {
      error = 'Failed to load service';
    } finally {
      loading = false;
    }
  }
  
  onMount(loadService);
</script>

<div class="max-w-6xl mx-auto space-y-6">
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
