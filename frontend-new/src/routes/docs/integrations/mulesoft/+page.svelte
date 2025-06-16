<script lang="ts">
  import { faArrowLeft } from '@fortawesome/free-solid-svg-icons';
  import Fa from 'svelte-fa';
  import type { PageData } from './$types';
  
  export let data: PageData;
</script>

<div class="min-h-screen bg-gray-50">
  <div class="max-w-5xl mx-auto p-8">
    <div class="bg-white rounded-lg shadow-sm p-8">
      <a href="/docs/integrations" class="inline-flex items-center text-primary-600 hover:text-primary-800 mb-6">
        <Fa icon={faArrowLeft} class="mr-2" />
        Back to Integration Docs
      </a>
      
      <div class="prose prose-lg max-w-none markdown-content">
        {@html data.htmlContent}
      </div>
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
  
  :global(.markdown-content blockquote) {
    @apply border-l-4 border-gray-300 pl-4 italic text-gray-600 mb-4;
  }
</style>
