# USABILITY: Accessibility Improvements Needed Throughout Application

**Type:** Usability Report
**Severity:** Medium
**Status:** Identified
**Date:** 2025-12-26
**Reporter:** UI Tester (Automated)

## Summary

The application has multiple accessibility issues that affect users who rely on keyboard navigation, screen readers, or other assistive technologies. Many interactive elements lack proper ARIA labels, keyboard navigation is incomplete, and form validation errors aren't announced to screen readers.

## Affected Components

- All interactive components (buttons, forms, modals)
- Card components (OfferCard, NeedCard, etc.)
- Navigation component
- Form pages (CreateOfferPage, CreateNeedPage, etc.)
- Error messaging

## Issues Identified

### 1. Missing ARIA Labels on Icon Buttons

Many buttons use only icons without text labels:

```typescript
// OfferCard - Edit/Delete buttons
<button onClick={() => onEdit(offer)}>
  <EditIcon />  {/* ← Screen reader announces "button" with no context */}
</button>

<button onClick={() => onDelete(offer.id)}>
  <TrashIcon />  {/* ← Screen reader says "button" - not helpful */}
</button>
```

**Impact:** Screen reader users don't know what these buttons do.

### 2. Form Validation Not Announced

```typescript
{error && <ErrorMessage message={error} />}

// Error appears visually but screen readers don't announce it
// User submits form, doesn't know why it failed
```

**Impact:** Blind users may not realize form submission failed or why.

### 3. Missing Keyboard Navigation

- Modal/overlay focus not trapped
- No focus return when closing modals
- Tab order may be illogical
- No keyboard shortcuts for common actions

**Impact:** Keyboard-only users struggle to navigate efficiently.

### 4. Poor Focus Indicators

Some interactive elements may not have visible focus states:

```css
/* Missing or unclear :focus styles */
button:focus {
  /* No distinct visual indicator */
}
```

**Impact:** Keyboard users can't tell where they are on the page.

### 5. Low Color Contrast

Some text/background combinations may not meet WCAG AA standards:

- Gray text on light backgrounds
- Placeholder text may be too light
- Disabled state text may be unreadable

**Impact:** Users with low vision can't read content.

### 6. Missing Alt Text

Images and icons may lack descriptive alt text:

```typescript
<img src={user.avatar} />  {/* ← No alt text */}
```

**Impact:** Screen reader users don't know what images show.

### 7. No Skip Links

No "Skip to main content" link for keyboard users:

**Impact:** Keyboard users must tab through entire navigation on every page.

### 8. Form Labels Not Associated

Some form inputs may not have properly associated labels:

```typescript
// Bad:
<label>Title</label>
<input type="text" />

// Good:
<label htmlFor="title">Title</label>
<input id="title" type="text" />
```

**Impact:** Screen readers can't tell what each input is for.

## Requirements

### MUST (WCAG 2.1 Level A)

- All images MUST have alt text
- Form inputs MUST have associated labels
- All functionality MUST be keyboard accessible
- Color MUST NOT be the only means of conveying information

### MUST (WCAG 2.1 Level AA)

- Text MUST have minimum 4.5:1 contrast ratio (3:1 for large text)
- Focus indicators MUST be visible
- Page MUST have a descriptive title
- Link text MUST be descriptive (no "click here")

### SHOULD

- Provide skip navigation links
- Announce dynamic content changes to screen readers
- Support keyboard shortcuts for power users
- Provide text alternatives for all non-text content

## Proposed Solutions

### 1. Add ARIA Labels to Icon Buttons

```typescript
<button
  onClick={() => onEdit(offer)}
  aria-label={`Edit offer: ${offer.title}`}
  title="Edit this offer"
>
  <EditIcon aria-hidden="true" />
</button>

<button
  onClick={() => onDelete(offer.id)}
  aria-label={`Delete offer: ${offer.title}`}
  title="Delete this offer"
>
  <TrashIcon aria-hidden="true" />
</button>
```

### 2. Announce Form Errors

```typescript
import { useEffect, useRef } from 'react';

const FormError = ({ message }: { message: string }) => {
  const errorRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Announce to screen readers when error appears
    if (message && errorRef.current) {
      errorRef.current.focus();
    }
  }, [message]);

  return (
    <div
      ref={errorRef}
      role="alert"
      aria-live="assertive"
      className="error-message"
      tabIndex={-1}
    >
      {message}
    </div>
  );
};
```

### 3. Improve Keyboard Navigation

```typescript
// Add focus trap for modals
import FocusTrap from 'focus-trap-react';

const Modal = ({ isOpen, onClose, children }) => {
  const previousFocus = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (isOpen) {
      previousFocus.current = document.activeElement as HTMLElement;
    } else if (previousFocus.current) {
      previousFocus.current.focus();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <FocusTrap>
      <div role="dialog" aria-modal="true">
        {children}
      </div>
    </FocusTrap>
  );
};
```

### 4. Add Skip Link

```typescript
// In Layout component
<a href="#main-content" className="skip-link">
  Skip to main content
</a>

// In CSS
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  background: #000;
  color: #fff;
  padding: 8px;
  z-index: 100;
}

.skip-link:focus {
  top: 0;
}
```

### 5. Improve Focus Indicators

```css
/* Make focus visible and consistent */
*:focus {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}

/* Or use :focus-visible for modern browsers */
*:focus-visible {
  outline: 3px solid #3b82f6;
  outline-offset: 2px;
}
```

### 6. Associate Labels with Inputs

```typescript
const FormField = ({ label, id, ...inputProps }) => (
  <div>
    <label htmlFor={id} className="form-label">
      {label}
    </label>
    <input id={id} {...inputProps} />
  </div>
);

// Usage:
<FormField
  label="Offer Title"
  id="offer-title"
  type="text"
  value={formData.title}
  onChange={(e) => setFormData({...formData, title: e.target.value})}
/>
```

### 7. Add Live Region for Dynamic Updates

```typescript
// Announce when offers are loaded/updated
<div
  role="status"
  aria-live="polite"
  aria-atomic="true"
  className="sr-only"
>
  {isLoading ? 'Loading offers...' : `${offers.length} offers found`}
</div>

// sr-only class (screen reader only):
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
```

## Implementation Plan

### Phase 1: Critical Fixes (High Impact, Low Effort)
1. Add ARIA labels to all icon buttons
2. Add skip link to main content
3. Associate all form labels with inputs
4. Add role="alert" to error messages

### Phase 2: Keyboard Navigation (Medium Effort)
1. Implement focus trap for modals
2. Add proper focus management
3. Improve focus indicators
4. Test full keyboard navigation flow

### Phase 3: Screen Reader Optimization (Medium Effort)
1. Add alt text to all images
2. Implement live regions for dynamic content
3. Add descriptive labels to all interactive elements
4. Test with NVDA and VoiceOver

### Phase 4: Advanced Improvements (Nice to Have)
1. Add keyboard shortcuts
2. Implement custom focus order where needed
3. Add ARIA landmarks for page regions
4. Support reduced motion preferences

## Test Scenarios

### WHEN a keyboard-only user navigates the site
THEN they MUST be able to access all functionality
AND they MUST see clear focus indicators
AND they MUST be able to skip repetitive navigation

### WHEN a screen reader user fills out a form
THEN all inputs MUST be announced with their labels
AND validation errors MUST be announced
AND they MUST know when form submission succeeds or fails

### WHEN a user with low vision accesses the site
THEN all text MUST meet contrast requirements
AND they MUST be able to read all content
AND focus indicators MUST be highly visible

### WHEN a user with motor impairments uses the site
THEN click targets MUST be large enough (minimum 44x44px)
AND they MUST be able to navigate without precision clicking

## Tools for Testing

1. **Automated:**
   - axe DevTools browser extension
   - Lighthouse accessibility audit
   - Pa11y CI for continuous testing

2. **Manual:**
   - Keyboard navigation testing
   - Screen reader testing (NVDA on Windows, VoiceOver on Mac/iOS)
   - Color contrast analyzer

3. **CI Integration:**
   ```json
   "scripts": {
     "test:a11y": "pa11y-ci --sitemap http://localhost:3000/sitemap.xml"
   }
   ```

## Impact

**Current State:** Application may be difficult or impossible to use for users with disabilities.

**Priority:** Medium (should be High for legal/ethical reasons) - Accessibility is a right, not a feature.

## Legal/Ethical Considerations

- May violate ADA (Americans with Disabilities Act) requirements
- May violate Section 508 compliance
- Excludes significant portion of potential users
- Contrary to solarpunk values of inclusivity and community

## Resources

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [React Accessibility](https://react.dev/learn/accessibility)
- [The A11Y Project](https://www.a11yproject.com/)
- [WebAIM Articles](https://webaim.org/articles/)
