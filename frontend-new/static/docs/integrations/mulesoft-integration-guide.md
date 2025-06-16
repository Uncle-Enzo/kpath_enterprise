# KPATH Enterprise - Mulesoft Integration Guide

## Overview

This guide demonstrates how to integrate KPATH Enterprise with Mulesoft to enable dynamic tool and service discovery for your integration flows. KPATH acts as a semantic discovery layer that helps Mulesoft applications find the right APIs, services, and tools based on natural language queries.

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Mulesoft      │────▶│  KPATH Enterprise │────▶│  Discovered     │
│   Application   │◀────│  Discovery API    │     │  Services       │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

## Prerequisites

- KPATH Enterprise instance running (default: http://localhost:8000)
- Mulesoft Anypoint Studio 7.x or later
- API Key or JWT token for KPATH authentication
- HTTP Connector in your Mule palette

## Integration Patterns

### 1. Direct HTTP Integration

#### Basic Service Discovery Flow

```xml
<?xml version="1.0" encoding="UTF-8"?>
<mule xmlns:http="http://www.mulesoft.org/schema/mule/http"
      xmlns:ee="http://www.mulesoft.org/schema/mule/ee/core"
      xmlns="http://www.mulesoft.org/schema/mule/core"
      xmlns:doc="http://www.mulesoft.org/schema/mule/documentation"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:schemaLocation="http://www.mulesoft.org/schema/mule/core 
        http://www.mulesoft.org/schema/mule/core/current/mule.xsd
        http://www.mulesoft.org/schema/mule/http 
        http://www.mulesoft.org/schema/mule/http/current/mule-http.xsd
        http://www.mulesoft.org/schema/mule/ee/core 
        http://www.mulesoft.org/schema/mule/ee/core/current/mule-ee.xsd">

    <!-- KPATH Configuration -->
    <http:request-config name="KPATH_HTTP_Config" doc:name="HTTP Request configuration">
        <http:request-connection host="${kpath.host}" port="${kpath.port}" />
    </http:request-config>

    <!-- Main Discovery Flow -->
    <flow name="kpath-service-discovery-flow">
        <http:listener doc:name="Listener" config-ref="HTTP_Listener_config" path="/discover"/>
        
        <!-- Transform incoming request to KPATH search format -->
        <ee:transform doc:name="Prepare KPATH Request">
            <ee:message>
                <ee:set-payload><![CDATA[%dw 2.0
output application/json
---
{
    query: attributes.queryParams.query default "customer management",
    limit: attributes.queryParams.limit default 5,
    domains: if (attributes.queryParams.domains?) 
             attributes.queryParams.domains splitBy "," 
             else null,
    capabilities: if (attributes.queryParams.capabilities?) 
                  attributes.queryParams.capabilities splitBy "," 
                  else null
}]]></ee:set-payload>
            </ee:message>
        </ee:transform>

        <!-- Call KPATH Discovery API -->
        <http:request method="POST" doc:name="KPATH Service Discovery" 
                     config-ref="KPATH_HTTP_Config" 
                     path="/api/v1/search/search">
            <http:headers><![CDATA[#[{
                "X-API-Key": p('kpath.api.key'),
                "Content-Type": "application/json"
            }]]]></http:headers>
        </http:request>

        <!-- Process and route based on discovered services -->
        <ee:transform doc:name="Process Discovery Results">
            <ee:message>
                <ee:set-payload><![CDATA[%dw 2.0
output application/json
---
{
    discovered_services: payload.results map {
        service_name: $.name,
        description: $.description,
        endpoint: $.endpoint,
        similarity_score: $.similarity_score,
        tools: $.tools default [],
        auth_type: $.auth_type default "bearer_token",
        agent_protocol: $.agent_protocol default "kpath-v1"
    },
    query_id: payload.query_id,
    total_found: sizeOf(payload.results)
}]]></ee:set-payload>
            </ee:message>
        </ee:transform>

        <!-- Choice router based on discovered services -->
        <choice doc:name="Route to Service">
            <when expression="#[sizeOf(payload.discovered_services) > 0]">
                <flow-ref name="invoke-best-service-flow" doc:name="Invoke Best Service"/>
            </when>
            <otherwise>
                <set-payload value='{"error": "No suitable service found"}' 
                            mimeType="application/json" doc:name="No Service Found"/>
            </otherwise>
        </choice>
    </flow>

    <!-- Sub-flow to invoke the best matching service -->
    <sub-flow name="invoke-best-service-flow">
        <set-variable variableName="selectedService" 
                     value="#[payload.discovered_services[0]]" 
                     doc:name="Select Best Service"/>
        
        <!-- Dynamic service invocation based on discovery -->
        <http:request method="#[vars.selectedService.method default 'POST']" 
                     doc:name="Invoke Discovered Service"
                     url="#[vars.selectedService.endpoint]">
            <http:headers><![CDATA[#[{
                "Authorization": "Bearer " ++ (vars.selectedService.auth_token default p('default.auth.token')),
                "Content-Type": "application/json"
            }]]]></http:headers>
        </http:request>
    </sub-flow>
</mule>
```

### 2. KPATH Custom Connector

Create a reusable KPATH connector for Mulesoft:

```java
package com.kpath.connector;

import org.mule.runtime.extension.api.annotation.Extension;
import org.mule.runtime.extension.api.annotation.Operations;
import org.mule.runtime.extension.api.annotation.connectivity.ConnectionProviders;
import org.mule.runtime.extension.api.annotation.param.Parameter;
import org.mule.runtime.extension.api.annotation.param.Optional;
import org.mule.runtime.extension.api.annotation.param.display.DisplayName;
import org.mule.runtime.extension.api.annotation.param.display.Example;

@Extension(name = "KPATH")
@Operations(KPATHOperations.class)
@ConnectionProviders(KPATHConnectionProvider.class)
public class KPATHConnector {

    @Parameter
    @DisplayName("KPATH Base URL")
    @Example("http://localhost:8000")
    private String baseUrl;

    @Parameter
    @DisplayName("API Key")
    @Optional
    private String apiKey;

    @Parameter
    @DisplayName("Use JWT Authentication")
    @Optional(defaultValue = "false")
    private boolean useJWT;

    // Getters and setters
}
```

#### KPATH Operations Class

```java
package com.kpath.connector;

import org.mule.runtime.extension.api.annotation.param.MediaType;
import org.mule.runtime.extension.api.annotation.param.Optional;
import org.mule.runtime.extension.api.annotation.param.Parameter;
import org.mule.runtime.extension.api.annotation.param.display.DisplayName;
import org.mule.runtime.extension.api.annotation.param.display.Summary;
import org.mule.runtime.extension.api.runtime.operation.Result;

import java.util.List;
import java.util.Map;

public class KPATHOperations {

    @MediaType(value = MediaType.APPLICATION_JSON)
    @DisplayName("Discover Services")
    @Summary("Discover services based on natural language query")
    public Result<Map<String, Object>, Void> discoverServices(
            @Parameter String query,
            @Optional(defaultValue = "5") Integer limit,
            @Optional List<String> domains,
            @Optional List<String> capabilities,
            KPATHConnection connection) {
        
        // Build request
        Map<String, Object> request = new HashMap<>();
        request.put("query", query);
        request.put("limit", limit);
        if (domains != null) request.put("domains", domains);
        if (capabilities != null) request.put("capabilities", capabilities);
        
        // Execute search
        return connection.searchServices(request);
    }

    @MediaType(value = MediaType.APPLICATION_JSON)
    @DisplayName("Get Service Tools")
    @Summary("Get available tools for a specific service")
    public Result<List<Map<String, Object>>, Void> getServiceTools(
            @Parameter Integer serviceId,
            KPATHConnection connection) {
        
        return connection.getTools(serviceId);
    }

    @MediaType(value = MediaType.APPLICATION_JSON)
    @DisplayName("Get Orchestration Analytics")
    @Summary("Get analytics for agent orchestration")
    public Result<Map<String, Object>, Void> getOrchestrationAnalytics(
            KPATHConnection connection) {
        
        return connection.getAnalytics();
    }
}
```

### 3. Anypoint Exchange Integration

Publish discovered services to Anypoint Exchange:

```xml
<flow name="sync-kpath-to-exchange">
    <scheduler doc:name="Scheduler">
        <scheduling-strategy>
            <fixed-frequency frequency="1" timeUnit="HOURS"/>
        </scheduling-strategy>
    </scheduler>
    
    <!-- Get all services from KPATH -->
    <http:request method="GET" doc:name="Get All Services" 
                 config-ref="KPATH_HTTP_Config" 
                 path="/api/v1/services">
        <http:headers><![CDATA[#[{
            "X-API-Key": p('kpath.api.key')
        }]]]></http:headers>
    </http:request>
    
    <!-- Transform to Exchange format -->
    <ee:transform doc:name="Transform to Exchange Format">
        <ee:message>
            <ee:set-payload><![CDATA[%dw 2.0
output application/json
---
payload.services map {
    name: $.name,
    description: $.description,
    version: $.version default "1.0.0",
    type: "rest-api",
    assetId: lower($.name) replace " " with "-",
    groupId: p('exchange.group.id'),
    tags: ($.capabilities default []) ++ 
          ($.domains default []) ++ 
          ["kpath-discovered"],
    documentation: {
        pages: [{
            pageName: "Home",
            content: "# " ++ $.name ++ "\n\n" ++ $.description ++ 
                    "\n\n## Endpoint\n" ++ $.endpoint ++
                    "\n\n## Tools\n" ++ write($.tools, "application/json")
        }]
    }
}]]></ee:set-payload>
        </ee:message>
    </ee:transform>
    
    <!-- Publish each service to Exchange -->
    <foreach doc:name="For Each Service">
        <http:request method="POST" doc:name="Publish to Exchange"
                     url="https://anypoint.mulesoft.com/exchange/api/v2/assets">
            <http:headers><![CDATA[#[{
                "Authorization": "Bearer " ++ p('anypoint.token'),
                "Content-Type": "application/json"
            }]]]></http:headers>
        </http:request>
    </foreach>
</flow>
```

### 4. Dynamic Router Pattern

Use KPATH for dynamic routing decisions:

```xml
<flow name="dynamic-routing-flow">
    <http:listener doc:name="Listener" config-ref="HTTP_Listener_config" path="/process"/>
    
    <!-- Store original payload -->
    <set-variable variableName="originalPayload" value="#[payload]" doc:name="Store Payload"/>
    
    <!-- Analyze request intent -->
    <ee:transform doc:name="Extract Intent">
        <ee:message>
            <ee:set-payload><![CDATA[%dw 2.0
output application/json
---
{
    query: payload.intent default payload.action default "process data",
    limit: 3,
    capabilities: payload.requiredCapabilities default []
}]]></ee:set-payload>
        </ee:message>
    </ee:transform>
    
    <!-- Discover appropriate service -->
    <flow-ref name="kpath-service-discovery-flow" doc:name="Discover Service"/>
    
    <!-- Dynamic routing based on discovery -->
    <choice doc:name="Dynamic Route">
        <when expression="#[payload.discovered_services[0].name == 'CustomerService']">
            <flow-ref name="customer-service-flow" doc:name="Customer Service"/>
        </when>
        <when expression="#[payload.discovered_services[0].name == 'PaymentService']">
            <flow-ref name="payment-service-flow" doc:name="Payment Service"/>
        </when>
        <when expression="#[payload.discovered_services[0].name == 'NotificationService']">
            <flow-ref name="notification-service-flow" doc:name="Notification Service"/>
        </when>
        <otherwise>
            <!-- Generic service invocation -->
            <flow-ref name="generic-service-invocation" doc:name="Generic Invocation"/>
        </otherwise>
    </choice>
</flow>
```

### 5. Caching Pattern

Implement caching for frequently used queries:

```xml
<flow name="cached-discovery-flow">
    <http:listener doc:name="Listener" config-ref="HTTP_Listener_config" path="/cached-discover"/>
    
    <!-- Generate cache key -->
    <set-variable variableName="cacheKey" 
                 value="#['kpath:' ++ attributes.queryParams.query]" 
                 doc:name="Generate Cache Key"/>
    
    <!-- Check cache -->
    <cache:contains cachingStrategy-ref="kpath-cache-strategy" key="#[vars.cacheKey]">
        <choice doc:name="Cache Decision">
            <when expression="#[payload]">
                <!-- Retrieve from cache -->
                <cache:retrieve cachingStrategy-ref="kpath-cache-strategy" key="#[vars.cacheKey]"/>
                <logger message="Retrieved from cache" level="INFO"/>
            </when>
            <otherwise>
                <!-- Call KPATH and cache result -->
                <flow-ref name="kpath-service-discovery-flow" doc:name="KPATH Discovery"/>
                <cache:store cachingStrategy-ref="kpath-cache-strategy" key="#[vars.cacheKey]"/>
                <logger message="Stored in cache" level="INFO"/>
            </otherwise>
        </choice>
    </cache:contains>
</flow>
```

## Configuration Properties

```properties
# config.properties
kpath.host=localhost
kpath.port=8000
kpath.api.key=kpe_your_api_key_here
kpath.timeout=30000
kpath.cache.ttl=3600

# Authentication
kpath.auth.type=api-key
kpath.jwt.token=${secure::jwt.token}

# Circuit Breaker
kpath.circuit.breaker.enabled=true
kpath.circuit.breaker.failure.threshold=5
kpath.circuit.breaker.timeout=60000

# Retry Policy
kpath.retry.count=3
kpath.retry.delay=1000
```

## Error Handling

```xml
<error-handler name="kpath-error-handler">
    <on-error-continue type="HTTP:UNAUTHORIZED">
        <logger message="KPATH Authentication failed" level="ERROR"/>
        <ee:transform>
            <ee:message>
                <ee:set-payload><![CDATA[%dw 2.0
output application/json
---
{
    error: "Authentication failed",
    message: "Invalid KPATH API key or token"
}]]></ee:set-payload>
            </ee:message>
        </ee:transform>
    </on-error-continue>
    
    <on-error-continue type="HTTP:NOT_FOUND">
        <logger message="KPATH service not found" level="WARN"/>
        <ee:transform>
            <ee:message>
                <ee:set-payload><![CDATA[%dw 2.0
output application/json
---
{
    error: "Service not found",
    message: "No matching services found for query"
}]]></ee:set-payload>
            </ee:message>
        </ee:transform>
    </on-error-continue>
    
    <on-error-continue type="HTTP:TIMEOUT">
        <logger message="KPATH timeout" level="ERROR"/>
        <!-- Fallback to cached results or default service -->
        <flow-ref name="fallback-service-flow"/>
    </on-error-continue>
</error-handler>
```

## Monitoring and Metrics

```xml
<flow name="kpath-metrics-flow">
    <!-- Collect KPATH usage metrics -->
    <sub-flow name="collect-kpath-metrics">
        <ee:transform doc:name="Prepare Metrics">
            <ee:message>
                <ee:set-payload><![CDATA[%dw 2.0
output application/json
---
{
    timestamp: now(),
    query: vars.query,
    responseTime: vars.responseTime,
    servicesFound: sizeOf(payload.results default []),
    selectedService: payload.results[0].name default "none",
    success: payload.results? and sizeOf(payload.results) > 0
}]]></ee:set-payload>
            </ee:message>
        </ee:transform>
        
        <!-- Send to monitoring system -->
        <http:request method="POST" doc:name="Send Metrics"
                     config-ref="Monitoring_HTTP_Config"
                     path="/metrics/kpath"/>
    </sub-flow>
</flow>
```

## Best Practices

### 1. Connection Management
- Use connection pooling for KPATH requests
- Implement circuit breakers for resilience
- Set appropriate timeouts (recommended: 30 seconds)

### 2. Security
- Store API keys in secure properties
- Use HTTPS for production deployments
- Implement rate limiting to respect KPATH limits

### 3. Performance
- Cache frequently used queries (TTL: 1 hour)
- Use asynchronous processing for non-critical discoveries
- Batch service discovery requests when possible

### 4. Error Handling
- Implement comprehensive error handling
- Provide fallback mechanisms
- Log all failures for troubleshooting

### 5. Monitoring
- Track discovery success rates
- Monitor response times
- Alert on authentication failures

## Example Use Cases

### 1. Customer 360 Integration
```xml
<flow name="customer-360-flow">
    <!-- Discover all customer-related services -->
    <kpath:discover-services query="customer data profile history"
                            limit="10"
                            domains="CRM,Sales,Support"
                            config-ref="KPATH_Config"/>
    
    <!-- Aggregate data from all discovered services -->
    <foreach doc:name="For Each Service">
        <http:request method="GET" 
                     url="#[payload.endpoint ++ '/customer/' ++ vars.customerId]"/>
        <ee:transform>
            <ee:variables>
                <ee:set-variable variableName="customerData">
                    <![CDATA[vars.customerData ++ payload]]>
                </ee:set-variable>
            </ee:variables>
        </ee:transform>
    </foreach>
</flow>
```

### 2. Payment Processing Router
```xml
<flow name="payment-router-flow">
    <!-- Discover payment services based on criteria -->
    <ee:transform>
        <ee:message>
            <ee:set-payload><![CDATA[%dw 2.0
output application/json
---
{
    query: "payment processing " ++ payload.currency ++ " " ++ payload.method,
    capabilities: ["process_payment", "fraud_check"],
    limit: 3
}]]></ee:set-payload>
        </ee:message>
    </ee:transform>
    
    <kpath:discover-services config-ref="KPATH_Config"/>
    
    <!-- Select best service based on cost and performance -->
    <ee:transform>
        <ee:message>
            <ee:set-payload><![CDATA[%dw 2.0
output application/json
var sortedServices = payload.discovered_services orderBy $.performance_score
---
sortedServices[0]]]></ee:set-payload>
        </ee:message>
    </ee:transform>
</flow>
```

## Troubleshooting

### Common Issues

1. **Authentication Failures**
   - Verify API key is correct and active
   - Check token expiration for JWT auth
   - Ensure proper header formatting

2. **No Services Found**
   - Refine search query
   - Check domain and capability filters
   - Verify services are registered in KPATH

3. **Timeout Errors**
   - Increase timeout settings
   - Check KPATH server health
   - Implement circuit breaker pattern

4. **SSL/TLS Issues**
   - Import KPATH certificates to truststore
   - Verify certificate validity
   - Check TLS version compatibility

## Support

For support with KPATH integration:
- Documentation: http://localhost:5173/user-guide
- API Reference: http://localhost:8000/docs
- Health Check: http://localhost:8000/health