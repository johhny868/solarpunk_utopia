# GAP-55: Frontend Agent List Empty

**Status:** Draft
**Priority:** P3 - Bug Fix
**Effort:** 1-2 hours

## Problem

Frontend shows empty agent list. Either API route wrong or data not loading.

## Investigation

1. Check API response:
   ```bash
   curl http://localhost:8000/api/agents
   ```

2. Check frontend fetch:
   ```typescript
   // Does this URL match the backend?
   const response = await fetch('/api/agents');
   ```

3. Check backend route:
   ```python
   @router.get("/agents")
   async def list_agents():
       # Is this returning data?
       return agents
   ```

## Likely Issues

1. **Route mismatch**: Frontend calls `/agents`, backend serves `/api/agents`
2. **Empty response**: Backend returns `[]` due to error handling
3. **CORS**: API blocked by browser
4. **Auth**: Endpoint requires auth, frontend not sending token

## Tasks

1. Debug API response
2. Check route paths match
3. Verify data exists
4. Fix whatever's broken

## Success Criteria

- [ ] Agent list renders in frontend
- [ ] API returns actual agent data
