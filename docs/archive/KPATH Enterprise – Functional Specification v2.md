# **KPATH Enterprise – Functional Specification**

## **Introduction**

KPATH Enterprise is a semantic search service for internal AI capabilities, designed to help an AI personal assistant (or agent) discover **which internal agents and tools** can fulfill a given natural language request. It acts as a “capability registry” lookup: given a prompt, KPATH returns the best-matching agents and their specific tools (capabilities) by analyzing semantic meaning, rather than exact keywords. Crucially, KPATH **performs discovery only** – it does **not orchestrate or execute** any actions itself. This service is intended for enterprise environments, where it can be deployed on-premises, in the cloud, or in hybrid setups to meet organizational needs.

## **Key Features and Requirements**

* **Semantic Capability Matching Only:** KPATH focuses on semantic similarity search over a registry of available capabilities. It converts the user’s natural language prompt into a vector embedding (a numerical representation of the query’s meaning) and finds which agent tools have descriptions with similar embeddings (i.e. similar meanings). It does **not** perform any workflow routing or tool execution – it simply returns relevant matches.

* **Agent and Tool Registry:** The system maintains a registry of internal **agents** (services or modules) and the **tools** (capabilities) each agent exposes. Each tool is essentially a discrete capability (e.g. an agent “CalendarAgent” might expose a tool “CreateEvent” to schedule meetings). For every tool, the registry stores metadata such as:

  * **Agent Name** – e.g. `"CalendarAgent"`.  
  * **Tool Name** – e.g. `"CreateEvent"`.  
  * **Tool Description** – a human-readable description of what the tool does.  
  * **Embedding** – the vector embedding of the description (used for semantic search).  
  * **Runtime Metadata (optional):** Details for calling or using the tool, such as an API endpoint or function identifier, input schema, and any auth requirements.  
* **Relevant Results with Scores:** Given a prompt, KPATH returns a list of the most relevant agent tools, each with a **similarity score** indicating how well it semantically matches the query. The score (e.g. a cosine similarity or normalized distance) allows the caller to gauge confidence. Results are ordered by descending relevance score (0 to 1, with 1 being a perfect match). The response structure for each match includes: the agent name, tool name, description, the match score, and any provided runtime metadata (like endpoint, input schema, auth). This structured output enables the calling assistant to easily interpret and potentially invoke the suggested tool if it has execution logic elsewhere.

* **Enterprise Deployment (On-Prem, Cloud, Hybrid):** KPATH Enterprise is designed for flexible deployment in corporate environments. It can be containerized and run on-premises (within a secure intranet or data center), deployed to a private cloud or an enterprise’s VPC, or offered as a hybrid service (e.g. search logic in cloud but data remains on-prem). The architecture should support high availability and scaling (e.g. horizontal scaling of the search service and the embedding vector index) to accommodate many concurrent queries. Data privacy and security are prioritized – all capability data and embeddings can be stored in enterprise-controlled databases. No sensitive query or embedding data needs to leave the organization’s environment in an on-prem deployment.

* **Security and Access Control Integration:** The service can integrate with enterprise Identity and Access Management (IAM) systems to **filter discovery results based on the caller’s permissions**. This means KPATH will only surface tools that the requesting user (or the user’s team/role) is allowed to discover. For example, if certain tools are restricted to HR department agents, a user outside HR would not see those in results. This **user-context filtering** is analogous to document-level access control in enterprise search – e.g. “you can filter a user's search results based on the user or their group access”. KPATH’s registry can store access tags (such as allowed roles or teams for each tool) and apply policy rules at query time.

* **Standards-Based API:** KPATH exposes its functionality via a RESTful API, documented in an OpenAPI (Swagger) specification for easy integration. The API accepts a natural language query and returns structured results in JSON. By adhering to OpenAPI standards, the service is self-documented and compatible with enterprise API management tools. Clients (such as the AI assistant) can be auto-generated from the OpenAPI spec, ensuring smooth integration.

* **No Workflow Orchestration:** It is emphasized that KPATH does not execute actions. It **only** provides a semantic lookup service. Orchestration (i.e. actually calling the chosen tool and handling its output) is handled by the AI assistant or another component. This separation keeps KPATH’s design focused and narrow: indexing and retrieving capability metadata with high semantic relevance.

## **Data Schema (PostgreSQL-Compatible)**

KPATH stores information about agents and tools in a relational database for reliability and ease of query. A PostgreSQL-compatible schema is proposed, leveraging standard SQL and the **pgvector** extension (for vector similarity search) to manage embeddings. The core tables might include **Agents**, **Tools**, and possibly a separate table or extension-managed column for **embeddings**. Below is a simplified schema definition:

\-- Enable the pgvector extension for vector storage (Postgres 13+)  
CREATE EXTENSION IF NOT EXISTS vector;

\-- Agents table: each agent is a container for tools/capabilities  
CREATE TABLE agents (  
    agent\_id SERIAL PRIMARY KEY,  
    name TEXT UNIQUE NOT NULL,        \-- e.g. "CalendarAgent"  
    description TEXT                  \-- optional description of the agent’s role  
);

\-- Tools (Capabilities) table: each row is a tool exposed by an agent  
CREATE TABLE tools (  
    tool\_id SERIAL PRIMARY KEY,  
    agent\_id INTEGER NOT NULL REFERENCES agents(agent\_id) ON DELETE CASCADE,  
    name TEXT NOT NULL,              \-- e.g. "CreateEvent"  
    description TEXT NOT NULL,       \-- description of what the tool does  
    endpoint TEXT,                   \-- optional endpoint/URL or identifier to invoke the tool  
    input\_schema JSONB,              \-- optional JSON schema for tool input parameters  
    auth\_type TEXT,                  \-- optional auth requirement (e.g. "OAuth2", "API Key", "None")  
    allowed\_roles TEXT\[\],            \-- optional list of roles/team tags allowed to use/discover this tool  
    embedding vector(1536)           \-- vector embedding of the description (1536 dims if using OpenAI ada)  
);

\-- Index for vector similarity search on the embedding (IVFFLAT index with cosine distance)  
CREATE INDEX tool\_embedding\_idx ON tools USING ivfflat (embedding vector\_cosine\_ops);

**Notes on the schema:**

* The `agents` table holds each agent’s basic info. The `tools` table represents capabilities. Each tool is linked to an agent via `agent_id`. Tools store descriptive metadata and an `embedding` vector for semantic search. We use a `vector(1536)` type here as an example dimension (1536 is the dimensionality of OpenAI’s `text-embedding-ada-002` model embeddings). The pgvector extension provides the `vector` column type and indexing mechanisms for similarity search.

* The `endpoint` field (if provided) could be a URL or internal RPC handle where the tool can be invoked. This is optional runtime metadata – not needed for the search itself, but returned so that a calling system knows how to call the tool if selected. Similarly, `input_schema` can hold a JSON Schema or parameters definition for the tool’s expected input (useful for the assistant to format a correct call), and `auth_type` indicates what authentication or permissions are required to call the tool’s API (e.g. some tools might require a service token or user delegation).

* The `allowed_roles` is an array of identifiers (role names, team names, etc.) used for IAM-based filtering. For example, a tool might have `allowed_roles = ['HR', 'Recruiting']`, meaning only users with those roles should see it. If a tool is open to all, this field can be NULL or empty.

* The `embedding` column stores the semantic vector for the tool’s description. By indexing this column with `ivfflat ... vector_cosine_ops`, we enable efficient approximate nearest-neighbor search using cosine similarity (common for embedding similarity). pgvector supports multiple distance metrics (inner product, Euclidean, cosine, etc.), and here we choose cosine distance for semantic relevance. The index improves query performance for large numbers of tools.

* **Alternate Storage:** While the above uses Postgres for both metadata and vector storage, KPATH could also use an external specialized vector database. In that case, the `embedding` might not be stored in the SQL table; instead, each tool’s embedding could be saved in a vector store (keyed by tool\_id) at indexing time. The Postgres schema would then exclude the `embedding` column, and the search component would query the vector DB for nearest neighbors. This design is flexible: enterprises can choose to keep everything in Postgres (leveraging pgvector for a single data store with ACID compliance) or use a dedicated vector engine if scaling demands. Popular open-source vector databases like **Milvus** or **Weaviate** are options – for example, *“Milvus is an open-source vector database for embedding similarity search and AI applications” and it works across local or cloud environments.* Such systems can handle very large vector indexes and offer hybrid search capabilities, but involve additional infrastructure. KPATH’s design allows either approach, as long as the tool metadata and embeddings remain consistent.

## **Semantic Matching Implementation**

**Embedding Model:** To power semantic search, KPATH relies on a vector **embedding model** that can translate text into a high-dimensional numeric vector capturing its meaning. In practice, each tool’s description is pre-computed into an embedding vector when the tool is registered (or updated), and query prompts are likewise embedded at runtime. A suitable embedding model (typically a transformer-based language model) must be chosen for the enterprise use case. For instance, OpenAI’s *text-embedding-ada-002* is a popular model that produces 1536-dimensional embeddings for any given text. Alternatively, open-source models (like SBERT sentence transformers or other LLM-based embeddings) can be deployed on-prem to avoid external API calls. The chosen model should be capable of capturing domain-specific language if the enterprise has a lot of jargon (fine-tuning or domain-specific embeddings might be considered for better results).

**Rationale:** *“A vector embedding model is responsible for the transformation of unstructured data (text, images, audio, video) into a vector of numbers that capture semantic similarity between data objects”. By converting both user queries and tool descriptions into this vector space, KPATH can measure their semantic closeness. Intuitively, if a user asks for something and a tool’s description means the same thing, their vectors will be near each other in this space, even if they don’t share keywords.*

**Vector Search:** When a query comes in, KPATH will perform a nearest-neighbor search in the embedding vector space to find the top matching tools. If using Postgres/pgvector, this is done via a SQL query using the `<=>` cosine distance operator or similar, with an `ORDER BY embedding <=> query_vector LIMIT K`. If using an external vector store, the service would query that store’s API to get the top K most similar vectors to the query’s vector. The result of the vector search is a set of tool identifiers with similarity scores (distance or similarity). These are then retrieved from the tools registry to assemble the final result set with full metadata.

**Similarity Scoring:** The raw output of the vector similarity search is often a distance (where lower is more similar for Euclidean or cosine distance). KPATH will convert this to a more intuitive score (for example, score \= 1 – cosine\_distance, to produce a similarity value where higher is better). All scores can be normalized to 0–1. This score indicates confidence in the match – e.g. a score of 0.95 suggests a very strong match in meaning. Typically, a threshold or top-N approach is used: e.g. return the top 5 matches above a certain similarity score. The exact threshold can be configurable.

**Filtering and Ranking:** After retrieving the top candidates by similarity, KPATH applies any necessary **filters** (such as IAM-based restrictions or other metadata filters). For instance, if the query came from user “Alice” who is in Engineering, and one of the top matches is an HR-only tool, KPATH would drop that result (based on `allowed_roles`). In such cases, it may fetch the next best result to still return the requested number of suggestions. The final list is then sorted by score descending.

Optionally, additional ranking logic can be applied if needed – for example, the system might slightly boost results from the same department as the user, or deprioritize deprecated tools. However, by default, pure semantic similarity is the primary ranking criterion.

**Embedding Vector Store Options:** For enterprise-grade deployments, KPATH can utilize different backing technologies for vector search:

* **PostgreSQL with pgvector:** As shown in the schema, this keeps all data in one place. pgvector supports both exact and approximate nearest neighbor search within Postgres. This is convenient and benefits from Postgres features (transactions, backups, etc.), but very large sets of embeddings (millions of vectors) might require careful indexing and hardware (or use of Postgres-compatible distributed systems).

* **Dedicated Vector Database:** Using a separate vector DB can improve scalability for huge vector counts or very high query throughput. Many open-source options exist (Milvus, Weaviate, Vespa, etc.) which are optimized for similarity search at scale. These often support HNSW or other advanced indexing out-of-the-box for fast approximate search. Enterprise users can deploy them on-prem or use managed cloud versions. For example, *Milvus provides a consistent experience whether on a developer’s laptop, a local cluster, or in the cloud*, making it suitable for hybrid deployments. The choice may depend on the organization’s comfort – if they prefer to minimize moving parts, pgvector might suffice; if they already use a vector DB or need extreme scale, that can be plugged in. KPATH’s logic to generate query embeddings and retrieve nearest neighbors would be abstracted to work with either backend.

* **Embedding Update and Maintenance:** Whenever a new tool is added to the registry, KPATH must compute its embedding via the chosen model and store it. Similarly, if a tool’s description is modified, its embedding should be recomputed. This can be handled synchronously (on registration) or in batch jobs. The system might also periodically re-index or vacuum the vector index for optimal performance, especially if using approximate indexes that benefit from rebuilding when data changes.

## **REST API Design (OpenAPI Style)**

KPATH provides a RESTful HTTP API for querying the capability registry. The API is simple, centered around a search endpoint since KPATH’s primary function is semantic lookup. In an OpenAPI-like specification, the service might be described as follows:

**Base URL:** The service could be hosted at an endpoint like `https://kpath.company.com/api` (for enterprise internal network) or a route in a larger enterprise API gateway. Only secure connections (HTTPS) are used.

**Authentication:** The API can integrate with the enterprise’s auth (for example, requiring a JWT or OAuth2 token in the Authorization header to identify the caller). The user identity from this token would be used for filtering results. (If KPATH is used by an internal assistant service, that assistant might call KPATH with a system identity plus an impersonation of the end-user or include the end-user’s roles in the request.)

### **`POST /search` – Semantic Capability Search**

**Description:** Accepts a natural language prompt and returns a list of matching agents/tools from the registry, ranked by relevance.

**Request Body (JSON):** The query and optional context. For example:

 {  
  "query": "Schedule a meeting with the VP next week",  
  "user\_id": "alice@example.com",  
  "user\_roles": \["Engineering", "ExecutiveAssistant"\]  
}

*  **Fields:**

  * `query` (string, required): The natural language prompt describing what the user wants to do. This could be a full sentence or keywords; KPATH will interpret it semantically.  
  * `user_id` (string, optional): The identifier of the user or calling agent. This might be used for logging or additional policy checks. (In many cases, the system might rely on auth token for identity instead of an explicit field.)  
  * `user_roles` (array of strings, optional): The roles/team context of the user. If provided, KPATH will use this to filter results (only show tools whose `allowed_roles` intersect with the user’s roles, if such restrictions exist). If not provided, KPATH may derive roles from the auth token or assume no filtering (i.e. all results visible).  
* *Note:* In an OpenAPI definition, these fields would be defined in the schema. For example, `query` as a required property, and `user_roles` could be a list of enums or free-form strings depending on enterprise IAM design.

**Response Body (JSON):** On success (HTTP 200), returns a JSON object containing an array of results. For example:

 {  
  "query": "Schedule a meeting with the VP next week",  
  "results": \[  
    {  
      "agent": "CalendarAgent",  
      "tool": "CreateEvent",  
      "description": "Schedule a new meeting on the corporate calendar with specified participants, date, and time.",  
      "score": 0.93,  
      "endpoint": "https://api.internal.corp/CalendarAgent/v1/create\_event",  
      "input\_schema": {  
        "type": "object",  
        "required": \["date", "time", "attendees"\],  
        "properties": {  
          "date": { "type": "string", "format": "date" },  
          "time": { "type": "string", "format": "time" },  
          "attendees": { "type": "array", "items": { "type": "string" } },  
          "subject": { "type": "string" }  
        }  
      },  
      "auth": "OAuth2"  
    },  
    {  
      "agent": "EmailAgent",  
      "tool": "SendEmail",  
      "description": "Send an email to specified recipients with a subject and body.",  
      "score": 0.77,  
      "endpoint": "https://api.internal.corp/EmailAgent/v1/send\_email",  
      "input\_schema": {  
        "type": "object",  
        "required": \["recipients", "subject", "body"\],  
        "properties": {  
          "recipients": { "type": "array", "items": { "type": "string", "format": "email" } },  
          "subject": { "type": "string" },  
          "body": { "type": "string" }  
        }  
      },  
      "auth": "None"  
    }  
  \]  
}

*  In this example, the user’s query about scheduling a meeting returned two matches: one is a CalendarAgent’s tool for creating calendar events (with a high score of 0.93), and another is an EmailAgent’s tool for sending emails (score 0.77), which might be relevant if scheduling a meeting via email is considered. Each result includes:

  * `agent`: Name of the agent service.  
  * `tool`: Name of the specific capability/tool.  
  * `description`: A description of what that tool does, from the registry.  
  * `score`: The semantic match score (0–1). In the output, scores are typically truncated to two decimal places for readability.  
  * `endpoint`: (If available) an endpoint or reference for invoking the tool. This could be a REST URL, RPC endpoint, or any internal scheme the organization uses. In the above JSON, we show hypothetical REST endpoints.  
  * `input_schema`: (If available) a JSON schema or parameters definition that describes what inputs this tool expects. This helps the AI assistant know how to format a request to this tool. In the example, `CreateEvent` requires date, time, attendees, etc.  
  * `auth`: (If available) the type of authentication needed to call this tool. E.g., "OAuth2" might indicate the assistant needs to include an OAuth2 token, whereas "None" means the tool is internal and doesn’t require additional auth, or perhaps uses the calling user’s context implicitly.  
* If no tools are found that meet a minimum relevance threshold, the `results` array may be empty. KPATH would typically also return a 204 No Content or a 200 with empty results in that case (depending on API design preferences).

* **Error Responses:** Standard HTTP error codes apply. For instance:

  * 400 Bad Request if the input JSON is invalid or required fields are missing (e.g. no query).  
  * 401 Unauthorized if the request is not properly authenticated.  
  * 500 Internal Server Error for unexpected failures (with a generic error message or code, since details should be logged internally, not exposed).

**OpenAPI Documentation:** The API is fully documented in an OpenAPI (v3) spec file. This allows integration platforms and developers to explore the endpoints and models. For example, the OpenAPI spec defines the structure of the request/response as shown above, and can be used to auto-generate clients. (As a reference, one existing semantic search API “follows OpenAPI specifications with full Swagger documentation” – KPATH does the same to ensure clarity and standardization.)

*Snippet of an OpenAPI-like definition for the /search endpoint:*

paths:  
  /search:  
    post:  
      summary: Semantic search for agent capabilities  
      requestBody:  
        required: true  
        content:  
          application/json:  
            schema:  
              type: object  
              properties:  
                query:  
                  type: string  
                  description: Natural language prompt describing the desired action.  
                user\_id:  
                  type: string  
                  description: Identifier of the requesting user (for logging/security).  
                user\_roles:  
                  type: array  
                  items: { type: string }  
                  description: List of the user's roles or groups for result filtering.  
      responses:  
        '200':  
          description: Successful lookup, returns matches.  
          content:  
            application/json:  
              schema:  
                type: object  
                properties:  
                  query:  
                    type: string  
                  results:  
                    type: array  
                    items:  
                      type: object  
                      properties:  
                        agent:       { type: string }  
                        tool:        { type: string }  
                        description: { type: string }  
                        score:       { type: number, format: float }  
                        endpoint:    { type: string }  
                        input\_schema: { type: object }   
                        auth:        { type: string }

*(This YAML is illustrative; the actual spec would include more details, e.g. components schemas, authentication requirements at the top level, etc.)*

## **Deployment Considerations**

**Architecture:** KPATH can be implemented as a stateless service (for example, a set of microservice instances behind a load balancer) that connects to the **capability registry database** (PostgreSQL or other) and to the **embedding vector index**. In a simple deployment, a single Postgres instance with pgvector could serve both roles. In a larger deployment, you might have a Postgres (for metadata) plus a separate vector DB or a distributed Postgres cluster for scale. The service itself might be developed in a suitable language (e.g. Python, Java, Node.js, Go – anything with libraries for database access and ML model inference).

* **On-Premises:** For organizations with strict data security, KPATH can be deployed within the company’s own infrastructure. The embedding model can be hosted on-prem as well (to avoid sending data to third-party APIs). This might involve running a local inference server for the model or using a smaller embedded model for real-time use. On-prem Postgres (with extensions) or an on-prem vector store (like an installed Milvus instance) would be used. The service can run in Docker/Kubernetes or on VMs managed by the enterprise. All connections would be internal, and IAM integration would tie into the company’s directory (e.g. using LDAP/Active Directory or OAuth with the on-prem IdP).

* **Cloud:** If deployed in a private cloud or as a SaaS, KPATH would reside in a secure cloud environment. The enterprise could use a managed Postgres service (with pgvector support) or a hosted vector DB service (many cloud providers or third parties offer vector DB SaaS). The embedding model might use a cloud API (like calling OpenAI’s embed API) if allowed by the enterprise, or a hosted model like Azure OpenAI or others. The service would enforce encryption in transit (HTTPS) and ideally at rest (database encryption) since it contains potentially sensitive descriptions of internal tools.

* **Hybrid:** Some enterprises may choose a hybrid approach – for instance, keep the vector database and data on-prem but use a cloud-based embedding model for convenience, or vice versa. KPATH’s design should allow for modular components (embedding generation, vector search, data storage) to be configured for either local or remote resources. For example, KPATH could be running as a cloud service but making secure calls to an on-prem database through a VPN or proxy. Alternatively, initial query embedding might be done cloud-side (if using a proprietary model) and then the vector is sent to the on-prem search index. These options come with trade-offs in latency and complexity, so KPATH’s documentation will guide administrators on these patterns.

* **Scalability:** The service should support enterprise scale: possibly thousands of tools and frequent queries. Vector search typically scales by sharding or indexing; the pgvector IVFFLAT index can handle millions of vectors by tuning the index parameters (number of clusters, probes, etc.). If using an external vector DB, those are built to scale horizontally (e.g. Milvus can distribute vectors across nodes). The stateless API layer can also be scaled out horizontally – multiple instances of the KPATH service can run behind a load balancer. Since each query is independent, scaling is straightforward. Caching can also be employed for repeated queries (though many queries will differ). If certain prompts are very common, caching their results for a short time might reduce load.

* **Monitoring and Logging:** In an enterprise setting, KPATH would integrate with monitoring systems to track performance (e.g. average query latency, vector index health) and log usage. Logs should include query metadata and which results were returned (but possibly not the full text of queries if that’s sensitive – or it should be scrubbed/anonymized). Audit logs might be required to trace who queried what capability, especially if the results involve sensitive tool names. The service should thus also allow enabling/disabling logging of query content per policy.

* **Updates and Consistency:** When the underlying registry data changes (new tools, removed tools, description updates), KPATH’s search index needs to stay consistent. For simplicity, if using Postgres, a single transaction can insert the new tool and its embedding. If using an external vector store, the service must have a process to update the vector index in tandem. Possibly, an “indexer” component or background job handles syncing new data into the vector store. The specification should define that *capability registration APIs* (outside the scope of this document) are available for adding/updating agents and tools, and that those trigger embedding recomputation.

## **Security and IAM Integration**

Enterprise deployment demands robust security measures. Aside from standard API security (authentication, encryption), KPATH’s unique aspect is controlling *who can discover what*. Not all internal tools should be exposed to every user or agent – even at the search stage – because the very existence or description of a capability might be sensitive. KPATH addresses this through integration with IAM and policy enforcement:

* **Authentication & Authorization:** Only authenticated services or users can query KPATH. Typically, an internal AI assistant service would have its own credentials to call KPATH, or it would pass along an end-user’s identity (for user-specific filtering). KPATH should validate tokens (JWTs, API keys, etc.) and determine the identity and roles of the caller. This could involve verifying a JWT’s claims or calling an introspection endpoint of the company’s IdP. If the caller is not authorized (e.g. missing a required scope or not in an allowed group to use KPATH), the request is rejected. Assuming the call is authorized, the next layer is filtering results.

* **Result Filtering by Role/Team:** Each tool in the registry can optionally carry metadata about who is allowed to use or discover it (as modeled by the `allowed_roles` field in the schema). The organization might define these access policies based on data sensitivity or team ownership of tools. For example, an “EmployeeSalaryTool” might only be visible to HR agents. KPATH enforces these by comparing the user’s roles (from the auth token or provided in the request) with the tool’s allowed list. Only matches where the intersection is non-empty (or the tool has no restrictions) are returned. Tools with no `allowed_roles` (or a designation like `allowed_roles = []` or a NULL) are assumed to be discoverable by all by default.

* **Policy Engine Integration:** In advanced scenarios, KPATH could integrate with a central policy engine (like AWS IAM policies, Google Cloud IAM, or an internal policy service). Instead of (or in addition to) static role lists on each tool, KPATH might call out to a policy decision point with the user identity and tool info to ask “Can user X discover tool Y?”. If the policy engine denies, that tool is filtered out. This dynamic approach can account for complex rules (time-based access, clearance level, etc.). However, for the functional spec, it’s sufficient to note that policy-based filtering is supported – likely by using attributes of the tool and user to decide access.

* **No Escalation of Privilege:** The filtering ensures that a user cannot even see that a certain capability exists if they aren’t supposed to. This is important because the output of KPATH could indirectly expose sensitive system functions. For instance, if there’s a tool “TerminateEmployee” available to HR, you don’t want a non-HR user to even know that capability is present by seeing it in search results. KPATH’s design effectively implements **row-level security** on search results akin to how secure search systems work (for reference, Amazon Kendra’s documentation describes how not all users should see all documents – only those they have access to, and KPATH mirrors that philosophy for tools).

* **Encryption and Data Security:** All communications with KPATH should be encrypted (HTTPS/TLS). The database should be secured and ideally encrypted at rest. Embeddings are numeric representations of text; while typically not reversible to the original text, they should still be protected as they might contain clues to the tool’s content. Role information and other metadata are also sensitive. KPATH will abide by the principle of least privilege: the service account for KPATH’s database access should only have rights to the necessary tables. If the embedding model is external (like a cloud API), additional care must be taken that no extremely sensitive text is embedded via an external call unless that’s allowed by policy.

* **Auditing:** For compliance, KPATH could log which user (or service) queried what and which results were returned. This audit trail can be reviewed to detect any inappropriate access or to support debugging (e.g. “User X didn’t see tool Y because of filter Z”). The spec can mention that auditing is configurable and can be integrated with SIEM systems.

## **Example Usage**

To illustrate how KPATH works end-to-end, consider the following scenario in an enterprise setting:

* **Scenario:** An employee’s AI assistant wants to help the employee schedule a meeting with an executive. The assistant translates the user’s request into a prompt: *“schedule a meeting with the VP next week.”* The assistant calls the KPATH `/search` API with this prompt (and includes the user’s identity or roles).

* **KPATH Processing:** The service receives the query and immediately generates an embedding for the text “schedule a meeting with the VP next week” using its embedding model. It then performs a vector similarity search in the tools database. Let’s say it finds these top 3 candidate tools (with raw cosine similarity scores):

  * **CalendarAgent – CreateEvent** (score 0.93) – because the description “Schedule a new meeting on the corporate calendar...” closely matches the idea of scheduling a meeting.  
  * **EmailAgent – SendEmail** (score 0.77) – because another way to schedule might involve sending an email, and the description “Send an email to specified recipients...” is somewhat related (though not as direct).  
  * **TravelAgent – BookTravel** (score 0.40) – because it has words like “schedule” and “next week” but it’s about travel, so semantically it’s a weak match.  
* Now, suppose the user’s roles are \["Engineering", "ExecutiveAssistant"\]. KPATH checks the allowed\_roles of each tool:

  * CreateEvent has allowed\_roles \= \[\] (meaning open to all) – passes.  
  * SendEmail has allowed\_roles \= \[\] – passes.  
  * BookTravel has allowed\_roles \= \["TravelDept"\] – the user is not in TravelDept, so this result is **filtered out**.  
* KPATH will thus prepare results for the first two tools only.

* **API Response:** The service returns a JSON response with the query echoed and a `results` list of two entries (CalendarAgent.CreateEvent and EmailAgent.SendEmail) along with their descriptions, scores, endpoints, etc. (Exactly as shown in the example response JSON in the API section above.) The BookTravel tool is omitted entirely because the user didn’t have access – from the caller’s perspective it’s as if it wasn’t a relevant match.

* **Assistant Action:** With these results, the AI assistant can decide the next step. It sees the top suggestion is CalendarAgent.CreateEvent. It knows (from the metadata) the endpoint and input schema, so it can formulate a call to that agent’s API to actually schedule the meeting. It might also use the EmailAgent.SendEmail tool if needed (perhaps to send a confirmation email). KPATH itself is not involved in those steps – it has done its job by providing the assistant with the knowledge of *what* tools to use.

* **Follow-up:** If the assistant queries something unrelated later (e.g. “send an email to all engineers”), it would call KPATH with that prompt and get a different set of matches (likely highlighting the EmailAgent.SendEmail as top). Over time, as new capabilities are added (say a “TeamsAgent – CreateTeamMeeting” tool gets added), KPATH’s results will evolve because that new tool’s embedding would make it surface for queries about scheduling meetings (possibly even outranking CalendarAgent if it’s more relevant).

This example demonstrates how KPATH enables a dynamic, natural interface to a wide array of internal tools by understanding the *meaning* of a request and linking it to the right capability. It stays within the scope of discovery, providing structured information that can be used by other components to perform the actual task.

## **Conclusion**

KPATH Enterprise is a focused solution for **semantic discovery of internal AI agent capabilities**. By maintaining a rich registry of agents and tools with embedded semantic representations, and by offering a secure, easy-to-use API, it bridges the gap between a user’s natural language request and the enterprise’s arsenal of services. This specification outlined how KPATH matches queries to tools using embeddings and vector search, the data schema backing it, the REST API contract, and considerations for deploying it in a secure, enterprise environment. With KPATH in place, organizations can empower their AI assistants to intelligently route requests to the right internal tools, all while respecting security policies and without hard-coding knowledge of each capability. The result is a more scalable and maintainable “brains” behind an AI assistant – one that can **discover** what to do, leaving the doing to the appropriate specialized agents.

