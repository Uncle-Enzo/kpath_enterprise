<script lang="ts">
  import { onMount } from 'svelte';
  import Fa from 'svelte-fa';
  import { faUpload, faDownload, faFileImport, faCheckCircle, faExclamationTriangle, faEye, faSpinner, faTimes, faBook } from '@fortawesome/free-solid-svg-icons';
  
  interface ImportResult {
    success: boolean;
    service_name: string;
    service_id?: number;
    error?: string;
    warnings: string[];
  }
  
  interface ImportResponse {
    total_services: number;
    successful_imports: number;
    failed_imports: number;
    results: ImportResult[];
    validation_errors: string[];
  }
  
  interface ValidationResponse {
    valid: boolean;
    service_count?: number;
    duplicate_names?: string[];
    metadata?: any;
    errors?: string[];
  }
  
  let fileInput: HTMLInputElement;
  let selectedFile: File | null = null;
  let dragActive = false;
  let importing = false;
  let validating = false;
  let importResults: ImportResponse | null = null;
  let validationResults: ValidationResponse | null = null;
  let previewData: any = null;
  let showPreview = false;
  
  // Download schema and sample files
  function downloadSchema() {
    const link = document.createElement('a');
    link.href = '/docs/import-schema.json';
    link.download = 'kpath-import-schema.json';
    link.click();
  }
  
  function downloadSample() {
    const link = document.createElement('a');
    link.href = '/docs/sample-import.json';
    link.download = 'sample-import.json';
    link.click();
  }
  
  // File handling
  function handleFileSelect(event: Event) {
    const target = event.target as HTMLInputElement;
    if (target.files && target.files[0]) {
      selectedFile = target.files[0];
      validateFile();
    }
  }
  
  function handleDrop(event: DragEvent) {
    event.preventDefault();
    dragActive = false;
    
    if (event.dataTransfer?.files && event.dataTransfer.files[0]) {
      selectedFile = event.dataTransfer.files[0];
      validateFile();
    }
  }
  
  function handleDragOver(event: DragEvent) {
    event.preventDefault();
    dragActive = true;
  }
  
  function handleDragLeave() {
    dragActive = false;
  }
  
  function clearFile() {
    selectedFile = null;
    validationResults = null;
    previewData = null;
    showPreview = false;
    if (fileInput) fileInput.value = '';
  }
  
  // Validation
  async function validateFile() {
    if (!selectedFile) return;
    
    validating = true;
    validationResults = null;
    
    const formData = new FormData();
    formData.append('file', selectedFile);
    
    try {
      const response = await fetch('/api/v1/import/services/validate-import', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: formData
      });
      
      validationResults = await response.json();
      
      if (validationResults?.valid) {
        await loadPreview();
      }
    } catch (error) {
      console.error('Validation error:', error);
      validationResults = {
        valid: false,
        errors: ['Failed to validate file']
      };
    } finally {
      validating = false;
    }
  }
  
  // Preview
  async function loadPreview() {
    if (!selectedFile) return;
    
    try {
      const text = await selectedFile.text();
      previewData = JSON.parse(text);
    } catch (error) {
      console.error('Preview error:', error);
    }
  }
  
  function togglePreview() {
    showPreview = !showPreview;
  }
  
  // Import
  async function importServices() {
    if (!selectedFile || !validationResults?.valid) return;
    
    importing = true;
    importResults = null;
    
    const formData = new FormData();
    formData.append('file', selectedFile);
    
    try {
      const response = await fetch('/api/v1/import/services/import', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: formData
      });
      
      importResults = await response.json();
    } catch (error) {
      console.error('Import error:', error);
      importResults = {
        total_services: 0,
        successful_imports: 0,
        failed_imports: 0,
        results: [],
        validation_errors: ['Import failed: ' + error]
      };
    } finally {
      importing = false;
    }
  }
  
  function resetImport() {
    clearFile();
    importResults = null;
  }
</script>

<div class="max-w-6xl mx-auto space-y-6">
  <div class="flex justify-between items-center">
    <div>
      <h1 class="text-2xl font-bold text-gray-900">Import Services</h1>
      <p class="text-gray-600">Bulk import multiple services from a JSON file</p>
    </div>
    <div class="flex space-x-3">
      <a href="/services/import-guide" class="btn btn-secondary">
        <Fa icon={faBook} class="mr-2" />
        Import Guide
      </a>
      <button on:click={downloadSchema} class="btn btn-secondary">
        <Fa icon={faDownload} class="mr-2" />
        Download Schema
      </button>
      <button on:click={downloadSample} class="btn btn-secondary">
        <Fa icon={faDownload} class="mr-2" />
        Download Sample
      </button>
    </div>
  </div>
  
  {#if !importResults}
    <!-- File Upload Section -->
    <div class="card">
      <h2 class="text-lg font-semibold mb-4">Select Import File</h2>
      
      <div 
        class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center transition-colors
               {dragActive ? 'border-primary-500 bg-primary-50' : 'hover:border-gray-400'}"
        on:drop={handleDrop}
        on:dragover={handleDragOver}
        on:dragleave={handleDragLeave}
      >
        {#if selectedFile}
          <div class="space-y-3">
            <Fa icon={faFileImport} class="text-4xl text-green-600 mx-auto" />
            <div>
              <p class="text-lg font-medium text-gray-900">{selectedFile.name}</p>
              <p class="text-sm text-gray-500">{(selectedFile.size / 1024).toFixed(2)} KB</p>
            </div>
            <button on:click={clearFile} class="btn btn-secondary btn-sm">
              <Fa icon={faTimes} class="mr-2" />
              Remove File
            </button>
          </div>
        {:else}
          <div class="space-y-3">
            <Fa icon={faUpload} class="text-4xl text-gray-400 mx-auto" />
            <div>
              <p class="text-lg font-medium text-gray-900">Drop your JSON file here</p>
              <p class="text-sm text-gray-500">or click to browse</p>
            </div>
            <input
              bind:this={fileInput}
              type="file"
              accept=".json"
              on:change={handleFileSelect}
              class="hidden"
            />
            <button on:click={() => fileInput?.click()} class="btn btn-primary">
              Select File
            </button>
          </div>
        {/if}
      </div>
    </div>
    
    <!-- Validation Results -->
    {#if validating}
      <div class="card">
        <div class="flex items-center justify-center py-8">
          <Fa icon={faSpinner} class="text-2xl text-primary-600 animate-spin mr-3" />
          <p class="text-lg">Validating file...</p>
        </div>
      </div>
    {:else if validationResults}
      <div class="card">
        <h2 class="text-lg font-semibold mb-4">Validation Results</h2>
        
        {#if validationResults.valid}
          <div class="bg-green-50 border border-green-200 rounded-md p-4">
            <div class="flex items-center">
              <Fa icon={faCheckCircle} class="text-green-600 mr-3" />
              <div>
                <h3 class="text-sm font-medium text-green-800">File is valid!</h3>
                <p class="text-sm text-green-700">
                  {validationResults.service_count} services ready for import
                </p>
              </div>
            </div>
            
            {#if validationResults.duplicate_names && validationResults.duplicate_names.length > 0}
              <div class="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded">
                <div class="flex items-center">
                  <Fa icon={faExclamationTriangle} class="text-yellow-600 mr-2" />
                  <p class="text-sm text-yellow-800">
                    Duplicate service names found: {validationResults.duplicate_names.join(', ')}
                  </p>
                </div>
              </div>
            {/if}
          </div>
          
          <div class="mt-4 flex justify-between items-center">
            <button on:click={togglePreview} class="btn btn-secondary">
              <Fa icon={faEye} class="mr-2" />
              {showPreview ? 'Hide' : 'Show'} Preview
            </button>
            
            <button 
              on:click={importServices}
              disabled={importing || (validationResults.duplicate_names && validationResults.duplicate_names.length > 0)}
              class="btn btn-primary"
            >
              {#if importing}
                <Fa icon={faSpinner} class="mr-2 animate-spin" />
                Importing...
              {:else}
                <Fa icon={faFileImport} class="mr-2" />
                Import Services
              {/if}
            </button>
          </div>
        {:else}
          <div class="bg-red-50 border border-red-200 rounded-md p-4">
            <div class="flex items-center mb-3">
              <Fa icon={faExclamationTriangle} class="text-red-600 mr-3" />
              <h3 class="text-sm font-medium text-red-800">Validation failed</h3>
            </div>
            <ul class="text-sm text-red-700 space-y-1">
              {#each validationResults.errors || [] as error}
                <li>• {error}</li>
              {/each}
            </ul>
          </div>
        {/if}
      </div>
    {/if}
    
    <!-- Preview Section -->
    {#if showPreview && previewData}
      <div class="card">
        <h2 class="text-lg font-semibold mb-4">File Preview</h2>
        
        <div class="bg-gray-50 rounded-lg p-4">
          <div class="mb-4">
            <h3 class="font-medium text-gray-900">Metadata</h3>
            <div class="text-sm text-gray-600">
              <p>Version: {previewData.version}</p>
              {#if previewData.metadata?.description}
                <p>Description: {previewData.metadata.description}</p>
              {/if}
              {#if previewData.metadata?.created_by}
                <p>Created by: {previewData.metadata.created_by}</p>
              {/if}
            </div>
          </div>
          
          <div>
            <h3 class="font-medium text-gray-900 mb-2">Services ({previewData.services?.length || 0})</h3>
            <div class="space-y-2 max-h-64 overflow-y-auto">
              {#each previewData.services || [] as service}
                <div class="bg-white p-3 rounded border">
                  <div class="flex justify-between items-start">
                    <div>
                      <p class="font-medium text-gray-900">{service.name}</p>
                      <p class="text-sm text-gray-600">{service.description}</p>
                    </div>
                    <span class="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded">
                      {service.tool_type}
                    </span>
                  </div>
                  {#if service.capabilities && service.capabilities.length > 0}
                    <div class="mt-2">
                      <p class="text-xs text-gray-500">
                        {service.capabilities.length} capabilities
                      </p>
                    </div>
                  {/if}
                </div>
              {/each}
            </div>
          </div>
        </div>
      </div>
    {/if}
  {:else}
    <!-- Import Results -->
    <div class="card">
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-lg font-semibold">Import Results</h2>
        <button on:click={resetImport} class="btn btn-secondary">
          Import Another File
        </button>
      </div>
      
      <!-- Summary -->
      <div class="grid grid-cols-3 gap-4 mb-6">
        <div class="bg-blue-50 p-4 rounded-lg">
          <div class="text-2xl font-bold text-blue-600">{importResults.total_services}</div>
          <div class="text-sm text-blue-800">Total Services</div>
        </div>
        <div class="bg-green-50 p-4 rounded-lg">
          <div class="text-2xl font-bold text-green-600">{importResults.successful_imports}</div>
          <div class="text-sm text-green-800">Successful</div>
        </div>
        <div class="bg-red-50 p-4 rounded-lg">
          <div class="text-2xl font-bold text-red-600">{importResults.failed_imports}</div>
          <div class="text-sm text-red-800">Failed</div>
        </div>
      </div>
      
      <!-- Validation Errors -->
      {#if importResults.validation_errors && importResults.validation_errors.length > 0}
        <div class="bg-red-50 border border-red-200 rounded-md p-4 mb-4">
          <h3 class="text-sm font-medium text-red-800 mb-2">Validation Errors</h3>
          <ul class="text-sm text-red-700 space-y-1">
            {#each importResults.validation_errors as error}
              <li>• {error}</li>
            {/each}
          </ul>
        </div>
      {/if}
      
      <!-- Individual Results -->
      <div class="space-y-3">
        {#each importResults.results as result}
          <div class="border rounded-lg p-4 {result.success ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}">
            <div class="flex items-center justify-between">
              <div class="flex items-center">
                <Fa 
                  icon={result.success ? faCheckCircle : faExclamationTriangle} 
                  class="{result.success ? 'text-green-600' : 'text-red-600'} mr-3"
                />
                <div>
                  <p class="font-medium {result.success ? 'text-green-800' : 'text-red-800'}">
                    {result.service_name}
                  </p>
                  {#if result.error}
                    <p class="text-sm text-red-700">{result.error}</p>
                  {/if}
                </div>
              </div>
              {#if result.success && result.service_id}
                <a href="/services/{result.service_id}" class="text-sm text-primary-600 hover:text-primary-800">
                  View Service →
                </a>
              {/if}
            </div>
            
            {#if result.warnings && result.warnings.length > 0}
              <div class="mt-2 pl-8">
                <p class="text-xs text-yellow-700 font-medium">Warnings:</p>
                <ul class="text-xs text-yellow-600 space-y-1">
                  {#each result.warnings as warning}
                    <li>• {warning}</li>
                  {/each}
                </ul>
              </div>
            {/if}
          </div>
        {/each}
      </div>
    </div>
  {/if}
</div>

<style>
  .animate-spin {
    animation: spin 1s linear infinite;
  }
  
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
</style>