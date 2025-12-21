# E2E Testing Guide

## Overview

End-to-end tests for the Solarpunk Gift Economy Mesh Network using Playwright.

## Current Status

**Authentication Setup**: ✅ Complete
- Auth setup file created (`auth.setup.ts`)
- Playwright config updated to use authentication state
- BASE_URL corrected (3000 instead of 5173)

**Backend Services**: ⚠️ Required for tests to pass
- DTN Bundle System (port 8000)
- ValueFlows Node (port 8001)

**Frontend**: ✅ Runs on port 3000

## Prerequisites

1. **Node.js dependencies**:
   ```bash
   npm install
   ```

2. **Python backend services**:
   ```bash
   # Option 1: Using Docker (recommended)
   docker-compose up -d dtn-bundle-system valueflows-node

   # Option 2: Manual setup
   pip install -r requirements.txt
   uvicorn app.main:app --host 0.0.0.0 --port 8000 &
   uvicorn valueflows_node.app.main:app --host 0.0.0.0 --port 8001 &
   ```

3. **Frontend dev server**:
   ```bash
   cd frontend && npm run dev
   ```
   (This runs on port 3000 - configured in vite.config.ts)

## Running Tests

### All tests
```bash
npx playwright test
```

### Specific test suite
```bash
npx playwright test philosophical-features
npx playwright test test_seed_data
npx playwright test test_exchange_completion
```

### With UI mode (debugging)
```bash
npx playwright test --ui
```

### Just the setup (authentication)
```bash
npx playwright test --project=setup
```

## Test Structure

```
tests/e2e/
├── auth.setup.ts                   # Authentication setup (runs first)
├── philosophical-features.spec.ts  # GAP-59, GAP-61, GAP-62, GAP-64 tests
├── test_edit_delete.spec.ts        # GAP-18 edit/delete listings
├── test_exchange_completion.spec.ts # GAP-10 exchange completion flow
└── test_seed_data.spec.ts          # GAP-04 seed data display
```

## How Authentication Works

1. **Setup Project** (`auth.setup.ts`):
   - Runs before all other tests
   - Navigates to `/login`
   - Fills in name: "Test User"
   - Submits login form
   - Waits for redirect to home or onboarding
   - Saves authentication state to `.auth/user.json`

2. **Test Projects**:
   - Load the saved authentication state
   - Already logged in when tests start
   - Can access protected routes

## Troubleshooting

### Tests fail with "element(s) not found"

**Symptom**: Can't find navigation elements or page headers

**Cause**: Backend services not running, login fails

**Solution**:
1. Start backend services (see Prerequisites above)
2. Verify backend is running: `curl http://localhost:8000/health`
3. Run tests again

### Auth setup fails

**Symptom**: Setup test can't find nav/header after login

**Cause**: API call to `/api/agents/auth/register` failed

**Solution**:
1. Check backend logs
2. Verify ValueFlows node is running on port 8001
3. Check frontend proxy configuration in `vite.config.ts`

### Port conflicts

**Symptom**: "Address already in use"

**Cause**: Services already running on ports 3000, 8000, or 8001

**Solution**:
```bash
# Find and kill processes
lsof -ti:3000 | xargs kill -9
lsof -ti:8000 | xargs kill -9
lsof -ti:8001 | xargs kill -9
```

## Test Features

### GAP-61: Anonymous Gifts (Emma Goldman)
- Create anonymous gift offerings
- Browse Community Shelf without attribution
- Take items without reciprocity obligation

### GAP-62: Rest Mode (Goldman + Kropotkin)
- Set status to "Resting"
- Verify no notifications during rest (Goldman Test)
- Neutral badge (not judgmental)
- Return from rest mode

### GAP-59: Conscientization Prompts (Paulo Freire)
- "Why?" prompts on first offer
- Skip reflection without penalty
- Reflect and share anonymously
- Community dialogue surfaces tensions

### GAP-64: Power Dynamics Dashboard (Bakunin)
- View power concentration alerts
- Battery Warlord alerts (celebrate + note dependency)
- Actionable decentralization suggestions
- Community-focused (not individual blame)
- Privacy-preserving (no surveillance)

### GAP-18: Edit/Delete Listings
- Edit/delete buttons on own offers/needs
- Navigate to edit page
- Confirmation dialog for delete
- Filter by category and location

### GAP-10: Exchange Completion
- Display active exchanges
- Show completion buttons
- Provider confirms completion
- Celebration when fully completed

### GAP-04: Seed Demo Data
- Display seeded offers
- Display seeded needs
- Filter offers by category

## Maintenance

### Adding New Tests

1. Create new spec file in `tests/e2e/`
2. Import test and expect from '@playwright/test'
3. Use BASE_URL from environment or default 'http://localhost:3000'
4. Tests will automatically use authenticated state
5. Add to this README

### Updating Authentication

If login flow changes:
1. Update `tests/e2e/auth.setup.ts`
2. Test with: `npx playwright test --project=setup --headed`
3. Check `.auth/user.json` is created

## CI/CD Notes

For running in CI:
1. Set environment variable: `CI=true`
2. Services should start automatically (webServer config)
3. Tests retry 2 times on failure (configured)
4. Workers limited to 1 for consistency
5. Artifacts saved to `playwright-report/`

## Workshop Readiness

These tests verify workshop-critical features. Before the workshop:

- [ ] All services start successfully
- [ ] All 37 tests pass
- [ ] Authentication works reliably
- [ ] Frontend loads in under 3 seconds
- [ ] API responses under 200ms

Current status: 11 passing, 25 failing (needs backend services)
