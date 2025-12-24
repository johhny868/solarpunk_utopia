# BUG: Multiple API Endpoints Return 404 Errors

**Type:** Bug Report
**Severity:** High
**Status:** Implemented
**Date:** 2025-12-21
**Reporter:** UI Tester (Automated)
**Fixed:** 2025-12-21

## Summary

Multiple API endpoints return 404 Not Found errors, indicating either missing backend routes or incorrect proxy configuration. This breaks core functionality across many pages.

## Steps to Reproduce

1. Start the frontend on port 3004
2. Navigate to any page after login
3. Observe network requests in browser DevTools
4. Note 404 responses for various endpoints

## Expected Behavior

- API endpoints should return appropriate data or empty arrays
- Backend should be running and accessible via Vite proxy
- No 404 errors for configured endpoints

## Actual Behavior

Console shows:
```
Failed to load communities: AxiosError
Failed to load resource: the server responded with a status of 404 (Not Found)
```

Multiple API calls fail with 404 on every page load.

## Root Cause Analysis

1. **Backend may not be running:** The backend on port 8888 needs to be started
2. **Proxy misconfiguration:** `vite.config.ts` proxies may not match actual backend routes
3. **Missing endpoints:** Backend may not have implemented all required routes

Looking at `vite.config.ts:19-48`:
- `/api/vf` proxied to `http://localhost:8888`
- `/api/discovery` proxied to `http://localhost:8888`
- etc.

## Proposed Solution

1. **Verify backend is running:**
   ```bash
   # Check if backend is running on 8888
   lsof -i :8888

   # Start backend if needed
   cd valueflows_node && python -m uvicorn app.main:app --port 8888
   ```

2. **Verify proxy routes match backend:**
   - Check backend routes in `valueflows_node/app/`
   - Ensure Vite proxy rewrites match actual endpoints

3. **Add better error handling:**
   - Show user-friendly error messages instead of silent failures
   - Implement offline mode when backend unavailable

## Impact

- **Core Functionality:** Many features broken (communities, agents, etc.)
- **User Experience:** Pages appear empty or stuck loading
- **Development:** Difficult to test features without working backend

## Failed Endpoints (from test logs)

- Communities endpoint (multiple calls)
- Various other 404s

## Requirements

### SHALL

- Backend SHALL be running for frontend to function
- Frontend SHALL display meaningful error when backend unavailable
- API calls SHALL either succeed OR show user-friendly error message
- Documentation SHALL include backend startup instructions
