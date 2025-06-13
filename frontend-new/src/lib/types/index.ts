// User and Authentication Types
export interface User {
  id: number;
  username: string;
  email: string;
  role: 'admin' | 'editor' | 'viewer' | 'user';
  created_at: string;
  updated_at: string;
  is_active: boolean;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// Service Types
export interface Service {
  id: number;
  name: string;
  description: string;
  endpoint?: string;
  version?: string;
  status: 'active' | 'inactive';
  created_at: string;
  updated_at: string;
  capabilities?: ServiceCapability[];
  domains?: string[];
}

export interface ServiceCapability {
  id: number;
  service_id: number;
  capability_name: string;
  capability_desc: string;
  input_schema?: any;
  output_schema?: any;
}

// Search Types
export interface SearchRequest {
  query: string;
  limit?: number;
  min_score?: number;
  domains?: string[];
  capabilities?: string[];
}

export interface SearchResult {
  service_id: number;
  score: number;
  rank: number;
  service: Service;
  distance?: number;
}

export interface SearchResponse {
  query: string;
  results: SearchResult[];
  total_results: number;
  search_time_ms: number;
  user_id: number;
}

// API Key Types
export interface APIKey {
  id: number;
  name: string;
  prefix: string;
  last_used?: string;
  expires_at?: string;
  created_at: string;
  active: boolean;
}

export interface APIKeyCreate {
  name: string;
  permissions?: Record<string, any>;
  expires_in_days?: number;
  rate_limit?: number;
}

export interface APIKeyResponse {
  api_key: string;
  id: number;
  name: string;
  prefix: string;
  permissions: Record<string, any>;
  expires_at?: string;
  created_at: string;
  rate_limit: number;
}

// Common Types
export interface PaginationParams {
  page?: number;
  limit?: number;
}

export interface ApiError {
  detail: string;
  status: number;
}
