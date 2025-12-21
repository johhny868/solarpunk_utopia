# GAP-54: Metrics Collection

**Status:** Draft
**Priority:** P3 - Operations
**Effort:** 4-6 hours

## Problem

No metrics. Can't monitor performance or errors.

## Solution

Add Prometheus metrics:

```python
from prometheus_client import Counter, Histogram, generate_latest

# Define metrics
request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

exchange_count = Counter(
    'exchanges_completed_total',
    'Total exchanges completed'
)

@app.middleware("http")
async def metrics_middleware(request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start

    request_count.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()

    request_duration.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)

    return response

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

## Privacy Note

Metrics are **aggregate only**:
- Request counts/durations by endpoint
- Exchange counts (not individual values)
- Error rates

NO individual user tracking.

## Tasks

1. Add prometheus_client
2. Define key metrics
3. Add middleware
4. Expose /metrics endpoint

## Success Criteria

- [ ] Prometheus metrics exposed
- [ ] Request counts/durations tracked
- [ ] No individual user data in metrics
