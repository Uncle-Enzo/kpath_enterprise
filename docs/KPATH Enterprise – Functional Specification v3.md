# **KPATH Enterprise – Functional Specification v3**

## **Introduction**

KPATH Enterprise is a semantic search service for internal AI capabilities, designed to help AI personal assistants (PAs) and agents discover **which internal agents, tools, and services** can fulfill a given natural language request. It acts as a semantic discovery layer that integrates in front of an ESB (e.g., Mulesoft, Apache Camel), enabling AI-driven discovery of capabilities across enterprise systems including APIs and Model Context Protocol (MCP) services. KPATH **performs discovery only** – it does **not orchestrate or execute** any actions itself. This service is intended for enterprise environments, where it can be deployed on-premises, in the cloud, or in hybrid setups to meet organizational needs.

## **Key Features and Requirements**

* **Semantic Capability Matching Only:** KPATH focuses on semantic similarity search over a registry of available capabilities using FAISS (Facebook AI Similarity Search) for high-performance vector operations. It converts the user's natural language prompt into a vector embedding and finds which services have descriptions with similar embeddings. It does **not** perform any workflow routing or tool execution – it simply returns relevant matches.

* **Service and Capability Registry:** The system maintains a registry of **services** (which can be agents, tools, or APIs) and their **capabilities**. Each service can expose multiple capabilities with rich metadata stored in PostgreSQL, while embeddings are indexed in FAISS for performance. For every service, the registry stores:
  * **Service Name** – e.g. `"CalendarAgent"` or `"EmailService"`
  * **Service Description** – overview of what the service provides
  * **Capabilities** – specific actions/tools the service exposes
  * **Runtime Metadata:** API endpoints, input schemas, auth requirements
  * **Access Policies:** RBAC/ABAC rules for discovery filtering

* **Feedback-Driven Ranking:** KPATH implements a feedback loop that tracks which services users select after searches, using this data to improve future rankings through usage-based boosting and optional learning-to-rank models.

* **Admin Interface:** A Svelte-based web interface provides service management, policy editing, observability dashboards, and index management capabilities with role-based access control.

* **Enterprise Deployment (On-Prem, Cloud, Hybrid):** KPATH Enterprise is designed for flexible deployment with high availability and horizontal scaling. The stateless Python backend can be deployed as multiple instances behind a load balancer, with PostgreSQL in HA mode and FAISS replicated or sharded across nodes.

* **Security and Access Control Integration:** The service integrates with enterprise IAM systems for both API authentication and result filtering based on RBAC and ABAC policies. Each service can have fine-grained access controls determining who can discover it.

* **Standards-Based API:** KPATH exposes its functionality via a RESTful API, documented in OpenAPI specification for easy integration. The API accepts natural language queries and returns structured results in JSON format.

## **Architecture**

### **Core Components**

* **KPATH Backend (Python):** Stateless API server that processes natural language queries and returns best-matched services/tools. Handles embedding generation, search coordination, and policy enforcement.

* **FAISS Vector Index:** High-performance similarity search index for tool embeddings. Can be deployed in-memory for speed or distributed for scale.

* **PostgreSQL Database:** Stores service metadata, user information, policies, audit logs, and feedback data. Does not store embeddings directly.
* **Admin Frontend (Svelte):** Web interface for managing services, policies, and monitoring system health. Supports basic auth initially with SSO integration planned.

* **Caching Layer:** Multi-level caching to accelerate embedding reuse and result delivery:
  * Prompt embedding cache
  * Search result cache (semantic cache)
  * Configurable TTL for freshness

* **Policy Engine:** Enforces RBAC and ABAC rules for access control, supporting complex conditions including time-based, location-based, and attribute-based policies.

### **High Availability & Scalability**

#### **Multi-Instance Deployment Architecture**

* **Load Balancing Configuration:**
  ```yaml
  load_balancer:
    algorithm: round_robin  # or least_connections
    health_check:
      endpoint: /health
      interval: 5s
      timeout: 2s
      failure_threshold: 3
    sticky_sessions: false  # Stateless design
  ```

* **Instance Distribution:**
  - Minimum 3 instances for production
  - Cross-availability-zone deployment
  - Auto-scaling based on CPU/memory/request latency
  - Rolling updates with zero downtime

#### **FAISS Index Resilience**

* **Index Replication Strategy:**
  ```python
  # Primary-replica configuration
  faiss_config = {
      "primary": {
          "node": "faiss-primary",
          "write": True,
          "read": True
      },
      "replicas": [
          {"node": "faiss-replica-1", "write": False, "read": True},
          {"node": "faiss-replica-2", "write": False, "read": True}
      ],
      "sync_interval": 60  # seconds
  }
  ```

* **Index Corruption Recovery:**
  1. **Detection:** Checksum validation on load
  2. **Automatic Failover:** Switch to replica within 5 seconds
  3. **Warm Index Restore:**
     ```bash
     # Restore from latest snapshot
     faiss-restore --snapshot s3://backups/faiss/latest \
                  --verify-checksum \
                  --warm-load \
                  --max-memory 16GB
     ```
  4. **Index Rebuild:** As last resort, regenerate from PostgreSQL

* **FAISS Failure Handling:**
  - Circuit breaker prevents cascading failures
  - Fallback to keyword search during index unavailability
  - Cached results serve during recovery
  - Alert on corruption detection

#### **Database High Availability**

* **PostgreSQL Configuration:**
  - Primary-standby replication with streaming WAL
  - Automated failover using Patroni/PgBouncer
  - Connection pooling for efficient resource use
  - Read replicas for search queries

#### **Service Mesh Integration**

* **Kubernetes Deployment:**
  ```yaml
  apiVersion: apps/v1
  kind: Deployment
  metadata:
    name: kpath-backend
  spec:
    replicas: 3
    strategy:
      type: RollingUpdate
      rollingUpdate:
        maxSurge: 1
        maxUnavailable: 0
  ```

* **Health Probes:**
  - Liveness: API responds to /health
  - Readiness: FAISS index loaded and PostgreSQL connected
  - Startup: Allows time for index loading

## **Integration Specifications**

### **Model Context Protocol (MCP) Integration**

KPATH provides native support for discovering and interfacing with MCP-compatible services:

* **MCP Service Discovery:**
  - Auto-discovery through MCP registry endpoints
  - Manual registration via Admin API
  - Periodic polling for new MCP services
  - Support for MCP service metadata transformation

* **MCP Metadata Mapping:**
  ```json
  {
    "mcp_service": {
      "name": "weather-service",
      "tools": ["get_weather", "get_forecast"],
      "schema_version": "1.0"
    },
    "kpath_mapping": {
      "service_name": "WeatherService",
      "capabilities": [
        {
          "name": "GetCurrentWeather",
          "mcp_tool": "get_weather",
          "description": "Get current weather for a location"
        }
      ]
    }
  }
  ```

* **Protocol Translation:**
  - MCP tool schemas → KPATH input/output schemas
  - MCP authentication → KPATH auth metadata
  - MCP versioning → KPATH service versioning

### **Enterprise Service Bus (ESB) Integration**

KPATH integrates with ESB platforms through standardized patterns:

* **Mulesoft Integration:**
  - Anypoint Platform connector
  - API autodiscovery from Exchange
  - Flow metadata extraction
  - DataWeave transformation support

* **Apache Camel Integration:**
  - Route discovery via JMX
  - Endpoint metadata extraction
  - Component capability mapping
  - Camel registry synchronization

* **Integration Patterns:**
  - Service Registry Synchronization
  - Event-Driven Updates (JMS/AMQP/Kafka)
  - Request/Reply correlation
  - Circuit breaker integration

### **Service Discovery Mechanisms**

* **Active Discovery:**
  - OpenAPI/Swagger endpoint scanning
  - Service mesh integration (Istio/Consul)
  - Kubernetes service discovery
  - WSDL parsing for SOAP services

* **Passive Registration:**
  - Webhook-based registration
  - CI/CD pipeline integration
  - GitOps-based updates
  - Manual registration via Admin UI/API

* **Discovery Configuration:**
  ```yaml
  discovery:
    openapi:
      enabled: true
      scan_interval: 300s
      endpoints:
        - https://api.internal/swagger
    kubernetes:
      enabled: true
      namespaces: ["production", "staging"]
      label_selector: "kpath.discovery=enabled"
    mcp:
      enabled: true
      registries:
        - https://mcp.internal/registry
  ```

## **Data Schema (PostgreSQL)**

KPATH stores service and operational metadata in PostgreSQL, with FAISS handling the vector search operations separately.

```sql
-- Core service registry
CREATE TABLE services (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT NOT NULL,
    endpoint TEXT,
    version TEXT,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Service capabilities
CREATE TABLE service_capability (
    id SERIAL PRIMARY KEY,
    service_id INTEGER REFERENCES services(id) ON DELETE CASCADE,
    capability_desc TEXT NOT NULL,
    capability_name TEXT,
    input_schema JSONB,
    output_schema JSONB
);
```
-- Interaction patterns
CREATE TABLE interaction_capability (
    id SERIAL PRIMARY KEY,
    service_id INTEGER REFERENCES services(id) ON DELETE CASCADE,
    interaction_desc TEXT NOT NULL,
    interaction_type TEXT -- 'sync', 'async', 'stream', etc.
);

-- Industry/domain classification
CREATE TABLE service_industry (
    id SERIAL PRIMARY KEY,
    service_id INTEGER REFERENCES services(id) ON DELETE CASCADE,
    domain TEXT NOT NULL -- 'HR', 'Finance', 'IT', etc.
);

-- User management
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    role TEXT,
    org_id INTEGER,
    attributes JSONB -- For ABAC
);

-- Access policies
CREATE TABLE access_policy (
    id SERIAL PRIMARY KEY,
    service_id INTEGER REFERENCES services(id),
    conditions JSONB NOT NULL,
    type TEXT CHECK (type IN ('RBAC', 'ABAC')),
    priority INTEGER DEFAULT 0
);

-- FAISS index metadata
CREATE TABLE faiss_index_metadata (
    id SERIAL PRIMARY KEY,
    index_name TEXT,
    last_updated TIMESTAMP,
    embedding_model TEXT,
    total_vectors INTEGER,
    index_params JSONB
);

-- Audit logging
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    action TEXT NOT NULL,
    payload JSONB,
    ip_address INET
);

-- Feedback for ranking improvement
CREATE TABLE feedback_log (
    id SERIAL PRIMARY KEY,
    query TEXT NOT NULL,
    query_embedding_hash TEXT, -- For caching
    selected_service_id INTEGER REFERENCES services(id),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER REFERENCES users(id),
    rank_position INTEGER,
    click_through BOOLEAN DEFAULT TRUE
);

-- Cache metadata
CREATE TABLE cache_entries (
    key TEXT PRIMARY KEY,
    value JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    hit_count INTEGER DEFAULT 0
);

-- Create indexes for performance
CREATE INDEX idx_services_status ON services(status);
CREATE INDEX idx_feedback_timestamp ON feedback_log(timestamp);
CREATE INDEX idx_audit_timestamp ON audit_logs(timestamp);
CREATE INDEX idx_cache_expires ON cache_entries(expires_at);

-- Additional tables for enhanced functionality

-- Service versioning
CREATE TABLE service_versions (
    id SERIAL PRIMARY KEY,
    service_id INTEGER REFERENCES services(id),
    version TEXT NOT NULL,
    version_tag TEXT, -- 'stable', 'beta', 'alpha', 'deprecated'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deprecated BOOLEAN DEFAULT FALSE,
    deprecated_at TIMESTAMP,
    sunset_at TIMESTAMP,
    compatible_with TEXT[], -- Array of compatible version patterns
    breaking_changes TEXT[],
    migration_notes TEXT,
    release_notes TEXT,
    UNIQUE(service_id, version)
);

-- Service health monitoring
CREATE TABLE service_health (
    id SERIAL PRIMARY KEY,
    service_id INTEGER REFERENCES services(id),
    health_status TEXT CHECK (health_status IN ('healthy', 'degraded', 'unhealthy', 'unknown')),
    last_check TIMESTAMP,
    response_time_ms INTEGER,
    error_count INTEGER DEFAULT 0,
    consecutive_failures INTEGER DEFAULT 0
);

-- API key management
CREATE TABLE api_keys (
    id SERIAL PRIMARY KEY,
    key_hash TEXT UNIQUE NOT NULL,
    user_id INTEGER REFERENCES users(id),
    name TEXT,
    scopes TEXT[],
    expires_at TIMESTAMP,
    last_used TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    active BOOLEAN DEFAULT TRUE
);

-- Query templates
CREATE TABLE query_templates (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    template TEXT NOT NULL,
    parameters JSONB,
    description TEXT,
    created_by INTEGER REFERENCES users(id),
    is_public BOOLEAN DEFAULT FALSE
);

-- Integration configurations
CREATE TABLE integration_configs (
    id SERIAL PRIMARY KEY,
    type TEXT NOT NULL, -- 'mcp', 'esb', 'openapi', etc.
    name TEXT NOT NULL,
    config JSONB NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    last_sync TIMESTAMP,
    UNIQUE(type, name)
);
```

## **Search Logic and Implementation**

### **Embedding Flow**

1. **Query Processing:**
   - Receive natural language prompt via API
   - Validate user authentication and extract user context
   - Check prompt embedding cache

2. **Embedding Generation:**
   - If not cached, generate embedding using transformer model (e.g., BGE, Sentence-BERT)
   - Cache the prompt embedding with configurable TTL
   - Typical embedding dimension: 768 or 1536 depending on model
3. **Similarity Search:**
   - Query FAISS index for k-nearest neighbors
   - FAISS returns service IDs with similarity scores
   - Apply post-filtering based on access policies

4. **Result Enhancement:**
   - Fetch full service metadata from PostgreSQL
   - Apply feedback-based score boosting
   - Sort by final composite score

5. **Response Assembly:**
   - Format results with metadata, scores, and runtime info
   - Log interaction for feedback loop
   - Return JSON response

### **Embedding Update Process**

Embeddings are regenerated when:
- New service is added
- Service description/capabilities are updated
- Service is deleted (removal from index)
- Embedding model is upgraded

Update process:
1. Generate new embeddings for affected services
2. Update FAISS index (add/update/remove vectors)
3. Update faiss_index_metadata table
4. Invalidate relevant caches

## **REST API Design (OpenAPI Style)**

### **Base Configuration**
- **Base URL:** `https://kpath.enterprise.com/api/v1`
- **Authentication:** Bearer token (JWT) or API key
- **Content-Type:** `application/json`

### **Endpoints**

#### **`POST /search` – Semantic Capability Search**

**Description:** Accepts a natural language prompt and returns matching services ranked by relevance.
**Request:**
```json
{
  "query": "Schedule a meeting with the VP next week",
  "user_context": {
    "user_id": "alice@example.com",
    "roles": ["Engineering", "ExecutiveAssistant"],
    "attributes": {
      "department": "Engineering",
      "clearance_level": "standard"
    }
  },
  "options": {
    "limit": 10,
    "min_score": 0.7,
    "include_feedback_boost": true
  }
}
```

**Response:**
```json
{
  "query": "Schedule a meeting with the VP next week",
  "results": [
    {
      "service": {
        "id": "svc_001",
        "name": "CalendarAgent",
        "description": "Corporate calendar management service"
      },
      "capability": {
        "name": "CreateEvent",
        "description": "Schedule a new meeting on the corporate calendar with specified participants, date, and time."
      },
      "score": 0.93,
      "feedback_boost": 0.05,
      "final_score": 0.98,
      "runtime": {
        "endpoint": "https://api.internal.corp/CalendarAgent/v1/create_event",
        "auth_type": "OAuth2",
        "input_schema": {
          "type": "object",
          "required": ["date", "time", "attendees"],
          "properties": {
            "date": { "type": "string", "format": "date" },
            "time": { "type": "string", "format": "time" },
            "attendees": { "type": "array", "items": { "type": "string" } },            "subject": { "type": "string" }
          }
        }
      }
    }
  ],
  "metadata": {
    "search_id": "search_12345",
    "processing_time_ms": 47,
    "cache_hit": false,
    "model_version": "bge-base-en-1.5"
  }
}
```

#### **`POST /log_feedback` – Log User Tool Selection**

**Description:** Records which service a user selected after a search to improve future rankings. This endpoint captures detailed feedback data for the learning system.

**Request:**
```json
{
  "search_id": "search_12345",
  "selected_service_id": "svc_001", 
  "result_position": 1,
  "selection_time_ms": 2340,
  "user_action": "clicked",
  "session_id": "session_abc123",
  "user_satisfaction": true,
  "metadata": {
    "client_type": "web",
    "experiment_id": "ranking_v2"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "feedback_id": "fb_98765",
  "message": "Feedback recorded successfully"
}
```

#### **`GET /services/{service_id}` – Get Service Details**

**Description:** Retrieves detailed information about a specific service.

#### **`GET /health` – Health Check**

**Description:** Returns system health status including component availability.

**Response:**
```json
{
  "status": "healthy",
  "components": {
    "api": "healthy",
    "database": "healthy",
    "faiss": "healthy",
    "cache": "healthy"
  },
  "version": "1.2.3"
}
```
### **Admin API Endpoints**

#### **Service Management**

##### **`GET /admin/services` – List Services**
**Description:** Retrieve all services with pagination and filtering.

**Query Parameters:**
- `page` (integer): Page number
- `limit` (integer): Items per page
- `status` (string): Filter by status (active/inactive)
- `domain` (string): Filter by domain

##### **`POST /admin/services` – Create Service**
**Description:** Register a new service in KPATH.

**Request:**
```json
{
  "name": "PayrollService",
  "description": "Handles employee payroll processing",
  "endpoint": "https://api.internal/payroll",
  "version": "2.0",
  "capabilities": [
    {
      "name": "CalculateSalary",
      "description": "Calculate employee monthly salary",
      "input_schema": {...},
      "output_schema": {...}
    }
  ],
  "domains": ["HR", "Finance"],
  "access_policy": {
    "type": "RBAC",
    "allowed_roles": ["HR_Manager", "Finance_Admin"]
  }
}
```

##### **`PUT /admin/services/{service_id}` – Update Service**
**Description:** Update an existing service configuration.

##### **`DELETE /admin/services/{service_id}` – Delete Service**
**Description:** Remove a service from the registry.

##### **`POST /admin/services/bulk` – Bulk Import Services**
**Description:** Import multiple services from JSON or CSV.

**Request:**
```json
{
  "format": "json",
  "data": [...],
  "update_existing": true,
  "validation_mode": "strict"
}
```

#### **Policy Management**

##### **`GET /admin/policies` – List Policies**
##### **`POST /admin/policies` – Create Policy**
##### **`PUT /admin/policies/{policy_id}` – Update Policy**
##### **`DELETE /admin/policies/{policy_id}` – Delete Policy**

#### **Index Management**

##### **`POST /admin/index/rebuild` – Rebuild FAISS Index**
**Description:** Trigger a complete rebuild of the vector index.

##### **`POST /admin/index/optimize` – Optimize Index**
**Description:** Optimize FAISS index for better performance.

##### **`GET /admin/index/stats` – Index Statistics**
**Response:**
```json
{
  "total_vectors": 5432,
  "index_size_mb": 234,
  "last_rebuild": "2024-12-01T10:00:00Z",
  "embedding_model": "bge-base-en-1.5",
  "index_type": "IVF1024,Flat"
}
```

#### **User Management**

##### **`GET /admin/users` – List Users**
##### **`POST /admin/users` – Create User**
##### **`PUT /admin/users/{user_id}` – Update User**
##### **`DELETE /admin/users/{user_id}` – Delete User**

#### **API Key Management**

##### **`POST /admin/api-keys` – Generate API Key**
**Response:**
```json
{
  "key": "kpath_live_abc123...",
  "key_id": "key_001",
  "expires_at": "2025-12-01T00:00:00Z"
}
```

##### **`GET /admin/api-keys` – List API Keys**
##### **`DELETE /admin/api-keys/{key_id}` – Revoke API Key**

### **Advanced Query Endpoints**

#### **`POST /search/advanced` – Advanced Search**
**Description:** Search with filters and advanced options.

**Request:**
```json
{
  "query": "process invoice",
  "filters": {
    "domains": ["Finance", "Accounting"],
    "exclude_services": ["LegacyInvoiceSystem"],
    "min_score": 0.8,
    "max_results": 5
  },
  "options": {
    "explain": true,
    "include_similar": true
  }
}
```

#### **`POST /search/batch` – Batch Search**
**Description:** Process multiple queries in a single request.

**Request:**
```json
{
  "queries": [
    {"id": "q1", "query": "send email"},
    {"id": "q2", "query": "schedule meeting"},
    {"id": "q3", "query": "generate report"}
  ],
  "common_filters": {
    "domains": ["Communication", "Productivity"]
  }
}
```

### **Webhook Endpoints**

#### **`POST /webhooks` – Register Webhook**
**Description:** Register a webhook for service events.

**Request:**
```json
{
  "url": "https://my-system.com/kpath-events",
  "events": ["service.created", "service.updated", "service.deleted"],
  "secret": "webhook_secret_key"
}
```

#### **`GET /webhooks` – List Webhooks**
#### **`DELETE /webhooks/{webhook_id}` – Delete Webhook**

### **Error Responses**

- **400 Bad Request:** Invalid query format or parameters
- **401 Unauthorized:** Missing or invalid authentication
- **403 Forbidden:** User lacks permission for requested operation
- **429 Too Many Requests:** Rate limit exceeded
- **500 Internal Server Error:** System error (generic message, details logged)

## **Admin Interface (Svelte)**

### **Functional Areas**

#### **Service Manager**
- Add/edit/delete services with form validation
- Bulk import via JSON/CSV with schema validation
- Manual test search to verify discoverability
- Embedding generation status indicator
- Service health monitoring

#### **Policy Editor**
- Visual policy builder for RBAC/ABAC rules
- Policy testing interface
- Bulk policy assignment
- Policy conflict detection

#### **Observability Dashboard**
- Real-time metrics visualization
- Search latency histogram (p50, p95, p99)
- FAISS index statistics
- Cache performance metrics
- Feedback analytics and trending queries

#### **Index Management**
- Manual and scheduled reindexing
- Index optimization controls
- Embedding model selection
- Backup/restore operations

### **Authentication and Authorization**
- **Phase 1:** Basic authentication with secure password storage
- **Phase 2:** SSO integration (OAuth 2.0/SAML)
- **Roles:**
  - **Admin:** Full system access
  - **Editor:** Manage services and policies
  - **Viewer:** Read-only access to dashboards
## **Feedback, Caching, and Learning**

### **Feedback Loop Implementation**

#### **User Selection Tracking**

KPATH tracks every user interaction to continuously improve search quality:

1. **Data Collection Points:**
   - **Search Initiated:** Query text, user context, timestamp
   - **Results Returned:** Service IDs, scores, positions
   - **User Selection:** Which service clicked, position in results
   - **Post-Selection:** Success indicators, time spent, follow-up actions

2. **Feedback Storage Schema:**
   ```sql
   -- Enhanced feedback tracking
   CREATE TABLE user_selections (
       id SERIAL PRIMARY KEY,
       search_id UUID NOT NULL,
       query TEXT NOT NULL,
       query_embedding_hash TEXT,
       selected_service_id INTEGER REFERENCES services(id),
       result_position INTEGER NOT NULL,
       selection_time_ms INTEGER, -- Time to select after results shown
       session_id UUID,
       user_satisfaction BOOLEAN, -- Optional explicit feedback
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );
   
   CREATE INDEX idx_selections_service ON user_selections(selected_service_id);
   CREATE INDEX idx_selections_query_hash ON user_selections(query_embedding_hash);
   ```

3. **Click-Through Rate (CTR) Calculation:**
   ```python
   def calculate_ctr(service_id, time_window='7d'):
       impressions = count_service_in_results(service_id, time_window)
       clicks = count_service_selections(service_id, time_window)
       ctr = clicks / impressions if impressions > 0 else 0
       return ctr
   ```

#### **Score Boosting Algorithm**

The feedback system adjusts service rankings based on historical performance:

1. **Base Score Calculation:**
   ```python
   final_score = semantic_score * (1 + feedback_boost)
   
   where:
   feedback_boost = log(1 + ctr * recency_weight) * boost_factor
   ```

2. **Recency Weighting:**
   - Last 24 hours: Weight = 1.0
   - Last 7 days: Weight = 0.7
   - Last 30 days: Weight = 0.3
   - Older: Weight = 0.1

3. **Position Bias Correction:**
   ```python
   # Correct for position bias (higher positions get more clicks)
   adjusted_ctr = raw_ctr / position_bias_factor[position]
   ```

4. **Continuous Learning Pipeline:**
   ```yaml
   feedback_pipeline:
     collection:
       buffer_size: 1000
       flush_interval: 60s
     
     aggregation:
       schedule: "*/15 * * * *"  # Every 15 minutes
       metrics:
         - ctr_by_service
         - avg_position_by_service
         - query_success_rate
     
     model_update:
       schedule: "0 * * * *"  # Hourly
       min_feedback_count: 100
       validation_split: 0.2
   ```

#### **How Feedback Improves Search Quality**

1. **Real-Time Adjustments:**
   - Popular services gradually rank higher
   - Underperforming services drop in rankings
   - New services get exploration bonus

2. **Query Pattern Learning:**
   - Identify common query→service mappings
   - Build query expansion rules
   - Detect synonym relationships

3. **A/B Testing Integration:**
   ```python
   # Test different ranking algorithms
   if user_in_experiment('ranking_v2'):
       results = apply_experimental_ranking(results)
   track_experiment_metrics(user_id, 'ranking_v2', selected_service)
   ```

4. **Feedback Analytics Dashboard:**
   - CTR trends by service
   - Query success rates
   - User satisfaction scores
   - Ranking algorithm performance

### **Caching Strategy**

#### **Multi-Layer Cache Architecture**

KPATH employs a sophisticated multi-layer caching system to minimize latency and reduce computational overhead:

```yaml
cache_layers:
  l1_memory:
    type: "in-process"
    size: "1GB"
    eviction: "LRU"
    
  l2_redis:
    type: "redis_cluster"
    nodes: ["redis-1:6379", "redis-2:6379", "redis-3:6379"]
    replication: true
    persistence: "AOF"
```

#### **1. Embedding Cache**

Avoid expensive embedding recomputation with intelligent caching:

**Redis Implementation:**
```python
class EmbeddingCache:
    def __init__(self, redis_client, ttl=86400):  # 24 hours default
        self.redis = redis_client
        self.ttl = ttl
    
    def get_or_compute(self, text):
        # Normalize and hash the query
        normalized = normalize_query(text)
        cache_key = f"emb:v1:{hashlib.sha256(normalized.encode()).hexdigest()}"
        
        # Try cache first
        cached = self.redis.get(cache_key)
        if cached:
            return np.frombuffer(cached, dtype=np.float32)
        
        # Compute if miss
        embedding = compute_embedding(normalized)
        
        # Store with TTL
        self.redis.setex(
            cache_key,
            self.ttl,
            embedding.tobytes()
        )
        return embedding
```

**Cache Configuration:**
- **TTL**: 24 hours (configurable per deployment)
- **Max Size**: 10GB allocated for embeddings
- **Eviction**: LRU when memory limit reached
- **Warm-up**: Pre-populate common queries on startup

#### **2. Search Result Cache**

Cache complete search results for common queries:

```python
class ResultCache:
    def __init__(self, redis_client, ttl=3600):  # 1 hour default
        self.redis = redis_client
        self.ttl = ttl
    
    def cache_key(self, query, user_context):
        # Include user context for personalized results
        context_hash = hashlib.md5(
            json.dumps(user_context, sort_keys=True).encode()
        ).hexdigest()
        query_hash = hashlib.sha256(query.encode()).hexdigest()
        return f"results:v1:{query_hash}:{context_hash}"
    
    def get(self, query, user_context):
        key = self.cache_key(query, user_context)
        cached = self.redis.get(key)
        if cached:
            return json.loads(cached)
        return None
    
    def set(self, query, user_context, results):
        key = self.cache_key(query, user_context)
        self.redis.setex(
            key,
            self.ttl,
            json.dumps(results)
        )
```

**Invalidation Strategy:**
- Service update → Invalidate all result caches
- Selective invalidation based on service domain
- Background refresh for popular queries

#### **3. Metadata Cache**

In-memory caching of frequently accessed service metadata:

```python
class MetadataCache:
    def __init__(self, capacity=10000):
        self.cache = LRUCache(capacity)
        self.stats = CacheStats()
    
    def get_service(self, service_id):
        if service_id in self.cache:
            self.stats.hit()
            return self.cache[service_id]
        
        self.stats.miss()
        service = db.get_service(service_id)
        self.cache[service_id] = service
        return service
```

#### **4. FAISS Index Cache**

Keep frequently accessed index portions in memory:

```yaml
faiss_cache:
  preload_percentage: 20  # Keep 20% of index in RAM
  mmap_enabled: true      # Memory-mapped files for large indexes
  hugepages: true         # Use hugepages for performance
```

#### **Cache Warming Strategies**

1. **Startup Warming:**
   ```python
   async def warm_caches():
       # Load top queries from last 7 days
       popular_queries = await get_popular_queries(days=7, limit=1000)
       
       # Pre-compute embeddings
       for query in popular_queries:
           embedding_cache.get_or_compute(query.text)
       
       # Pre-load popular service metadata
       popular_services = await get_popular_services(limit=500)
       for service in popular_services:
           metadata_cache.get_service(service.id)
   ```

2. **Continuous Warming:**
   - Background job refreshes expiring cache entries
   - Predictive caching based on usage patterns
   - Off-peak pre-computation of embeddings

#### **Cache Monitoring**

Real-time cache performance metrics:

```json
{
  "embedding_cache": {
    "hit_rate": 0.85,
    "miss_rate": 0.15,
    "avg_compute_time_ms": 12,
    "memory_used_mb": 2048
  },
  "result_cache": {
    "hit_rate": 0.45,
    "miss_rate": 0.55,
    "avg_ttl_remaining": 1823,
    "entries": 15420
  }
}
```

## **Deployment Options**

### **On-Premises Deployment**

- **Infrastructure:**
  - KPATH API: Kubernetes cluster or VM fleet
  - PostgreSQL: Enterprise DB cluster with replication
  - FAISS: High-memory nodes with NVMe storage
  - Admin UI: Internal web server
- **Integration:**
  - LDAP/Active Directory for authentication
  - Internal PKI for TLS certificates
  - Existing monitoring stack (Prometheus/Grafana)

### **Cloud Deployment**

- **Infrastructure:**
  - KPATH API: Kubernetes (EKS/GKE/AKS) or container instances
  - PostgreSQL: Managed service (RDS/Cloud SQL)
  - FAISS: Container with persistent volumes or managed vector DB
  - Admin UI: Behind cloud load balancer with WAF

- **Security:**
  - VPC isolation with private subnets
  - Managed identities for service authentication
  - Cloud KMS for encryption keys

### **Hybrid Deployment**

- **Architecture:**
  - KPATH API in DMZ or cloud
  - PostgreSQL on-premises with secure replication
  - FAISS distributed between environments
  - Service mesh for secure communication

- **Use Cases:**
  - Comply with data residency requirements
  - Leverage cloud elasticity with on-prem data
  - Gradual cloud migration path

## **Operational Features**

### **Service Health Monitoring**

KPATH continuously monitors the health of registered services:

* **Health Check Configuration:**
  ```yaml
  health_check:
    interval: 30s
    timeout: 5s
    consecutive_failures: 3
    endpoints:
      - type: http
        path: /health
        expected_status: 200
      - type: tcp
        port: 443
  ```

* **Health States:**
  - **Healthy:** Service responding normally
  - **Degraded:** Slow response times or partial failures
  - **Unhealthy:** Service not responding or failing checks
  - **Unknown:** Unable to determine status

* **Automated Actions:**
  - Reduce ranking for degraded services
  - Remove unhealthy services from results
  - Send alerts on status changes
  - Trigger webhook notifications

### **Rate Limiting**

Comprehensive rate limiting to prevent abuse:

* **Configuration Levels:**
  ```yaml
  rate_limits:
    global:
      requests_per_second: 1000
      burst: 2000
    per_user:
      requests_per_minute: 100
      requests_per_hour: 1000
    per_api_key:
      requests_per_second: 50
    per_ip:
      requests_per_minute: 60
  ```

* **Rate Limit Headers:**
  ```
  X-RateLimit-Limit: 100
  X-RateLimit-Remaining: 75
  X-RateLimit-Reset: 1638360000
  ```

* **Adaptive Rate Limiting:**
  - Increase limits for trusted users
  - Decrease limits during high load
  - Exempt internal services

### **Multi-tenancy**

Support for isolated environments within a single deployment:

* **Tenant Isolation:**
  - Separate service registries per tenant
  - Isolated FAISS indexes
  - Tenant-specific policies
  - Data segregation at database level

* **Tenant Configuration:**
  ```json
  {
    "tenant_id": "acme_corp",
    "settings": {
      "max_services": 1000,
      "max_users": 500,
      "features": ["mcp_integration", "advanced_search"],
      "embedding_model": "custom-acme-model"
    }
  }
  ```

* **Cross-Tenant Features:**
  - Shared service marketplace
  - Federated search (with permissions)
  - Tenant-level analytics

## **Advanced Features**

### **Query Language**

Extended query syntax for power users:

* **Boolean Operators:**
  ```
  "send email" AND (customer OR client)
  "generate report" NOT financial
  ```

* **Domain Filters:**
  ```
  @domain:HR "employee onboarding"
  @exclude:Legacy "invoice processing"
  ```

* **Metadata Queries:**
  ```
  @version:>2.0 "payment processing"
  @auth:oauth2 "data export"
  ```

### **Query Templates**

Reusable query patterns:

```json
{
  "template_name": "find_communication_tool",
  "template": "send {message_type} to {recipient_type}",
  "parameters": {
    "message_type": ["email", "sms", "notification"],
    "recipient_type": ["customer", "employee", "vendor"]
  },
  "filters": {
    "domains": ["Communication"]
  }
}
```

### **Service Versioning**

Comprehensive version management with compatibility tracking:

#### **Version Schema**

Each service version includes:
```json
{
  "service_id": "svc_001",
  "version": "2.1.0",
  "version_tag": "stable",
  "deprecated": false,
  "compatible_with": ["2.0.*", "1.9.*"],
  "breaking_changes": [
    "Removed /legacy endpoint",
    "Changed auth from API key to OAuth2"
  ],
  "release_notes": "Added batch processing support",
  "created_at": "2024-11-01T10:00:00Z"
}
```

#### **Version Tags**
- **stable**: Production-ready, recommended version
- **beta**: Feature-complete but testing in progress
- **alpha**: Early preview, may have breaking changes
- **deprecated**: Marked for removal, migration required

#### **Compatibility Rules**

```python
class VersionCompatibility:
    def is_compatible(self, requested_version, service_version):
        """Check if service version satisfies requested version pattern"""
        # Exact match
        if requested_version == service_version.version:
            return True
        
        # Check compatible_with patterns
        for pattern in service_version.compatible_with:
            if self.matches_pattern(requested_version, pattern):
                return True
        
        # Semantic versioning rules
        return self.check_semver_compatibility(
            requested_version, 
            service_version.version
        )
```

#### **Deprecation Workflow**

1. **Mark as Deprecated:**
   ```sql
   UPDATE service_versions 
   SET deprecated = true,
       deprecated_at = NOW(),
       sunset_at = NOW() + INTERVAL '6 months',
       version_tag = 'deprecated'
   WHERE service_id = ? AND version = ?;
   ```

2. **Deprecation Notices:**
   ```json
   {
     "warning": "This service version is deprecated",
     "deprecated_since": "2024-12-01",
     "sunset_date": "2025-06-01",
     "migration_guide": "https://docs.internal/migrate-to-v3",
     "replacement_version": "3.0.0"
   }
   ```

3. **Grace Period Handling:**
   - Warnings in API responses
   - Email notifications to service consumers
   - Gradual traffic shifting to new version

#### **Version Discovery**

Enhanced search considers version requirements:

```json
// Request with version constraint
{
  "query": "invoice processing",
  "version_requirements": {
    "min_version": "2.0.0",
    "prefer_stable": true,
    "allow_deprecated": false
  }
}

// Response includes version info
{
  "results": [{
    "service": "InvoiceAPI",
    "versions": [
      {
        "version": "3.0.0",
        "tag": "stable",
        "match_score": 0.95
      },
      {
        "version": "2.5.0",
        "tag": "stable",
        "deprecated": true,
        "match_score": 0.93
      }
    ]
  }]
}
```

#### **Version Migration Support**

```python
class VersionMigrationHelper:
    def get_migration_path(self, from_version, to_version):
        """Generate migration steps between versions"""
        migrations = []
        
        # Get all intermediate versions
        path = self.find_upgrade_path(from_version, to_version)
        
        for i in range(len(path) - 1):
            migration = {
                "from": path[i],
                "to": path[i + 1],
                "breaking_changes": self.get_breaking_changes(path[i], path[i + 1]),
                "migration_script": self.get_migration_script(path[i], path[i + 1])
            }
            migrations.append(migration)
        
        return migrations
```

## **Migration and Import Tools**

### **Data Import Formats**

* **OpenAPI/Swagger Import:**
  ```bash
  kpath import openapi https://api.internal/swagger.json \
    --domain "Customer Service" \
    --auto-generate-descriptions
  ```

* **Service Catalog Import:**
  - CSV format with predefined schema
  - JSON bulk import
  - YAML service definitions
  - Excel template support

* **Import Validation:**
  - Schema validation
  - Duplicate detection
  - Dependency checking
  - Rollback on errors

### **Export Capabilities**

* **Backup Formats:**
  - Full database dump
  - Service registry export (JSON/YAML)
  - FAISS index snapshot
  - Configuration backup

* **Selective Export:**
  ```bash
  kpath export --format json \
    --domains "HR,Finance" \
    --include-policies \
    --output services-backup.json
  ```

## **Security and Privacy**

### **Access Control**

1. **Role-Based Access Control (RBAC):**
   - Predefined roles with permission sets
   - Service-level access restrictions
   - Administrative role separation

2. **Attribute-Based Access Control (ABAC):**
   - Dynamic policies based on user attributes
   - Contextual access (time, location, device)
   - Fine-grained service filtering
### **Data Protection**

- **Encryption:**
  - TLS 1.3 for all API communications
  - AES-256 for data at rest
  - Encrypted backups with key rotation

- **Privacy:**
  - Query anonymization options
  - PII detection and masking
  - Configurable data retention policies

### **Security Hardening**

#### **Response Timing Normalization**

Prevent timing attacks by ensuring uniform response times:

```python
class TimingNormalizer:
    def __init__(self, target_latency_ms=100):
        self.target_latency = target_latency_ms
    
    async def normalize_response(self, handler):
        start_time = time.time()
        
        # Process request
        result = await handler()
        
        # Calculate elapsed time
        elapsed_ms = (time.time() - start_time) * 1000
        
        # Add delay to reach target latency
        if elapsed_ms < self.target_latency:
            delay_ms = self.target_latency - elapsed_ms
            # Add random jitter ±10%
            jitter = random.uniform(-0.1, 0.1) * delay_ms
            await asyncio.sleep((delay_ms + jitter) / 1000)
        
        return result
```

Configuration:
```yaml
security:
  timing_protection:
    enabled: true
    target_latency_ms: 100
    jitter_percentage: 10
    exclude_endpoints: ["/health", "/metrics"]
```

#### **Error Sanitization**

Prevent information leakage through error messages:

```python
class ErrorSanitizer:
    def sanitize_error(self, error, request_context):
        # Log full error internally
        logger.error(f"Full error: {error}", extra={
            "request_id": request_context.id,
            "user_id": request_context.user_id,
            "traceback": traceback.format_exc()
        })
        
        # Return sanitized error to client
        if isinstance(error, ValidationError):
            return {
                "error": "Invalid request",
                "code": "VALIDATION_ERROR",
                "request_id": request_context.id
            }
        elif isinstance(error, AuthenticationError):
            return {
                "error": "Authentication failed",
                "code": "AUTH_ERROR"
            }
        else:
            # Generic error for unexpected issues
            return {
                "error": "Internal server error",
                "code": "INTERNAL_ERROR",
                "request_id": request_context.id
            }
```

#### **Logging Anonymization**

Protect user privacy in logs:

```python
class LogAnonymizer:
    def __init__(self):
        self.pii_patterns = [
            (r'\b[\w\.-]+@[\w\.-]+\.\w+\b', '[EMAIL]'),  # Email
            (r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]'),  # Phone
            (r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', '[CARD]'),  # Credit card
            (r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]'),  # SSN
        ]
    
    def anonymize(self, log_entry):
        # Hash user IDs
        if 'user_id' in log_entry:
            log_entry['user_id_hash'] = hashlib.sha256(
                log_entry['user_id'].encode()
            ).hexdigest()[:16]
            del log_entry['user_id']
        
        # Anonymize query text
        if 'query' in log_entry:
            anonymized_query = log_entry['query']
            for pattern, replacement in self.pii_patterns:
                anonymized_query = re.sub(pattern, replacement, anonymized_query)
            log_entry['query'] = anonymized_query
        
        # Remove sensitive headers
        if 'headers' in log_entry:
            sensitive_headers = ['Authorization', 'Cookie', 'X-API-Key']
            for header in sensitive_headers:
                if header in log_entry['headers']:
                    log_entry['headers'][header] = '[REDACTED]'
        
        return log_entry
```

#### **Privacy Configuration**

```yaml
privacy:
  logging:
    anonymize_queries: true
    anonymize_user_ids: true
    retention_days: 30
    
  pii_detection:
    enabled: true
    scan_request_body: true
    scan_response_body: false
    action: "reject"  # or "anonymize"
    
  gdpr_compliance:
    right_to_erasure: true
    data_portability: true
    consent_tracking: true
```

#### **Additional Security Measures**

- **Constant-time authentication:** Prevent timing attacks on password/token validation
- **Rate limiting:** Multi-level rate limits (global, per-user, per-IP)
- **Input validation:** Strict schema validation for all inputs
- **Security headers:** HSTS, CSP, X-Frame-Options, X-Content-Type-Options
- **Regular scanning:** Weekly dependency scans, monthly penetration tests

### **API Key Management**

* **Key Generation:**
  - Cryptographically secure random generation
  - Configurable key prefixes (e.g., `kpath_live_`, `kpath_test_`)
  - Key hashing with bcrypt/scrypt

* **Key Scoping:**
  ```json
  {
    "key_id": "key_001",
    "scopes": ["search:read", "services:read"],
    "rate_limit_override": 200,
    "allowed_ips": ["10.0.0.0/8"],
    "expires_at": "2025-12-31T23:59:59Z"
  }
  ```

* **Key Rotation:**
  - Automated rotation reminders
  - Grace period for old keys
  - Audit trail of key usage

### **Compliance Features**

* **GDPR Compliance:**
  - Query anonymization
  - User data export API
  - Right to deletion support
  - Consent management

* **Audit Trail Requirements:**
  - Immutable audit logs
  - Cryptographic log chaining
  - Long-term archive storage
  - Compliance reporting APIs

* **Data Residency:**
  - Geo-fencing for data storage
  - Regional service discovery
  - Cross-border transfer controls

## **Resilience and Reliability**

### **Circuit Breakers**

Prevent cascade failures with intelligent circuit breaking:

```yaml
circuit_breaker:
  failure_threshold: 5
  timeout: 30s
  half_open_requests: 3
  monitoring_interval: 10s
  exclude_status_codes: [404, 401]
```

### **Retry Policies**

Configurable retry strategies:

```json
{
  "retry_policy": {
    "max_attempts": 3,
    "backoff": "exponential",
    "initial_delay": "100ms",
    "max_delay": "10s",
    "retry_on": ["network_error", "timeout", "5xx"]
  }
}
```

### **Graceful Degradation**

* **Fallback Strategies:**
  - Return cached results on FAISS failure
  - Use keyword search if semantic search fails
  - Provide partial results on timeout
  - Static service list as last resort

* **Load Shedding:**
  - Priority queue for requests
  - Reject low-priority requests under load
  - Adaptive timeout adjustment

## **Technical Specifications**

### **FAISS Configuration**

* **Index Types and Parameters:**
  ```python
  # For small datasets (<100k vectors)
  index = faiss.IndexFlatL2(dimension)
  
  # For medium datasets (100k-1M vectors)
  index = faiss.IndexIVFFlat(
      quantizer, dimension, nlist=1024
  )
  
  # For large datasets (>1M vectors)
  index = faiss.IndexIVFPQ(
      quantizer, dimension, nlist=4096, m=8, nbits=8
  )
  ```

* **Memory Requirements:**
  - Flat index: 4 × dimension × num_vectors bytes
  - IVF index: (4 × dimension × num_vectors) / compression_ratio
  - PQ index: ~32-64 bytes per vector

* **Performance Tuning:**
  ```yaml
  faiss_config:
    index_type: "IVF4096,PQ8"
    nprobe: 32  # Number of clusters to search
    efSearch: 128  # For HNSW indexes
    train_size: 100000  # Vectors for training
  ```

### **Embedding Model Management**

* **Model Registry:**
  ```json
  {
    "model_id": "bge-base-en-1.5",
    "type": "sentence-transformer",
    "dimension": 768,
    "language": "en",
    "performance": {
      "inference_time_ms": 12,
      "memory_mb": 420
    }
  }
  ```

* **A/B Testing Framework:**
  ```yaml
  ab_test:
    control:
      model: "bge-base-en-1.5"
      weight: 0.5
    variant:
      model: "e5-large-v2"
      weight: 0.5
    metrics:
      - click_through_rate
      - user_satisfaction
    duration: "7d"
  ```

* **Model Migration:**
  1. Load new model in shadow mode
  2. Dual-index with both models
  3. A/B test on subset of traffic
  4. Gradual rollout if successful
  5. Rebuild index with new model

### **Performance Benchmarks**

* **Target SLAs:**
  - Search latency p50: <50ms
  - Search latency p95: <100ms
  - Search latency p99: <200ms
  - Throughput: 1000 QPS per node
  - Index update time: <5s for single update
  - Bulk import: 1000 services/minute

* **Optimization Strategies:**
  - Connection pooling
  - Query result caching
  - Embedding precomputation
  - Index sharding by domain
  - Read replicas for search

## **Observability and Monitoring**

### **Core Metrics**

#### **Performance Metrics**

```yaml
performance_metrics:
  query_latency:
    description: "End-to-end search request latency"
    unit: "milliseconds"
    aggregations: ["avg", "p50", "p75", "p95", "p99"]
    sla:
      p50: 50ms
      p95: 100ms
      p99: 200ms
  
  throughput:
    description: "Queries processed per second"
    unit: "requests/second"
    aggregations: ["rate_1m", "rate_5m"]
    
  error_rates:
    description: "Percentage of failed requests by type"
    categories:
      - "client_error_4xx"
      - "server_error_5xx"
      - "timeout_errors"
      - "validation_errors"
    alert_threshold: 1%
```

#### **Search Quality Metrics**

```yaml
search_quality_metrics:
  click_through_rate:
    description: "Percentage of searches resulting in selection"
    formula: "selections / total_searches"
    aggregations: ["hourly", "daily", "weekly"]
    baseline: 0.75
    
  mean_reciprocal_rank:
    description: "Average of 1/rank of first relevant result"
    formula: "mean(1/position_of_selected_result)"
    target: 0.8
    
  null_result_rate:
    description: "Searches returning no results"
    alert_threshold: 5%
    
  result_relevance_distribution:
    description: "Distribution of semantic similarity scores"
    buckets: [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    
  time_to_first_click:
    description: "Time between results shown and first selection"
    unit: "seconds"
    target_p50: 3s
```

#### **System Health Metrics**

```yaml
system_health_metrics:
  faiss_index:
    memory_usage_gb:
      description: "FAISS index memory consumption"
      alert_threshold: 90%
    vector_count:
      description: "Total vectors in index"
    index_freshness:
      description: "Time since last index update"
      alert_threshold: 3600s
    search_latency_ms:
      description: "Pure FAISS search time"
      
  postgresql:
    connection_pool:
      active: "Active connections"
      idle: "Idle connections"
      waiting: "Requests waiting for connection"
    replication_lag_ms:
      description: "Primary-replica lag"
      alert_threshold: 1000ms
    query_performance:
      slow_queries: "Queries over 100ms"
      deadlocks: "Deadlock count"
      
  cache_performance:
    embedding_cache:
      hit_rate: "Percentage of cache hits"
      miss_rate: "Percentage of cache misses"
      eviction_rate: "Evictions per minute"
      memory_usage_mb: "Cache memory usage"
    result_cache:
      hit_rate: "Result cache hit rate"
      ttl_expires: "Expires per minute"
```

#### **Embedding Metrics**

```yaml
embedding_metrics:
  generation_time_ms:
    description: "Time to generate embedding"
    aggregations: ["avg", "p95"]
    
  model_inference:
    batch_size: "Average batch size"
    gpu_utilization: "GPU usage percentage"
    memory_usage: "Model memory footprint"
    
  embedding_quality:
    dimension_coverage: "Active dimensions percentage"
    similarity_distribution: "Distribution of similarities"
```

### **A/B Testing Framework**

```python
class ABTestMetrics:
    def __init__(self):
        self.experiments = {}
    
    def track_experiment(self, experiment_id, variant, metrics):
        """Track metrics for A/B test variant"""
        if experiment_id not in self.experiments:
            self.experiments[experiment_id] = {
                'start_time': datetime.now(),
                'variants': {}
            }
        
        variant_data = self.experiments[experiment_id]['variants'].get(
            variant, 
            {'count': 0, 'metrics': defaultdict(list)}
        )
        
        variant_data['count'] += 1
        for metric, value in metrics.items():
            variant_data['metrics'][metric].append(value)
        
        self.experiments[experiment_id]['variants'][variant] = variant_data
    
    def get_experiment_results(self, experiment_id):
        """Calculate statistical significance of experiment"""
        experiment = self.experiments.get(experiment_id)
        if not experiment:
            return None
        
        results = {}
        for variant, data in experiment['variants'].items():
            results[variant] = {
                'sample_size': data['count'],
                'metrics': {}
            }
            
            for metric, values in data['metrics'].items():
                results[variant]['metrics'][metric] = {
                    'mean': np.mean(values),
                    'std': np.std(values),
                    'p95': np.percentile(values, 95)
                }
        
        # Calculate statistical significance
        if len(results) == 2:  # A/B test
            variants = list(results.keys())
            for metric in results[variants[0]]['metrics']:
                control = results[variants[0]]['metrics'][metric]
                treatment = results[variants[1]]['metrics'][metric]
                
                # T-test for significance
                t_stat, p_value = stats.ttest_ind(
                    data['metrics'][metric] for variant, data in experiment['variants'].items()
                )
                
                results['significance'] = {
                    metric: {
                        't_statistic': t_stat,
                        'p_value': p_value,
                        'significant': p_value < 0.05
                    }
                }
        
        return results
```

### **Metrics Dashboard**

```yaml
dashboard_panels:
  - name: "Real-Time Performance"
    refresh: 10s
    widgets:
      - type: "line_chart"
        metric: "query_latency_p95"
        period: "1h"
      - type: "gauge"
        metric: "current_qps"
        thresholds: [100, 500, 1000]
        
  - name: "Search Quality"
    refresh: 60s
    widgets:
      - type: "line_chart"
        metric: "click_through_rate"
        period: "24h"
      - type: "heatmap"
        metric: "relevance_score_distribution"
        
  - name: "A/B Test Results"
    refresh: 300s
    widgets:
      - type: "comparison_table"
        experiments: "active"
        metrics: ["ctr", "latency", "relevance"]
      - type: "significance_chart"
        show_confidence_intervals: true
```

### **Alerting Rules**

```yaml
alerts:
  - name: "High Query Latency"
    condition: "query_latency_p95 > 200ms for 5m"
    severity: "warning"
    
  - name: "Low Click-Through Rate"
    condition: "click_through_rate < 0.5 for 30m"
    severity: "warning"
    
  - name: "FAISS Memory Critical"
    condition: "faiss_memory_usage > 90%"
    severity: "critical"
    
  - name: "Index Staleness"
    condition: "time_since_index_update > 2h"
    severity: "warning"
    
  - name: "Experiment Significance Reached"
    condition: "ab_test_p_value < 0.05"
    severity: "info"
```
### **Logging**

- Structured JSON logs
- Correlation IDs for request tracing
- Log aggregation to central system
- Sensitive data masking

### **Distributed Tracing**

* **OpenTelemetry Integration:**
  ```yaml
  tracing:
    enabled: true
    exporter: "otlp"
    endpoint: "http://otel-collector:4317"
    sample_rate: 0.1
    propagators: ["tracecontext", "baggage"]
  ```

* **Trace Points:**
  - API request entry/exit
  - Database queries
  - FAISS search operations
  - External service calls
  - Cache operations

* **Custom Spans:**
  ```python
  with tracer.start_as_current_span("semantic_search") as span:
      span.set_attribute("query.text", query)
      span.set_attribute("query.embedding_dim", 768)
      span.set_attribute("results.count", len(results))
  ```

### **Debug Mode**

* **Query Explanation:**
  ```json
  {
    "query": "send invoice",
    "explanation": {
      "embedding_generation_ms": 12,
      "faiss_search_ms": 8,
      "candidates": [
        {
          "service": "InvoiceService",
          "raw_score": 0.92,
          "feedback_boost": 0.03,
          "final_score": 0.95,
          "factors": {
            "semantic_similarity": 0.92,
            "domain_match": true,
            "recent_usage": 0.8
          }
        }
      ],
      "filters_applied": ["domain:Finance", "status:active"]
    }
  }
  ```

* **Performance Profiling:**
  - Flame graphs for request processing
  - Memory allocation tracking
  - Query plan analysis

## **SDK and Client Libraries**

### **Official SDKs**

* **Python SDK:**
  ```python
  from kpath import KPATHClient
  
  client = KPATHClient(
      api_key="kpath_live_...",
      base_url="https://kpath.internal/api/v1"
  )
  
  results = client.search(
      query="process payment",
      filters={"domains": ["Finance"]},
      limit=5
  )
  ```

* **JavaScript/TypeScript SDK:**
  ```typescript
  import { KPATHClient } from '@kpath/client';
  
  const client = new KPATHClient({
    apiKey: process.env.KPATH_API_KEY,
    timeout: 5000,
  });
  
  const results = await client.search({
    query: 'send notification',
    userContext: { roles: ['admin'] }
  });
  ```

* **Java SDK:**
  ```java
  KPATHClient client = KPATHClient.builder()
      .apiKey("kpath_live_...")
      .connectTimeout(Duration.ofSeconds(5))
      .build();
  
  SearchResults results = client.search(
      SearchRequest.builder()
          .query("generate report")
          .minScore(0.8)
          .build()
  );
  ```

* **Go SDK:**
  ```go
  client := kpath.NewClient(
      kpath.WithAPIKey("kpath_live_..."),
      kpath.WithTimeout(5 * time.Second),
  )
  
  results, err := client.Search(ctx, &kpath.SearchRequest{
      Query: "update customer record",
      Limit: 10,
  })
  ```

### **SDK Features**

* **Common Functionality:**
  - Automatic retry with backoff
  - Request/response logging
  - Error handling and types
  - Async/await support
  - Streaming responses (where applicable)

* **Development Tools:**
  - Mock client for testing
  - Request builders
  - Response validators
  - Debug mode
  - Performance metrics

## **Disaster Recovery**

### **Comprehensive Backup Strategy**

#### **1. PostgreSQL Backup and Recovery**

**Continuous WAL Archiving:**
```yaml
postgresql:
  wal_archiving:
    enabled: true
    archive_mode: "on"
    archive_command: "pgbackrest --stanza=kpath archive-push %p"
    archive_timeout: 300  # 5 minutes
    
  backup_schedule:
    full_backup:
      frequency: "daily"
      time: "02:00 UTC"
      retention: 30  # days
      
    incremental_backup:
      frequency: "hourly"
      retention: 7  # days
      
    wal_retention:
      minimum: 3  # days
      maximum: 7  # days
```

**Backup Script:**
```bash
#!/bin/bash
# PostgreSQL Full Backup with pgBackRest

pgbackrest --stanza=kpath \
           --type=full \
           --repo-retention-full=30 \
           --compress-level=6 \
           --process-max=4 \
           backup

# Verify backup
pgbackrest --stanza=kpath info

# Upload to offsite storage
aws s3 sync /var/lib/pgbackrest \
            s3://kpath-backups/postgres/ \
            --storage-class GLACIER
```

**Point-in-Time Recovery (PITR):**
```bash
# Restore to specific timestamp
pgbackrest --stanza=kpath \
           --type=time \
           --target="2024-12-10 14:30:00 UTC" \
           --target-action=promote \
           restore

# Restore to specific transaction
pgbackrest --stanza=kpath \
           --type=xid \
           --target="1234567" \
           restore
```

#### **2. FAISS Index Backup and Recovery**

**Snapshot Strategy:**
```python
class FAISSBackupManager:
    def __init__(self, index_path, backup_path):
        self.index_path = index_path
        self.backup_path = backup_path
        
    def create_snapshot(self):
        """Create consistent FAISS index snapshot"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_name = f"faiss_snapshot_{timestamp}"
        
        # Pause writes to ensure consistency
        with self.write_lock():
            # Calculate checksum
            checksum = self.calculate_checksum(self.index_path)
            
            # Create snapshot
            snapshot_path = os.path.join(self.backup_path, snapshot_name)
            shutil.copytree(self.index_path, snapshot_path)
            
            # Save metadata
            metadata = {
                "timestamp": timestamp,
                "checksum": checksum,
                "vector_count": self.get_vector_count(),
                "index_type": self.get_index_type(),
                "embedding_model": self.get_model_version()
            }
            
            with open(f"{snapshot_path}/metadata.json", "w") as f:
                json.dump(metadata, f)
                
        return snapshot_name
    
    def restore_snapshot(self, snapshot_name, verify=True):
        """Restore FAISS index from snapshot"""
        snapshot_path = os.path.join(self.backup_path, snapshot_name)
        
        # Verify snapshot integrity
        if verify:
            if not self.verify_snapshot(snapshot_path):
                raise Exception("Snapshot verification failed")
        
        # Backup current index
        self.create_backup("pre_restore_backup")
        
        # Restore snapshot
        with self.write_lock():
            shutil.rmtree(self.index_path)
            shutil.copytree(snapshot_path, self.index_path)
            
        # Warm up index
        self.warm_index()
        
        return True
```

**Incremental Index Updates:**
```python
def backup_incremental_changes():
    """Backup only changed vectors since last snapshot"""
    last_snapshot = get_latest_snapshot()
    changes = get_vector_changes_since(last_snapshot.timestamp)
    
    incremental_backup = {
        "base_snapshot": last_snapshot.name,
        "timestamp": datetime.now(),
        "added_vectors": changes.added,
        "removed_vectors": changes.removed,
        "updated_vectors": changes.updated
    }
    
    save_incremental_backup(incremental_backup)
```

#### **3. Configuration Backup**

**Infrastructure as Code:**
```yaml
# terraform/kpath_config.tf
resource "aws_s3_bucket" "kpath_config_backup" {
  bucket = "kpath-config-backup"
  
  versioning {
    enabled = true
  }
  
  lifecycle_rule {
    enabled = true
    
    noncurrent_version_expiration {
      days = 90
    }
  }
}

# Backup all configuration
resource "aws_s3_bucket_object" "config_files" {
  for_each = fileset("${path.module}/config", "**/*")
  
  bucket = aws_s3_bucket.kpath_config_backup.id
  key    = each.value
  source = "${path.module}/config/${each.value}"
  etag   = filemd5("${path.module}/config/${each.value}")
}
```

### **Recovery Playbook**

#### **Scenario 1: Complete System Failure**

```bash
#!/bin/bash
# Complete disaster recovery playbook

# 1. Provision new infrastructure
terraform apply -auto-approve

# 2. Restore PostgreSQL
echo "Restoring PostgreSQL..."
pgbackrest --stanza=kpath \
           --delta \
           --log-level-console=info \
           restore

# Start PostgreSQL
systemctl start postgresql

# 3. Restore FAISS index
echo "Restoring FAISS index..."
python restore_faiss.py --snapshot latest --verify

# 4. Restore configuration
echo "Restoring configuration..."
aws s3 sync s3://kpath-config-backup/config /opt/kpath/config

# 5. Deploy application
kubectl apply -f k8s/kpath-deployment.yaml

# 6. Verify system health
python verify_recovery.py --full-check
```

#### **Scenario 2: FAISS Index Corruption**

```python
def handle_index_corruption():
    """Automated recovery from FAISS index corruption"""
    
    # 1. Detect corruption
    if not verify_index_integrity():
        logger.error("FAISS index corruption detected")
        
        # 2. Switch to backup index
        switch_to_backup_index()
        
        # 3. Attempt repair
        try:
            repair_index()
            if verify_index_integrity():
                logger.info("Index repaired successfully")
                return
        except Exception as e:
            logger.error(f"Repair failed: {e}")
        
        # 4. Restore from snapshot
        latest_snapshot = get_latest_valid_snapshot()
        restore_snapshot(latest_snapshot)
        
        # 5. Replay recent changes
        replay_changes_since(latest_snapshot.timestamp)
        
        # 6. Verify recovery
        run_integrity_checks()
```

#### **Scenario 3: Partial Data Loss**

```sql
-- Restore specific tables from backup
-- while keeping system online

-- 1. Create temporary schema
CREATE SCHEMA recovery_temp;

-- 2. Restore to temporary schema
pg_restore --schema-only \
           --schema=recovery_temp \
           --dbname=kpath \
           backup_file.dump

-- 3. Copy missing data
INSERT INTO services 
SELECT * FROM recovery_temp.services 
WHERE id NOT IN (SELECT id FROM services);

-- 4. Cleanup
DROP SCHEMA recovery_temp CASCADE;
```

### **Recovery Time Objectives (RTO)**

| Component | RTO | RPO | Method |
|-----------|-----|-----|---------|
| PostgreSQL | 15 min | 5 min | WAL streaming + automated failover |
| FAISS Index | 5 min | 1 hour | Hot standby + snapshots |
| API Service | 2 min | 0 | Stateless + auto-scaling |
| Configuration | 10 min | 24 hours | Git + S3 versioning |

### **Disaster Recovery Testing**

```yaml
dr_testing:
  schedule: "quarterly"
  scenarios:
    - full_datacenter_failure
    - database_corruption
    - index_corruption
    - network_partition
    
  validation:
    - data_integrity_check
    - service_availability
    - performance_benchmarks
    - security_audit
    
  documentation:
    - update_runbooks
    - record_recovery_times
    - identify_improvements
```

## **Use Cases and Agent Workflows**

### **Internal Agent to Internal Agent**
- HR Bot queries: "Find employee onboarding checklist"
- KPATH returns HR Service with "GetOnboardingChecklist" capability
- Direct API integration using returned endpoint
### **Personal Assistant + Internal Tooling**
- User: "Reset my password"
- PA queries KPATH → Returns IAM Service
- PA formats request per schema and calls IAM API

### **Personal Assistant + External Agent (MCP)**
- User: "Book a business flight to London"
- KPATH returns both internal Travel Service and external Amadeus MCP
- PA selects based on policies and user preferences

### **Multi-Service Orchestration Discovery**
- Complex query: "Plan team offsite with travel and catering"
- KPATH returns multiple relevant services
- PA or orchestrator combines capabilities

## **Testing Strategy**

### **Test Types**

1. **Unit Tests:**
   - Embedding generation accuracy
   - Policy evaluation logic
   - Cache operations

2. **Integration Tests:**
   - API endpoint validation
   - Database operations
   - FAISS search accuracy

3. **Performance Tests:**
   - Load testing with realistic query patterns
   - Stress testing index updates
   - Latency benchmarks

4. **Security Tests:**
   - Penetration testing
   - Authentication bypass attempts
   - Policy enforcement validation

### **Test Data Management**

* **Synthetic Data Generation:**
  ```python
  # Generate test services with realistic descriptions
  test_services = generate_test_services(
      count=1000,
      domains=["HR", "Finance", "IT"],
      capability_patterns=["CRUD", "Report", "Integration"]
  )
  ```

* **Test Scenarios:**
  - Edge cases (empty queries, special characters)
  - Multi-language queries
  - Ambiguous requests
  - Domain-specific terminology

### **Continuous Testing**

* **CI/CD Integration:**
  ```yaml
  test_pipeline:
    - unit_tests:
        coverage_threshold: 80%
    - integration_tests:
        environments: ["staging"]
    - performance_tests:
        baseline_comparison: true
    - security_scan:
        owasp_top_10: true
  ```

* **Automated Quality Gates:**
  - Semantic accuracy > 90%
  - Latency regression < 10%
  - Zero security vulnerabilities
  - API compatibility check

### **Chaos Engineering**

* **Failure Scenarios:**
  - Random service failures
  - Network partitions
  - Database connection loss
  - FAISS index corruption
  - Cache poisoning

* **Resilience Validation:**
  ```bash
  chaos-monkey --target kpath \
    --scenarios "kill-pods,network-delay,cpu-stress" \
    --duration 1h \
    --alert-on-sla-breach
  ```

## **Deployment and Operations**

### **Deployment Pipeline**

* **Blue-Green Deployment:**
  ```yaml
  deployment:
    strategy: blue-green
    health_check_delay: 30s
    traffic_shift:
      - 10%: 5m
      - 50%: 10m
      - 100%: 15m
    rollback_on_error: true
  ```

* **Canary Releases:**
  - Gradual rollout to subset of users
  - Automated metrics comparison
  - Automatic rollback on anomalies

### **Operational Runbooks**

* **Common Issues:**
  1. **High Latency:**
     - Check FAISS index size
     - Verify cache hit rates
     - Review database query performance
  
  2. **Service Discovery Failures:**
     - Validate integration endpoints
     - Check authentication tokens
     - Review network connectivity

* **Emergency Procedures:**
  - Service degradation protocol
  - Data recovery steps
  - Stakeholder communication plan

## **Cost Optimization**

### **Resource Management**

* **Auto-scaling Policies:**
  ```yaml
  autoscaling:
    min_replicas: 2
    max_replicas: 20
    metrics:
      - type: cpu
        target: 70%
      - type: custom
        metric: request_latency_p95
        target: 100ms
  ```

* **Cost Controls:**
  - Embedding computation quotas
  - API rate limits by tier
  - Storage optimization (index compression)
  - Idle resource shutdown

### **Usage Analytics**

* **Cost Attribution:**
  - Per-tenant resource usage
  - Per-query computational cost
  - Storage costs by service domain
  - API call pricing tiers

## **Future Enhancements**

* **Embedding Model Registry:** Version and A/B test different embedding models
* **Semantic Query Expansion:** Use synonyms and domain knowledge
* **Multi-Modal Search:** Support for image or voice queries
* **Graph-Based Recommendations:** Service co-occurrence patterns
* **Real-Time Index Updates:** Streaming architecture for instant updates
* **Federation:** Connect multiple KPATH instances across organizations
* **Natural Language Policies:** Define access rules in plain English
## **Summary**

KPATH Enterprise provides a comprehensive, enterprise-grade semantic discovery layer for AI agent ecosystems. This v3 specification encompasses:

**Core Capabilities:**
- High-performance semantic search using FAISS
- Rich service and capability registry with PostgreSQL
- Feedback-driven ranking with machine learning potential
- Comprehensive admin interface for service management
- Enterprise-grade security with RBAC/ABAC

**Integration Features:**
- Native MCP (Model Context Protocol) support
- ESB integration (Mulesoft, Apache Camel)
- Multiple service discovery mechanisms
- Webhook-based event system

**Operational Excellence:**
- Multi-tenancy support for shared deployments
- Advanced monitoring with distributed tracing
- Comprehensive rate limiting and resilience features
- Automated health monitoring and circuit breakers
- Cost optimization and resource management

**Developer Experience:**
- RESTful API with OpenAPI documentation
- Full Admin API for programmatic management
- Official SDKs in Python, JavaScript, Java, and Go
- Advanced query language with filters and templates
- Debug mode with query explanations

**Enterprise Readiness:**
- Flexible deployment options (on-prem, cloud, hybrid)
- Compliance features (GDPR, audit trails)
- Sophisticated version management
- Import/export tools for migration
- Comprehensive testing and chaos engineering
- Operational runbooks and deployment strategies

The system's modular architecture ensures it can grow with organizational needs while maintaining consistent performance, security, and reliability standards. With its focus on developer experience, operational excellence, and enterprise requirements, KPATH Enterprise serves as the foundational discovery layer for the next generation of AI-powered enterprise systems.