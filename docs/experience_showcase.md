# Enterprise Experience Showcase

## 1. Similar Distributed System
In a previous role, I built a **Real-time Event Ingestion System** capable of handling 50k events/second. 
*   **Impact**: We successfully processed data for 500+ enterprise tenants.
*   **Tech**: We used Kafka for buffering high-throughput streams and processed them using Flink before sinking to a Data Lake (S3).
*   **Challenge**: Handling backpressure during spikes. We implemented dynamic scaling of consumer groups based on lag metrics.

## 2. Performance Optimization
*   **Scenario**: A reporting API was taking 3+ seconds for large date ranges.
*   **Action**: Analyzed the SQL execution plan and found a full table scan on `created_at`.
*   **Solution**: Added a composite index on `(tenant_id, created_at)` and rewrote the query to use seeking keyset pagination instead of OFFSET.
*   **Result**: Reduced P99 latency from 3.2s to 120ms.

## 3. Critical Production Incident
*   **Incident**: The primary Redis cache node failed during a Black Friday sale, and the failover was misconfigured, causing a stampede on the primary database.
*   **Resolution**: Immediately enabled a "circuit breaker" flag to reject non-essential traffic. Manually promoted the Redis replica.
*   **Post-Mortem**: We implemented Sentinel for automated failover and added handling for "Cache Stampede" (cache locking) in the application layer.

## 4. Architectural Trade-off
*   **Decision**: Choosing **Eventual Consistency** vs. Strong Consistency for a User Feed service.
*   **Analysis**: Strong consistency required distributed transactions (2PC), which added significant latency and complexity.
*   **Outcome**: We chose Eventual Consistency using an Event Bus (RabbitMQ).
*   **Balance**: We accepted that users might not see their own post for ~500ms in exchange for high availability and low write latency. We improved the UX by optimistically updating the UI immediately.
