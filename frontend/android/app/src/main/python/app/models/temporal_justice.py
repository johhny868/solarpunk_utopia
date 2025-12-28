"""
Temporal Justice Models

Don't exclude caregivers and workers with fragmented availability.

Based on Silvia Federici's "Wages Against Housework" - acknowledging that
care work is real work, and that participation shouldn't require
synchronous availability.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from enum import Enum


class TemporalAvailabilityPreference(str, Enum):
    """User's temporal availability preference"""
    SYNCHRONOUS = "synchronous"  # Prefers real-time coordination
    ASYNCHRONOUS = "asynchronous"  # Prefers async participation
    FRAGMENTED = "fragmented"  # Has fragmented availability chunks


class SlowExchangeStatus(str, Enum):
    """Status of a slow exchange"""
    COORDINATING = "coordinating"  # Still figuring out logistics
    IN_PROGRESS = "in_progress"  # Exchange is happening
    PAUSED = "paused"  # Temporarily on hold
    COMPLETED = "completed"  # Successfully completed
    CANCELLED = "cancelled"  # Cancelled by either party


class ContributionType(str, Enum):
    """Type of time contribution"""
    CARE_WORK = "care_work"  # Childcare, eldercare, etc.
    COMMUNITY_LABOR = "community_labor"  # Network maintenance
    AVAILABILITY_SHARING = "availability_sharing"  # Making time available
    COORDINATION = "coordination"  # Organizing exchanges


class RecurrenceType(str, Enum):
    """Availability recurrence pattern"""
    WEEKLY = "weekly"  # Repeats weekly
    ONE_TIME = "one_time"  # One-time availability
    FLEXIBLE = "flexible"  # Flexible/variable


class ChunkOfferStatus(str, Enum):
    """Status of a chunk offer"""
    AVAILABLE = "available"  # Available for claiming
    CLAIMED = "claimed"  # Someone has claimed it
    COMPLETED = "completed"  # Exchange completed


@dataclass
class AvailabilityWindow:
    """A window of time when someone is available"""
    id: str
    user_id: str

    # Time window
    day_of_week: Optional[int]  # 0-6 (Sunday-Saturday)
    start_time: Optional[str]  # HH:MM
    end_time: Optional[str]  # HH:MM
    duration_minutes: int

    # Or specific date/time
    specific_date: Optional[str]  # YYYY-MM-DD
    specific_start_time: Optional[str]  # HH:MM

    # Recurrence
    recurrence_type: RecurrenceType

    # Context
    description: Optional[str]  # "After kids sleep", "Lunch break", etc.

    # Active status
    is_active: bool

    # Metadata
    created_at: datetime
    updated_at: Optional[datetime]


@dataclass
class SlowExchange:
    """An exchange that happens over weeks, not days"""
    id: str

    # Match/Exchange reference
    proposal_id: Optional[str]

    # Parties
    offerer_id: str
    requester_id: str

    # Exchange details
    what: str
    category: str

    # Timeline
    expected_duration_days: int
    deadline: Optional[datetime]

    # Status
    status: SlowExchangeStatus

    # Progress tracking
    last_contact_at: Optional[datetime]
    next_proposed_contact: Optional[datetime]
    check_ins_count: int

    # Notes
    coordination_notes: Optional[List[dict]]  # Timestamped notes

    # Metadata
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]


@dataclass
class TimeContribution:
    """Time contributed to community - especially care work"""
    id: str
    user_id: str

    # Contribution type
    contribution_type: ContributionType

    # Details
    description: str
    category: Optional[str]

    # Time
    hours_contributed: float
    contributed_at: datetime

    # Attribution
    acknowledged_by: Optional[List[str]]  # User IDs who acknowledged
    acknowledgment_count: int

    # Context
    related_exchange_id: Optional[str]
    related_cell_id: Optional[str]

    # Metadata
    created_at: datetime


@dataclass
class AsyncVotingRecord:
    """Record of async voting on proposals"""
    id: str
    proposal_id: str
    user_id: str

    # Vote
    vote: str  # 'approve', 'reject', 'abstain'

    # Context
    voted_at: datetime
    time_to_vote_hours: Optional[float]  # How long after proposal creation

    # Notes
    voting_notes: Optional[str]


@dataclass
class ChunkOffer:
    """An offer for a specific time chunk"""
    id: str
    proposal_id: str  # Links to main offer proposal
    user_id: str

    # Chunk details
    availability_window_id: str

    # What they're offering
    what_offered: str
    category: str

    # Status
    status: ChunkOfferStatus

    # If claimed
    claimed_by_user_id: Optional[str]
    claimed_at: Optional[datetime]

    # Metadata
    created_at: datetime
    completed_at: Optional[datetime]


@dataclass
class TemporalJusticeMetrics:
    """Metrics for temporal justice success"""
    id: str

    # Timeframe
    period_start: datetime
    period_end: datetime

    # Participation metrics
    total_active_members: int
    members_with_fragmented_availability: int
    members_with_care_responsibilities: int

    # Exchange metrics
    total_exchanges: int
    slow_exchanges_count: int
    slow_exchanges_completed: int
    avg_slow_exchange_duration_days: float

    # Contribution metrics
    total_time_contributions_hours: float
    care_work_acknowledged_hours: float

    # Success metric: >30% of active members have fragmented availability
    fragmented_availability_percentage: float

    # Metadata
    calculated_at: datetime
