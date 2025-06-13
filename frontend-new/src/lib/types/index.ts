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
  status: 'active' | 'inactive' | 'deprecated';
  created_at: string;
  updated_at: string;
  
  // New enterprise integration fields
  tool_type: 'InternalAgent' | 'ExternalAgent' | 'API' | 'LegacySystem' | 'ESBEndpoint' | 'MicroService';
  interaction_modes?: string[];
  visibility: 'internal' | 'org-wide' | 'public' | 'restricted';
  deprecation_date?: string;
  deprecation_notice?: string;
  success_criteria?: Record<string, any>;
  default_timeout_ms: number;
  default_retry_policy?: Record<string, any>;
  
  // Relationships
  capabilities?: ServiceCapability[];
  industries?: ServiceIndustry[];
  integration_details?: ServiceIntegrationDetails;
  agent_protocols?: ServiceAgentProtocols;
}

export interface ServiceCreate {
  name: string;
  description: string;
  endpoint?: string;
  version?: string;
  status?: 'active' | 'inactive' | 'deprecated';
  tool_type?: 'InternalAgent' | 'ExternalAgent' | 'API' | 'LegacySystem' | 'ESBEndpoint' | 'MicroService';
  interaction_modes?: string[];
  visibility?: 'internal' | 'org-wide' | 'public' | 'restricted';
  deprecation_date?: string;
  deprecation_notice?: string;
  success_criteria?: Record<string, any>;
  default_timeout_ms?: number;
  default_retry_policy?: Record<string, any>;
}

export interface ServiceUpdate extends Partial<ServiceCreate> {}

export interface ServiceCapability {
  id: number;
  service_id: number;
  capability_name?: string;
  capability_desc: string;
  input_schema?: any;
  output_schema?: any;
  created_at: string;
}

export interface ServiceIndustry {
  id: number;
  service_id: number;
  domain: string;
}

// Integration Details Types
export interface ServiceIntegrationDetails {
  id: number;
  service_id: number;
  access_protocol: string;
  base_endpoint?: string;
  
  // Authentication
  auth_method?: string;
  auth_config?: Record<string, any>;
  auth_endpoint?: string;
  
  // Rate Limiting & Performance
  rate_limit_requests?: number;
  rate_limit_window_seconds?: number;
  max_concurrent_requests?: number;
  circuit_breaker_config?: Record<string, any>;
  
  // Request/Response Configuration
  default_headers?: Record<string, any>;
  request_content_type?: string;
  response_content_type?: string;
  request_transform?: Record<string, any>;
  response_transform?: Record<string, any>;
  
  // ESB Specific Fields
  esb_type?: string;
  esb_service_name?: string;
  esb_routing_key?: string;
  esb_operation?: string;
  esb_adapter_type?: string;
  esb_namespace?: string;
  esb_version?: string;
  
  // Health Check
  health_check_endpoint?: string;
  health_check_interval_seconds?: number;
  
  created_at: string;
  updated_at: string;
}

export interface ServiceIntegrationDetailsCreate extends Omit<ServiceIntegrationDetails, 'id' | 'service_id' | 'created_at' | 'updated_at'> {}
export interface ServiceIntegrationDetailsUpdate extends Partial<ServiceIntegrationDetailsCreate> {}

// Agent Protocol Types
export interface ServiceAgentProtocols {
  id: number;
  service_id: number;
  
  // Protocol Information
  message_protocol: string;
  protocol_version?: string;
  expected_input_format?: string;
  response_style?: string;
  
  // Communication Details
  message_examples?: Record<string, any>;
  tool_schema?: Record<string, any>;
  input_validation_rules?: Record<string, any>;
  output_parsing_rules?: Record<string, any>;
  
  // Capabilities
  requires_session_state: boolean;
  max_context_length?: number;
  supported_languages?: string[];
  supports_streaming: boolean;
  supports_async: boolean;
  supports_batch: boolean;
  
  created_at: string;
}

export interface ServiceAgentProtocolsCreate extends Omit<ServiceAgentProtocols, 'id' | 'service_id' | 'created_at'> {}
export interface ServiceAgentProtocolsUpdate extends Partial<ServiceAgentProtocolsCreate> {}

// Service Industries Types
export interface ServiceIndustries {
  id: number;
  service_id: number;
  
  // Industry Classification
  industry: string;
  sub_industry?: string;
  use_case_category?: string;
  
  // Use Case Details
  use_case_description?: string;
  business_value?: string;
  typical_consumers?: string[];
  
  // Relevance & Priority
  relevance_score?: number;
  priority_rank?: number;
  compliance_frameworks?: string[];
  
  created_at: string;
}

export interface ServiceIndustriesCreate extends Omit<ServiceIndustries, 'id' | 'service_id' | 'created_at'> {}
export interface ServiceIndustriesUpdate extends Partial<ServiceIndustriesCreate> {}

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

// Helper type for tool types
export const TOOL_TYPES = [
  { value: 'API', label: 'API Endpoint' },
  { value: 'InternalAgent', label: 'Internal Agent' },
  { value: 'ExternalAgent', label: 'External Agent' },
  { value: 'LegacySystem', label: 'Legacy System' },
  { value: 'ESBEndpoint', label: 'ESB Endpoint' },
  { value: 'MicroService', label: 'Microservice' }
] as const;

export const VISIBILITY_LEVELS = [
  { value: 'internal', label: 'Internal Only' },
  { value: 'org-wide', label: 'Organization Wide' },
  { value: 'public', label: 'Public' },
  { value: 'restricted', label: 'Restricted Access' }
] as const;

export const INTERACTION_MODES = [
  { value: 'sync', label: 'Synchronous' },
  { value: 'async', label: 'Asynchronous' },
  { value: 'stream', label: 'Streaming' },
  { value: 'batch', label: 'Batch Processing' }
] as const;