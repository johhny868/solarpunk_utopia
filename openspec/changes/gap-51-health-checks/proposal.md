# GAP-51: Health Checks

**Status:** Draft
**Priority:** P2 - Operations
**Effort:** 2-3 hours

## Problem

Health endpoint returns 200 without verifying dependencies.

## Solution

Check all critical dependencies:

```python
@router.get("/health")
async def health_check():
    checks = {
        "database": await check_db(),
        "vf_service": await check_vf_api(),
        "cache": await check_cache()
    }
    all_healthy = all(checks.values())
    status = 200 if all_healthy else 503
    return JSONResponse(checks, status_code=status)

async def check_db() -> bool:
    try:
        await db.execute("SELECT 1")
        return True
    except Exception:
        return False

async def check_vf_api() -> bool:
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{VF_URL}/health", timeout=5)
            return r.status_code == 200
    except Exception:
        return False
```

## Tasks

1. Add dependency health checks
2. Return 503 if any dependency unhealthy
3. Add /ready endpoint (for k8s)
4. Add /live endpoint (for k8s)

## Success Criteria

- [ ] Health checks verify DB
- [ ] Health checks verify external services
- [ ] Returns 503 when unhealthy
