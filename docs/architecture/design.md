# Architecture Design Document
**Project**: Distributed Document Search Service

## 1. High-Level Architecture
The system follows a microservices-based architecture to ensure scalability, fault tolerance, and independent deployment of components.

```mermaid
graph TD
    User[User/Client] -->|HTTPS| LB[Load Balancer]
    LB --> API[API Gateway / Service]
    
    subgraph "Application Layer"
        API -->|Read/Write| Cache[Redis Cache]
        API -->|Index| Queue[Message Queue (Simulated/Internal)]
    end

    subgraph "Data Layer"
        Queue -->|Async| Worker[Indexer Worker]
        Worker -->|Store Metadata| DB[(MongoDB)]
        Worker -->|Index Text| ES[(Elasticsearch)]
        API -->|Search| ES
    end
```

### Components
1.  **Load Balancer**: Distributes incoming traffic across API instances (e.g., Nginx or Cloud LB).
2.  **API Service (FastAPI)**: Handles REST requests, authentication, and validation.
3.  **Redis Cache**: Caches frequent search results and manages rate-limiting tokens.
4.  **Indexer Worker**: Asynchronously processes document ingestion to avoid blocking the API.
5.  **MongoDB**: Source of Truth for document metadata and tenant configurations.
6.  **Elasticsearch**: specialized search engine for full-text queries and ranking.

## 2. Data Flow

### Indexing Flow (Write)
1.  **POST /documents**: Client sends document.
2.  **Validation**: API validates tenant permissions and payload.
3.  **Persist**: Document metadata stored in **MongoDB** immediately.
4.  **Queue**: Document ID pushed to processing queue.
5.  **Index**: Worker picks up job, processes text, and indexes into **Elasticsearch**.

### Search Flow (Read)
1.  **GET /search**: Client sends query.
2.  **Cache Check**: API checks **Redis** for identical query hash.
    *   *Hit*: Return cached JSON.
3.  **Query**: If miss, API constructs Elasticsearch query with `tenant_id` filter.
4.  **Fetch**: Elasticsearch returns ranked document IDs.
5.  **Enrich**: (Optional) API fetches full metadata from MongoDB if not in ES.
6.  **Return**: Results returned to client and cached in Redis.

## 3. Database & Storage Strategy
*   **MongoDB (Primary Store)**:
    *   Stores `documents` collection with fields: `_id`, `tenant_id`, `created_at`, `raw_content`.
    *   Stores `tenants` collection.
    *   *Why*: Flexible schema, high write throughput, easy sharding.
*   **Elasticsearch (Search Engine)**:
    *   Stores searchable fields: `title`, `content` (analyzed), `tenant_id`.
    *   *Why*: Lucene-based, proven scaling for text search.
*   **Redis (Cache)**:
    *   Stores `search:{tenant_id}:{query_hash}` -> `result_json` (TTL: 5 mins).
    *   Stores `ratelimit:{tenant_id}` counters.

## 4. API Design
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/documents` | Ingest a new document. |
| `GET` | `/search?q={text}` | Search documents for the caller's tenant. |
| `GET` | `/documents/{id}` | Retrieve a specific document. |
| `DELETE` | `/documents/{id}` | Delete a document. |
| `GET` | `/health` | Service health status. |

## 5. Multi-Tenancy Strategy
*   **Logic Isolation**: "Shared Resources, Logical Separation".
*   **Implementation**:
    *   Every MongoDB document has a `tenant_id`.
    *   Every Elasticsearch document has a `tenant_id` field.
    *   **Crucial**: All search queries **MUST** include a `filter: { term: { "tenant_id": "..." } }` clause to prevent data leaks.

## 6. Consistency Model
*   **Metadata**: Strong Consistency (Read-your-writes) via MongoDB.
*   **Search**: Eventual Consistency. Elasticsearch has a "refresh interval" (default 1s).
    *   *Trade-off*: A document indexed now might take ~1s to appear in search results. This is acceptable for a search service to gain write performance.

## 7. Scalability & Resilience
*   **Horizontal Scaling**: API and Workers are stateless and can autoscale.
*   **Database Scaling**: MongoDB sharding by `tenant_id` or `_id`.
*   **Resilience**: Circuit Breakers on Elasticsearch calls to prevent cascading failures.
