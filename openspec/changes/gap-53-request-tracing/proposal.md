# GAP-53: Request Tracing

**Status:** Draft
**Priority:** P3 - Operations
**Effort:** 4-6 hours

## Problem

No correlation IDs. Can't trace requests across services/logs.

## Solution

Add correlation ID middleware:

```python
import uuid

@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    # Use incoming ID or generate new one
    correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())

    # Attach to request state
    request.state.correlation_id = correlation_id

    # Add to structlog context
    structlog.contextvars.bind_contextvars(correlation_id=correlation_id)

    # Process request
    response = await call_next(request)

    # Add to response headers
    response.headers["X-Correlation-ID"] = correlation_id

    return response
```

All logs automatically include correlation_id:
```json
{"event": "proposal_created", "correlation_id": "abc-123", ...}
```

## Tasks

1. Add correlation ID middleware
2. Integrate with structlog
3. Forward ID to downstream services
4. Add to error responses

## Success Criteria

- [ ] All requests have correlation ID
- [ ] ID appears in all logs
- [ ] ID forwarded to VF service
- [ ] ID in error responses
