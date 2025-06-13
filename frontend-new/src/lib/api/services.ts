import { api } from './client';
import type { 
  Service, 
  ServiceCreate,
  ServiceUpdate,
  ServiceCapability, 
  ServiceIntegrationDetails,
  ServiceIntegrationDetailsCreate,
  ServiceIntegrationDetailsUpdate,
  ServiceAgentProtocols,
  ServiceAgentProtocolsCreate,
  ServiceAgentProtocolsUpdate,
  ServiceIndustries,
  ServiceIndustriesCreate,
  ServiceIndustriesUpdate,
  PaginationParams 
} from '$lib/types';

export interface ServiceListResponse {
  items: Service[];
  total: number;
  skip: number;
  limit: number;
}

export const servicesApi = {
  // Core Service CRUD
  list: async (params?: { skip?: number; limit?: number; status?: string; domain?: string }): Promise<ServiceListResponse> => {
    const skip = params?.skip || ((params as any)?.page - 1) * ((params as any)?.limit || 20) || 0;
    return api.get('/services', { ...params, skip });
  },
  
  get: async (id: number): Promise<Service> => {
    return api.get(`/services/${id}`);
  },
  
  create: async (data: ServiceCreate): Promise<Service> => {
    return api.post('/services', data);
  },
  
  update: async (id: number, data: ServiceUpdate): Promise<Service> => {
    return api.put(`/services/${id}`, data);
  },
  
  delete: async (id: number): Promise<void> => {
    return api.delete(`/services/${id}`);
  },
  
  // Capability Management
  addCapability: async (serviceId: number, capability: Omit<ServiceCapability, 'id' | 'service_id' | 'created_at'>): Promise<ServiceCapability> => {
    return api.post(`/services/${serviceId}/capabilities`, capability);
  },
  
  removeCapability: async (serviceId: number, capabilityId: number): Promise<void> => {
    return api.delete(`/services/${serviceId}/capabilities/${capabilityId}`);
  },
  
  // Integration Details
  getIntegration: async (serviceId: number): Promise<ServiceIntegrationDetails> => {
    return api.get(`/services/${serviceId}/integration`);
  },
  
  createIntegration: async (serviceId: number, data: ServiceIntegrationDetailsCreate): Promise<ServiceIntegrationDetails> => {
    return api.post(`/services/${serviceId}/integration`, data);
  },
  
  updateIntegration: async (serviceId: number, data: ServiceIntegrationDetailsUpdate): Promise<ServiceIntegrationDetails> => {
    return api.put(`/services/${serviceId}/integration`, data);
  },
  
  deleteIntegration: async (serviceId: number): Promise<void> => {
    return api.delete(`/services/${serviceId}/integration`);
  },
  
  // Agent Protocols
  getAgentProtocols: async (serviceId: number): Promise<ServiceAgentProtocols> => {
    return api.get(`/services/${serviceId}/agent-protocols`);
  },
  
  createAgentProtocols: async (serviceId: number, data: ServiceAgentProtocolsCreate): Promise<ServiceAgentProtocols> => {
    return api.post(`/services/${serviceId}/agent-protocols`, data);
  },
  
  updateAgentProtocols: async (serviceId: number, data: ServiceAgentProtocolsUpdate): Promise<ServiceAgentProtocols> => {
    return api.put(`/services/${serviceId}/agent-protocols`, data);
  },
  
  deleteAgentProtocols: async (serviceId: number): Promise<void> => {
    return api.delete(`/services/${serviceId}/agent-protocols`);
  },
  
  // Industries
  getIndustries: async (serviceId: number): Promise<ServiceIndustries[]> => {
    return api.get(`/services/${serviceId}/industries`);
  },
  
  addIndustry: async (serviceId: number, data: ServiceIndustriesCreate): Promise<ServiceIndustries> => {
    return api.post(`/services/${serviceId}/industries`, data);
  },
  
  updateIndustry: async (serviceId: number, industryId: number, data: ServiceIndustriesUpdate): Promise<ServiceIndustries> => {
    return api.put(`/services/${serviceId}/industries/${industryId}`, data);
  },
  
  deleteIndustry: async (serviceId: number, industryId: number): Promise<void> => {
    return api.delete(`/services/${serviceId}/industries/${industryId}`);
  }
};
