import { api } from './client';
import type { LoginRequest, LoginResponse, User } from '$lib/types';

export const authApi = {
  login: async (credentials: LoginRequest): Promise<LoginResponse> => {
    // Backend expects form data for OAuth2PasswordRequestForm
    const formData = new URLSearchParams();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);
    
    return api.post('/auth/login', formData.toString(), {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });
  },
  
  register: async (userData: { username: string; email: string; password: string }): Promise<User> => {
    return api.post('/auth/register', userData);
  },
  
  me: async (): Promise<User> => {
    return api.get('/auth/me');
  },
  
  refreshToken: async (): Promise<LoginResponse> => {
    return api.post('/auth/refresh');
  }
};
