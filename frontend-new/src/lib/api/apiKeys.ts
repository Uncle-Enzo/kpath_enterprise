import { api } from './client';
import type { APIKey, APIKeyCreate, APIKeyResponse } from '$lib/types';

export interface APIKeyUsageResponse {
  key_id: number;
  total_requests: number;
  requests_last_hour: number;
  requests_today: number;
  rate_limit: number;
  endpoints_used: Array<{ endpoint: string; count: number }>;
  daily_usage: Array<{ date: string; count: number }>;
}

export const apiKeysApi = {
  list: async (): Promise<APIKey[]> => {
    return api.get('/api-keys/');
  },
  
  create: async (data: APIKeyCreate): Promise<APIKeyResponse> => {
    return api.post('/api-keys/', data);
  },
  
  revoke: async (keyId: number): Promise<{ message: string }> => {
    return api.delete(`/api-keys/${keyId}`);
  },
  
  getUsage: async (keyId: number, days: number = 7): Promise<APIKeyUsageResponse> => {
    return api.get(`/api-keys/${keyId}/usage`, { days });
  }
};
