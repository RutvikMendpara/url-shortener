from prometheus_client import Counter, Histogram


redirect_requests = Counter(
    "redirect_requests_total",
    "Total redirect requests"
)

cache_hits = Counter(
    "redis_cache_hits_total",
    "Redis cache hits"
)

cache_misses = Counter(
    "redis_cache_misses_total",
    "Redis cache misses"
)

url_creations = Counter(
    "url_creations_total",
    "Total short URLs created"
)

rate_limited_requests = Counter(
    "rate_limited_requests_total",
    "Total rate limited requests"
)

redirect_latency = Histogram(
    "redirect_latency_seconds",
    "Redirect latency"
)