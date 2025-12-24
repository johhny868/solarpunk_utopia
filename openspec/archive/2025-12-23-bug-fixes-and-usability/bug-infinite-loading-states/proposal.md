# BUG: Pages Stuck in Infinite Loading State

**Type:** Bug Report
**Severity:** Medium
**Status:** Implemented
**Date:** 2025-12-21
**Reporter:** UI Tester (Automated)
**Fixed:** 2025-12-21 (Fixed agents API path to use /api/vf/agents)

## Summary

Several pages show a loading spinner and "Loading..." message indefinitely, never resolving to show content or an error message. This leaves users confused about whether the page is working.

## Affected Pages

1. **Steward Dashboard** (`/steward`) - Shows "Loading..." forever
2. **AI Agents** (`/agents`) - Shows "Loading AI agents..." forever
3. Potentially others when backend is unavailable

## Steps to Reproduce

1. Login to the application
2. Navigate to `/steward` or `/agents`
3. Observe loading indicator
4. Wait - loading never completes

## Expected Behavior

- Loading state should resolve within reasonable time (5-10 seconds max)
- If data unavailable, show "No data" or error message
- Loading timeout should trigger fallback UI

## Actual Behavior

- Loading spinner spins forever
- No timeout mechanism
- User left wondering if app is broken
- No way to recover without manually navigating away

## Evidence

Screenshots:
- `test-results/12-agents-page.png` - Shows loading state with spinner
- `test-results/17-steward-dashboard.png` - Shows "Loading..." text

## Root Cause Analysis

1. **API calls failing silently:** 404 errors from backend not handled
2. **No loading timeout:** React Query or fetch calls have no timeout
3. **Missing error boundaries:** Errors don't bubble up to UI

## Proposed Solution

### 1. Add query timeouts to React Query config

```typescript
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60000,
      retry: 1,
      // Add timeout
      networkMode: 'offlineFirst',
    },
  },
});
```

### 2. Handle loading timeout in components

```typescript
const { data, isLoading, isError } = useQuery({
  queryKey: ['agents'],
  queryFn: fetchAgents,
  // Add retry and error handling
  retry: 2,
  retryDelay: 1000,
});

// Show error after timeout
if (isLoading && !data) {
  return <LoadingWithTimeout timeout={10000} fallback={<EmptyState />} />;
}
```

### 3. Add error states to all data-fetching pages

```typescript
if (isError) {
  return <ErrorMessage message="Failed to load data. Please try again." />;
}
```

## Impact

- **User Experience:** Users think app is broken
- **Retention:** Users abandon pages that never load
- **Support:** Increased support requests about "stuck" pages

## Requirements

### SHALL

- Loading states SHALL timeout after 10 seconds maximum
- Failed data fetches SHALL show error message to user
- Users SHALL be able to retry failed requests
- Empty states SHALL be shown when no data available
