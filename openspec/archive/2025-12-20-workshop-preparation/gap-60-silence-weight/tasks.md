# GAP-60: Silence Weight in Governance - Implementation Tasks

**Status**: In Progress
**Priority**: P3 - Philosophical (Post-Workshop)
**Estimated Total Effort**: 2-3 days
**Philosopher**: bell hooks

## Overview

Implement bell hooks' framework for equitable governance by tracking and surfacing silence in decision-making, without shaming or surveilling quiet participants.

## Phase 1: Data Models & Database (4-6 hours)

### Task 1.1: Create Governance Vote Models
**Effort**: 2 hours

Create data models for tracking votes with silence awareness:

```python
# app/models/governance.py

from pydantic import BaseModel, Field
from typing import List, Dict, Literal, Optional
from datetime import datetime
from enum import Enum

class VoteChoice(str, Enum):
    YES = "yes"
    NO = "no"
    ABSTAIN = "abstain"

class VoteSession(BaseModel):
    """Vote session with silence tracking"""
    id: str
    proposal_id: str
    cell_id: str
    opened_at: datetime
    closes_at: datetime
    eligible_voters: List[str]  # All cell members at time of opening
    votes: Dict[str, VoteChoice]  # user_id -> choice
    extended_count: int = 0
    quorum_required: Optional[float] = None  # 0.0-1.0, for critical decisions

    @property
    def silent_voters(self) -> List[str]:
        """Voters who haven't participated"""
        return [v for v in self.eligible_voters if v not in self.votes]

    @property
    def silence_weight(self) -> float:
        """Ratio of silent to total eligible voters"""
        total = len(self.eligible_voters)
        return len(self.silent_voters) / total if total > 0 else 0.0

    @property
    def participation_rate(self) -> float:
        """Ratio of participated to total eligible"""
        return 1.0 - self.silence_weight

    @property
    def should_pause(self) -> bool:
        """More silent than voted = pause for outreach"""
        return len(self.silent_voters) > len(self.votes)

    @property
    def has_quorum(self) -> bool:
        """Check if quorum requirement met"""
        if self.quorum_required is None:
            return True
        return self.participation_rate >= self.quorum_required

class VoteOutreach(BaseModel):
    """Ephemeral - NOT stored after vote closes"""
    id: str
    vote_session_id: str
    sent_at: datetime
    sent_to: List[str]  # Who got check-ins
    message: str
    # NOTE: No record of responses or reasons for silence
```

**Files to Create**:
- `app/models/governance.py` - Vote models with silence tracking

**Verification**:
- [ ] Models import without errors
- [ ] silence_weight property calculates correctly
- [ ] should_pause logic works as expected

---

### Task 1.2: Create Database Schema
**Effort**: 2 hours

```sql
-- app/database/migrations/004_governance_silence_weight.sql

CREATE TABLE IF NOT EXISTS vote_sessions (
    id TEXT PRIMARY KEY,
    proposal_id TEXT NOT NULL,
    cell_id TEXT NOT NULL,
    opened_at TIMESTAMP NOT NULL,
    closes_at TIMESTAMP NOT NULL,
    eligible_voters TEXT NOT NULL,  -- JSON array
    votes TEXT NOT NULL DEFAULT '{}',  -- JSON object {user_id: choice}
    extended_count INTEGER DEFAULT 0,
    quorum_required REAL,  -- NULL or 0.0-1.0
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cell_id) REFERENCES cells(id)
);

CREATE INDEX idx_vote_sessions_cell ON vote_sessions(cell_id);
CREATE INDEX idx_vote_sessions_proposal ON vote_sessions(proposal_id);
CREATE INDEX idx_vote_sessions_closes_at ON vote_sessions(closes_at);

-- Ephemeral table - auto-purge after vote closes
CREATE TABLE IF NOT EXISTS vote_outreach (
    id TEXT PRIMARY KEY,
    vote_session_id TEXT NOT NULL,
    sent_at TIMESTAMP NOT NULL,
    sent_to TEXT NOT NULL,  -- JSON array
    message TEXT NOT NULL,
    purge_at TIMESTAMP NOT NULL,  -- Set to vote closes_at
    FOREIGN KEY (vote_session_id) REFERENCES vote_sessions(id) ON DELETE CASCADE
);

CREATE INDEX idx_vote_outreach_purge ON vote_outreach(purge_at);
```

**Files to Create**:
- `app/database/migrations/004_governance_silence_weight.sql`

**Verification**:
- [ ] Migration runs successfully
- [ ] Tables created with correct schema
- [ ] Indexes created

---

### Task 1.3: Create Repository Layer
**Effort**: 2-3 hours

```python
# app/database/governance_repository.py

class GovernanceRepository:
    async def create_vote_session(self, session: VoteSession) -> VoteSession
    async def get_vote_session(self, session_id: str) -> Optional[VoteSession]
    async def cast_vote(self, session_id: str, user_id: str, choice: VoteChoice) -> VoteSession
    async def extend_vote_session(self, session_id: str, new_closes_at: datetime) -> VoteSession
    async def get_active_sessions(self, cell_id: str) -> List[VoteSession]
    async def create_outreach(self, outreach: VoteOutreach) -> VoteOutreach
    async def purge_expired_outreach(self) -> int
```

**Files to Create**:
- `app/database/governance_repository.py`

**Verification**:
- [ ] All CRUD operations work
- [ ] JSON serialization/deserialization works for arrays/objects
- [ ] Outreach purge logic works

---

## Phase 2: Service Layer (3-4 hours)

### Task 2.1: Governance Service
**Effort**: 3-4 hours

```python
# app/services/governance_service.py

class GovernanceService:
    def __init__(self, repo: GovernanceRepository):
        self.repo = repo

    async def create_vote(
        self,
        proposal_id: str,
        cell_id: str,
        duration_hours: int,
        quorum_required: Optional[float] = None
    ) -> VoteSession:
        """Create new vote session with eligible voters from cell"""
        # Get current cell members
        eligible = await self.get_cell_members(cell_id)

        session = VoteSession(
            id=generate_id(),
            proposal_id=proposal_id,
            cell_id=cell_id,
            opened_at=datetime.now(),
            closes_at=datetime.now() + timedelta(hours=duration_hours),
            eligible_voters=eligible,
            votes={},
            quorum_required=quorum_required
        )

        return await self.repo.create_vote_session(session)

    async def cast_vote(
        self,
        session_id: str,
        user_id: str,
        choice: VoteChoice
    ) -> VoteSession:
        """Cast vote and return updated session"""
        return await self.repo.cast_vote(session_id, user_id, choice)

    async def check_silence_weight(self, session_id: str) -> Dict:
        """Get silence metrics for display"""
        session = await self.repo.get_vote_session(session_id)
        if not session:
            raise ValueError("Session not found")

        return {
            "silence_weight": session.silence_weight,
            "participation_rate": session.participation_rate,
            "should_pause": session.should_pause,
            "has_quorum": session.has_quorum,
            "silent_count": len(session.silent_voters),
            "voted_count": len(session.votes),
            "eligible_count": len(session.eligible_voters)
        }

    async def send_gentle_check_in(
        self,
        session_id: str,
        moderator_id: str
    ) -> VoteOutreach:
        """Send check-in to silent voters (ephemeral, no tracking)"""
        session = await self.repo.get_vote_session(session_id)
        if not session:
            raise ValueError("Session not found")

        # Create non-shaming message
        message = (
            f"We're voting on a proposal. No pressure to vote, but wanted you to know. "
            f"Closes {session.closes_at.strftime('%b %d at %I:%M%p')}."
        )

        outreach = VoteOutreach(
            id=generate_id(),
            vote_session_id=session_id,
            sent_at=datetime.now(),
            sent_to=session.silent_voters,
            message=message
        )

        # Save ephemeral record (will be purged when vote closes)
        await self.repo.create_outreach(outreach)

        # Send notifications (implementation depends on notification system)
        # await self.send_notifications(session.silent_voters, message)

        return outreach

    async def extend_vote_session(
        self,
        session_id: str,
        additional_hours: int
    ) -> VoteSession:
        """Extend voting period for low participation"""
        session = await self.repo.get_vote_session(session_id)
        if not session:
            raise ValueError("Session not found")

        new_closes_at = session.closes_at + timedelta(hours=additional_hours)
        return await self.repo.extend_vote_session(session_id, new_closes_at)
```

**Files to Create**:
- `app/services/governance_service.py`

**Verification**:
- [ ] Vote creation works
- [ ] Silence metrics calculate correctly
- [ ] Check-in messages created (ephemeral)
- [ ] Vote extension works

---

## Phase 3: API Endpoints (2-3 hours)

### Task 3.1: Vote Management API
**Effort**: 2-3 hours

```python
# app/api/governance.py

from fastapi import APIRouter, Depends, HTTPException
from app.services.governance_service import GovernanceService
from app.models.governance import VoteChoice

router = APIRouter(prefix="/api/governance", tags=["governance"])

@router.post("/votes/create")
async def create_vote_session(
    request: CreateVoteRequest,
    service: GovernanceService = Depends(get_governance_service)
):
    """Create a new vote session"""
    session = await service.create_vote(
        proposal_id=request.proposal_id,
        cell_id=request.cell_id,
        duration_hours=request.duration_hours,
        quorum_required=request.quorum_required
    )
    return session

@router.post("/votes/{session_id}/cast")
async def cast_vote(
    session_id: str,
    request: CastVoteRequest,
    user_id: str = Depends(get_current_user),
    service: GovernanceService = Depends(get_governance_service)
):
    """Cast a vote (yes/no/abstain)"""
    session = await service.cast_vote(
        session_id=session_id,
        user_id=user_id,
        choice=request.choice
    )
    return session

@router.get("/votes/{session_id}/silence-metrics")
async def get_silence_metrics(
    session_id: str,
    service: GovernanceService = Depends(get_governance_service)
):
    """Get silence weight and participation metrics"""
    metrics = await service.check_silence_weight(session_id)

    # Add gentle prompt if needed
    if metrics["silence_weight"] > 0.3:
        metrics["prompt"] = (
            f"{metrics['silent_count']} people haven't voted yet. "
            "What does this silence mean?"
        )

    return metrics

@router.post("/votes/{session_id}/send-check-in")
async def send_check_in(
    session_id: str,
    moderator_id: str = Depends(require_moderator),
    service: GovernanceService = Depends(get_governance_service)
):
    """Send gentle check-in to silent voters (no pressure)"""
    outreach = await service.send_gentle_check_in(
        session_id=session_id,
        moderator_id=moderator_id
    )

    return {
        "success": True,
        "sent_to_count": len(outreach.sent_to),
        "message": "Gentle check-in sent to silent voters"
    }

@router.post("/votes/{session_id}/extend")
async def extend_vote(
    session_id: str,
    request: ExtendVoteRequest,
    moderator_id: str = Depends(require_moderator),
    service: GovernanceService = Depends(get_governance_service)
):
    """Extend voting period for low participation"""
    session = await service.extend_vote_session(
        session_id=session_id,
        additional_hours=request.additional_hours
    )

    return {
        "success": True,
        "new_closes_at": session.closes_at,
        "extended_count": session.extended_count
    }

@router.get("/votes/active/{cell_id}")
async def get_active_votes(
    cell_id: str,
    service: GovernanceService = Depends(get_governance_service)
):
    """Get active vote sessions for a cell"""
    sessions = await service.repo.get_active_sessions(cell_id)

    # Enrich with silence metrics
    enriched = []
    for session in sessions:
        metrics = {
            "session": session,
            "silence_weight": session.silence_weight,
            "should_pause": session.should_pause
        }
        enriched.append(metrics)

    return enriched
```

**Files to Create**:
- `app/api/governance.py`
- `app/api/models/governance_requests.py` (request/response models)

**Verification**:
- [ ] All endpoints respond correctly
- [ ] Silence metrics returned
- [ ] Check-in messages sent
- [ ] Vote extension works

---

## Phase 4: Background Jobs (1-2 hours)

### Task 4.1: Outreach Purge Job
**Effort**: 1-2 hours

```python
# app/workers/governance_worker.py

async def purge_expired_outreach():
    """Delete outreach records after votes close (privacy)"""
    repo = get_governance_repository()
    deleted = await repo.purge_expired_outreach()
    logger.info(f"Purged {deleted} expired outreach records")

# Schedule to run every hour
# In main.py or scheduler config
```

**Files to Create**:
- `app/workers/governance_worker.py`

**Verification**:
- [ ] Purge job runs successfully
- [ ] Expired records deleted
- [ ] No errors in logs

---

## Phase 5: Tests (3-4 hours)

### Task 5.1: Unit Tests
**Effort**: 2 hours

```python
# tests/test_governance_silence_weight.py

def test_silence_weight_calculation():
    """Silence weight = silent / total"""
    session = VoteSession(
        id="test",
        proposal_id="prop-1",
        cell_id="cell-1",
        opened_at=datetime.now(),
        closes_at=datetime.now() + timedelta(hours=24),
        eligible_voters=["alice", "bob", "carol", "dave"],
        votes={"alice": VoteChoice.YES}
    )

    assert session.silence_weight == 0.75  # 3 silent out of 4
    assert session.participation_rate == 0.25
    assert session.should_pause == True  # More silent than voted

def test_quorum_requirement():
    """Critical votes require quorum"""
    session = VoteSession(
        eligible_voters=["a", "b", "c", "d", "e"],
        votes={"a": "yes", "b": "yes"},
        quorum_required=0.6  # Need 60% participation
    )

    assert session.has_quorum == False  # Only 40% participated

    session.votes["c"] = "yes"
    assert session.has_quorum == True  # Now 60%

def test_no_silence_tracking_patterns():
    """Verify we don't track WHO is silent over time"""
    # Cast votes in session 1
    session1 = create_vote_session("cell-1")
    cast_vote(session1.id, "alice", VoteChoice.YES)
    # Bob is silent

    # Create session 2
    session2 = create_vote_session("cell-1")
    # Bob is silent again

    # Verify: No way to query "Bob's silence pattern"
    # We should NOT have a function like get_silence_history(user_id)
    with pytest.raises(AttributeError):
        get_user_silence_history("bob")

def test_outreach_ephemeral():
    """Outreach records purged after vote closes"""
    session = create_vote_session("cell-1", duration_hours=1)
    outreach = send_gentle_check_in(session.id, moderator_id="alice")

    # Outreach exists
    assert get_outreach(outreach.id) is not None

    # Fast-forward past vote close
    with freeze_time(datetime.now() + timedelta(hours=2)):
        purge_expired_outreach()

    # Outreach deleted
    assert get_outreach(outreach.id) is None

def test_extend_vote_for_low_participation():
    """Extend voting period when turnout is low"""
    session = create_vote_session("cell-1", duration_hours=24)
    original_closes = session.closes_at

    # Only 30% participated
    cast_vote(session.id, "alice", VoteChoice.YES)
    # 9 people silent

    # Extend by 48 hours
    extended = extend_vote_session(session.id, additional_hours=48)

    assert extended.closes_at == original_closes + timedelta(hours=48)
    assert extended.extended_count == 1
```

**Files to Create**:
- `tests/test_governance_silence_weight.py`

**Verification**:
- [ ] All tests pass
- [ ] Silence weight calculations correct
- [ ] Quorum logic works
- [ ] Privacy guarantees verified

---

### Task 5.2: Integration Tests
**Effort**: 1-2 hours

```python
# tests/integration/test_governance_flow.py

async def test_full_vote_flow_with_silence_check():
    """Complete flow: create vote → cast votes → check silence → extend → close"""

    # Create vote
    session = await create_vote(
        proposal_id="prop-1",
        cell_id="sunrise-collective",
        duration_hours=24,
        quorum_required=0.5
    )

    # 3 people vote
    await cast_vote(session.id, "alice", VoteChoice.YES)
    await cast_vote(session.id, "bob", VoteChoice.NO)
    await cast_vote(session.id, "carol", VoteChoice.ABSTAIN)

    # Check silence (7 people silent out of 10)
    metrics = await check_silence_weight(session.id)
    assert metrics["silence_weight"] == 0.7
    assert metrics["should_pause"] == True

    # Send gentle check-in
    await send_gentle_check_in(session.id, moderator_id="facilitator")

    # Extend vote
    await extend_vote_session(session.id, additional_hours=48)

    # More people vote
    await cast_vote(session.id, "dave", VoteChoice.YES)
    await cast_vote(session.id, "eve", VoteChoice.YES)

    # Check again
    metrics = await check_silence_weight(session.id)
    assert metrics["participation_rate"] == 0.5  # Met quorum
    assert metrics["has_quorum"] == True
```

**Verification**:
- [ ] Full flow works end-to-end
- [ ] Metrics update correctly
- [ ] Quorum enforcement works

---

## Phase 6: Documentation (1 hour)

### Task 6.1: Update Proposal Status
**Effort**: 30 min

Update `openspec/changes/gap-60-silence-weight/proposal.md`:
- Change status to "Implemented"
- Add implementation summary
- Link to code locations

### Task 6.2: Add Usage Examples
**Effort**: 30 min

Create `docs/governance_silence_weight.md` with:
- How to create a vote with quorum
- How to check silence metrics
- How to send check-ins (without pressure)
- Privacy guarantees explained

---

## Success Criteria

- [ ] Vote sessions track eligible voters and votes
- [ ] silence_weight calculation works correctly
- [ ] should_pause logic triggers at > 50% silence
- [ ] Quorum requirements enforced for critical votes
- [ ] Gentle check-ins can be sent to silent voters
- [ ] Outreach records are ephemeral (auto-purge)
- [ ] NO tracking of silence patterns over time
- [ ] Vote extension works for low participation
- [ ] All tests pass
- [ ] Privacy guarantees verified

---

## Privacy Guarantees (Critical)

**What we track:**
- Who voted (public: the vote itself)
- Who hasn't voted (computed: eligible - voted)
- Whether outreach was sent (ephemeral, deleted after vote)

**What we DON'T track:**
- Why someone is silent
- Whether they saw the check-in
- Patterns of silence over time
- Individual silence history

**Verification**: Write tests that prove we can't query silence patterns.

---

## bell hooks Would Approve If...

- [ ] No shaming of quiet people
- [ ] Silence is made visible but not punished
- [ ] Check-ins are gentle, not demanding
- [ ] No surveillance of participation patterns
- [ ] Decisions require affirmative consent, not assumed from silence
- [ ] Marginalized voices are invited, not forced

---

## Estimated Timeline

| Phase | Tasks | Effort | Days |
|-------|-------|--------|------|
| Phase 1 | Database & Models | 4-6h | 1 |
| Phase 2 | Service Layer | 3-4h | 0.5 |
| Phase 3 | API Endpoints | 2-3h | 0.5 |
| Phase 4 | Background Jobs | 1-2h | 0.25 |
| Phase 5 | Tests | 3-4h | 0.5 |
| Phase 6 | Documentation | 1h | 0.25 |
| **Total** | | **14-20h** | **2-3 days** |

---

## Dependencies

- Cell membership system (to get eligible_voters)
- Notification system (for check-in messages)
- Governance Circle Agent (optional: AI-assisted facilitation)

---

## Next Steps After Implementation

1. Frontend UI to display silence_weight
2. Visual prompt when silence_weight > 0.5
3. One-click "send check-in" button for moderators
4. Meeting mode with voice equity tracking (future)

---

**Philosophy**: "I will not have my life narrowed down. I will not bow down to somebody else's whim or to someone else's ignorance." - bell hooks

Respecting silence IS respecting voice.
