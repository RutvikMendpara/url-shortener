# System Architecture

This document describes the architecture and internal design of the URL Shortener service.

The goal of this system is to demonstrate common backend engineering patterns such as caching, background processing, rate limiting, and containerized services.

---

# High Level Architecture

The application is composed of several services running in separate containers.

```
Client
   |
   v
FastAPI API
   |
   |------ Redis (cache + rate limiting + job queue)
   |
   |------ PostgreSQL (persistent storage)


RQ Worker (analytics processing) -> Redis (job queue) -> PostgreSQL (update click counts)
Prometheus -> collects metrics
Grafana -> visualizes metrics
```

Each component has a specific responsibility to keep the system simple and modular.

---

# Components

## API Service

The API service is implemented using **FastAPI** and is responsible for:

- handling HTTP requests
- creating short URLs
- redirecting users
- pushing analytics events to the job queue
- exposing application metrics

The API is designed to keep the **redirect path extremely lightweight**, minimizing latency for users accessing short links.

---

## PostgreSQL

PostgreSQL acts as the **primary persistent storage**.

The database stores:

- original URLs
- generated short codes
- creation timestamps
- expiration timestamps
- click counts

Schema:

```
urls

id           BIGSERIAL PRIMARY KEY
short_code   VARCHAR(10) UNIQUE
original_url TEXT
created_at   TIMESTAMP
expires_at   TIMESTAMP NULL
click_count  INTEGER
```

The primary lookup query used by the redirect endpoint:

```
SELECT original_url
FROM urls
WHERE short_code = ?
```

An index on `short_code` ensures fast lookups.

---

## Redis

Redis is used for three independent responsibilities.

### 1. Redirect Cache

Redis stores cached mappings of:

```
short_code -> original_url
```

This prevents the system from querying the database on every redirect.

Typical flow:

```
request
-> redis lookup
-> cache hit -> redirect
-> cache miss -> database query -> cache result
```

Caching significantly reduces database load under heavy traffic.

---

### 2. Rate Limiting

To prevent abuse of the URL creation endpoint, the service implements simple rate limiting.

Example rule:

```
10 URL creations per minute per IP
```

Implementation uses Redis atomic counters with expiration.

Example key format:

```
rate_limit:{ip}
```

Redis automatically expires these keys after the defined time window.

---

### 3. Job Queue

Redis also acts as the backend for **RQ (Redis Queue)**.

When a redirect occurs, the API enqueues an analytics event instead of writing directly to the database.

```
redirect request
-> enqueue job
-> worker processes job
```

This prevents database writes from slowing down redirect responses.

---

## Background Worker

Analytics jobs are processed by a dedicated worker container running **RQ**.

Worker responsibilities:

- consume analytics jobs
- update click counts
- process background tasks

Worker command:

```
rq worker analytics
```

Decoupling analytics from the API allows the redirect endpoint to remain fast even during high traffic.

---

# Request Flows

## URL Creation Flow

```
Client
   |
POST /url/shorten
   |
Rate limit check (Redis)
   |
Insert row into PostgreSQL
   |
Generate Base62 short code
   |
Return shortened URL
```

Short codes are generated using **Base62 encoding of the database ID**.

Advantages:

- deterministic
- no collisions
- constant-time generation

---

## Redirect Flow (Hot Path)

The redirect endpoint is the most performance-sensitive part of the system.

```
Client
   |
GET /url/{short_code}
   |
Redis cache lookup
   |
Cache hit -> Enqueue analytics job -> HTTP redirect response
   |
Cache miss -> PostgreSQL lookup
   |
Cache result in Redis
   |
Enqueue analytics job
   |
HTTP redirect response
```

The goal is to keep this path as short as possible.

---

# Asynchronous Analytics

Every redirect generates an analytics event.

Instead of performing a database write during the redirect request:

```
redirect
-> enqueue job
-> worker processes event
-> update click_count
```

Benefits:

- faster response time
- reduced database contention
- better scalability under high traffic

---

# Observability

The system includes a minimal observability stack.

## Metrics

The API exposes metrics at:

```
/metrics
```

Prometheus scrapes this endpoint periodically.

Example metrics collected:

```
redirect_requests_total
redis_cache_hits_total
redis_cache_misses_total
url_creations_total
rate_limited_requests_total
redirect_latency_seconds
```

These metrics help monitor traffic volume, cache efficiency, and latency.

---

## Logging

The API uses structured logs to capture important system events such as:

- URL creation
- redirect requests
- rate limit violations
- cache hits and misses

Logs help diagnose issues during development and debugging.

---

# Container Architecture

The system is deployed locally using Docker Compose.

Services:

```
url_shortener_api
url_shortener_worker
url_shortener_postgres
url_shortener_redis
url_shortener_prometheus
url_shortener_grafana
```

Each service runs in an isolated container connected through a shared Docker network.

This setup simulates a small production-style distributed system.

---

# Design Considerations

Several design decisions were made to keep the system simple while still demonstrating common backend patterns.

### Cache First Redirects

Using Redis for redirect caching dramatically reduces database reads.

### Asynchronous Analytics

Redirect latency should not depend on database writes.

Moving analytics to background workers keeps the hot path fast.

### Deterministic Short Codes

Base62 encoding of the database ID avoids collision handling and simplifies generation.

### Containerized Services

Running each component in a container makes the system easier to run locally and closer to real deployment setups.

---

# Limitations

This project focuses on demonstrating architecture patterns rather than building a fully production-ready service.

Limitations include:

- single database instance
- single Redis instance
- no horizontal scaling
- minimal authentication
- limited analytics capabilities

These would normally be addressed in a larger production deployment.

---

# Possible Improvements

Potential extensions include:

```
custom short codes
link expiration enforcement
authentication
API keys for rate limiting
load testing
horizontal scaling
distributed workers
```

These improvements would move the system closer to a fully production-grade service.
