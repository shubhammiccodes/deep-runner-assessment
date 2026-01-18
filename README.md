# Distributed Document Search Service

## Overview
A prototype of a distributed document search service designed to handle 10+ million documents with sub-second response times, demonstrating enterprise-grade architectural patterns.

## Stage 1: Requirement Analysis & Tech Stack Selection

### 1. Requirements Analysis
*   **Scale**: 10M+ documents, multi-tenant architecture.
*   **Performance**: <500ms p95 latency, 1000+ RPS.
*   **Features**: Full-text search, relevance ranking, tenant isolation, secure access.
*   **Deliverables**: Architecture doc, working prototype, production readiness analysis.

### 2. Technology Stack Selection
*   **Language/Framework**: Python 3.11+ with **FastAPI**.
    *   *Why*: High performance (asyncio), easy documentation (OpenAPI), great ecosystem for backend services.
*   **Search Engine**: **Elasticsearch** (v8.x).
    *   *Why*: Industry standard for distributed search, supports complex queries, horizontal scaling, and fuzzy matching.
*   **Database**: **MongoDB**.
    *   *Why*: Flexible document schema fits the "document search" domain perfectly; easy horizontal scaling (sharding) for millions of records.
*   **Caching**: **Redis**.
    *   *Why*: Low-latency in-memory store for result caching and rate-limiting buckets.
*   **Containerization**: **Docker** & **Docker Compose**.
    *   *Why*: Consistent development and deployment environments.

### 3. High-Level Data Model
*   **Tenant**: `id` (UUID), `api_key` (String), `name` (String), `rate_limit_tier` (Enum).
*   **Document**: `id` (UUID), `tenant_id` (UUID), `title` (String), `content` (Text), `created_at` (Timestamp).

## Documentation
*   [Architecture Design](docs/architecture/design.md): High-level diagrams, data flow, and multi-tenancy strategy.
*   [Production Readiness](docs/production_readiness.md): Scalability to 100x growth, security, and observability.
*   [Experience Showcase](docs/experience_showcase.md): Examples of past distributed systems work and incident resolution.

## Getting Started

### Prerequisites
*   Docker & Docker Compose
*   Python 3.11+

### Installation
1.  **Clone the repository**:
    ```bash
    git clone https://github.com/shubhammiccodes/deep-runner-assessment.git
    cd deep-runner-assessment
    ```

2.  **Start Infrastructure**:
    ```bash
    docker-compose up -d
    ```
    Wait for Elasticsearch to become healthy (~30s).

3.  **Install Dependencies**:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate  # Windows
    # source venv/bin/activate # Linux/Mac
    pip install -r requirements.txt
    ```

4.  **Run the API**:
    ```bash
    uvicorn app.main:app --reload
    ```
    Access Swagger UI at: `http://localhost:8000/docs`

### Testing
Run the integration test script to verify the end-to-end flow:
```bash
python scripts/test_integration.py
```
This script will:
1. Ingest a document.
2. Wait for indexing.
3. Perform a search (Cache Miss).
4. Perform the same search (Cache Hit).
5. Clean up.
