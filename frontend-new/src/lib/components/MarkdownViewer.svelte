<script lang="ts">
  import { marked } from 'marked';
  import { faArrowLeft } from '@fortawesome/free-solid-svg-icons';
  import Fa from 'svelte-fa';
  
  export let content: string = '';
  export let title: string = '';
  
  // Configure marked for better code highlighting
  marked.setOptions({
    gfm: true,
    breaks: true,
    pedantic: false,
    sanitize: false,
    smartLists: true,
    smartypants: false
  });
  
  $: htmlContent = marked(content);
</script>

<div class="min-h-screen bg-gray-50">
  <div class="max-w-5xl mx-auto p-8">
    <div class="bg-white rounded-lg shadow-sm p-8">
      <a href="/docs/integrations" class="inline-flex items-center text-primary-600 hover:text-primary-800 mb-6">
        <Fa icon={faArrowLeft} class="mr-2" />
        Back to Integration Docs
      </a>
      
      <div class="prose prose-lg max-w-none">
        {@html htmlContent}
      </div>
    </div>
  </div>
</div>

<style>
  :global(.prose pre) {
    background-color: #1e293b;
    color: #e2e8f0;
    padding: 1rem;
    border-radius: 0.375rem;
    overflow-x: auto;
  }
  
  :global(.prose code) {
    background-color: #e5e7eb;
    color: #1f2937;
    padding: 0.125rem 0.25rem;
    border-radius: 0.25rem;
    font-size: 0.875em;
  }
  
  :global(.prose pre code) {
    background-color: transparent;
    color: inherit;
    padding: 0;
  }
  
  :global(.prose h1) {
    color: #1e40af;
    font-weight: 700;
  }
  
  :global(.prose h2) {
    color: #2563eb;
    font-weight: 600;
    margin-top: 2rem;
  }
  
  :global(.prose h3) {
    color: #3b82f6;
    font-weight: 600;
  }
  
  :global(.prose a) {
    color: #2563eb;
    text-decoration: underline;
  }
  
  :global(.prose a:hover) {
    color: #1d4ed8;
  }
  
  :global(.prose table) {
    width: 100%;
    border-collapse: collapse;
  }
  
  :global(.prose th) {
    background-color: #f3f4f6;
    padding: 0.75rem;
    text-align: left;
    font-weight: 600;
  }
  
  :global(.prose td) {
    padding: 0.75rem;
    border-top: 1px solid #e5e7eb;
  }
</style>
