# Testing Guide: Philosophical Features

This guide explains how to run tests for the philosophical features (GAP-59, GAP-61, GAP-62, GAP-64).

---

## Test Overview

### Backend Tests (Python + pytest)

Location: `/test_bakunin_analytics.py`

**What it tests**:
- ✅ Battery Warlord detection (resource concentration ≥30%)
- ✅ Skill Gatekeeper detection (monopolies on critical skills)
- ✅ API response format correctness
- ✅ Risk level assessment (LOW/MEDIUM/HIGH/CRITICAL)
- ✅ Dependency counting

**Run command**:
```bash
pytest test_bakunin_analytics.py -v
```

**Expected output**:
```
test_detect_battery_warlord PASSED
test_detect_skill_gatekeeper PASSED
test_api_response_format PASSED

✓ All Bakunin Analytics tests passed!
"Where there is authority, there is no freedom." - Mikhail Bakunin
```

---

### Frontend E2E Tests (Playwright)

Location: `/tests/e2e/philosophical-features.spec.ts`

**What it tests**:

#### GAP-61: Anonymous Gifts
- ✅ Creating anonymous offerings
- ✅ Browsing Community Shelf without attribution
- ✅ Taking gifts without reciprocity obligation

#### GAP-62: Rest Mode
- ✅ Setting status to Resting
- ✅ NO notifications sent when resting (Goldman Test)
- ✅ Neutral badge presentation (no guilt-trips)
- ✅ Returning from rest mode

#### GAP-59: Conscientization Prompts
- ✅ "Why?" prompts trigger appropriately
- ✅ Skip button is prominent (no coercion)
- ✅ Reflections can be shared anonymously
- ✅ Dialogue space surfaces tensions, not just celebrations

#### GAP-64: Power Dynamics
- ✅ Viewing concentration alerts
- ✅ Alerts celebrate contribution while noting dependency
- ✅ Actionable decentralization suggestions
- ✅ No individual surveillance or ranking

#### Goldman Test Enforcement
- ✅ NO engagement metrics anywhere
- ✅ NO guilt-trip language
- ✅ NO gamification or points
- ✅ All prompts have prominent Skip/Dismiss

---

## Running the Tests

### Prerequisites

1. **Backend running**:
   ```bash
   cd valueflows_node
   source venv/bin/activate
   python -m app.main
   ```
   Should be running on `http://localhost:8001`

2. **Frontend running**:
   ```bash
   cd frontend
   npm run dev
   ```
   Should be running on `http://localhost:5173`

3. **Playwright installed**:
   ```bash
   npx playwright install
   ```

---

### Run Backend Tests

```bash
# From project root
pytest test_bakunin_analytics.py -v
```

**What success looks like**:
```
✓ Battery warlord detection working!
✓ Skill gatekeeper detection working!
✓ API response format correct!
```

---

### Run Frontend E2E Tests

```bash
# From project root
npx playwright test philosophical-features.spec.ts
```

**Options**:
```bash
# Run with UI (see browser)
npx playwright test philosophical-features.spec.ts --headed

# Run specific test
npx playwright test philosophical-features.spec.ts -g "Anonymous Gifts"

# Debug mode
npx playwright test philosophical-features.spec.ts --debug

# Generate test report
npx playwright test philosophical-features.spec.ts --reporter=html
```

**What success looks like**:
```
✓ User can create an anonymous gift offering
✓ User can browse Community Shelf without attribution
✓ User can set status to Resting
✓ Resting user receives NO notifications (Goldman Test)
✓ First-time offer triggers "Why?" prompt
✓ User can skip reflection without penalty
✓ User can view power concentration alerts
✓ Power alert provides actionable suggestions
✓ No engagement metrics or gamification anywhere
```

---

## Test Coverage Summary

| Feature | Backend Tests | E2E Tests | Status |
|---------|---------------|-----------|--------|
| GAP-59: Conscientization | N/A | ✅ 4 tests | Complete |
| GAP-61: Anonymous Gifts | N/A | ✅ 3 tests | Complete |
| GAP-62: Rest Mode | N/A | ✅ 4 tests | Complete |
| GAP-64: Power Dynamics | ✅ 3 tests | ✅ 5 tests | Complete |
| Goldman Test Enforcement | N/A | ✅ 2 tests | Complete |

**Total**: 3 backend tests + 18 E2E tests = **21 tests**

---

## Writing New Tests

### Adding a Backend Test

```python
def test_new_power_detection(test_db):
    """Test description"""
    # Setup: Create test data
    cursor = test_db.cursor()
    # ... insert agents, resources, etc.

    # Execute: Run detection
    service = BakuninAnalyticsService(db_path)
    alerts = service.detect_battery_warlords()

    # Assert: Verify results
    assert len(alerts) > 0
    assert alerts[0].risk_level == 'critical'
```

### Adding a Frontend E2E Test

```typescript
test('User can do X without Y', async ({ page }) => {
  // Navigate
  await page.goto(`${BASE_URL}/feature`);

  // Interact
  await page.click('button:has-text("Action")');

  // Assert
  await expect(page.locator('.result')).toContainText('Expected');

  // Goldman Test: Verify NO forbidden pattern
  await expect(page.locator('body')).not.toContainText('guilt-trip');
});
```

---

## Common Test Failures

### "Page not found" errors
**Cause**: Frontend not running or wrong URL
**Fix**: Check `http://localhost:5173` is accessible

### "Database locked" in backend tests
**Cause**: Previous test didn't clean up
**Fix**: Tests use `:memory:` database, should not happen. If it does, restart test runner.

### "Element not found" in E2E tests
**Cause**: Frontend UI changed or feature not implemented yet
**Fix**: Update test selectors or implement the feature

### "Goldman Test violation" detected
**Cause**: UI has guilt-trip language, engagement metrics, or coercive elements
**Fix**: **This is serious** - remove the violating feature immediately. Goldman Test failures should block deployment.

---

## Goldman Test Checklist

Before merging any UI changes, verify:

- [ ] **No engagement metrics**: No streaks, points, levels, badges
- [ ] **No guilt-trips**: No "haven't posted", "falling behind", "should"
- [ ] **No coercion**: All prompts have prominent Skip/Dismiss
- [ ] **No surveillance**: No individual contribution tracking, rankings, leaderboards
- [ ] **No productivity pressure**: Rest mode users get ZERO notifications
- [ ] **No reciprocity obligation**: Anonymous gifts don't create "thank" or "owe" UI

**If any checkbox fails**: Do NOT merge. Fix the violation first.

---

## Continuous Integration

### Recommended CI Pipeline

```yaml
# .github/workflows/test.yml
name: Test Philosophical Features

on: [push, pull_request]

jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run backend tests
        run: pytest test_bakunin_analytics.py -v

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install Playwright
        run: npx playwright install --with-deps
      - name: Start services
        run: |
          docker-compose up -d
          sleep 10  # Wait for services to start
      - name: Run E2E tests
        run: npx playwright test philosophical-features.spec.ts
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v2
        with:
          name: playwright-report
          path: playwright-report/
```

---

## Test Data Setup

### For Backend Tests

Tests use in-memory SQLite with minimal schema. No external setup needed.

### For Frontend E2E Tests

Tests expect:
1. **Running backend API** on port 8001
2. **Running frontend** on port 5173
3. **Test data** seeded (optional, tests can create their own)

**Seed test data** (optional):
```bash
python scripts/seed_test_data.py
```

This creates:
- 10 agents (including some in rest mode)
- 15 critical resource specs (batteries, bike repair, water filters, etc.)
- 30 listings (some anonymous, some concentrated)
- 50 completed exchanges

---

## Debugging Failed Tests

### Backend Tests

```bash
# Run with verbose output
pytest test_bakunin_analytics.py -v -s

# Run specific test
pytest test_bakunin_analytics.py::test_detect_battery_warlord -v

# Drop into debugger on failure
pytest test_bakunin_analytics.py --pdb
```

### Frontend E2E Tests

```bash
# Run with browser visible
npx playwright test --headed

# Run in debug mode (pause before each action)
npx playwright test --debug

# Record test (generate test code by clicking in browser)
npx playwright codegen http://localhost:5173
```

### Check API is responding

```bash
# Test power dynamics endpoint
curl http://localhost:8001/vf/power-dynamics | jq

# Expected: JSON with resource_concentration, skill_gatekeepers arrays
```

---

## Performance Benchmarks

### Backend Tests
- Expected runtime: **< 2 seconds**
- Database operations: In-memory (fast)

### Frontend E2E Tests
- Expected runtime: **< 2 minutes** for full suite
- Each test: **< 10 seconds**

If tests are slower, investigate:
- Network latency
- Database not using indexes
- Frontend rendering performance

---

## Future Test Coverage

### Planned Tests

- [ ] **API integration tests** (backend + frontend contract testing)
- [ ] **Load testing** (100 agents, 1000 listings, does detection still work?)
- [ ] **Accessibility testing** (screen reader compatibility)
- [ ] **Mobile responsiveness** (philosophical features on small screens)
- [ ] **Internationalization** (Goldman Test phrases in other languages)

---

## Resources

- **Playwright Docs**: https://playwright.dev
- **pytest Docs**: https://docs.pytest.org
- **Goldman Test Definition**: `docs/GAP62_NOTIFICATION_DESIGN_GUIDE.md`
- **Philosophy References**: `docs/PHILOSOPHICAL_SPECS_COMPLETE.md`

---

**Remember**: Tests aren't just for catching bugs—they're for enforcing philosophical principles. A failing Goldman Test should be treated as seriously as a security vulnerability.

*"Where there is authority, there is no freedom."* - Mikhail Bakunin
