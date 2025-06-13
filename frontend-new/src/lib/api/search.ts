import { api } from './client';
import type { SearchRequest, SearchResponse } from '$lib/types';

export const searchApi = {
  search: async (request: SearchRequest): Promise<SearchResponse> => {
    return api.post('/search/search', request);
  },
  
  searchGet: async (params: SearchRequest): Promise<SearchResponse> => {
    return api.get('/search/search', params);
  },
  
  getStatus: async (): Promise<{
    initialized: boolean;
    index_built: boolean;
    embedding_service: string;
    search_service: string;
    files: any;
  }> => {
    return api.get('/search/status');
  },
  
  rebuildIndex: async (): Promise<{ message: string; status: string }> => {
    return api.post('/search/rebuild', {});
  },
  
  initializeSearch: async (): Promise<{ message: string; status: string }> => {
    return api.post('/search/initialize');
  }
};
