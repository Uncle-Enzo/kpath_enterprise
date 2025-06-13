-- Insert example services demonstrating new capabilities

-- 1. ESB-Connected SAP Finance Service
INSERT INTO services (name, description, tool_type, interaction_modes, visibility, version, default_timeout_ms)
VALUES (
    'SAPFinanceConnector',
    'Access SAP financial data through MuleSoft ESB for real-time balance queries and transaction history',
    'ESBEndpoint',
    ARRAY['ESB', 'SOAP'],
    'restricted',
    '1.0.0',
    30000
) ON CONFLICT (name) DO NOTHING;

-- Add integration details for SAP connector
INSERT INTO service_integration_details (
    service_id,
    access_protocol,
    base_endpoint,
    auth_method,
    auth_config,
    esb_type,
    esb_service_name,
    esb_routing_key,
    esb_operation,
    esb_adapter_type,
    request_content_type,
    response_content_type,
    rate_limit_requests,
    rate_limit_window_seconds
)
SELECT 
    id,
    'https',
    'https://esb.company.com/mulesoft/api',
    'Custom',
    '{"type": "mulesoft_token", "token_header": "X-Mule-Token"}'::jsonb,
    'MuleSoft',
    'sap-finance-connector',
    'finance.sap.v1',
    'FinanceDataRetrieval',
    'SAP',
    'text/xml',
    'text/xml',
    10,
    60
FROM services WHERE name = 'SAPFinanceConnector'
ON CONFLICT (service_id) DO NOTHING;

-- 2. External AI Agent (OpenAI)
INSERT INTO services (name, description, tool_type, interaction_modes, visibility, default_timeout_ms)
VALUES (
    'OpenAIAssistant',
    'External AI assistant for natural language processing, text generation, and analysis tasks',
    'ExternalAgent',
    ARRAY['REST', 'Webhook'],
    'restricted',
    60000
) ON CONFLICT (name) DO NOTHING;

-- Add integration details
INSERT INTO service_integration_details (
    service_id,
    access_protocol,
    base_endpoint,
    auth_method,
    auth_config,
    rate_limit_requests,
    rate_limit_window_seconds,
    circuit_breaker_config
)
SELECT 
    id,
    'https',
    'https://api.openai.com/v1',
    'APIKey',
    '{"header_name": "Authorization", "header_prefix": "Bearer"}'::jsonb,
    50,
    60,
    '{"failure_threshold": 5, "recovery_timeout_ms": 30000, "expected_error_codes": [429, 503]}'::jsonb
FROM services WHERE name = 'OpenAIAssistant'
ON CONFLICT (service_id) DO NOTHING;

-- Add agent protocol info
INSERT INTO service_agent_protocols (
    service_id,
    message_protocol,
    protocol_version,
    response_style,
    supports_streaming,
    max_context_length,
    message_examples
)
SELECT 
    id,
    'OpenAI-API',
    'v1',
    'natural_language',
    true,
    4096,
    '[{"input": "Summarize this text", "output": {"type": "completion", "text": "Summary of the text..."}}]'::jsonb
FROM services WHERE name = 'OpenAIAssistant'
ON CONFLICT (service_id) DO NOTHING;

-- 3. Legacy Mainframe System
INSERT INTO services (
    name, 
    description, 
    tool_type, 
    interaction_modes, 
    visibility,
    deprecation_date,
    deprecation_notice,
    default_timeout_ms
)
VALUES (
    'MainframeInventorySystem',
    'Legacy mainframe system for inventory management with COBOL-based transactions',
    'LegacySystem',
    ARRAY['Custom'],
    'internal',
    '2025-12-31'::timestamp,
    'Will be replaced by cloud-based inventory management system',
    45000
) ON CONFLICT (name) DO NOTHING;

-- 4. Internal Data Analysis Agent
INSERT INTO services (name, description, tool_type, interaction_modes, visibility, version)
VALUES (
    'AdvancedDataAnalysisAgent',
    'AI agent that performs complex data analysis, statistical modeling, and generates insights with visualizations',
    'InternalAgent',
    ARRAY['AgentMessage', 'REST'],
    'org-wide',
    '3.2.1'
) ON CONFLICT (name) DO NOTHING;

-- Add agent protocol
INSERT INTO service_agent_protocols (
    service_id,
    message_protocol,
    protocol_version,
    expected_input_format,
    response_style,
    requires_session_state,
    max_context_length,
    supported_languages,
    supports_streaming,
    supports_async,
    tool_schema
)
SELECT 
    id,
    'KPATH-agent-v1',
    '1.0',
    'Natural language queries about data analysis, trends, and insights',
    'structured',
    true,
    4000,
    ARRAY['en', 'es', 'fr'],
    true,
    true,
    '{
        "type": "object",
        "properties": {
            "action": {"type": "string", "enum": ["analyze", "compare", "forecast", "summarize"]},
            "data_source": {"type": "string"},
            "parameters": {"type": "object"}
        }
    }'::jsonb
FROM services WHERE name = 'AdvancedDataAnalysisAgent'
ON CONFLICT (service_id) DO NOTHING;

-- 5. Microservice Example
INSERT INTO services (name, description, tool_type, interaction_modes, visibility, version)
VALUES (
    'NotificationMicroservice',
    'High-performance microservice for multi-channel notifications (email, SMS, push, in-app)',
    'MicroService',
    ARRAY['REST', 'gRPC', 'Kafka'],
    'internal',
    '2.1.0'
) ON CONFLICT (name) DO NOTHING;

-- Add integration details
INSERT INTO service_integration_details (
    service_id,
    access_protocol,
    base_endpoint,
    auth_method,
    auth_config,
    rate_limit_requests,
    rate_limit_window_seconds,
    health_check_endpoint,
    health_check_interval_seconds
)
SELECT 
    id,
    'grpc',
    'grpc://notification-service.k8s.local:50051',
    'JWT',
    '{"issuer": "https://auth.company.com", "audience": "notification-service"}'::jsonb,
    1000,
    60,
    '/grpc.health.v1.Health/Check',
    10
FROM services WHERE name = 'NotificationMicroservice'
ON CONFLICT (service_id) DO NOTHING;

-- Add industries for all new services
INSERT INTO service_industries (service_id, industry, relevance_score, use_cases)
SELECT id, 'finance', 1.0, ARRAY['balance queries', 'transaction history', 'financial reporting']
FROM services WHERE name = 'SAPFinanceConnector'
ON CONFLICT (service_id, industry) DO NOTHING;

INSERT INTO service_industries (service_id, industry, relevance_score, use_cases)
SELECT id, 'technology', 0.9, ARRAY['AI assistance', 'content generation', 'text analysis']
FROM services WHERE name = 'OpenAIAssistant'
ON CONFLICT (service_id, industry) DO NOTHING;

INSERT INTO service_industries (service_id, industry, relevance_score, use_cases)
SELECT id, 'manufacturing', 1.0, ARRAY['inventory tracking', 'stock levels', 'warehouse management']
FROM services WHERE name = 'MainframeInventorySystem'
ON CONFLICT (service_id, industry) DO NOTHING;

INSERT INTO service_industries (service_id, industry, relevance_score, use_cases)
SELECT id, 'analytics', 1.0, ARRAY['data analysis', 'trend detection', 'predictive modeling']
FROM services WHERE name = 'AdvancedDataAnalysisAgent'
ON CONFLICT (service_id, industry) DO NOTHING;