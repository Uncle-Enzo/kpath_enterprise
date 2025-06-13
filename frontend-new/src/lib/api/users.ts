import { api } from './client';
import type { User, PaginationParams } from '$lib/types';

export interface UserCreateRequest {
  username: string;
  email: string;
  password: string;
  role: 'admin' | 'editor' | 'viewer' | 'user';
}

export interface UserListResponse {
  users: User[];
  total: number;
  page: number;
  limit: number;
}

export const usersApi = {
  list: async (params?: PaginationParams): Promise<User[]> => {
    // Backend returns User[] directly, not wrapped in an object
    return api.get('/users/', params);
  },
  
  get: async (id: number): Promise<User> => {
    return api.get(`/users/${id}`);
  },
  
  create: async (data: UserCreateRequest): Promise<User> => {
    return api.post('/users/', data);
  },
  
  update: async (id: number, data: Partial<UserCreateRequest>): Promise<User> => {
    return api.put(`/users/${id}`, data);
  },
  
  delete: async (id: number): Promise<void> => {
    return api.delete(`/users/${id}`);
  }
};
