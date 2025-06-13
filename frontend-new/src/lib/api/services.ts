import { api } from './client';
import type { Service, ServiceCapability, PaginationParams } from '$lib/types';

export interface ServiceCreateRequest {
  name: string;
  description: string;
  endpoint?: string;
  version?: string;
  status?: 'active' | 'inactive';
  capabilities?: Omit<ServiceCapability, 'id' | 'service_id'>[];
  domains?: string[];
}

export interface ServiceListResponse {
  items: Service[];
  total: number;
  skip: number;
  limit: number;
}

export const servicesApi = {
  list: async (params?: { skip?: number; limit?: number; status?: string; domain?: string }): Promise<ServiceListResponse> => {
    const skip = params?.skip || ((params as any)?.page - 1) * ((params as any)?.limit || 20) || 0;
    return api.get('/services', { ...params, skip });
  },
  
  get: async (id: number): Promise<Service> => {
    return api.get(`/services/${id}`);
  },
  
  create: async (data: ServiceCreateRequest): Promise<Service> => {
    return api.post('/services', data);
  },
  
  update: async (id: number, data: Partial<ServiceCreateRequest>): Promise<Service> => {
    return api.put(`/services/${id}`, data);
  },
  
  delete: async (id: number): Promise<void> => {
    return api.delete(`/services/${id}`);
  },
  
  addCapability: async (serviceId: number, capability: Omit<ServiceCapability, 'id' | 'service_id'>): Promise<ServiceCapability> => {
    return api.post(`/services/${serviceId}/capabilities`, capability);
  },
  
  removeCapability: async (serviceId: number, capabilityId: number): Promise<void> => {
    return api.delete(`/services/${serviceId}/capabilities/${capabilityId}`);
  }
};
