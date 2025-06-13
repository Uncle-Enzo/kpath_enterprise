# KPATH Enterprise Service Import Guide

## Table of Contents
1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [JSON Schema Structure](#json-schema-structure)
4. [Service Fields Reference](#service-fields-reference)
5. [Examples by Service Type](#examples-by-service-type)
6. [Import Process](#import-process)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

## Overview

The KPATH Enterprise Service Import system allows you to bulk import multiple services from a single JSON file. This is ideal for:
- Initial system setup with multiple services
- Migrating services from other systems
- Bulk updates to service configurations
- Creating consistent service definitions across environments

### Supported Features
- All service types (API, Internal Agent, External Agent, ESB Endpoint, Legacy System, Microservice)
- Complete enterprise integration configurations
- Authentication and security settings
- Agent communication protocols
- Service capabilities and industries
- Validation and error handling

## Getting Started

### Step 1: Access the Import System
1. Navigate to **Services** → **Import Services**
2. Or visit: `http://localhost:5174/services/import`

### Step 2: Download Resources
- **Schema File**: Click "Download Schema" for the complete JSON schema
- **Sample File**: Click "Download Sample" for working examples

### Step 3: Create Your Import File
Use any text editor to create a JSON file following the schema structure.

## JSON Schema Structure

### Basic File Structure
```json
{
  "version": "1.0",
  "metadata": {
    "description": "Description of this import batch",
    "created_by": "your-username",
    "created_at": "2025-06-13T22:00:00Z",
    "tags": ["tag1", "tag2"]
  },
  "services": [
    {
      // Service definitions go here
    }
  ]
}
```

### Required Fields
Every import file must have:
- `version`: Schema version (currently "1.0")
- `services`: Array of service objects

Every service must have:
- `name`: Unique service name
- `description`: Service description  
- `tool_type`: One of the supported service types

## Service Fields Reference

### Core Service Fields

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `name` | string | ✅ | Unique service name | "Customer Analytics API" |
| `description` | string | ✅ | Detailed description | "Provides customer behavior analysis" |
| `tool_type` | string | ✅ | Service type | "API", "InternalAgent", "ExternalAgent", "ESBEndpoint", "LegacySystem", "MicroService" |
| `endpoint` | string | ❌ | Service endpoint URL | "https://api.company.com/v1" |
| `version` | string | ❌ | Service version | "1.2.0" |
| `status` | string | ❌ | Service status (default: "active") | "active", "inactive", "deprecated" |
| `visibility` | string | ❌ | Access level (default: "internal") | "internal", "org-wide", "public", "restricted" |
| `interaction_modes` | array | ❌ | Supported interaction types | ["sync", "async", "stream", "batch"] |
| `default_timeout_ms` | integer | ❌ | Default timeout (default: 30000) | 15000 |

### Advanced Configuration

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `success_criteria` | object | Success conditions | `{"status_codes": [200, 201], "max_response_time_ms": 2000}` |
| `default_retry_policy` | object | Retry configuration | `{"max_retries": 3, "backoff_multiplier": 1.5}` |
| `deprecation_date` | string | When service will be deprecated | "2025-12-31T23:59:59Z" |
| `deprecation_notice` | string | Deprecation explanation | "Use v2 API instead" |

### Integration Details

For services requiring integration configuration:

```json
"integration_details": {
  "access_protocol": "REST",
  "base_endpoint": "https://api.company.com/v1",
  "auth_method": "OAuth2",
  "auth_endpoint": "https://auth.company.com/oauth2/token",
  "rate_limit_requests": 1000,
  "rate_limit_window_seconds": 3600,
  "max_concurrent_requests": 50,
  "request_content_type": "application/json",
  "response_content_type": "application/json",
  "health_check_endpoint": "/health",
  "health_check_interval_seconds": 30
}
```

#### Integration Fields Reference

| Field | Description | Values |
|-------|-------------|--------|
| `access_protocol` | Communication protocol | "REST", "GraphQL", "gRPC", "SOAP", "WebSocket", "ESB" |
| `auth_method` | Authentication method | "OAuth2", "JWT", "APIKey", "Basic", "Custom" |
| `rate_limit_requests` | Max requests per window | Integer |
| `rate_limit_window_seconds` | Rate limit time window | Integer (seconds) |
| `max_concurrent_requests` | Max simultaneous requests | Integer |

#### ESB-Specific Fields

For ESB endpoints, add these fields to `integration_details`:

```json
"esb_type": "MuleSoft",
"esb_service_name": "CustomerService",
"esb_routing_key": "customer.events",
"esb_operation": "getCustomerData",
"esb_adapter_type": "HTTP",
"esb_namespace": "com.company.services",
"esb_version": "1.0"
```

### Agent Protocols

For Agent-type services (`InternalAgent`, `ExternalAgent`):

```json
"agent_protocols": {
  "message_protocol": "OpenAI",
  "protocol_version": "1.0",
  "response_style": "conversational",
  "requires_session_state": true,
  "max_context_length": 8192,
  "supported_languages": ["English", "Spanish", "French"],
  "supports_streaming": true,
  "supports_async": true,
  "supports_batch": false
}
```

#### Agent Protocol Fields

| Field | Description | Values |
|-------|-------------|--------|
| `message_protocol` | Message format | "JSON-RPC", "OpenAI", "Anthropic", "Custom" |
| `response_style` | Response formatting | "structured", "conversational", "technical", "casual" |
| `requires_session_state` | Needs conversation context | boolean |
| `supports_streaming` | Can stream responses | boolean |
| `supports_async` | Supports async operations | boolean |
| `supports_batch` | Can process batches | boolean |

### Capabilities

Define what the service can do:

```json
"capabilities": [
  {
    "capability_name": "customer_segmentation",
    "capability_desc": "Segment customers based on behavior patterns",
    "input_schema": {
      "type": "object",
      "properties": {
        "customer_ids": {"type": "array", "items": {"type": "string"}}
      }
    },
    "output_schema": {
      "type": "object", 
      "properties": {
        "segments": {"type": "array", "items": {"type": "string"}}
      }
    }
  }
]
```

### Industries

Classify service by industry and use case:

```json
"industries": [
  {
    "industry": "Retail",
    "sub_industry": "E-commerce",
    "use_case_category": "Customer Intelligence",
    "use_case_description": "Analyze customer behavior for personalized marketing",
    "business_value": "Increase customer retention by 25%",
    "typical_consumers": ["Marketing Teams", "Sales Teams"],
    "relevance_score": 95,
    "priority_rank": 1,
    "compliance_frameworks": ["GDPR", "CCPA"]
  }
]
```

## Examples by Service Type

### API Service Example

```json
{
  "name": "Customer Analytics API",
  "description": "Advanced customer analytics and insights API",
  "tool_type": "API",
  "endpoint": "https://api.company.com/customer-analytics/v1",
  "version": "1.2.0",
  "status": "active",
  "visibility": "org-wide",
  "interaction_modes": ["sync", "async"],
  "default_timeout_ms": 15000,
  "success_criteria": {
    "status_codes": [200, 201, 202],
    "max_response_time_ms": 2000
  },
  "integration_details": {
    "access_protocol": "REST",
    "base_endpoint": "https://api.company.com/customer-analytics/v1",
    "auth_method": "OAuth2",
    "auth_endpoint": "https://auth.company.com/oauth2/token",
    "rate_limit_requests": 1000,
    "rate_limit_window_seconds": 3600
  },
  "capabilities": [
    {
      "capability_name": "customer_segmentation",
      "capability_desc": "Segment customers based on behavior patterns"
    }
  ]
}
```

### Internal Agent Example

```json
{
  "name": "AI Support Agent",
  "description": "Intelligent customer support agent",
  "tool_type": "InternalAgent",
  "status": "active",
  "visibility": "internal",
  "interaction_modes": ["sync", "stream"],
  "agent_protocols": {
    "message_protocol": "OpenAI",
    "protocol_version": "1.0",
    "response_style": "conversational",
    "requires_session_state": true,
    "max_context_length": 8192,
    "supports_streaming": true,
    "supports_async": true
  },
  "capabilities": [
    {
      "capability_name": "natural_language_processing",
      "capability_desc": "Process and understand natural language queries"
    },
    {
      "capability_name": "knowledge_retrieval", 
      "capability_desc": "Retrieve relevant information from knowledge base"
    }
  ]
}
```

### ESB Endpoint Example

```json
{
  "name": "Legacy ERP Integration",
  "description": "Integration layer for legacy ERP system",
  "tool_type": "ESBEndpoint", 
  "endpoint": "https://esb.company.com/erp/v1",
  "status": "active",
  "visibility": "restricted",
  "interaction_modes": ["sync"],
  "default_timeout_ms": 45000,
  "integration_details": {
    "access_protocol": "ESB",
    "base_endpoint": "https://esb.company.com/erp/v1",
    "auth_method": "Basic",
    "esb_type": "MuleSoft",
    "esb_service_name": "ERPIntegration", 
    "esb_routing_key": "erp.financial.data",
    "esb_operation": "getFinancialData"
  }
}
```

### Legacy System Example

```json
{
  "name": "Mainframe Financial System",
  "description": "Legacy mainframe system for financial processing",
  "tool_type": "LegacySystem",
  "status": "active",
  "visibility": "restricted", 
  "interaction_modes": ["sync"],
  "default_timeout_ms": 60000,
  "deprecation_date": "2026-12-31T23:59:59Z",
  "deprecation_notice": "Will be replaced by new cloud-based system",
  "integration_details": {
    "access_protocol": "SOAP",
    "auth_method": "Custom",
    "rate_limit_requests": 10,
    "rate_limit_window_seconds": 60
  }
}
```

## Import Process

### 1. File Upload
- **Drag & Drop**: Drag your JSON file onto the upload area
- **Browse**: Click to select file from your computer
- **Validation**: File is automatically validated against the schema

### 2. Validation Results
- **Success**: Green checkmark indicates valid file
- **Errors**: Red warning shows validation issues
- **Duplicates**: Yellow warning for duplicate service names

### 3. Preview
- Click "Show Preview" to see services that will be imported
- Review metadata and service list
- Check service types and configurations

### 4. Import Execution
- Click "Import Services" to start the process
- Progress is shown in real-time
- Individual service results are displayed

### 5. Results Review
- **Summary**: Total, successful, and failed imports
- **Individual Results**: Success/failure for each service
- **Warnings**: Non-critical issues that occurred
- **Links**: Direct links to successfully created services

## Troubleshooting

### Common Validation Errors

**"Invalid JSON file"**
- Check JSON syntax with a JSON validator
- Ensure all brackets and quotes are properly closed
- Remove trailing commas

**"Service name already exists"**
- Service names must be unique
- Use different names or delete existing services first

**"Required field missing"**
- Ensure all required fields are present: `name`, `description`, `tool_type`
- Check field spelling and case sensitivity

**"Invalid tool_type"**
- Must be one of: "InternalAgent", "ExternalAgent", "API", "LegacySystem", "ESBEndpoint", "MicroService"
- Check exact spelling and capitalization

**"Invalid visibility level"**
- Must be one of: "internal", "org-wide", "public", "restricted"
- Check spelling and use lowercase

### Import Warnings

**"Integration details noted but not fully implemented"**
- Integration details are saved but some advanced features may not be active yet
- Basic service functionality will work normally

**"Failed to import capability"**
- Capability creation failed but service was created
- You can manually add capabilities later

### Performance Tips

**Large Files**
- Keep imports under 100 services per file for best performance
- Break large imports into smaller batches
- Use descriptive metadata to track import batches

**Network Issues**
- Ensure stable internet connection during import
- Large files may take several minutes to process
- Don't refresh the page during import

## Best Practices

### File Organization

**Use Descriptive Metadata**
```json
"metadata": {
  "description": "Q4 2025 Service Migration - Finance Department",
  "created_by": "admin",
  "created_at": "2025-06-13T22:00:00Z", 
  "tags": ["migration", "finance", "q4-2025"]
}
```

**Group Related Services**
- Put related services in the same import file
- Use consistent naming conventions
- Group by department, project, or functionality

### Service Definitions

**Complete Descriptions**
- Provide detailed, meaningful descriptions
- Include purpose, functionality, and usage notes
- Mention any special requirements or limitations

**Consistent Tool Types**
- Use appropriate tool types for each service
- "API" for REST/GraphQL services
- "InternalAgent" for internal AI agents
- "ExternalAgent" for third-party AI services
- "ESBEndpoint" for enterprise service bus connections
- "LegacySystem" for older systems being modernized
- "MicroService" for modern microservices

**Proper Visibility Settings**
- "internal" - Only for internal team use
- "org-wide" - Available across the organization
- "public" - Available to external consumers
- "restricted" - Limited access with approval required

### Configuration Management

**Environment-Specific Imports**
- Create separate import files for different environments
- Use environment-specific endpoints and configurations
- Include environment in the metadata description

**Version Control**
- Store import files in version control
- Use meaningful commit messages
- Tag releases that correspond to imports

**Documentation**
- Document any custom configurations
- Include contact information in metadata
- Maintain a changelog of import batches

### Security Considerations

**Sensitive Information**
- Don't include actual API keys or passwords in import files
- Use placeholder values that will be configured separately
- Store import files securely

**Access Control**
- Only admin users can perform imports
- Review service visibility settings carefully
- Consider approval workflows for sensitive services

**Validation**
- Always validate files before importing
- Test imports in non-production environments first
- Review all import results before proceeding

---

## Need Help?

- **Download Schema**: Get the complete JSON schema file
- **Download Sample**: Working examples to start from
- **API Documentation**: Visit `/docs` for complete API reference
- **Support**: Contact your system administrator

---

*This guide covers KPATH Enterprise Service Import Schema v1.0*