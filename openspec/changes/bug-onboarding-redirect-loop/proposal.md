# BUG: Potential Onboarding Redirect Loop

**Type:** Bug Report
**Severity:** High
**Status:** Identified
**Date:** 2025-12-26
**Reporter:** UI Tester (Automated)

## Summary

The HomePage checks if onboarding is completed and redirects to `/onboarding` if not. However, there's a risk of redirect loops if the onboarding page doesn't properly set the completion flag or has its own authentication/redirect logic.

## Affected Components

- HomePage (frontend/src/pages/HomePage.tsx)
- OnboardingPage (frontend/src/pages/OnboardingPage.tsx)
- ProtectedRoute component
- localStorage onboarding_completed flag

## Steps to Reproduce

1. Create a new account and log in
2. Observe navigation behavior
3. Check for redirect loops in browser

**Expected Behavior:**
- New user logs in → redirected to /onboarding
- User completes onboarding → flag set in localStorage
- User redirected to home page
- No further redirects

**Actual Behavior (Potential):**
- If onboarding doesn't set the flag properly, infinite redirect loop
- If onboarding page also checks auth and redirects, possible loop
- If localStorage is cleared, user sent to onboarding again unexpectedly

## Code Locations

### HomePage.tsx Lines 22-27
```typescript
useEffect(() => {
  const hasCompletedOnboarding = localStorage.getItem('onboarding_completed');

  if (!hasCompletedOnboarding) {
    navigate('/onboarding');
  }
}, [navigate]);
```

### Concerns

1. **Missing Completion Logic**: Need to verify OnboardingPage properly sets `localStorage.setItem('onboarding_completed', 'true')`
2. **No Redirect Protection**: HomePage doesn't check if already on onboarding route
3. **localStorage Fragility**: If localStorage is cleared or unavailable, user sent to onboarding repeatedly
4. **No Backend Sync**: Onboarding status not stored in user profile, only in localStorage

## Requirements

### MUST

- The onboarding completion flag MUST be reliably set when onboarding is complete
- The redirect logic MUST prevent infinite loops
- The onboarding status SHOULD be stored in the user's profile on the backend
- The application MUST handle localStorage being unavailable or cleared

### SHOULD

- Onboarding status SHOULD be checked from the backend on login
- The HomePage SHOULD not redirect if the user is already completing onboarding
- There SHOULD be a way for users to reset/redo onboarding if desired

## Proposed Solution

### 1. Backend Storage
```typescript
// Add to user profile
interface User {
  id: string;
  name: string;
  onboarding_completed: boolean;  // ← Store on backend
  onboarding_completed_at?: Date;
}
```

### 2. Improved HomePage Logic
```typescript
useEffect(() => {
  // Don't redirect if already on onboarding page
  if (location.pathname === '/onboarding') return;

  // Check backend first, fall back to localStorage
  const hasCompletedOnboarding =
    user?.onboarding_completed ||
    localStorage.getItem('onboarding_completed') === 'true';

  if (!hasCompletedOnboarding) {
    navigate('/onboarding', { replace: true });
  }
}, [navigate, location.pathname, user]);
```

### 3. OnboardingPage Completion
```typescript
// In OnboardingPage final step
const handleComplete = async () => {
  try {
    // Update backend
    await updateUser({ onboarding_completed: true });

    // Update localStorage as backup
    localStorage.setItem('onboarding_completed', 'true');

    // Navigate to home
    navigate('/', { replace: true });
  } catch (error) {
    console.error('Failed to complete onboarding:', error);
  }
};
```

### 4. Add Backend Endpoint
```python
# In user API
@router.patch("/users/me")
async def update_current_user(
    update: UserUpdate,
    current_user: User = Depends(get_current_user)
):
    # Update user including onboarding_completed flag
    ...
```

## Test Scenarios

### WHEN a new user completes onboarding
THEN the onboarding_completed flag MUST be set to true in the backend
AND the flag MUST also be set in localStorage
AND the user MUST be redirected to the home page

### WHEN a user with completed onboarding navigates to home
THEN they MUST NOT be redirected back to onboarding
AND they MUST see the normal home page content

### WHEN a user's localStorage is cleared but backend shows onboarding complete
THEN the user MUST NOT be sent through onboarding again
AND the localStorage flag SHOULD be restored from backend data

### WHEN a user manually navigates to /onboarding after completing it
THEN they SHOULD be allowed to view it (for reference)
OR they SHOULD be redirected to home with a message

## Impact

**Current State:** Uncertain - may work fine, or may create frustrating redirect loops for users.

**Priority:** High - Could completely block new users from accessing the application if redirect loop occurs.

## Additional Investigation Needed

1. Review OnboardingPage.tsx to verify completion logic
2. Test with new user account to confirm flow works
3. Test with localStorage disabled/cleared
4. Verify backend user model includes onboarding tracking
