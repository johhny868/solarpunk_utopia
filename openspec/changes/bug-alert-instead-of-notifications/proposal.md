# BUG: Using Browser alert() Instead of In-App Notifications

**Type:** Bug Report
**Severity:** Medium
**Status:** Identified
**Date:** 2025-12-26
**Reporter:** UI Tester (Automated)

## Summary

Several pages use the browser's native `alert()` function for error messages instead of the application's notification system. This creates an inconsistent and jarring user experience, especially since an ErrorMessage component already exists in the codebase.

## Affected Components

- OffersPage (frontend/src/pages/OffersPage.tsx) - Lines 48-51
- NeedsPage (likely similar pattern)
- Potentially other pages with delete/error handling

## Steps to Reproduce

1. Navigate to /offers
2. Try to delete an offer (when backend fails or returns error)
3. Observe the error notification

**Expected Behavior:**
- Error displayed in-app using toast notification or inline ErrorMessage component
- Consistent with other error handling in the application
- Modern, polished UX

**Actual Behavior:**
- Browser alert() dialog appears
- Blocks entire page until dismissed
- Looks unprofessional and breaks immersion
- Inconsistent with ErrorMessage component used elsewhere

## Code Location

### OffersPage.tsx Lines 48-51
```typescript
const handleDelete = async (offerId: string) => {
  try {
    await deleteOffer(offerId);
  } catch (error) {
    alert('Failed to delete offer. Please try again.');  // ← Browser alert!
  }
};
```

### Existing ErrorMessage Component
The codebase already has `frontend/src/components/ErrorMessage.tsx` which should be used instead.

## Requirements

### MUST

- Error messages MUST use in-app notification system, not browser alerts
- Error handling MUST be consistent across all pages
- Critical errors MUST be displayed prominently but non-blocking

### SHOULD

- The application SHOULD use a toast notification library for temporary messages
- Success messages SHOULD also use the same notification system
- Notifications SHOULD be dismissible
- Notifications SHOULD auto-dismiss after a reasonable time

## Proposed Solution

### Option 1: Toast Notification Library (Recommended)
Install and use a toast library like `react-hot-toast` or `sonner`:

```typescript
import toast from 'react-hot-toast';

const handleDelete = async (offerId: string) => {
  try {
    await deleteOffer(offerId);
    toast.success('Offer deleted successfully');
  } catch (error) {
    toast.error('Failed to delete offer. Please try again.');
  }
};
```

### Option 2: Inline Error State
Use local state to show errors inline:

```typescript
const [deleteError, setDeleteError] = useState<string | null>(null);

const handleDelete = async (offerId: string) => {
  setDeleteError(null);
  try {
    await deleteOffer(offerId);
  } catch (error) {
    setDeleteError('Failed to delete offer. Please try again.');
  }
};

// In render:
{deleteError && <ErrorMessage message={deleteError} />}
```

### Option 3: Custom Notification Context
Create a NotificationContext provider:

```typescript
// NotificationContext.tsx
export const useNotification = () => {
  const context = useContext(NotificationContext);
  return {
    showError: (message: string) => { /* ... */ },
    showSuccess: (message: string) => { /* ... */ },
    showInfo: (message: string) => { /* ... */ }
  };
};

// Usage
const { showError, showSuccess } = useNotification();

const handleDelete = async (offerId: string) => {
  try {
    await deleteOffer(offerId);
    showSuccess('Offer deleted successfully');
  } catch (error) {
    showError('Failed to delete offer. Please try again.');
  }
};
```

## Implementation Steps

1. Choose and install a toast notification library (recommend `sonner` for modern UX)
2. Set up toast provider in App.tsx
3. Find all instances of `alert()` in codebase
4. Replace with appropriate toast calls
5. Add success messages where appropriate
6. Update error handling documentation

## Test Scenarios

### WHEN a delete operation fails
THEN the user MUST see an in-app error notification
AND the notification MUST not block the page
AND the notification SHOULD auto-dismiss after 5 seconds

### WHEN a delete operation succeeds
THEN the user SHOULD see a success notification
AND the offer MUST be removed from the list

### WHEN multiple errors occur in sequence
THEN each SHOULD be displayed
AND they SHOULD queue or stack appropriately

## Impact

**Current State:** Browser alerts create unprofessional, jarring experience and are inconsistent with the rest of the application.

**Priority:** Medium - Not blocking functionality, but significantly impacts polish and user experience.

## Code Search Needed

Search codebase for all instances of:
- `alert(`
- `window.alert(`
- `confirm(`
- `prompt(`

Replace all with appropriate in-app alternatives.
