<script lang="ts">
  import { faArrowLeft } from '@fortawesome/free-solid-svg-icons';
  import Fa from 'svelte-fa';
  import { onMount } from 'svelte';
  import { marked } from 'marked';
  
  let htmlContent = '';
  let loading = true;
  
  onMount(async () => {
    try {
      const response = await fetch('/docs/integrations/ESB-Integration-Summary.md');
      if (response.ok) {
        const markdown = await response.text();
        htmlContent = marked(markdown);
      } else {
        htmlContent = '<h1>Error loading documentation</h1><p>Could not load the ESB Integration Summary.</p>';
      }
    } catch (error) {
      htmlContent = '<h1>Error loading documentation</h1><p>Could not load the ESB Integration Summary.</p>';
    } finally {
      loading = false;
    }
  });
</script>

<div class="min-h-screen bg-gray-50">
  <div class="max-w-5xl mx-auto p-8">
    <div class="bg-white rounded-lg shadow-sm p-8">
      <a href="/docs/integrations" class="inline-flex items-center text-primary-600 hover:text-primary-800 mb-6">
        <Fa icon={faArrowLeft} class="mr-2" />
        Back to Integration Docs
      </a>
      
      {#if loading}
        <div class="text-center py-8">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p class="mt-4 text-gray-600">Loading documentation...</p>
        </div>
      {:else}
        <div class="prose prose-lg max-w-none markdown-content">
          {@html htmlContent}
        </div>
      {/if}
    </div>
  </div>
</div>

<style>
  :global(.markdown-content h1) {
    @apply text-3xl font-bold text-gray-900 mb-4;
  }
  :global(.markdown-content h2) {
    @apply text-2xl font-semibold text-gray-800 mt-8 mb-4;
  }
  :global(.markdown-content h3) {
    @apply text-xl font-semibold text-gray-700 mt-6 mb-3;
  }
  :global(.markdown-content p) {
    @apply text-gray-600 mb-4;
  }
  :global(.markdown-content pre) {
    @apply bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto mb-4;
  }
  :global(.markdown-content code) {
    @apply bg-gray-100 text-gray-800 px-1 py-0.5 rounded text-sm;
  }
  :global(.markdown-content pre code) {
    @apply bg-transparent p-0 text-gray-100;
  }
  :global(.markdown-content ul) {
    @apply list-disc list-inside mb-4 text-gray-600;
  }
  :global(.markdown-content ol) {
    @apply list-decimal list-inside mb-4 text-gray-600;
  }
  :global(.markdown-content a) {
    @apply text-primary-600 hover:text-primary-800 underline;
  }
  :global(.markdown-content table) {
    @apply w-full mb-4;
  }
  :global(.markdown-content th) {
    @apply bg-gray-100 p-2 text-left font-semibold;
  }
  :global(.markdown-content td) {
    @apply p-2 border-t border-gray-200;
  }
</style>
