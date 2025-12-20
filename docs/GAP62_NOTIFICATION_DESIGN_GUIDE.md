# GAP-62 Notification Design Guide: No Guilt-Trips

**Status**: Active Design Constraint
**Philosophy**: Emma Goldman + Peter Kropotkin - "The right to be lazy is sacred"
**Date**: 2025-12-19

## Purpose

This document ensures all future notification development adheres to GAP-62 (Loafer's Rights) principles. No notification should pressure users to contribute, compare their activity to others, or make them feel guilty for resting.

---

## Core Principles

### ✅ ALLOWED: Informational Notifications

Notifications that inform users about events relevant to them:

```typescript
// ✅ GOOD: Informing about matches/responses
"Alice accepted your offer of tomatoes"
"New offer matches your need for beekeeping help"
"Your listing expires in 24 hours"

// ✅ GOOD: System updates
"New community shelf items available"
"Emma added you to 'Garden Collective' group"

// ✅ GOOD: Direct communication
"Bob sent you a message"
"Community event tomorrow: Seed Swap"
```

**Why allowed**: These notifications serve the user's needs without implying obligation.

---

### ❌ FORBIDDEN: Guilt-Trip Notifications

Notifications that pressure contribution or shame non-participation:

```typescript
// ❌ BAD: Contribution pressure
"You haven't posted an offer in 2 weeks!"
"It's been a while - share something with the community?"
"Your neighbors are waiting for your contributions"

// ❌ BAD: Comparison/competition
"You're in the bottom 10% of contributors this month"
"Alice has shared 47 items - you've only shared 3"
"Top contributors this week: [leaderboard]"

// ❌ BAD: Productivity shaming
"Your profile looks empty - add some offers!"
"Come on, you can do better!"
"Inactive users may lose community access" // FALSE SCARCITY

// ❌ BAD: Subtle pressure
"The community needs more offers like yours"
"Haven't seen you in a while - everything okay?" // Implies obligation
```

**Why forbidden**: These create capitalist productivity pressure incompatible with mutual aid.

---

## Design Patterns

### Pattern 1: Rest Mode Awareness

When implementing notifications, **ALWAYS check agent status first**:

```python
async def should_send_notification(user_id: str, notification_type: str) -> bool:
    """Check if notification should be sent based on user status"""
    agent = await get_agent(user_id)

    # GAP-62: Respect rest mode
    if agent.status in [AgentStatus.RESTING, AgentStatus.SABBATICAL]:
        # Only send critical notifications
        if notification_type in ['safety_alert', 'urgent_message']:
            return True
        return False  # Silence all other notifications

    return True
```

**Critical notifications only:**
- Safety/security alerts
- Time-sensitive direct messages from close connections
- Medical/emergency coordination

### Pattern 2: Supportive Messaging

When users haven't been active, **celebrate their break instead of pressuring them**:

```typescript
// ❌ WRONG
if (daysSinceLastOffer > 14) {
  notify("You haven't shared anything recently - post an offer?");
}

// ✅ RIGHT
if (agent.status === 'active' && daysSinceLastOffer > 30) {
  // Optional: gentle, non-judgmental reminder IF user has enabled it
  if (user.settings.reminders_enabled) {
    notify("Taking a break? That's valid. The commune is here when you're ready.");
  }
}
```

**Key difference**: The right version:
1. Checks if user is actively participating (not in rest mode)
2. Only sends if user has opted into reminders
3. Normalizes rest instead of pressuring contribution

### Pattern 3: Community Stats (Aggregate, Not Individual)

```typescript
// ❌ WRONG: Individual comparison
{
  title: "Your Contribution Stats",
  body: "You've shared 3 gifts this month. Top contributors: Alice (47), Bob (32)",
  action: "Contribute more"
}

// ✅ RIGHT: Community abundance
{
  title: "Community Abundance This Month",
  body: `
    347 gifts shared
    89 needs met
    23 people in rest mode (we're holding you)
  `,
  action: "Browse community shelf"
}
```

**Key difference**: Focus on collective abundance, not individual scores.

---

## Implementation Checklist

Before implementing ANY notification feature, verify:

- [ ] Does this notification inform or pressure?
- [ ] Does it respect rest mode (check `agent.status`)?
- [ ] Does it compare users or create hierarchy?
- [ ] Is it opt-in or default-on?
- [ ] Does the language normalize rest and non-participation?
- [ ] Would Emma Goldman approve of this notification?

**If you answer "pressure", "no", "yes", "default-on", "no", or "no" to any of these, redesign the notification.**

---

## Rest Mode Integration

All notification code MUST integrate with rest mode:

### Backend Template

```python
from valueflows_node.app.models.vf.agent import AgentStatus
from valueflows_node.app.repositories.vf.agent_repo import AgentRepository

async def send_notification(user_id: str, notification_type: str, message: str):
    """Send notification respecting GAP-62 rest mode"""
    # Get agent status
    db = get_database()
    db.connect()
    agent_repo = AgentRepository(db.conn)
    agent = agent_repo.find_by_id(user_id)
    db.close()

    if not agent:
        return False

    # GAP-62: Respect rest mode
    if agent.status in [AgentStatus.RESTING, AgentStatus.SABBATICAL]:
        # Only critical notifications
        if notification_type not in ['safety_alert', 'urgent_message']:
            logger.info(f"Skipping notification for {user_id} - in rest mode")
            return False

    # Send notification
    await notification_service.send(user_id, notification_type, message)
    return True
```

### Frontend Template

```typescript
import { useAgent } from '@/hooks/useAgent';

export function NotificationBadge() {
  const { agent } = useAgent();
  const { notifications } = useNotifications();

  // GAP-62: Show rest mode status instead of notification count
  if (agent?.status === 'resting' || agent?.status === 'sabbatical') {
    return (
      <Badge variant="peaceful">
        🌙 Resting
      </Badge>
    );
  }

  return notifications.length > 0 ? (
    <Badge variant="info">{notifications.length}</Badge>
  ) : null;
}
```

---

## Settings Requirements

Users MUST be able to control notifications:

```typescript
interface NotificationSettings {
  // GAP-62: All contribution-related reminders default OFF
  contributionReminders: boolean;  // Default: false
  statsVisibility: 'hidden' | 'personal' | 'community';  // Default: 'community'

  // Core functionality notifications
  matchNotifications: boolean;  // Default: true
  messageNotifications: boolean;  // Default: true
  eventNotifications: boolean;  // Default: true

  // Rest mode
  restModeEnabled: boolean;  // Controlled via PATCH /vf/agents/{id}/status
}
```

**Critical**: Contribution reminders MUST default to OFF. Users opt IN to pressure, not OUT.

---

## Forbidden Patterns

### Anti-Pattern 1: "Engagement" Metrics

```typescript
// ❌ NEVER track or display these metrics
interface ForbiddenMetrics {
  contributionScore: number;  // FORBIDDEN
  rank: number;  // FORBIDDEN
  percentile: number;  // FORBIDDEN
  streak: number;  // FORBIDDEN (gamification pressure)
  lastActiveDate: string;  // FORBIDDEN (used for shaming)
}
```

**Why forbidden**: These metrics exist solely to create pressure and comparison.

### Anti-Pattern 2: "Nudge" Algorithms

```typescript
// ❌ NEVER implement engagement algorithms
function calculateEngagementNudge(user) {
  if (user.daysSinceLastPost > 7) {
    return "suggestion_to_post";  // FORBIDDEN
  }
}
```

**Why forbidden**: This is surveillance capitalism dressed as mutual aid.

### Anti-Pattern 3: Social Pressure

```typescript
// ❌ NEVER use peer pressure tactics
"Your friends Alice and Bob have contributed this week"  // FORBIDDEN
"The community is counting on you"  // FORBIDDEN
"Don't let your cell down"  // FORBIDDEN
```

**Why forbidden**: True mutual aid is voluntary, not coerced through social pressure.

---

## Philosophical Grounding

### Emma Goldman: "The Right to Be Lazy"

> "The right to be lazy is not the enemy of solidarity. It's its foundation."

Notifications should serve users' needs, not the system's desire for engagement. A user taking a year off is as valid as a user sharing daily.

### Peter Kropotkin: Mutual Aid

> "In a well-organized society, all will have a right to live and to enjoy life."

Not "earn" the right. Not "work for" the right. Just **have** the right. Notifications must reflect this unconditional belonging.

### Paul Lafargue: Productivity as Violence

> "The capitalist fetish for productivity must be rejected."

Any notification that measures or compares productivity is capitalist violence, not mutual aid.

---

## Review Process

Before merging ANY notification feature:

1. **Self-review**: Does this pass the Goldman Test?
   - "Would Emma Goldman approve of this notification?"

2. **Code review**: Check for forbidden patterns
   - Grep for: `contribution`, `score`, `rank`, `streak`, `active`
   - Flag any usage that creates pressure

3. **User testing**: Show to community members
   - "Does this make you feel pressured?"
   - "Would you feel bad receiving this notification?"

If **any** user reports feeling pressured, **reject the notification design**.

---

## Examples in Practice

### Scenario 1: User Hasn't Posted in 3 Months

**❌ Wrong Approach:**
```typescript
if (monthsSinceLastPost >= 3) {
  notify("We miss your contributions! Share something today?");
}
```

**✅ Right Approach:**
```typescript
// No notification at all
// User's absence is their right
// If they return, welcome them without judgment
```

### Scenario 2: Community Shelf is Empty

**❌ Wrong Approach:**
```typescript
notify("The community shelf is empty - can you help fill it?");
```

**✅ Right Approach:**
```typescript
// Option 1: No notification (scarcity is temporary, not emergency)

// Option 2: If genuinely informational
notify("Community shelf currently empty - check back later or add items if you have capacity");
// Note the "if you have capacity" - no obligation
```

### Scenario 3: User Has Only Needs, No Offers

**❌ Wrong Approach:**
```typescript
if (offers.length === 0 && needs.length > 0) {
  notify("Balance your profile - add some offers too!");
}
```

**✅ Right Approach:**
```typescript
// No notification
// Profile with only needs is 100% valid
// Display on profile: "Everyone goes through seasons of capacity and need"
```

---

## Maintenance

This guide MUST be updated when:
- New notification types are proposed
- Notification system architecture changes
- Community feedback indicates pressure is being felt

**Last updated**: 2025-12-19
**Next review**: When GAP-09 (Notification System) frontend is implemented

---

## Related Specs

- **GAP-62**: Loafer's Rights (this spec)
- **GAP-09**: Notification System (implementation must follow this guide)
- **GAP-61**: Anonymous Gifts (no surveillance of generosity)
- **GAP-59**: Conscientization Prompts (critical reflection, not pressure)

---

## Enforcement

This is not a suggestion. This is a **design constraint**.

Any notification that violates these principles MUST be:
1. Flagged in code review
2. Rejected from merge
3. Removed if already deployed

**The right to be lazy is sacred. Our notification system must reflect this.**
