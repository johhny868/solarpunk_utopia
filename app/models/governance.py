"""
Governance models with bell hooks' Silence Weight framework.

Tracks participation in decision-making while respecting silence and privacy.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Literal, Optional
from datetime import datetime, timedelta
from enum import Enum
import uuid


class VoteChoice(str, Enum):
    """Valid vote choices"""
    YES = "yes"
    NO = "no"
    ABSTAIN = "abstain"


class VoteSession(BaseModel):
    """
    Vote session with silence tracking.

    bell hooks: "The function of art is to do more than tell it like it is -
    it's to imagine what is possible."

    This model tracks who hasn't voted (silence) while respecting privacy:
    - Silence is visible in aggregate (silence_weight)
    - No tracking of patterns over time
    - Ephemeral outreach records (auto-purge)
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    proposal_id: str
    cell_id: str
    opened_at: datetime = Field(default_factory=datetime.now)
    closes_at: datetime
    eligible_voters: List[str]  # Cell members at time of opening
    votes: Dict[str, VoteChoice] = Field(default_factory=dict)  # user_id -> choice
    extended_count: int = 0
    quorum_required: Optional[float] = None  # 0.0-1.0, for critical decisions
    created_at: datetime = Field(default_factory=datetime.now)

    @property
    def silent_voters(self) -> List[str]:
        """
        Voters who haven't participated.

        NOTE: This is computed, not stored. We don't track silence patterns.
        """
        return [v for v in self.eligible_voters if v not in self.votes]

    @property
    def silence_weight(self) -> float:
        """
        Ratio of silent to total eligible voters.

        > 0.5 = more silent than voted (should pause for outreach)
        > 0.3 = gentle prompt recommended
        """
        total = len(self.eligible_voters)
        return len(self.silent_voters) / total if total > 0 else 0.0

    @property
    def participation_rate(self) -> float:
        """Ratio of participated to total eligible (inverse of silence_weight)"""
        return 1.0 - self.silence_weight

    @property
    def should_pause(self) -> bool:
        """
        More silent than voted = pause for outreach.

        bell hooks: Don't assume silence = consent.
        """
        return len(self.silent_voters) > len(self.votes)

    @property
    def has_quorum(self) -> bool:
        """
        Check if quorum requirement met.

        For critical decisions, require affirmative participation.
        Silence ≠ agreement.
        """
        if self.quorum_required is None:
            return True
        return self.participation_rate >= self.quorum_required

    @property
    def is_closed(self) -> bool:
        """Check if voting period has ended"""
        return datetime.now() >= self.closes_at

    @property
    def vote_counts(self) -> Dict[str, int]:
        """Count votes by choice"""
        counts = {"yes": 0, "no": 0, "abstain": 0}
        for choice in self.votes.values():
            counts[choice.value] += 1
        return counts

    @property
    def result(self) -> Optional[str]:
        """
        Determine vote result (if closed and has quorum).

        Returns: "passed", "failed", "no_quorum", or None if still open
        """
        if not self.is_closed:
            return None

        if not self.has_quorum:
            return "no_quorum"

        counts = self.vote_counts
        if counts["yes"] > counts["no"]:
            return "passed"
        elif counts["no"] > counts["yes"]:
            return "failed"
        else:
            return "tie"


class VoteOutreach(BaseModel):
    """
    Ephemeral record of check-ins sent to silent voters.

    PRIVACY GUARANTEE: This record is auto-purged when vote closes.

    We track:
    - THAT outreach was sent
    - WHO it was sent to

    We DON'T track:
    - Whether they responded
    - Why they're silent
    - Patterns of silence over time
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    vote_session_id: str
    sent_at: datetime = Field(default_factory=datetime.now)
    sent_to: List[str]  # User IDs who got check-ins
    message: str
    purge_at: datetime  # Set to vote closes_at
    created_at: datetime = Field(default_factory=datetime.now)

    @property
    def is_expired(self) -> bool:
        """Check if this outreach should be purged"""
        return datetime.now() >= self.purge_at


class CreateVoteRequest(BaseModel):
    """Request to create a new vote session"""
    proposal_id: str
    cell_id: str
    duration_hours: int = 72  # Default: 3 days
    quorum_required: Optional[float] = None  # 0.0-1.0


class CastVoteRequest(BaseModel):
    """Request to cast a vote"""
    choice: VoteChoice


class ExtendVoteRequest(BaseModel):
    """Request to extend voting period"""
    additional_hours: int = Field(ge=1, le=168)  # 1 hour to 1 week


class SilenceMetrics(BaseModel):
    """
    Silence and participation metrics for display.

    These are computed on-the-fly, not stored.
    """
    silence_weight: float
    participation_rate: float
    should_pause: bool
    has_quorum: bool
    silent_count: int
    voted_count: int
    eligible_count: int
    prompt: Optional[str] = None  # Gentle prompt if silence_weight > threshold


# Type aliases for clarity
UserId = str
ProposalId = str
CellId = str
