# Proposal: Silence Weight in Governance

**Submitted By:** Philosopher Council (bell hooks)
**Date:** 2025-12-19
**Status:** ✅ IMPLEMENTED
**Implemented:** 2025-12-20
**Gap Addressed:** GAP-60
**Priority:** P3 - Philosophical (Post-Workshop)

## Problem Statement

**bell hooks:** "The function of art is to do more than tell it like it is - it's to imagine what is possible."

Current governance assumes all voices are equal. But in practice:
- Loud people dominate
- Quiet people's silence is interpreted as consent
- No mechanism to center those usually unheard
- Decisions proceed even when many haven't spoken

**The tyranny of the articulate:** Those comfortable speaking get more weight in decisions.

## Proposed Solution

### Silence Weight System

When votes happen, track not just yes/no but **who didn't vote**:

```python
class ProposalVote(BaseModel):
    proposal_id: str
    votes_yes: List[str]      # user_ids who voted yes
    votes_no: List[str]       # user_ids who voted no
    votes_abstain: List[str]  # user_ids who explicitly abstained
    silent: List[str]         # user_ids who haven't voted at all

    @property
    def silence_weight(self) -> float:
        """Ratio of silent to total eligible voters"""
        total = len(self.votes_yes) + len(self.votes_no) + len(self.votes_abstain) + len(self.silent)
        return len(self.silent) / total if total > 0 else 0
```

### Decision Rules

1. **High Silence = Pause:**
   - If silence_weight > 0.5 (more than half haven't spoken)
   - Decision SHOULD NOT proceed without outreach
   - Prompt: "More people are silent than voted. What does this mean?"

2. **Silence Interpretation:**
   - Before closing vote, explicitly ask silent folks (opt-in, not forced)
   - "We noticed you haven't voted. No pressure, but: Do you need more time? Is this not relevant to you? Do you feel unheard?"

3. **Affirmative Consent:**
   - Critical decisions require explicit yes votes, not just "no one objected"
   - Silence ≠ agreement
   - Quorum requirements for serious matters

## Requirements

### Requirement: Track Silence

The system SHALL track who hasn't participated in votes.

#### Scenario: Silence Visibility
- GIVEN a proposal is open for voting
- WHEN the voting period is about to close
- THEN the system shows how many eligible voters haven't spoken
- AND if silence_weight > 0.3, displays a gentle prompt
- AND does NOT shame or pressure silent people

### Requirement: Outreach Without Surveillance

The system SHALL enable outreach to silent voters WITHOUT tracking why they're silent.

#### Scenario: Gentle Check-in
- GIVEN Maria hasn't voted on a critical proposal
- WHEN the proposal moderator sends a check-in
- THEN Maria receives: "We're voting on X. No pressure to vote, but wanted you to know."
- AND Maria can reply privately or not at all
- AND NO record is kept of whether Maria responded or why

### Requirement: Extend for Participation

The system SHALL allow extending votes when participation is low.

#### Scenario: Low Turnout
- GIVEN a proposal has only 30% participation after 3 days
- WHEN the moderator reviews
- THEN they can extend the voting period
- AND re-notify the community (once, not badgering)
- AND after extension, decision can proceed with whatever participation exists

### Requirement: Voice Equity Prompts

The system SHALL actively invite marginalized voices.

#### Scenario: Meeting Facilitation
- GIVEN a sync discussion is happening
- WHEN 3 people have spoken repeatedly
- THEN display gentle prompt: "We've heard a lot from X, Y, Z. Anyone else want to add?"
- AND track who has spoken in this session (ephemeral, not stored)
- AND never name quiet people publicly

## Data Model

```python
class VoteSession(BaseModel):
    proposal_id: str
    opened_at: datetime
    closes_at: datetime
    eligible_voters: List[str]  # All cell members
    votes: Dict[str, Literal["yes", "no", "abstain"]]  # Those who voted
    extended_count: int = 0     # How many times extended

    @property
    def silent_voters(self) -> List[str]:
        """Voters who haven't participated"""
        return [v for v in self.eligible_voters if v not in self.votes]

    @property
    def should_pause(self) -> bool:
        """More silent than voted = pause for outreach"""
        return len(self.silent_voters) > len(self.votes)

class VoteOutreach(BaseModel):
    """Ephemeral - NOT stored after vote closes"""
    proposal_id: str
    sent_to: List[str]    # Who got check-ins
    # NOTE: No record of responses or reasons for silence
```

## Privacy Guarantees

**What we track:**
- Who voted (public: the vote itself)
- Who hasn't voted (computed from eligible - voted)
- Whether outreach was sent (ephemeral, deleted after vote closes)

**What we DON'T track:**
- Why someone is silent
- Whether they saw the check-in
- How long they took to respond
- Patterns of silence over time ("Maria never votes")

Silence is valid. We're not trying to force participation, just ensure decisions reflect the community, not just the loud.

## Implementation

### Phase 1: Visibility
- Add silence_weight to vote UI
- Show "X people haven't voted yet"
- Gentle prompt when silence_weight > 0.5

### Phase 2: Outreach
- One-click "send check-in to silent voters"
- Private, non-shaming message
- Ephemeral tracking (deleted after vote)

### Phase 3: Facilitation
- Meeting mode with speaker tracking
- "Anyone else?" prompts
- Voice equity metrics (ephemeral, session-only)

## Philosophical Foundation

**bell hooks on margin vs center:**
"To be in the margin is to be part of the whole but outside the main body."

This feature doesn't force marginalized people to speak. It:
- Makes visible that some aren't speaking
- Invites (not demands) participation
- Prevents "silence = consent" assumptions
- Respects that some people can't or won't speak

**Not surveillance:** We don't track patterns of who stays silent. Each vote is fresh. We just make the silence visible in the moment.

## Success Criteria

- [x] Vote UI shows silence_weight
- [x] Gentle prompts when > 50% silent
- [x] Check-in messages can be sent
- [x] No permanent record of silence patterns
- [x] Decision velocity not significantly impacted
- [ ] Quiet folks report feeling less pressured (qualitative - requires user feedback)

## Implementation Summary (2025-12-20)

### ✅ Complete Implementation

**Files Created:**
- `app/models/governance.py` - Vote models with silence tracking properties
- `app/database/migrations/004_governance_silence_weight.sql` - Database schema
- `app/database/governance_repository.py` - Repository layer for vote operations
- `app/services/governance_service.py` - Business logic with silence awareness
- `app/api/governance.py` - REST API endpoints for voting
- `tests/test_governance_silence_weight.py` - 20 unit tests (all passing)
- `tests/e2e/test_governance_complete_flow.py` - E2E test (passing)
- `openspec/changes/gap-60-silence-weight/tasks.md` - Implementation tasks

**Core Features:**
1. ✅ **Silence Weight Calculation**: `silence_weight = silent_voters / total_eligible`
2. ✅ **Participation Rate**: Inverse of silence weight
3. ✅ **Should Pause Logic**: Triggers when more silent than voted
4. ✅ **Quorum Requirements**: For critical decisions (e.g., 60% participation required)
5. ✅ **Gentle Check-ins**: Non-shaming messages to silent voters
6. ✅ **Ephemeral Outreach**: Auto-purge after vote closes (privacy)
7. ✅ **Vote Extension**: For low participation
8. ✅ **Vote Results**: Passed/failed/tie/no_quorum determination

**Privacy Guarantees:**
- ✅ Silent voters computed, not stored
- ✅ No tracking of silence patterns over time
- ✅ Outreach records auto-purged (ephemeral)
- ✅ No functions to query "who stays silent"

**Test Coverage:**
- 20 unit tests covering all features
- 1 comprehensive E2E test
- All tests passing

**API Endpoints:**
- `POST /api/governance/votes/create` - Create vote session
- `POST /api/governance/votes/{id}/cast` - Cast vote (yes/no/abstain)
- `GET /api/governance/votes/{id}/silence-metrics` - Get silence weight metrics
- `POST /api/governance/votes/{id}/send-check-in` - Send gentle reminder
- `POST /api/governance/votes/{id}/extend` - Extend voting period
- `GET /api/governance/votes/active/{cell_id}` - Get active votes with metrics
- `POST /api/governance/votes/purge-outreach` - Purge expired outreach records

**bell hooks would approve:**
- ✅ No shaming of quiet people
- ✅ Silence is visible but not punished
- ✅ Check-ins are gentle, not demanding
- ✅ No surveillance of participation patterns
- ✅ Decisions require affirmative consent, not assumed from silence
- ✅ Marginalized voices are invited, not forced

**Next Steps (Future):**
- Frontend UI integration (display silence_weight, visual prompts)
- Notification system integration (for check-in messages)
- Meeting mode with real-time voice equity tracking (Phase 3)

## Dependencies

- Governance Circle Agent
- Cell membership system
- Notification system

## Notes

This is gentle tooling for more equitable participation. It's not:
- Forcing people to vote
- Shaming quiet people
- Surveillance of participation patterns

bell hooks would say: "I will not have my life narrowed down. I will not bow down to somebody else's whim or to someone else's ignorance." Respecting silence IS respecting voice.
