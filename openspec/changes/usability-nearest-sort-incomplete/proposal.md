# USABILITY: "Nearest" Sort Option Not Implemented

**Type:** Usability Report
**Severity:** Medium
**Status:** Identified
**Date:** 2025-12-26
**Reporter:** UI Tester (Automated)

## Summary

The OffersPage has a "Nearest (coming soon)" sort option in the dropdown, but selecting it silently falls back to "newest" sort without any user feedback. This is confusing - users might think the sort is working when it's not.

## Affected Components

- OffersPage (frontend/src/pages/OffersPage.tsx) - Lines 78-79
- NeedsPage (likely similar pattern)

## Current Behavior

**User Actions:**
1. Navigate to /offers
2. Click "Sort By" dropdown
3. Select "Nearest (coming soon)"

**Actual Behavior:**
- Option appears in dropdown as selectable
- Selecting it sets sortBy state to "nearest"
- Code silently falls back to "newest" sort
- No feedback to user that feature isn't available
- User might think offers are sorted by distance when they're not

## Code Location

### OffersPage.tsx Lines 78-79
```typescript
// Sort offers
const sortedOffers = React.useMemo(() => {
  if (sortBy === 'nearest') {
    // TODO: implement geolocation-based sorting
    return offers; // Falls back to unsorted/newest
  }
  // ... other sort options
}, [offers, sortBy]);
```

## Problems

1. **No User Feedback**: Selecting "Nearest" gives no indication it doesn't work
2. **Misleading UI**: Option looks functional but isn't
3. **Poor UX**: User may make decisions based on incorrect sort order
4. **Inconsistent State**: UI shows "Nearest" selected but results aren't sorted that way

## Requirements

### MUST

- If a feature is not implemented, it MUST NOT appear as a selectable option
- OR it MUST be clearly disabled with explanation
- Users MUST NOT be misled about how data is sorted

### SHOULD

- Coming soon features SHOULD be visually distinct (grayed out, disabled)
- There SHOULD be a tooltip explaining when the feature will be available
- The application SHOULD gracefully handle unimplemented features

## Proposed Solutions

### Option 1: Disable the Option (Recommended for Now)
```typescript
<option value="nearest" disabled>
  Nearest (location-based sorting coming soon)
</option>
```

**Pros:**
- Honest about current state
- No user confusion
- Simple to implement

**Cons:**
- Feature still not available

### Option 2: Show Notification When Selected
```typescript
const handleSortChange = (newSort: string) => {
  if (newSort === 'nearest') {
    toast.info('Location-based sorting is coming soon! Showing newest offers for now.');
    setSortBy('newest');
  } else {
    setSortBy(newSort);
  }
};
```

**Pros:**
- User gets clear feedback
- Explains the limitation
- Sets correct expectations

### Option 3: Implement the Feature
```typescript
const sortedOffers = React.useMemo(() => {
  if (sortBy === 'nearest' && userLocation) {
    return [...offers].sort((a, b) => {
      const distA = calculateDistance(userLocation, a.location);
      const distB = calculateDistance(userLocation, b.location);
      return distA - distB;
    });
  }
  // ...
}, [offers, sortBy, userLocation]);
```

**Requirements for implementation:**
- Request user's geolocation permission
- Store location with each offer
- Calculate distances client-side or server-side
- Handle missing location data gracefully

### Option 4: Remove the Option Entirely
Remove "Nearest" from the UI until ready to implement.

**Pros:**
- Cleanest UX
- No confusion or disabled states

**Cons:**
- Doesn't signal upcoming feature

## Recommendations

**Short-term (Immediate):**
- Disable the "Nearest" option with clear label
- Add tooltip: "We're working on location-based sorting! Expected in Q1 2026."

**Medium-term (Next Sprint):**
- Implement geolocation-based sorting
- Request location permission on first use
- Add privacy notice about location data

**Implementation considerations for location sorting:**
1. Privacy: Make location sharing opt-in, explain how data is used
2. Accuracy: Use approximate location (city/neighborhood level) for privacy
3. Fallback: Handle users who deny location permission
4. Performance: Calculate distances efficiently for large lists
5. Caching: Store calculated distances to avoid re-computation

## Test Scenarios

### WHEN a user selects "Nearest (coming soon)"
THEN they MUST receive clear feedback that the feature isn't available yet
OR the option MUST be disabled and unselectable

### WHEN "Nearest" is disabled
THEN hovering/clicking SHOULD show a tooltip explaining when it will be available

### WHEN location sorting is implemented
THEN users MUST be asked for location permission
AND they MUST be able to deny permission and still use the app

### WHEN a user has location permission enabled
THEN offers MUST be sorted by actual distance from user
AND distance SHOULD be displayed on each offer card

## Impact

**Current State:** Users may be confused or make incorrect assumptions about offer ordering.

**Priority:** Medium - Not breaking functionality, but misleading UX should be fixed.

## Related Enhancements

Once location features are implemented, consider:
- Showing distance on offer cards ("2.3 miles away")
- Map view of offers
- Radius filter ("Show offers within 5 miles")
- Location-based notifications ("New offer near you!")
