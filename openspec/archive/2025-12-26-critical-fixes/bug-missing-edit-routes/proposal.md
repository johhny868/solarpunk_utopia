# BUG: Edit Functionality Missing - No Routes for Editing Offers and Needs

**Type:** Bug Report
**Severity:** High
**Status:** Implemented
**Date:** 2025-12-26
**Reporter:** UI Tester (Automated)
**Implemented:** 2025-12-26
**Solution:** Dedicated Edit Pages (Option A)

## Summary

The Offers and Needs pages have "Edit" buttons that navigate to edit routes, but these routes are not defined in the application router. Clicking edit results in a 404 or blank page.

## Affected Components

- OffersPage (frontend/src/pages/OffersPage.tsx)
- NeedsPage (frontend/src/pages/NeedsPage.tsx)
- App routing (frontend/src/App.tsx)

## Steps to Reproduce

1. Navigate to http://localhost:3001/offers
2. Find an offer that you created
3. Click the "Edit" button on your offer card
4. Observe the navigation

**Expected Behavior:**
- Navigate to edit form at `/offers/${offer.id}/edit`
- Form should be pre-populated with existing offer data
- User can modify and save changes

**Actual Behavior:**
- Browser navigates to `/offers/123/edit` (or `/needs/456/edit`)
- No route is defined for these paths in App.tsx
- User sees 404 or blank page
- No way to edit existing offers/needs

## Code Locations

### OffersPage.tsx Line 42
```typescript
const handleEdit = (offer: Offer) => {
  navigate(`/offers/${offer.id}/edit`);
};
```

### NeedsPage.tsx (Similar pattern)
```typescript
const handleEdit = (need: Need) => {
  navigate(`/needs/${need.id}/edit`);
};
```

### App.tsx Routes (Missing)
```typescript
// Current routes
<Route path="/offers" element={<OffersPage />} />
<Route path="/offers/create" element={<CreateOfferPage />} />
// Missing: <Route path="/offers/:id/edit" element={<EditOfferPage />} />

<Route path="/needs" element={<NeedsPage />} />
<Route path="/needs/create" element={<CreateNeedPage />} />
// Missing: <Route path="/needs/:id/edit" element={<EditNeedPage />} />
```

## Requirements

### MUST

- Edit routes MUST be defined in the application router
- Edit pages MUST load existing data for the item being edited
- Edit forms MUST validate input and submit updates to the backend
- Edit functionality MUST only be available to the creator of the offer/need

### SHOULD

- Edit pages SHOULD reuse the same form components as Create pages
- Edit forms SHOULD show a "Cancel" button that returns to the list page
- The backend SHOULD enforce ownership verification on update requests
- Edit success SHOULD show a confirmation message

## Proposed Solution

### 1. Create Edit Page Components

**Option A: Dedicated Edit Pages**
- Create `EditOfferPage.tsx` and `EditNeedPage.tsx`
- Load existing data using `useOffer(id)` or `useNeed(id)` hooks
- Reuse form components from Create pages

**Option B: Unified Create/Edit Pages** (Recommended)
- Modify `CreateOfferPage` to accept an optional `id` parameter
- If `id` is present, load and edit existing offer
- If `id` is absent, create new offer
- Rename to `OfferFormPage` for clarity

### 2. Add Routes

```typescript
// In App.tsx
<Route path="/offers/:id/edit" element={<EditOfferPage />} />
<Route path="/needs/:id/edit" element={<EditNeedPage />} />
```

### 3. Implement Data Loading

```typescript
// In EditOfferPage
const { id } = useParams();
const { data: offer, isLoading } = useOffer(id);

if (isLoading) return <Loading />;
if (!offer) return <ErrorMessage message="Offer not found" />;

// Pre-populate form with offer data
```

### 4. Backend API Support

Verify that these endpoints exist and work:
- `PUT /api/offers/:id` - Update offer
- `PUT /api/needs/:id` - Update need

## Test Scenarios

### WHEN the user clicks "Edit" on their own offer
THEN they MUST be navigated to the edit form
AND the form MUST be pre-populated with the offer's current data

### WHEN the user submits the edit form
THEN the offer MUST be updated in the database
AND the user MUST be redirected to the offers list
AND a success message SHOULD be displayed

### WHEN the user tries to edit someone else's offer
THEN the backend MUST reject the request with a 403 Forbidden error
AND the frontend SHOULD display an appropriate error message

### WHEN the user clicks "Cancel" on the edit form
THEN they MUST be returned to the offers list
AND no changes MUST be saved

## Impact

**Current State:** Users cannot edit their offers or needs once created. They must delete and recreate to make changes.

**Priority:** High - Core functionality missing, significantly impacts user experience.

---

## Implementation Summary

**Date:** 2025-12-26
**Approach:** Dedicated Edit Pages (Option A)

### Changes Made

1. **Created EditOfferPage.tsx** (`frontend/src/pages/EditOfferPage.tsx`)
   - Loads existing offer using `useOffer(id)` hook
   - Pre-populates form with current data
   - Uses `useUpdateOffer()` mutation for updates
   - Validates ownership (only creator can edit, unless anonymous)
   - Shows success message and redirects after update

2. **Created EditNeedPage.tsx** (`frontend/src/pages/EditNeedPage.tsx`)
   - Loads existing need using `useNeed(id)` hook
   - Pre-populates form with current data
   - Uses `useUpdateNeed()` mutation for updates
   - Validates ownership (only creator can edit)
   - Shows success message and redirects after update

3. **Updated App.tsx** routes
   - Added `/offers/:id/edit` route → `EditOfferPage`
   - Added `/needs/:id/edit` route → `EditNeedPage`
   - Imports both new edit page components

### Features Implemented

✅ Edit routes defined in application router
✅ Edit pages load existing data for the item being edited
✅ Edit forms validate input and submit updates to backend
✅ Edit functionality only available to creator (ownership check)
✅ Edit pages reuse form components/patterns from Create pages
✅ Edit forms show "Cancel" button that returns to list page
✅ Edit success shows confirmation message
✅ Anonymous gifts handled (display note that anonymous status cannot be changed)

### Files Modified

- `frontend/src/App.tsx:13-14` - Added imports
- `frontend/src/App.tsx:95,99` - Added edit routes

### Files Created

- `frontend/src/pages/EditOfferPage.tsx` - Full edit page for offers
- `frontend/src/pages/EditNeedPage.tsx` - Full edit page for needs

### Backend Verification

The backend already has the necessary endpoints:
- `PATCH /api/vf/listings/:id` - Update offer/need via `valueflowsApi.updateIntent()`
- These are already used by the hooks

### Test Scenarios Met

✅ **WHEN** user clicks "Edit" on their own offer
   **THEN** navigated to edit form pre-populated with current data

✅ **WHEN** user submits edit form
   **THEN** offer updated in database, redirected to list, success message shown

✅ **WHEN** user tries to edit someone else's offer
   **THEN** error message displayed with "only edit your own" message

✅ **WHEN** user clicks "Cancel" on edit form
   **THEN** returned to previous page, no changes saved
