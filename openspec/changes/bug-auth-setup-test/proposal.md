# BUG: E2E Auth Setup Test Fails Due to Button Text Mismatch

**Type:** Bug Report (Test Infrastructure)
**Severity:** Medium
**Status:** Implemented
**Date:** 2025-12-21
**Reporter:** UI Tester (Automated)
**Fixed:** 2025-12-21 (Added data-testid attributes to onboarding buttons)

## Summary

The Playwright auth setup test (`tests/e2e/auth.setup.ts`) fails because:
1. Button text doesn't match expected patterns
2. Onboarding flow doesn't have a skip option
3. Test expects `nav` or `header` but onboarding page has neither

## Steps to Reproduce

```bash
npx playwright test --project=setup
```

## Expected Behavior

- Auth setup should complete successfully
- Authenticated state should be saved for other tests
- All E2E tests should run

## Actual Behavior

```
Error: expect(locator).toBeVisible() failed
Locator: locator('nav, header')
Expected: visible
Timeout: 5000ms
Error: element(s) not found
```

Test gets stuck on onboarding page and can't find navigation.

## Root Cause Analysis

In `auth.setup.ts:33-43`:
```typescript
const skipButton = page.locator('button:has-text("Skip")');
const continueButton = page.locator('button:has-text("Continue")');
const getStartedButton = page.locator('button:has-text("Get Started")');
```

But actual button texts are:
- "Let's Get Started →" (WelcomeStep)
- "I'm Ready to Share →" (GiftEconomyStep)
- "Enter the Network →" (CompletionStep)

The `has-text` partial matching should work, but the special characters may cause issues.

## Proposed Solution

### Option A: Update test to match actual buttons

```typescript
const buttonPatterns = [
  /Let's Get Started/i,
  /I'm Ready to Share/i,
  /Skip/i,
  /Continue/i,
  /Enter the Network/i,
  /Finish/i,
];

for (const pattern of buttonPatterns) {
  const btn = page.locator('button').filter({ hasText: pattern }).first();
  if (await btn.isVisible({ timeout: 500 }).catch(() => false)) {
    await btn.click();
    await page.waitForTimeout(300);
  }
}
```

### Option B: Add data-testid attributes to onboarding buttons

```tsx
<button data-testid="onboarding-next" onClick={onNext}>
  Let's Get Started →
</button>
```

Then in test:
```typescript
await page.locator('[data-testid="onboarding-next"]').click();
```

### Option C: Add skip onboarding mechanism

Add localStorage flag check that skips onboarding:
```typescript
localStorage.setItem('onboarding_completed', 'true');
```

## Impact

- **CI/CD:** All E2E tests fail because auth setup fails
- **Development:** Can't run automated tests
- **Quality:** No automated regression testing

## Requirements

### SHALL

- Auth setup test SHALL complete successfully
- Test SHALL handle all onboarding button variations
- Test SHALL work regardless of onboarding state
- Tests SHOULD use data-testid for reliable element selection
