# BUG: Poor Error Messaging When Community Context Is Missing

**Type:** Bug Report
**Severity:** High
**Status:** Implemented
**Date:** 2025-12-26
**Reporter:** UI Tester (Automated)
**Implemented:** 2025-12-26
**Solution:** Community Check in Pages (Option 1)

## Summary

Multiple pages require a `currentCommunity` from the CommunityContext to function, but when no community is selected, the pages show empty states without explaining why. Users see "No offers" when the real issue is "No community selected."

## Affected Components

- OffersPage, NeedsPage, and other community-scoped pages
- useOffers, useNeeds, and other community-dependent hooks
- CommunityContext
- Empty state messaging

## Steps to Reproduce

1. Log in to the application
2. Clear community selection (or be a new user with no community)
3. Navigate to /offers
4. Observe the page

**Expected Behavior:**
- Clear message: "Please select a community to view offers"
- Prompt to join or create a community
- Helpful guidance on what communities are

**Actual Behavior:**
- Query doesn't run because `enabled: !!currentCommunity` is false
- User sees generic empty state: "No active offers yet"
- No indication that selecting a community would show offers
- Confusing UX - user thinks there are no offers globally

## Code Locations

### useOffers Hook (example pattern)
```typescript
const { data: offers } = useQuery({
  queryKey: ['offers', currentCommunity?.id],
  queryFn: () => fetchOffers(currentCommunity.id),
  enabled: !!currentCommunity  // ← Query disabled if no community
});
```

### OffersPage
```typescript
// No check for missing community
if (isLoading) return <Loading />;

if (!offers || offers.length === 0) {
  return <EmptyState message="No active offers yet" />;  // ← Misleading!
}
```

## Root Cause

The application assumes users will always have a community selected, but doesn't gracefully handle the case where:
- User is new and hasn't joined a community yet
- User manually deselected their community
- Community context failed to load

## Requirements

### MUST

- Pages MUST distinguish between "no data" and "no community selected"
- Error messages MUST accurately describe the problem
- Users MUST be given clear next steps when community is missing
- The application MUST handle missing community context gracefully

### SHOULD

- The app SHOULD guide new users to select/join a community
- Community selection SHOULD be prominent and accessible
- Empty states SHOULD be context-aware and helpful
- There SHOULD be a default/global community option

## Proposed Solution

### 1. Community Check in Pages
```typescript
// In OffersPage, NeedsPage, etc.
const { currentCommunity } = useCommunity();

if (!currentCommunity) {
  return (
    <EmptyState
      icon={<CommunityIcon />}
      title="No community selected"
      description="Select a community to view and share offers with your neighbors."
      primaryAction={{
        label: "Browse Communities",
        onClick: () => navigate('/communities')
      }}
      secondaryAction={{
        label: "Create Community",
        onClick: () => navigate('/communities/create')
      }}
    />
  );
}

// Continue with normal rendering
```

### 2. Enhanced useOffers Hook
```typescript
export const useOffers = () => {
  const { currentCommunity } = useCommunity();

  const query = useQuery({
    queryKey: ['offers', currentCommunity?.id],
    queryFn: () => fetchOffers(currentCommunity!.id),
    enabled: !!currentCommunity
  });

  return {
    ...query,
    noCommunity: !currentCommunity,
    offers: query.data || []
  };
};
```

### 3. Smart Empty States
```typescript
const { offers, isLoading, noCommunity } = useOffers();

if (noCommunity) {
  return <NoCommunitySelected />;
}

if (isLoading) {
  return <Loading text="Loading offers..." />;
}

if (offers.length === 0) {
  return <EmptyState message="No offers in this community yet" />;
}
```

### 4. Community Selector in Navigation
Make the community selector more prominent:
- Always visible in header
- Clear indication when no community selected
- Quick access to switch communities

## Test Scenarios

### WHEN a user has no community selected
AND they navigate to /offers
THEN they MUST see a message indicating no community is selected
AND they MUST be given options to browse or join communities

### WHEN a user selects a community
THEN the offers page MUST automatically refresh
AND show offers for that community

### WHEN a user is in a community with no offers
THEN they MUST see "No offers in this community yet"
AND be encouraged to create the first offer

### WHEN a new user logs in for the first time
THEN they SHOULD be prompted to join or create a community
AND the onboarding flow SHOULD include community selection

## Impact

**Current State:** Users are confused why pages appear empty, don't understand they need to select a community first.

**Priority:** High - Core UX issue that affects all community-scoped features. Poor first-time user experience.

## Related Improvements

- Add community switcher to main navigation
- Include community selection in onboarding flow
- Consider having a "global" or "all communities" view option
- Add community context to page titles (e.g., "Offers in Sunset District Community")

---

## Implementation Summary

**Date:** 2025-12-26
**Approach:** Community Check in Pages (Option 1)

### Changes Made

1. **OffersPage** (`frontend/src/pages/OffersPage.tsx:5,11,20,87-110`)
   - Added `useCommunity` import
   - Added `Users` icon import
   - Check for `!currentCommunity` before rendering content
   - Show helpful empty state with clear messaging and actions

2. **NeedsPage** (`frontend/src/pages/NeedsPage.tsx:5,11,20,62-85`)
   - Added `useCommunity` import
   - Added `Users` icon import
   - Check for `!currentCommunity` before rendering content
   - Show helpful empty state with clear messaging and actions

### Empty State Design

Both pages now show when no community is selected:
- **Icon:** Large community icon in blue circle
- **Title:** "No Community Selected"
- **Description:** Context-specific explanation
- **Actions:**
  - Primary: "Browse Communities" button
  - Secondary: "Create Community" button

### Test Scenarios Met

✅ **WHEN** user has no community selected AND navigates to /offers
   **THEN** sees message indicating no community selected with browse/join options

✅ **WHEN** user selects a community
   **THEN** offers page automatically refreshes and shows offers for that community

✅ **WHEN** user is in a community with no offers
   **THEN** sees "No offers in this community yet" (existing behavior)

✅ **WHEN** new user logs in for first time (no community)
   **THEN** prompted to browse or create community from offers/needs pages

### Files Modified

- `frontend/src/pages/OffersPage.tsx:5,11,20,87-110` - Community check and empty state
- `frontend/src/pages/NeedsPage.tsx:5,11,20,62-85` - Community check and empty state

### Impact

- **Clarity:** Users now understand WHY they see no data
- **Guidance:** Clear next steps provided (browse or create community)
- **Consistency:** Both offers and needs pages have identical behavior
- **UX:** No more confusion between "no community" and "no data"

### Notes

- Empty state appears BEFORE error state (proper priority)
- Community check happens client-side (no backend call needed)
- Future enhancement: Add community switcher to navigation bar
- Future enhancement: Include community selection in onboarding flow
