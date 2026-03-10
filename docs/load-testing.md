# Load Testing Results

Load testing was performed using **k6** to evaluate the performance of the redirect endpoint and the URL creation endpoint.

Tests were executed locally against the Docker-based deployment.

Detailed raw results are available in:

- [Redirect Endpoint Test Results](../load-test/results/redirect_test_results.json)
- [URL Creation Endpoint Test Results](../load-test/results/create_url_test_results.json)

---

# Redirect Endpoint Test

**Endpoint**

```
GET /url/{short_code}
```

**Test Configuration**

- Virtual Users: 50
- Duration: 30 seconds
- Redirect following disabled (to measure API latency only)

**Results**

| Metric          | Value    |
| --------------- | -------- |
| Total Requests  | 1500     |
| Requests/sec    | ~49.4    |
| Average Latency | 9.39 ms  |
| Median Latency  | 3.97 ms  |
| P90 Latency     | 24.39 ms |
| P95 Latency     | 41.56 ms |
| Max Latency     | 110.9 ms |
| Error Rate      | 0%       |

**Observations**

- Median latency is under **4 ms**, indicating most redirects are served from **Redis cache**.
- Higher percentiles represent occasional **database lookups on cache misses**.
- No request failures were observed.

---

# URL Creation Endpoint Test

**Endpoint**

```
POST /url/shorten
```

**Test Configuration**

- Virtual Users: 1
- Total Requests: 12
- Rate limit: **10 requests per minute per IP**

This test intentionally exceeds the rate limit to verify correct behavior.

**Results**

| Metric                | Value    |
| --------------------- | -------- |
| Total Requests        | 12       |
| Successful Creations  | 10       |
| Rate Limited Requests | 2        |
| Average Latency       | 15.23 ms |
| Median Latency        | 14.03 ms |
| P90 Latency           | 19.45 ms |
| P95 Latency           | 26.17 ms |
| Max Latency           | 34.38 ms |

**Observations**

- The first 10 requests succeeded.
- Requests beyond the configured limit returned **HTTP 429 (Too Many Requests)** as expected.
- Average latency remained under **20 ms**, indicating efficient request handling.

---

## Running Load Tests

Install k6 and run the tests:

```
k6 run load-test/redirect_test.js
k6 run load-test/create_url_test.js
```

---

# Summary

The load tests demonstrate:

- Fast redirect performance due to **Redis caching**
- Stable request latency under concurrent load
- Correct enforcement of **rate limiting**
- No request failures during redirect testing

These results confirm that the system handles typical traffic patterns efficiently while protecting the API from abuse.
