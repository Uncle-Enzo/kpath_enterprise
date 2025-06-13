# KPATH Enterprise Service Data Model & Search Embeddings

## Service Data Model

### Core Service Table (`services`)
The main service entity stores the following fields:

| Field | Type | Description | Used in Embeddings |
|-------|------|-------------|-------------------|
| **id** | Integer | Primary key | No |
| **name** | String | Unique service name | **Yes (3x weight)** |
| **description** | Text | Service description | **Yes** |
| **endpoint** | Text | API endpoint URL | No |
| **version** | String | Service version | No |
| **status** | String | active/inactive/deprecated | No (filter only) |
| **created_at** | DateTime | Creation timestamp | No |
| **updated_at** | DateTime | Last update timestamp | No |

### Related Tables

#### ServiceCapability (`service_capability`)
Stores the capabilities/functions of each service:

| Field | Type | Description | Used in Embeddings |
|-------|------|-------------|-------------------|
| **id** | Integer | Primary key | No |
| **service_id** | Integer | Foreign key to services | No |
| **capability_desc** | Text | Capability description | **Yes** |
| **capability_name** | String | Capability name | No |
| **input_schema** | JSON | Input parameters schema | No |
| **output_schema** | JSON | Output format schema | No |
| **created_at** | DateTime | Creation timestamp | No |

#### ServiceIndustry (`service_industry`)
Classifies services by business domain:

| Field | Type | Description | Used in Embeddings |
|-------|------|-------------|-------------------|
| **id** | Integer | Primary key | No |
| **service_id** | Integer | Foreign key to services | No |
| **domain** | String | Business domain (e.g., Finance, Marketing) | **Yes** |

#### InteractionCapability (`interaction_capability`)
Defines how services can be interacted with:

| Field | Type | Description | Used in Embeddings |
|-------|------|-------------|-------------------|
| **id** | Integer | Primary key | No |
| **service_id** | Integer | Foreign key to services | No |
| **interaction_desc** | Text | Interaction description | No |
| **interaction_type** | String | sync/async/stream/batch | No |

### Other Related Tables (Not Used in Embeddings)
- **AccessPolicy**: Access control policies
- **ServiceVersion**: Version history
- **ServiceHealth**: Health monitoring data

## Embedding Generation Process

### Fields Used for Search Embeddings

The embedding generation combines the following fields into a single text representation:

1. **Service Name** (weighted 3x)
   - Repeated 3 times to give higher importance
   - Example: "CustomerDataAPI CustomerDataAPI CustomerDataAPI"

2. **Service Description**
   - Full description text
   - Example: "Core API for accessing and managing customer master data"

3. **Capabilities** (from ServiceCapability table)
   - All capability_desc values concatenated
   - Example: "Retrieve customer profile Update customer information Search customers"

4. **Domains** (from ServiceIndustry table)
   - All domain values concatenated
   - Example: "Customer Service Data Management Analytics"

5. **Tags** (if present)
   - Currently not implemented in the database schema
   - Handled gracefully with empty list

### Embedding Text Construction

```python
# Pseudo-code of embedding text generation
text_parts = []

# Add name with 3x weight
text_parts.extend([service.name] * 3)

# Add description
text_parts.append(service.description)

# Add all capabilities
for capability in service.capabilities:
    text_parts.append(capability.capability_desc)

# Add all domains
for industry in service.industries:
    text_parts.append(industry.domain)

# Combine all parts
combined_text = ' '.join(text_parts)
```

### Example Embedding Text

For the **CustomerDataAPI** service:
```
CustomerDataAPI CustomerDataAPI CustomerDataAPI Core API for accessing and managing customer master data, profiles, and preferences across the enterprise Retrieve customer profile and data by ID or email Update customer information and preferences Search customers by various criteria Get customer analytics and insights Customer Service Data Management Analytics
```

## Search Process

1. **Query Processing**: User query is converted to a 384-dimensional embedding
2. **Similarity Calculation**: Cosine similarity between query embedding and all service embeddings
3. **Ranking**: Services ranked by similarity score
4. **Filtering**: Optional post-search filtering by domain or capability

## Key Insights

- **Name gets 3x weight**: Service names are most important for discovery
- **Description and capabilities are equally weighted**: Both contribute to understanding what the service does
- **Domains help with categorization**: Used both in embeddings and post-search filtering
- **Technical details excluded**: Endpoint URLs, versions, schemas are not searchable
- **Status used for filtering only**: Only 'active' services are indexed

This design ensures that searches focus on:
- What the service is called (name)
- What it does (description & capabilities)
- What business area it serves (domains)
