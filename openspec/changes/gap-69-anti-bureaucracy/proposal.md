# Proposal: Anti-Bureaucracy (Committee Sabotage Resilience)

**Submitted By:** Philosopher Council (CIA Manual + Anarchist Tradition)
**Date:** 2025-12-19
**Status:** Draft
**Gap Addressed:** GAP-69
**Priority:** P3 - Philosophical (Post-Workshop)

## Problem Statement

The CIA's 1944 Simple Sabotage Manual advised saboteurs to:
- "Insist on doing everything through channels"
- "Make speeches, talk as frequently as possible"
- "Refer all matters to committees for further study"
- "Attempt to make committees as large as possible"

**Sound familiar?** Many communes accidentally sabotage themselves with over-process.

Bureaucracy is the enemy of action. Process can become performance. Meetings can replace doing.

## Proposed Solution

### Anti-Bureaucracy Guardrails

Gentle nudges when the community is accidentally self-sabotaging:

### 1. Process Budget

Track how much time goes into process vs. action:

```python
class ProcessMetrics(BaseModel):
    """Aggregated, not per-person surveillance"""
    cell_id: str
    period: str  # "2025-W12"

    time_discussing: timedelta    # Aggregate meeting/proposal time
    time_doing: timedelta         # Aggregate exchange/action time

    @property
    def process_ratio(self) -> float:
        """Higher = more bureaucracy"""
        total = self.time_discussing + self.time_doing
        return self.time_discussing / total if total else 0

    @property
    def warning(self) -> Optional[str]:
        if self.process_ratio > 0.5:
            return "You're spending more time deciding than doing. CIA sabotage manual approves. Anarchists don't."
        return None
```

### 2. Committee Size Limits

Research shows groups over 7 become ineffective:

```python
MAX_COMMITTEE_SIZE = 7

def add_committee_member(committee_id: str, user_id: str):
    committee = get_committee(committee_id)

    if len(committee.members) >= MAX_COMMITTEE_SIZE:
        return Warning(
            "Committees over 7 people become ineffective. "
            "Consider splitting into two groups, or having some members step back."
        )

    committee.members.append(user_id)
```

### 3. Decision Velocity

Track how long decisions take:

```python
class DecisionVelocity(BaseModel):
    """Cell-level, not individual surveillance"""
    cell_id: str
    avg_decision_time: timedelta
    pending_decisions: int

    @property
    def bureaucracy_risk(self) -> str:
        days = self.avg_decision_time.days
        if days < 2:
            return "LOW - You're deciding quickly"
        elif days < 7:
            return "MEDIUM - Are you being careful or stuck?"
        else:
            return "HIGH - CIA saboteurs would be proud. Time to unstick?"
```

### 4. Just Do It Mode

For small, reversible decisions:

```python
class DecisionScope(BaseModel):
    affects_people: int           # How many people impacted
    reversible: bool              # Can we undo it?
    resources_committed: float    # $ or equivalent

def should_just_do_it(scope: DecisionScope) -> bool:
    """Some things don't need committee approval"""
    if scope.affects_people <= 3 and scope.reversible:
        return True  # Just do it!
    return False

# Prompt:
# "This decision affects 2 people and is reversible.
#  Instead of forming a committee, consider: just try it.
#  You can always undo it if it doesn't work."
```

## Requirements

### Requirement: Process Visibility

The system SHALL make process overhead visible.

#### Scenario: Process Check
- GIVEN a cell has spent 10 hours in meetings this week
- AND completed 3 exchanges
- WHEN the steward views cell health
- THEN they see: "Process ratio: 77%. More discussing than doing."
- AND gentle suggestion: "Is all this process necessary?"

### Requirement: Committee Size Warnings

The system SHALL warn when committees get too large.

#### Scenario: Too Many Cooks
- GIVEN a committee has 7 members
- WHEN someone tries to add an 8th
- THEN warning appears: "Committees over 7 become ineffective"
- AND options: "Split into two groups" or "Override warning"
- AND if overridden, the app allows it (not a hard block)

### Requirement: Decision Velocity Tracking

The system SHALL track how long decisions take.

#### Scenario: Stuck Decisions
- GIVEN a proposal has been open for 14 days
- AND discussion is ongoing
- WHEN the steward views it
- THEN they see: "This decision has been open for 14 days. Bureaucracy risk: HIGH"
- AND suggestion: "Set a deadline, or table it for now"

### Requirement: Just Do It Encouragement

The system SHALL encourage action for small decisions.

#### Scenario: Don't Need Permission
- GIVEN Alice wants to organize a neighborhood cleanup
- AND it affects ~5 people and costs nothing
- WHEN Alice starts to create a proposal
- THEN she sees: "This seems small and reversible. Do you need to propose it, or just do it?"
- AND option: "Just announce it" (no approval process)

## Data Model

```python
class CellProcessMetrics(BaseModel):
    """Aggregated cell-level metrics - NOT individual surveillance"""
    cell_id: str
    week: str

    # Aggregate time spent
    total_meeting_time: timedelta
    total_proposal_discussion: timedelta
    total_exchanges_completed: int

    # Computed
    @property
    def process_overhead(self) -> float:
        """Ratio of process to action"""
        pass

class DecisionTracker(BaseModel):
    proposal_id: str
    opened_at: datetime
    decided_at: Optional[datetime]

    @property
    def days_open(self) -> int:
        end = self.decided_at or datetime.utcnow()
        return (end - self.opened_at).days
```

## Privacy Guarantees

Anti-bureaucracy features measure the **system**, not individuals:

**What we track:**
- Total meeting time (aggregated, not who attended)
- Decision velocity (how long proposals stay open)
- Committee sizes (membership counts)

**What we DON'T track:**
- Who talks most in meetings
- Who blocks decisions
- Individual "bureaucracy scores"
- Who is "slowing things down"

This is about healthy systems, not blaming individuals.

## Implementation

### Phase 1: Process Visibility
- Track meeting time (aggregate)
- Show process ratio on cell dashboard
- Gentle warnings when ratio is high

### Phase 2: Committee Guardrails
- Warn when adding 8th member
- Suggest splits
- Track committee sizes over time (aggregate)

### Phase 3: Decision Velocity
- Show how long proposals are open
- Suggest deadlines for stuck decisions
- Bureaucracy risk indicator

### Phase 4: Just Do It Mode
- Detect small/reversible proposals
- Encourage direct action
- "Announce" option vs "Propose" option

## Anti-Bureaucracy Prompts

```python
ANTI_BUREAUCRACY_PROMPTS = [
    {
        "trigger": "proposal_open_7_days",
        "message": "This has been discussed for a week. Ready to decide?"
    },
    {
        "trigger": "committee_size_8",
        "message": "Research shows groups over 7 become ineffective. Split up?"
    },
    {
        "trigger": "process_ratio_high",
        "message": "You're spending more time deciding than doing. The CIA approves. Do you?"
    },
    {
        "trigger": "small_proposal_detected",
        "message": "This affects 3 people and is reversible. Just try it?"
    }
]
```

## Philosophical Foundation

**Anarchism vs. bureaucracy:**
Bureaucracy is centralized control disguised as process. It creates gatekeepers, slows action, and exhausts energy on procedure rather than purpose.

**Prefigurative politics:**
We should practice the world we want to build. Do we want a world of endless meetings? Or a world where people just help each other?

**CIA wisdom (inverted):**
The CIA knew exactly how to sabotage organizations: make them bureaucratic. We can use their wisdom in reverse - recognize the warning signs and avoid them.

**Bias toward action:**
When in doubt, do something. A bad decision quickly reversed teaches more than months of committee deliberation. Action generates feedback. Process generates... more process.

## Success Criteria

- [ ] Process ratio visible to stewards
- [ ] Committee size warnings work
- [ ] Decision velocity tracked
- [ ] "Just do it" prompts for small decisions
- [ ] No individual surveillance (aggregate metrics only)
- [ ] Warnings are gentle, not shaming

## Dependencies

- Proposal/governance system
- Meeting tracking (if implemented)
- Cell dashboard

## Notes

This isn't anti-process. Good process is valuable. But process can metastasize. Meetings can become the work instead of supporting the work.

The CIA knew this. They weaponized bureaucracy. We should be aware of the symptoms:
- Everything needs committee approval
- Committees grow endlessly
- Decisions take weeks
- More talking than doing

When you see these signs, the app will gently remind you: "Anarchists don't love meetings. Do you really need this one?"
