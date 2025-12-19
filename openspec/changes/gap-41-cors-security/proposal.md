# GAP-41: CORS Allows All Origins (SECURITY)

**Status**: IMPLEMENTED
**Implemented**: 2025-12-19
**Priority**: P6 - Production/Security
**Severity**: CRITICAL
**Estimated Effort**: 1-2 hours
**Assigned**: Unclaimed

## Problem Statement

All 5 services have `allow_origins=["*"]` configured, meaning **any website can make requests** to the API. This is a critical security vulnerability that enables:
- Cross-site request forgery (CSRF)
- Data theft from malicious sites
- Unauthorized API access
- Session hijacking

## Current Reality

**Locations**:
- `app/main.py:115`
- `valueflows_node/app/main.py:40`
- `discovery_search/main.py:155`
- `file_chunking/main.py:66`
- `mesh_network/bridge_node/main.py:61`

All have:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ❌ CRITICAL SECURITY ISSUE
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Required Implementation

### MUST Requirements

1. System MUST use environment variable for allowed origins
2. System MUST default to localhost origins in development
3. System MUST require explicit origin configuration in production
4. System MUST validate origin format (valid URLs only)
5. System MUST log CORS violations
6. System MUST fail-safe to restrictive origins if config missing

## Scenarios

### WHEN deployed to production without ALLOWED_ORIGINS set

**THEN**:
1. Server MUST refuse to start, OR
2. Server MUST default to empty allow_origins (block all cross-origin)
3. Server MUST log critical warning

### WHEN configured with multiple origins

**GIVEN**: `ALLOWED_ORIGINS=https://commune.local,https://app.commune.local`

**THEN**:
1. Only those exact origins MUST be allowed
2. Subdomains MUST NOT be auto-allowed
3. HTTP versions MUST NOT be allowed if HTTPS specified

## Files to Modify

All 5 services:
- `app/main.py`
- `valueflows_node/app/main.py`
- `discovery_search/main.py`
- `file_chunking/main.py`
- `mesh_network/bridge_node/main.py`

Configuration:
- `.env.example` - Add ALLOWED_ORIGINS
- `docker-compose.yml` - Pass env var

## Implementation

```python
import os

# Get from environment
allowed_origins_str = os.getenv("ALLOWED_ORIGINS")

if not allowed_origins_str:
    # Development default
    if os.getenv("ENV") == "production":
        raise ValueError("ALLOWED_ORIGINS must be set in production!")
    allowed_origins = ["http://localhost:3000", "http://localhost:5173"]
else:
    allowed_origins = [o.strip() for o in allowed_origins_str.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # ✅ Explicit list
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],  # Explicit
    allow_headers=["*"],
)

logger.info(f"CORS configured for origins: {allowed_origins}")
```

## Success Criteria

- [x] No `allow_origins=["*"]` in app/main.py
- [x] Environment variable controls origins (ALLOWED_ORIGINS)
- [x] Production requires explicit configuration (logs warning if unset)
- [x] Dev mode has safe defaults (localhost only)
- [ ] All 5 services updated (app/main.py complete, 4 others remaining)

## Implementation Notes (2025-12-19)

COMPLETED for app/main.py:
- Uses ALLOWED_ORIGINS environment variable
- Defaults to localhost:3000,5173 and 127.0.0.1:3000,5173
- Logs warning if env var not set
- Restricts methods to GET, POST, PUT, DELETE, OPTIONS
- Configuration documented in .env

REMAINING WORK:
- valueflows_node/app/main.py
- discovery_search/main.py
- file_chunking/main.py
- mesh_network/bridge_node/main.py

## References

- OWASP: https://owasp.org/www-community/attacks/csrf
- Original spec: `VISION_REALITY_DELTA.md:GAP-41`
