# USABILITY: Anonymous Gift Feature Needs Clearer Explanation

**Type:** Usability Report
**Severity:** Medium
**Status:** Identified
**Date:** 2025-12-26
**Reporter:** UI Tester (Automated)

## Summary

The CreateOfferPage has an "anonymous gift" checkbox, but the implications aren't fully clear to users. The interaction with visibility settings, agent_id, and how recipients interact with anonymous gifts needs better explanation.

## Affected Components

- CreateOfferPage (frontend/src/pages/CreateOfferPage.tsx) - Lines 73, 297-329

## Current Implementation

```typescript
// Line 73: Sets agent_id to undefined for anonymous gifts
const offerData = {
  ...formData,
  agent_id: isAnonymousGift ? undefined : user?.id,
  // ...
};

// Lines 297-329: Checkbox with some explanation
<label className="flex items-center gap-2">
  <input
    type="checkbox"
    checked={isAnonymousGift}
    onChange={(e) => setIsAnonymousGift(e.target.checked)}
  />
  <span>Make this an anonymous gift</span>
</label>

{isAnonymousGift && (
  <div className="bg-blue-50 p-3 rounded">
    <p className="text-sm text-gray-700">
      This gift will be listed without your name. Recipients won't know who offered it.
      You'll still be able to see and manage your anonymous gifts in your profile.
    </p>
  </div>
)}
```

## Questions/Concerns

### 1. Backend Handling
- Does backend accept `undefined` agent_id?
- Or should it use a special "anonymous" sentinel value?
- How is ownership tracked if agent_id is undefined?

### 2. Interaction with Visibility
- If visibility is "only_me" and gift is anonymous, who can see it?
- If visibility is "public" and gift is anonymous, does anonymity matter?
- Should anonymous gifts have restricted visibility options?

### 3. Management and Coordination
```typescript
// Line 73 comment: "You'll still be able to see and manage your anonymous gifts"
// But how if agent_id is undefined?
// Need backend to track anonymous gift creator differently
```

### 4. Privacy Implications Not Fully Explained
Users might not understand:
- Can coordinators/stewards see anonymous gift creators?
- Is the anonymity just UI-level or database-level?
- Can system logs reveal the creator?
- What about matchmaking AI - does it know the creator?

### 5. Fulfillment Questions
- How does a recipient claim an anonymous gift?
- How does the giver know someone claimed it?
- How are logistics coordinated without revealing identity?
- What if the recipient has questions?

## Requirements

### MUST

- The anonymous gift feature MUST clearly explain what information is hidden and from whom
- The backend MUST properly handle anonymous gift creation and tracking
- Anonymous gift creators MUST still be able to manage their own gifts
- The system MUST provide a secure way to coordinate anonymous gift fulfillment

### SHOULD

- The UI SHOULD explain the full implications of making a gift anonymous
- There SHOULD be examples or use cases for when to use anonymous gifts
- The visibility selector SHOULD be disabled or adjusted for anonymous gifts
- There SHOULD be a private messaging system for coordinating anonymous gifts

### MAY

- The system MAY allow different levels of anonymity
- Moderators/stewards MAY have access to anonymous gift creator info for safety
- The UI MAY show an FAQ or help link about anonymous gifts

## Proposed Solutions

### 1. Enhanced Explanation
```typescript
{isAnonymousGift && (
  <div className="bg-blue-50 p-4 rounded-lg space-y-3">
    <div className="flex items-start gap-2">
      <InfoIcon className="text-blue-600 mt-0.5" />
      <div className="text-sm text-gray-700 space-y-2">
        <p className="font-medium">How anonymous gifts work:</p>

        <ul className="list-disc list-inside space-y-1 ml-2">
          <li>Your name will not appear on the listing</li>
          <li>Recipients can claim the gift without knowing who you are</li>
          <li>Coordination happens through secure, anonymous messaging</li>
          <li>You can still manage and cancel your anonymous gifts</li>
          <li>Community stewards can see your identity for safety purposes</li>
        </ul>

        <p className="text-gray-600 italic">
          Use anonymous gifts when you want to give without recognition, support someone
          without them feeling indebted, or maintain privacy for sensitive items.
        </p>

        <a href="/help/anonymous-gifts" className="text-blue-600 underline">
          Learn more about anonymous gifts →
        </a>
      </div>
    </div>
  </div>
)}
```

### 2. Adjust Visibility Options
```typescript
{isAnonymousGift ? (
  <div>
    <label className="block text-sm font-medium text-gray-700 mb-2">
      Visibility (Anonymous)
    </label>
    <p className="text-sm text-gray-500 mb-2">
      Anonymous gifts are always visible to your community, but without your name.
    </p>
    <VisibilitySelector
      value="community"
      onChange={() => {}} // Locked to community for anonymous
      disabled={true}
    />
  </div>
) : (
  <VisibilitySelector
    value={formData.visibility}
    onChange={(v) => setFormData({...formData, visibility: v})}
  />
)}
```

### 3. Backend Implementation
```python
# In offer creation endpoint
if is_anonymous:
    # Store creator in separate field for tracking/moderation
    offer.created_by = current_user.id
    # But don't expose in public API
    offer.agent_id = None
    # Or use special anonymous user ID
    offer.agent_id = get_anonymous_user_id()

# Ensure creator can still query their own anonymous offers
def get_my_offers(include_anonymous: bool = True):
    offers = Offer.query.filter_by(agent_id=current_user.id)
    if include_anonymous:
        anonymous = Offer.query.filter_by(
            created_by=current_user.id,
            agent_id=None
        )
        offers = offers.union(anonymous)
    return offers
```

### 4. Anonymous Coordination System
```typescript
// When someone claims anonymous gift
// System creates encrypted message thread
// Provides coordination without revealing identities
// Both parties get notification but not each other's identity

// Example flow:
1. Alice creates anonymous offer: "Bicycle"
2. Bob claims it
3. System creates message thread: "Anonymous Gift Coordination #123"
4. Alice sees: "Someone claimed your bicycle"
5. Bob sees: "You claimed a bicycle"
6. Both can message to arrange pickup
7. Optional: Use pickup codes instead of addresses
```

## Test Scenarios

### WHEN a user checks "Make this anonymous"
THEN they MUST see a clear explanation of how anonymity works
AND visibility options SHOULD be adjusted appropriately

### WHEN a user creates an anonymous gift
THEN the backend MUST store it with hidden creator
AND the creator MUST still be able to see it in "My Offers"

### WHEN someone claims an anonymous gift
THEN coordination MUST happen without revealing the giver's identity
AND both parties MUST be able to communicate securely

### WHEN a steward reviews anonymous gifts
THEN they SHOULD be able to see creator info for moderation purposes
AND this SHOULD be clearly disclosed in the anonymous gift explanation

## Impact

**Current State:** Feature exists but implications aren't fully clear, may confuse users or not work as expected.

**Priority:** Medium - Feature is usable but needs better explanation and possibly backend fixes.

## Related Improvements

- Implement anonymous messaging system
- Add pickup codes / dead drop locations for truly anonymous exchanges
- Create moderation dashboard for stewards to review anonymous gifts
- Add reporting system for abuse of anonymous features
- Consider karma/trust requirements to create anonymous gifts (prevent spam)
