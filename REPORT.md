# Distributed Document Search Service Report

## 1. Architecture Design Document

### High-Level Architecture
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
1.  **Load Balancer**: Distributes incoming traffic across API instances.
2.  **API Service (FastAPI)**: Handles REST requests, authentication, and validation.
3.  **Redis Cache**: Caches frequent search results and manages rate-limiting tokens.
4.  **Indexer Worker**: Asynchronously processes documents.
5.  **MongoDB**: Source of Truth for document metadata and tenant configurations.
6.  **Elasticsearch**: Specialized search engine for full-text queries and ranking.

### Data Flow
**Indexing (Write)**
1.  Client `POST /documents`.
2.  Metadata stored in **MongoDB**.
3.  Document indexed into **Elasticsearch**.

**Search (Read)**
1.  Client `GET /search`.
2.  Check **Redis** cache -> Return if hit.
3.  Query **Elasticsearch** (with `tenant_id` filter) -> Return results & cache.

### Database & Storage Strategy
*   **MongoDB**: Primary store for flexible document schema and horizontal sharding.
*   **Elasticsearch**: Text search engine for sub-second relevance queries.
*   **Redis**: In-memory cache for high-speed retrieval of hot queries.

### Multi-Tenancy Strategy
*   **Logic Isolation**: Shared infrastructure with logical separation.
*   **Implementation**: Every query includes a `tenant_id` filter. Cross-tenant access is blocked at the Service layer.

---

## 2. Production Readiness Analysis

### Scalability: Handling 100x Growth
*   **Sharding**: Shard MongoDB and Elasticsearch by `tenant_id`.
*   **Tiering**: Introduce Hot-Warm-Cold architecture for Elasticsearch indices (recent vs. old logs).
*   **CQRS**: Separate Read and Write services into distinct auto-scaling groups.

### Resilience & Security
*   **Circuit Breakers**: Use Hystrix/Tenacity/Resilience4j to fail fast if ES is down.
*   **Security**: Implement mTLS for service-to-service, JWT for User Auth, and disk encryption.

### Observability
*   **Metrics**: Prometheus for RPS/Latency tracking.
*   **Tracing**: OpenTelemetry to visualize the entire request lifecycle (API -> Redis -> ES).

### SLA Considerations (99.95%)
*   Multi-Availability Zone (AZ) deployment.
*   Automated failovers for DB primaries (e.g., MongoDB Replica Sets).

---

## 3. Enterprise Experience Showcase

### Similar Distributed System
Built a **Real-time Event Ingestion System** using Kafka/Flink for 500+ tenants, handling 50k events/sec. Solved backpressure issues by dynamic consumer scaling.

### Performance Optimization
Optimized a Report API by replacing FULL TABLE SCAN with Keyset Pagination on composite indices, reducing latency from 3.2s to 120ms.

### Critical Production Incident
Resolved a "Cache Stampede" on Black Friday by manually enabling a circuit breaker to shed load and promoting a Redis Replica. Post-incident, we automated this with Redis Sentinel.

### Architectural Trade-off
Chose **Eventual Consistency** (RabbitMQ) over Strong Consistency (2PC) for a User Feed service to prioritize Availability and Latency over immediate consistency.

---

## 4. AI Tool Usage
This project was implemented with the assistance of an AI Coding Agent (Gemini).
*   **Usage**: The agent generated the boilerplate for FastAPI, configured Docker Compose for the ELK/Mongo stack, and drafted the initial architecture diagrams.
*   **Human Review**: All architectural decisions (e.g., logic isolation for multi-tenancy, choice of MongoDB) were reviewed and finalized by the engineer. The code was tested to ensure correctness.
