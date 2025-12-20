# Anti-Bureaucracy Guide - GAP-69

**CIA Simple Sabotage Manual (1944):** "Insist on doing everything through channels. Refer all matters to committees for further study. Make committees as large as possible."

**Us:** Let's not do that.

## Implementation Guide

Anti-bureaucracy features help communities recognize when they're accidentally self-sabotaging with over-process.

### 1. Process Budget (Implemented in governance metrics)

**Location:** `app/services/governance_metrics_service.py`

```python
class ProcessMetrics:
    """Track time spent discussing vs. doing (aggregated, not per-person)"""

    cell_id: str
    week: str

    time_discussing: timedelta  # Aggregate meeting/proposal time
    time_doing: timedelta      # Aggregate exchange/action time

    @property
    def process_ratio(self) -> float:
        """Higher = more bureaucracy"""
        total = self.time_discussing + self.time_doing
        return self.time_discussing / total if total else 0

    @property
    def warning(self) -> Optional[str]:
        if self.process_ratio > 0.5:
            return "You're spending more time deciding than doing. CIA approves. Anarchists don't."
        return None
```

### 2. Committee Size Limits (Implemented in governance)

**Location:** `app/services/governance_service.py`

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

### 3. Decision Velocity (Tracked in proposals)

**Location:** `app/services/proposal_service.py`

```python
class DecisionVelocity:
    """Cell-level metrics, not individual surveillance"""

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

### 4. Just Do It Mode (Proposal creation)

**Location:** `app/services/proposal_service.py`

```python
class DecisionScope:
    affects_people: int
    reversible: bool
    resources_committed: float

def should_just_do_it(scope: DecisionScope) -> bool:
    """Some things don't need committee approval"""
    if scope.affects_people <= 3 and scope.reversible:
        return True  # Just do it!
    return False

# UI prompt:
# "This decision affects 2 people and is reversible.
#  Instead of forming a committee, consider: just try it.
#  You can always undo it if it doesn't work."
```

## Steward Dashboard Integration

**Location:** `app/api/steward_dashboard.py`

```python
@router.get("/process-metrics")
async def get_process_metrics(cell_id: str):
    """Get process overhead metrics"""
    metrics = get_metrics(cell_id)

    return {
        "process_ratio": metrics.process_ratio,
        "warning": metrics.warning,
        "decision_velocity": metrics.decision_velocity,
        "stuck_proposals": metrics.stuck_proposals
    }
```

## Anti-Bureaucracy Prompts

```python
ANTI_BUREAUCRACY_PROMPTS = {
    "proposal_open_7_days": {
        "message": "This has been discussed for a week. Ready to decide?"
    },
    "committee_size_8": {
        "message": "Research shows groups over 7 become ineffective. Split up?"
    },
    "process_ratio_high": {
        "message": "You're spending more time deciding than doing. The CIA approves. Do you?"
    },
    "small_proposal_detected": {
        "message": "This affects 3 people and is reversible. Just try it?"
    }
}
```

## Usage

### For Stewards

Dashboard shows process health:

```
Process Health (This Week):
- Meeting time: 10 hours
- Exchange time: 3 hours
- Process ratio: 77% ⚠️

Warning: More discussing than doing

Stuck Proposals:
- "Garden expansion" (14 days open)
- "Tool library hours" (21 days open)

Suggestion: Set deadlines or table for now
```

### For Members

When creating proposals:

```
New Proposal: "Neighborhood cleanup Saturday"

Affects: ~5 people
Reversible: Yes
Cost: $0

💡 This seems small and reversible.
   Do you need to propose it, or just announce it?

[Just Announce]  [Create Proposal Anyway]
```

## Philosophy

**Why this matters:**

1. **Process can metastasize:** Meetings become the work instead of supporting the work
2. **CIA knew this:** They weaponized bureaucracy as sabotage
3. **Bias toward action:** Bad decision quickly reversed > months of deliberation
4. **Prefigurative politics:** Practice the world we want (not endless meetings)

**Anarchism vs. bureaucracy:**
Bureaucracy is centralized control disguised as process. It creates gatekeepers, slows action, exhausts energy on procedure rather than purpose.

## Implementation Status

✅ Process metrics in governance service
✅ Committee size warnings
✅ Decision velocity tracking
✅ "Just do it" detection logic
✅ Steward dashboard integration
⏳ Frontend UI for warnings (pending)
⏳ Automated cleanup of stuck proposals (pending)

The monitoring is in place. Next: make it visible and actionable.
