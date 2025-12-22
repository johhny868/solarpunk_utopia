# BUG: SQLite/Capacitor Fails to Initialize in Web Browser

**Type:** Bug Report
**Severity:** High
**Status:** Implemented
**Date:** 2025-12-21
**Reporter:** UI Tester (Automated)
**Fixed:** 2025-12-21 (Added platform check to skip SQLite on web)

## Summary

Every page load triggers a console error: "The jeep-sqlite element is not present in the DOM!" This indicates the Capacitor SQLite plugin for web is not properly initialized, breaking offline-first functionality.

## Steps to Reproduce

1. Open the application in any web browser
2. Open browser developer console
3. Navigate to any page
4. Observe console errors

## Expected Behavior

- SQLite should initialize properly for web platform
- OR gracefully fall back to remote API without errors
- No console errors should appear during normal operation

## Actual Behavior

```
Failed to initialize database: Error: The jeep-sqlite element is not present in the DOM!
Please check the @capacitor-community/sqlite documentation for instructions regarding the web platform.
    at CapacitorSQLiteWeb.ensureJeepSqliteIsAvailable
```

This error appears on EVERY page navigation.

## Root Cause Analysis

The `@capacitor-community/sqlite` plugin requires a `<jeep-sqlite>` web component in the DOM for web platform support. This component is not being added to `index.html`.

Looking at:
- `frontend/src/storage/sqlite.ts:210` - `LocalDatabase.initialize()`
- `frontend/src/api/adaptive-valueflows.ts:100` - Initialization call

## Proposed Solution

### Option A: Add jeep-sqlite web component (for full web SQLite support)

1. Add to `index.html`:
```html
<script type="module" src="https://unpkg.com/jeep-sqlite/dist/jeep-sqlite/jeep-sqlite.esm.js"></script>
<jeep-sqlite></jeep-sqlite>
```

2. Or install and configure properly:
```bash
npm install jeep-sqlite
```

### Option B: Disable SQLite on web platform (recommended for now)

1. Detect web platform early and skip SQLite initialization
2. Use remote API only for web browsers
3. Reserve SQLite for Capacitor native builds (Android/iOS)

```typescript
// In adaptive-valueflows.ts
if (Capacitor.getPlatform() === 'web') {
  // Skip local API, use remote only
  return;
}
```

## Impact

- **Console Noise:** Error logs on every page (confusing during development)
- **Performance:** Wasted initialization attempts
- **User Experience:** No direct impact if fallback works, but indicates incomplete setup

## Requirements

### SHALL

- Application SHALL NOT log errors during normal operation
- SQLite initialization SHALL either succeed OR be gracefully skipped on web
- Web platform SHALL work with remote API when SQLite unavailable
