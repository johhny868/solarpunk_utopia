# USABILITY: Date Input Fields Need Better UX

**Type:** Usability Report
**Severity:** Medium
**Status:** Identified
**Date:** 2025-12-26
**Reporter:** UI Tester (Automated)

## Summary

The availability date fields in CreateOfferPage and CreateNeedPage use native HTML5 date inputs, which have poor and inconsistent UX across browsers and devices. There's also no validation to ensure "Available From" comes before "Available Until."

## Affected Components

- CreateOfferPage (frontend/src/pages/CreateOfferPage.tsx) - Lines 271-287
- CreateNeedPage (likely similar pattern)
- Any form with date/time inputs

## Current Implementation

```typescript
<input
  type="date"
  value={formData.available_from || ''}
  onChange={(e) => setFormData({...formData, available_from: e.target.value})}
/>

<input
  type="date"
  value={formData.available_until || ''}
  onChange={(e) => setFormData({...formData, available_until: e.target.value})}
/>
```

## Problems

### 1. Inconsistent Browser Experience
- **Chrome/Edge**: Custom calendar picker
- **Firefox**: Different calendar style
- **Safari**: Native iOS picker on mobile, different desktop picker
- **Mobile browsers**: Varying native pickers
- No consistent styling or branding

### 2. No Date Validation
```typescript
// No check for this:
if (available_from > available_until) {
  // Invalid! But not caught
}
```

Users can select:
- "Available Until" before "Available From"
- Dates in the past
- Dates years in the future

### 3. No User-Friendly Presets
Common needs like:
- "Available today"
- "Next 7 days"
- "Next 30 days"
- "Indefinite"

All require manual date selection.

### 4. No Clear Affordances
- Not obvious these fields are optional vs required
- No placeholder text showing date format
- No help text explaining what these dates mean

### 5. Mobile UX Issues
- Native mobile date pickers vary widely
- Some are hard to use for selecting distant dates
- Keyboard input often disabled

## Requirements

### MUST

- Date inputs MUST prevent invalid date ranges (from > until)
- The UI MUST provide clear feedback about date validation errors
- Dates MUST be displayed in user's local format

### SHOULD

- Date pickers SHOULD have consistent styling across browsers
- The UI SHOULD offer common preset options
- The UI SHOULD show a visual calendar for date selection
- Validation SHOULD happen in real-time, not just on submit

### MAY

- The UI MAY offer relative date presets ("1 week from now")
- Advanced users MAY be able to type dates directly
- The UI MAY support date ranges with a single picker interaction

## Proposed Solutions

### Option 1: React Date Picker Library (Recommended)
Use a library like `react-datepicker` or `react-day-picker`:

```typescript
import DatePicker from 'react-datepicker';
import "react-datepicker/dist/react-datepicker.css";

<div>
  <label>Available From</label>
  <DatePicker
    selected={formData.available_from}
    onChange={(date) => setFormData({...formData, available_from: date})}
    minDate={new Date()} // No past dates
    maxDate={formData.available_until || null} // Can't be after "until"
    placeholderText="Select start date"
    dateFormat="MMM d, yyyy"
  />
</div>

<div>
  <label>Available Until</label>
  <DatePicker
    selected={formData.available_until}
    onChange={(date) => setFormData({...formData, available_until: date})}
    minDate={formData.available_from || new Date()} // Can't be before "from"
    placeholderText="Select end date (optional)"
    dateFormat="MMM d, yyyy"
  />
</div>
```

**Pros:**
- Consistent across all browsers
- Built-in validation
- Keyboard accessible
- Customizable styling

**Cons:**
- Additional dependency
- Needs custom CSS for theme matching

### Option 2: Date Range Component
Create a dedicated DateRange component:

```typescript
<DateRangeSelector
  label="Availability Period"
  from={formData.available_from}
  until={formData.available_until}
  onChange={(from, until) => setFormData({...formData, available_from: from, available_until: until})}
  presets={[
    { label: 'Next 7 days', value: { from: new Date(), until: addDays(new Date(), 7) } },
    { label: 'Next 30 days', value: { from: new Date(), until: addDays(new Date(), 30) } },
    { label: 'Always available', value: { from: new Date(), until: null } }
  ]}
/>
```

**Pros:**
- Single component for the whole range
- Easy to add presets
- Enforces logical date ranges
- Reusable across app

**Cons:**
- More initial development work
- Needs good design

### Option 3: Improved Native Input with Validation
Keep native inputs but add comprehensive validation:

```typescript
const validateDates = () => {
  const errors = [];

  if (formData.available_from && formData.available_until) {
    if (new Date(formData.available_from) > new Date(formData.available_until)) {
      errors.push("'Available From' must be before 'Available Until'");
    }
  }

  if (formData.available_from && new Date(formData.available_from) < new Date()) {
    errors.push("'Available From' cannot be in the past");
  }

  return errors;
};

// Show errors inline
{dateErrors.map(error => (
  <ErrorMessage key={error} message={error} />
))}
```

**Pros:**
- No dependencies
- Works with native mobile pickers
- Simple implementation

**Cons:**
- Still inconsistent across browsers
- No presets

## Recommended Implementation

**Phase 1: Quick Win**
- Add validation for date ranges
- Add clear labels and help text
- Add optional preset buttons above date inputs

**Phase 2: Enhanced UX**
- Implement react-datepicker or similar
- Create custom DateRange component
- Add theme styling to match app design

## Test Scenarios

### WHEN a user selects "Available From" date
THEN "Available Until" MUST not allow dates before that date

### WHEN a user tries to submit with invalid dates
THEN clear error messages MUST be shown
AND the form MUST not submit

### WHEN a user clicks "Next 7 days" preset
THEN both date fields MUST be populated correctly
AND they MUST see a visual confirmation

### WHEN a user is on mobile
THEN the date picker MUST be usable with touch
AND it MUST work consistently across iOS and Android

## Impact

**Current State:** Dates are cumbersome to select, validation is missing, mobile experience varies.

**Priority:** Medium - Affects user experience but has workarounds (users can still enter dates manually).

## Related Improvements

Consider similar improvements for:
- Time pickers (for event scheduling)
- Date/time combinations
- Recurring availability patterns
- Timezone handling for distributed communities
