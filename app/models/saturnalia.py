"""Models for Saturnalia Protocol

'All authority is a mask, not a face.' - Paulo Freire
"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional


class SaturnaliaMode(Enum):
    """Modes of Saturnalia inversion."""
    ROLE_SWAP = "role_swap"
    ANONYMOUS_PERIOD = "anonymous_period"
    REPUTATION_BLINDNESS = "reputation_blindness"
    RANDOM_FACILITATION = "random_facilitation"
    VOICE_INVERSION = "voice_inversion"


class EventStatus(Enum):
    """Status of a Saturnalia event."""
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TriggerType(Enum):
    """How an event was triggered."""
    SCHEDULED = "scheduled"
    MANUAL = "manual"


class SwapStatus(Enum):
    """Status of a role swap."""
    ACTIVE = "active"
    RESTORED = "restored"


@dataclass
class SaturnaliaConfig:
    """Configuration for Saturnalia events."""
    id: str
    cell_id: Optional[str]  # None = network-wide
    community_id: Optional[str]

    # Configuration
    enabled: bool
    enabled_modes: List[SaturnaliaMode]

    # Schedule
    frequency: str  # 'annually', 'biannually', 'quarterly', 'manual'
    duration_hours: int

    # Safety
    exclude_safety_critical: bool
    allow_individual_opt_out: bool

    # Next event
    next_scheduled_start: Optional[datetime]

    # Metadata
    created_at: datetime
    updated_at: datetime
    created_by: str


@dataclass
class SaturnaliaEvent:
    """A Saturnalia event occurrence."""
    id: str
    config_id: str

    # Event details
    start_time: datetime
    end_time: datetime
    active_modes: List[SaturnaliaMode]

    # Status
    status: EventStatus

    # Trigger
    trigger_type: TriggerType
    triggered_by: Optional[str]

    # Metadata
    created_at: datetime
    activated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None


@dataclass
class SaturnaliaRoleSwap:
    """A temporary role swap during Saturnalia."""
    id: str
    event_id: str

    # Original role holder
    original_user_id: str
    original_role: str

    # Temporary role holder
    temporary_user_id: str

    # Scope
    scope_type: str  # 'cell', 'community', 'network'
    scope_id: Optional[str]

    # Status
    status: SwapStatus

    # Metadata
    swapped_at: datetime
    restored_at: Optional[datetime] = None


@dataclass
class SaturnaliaOptOut:
    """User opt-out from Saturnalia modes."""
    id: str
    user_id: str

    # Opt-out scope
    mode: SaturnaliaMode
    scope_type: str  # 'all', 'cell', 'community'
    scope_id: Optional[str]

    # Reason
    reason: Optional[str]

    # Duration
    is_permanent: bool
    expires_at: Optional[datetime]

    # Metadata
    opted_out_at: datetime


@dataclass
class SaturnaliaAnonymousPost:
    """Record of an anonymous post during Saturnalia."""
    id: str
    event_id: str

    # Post details
    post_type: str  # 'offer', 'need', 'message', 'proposal'
    post_id: str
    actual_author_id: str  # Hidden during event, revealed after

    # Metadata
    created_at: datetime
    revealed_at: Optional[datetime] = None


@dataclass
class SaturnaliaReflection:
    """Post-event reflection from a participant."""
    id: str
    event_id: str
    user_id: str

    # Reflection
    what_learned: str
    what_surprised: Optional[str]
    what_changed: Optional[str]

    # Suggestions
    suggestions: Optional[str]

    # Rating
    overall_rating: Optional[int]  # 1-5
    would_do_again: bool

    # Metadata
    submitted_at: datetime
