# KPATH Enterprise - Apache Camel Integration Guide

## Overview

This guide demonstrates how to integrate KPATH Enterprise with Apache Camel to enable dynamic service discovery and intelligent routing. KPATH provides semantic search capabilities that help Camel routes discover and connect to the right services based on natural language queries.

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Apache Camel   │────▶│  KPATH Enterprise │────▶│  Discovered     │
│     Routes      │◀────│  Discovery API    │     │  Services       │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

## Prerequisites

- KPATH Enterprise instance running (default: http://localhost:8000)
- Apache Camel 3.x or later
- API Key or JWT token for KPATH authentication
- Camel HTTP component (`camel-http` dependency)

## Maven Dependencies

```xml
<dependencies>
    <!-- Camel Core -->
    <dependency>
        <groupId>org.apache.camel</groupId>
        <artifactId>camel-core</artifactId>
        <version>3.20.0</version>
    </dependency>
    
    <!-- HTTP Component for KPATH calls -->
    <dependency>
        <groupId>org.apache.camel</groupId>
        <artifactId>camel-http</artifactId>
        <version>3.20.0</version>
    </dependency>
    
    <!-- JSON Processing -->
    <dependency>
        <groupId>org.apache.camel</groupId>
        <artifactId>camel-jackson</artifactId>
        <version>3.20.0</version>
    </dependency>
    
    <!-- For caching -->
    <dependency>
        <groupId>org.apache.camel</groupId>
        <artifactId>camel-caffeine</artifactId>
        <version>3.20.0</version>
    </dependency>
    
    <!-- Circuit Breaker -->
    <dependency>
        <groupId>org.apache.camel</groupId>
        <artifactId>camel-resilience4j</artifactId>
        <version>3.20.0</version>
    </dependency>
</dependencies>
```

## Integration Patterns

### 1. Basic Service Discovery Route

```java
import org.apache.camel.builder.RouteBuilder;
import org.apache.camel.model.dataformat.JsonLibrary;

public class KPATHDiscoveryRoute extends RouteBuilder {
    
    @Override
    public void configure() throws Exception {
        
        // KPATH Service Discovery Route
        from("direct:discover-service")
            .routeId("kpath-discovery")
            .setHeader("Content-Type", constant("application/json"))
            .setHeader("X-API-Key", simple("{{kpath.api.key}}"))
            
            // Prepare discovery request
            .process(exchange -> {
                String query = exchange.getIn().getHeader("query", String.class);
                Integer limit = exchange.getIn().getHeader("limit", 5, Integer.class);
                
                Map<String, Object> request = new HashMap<>();
                request.put("query", query);
                request.put("limit", limit);
                
                // Optional filters
                List<String> domains = exchange.getIn().getHeader("domains", List.class);
                if (domains != null) request.put("domains", domains);
                
                List<String> capabilities = exchange.getIn().getHeader("capabilities", List.class);
                if (capabilities != null) request.put("capabilities", capabilities);
                
                exchange.getIn().setBody(request);
            })
            
            // Convert to JSON
            .marshal().json(JsonLibrary.Jackson)
            
            // Call KPATH API
            .to("http://{{kpath.host}}:{{kpath.port}}/api/v1/search/search?bridgeEndpoint=true")
            
            // Process response
            .unmarshal().json(JsonLibrary.Jackson, Map.class)
            
            // Extract best matching service
            .process(exchange -> {
                Map<String, Object> response = exchange.getIn().getBody(Map.class);
                List<Map<String, Object>> results = (List<Map<String, Object>>) response.get("results");
                
                if (results != null && !results.isEmpty()) {
                    exchange.getIn().setBody(results.get(0));
                    exchange.getIn().setHeader("serviceFound", true);
                } else {
                    exchange.getIn().setHeader("serviceFound", false);
                }
            });
    }
}
```

### 2. Dynamic Routing with KPATH

```java
public class DynamicServiceRouter extends RouteBuilder {
    
    @Override
    public void configure() throws Exception {
        
        // Main processing route
        from("direct:process-request")
            .routeId("dynamic-processor")
            
            // Extract intent from request
            .process(exchange -> {
                Map<String, Object> body = exchange.getIn().getBody(Map.class);
                String intent = (String) body.getOrDefault("intent", "process data");
                exchange.getIn().setHeader("query", intent);
            })
            
            // Discover appropriate service
            .to("direct:discover-service")
            
            // Route based on discovery
            .choice()
                .when(header("serviceFound").isEqualTo(true))
                    .to("direct:invoke-discovered-service")
                .otherwise()
                    .to("direct:fallback-service")
            .end();
        
        // Invoke discovered service
        from("direct:invoke-discovered-service")
            .routeId("service-invoker")
            .process(exchange -> {
                Map<String, Object> service = exchange.getIn().getBody(Map.class);
                String endpoint = (String) service.get("endpoint");
                String authType = (String) service.getOrDefault("auth_type", "bearer_token");
                
                // Set dynamic endpoint
                exchange.getIn().setHeader("CamelHttpUri", endpoint);
                
                // Set authentication
                if ("bearer_token".equals(authType)) {
                    exchange.getIn().setHeader("Authorization", 
                        "Bearer " + exchange.getContext().resolvePropertyPlaceholders("{{service.auth.token}}"));
                } else if ("api_key".equals(authType)) {
                    exchange.getIn().setHeader("X-API-Key", 
                        exchange.getContext().resolvePropertyPlaceholders("{{service.api.key}}"));
                }
            })
            .toD("${header.CamelHttpUri}?bridgeEndpoint=true");
    }
}
```

### 3. KPATH Component Implementation

Create a custom Camel component for KPATH:

```java
package org.apache.camel.component.kpath;

import org.apache.camel.*;
import org.apache.camel.support.DefaultComponent;
import org.apache.camel.support.DefaultEndpoint;
import org.apache.camel.support.DefaultProducer;

@Component("kpath")
public class KPATHComponent extends DefaultComponent {
    
    @Override
    protected Endpoint createEndpoint(String uri, String remaining, Map<String, Object> parameters) throws Exception {
        KPATHEndpoint endpoint = new KPATHEndpoint(uri, this);
        endpoint.setOperation(remaining);
        setProperties(endpoint, parameters);
        return endpoint;
    }
}

public class KPATHEndpoint extends DefaultEndpoint {
    
    @UriPath(description = "Operation to perform", enums = "discover,tools,analytics")
    private String operation;
    
    @UriParam(defaultValue = "localhost")
    private String host = "localhost";
    
    @UriParam(defaultValue = "8000")
    private int port = 8000;
    
    @UriParam(label = "security", secret = true)
    private String apiKey;
    
    public KPATHEndpoint(String uri, Component component) {
        super(uri, component);
    }
    
    @Override
    public Producer createProducer() throws Exception {
        return new KPATHProducer(this);
    }
    
    @Override
    public Consumer createConsumer(Processor processor) throws Exception {
        throw new UnsupportedOperationException("KPATH component doesn't support consumer");
    }
    
    // Getters and setters...
}

public class KPATHProducer extends DefaultProducer {
    
    private final KPATHEndpoint endpoint;
    private final HttpClient httpClient;
    
    public KPATHProducer(KPATHEndpoint endpoint) {
        super(endpoint);
        this.endpoint = endpoint;
        this.httpClient = HttpClient.newHttpClient();
    }
    
    @Override
    public void process(Exchange exchange) throws Exception {
        String operation = endpoint.getOperation();
        
        switch (operation) {
            case "discover":
                performDiscovery(exchange);
                break;
            case "tools":
                getServiceTools(exchange);
                break;
            case "analytics":
                getAnalytics(exchange);
                break;
            default:
                throw new IllegalArgumentException("Unknown operation: " + operation);
        }
    }
    
    private void performDiscovery(Exchange exchange) throws Exception {
        // Extract parameters
        String query = exchange.getIn().getHeader("query", String.class);
        Integer limit = exchange.getIn().getHeader("limit", 5, Integer.class);
        
        // Build request
        Map<String, Object> request = new HashMap<>();
        request.put("query", query);
        request.put("limit", limit);
        
        // Make HTTP call
        String url = String.format("http://%s:%d/api/v1/search/search", 
                                   endpoint.getHost(), endpoint.getPort());
        
        HttpRequest httpRequest = HttpRequest.newBuilder()
            .uri(URI.create(url))
            .header("Content-Type", "application/json")
            .header("X-API-Key", endpoint.getApiKey())
            .POST(HttpRequest.BodyPublishers.ofString(
                new ObjectMapper().writeValueAsString(request)))
            .build();
        
        HttpResponse<String> response = httpClient.send(httpRequest, 
                                                       HttpResponse.BodyHandlers.ofString());
        
        // Process response
        Map<String, Object> result = new ObjectMapper().readValue(
            response.body(), new TypeReference<Map<String, Object>>() {});
        
        exchange.getIn().setBody(result);
    }
}
```

### 4. Content-Based Router with KPATH

```java
public class ContentBasedRouter extends RouteBuilder {
    
    @Override
    public void configure() throws Exception {
        
        // Error handling
        onException(Exception.class)
            .handled(true)
            .to("log:kpath-error?level=ERROR")
            .to("direct:error-handler");
        
        // Main routing flow
        from("activemq:queue:incoming")
            .routeId("content-router")
            
            // Analyze message content
            .process(exchange -> {
                String body = exchange.getIn().getBody(String.class);
                String query = analyzeContent(body);
                exchange.getIn().setHeader("kpath.query", query);
            })
            
            // Discover appropriate service using KPATH
            .setHeader("query", header("kpath.query"))
            .to("kpath:discover?apiKey={{kpath.api.key}}")
            
            // Extract service information
            .process(exchange -> {
                Map<String, Object> response = exchange.getIn().getBody(Map.class);
                List<Map<String, Object>> results = (List<Map<String, Object>>) response.get("results");
                
                if (results != null && !results.isEmpty()) {
                    Map<String, Object> service = results.get(0);
                    exchange.getIn().setHeader("targetService", service.get("name"));
                    exchange.getIn().setHeader("targetEndpoint", service.get("endpoint"));
                }
            })
            
            // Route based on discovered service
            .choice()
                .when(header("targetService").isEqualTo("CustomerService"))
                    .to("direct:customer-processing")
                .when(header("targetService").isEqualTo("OrderService"))
                    .to("direct:order-processing")
                .when(header("targetService").isEqualTo("PaymentService"))
                    .to("direct:payment-processing")
                .otherwise()
                    .to("direct:generic-processing")
            .end();
    }
    
    private String analyzeContent(String content) {
        // Simple content analysis - in practice, use NLP
        if (content.contains("customer") || content.contains("user")) {
            return "customer management data";
        } else if (content.contains("order") || content.contains("purchase")) {
            return "order processing fulfillment";
        } else if (content.contains("payment") || content.contains("transaction")) {
            return "payment processing transaction";
        }
        return "general data processing";
    }
}
```

### 5. Caching and Circuit Breaker Pattern

```java
public class ResilientKPATHRoute extends RouteBuilder {
    
    @Override
    public void configure() throws Exception {
        
        // Configure circuit breaker
        CircuitBreakerConfig config = CircuitBreakerConfig.custom()
            .failureRateThreshold(50)
            .waitDurationInOpenState(Duration.ofSeconds(30))
            .slidingWindowSize(10)
            .build();
        
        // Cached discovery route with circuit breaker
        from("direct:cached-discovery")
            .routeId("cached-kpath-discovery")
            
            // Generate cache key
            .process(exchange -> {
                String query = exchange.getIn().getHeader("query", String.class);
                String cacheKey = "kpath:" + query.toLowerCase().replaceAll("\\s+", "_");
                exchange.getIn().setHeader("cacheKey", cacheKey);
            })
            
            // Check cache first
            .to("caffeine-cache://kpathCache?action=GET")
            .choice()
                .when(body().isNotNull())
                    .log("Cache hit for query: ${header.query}")
                    .to("direct:process-cached-result")
                .otherwise()
                    // Circuit breaker around KPATH call
                    .circuitBreaker()
                        .resilience4jConfiguration(config)
                        .to("direct:discover-service")
                        
                        // Store in cache on success
                        .to("caffeine-cache://kpathCache?action=PUT")
                    .onFallback()
                        .log("Circuit breaker open - using fallback")
                        .to("direct:fallback-discovery")
                    .end()
            .end();
        
        // Fallback discovery logic
        from("direct:fallback-discovery")
            .process(exchange -> {
                // Return default services when KPATH is unavailable
                Map<String, Object> fallback = new HashMap<>();
                fallback.put("name", "DefaultService");
                fallback.put("endpoint", "http://default-service/api");
                fallback.put("fallback", true);
                
                exchange.getIn().setBody(Collections.singletonMap("results", 
                                                                 Collections.singletonList(fallback)));
            });
    }
}
```

### 6. Integration with Camel K

For Kubernetes deployments using Camel K:

```groovy
// kpath-integration.groovy
import org.apache.camel.builder.RouteBuilder

class KPATHIntegration extends RouteBuilder {
    
    void configure() {
        
        // Kubernetes service discovery with KPATH
        from('knative:channel/requests')
            .log('Received request: ${body}')
            
            // Extract query from CloudEvent
            .process { exchange ->
                def event = exchange.in.body
                exchange.in.headers['query'] = event.data?.intent ?: 'process request'
            }
            
            // Discover service via KPATH
            .setHeader('Content-Type', constant('application/json'))
            .setHeader('X-API-Key', constant('{{kpath.api.key}}'))
            .setBody {
                [query: it.in.headers.query, limit: 3]
            }
            .marshal().json()
            .to('http://kpath-service:8000/api/v1/search/search')
            .unmarshal().json()
            
            // Route to discovered service
            .process { exchange ->
                def results = exchange.in.body.results
                if (results && !results.empty) {
                    def service = results[0]
                    exchange.in.headers['targetService'] = service.name
                    exchange.in.headers['targetEndpoint'] = service.endpoint
                }
            }
            
            // Send to discovered service
            .toD('${header.targetEndpoint}')
            
            // Send response
            .to('knative:channel/responses')
    }
}
```

### 7. Stream Processing with KPATH

```java
public class StreamProcessingRoute extends RouteBuilder {
    
    @Override
    public void configure() throws Exception {
        
        // Process streaming data with dynamic service discovery
        from("kafka:input-stream?brokers={{kafka.brokers}}")
            .routeId("stream-processor")
            
            // Batch messages for efficient discovery
            .aggregate(constant(true), new GroupedExchangeAggregationStrategy())
                .completionSize(10)
                .completionTimeout(5000)
            
            // Analyze batch to determine required service
            .process(exchange -> {
                List<Exchange> exchanges = exchange.getIn().getBody(List.class);
                String commonIntent = analyzeExchanges(exchanges);
                exchange.getIn().setHeader("batchQuery", commonIntent);
                exchange.getIn().setHeader("originalExchanges", exchanges);
            })
            
            // Discover service for batch
            .setHeader("query", header("batchQuery"))
            .to("direct:cached-discovery")
            
            // Process each message with discovered service
            .split(header("originalExchanges"))
                .streaming()
                .process(exchange -> {
                    // Apply discovered service
                    Map<String, Object> service = exchange.getProperty("discoveredService", Map.class);
                    if (service != null) {
                        exchange.getIn().setHeader("targetEndpoint", service.get("endpoint"));
                    }
                })
                .toD("${header.targetEndpoint}")
            .end()
            
            // Send to output stream
            .to("kafka:output-stream?brokers={{kafka.brokers}}");
    }
    
    private String analyzeExchanges(List<Exchange> exchanges) {
        // Analyze batch to find common processing need
        Map<String, Integer> intents = new HashMap<>();
        
        for (Exchange ex : exchanges) {
            String content = ex.getIn().getBody(String.class);
            String intent = detectIntent(content);
            intents.merge(intent, 1, Integer::sum);
        }
        
        // Return most common intent
        return intents.entrySet().stream()
            .max(Map.Entry.comparingByValue())
            .map(Map.Entry::getKey)
            .orElse("general processing");
    }
}
```

## Configuration

### Application Properties

```properties
# application.properties

# KPATH Configuration
kpath.host=localhost
kpath.port=8000
kpath.api.key=kpe_your_api_key_here
kpath.timeout=30000
kpath.cache.ttl=3600000

# Circuit Breaker
resilience4j.circuitbreaker.instances.kpath.failure-rate-threshold=50
resilience4j.circuitbreaker.instances.kpath.wait-duration-in-open-state=30s
resilience4j.circuitbreaker.instances.kpath.sliding-window-size=10

# Retry Configuration
resilience4j.retry.instances.kpath.max-attempts=3
resilience4j.retry.instances.kpath.wait-duration=1s

# Service Defaults
service.auth.token=${SERVICE_AUTH_TOKEN}
service.api.key=${SERVICE_API_KEY}

# Kafka Configuration
kafka.brokers=localhost:9092
```

### Spring Boot Configuration

```java
@Configuration
public class CamelConfiguration {
    
    @Bean
    public RouteBuilder kpathRoutes() {
        return new RouteBuilder() {
            @Override
            public void configure() throws Exception {
                // Global error handler
                errorHandler(deadLetterChannel("direct:error-queue")
                    .maximumRedeliveries(3)
                    .redeliveryDelay(1000)
                    .useExponentialBackOff());
                
                // Configure KPATH routes
                from("direct:kpath-discovery")
                    .routeId("kpath-main")
                    .to("kpath:discover?apiKey={{kpath.api.key}}");
            }
        };
    }
    
    @Bean
    public CacheManager cacheManager() {
        CaffeineCacheManager cacheManager = new CaffeineCacheManager("kpathCache");
        cacheManager.setCaffeine(Caffeine.newBuilder()
            .expireAfterWrite(1, TimeUnit.HOURS)
            .maximumSize(1000));
        return cacheManager;
    }
}
```
